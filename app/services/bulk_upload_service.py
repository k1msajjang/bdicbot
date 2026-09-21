import pandas as pd
from io import BytesIO
from fastapi import HTTPException
from app.db.supabase_client import supabase
from app.services.knowledge_base_service import create_knowledge_base_entry
import logging

logger = logging.getLogger(__name__)

MAX_ROWS = 50
REQUIRED_COLUMNS = {"judul", "jawaban", "kategori", "program", "tags"}


def parse_upload_file(filename: str, content: bytes) -> pd.DataFrame:
    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(
                BytesIO(content),
                index_col=False,
                dtype=str,
                keep_default_na=False,
                on_bad_lines="error",
            )
        elif filename.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(BytesIO(content), dtype=str)
            df = df.fillna("")
        else:
            raise HTTPException(status_code=400, detail="Format file tidak didukung, gunakan .csv atau .xlsx")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gagal parse file upload: {e}")
        raise HTTPException(status_code=400, detail="File tidak bisa dibaca, cek kembali format dan isi filenya")

    df.columns = df.columns.astype(str).str.strip().str.lower()

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"Kolom wajib tidak ditemukan: {', '.join(missing_columns)}")

    unexpected_columns = set(df.columns) - REQUIRED_COLUMNS
    if unexpected_columns:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Ditemukan kolom tak dikenal: {', '.join(unexpected_columns)}. "
                "Biasanya ini tanda ada nilai bertanda koma yang belum dibungkus tanda kutip "
                "(untuk CSV), atau kolom/data tambahan di luar template (untuk Excel). "
                "Periksa kembali file sebelum upload ulang."
            )
        )

    df = df[list(REQUIRED_COLUMNS)]  # buang kemungkinan urutan kolom acak, kunci ke urutan yang kita harapkan
    df = df.dropna(how="all")  # buang baris kosong total (sisa export Excel)

    if len(df) == 0:
        raise HTTPException(status_code=400, detail="File tidak berisi data")
    if len(df) > MAX_ROWS:
        raise HTTPException(status_code=400, detail=f"Maksimal {MAX_ROWS} baris per upload, file ini punya {len(df)} baris")

    return df


def _load_master_data_maps() -> tuple[dict, dict]:
    try:
        cat_response = supabase.table("categories").select("id, name").execute()
        prog_response = supabase.table("programs").select("id, name").execute()
    except Exception as e:
        logger.error(f"Gagal load master data untuk bulk upload: {e}")
        raise HTTPException(status_code=503, detail="Gagal memuat data kategori/program, coba lagi nanti")

    category_map = {c["name"].strip().lower(): c["id"] for c in cat_response.data}
    program_map = {p["name"].strip().lower(): p["id"] for p in prog_response.data}
    return category_map, program_map


def _split_names(raw) -> list[str]:
    if pd.isna(raw) or not str(raw).strip():
        return []
    return [n.strip() for n in str(raw).split(",") if n.strip()]


def _resolve_tag_ids(tag_names: list[str]) -> list[int]:
    if not tag_names:
        return []
    try:
        existing = supabase.table("tags").select("id, name").in_("name", tag_names).execute()
    except Exception as e:
        logger.error(f"Gagal cek tags existing: {e}")
        raise HTTPException(status_code=503, detail="Gagal memproses tags, coba lagi nanti")

    existing_map = {t["name"].strip().lower(): t["id"] for t in existing.data}
    tag_ids = []
    for name in tag_names:
        key = name.lower()
        if key in existing_map:
            tag_ids.append(existing_map[key])
        else:
            try:
                created = supabase.table("tags").insert({"name": name}).execute()
                new_id = created.data[0]["id"]
                existing_map[key] = new_id
                tag_ids.append(new_id)
            except Exception as e:
                logger.error(f"Gagal bikin tag baru '{name}': {e}")
                raise HTTPException(status_code=503, detail=f"Gagal membuat tag baru: {name}")
    return tag_ids


def process_bulk_upload(df: pd.DataFrame, user_id: int) -> dict:
    category_map, program_map = _load_master_data_maps()

    berhasil = []
    gagal = []

    for position, (_, row) in enumerate(df.iterrows()):
        baris_ke = position + 2  # +2: posisi 0-based, plus 1 baris header di file asli

        try:
            judul = str(row["judul"]).strip()
            jawaban = str(row["jawaban"]).strip()

            if not judul or judul.lower() == "nan":
                raise ValueError("judul kosong")
            if not jawaban or jawaban.lower() == "nan":
                raise ValueError("jawaban kosong")

            kategori_names = _split_names(row["kategori"])
            program_names = _split_names(row["program"])
            tag_names = _split_names(row.get("tags"))

            if not kategori_names:
                raise ValueError("kategori kosong, minimal 1")
            if not program_names:
                raise ValueError("program kosong, minimal 1")

            category_ids = []
            for name in kategori_names:
                if name.lower() not in category_map:
                    raise ValueError(f"kategori '{name}' tidak ditemukan")
                category_ids.append(category_map[name.lower()])

            program_ids = []
            for name in program_names:
                if name.lower() not in program_map:
                    raise ValueError(f"program '{name}' tidak ditemukan")
                program_ids.append(program_map[name.lower()])

            tag_ids = _resolve_tag_ids(tag_names)

            new_id = create_knowledge_base_entry(
                judul=judul, jawaban=jawaban,
                category_ids=category_ids, program_ids=program_ids, tag_ids=tag_ids,
                user_id=user_id
            )
            berhasil.append({"baris": baris_ke, "id": new_id, "judul": judul})

        except HTTPException as e:
            gagal.append({"baris": baris_ke, "error": e.detail})
        except ValueError as e:
            gagal.append({"baris": baris_ke, "error": str(e)})
        except Exception as e:
            logger.error(f"Gagal proses baris {baris_ke} bulk upload: {e}")
            gagal.append({"baris": baris_ke, "error": "Gagal diproses, terjadi kesalahan"})

    return {
        "total_baris": len(df),
        "berhasil": len(berhasil),
        "gagal": len(gagal),
        "detail_berhasil": berhasil,
        "detail_gagal": gagal,
    }
from fastapi import HTTPException
from app.db.supabase_client import supabase
from app.services.embedding_service import generate_embedding
import logging

logger = logging.getLogger(__name__)

def create_knowledge_base_entry(judul: str, jawaban: str, category_ids: list[int],
                                  program_ids: list[int], tag_ids: list[int], user_id: int) -> int:
    tag_names = []
    if tag_ids:
        try:
            tag_response = supabase.table("tags").select("name").in_("id", tag_ids).execute()
            tag_names = [t["name"] for t in tag_response.data]
        except Exception as e:
            logger.error(f"Gagal ambil nama tags: {e}")
            raise HTTPException(status_code=503, detail="Gagal memproses tags, coba lagi nanti")

    embed_text = f"{judul}. {jawaban}. Kata kunci: {', '.join(tag_names)}"

    try:
        embedding = generate_embedding(embed_text)
    except Exception as e:
        logger.error(f"Gagal generate embedding: {e}")
        raise HTTPException(status_code=503, detail="Gagal memproses AI, coba lagi nanti")

    try:
        response = supabase.rpc("create_knowledge_base_entry", {
            "p_judul": judul,
            "p_jawaban": jawaban,
            "p_embedding": embedding,
            "p_category_ids": category_ids,
            "p_program_ids": program_ids,
            "p_tag_ids": tag_ids,
            "p_user_id": user_id
        }).execute()
    except Exception as e:
        logger.error(f"Gagal simpan knowledge_base: {e}")
        raise HTTPException(status_code=400, detail="Gagal menyimpan data, cek kategori/program/tags yang dipilih valid")

    return response.data
def toggle_knowledge_base_status(entry_id: int, new_status: bool, user_id: int) -> None:
    try:
        supabase.rpc("toggle_knowledge_base_status",{
            "p_id": entry_id,
            "p_new_status": new_status,
            "p_user_id": user_id
        }).execute()
    except Exception as e:
        logger.error(f"Gagal toggle status entry {entry_id}: {e}")
        raise HTTPException(status_code=404,detail="Entry tidak ditemukan.")

def update_knowledge_base_entry(entry_id: int, judul: str, jawaban: str, category_ids: list[int],
                                  program_ids: list[int], tag_ids: list[int], user_id: int) -> None:
    tag_names = []
    if tag_ids:
        try:
            tag_response = supabase.table("tags").select("name").in_("id", tag_ids).execute()
            tag_names = [t["name"] for t in tag_response.data]
        except Exception as e:
            logger.error(f"Gagal ambil nama tags: {e}")
            raise HTTPException(status_code=503, detail="Gagal memproses tags, coba lagi nanti")

    embed_text = f"{judul}. {jawaban}. Kata kunci: {', '.join(tag_names)}"

    try:
        embedding = generate_embedding(embed_text)
    except Exception as e:
        logger.error(f"Gagal generate embedding: {e}")
        raise HTTPException(status_code=503, detail="Gagal memproses AI, coba lagi nanti")

    try:
        supabase.rpc("update_knowledge_base_entry", {
            "p_id": entry_id, "p_judul": judul, "p_jawaban": jawaban, "p_embedding": embedding,
            "p_category_ids": category_ids, "p_program_ids": program_ids, "p_tag_ids": tag_ids,
            "p_user_id": user_id
        }).execute()
    except Exception as e:
        logger.error(f"Gagal update knowledge_base {entry_id}: {e}")
        raise HTTPException(status_code=400, detail="Gagal menyimpan perubahan, cek id entry dan kategori/program/tags valid")


def delete_knowledge_base_entry(entry_id: int, user_id: int) -> None:
    try:
        supabase.rpc("delete_knowledge_base_entry", {"p_id": entry_id, "p_user_id": user_id}).execute()
    except Exception as e:
        logger.error(f"Gagal hapus knowledge_base {entry_id}: {e}")
        raise HTTPException(status_code=404, detail="Entry tidak ditemukan")
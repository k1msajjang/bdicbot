from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import decode_access_token
from app.db.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)

# Memperkenalkan skema Bearer Token ke OpenAPI / Swagger UI
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    # HTTPBearer otomatis mengekstrak token dari header "Authorization: Bearer <token>"
    token = credentials.credentials

    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=401, 
            detail="Sesi tidak valid atau sudah kedaluwarsa. Silakan login kembali."
        )

    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Token tidak valid.")

    try:
        response = (
            supabase.table("users")
            .select("id, role_id, is_active")
            .eq("id", user_id)
            .execute()
        )
    except Exception as e:
        logger.error(f"Gagal verifikasi user saat auth: {e}")
        raise HTTPException(status_code=503, detail="Gagal memverifikasi sesi, coba lagi nanti.")

    users = response.data
    if not users:
        raise HTTPException(status_code=401, detail="Akun tidak ditemukan.")

    user = users[0]

    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Akun nonaktif.")

    return {"user_id": user["id"], "role_id": user["role_id"]}

def require_superadmin(current_user: dict = Depends(get_current_user)) -> dict:
    try:
        response = supabase.table("roles").select("name").eq("id", current_user["role_id"]).execute()
    except Exception as e:
        logger.error(f"Gagal cek role: {e}")
        raise HTTPException(status_code=503, detail="Gagal memverifikasi akses, coba lagi nanti")

    roles = response.data
    if not roles or roles[0]["name"].lower() != "superadmin":
        raise HTTPException(status_code=403, detail="Hanya SuperAdmin yang boleh melakukan aksi ini")

    return current_user
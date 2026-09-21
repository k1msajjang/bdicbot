from fastapi import HTTPException
from app.db.supabase_client import supabase
from app.utils.security import hash_password
import logging

logger = logging.getLogger(__name__)

def create_user(username: str, password: str, nama: str, role_name: str, created_by_user_id: int) -> int:
    try:
        role_response = supabase.table("roles").select("id").ilike("name", role_name).execute()
    except Exception as e:
        logger.error(f"Gagal cek role saat create user: {e}")
        raise HTTPException(status_code=503, detail="Gagal memverifikasi role, coba lagi nanti")

    roles = role_response.data
    if not roles:
        raise HTTPException(status_code=400, detail=f"Role '{role_name}' tidak ditemukan")
    role_id = roles[0]["id"]

    hashed_password = hash_password(password)

    try:
        response = supabase.rpc("create_user_account", {
            "p_username": username,
            "p_password_hash": hashed_password,
            "p_nama": nama,
            "p_role_id": role_id,
            "p_created_by": created_by_user_id
        }).execute()
    except Exception as e:
        logger.error(f"Gagal create user account: {e}")
        raise HTTPException(status_code=400, detail="Gagal membuat akun, kemungkinan username sudah dipakai")

    return response.data
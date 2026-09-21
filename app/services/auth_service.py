from fastapi import HTTPException 
from app.db.supabase_client import supabase
from app.utils.security import verify_password, create_access_token
import logging

logger = logging.getLogger(__name__)

GENERIC_LOGIN_ERROR = "Username atau password salah."

def authenticate_user(username: str, password: str) -> str:
    try:
        response = (
            supabase.table("users")
            .select("id,pw,is_active")
            .eq("username",username)
            .execute()
        )
    except Exception as e:
        logger.error(f"Gagal query users saat login: {e}")
        raise HTTPException(status_code=503,detail="Gagal memproses login,coba lagi nanti.")

    users = response.data
    if not users:
        raise HTTPException(status_code=401, detail = GENERIC_LOGIN_ERROR)

    user = users[0]

    if not verify_password(password,user["pw"]):
        raise HTTPException(status_code=401, detail=GENERIC_LOGIN_ERROR)

    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Akun nonaktif.")

    token = create_access_token({"sub":str(user["id"])})
    return token
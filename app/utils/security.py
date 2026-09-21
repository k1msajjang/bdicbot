import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.config import settings

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except (ValueError, TypeError):
        # Hash di database rusak/format gak valid — anggap gagal verifikasi,
        # jangan biarin exception ini nge-crash request
        return False

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    to_encode.update({
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    })
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
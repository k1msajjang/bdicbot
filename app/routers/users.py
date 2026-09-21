from fastapi import APIRouter, Depends
from app.schemas.user_schemas import CreateUserRequest
from app.services.user_service import create_user
from app.utils.deps import require_superadmin

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("")
def create_user_account(payload: CreateUserRequest, current_user: dict = Depends(require_superadmin)):
    new_id = create_user(
        username=payload.username,
        password=payload.password,
        nama=payload.nama,
        role_name=payload.role,
        created_by_user_id=current_user["user_id"]
    )
    return {"id": new_id, "message": "Akun berhasil dibuat"}
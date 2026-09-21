from fastapi import APIRouter, Depends, Request
from app.schemas.auth_schemas import LoginRequest, TokenResponse
from app.services.auth_service import authenticate_user
from app.utils.deps import get_current_user
from app.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest):
    token = authenticate_user(payload.username, payload.password)
    return TokenResponse(access_token=token)

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
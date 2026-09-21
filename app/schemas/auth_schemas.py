from pydantic import BaseModel, Field, field_validator

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=72)

    @field_validator("username")
    @classmethod
    def strip_username(cls, v: str) -> str:
        return v.strip()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
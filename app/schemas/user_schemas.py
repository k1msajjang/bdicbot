from pydantic import BaseModel, Field, field_validator

class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8, max_length=72)
    nama: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1, max_length=50)

    @field_validator("username")
    @classmethod
    def strip_username(cls, v: str) -> str:
        return v.strip()
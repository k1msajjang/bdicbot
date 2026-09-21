from pydantic import BaseModel, Field
from uuid import UUID

class ChatRequest(BaseModel):
    session_id: UUID
    message: str = Field(..., min_length=1, max_length=1000)

class ChatResponse(BaseModel):
    session_id: UUID
    reply: str

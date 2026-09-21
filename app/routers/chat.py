from fastapi import APIRouter,Request
from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.services.chat_service import process_chat_message
from app.core.limiter import limiter

router = APIRouter(tags=["Chat"])

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
def chat(request: Request, payload: ChatRequest):
    reply = process_chat_message(payload.session_id, payload.message)
    return ChatResponse(session_id=payload.session_id, reply=reply)

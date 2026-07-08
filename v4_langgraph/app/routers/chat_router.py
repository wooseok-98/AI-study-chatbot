"""채팅 라우팅 — POST /chat (대화), GET /chat/{session_id}/history (지난 대화)"""

from fastapi import APIRouter

from app.controllers.chat_controller import handle_chat
from app.schemas.chat import ChatRequest, ChatResponse
from shared import db

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    answer = handle_chat(req.question, req.session_id)
    return ChatResponse(answer=answer)


@router.get("/chat/{session_id}/history")
def get_chat_history(session_id: str):
    """그 세션의 지난 대화를 [{"role":..., "content":...}, ...] 로 반환"""
    return db.get_history(session_id)

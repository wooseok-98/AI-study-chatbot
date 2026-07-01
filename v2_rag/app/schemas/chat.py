"""POST /chat 의 요청/응답 데이터 모델 (입력·출력 형식 정의·검증)"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"  # 세션 구분용 (없으면 default)


class ChatResponse(BaseModel):
    answer: str

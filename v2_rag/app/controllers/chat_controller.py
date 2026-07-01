"""RAG 근거 기반 답변 생성"""

from app.core import llm, rag
from shared import db


def handle_chat(question: str, session_id: str) -> str:
    # 1. 해당 session_id 의 이전 대화를 DB에서 불러오기
    history = db.get_history(session_id)

    # 2. 관련 노트 검색
    contexts = rag.search(question)

    # 3. 근거 기반 답변 받기
    answer = llm.answer_with_context(question, contexts, history)

    # 4. 질문과 답변을 DB에 저장 (다음 턴/재방문 때 불러올 수 있도록)
    db.save_message(session_id, "user", question)
    db.save_message(session_id, "assistant", answer)

    # 5. 답변 반환
    return answer

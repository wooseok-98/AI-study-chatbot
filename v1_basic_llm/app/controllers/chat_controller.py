"""대화 흐름 제어 + 멀티턴 history 관리 (DB 영속 저장)"""

from app.core import llm
from shared import db


def handle_chat(question: str, session_id: str) -> str:
    # 1. 해당 session_id 의 이전 대화를 DB에서 불러오기
    history = db.get_history(session_id)

    # 2. 이번 질문을 history 끝에 추가 (llm 에 보낼 용도)
    history.append({"role": "user", "content": question})

    # 3. llm 호출해서 답변 받기
    answer = llm.chat(history)

    # 4. 질문과 답변을 DB에 저장 (다음 턴/재방문 때 불러올 수 있도록)
    db.save_message(session_id, "user", question)
    db.save_message(session_id, "assistant", answer)

    # 5. 답변 반환
    return answer

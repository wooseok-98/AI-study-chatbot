"""ReAct 에이전트 호출 + 멀티턴 + DB (v4)

v3는 chains.answer(고정 체인), v4는 graph.answer(에이전트 그래프) 호출.
controller 입장에선 "answer 하나 부른다"로 동일 — 안이 체인이냐 에이전트냐만 다름.
"""

from app.core import graph
from shared import db


def handle_chat(question: str, session_id: str) -> str:
    history = db.get_history(session_id)         # 이전 대화 (dict 리스트)
    answer = graph.answer(question, history)     # ReAct 에이전트 실행

    db.save_message(session_id, "user", question)
    db.save_message(session_id, "assistant", answer)
    return answer

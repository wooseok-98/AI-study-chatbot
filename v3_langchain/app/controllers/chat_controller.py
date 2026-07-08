"""RAG 흐름 (LangChain 체인 호출) + 멀티턴 + DB

v2는 rag.search + llm.answer_with_context 를 따로 호출했는데,
v3는 그 흐름이 chains.answer(체인) 한 번 호출로 압축됨.
"""

from app.core import chains
from shared import db


def handle_chat(question: str, session_id: str) -> str:
    history = db.get_history(session_id)        # 이전 대화 (dict 리스트)
    answer = chains.answer(question, history)   # LCEL 체인 실행 (검색+생성)

    db.save_message(session_id, "user", question)
    db.save_message(session_id, "assistant", answer)
    return answer

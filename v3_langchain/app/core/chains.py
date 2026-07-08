"""RAG 체인 (LCEL) — 검색 → 프롬프트 → LLM → 파싱을 파이프(|)로 연결

v2에서 controller가 손으로 조립하던 흐름을, LangChain 체인 한 줄로 표현
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage

from app.core import rag
from app.core.llm import llm

RAG_SYSTEM = (
    "너는 AI 학습 도우미야. 아래 [노트] 내용만 근거로 답해. "
    "노트에 없는 내용은 지어내지 말고 '노트에서 찾지 못했어요'라고 말해. "
    "답변 끝에 참고한 출처를 알려줘."
)

# 프롬프트 템플릿 (v2의 f-string 프롬프트 → LangChain 템플릿)
#   {history}  = 이전 대화 (멀티턴)
#   {context}  = 검색된 근거 조각
#   {question} = 이번 질문
prompt = ChatPromptTemplate.from_messages([
    ("system", RAG_SYSTEM),
    MessagesPlaceholder("history"),
    ("human", "[노트]\n{context}\n\n[질문]\n{question}"),
])


def _format_docs(docs) -> str:
    """검색된 Document 들을 근거 블록 문자열로 (v2의 context_block)"""
    return "\n\n".join(
        f"[출처: {d.metadata['source']}]\n{d.page_content}" for d in docs
    )


# ── LCEL 체인 ──────────────────────────────────────────────
# 질문으로 검색해 context 를 채운 뒤 → 프롬프트 → LLM → 텍스트
rag_chain = (
    RunnablePassthrough.assign(
        context=lambda x: _format_docs(rag.retrieve(x["question"]))
    )
    | prompt
    | llm
    | StrOutputParser()
)


def answer(question: str, history_dicts: list) -> str:
    """controller 진입점 — DB history(dict) → LangChain 메시지로 변환 후 체인 실행"""
    history = [
        AIMessage(m["content"]) if m["role"] == "assistant" else HumanMessage(m["content"])
        for m in history_dicts
    ]
    return rag_chain.invoke({"question": question, "history": history})

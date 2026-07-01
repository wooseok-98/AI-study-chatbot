"""Claude API 호출 — LLM 교체 단일 지점 (모델·시스템프롬프트는 여기서만 관리)"""

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5"  # 실제 테스트는 "claude-opus-4-8"
RAG_SYSTEM = (
    "너는 AI 학습 도우미야. 아래 제공된 [노트] 내용만 근거로 답해. "
    "노트에 없는 내용은 지어내지 말고 '노트에서 찾지 못했어요'라고 말해. "
    "답변 끝에 참고한 출처(파일명)를 알려줘."
)

def answer_with_context(question: str, contexts: list[dict], history: list = None) -> str:
    """검색된 노트 조각(contexts)을 근거로 답변 생성"""
    history = history or []

    # 검색된 조각들을 근거 블록으로 묶기
    context_block = "\n\n".join(
        f"[출처: {c['source']}]\n{c['text']}" for c in contexts
    )
    user_content = f"[노트]\n{context_block}\n\n[질문]\n{question}"

    messages = history + [{"role": "user", "content": user_content}]
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=RAG_SYSTEM,
        messages=messages,
    )
    return response.content[0].text

"""Claude API 호출 — LLM 교체 단일 지점 (모델·시스템프롬프트는 여기서만 관리)"""

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5"  # 실제 테스트는 "claude-opus-4-8"
SYSTEM_PROMPT = "너는 AI 엔지니어 취업 준비생을 위한 AI 학습 도우미야" 

# 대화 진행 함수
def chat(messages: list[dict]) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    # 여러가지 응답(토큰 사용량, 모델 정보 등) 중 답변만 반환
    return response.content[0].text
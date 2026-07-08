"""LLM — LangChain ChatAnthropic (모델 교체 단일 지점)

v2의 anthropic client 를 LangChain 래퍼로 교체.
ANTHROPIC_API_KEY 는 환경변수에서 자동으로 읽음.
"""

from langchain_anthropic import ChatAnthropic

MODEL = "claude-haiku-4-5"

llm = ChatAnthropic(model=MODEL, max_tokens=2048)

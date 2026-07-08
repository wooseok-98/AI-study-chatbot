"""에이전트 도구 — LLM이 골라 쓰는 3개 도구 (노트·위키·웹 검색)

@tool 데코레이터가 함수를 'LangChain 도구'로 만듦.
docstring이 곧 도구 설명 → LLM이 이걸 읽고 어떤 도구를 쓸지 판단.
"""

from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

from app.core import rag


@tool
def search_notes(query: str) -> str:
    """사용자가 직접 정리한 학습 노트(RNN, LSTM, RAG, LangChain, FastAPI 등)에서 검색한다.
    '내가 정리한', '내 노트' 처럼 사용자 본인의 정리 내용을 물을 때 사용."""
    return rag.search_notes(query)


@tool
def search_wiki(query: str) -> str:
    """위키피디아(AI/ML 주제)에서 검색한다. 일반적인 개념·정의 설명이 필요할 때 사용."""
    return rag.search_wiki(query)


_ddg = DuckDuckGoSearchRun()


@tool
def web_search(query: str) -> str:
    """웹을 검색한다. 노트·위키에 없는 최신 정보나 실시간 정보가 필요할 때 사용."""
    return _ddg.run(query)


TOOLS = [search_notes, search_wiki, web_search]

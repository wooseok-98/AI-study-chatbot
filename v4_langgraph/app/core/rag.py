"""RAG 검색 (LangChain) — 노트/위키 벡터스토어에서 검색해 문자열로 반환

v4에서는 도구(tools.py)가 이 함수들을 호출.
검색 결과를 LLM에게 줄 텍스트(출처 포함)로 포맷해서 반환.
인덱스는 v3의 lc_notes_index / lc_wiki_index 를 그대로 재사용.
"""

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

import shared

DATA_DIR = Path(shared.__file__).resolve().parent / "data"

_embeddings = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sroberta-multitask",
    encode_kwargs={"normalize_embeddings": True},
)

_notes = FAISS.load_local(
    str(DATA_DIR / "lc_notes_index"), _embeddings, allow_dangerous_deserialization=True
)
_wiki = FAISS.load_local(
    str(DATA_DIR / "lc_wiki_index"), _embeddings, allow_dangerous_deserialization=True
)


def _format(docs) -> str:
    if not docs:
        return "(검색 결과 없음)"
    return "\n\n".join(
        f"[출처: {d.metadata['source']}]\n{d.page_content}" for d in docs
    )


def search_notes(query: str, k: int = 4) -> str:
    """학습 노트 인덱스 검색 → 출처 포함 문자열"""
    return _format(_notes.similarity_search(query, k=k))


def search_wiki(query: str, k: int = 4) -> str:
    """위키 인덱스 검색 → 출처 포함 문자열"""
    return _format(_wiki.similarity_search(query, k=k))

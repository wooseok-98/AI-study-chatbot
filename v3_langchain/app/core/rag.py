"""RAG 검색 (LangChain) — 저장된 FAISS 벡터스토어에서 노트+위키 검색·병합

v2의 수동 FAISS 검색을 LangChain 벡터스토어로 교체.
벡터+원문(Document)을 LangChain이 함께 관리 → chunks.json 따로 안 씀.
"""

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

import shared

DATA_DIR = Path(shared.__file__).resolve().parent / "data"

# 빌드 때와 같은 임베딩 (질문도 같은 방식으로 벡터화되어야 비교 가능)
_embeddings = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sroberta-multitask",
    encode_kwargs={"normalize_embeddings": True},
)

# 저장된 벡터스토어 로드 (allow_dangerous...: 로컬에서 만든 pkl 로드 허용)
_notes = FAISS.load_local(
    str(DATA_DIR / "lc_notes_index"), _embeddings, allow_dangerous_deserialization=True
)
_wiki = FAISS.load_local(
    str(DATA_DIR / "lc_wiki_index"), _embeddings, allow_dangerous_deserialization=True
)


def retrieve(question: str, top_k: int = 4):
    """노트+위키에서 검색해 관련 Document top_k 개 반환 (v2 rag.search 대응)"""
    hits = (
        _notes.similarity_search_with_score(question, k=top_k)
        + _wiki.similarity_search_with_score(question, k=top_k)
    )
    hits.sort(key=lambda pair: pair[1])   # 점수(거리) 작을수록 유사
    return [doc for doc, _score in hits[:top_k]]

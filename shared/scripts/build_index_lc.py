"""LangChain FAISS 인덱스 빌드 (v3용) — 로더(v2 재사용) → Document → FAISS 저장

실행: python -m shared.scripts.build_index_lc
결과: shared/data/lc_notes_index/ , shared/data/lc_wiki_index/
"""

from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from shared.ingest.markdown_loader import load_and_chunk_notes
from shared.ingest.wiki_loader import load_and_chunk_wiki

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# v2 embedding.py 를 LangChain 래퍼로 (같은 모델, 정규화)
embeddings = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sroberta-multitask",
    encode_kwargs={"normalize_embeddings": True},
)


def build(chunks: list[dict], name: str):
    # 우리 조각 {text, source} → LangChain Document 로 변환
    docs = [
        Document(page_content=c["text"], metadata={"source": c["source"]})
        for c in chunks
    ]
    # 임베딩 + FAISS 생성 + 저장을 한 번에 (v2의 build_index 를 압축)
    store = FAISS.from_documents(docs, embeddings)
    store.save_local(str(DATA_DIR / name))
    print(f"✅ {name}: 조각 {len(docs)}개")


if __name__ == "__main__":
    print("노트 인덱스 빌드 중...")
    build(load_and_chunk_notes(), "lc_notes_index")
    print("위키 인덱스 빌드 중...")
    build(load_and_chunk_wiki(), "lc_wiki_index")

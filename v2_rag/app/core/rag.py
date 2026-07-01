"""RAG 검색 — 질문에 관련된 노트/위키 조각을 FAISS에서 찾는다"""

import json
from pathlib import Path

import faiss
import numpy as np

import shared
from shared import embedding

# shared/data 위치 (shared 패키지 기준으로 계산 → 어디서 실행하든 안정적)
DATA_DIR = Path(shared.__file__).resolve().parent / "data"


def _load_index(name: str):
    """저장된 FAISS 인덱스 + 조각 메타 불러오기"""
    index = faiss.read_index(str(DATA_DIR / name / "index.faiss"))
    with open(DATA_DIR / name / "chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks


# import 시 1회 로드 (노트 인덱스)
_notes_index, _notes_chunks = _load_index("notes_index")
_wiki_index, _wiki_chunks = _load_index("wiki_index")

def _search_one(index, chunks, qvec, top_k):
    """인덱스 하나에서 top_k 검색"""
    scores, ids = index.search(qvec, top_k)
    results = []
    for score, idx in zip(scores[0], ids[0]):
        chunk = chunks[idx]
        results.append({
            "text": chunk["text"],
            "source": chunk["source"],
            "score": float(score),
        })
    return results


def search(question: str, top_k: int = 4) -> list[dict]:
    """노트 + 위키 두 인덱스를 검색해 합친 뒤 상위 top_k 반환"""
    qvec = embedding.embed([question])
    qvec = np.asarray(qvec, dtype="float32")

    # 두 인덱스 각각 검색
    notes = _search_one(_notes_index, _notes_chunks, qvec, top_k)
    wiki = _search_one(_wiki_index, _wiki_chunks, qvec, top_k)

    # 합쳐서 점수순 정렬 → 상위 top_k
    merged = notes + wiki
    merged.sort(key=lambda r: r["score"], reverse=True)
    return merged[:top_k]

"""인덱스 빌드 스크립트 (1회 실행) — 노트/위키 → 임베딩 → FAISS 인덱스 저장"""

import json
from pathlib import Path

import faiss
import numpy as np

from shared import embedding
from shared.ingest.markdown_loader import load_and_chunk_notes
from shared.ingest.wiki_loader import load_and_chunk_wiki

# 저장 위치: shared/data
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def build_index(chunks: list[dict], out_dir: Path):
    """청킹 목록 → 임베딩 → FAISS 인덱스 저장"""
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. 청킹 텍스트만 뽑아서 임베딩
    texts = [chunk["text"] for chunk in chunks]
    vectors = embedding.embed(texts)                # (N, 768) shape
    vectors = np.array(vectors).astype("float32")   # FAISS는 float32 필요

    # 2. FAISS 인덱스 생성
    dim = vectors.shape[1]                          # 임베딩 차원 (768)
    index = faiss.IndexFlatIP(dim)                  # 내적(코사인) 기반 인덱스
    index.add(vectors)

    # 3. FAISS 인덱스 저장
    faiss.write_index(index, str(out_dir / "index.faiss"))
    with open(out_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"✅ 저장: {out_dir.name}  (조각 {len(chunks)}개, {dim}차원)")


if __name__ == "__main__":
    print("노트 인덱스 빌드 중...")
    notes = load_and_chunk_notes()
    build_index(notes, DATA_DIR / "notes_index")

    print("위키 인덱스 빌드 중...")           
    wiki = load_and_chunk_wiki()              
    build_index(wiki, DATA_DIR / "wiki_index")

"""임베딩 모델 래퍼 — 글을 의미 벡터로 바꾸는 공용 모듈 (노트·위키 공통)"""

from sentence_transformers import SentenceTransformer

MODEL_NAME = "jhgan/ko-sroberta-multitask"   # 한국어 특화 임베딩 모델

_model = SentenceTransformer(MODEL_NAME)

def embed(texts: list[str]):
    return _model.encode(texts, normalize_embeddings=True)
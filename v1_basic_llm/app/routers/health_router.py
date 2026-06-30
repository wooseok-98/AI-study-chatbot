"""GET /health — 서버 생존 확인 엔드포인트 (보일러플레이트)"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}

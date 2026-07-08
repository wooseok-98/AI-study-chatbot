"""위키피디아 로딩 + 청킹 — MediaWiki API로 문서를 받아 문단 단위로 조각낸다"""

import time

import requests

API_URL = "https://ko.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "AI-study-chatbot/1.0 (learning project)"}

TOPICS = [
    "순환 신경망",
    "장단기 메모리",
    "합성곱 신경망",
    "트랜스포머 (기계 학습)",
    "인공 신경망",
    "딥 러닝",
    "자연어 처리",
    "기계 학습",
    "RAG",
    "LangChain",
    "LangGraph"
]

CHUNK_SIZE = 400


def _fetch(title: str):
    """위키 문서의 제목·본문(순수 텍스트)을 가져온다. 없으면 (None, None)"""
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,   # HTML 대신 순수 텍스트
        "redirects": 1,     # 리다이렉트 따라가기
        "titles": title,
        "format": "json",
    }
    resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
    try:
        data = resp.json()                  # 응답이 JSON 아니면(rate limit 등) 예외
    except ValueError:
        return None, None
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None, None
    page = next(iter(pages.values()))       # 결과 첫 문서
    if "missing" in page or not page.get("extract"):
        return None, None
    return page["title"], page["extract"]


def load_and_chunk_wiki() -> list[dict]:
    chunks = []
    for topic in TOPICS:
        time.sleep(0.3)   # rate limit 회피용 짧은 딜레이
        title, text = _fetch(topic)
        if text is None:
            print(f"⚠️  없음/실패: {topic}")
            continue
        source = f"wiki:{title}"
        for chunk in split_by_paragraph(text):
            chunks.append({"text": chunk, "source": source})
        print(f"✅ {title}")
    return chunks


def split_by_paragraph(text: str, size: int = CHUNK_SIZE) -> list[str]:
    """문단들을 이어붙여 ~size 글자 단위로 자른다"""
    chunks = []
    current = ""
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) > size and current:
            chunks.append(current.strip())
            current = para
        else:
            current += "\n" + para
    if current.strip():
        chunks.append(current.strip())
    return chunks

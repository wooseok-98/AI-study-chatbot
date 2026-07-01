"""노트 로딩 + 청킹 — AI-study 마크다운 노트를 ## 섹션 단위 조각으로 자른다

반환 형식: [{"text": 조각내용, "source": "07_RAG/1-1_....md"}, ...]
  - text   : 검색·임베딩 대상이 되는 조각 내용
  - source : 출처 (나중에 "이 노트 참고했어요" 표시용)
"""

from pathlib import Path

# AI-study 노트 폴더 (이 프로젝트 바깥, 상위 레포에 위치)
NOTES_DIR = Path(__file__).resolve().parents[4] / "AI-study"


def load_and_chunk_notes() -> list[dict]:
    """모든 .md 노트를 읽어 ## 섹션 단위로 청킹"""
    chunks: list[dict] = []

    for md_file in NOTES_DIR.rglob("*.md"):
        # 마크다운 파일 읽기
        text = md_file.read_text(encoding="utf-8")    # 내용
        source = str(md_file.relative_to(NOTES_DIR))  # 출처

        # ## 헤더 기준으로 섹션 나누기
        for section in split_by_header(text):
            chunks.append({"text": section, "source": source})

    return chunks


def split_by_header(text: str) -> list[str]:
    """마크다운 텍스트를 ## 헤더 기준으로 섹션 리스트로 나눈다."""
    sections = []   # 완성 섹션
    current = []    # 현재 만들고 있는 섹션

    for line in text.splitlines():
        if line.startswith("## ") and current:
            # 새로운 섹션 시작, 이전 섹션 저장
            sections.append("\n".join(current).strip())
            current = [line]  # 새 섹션 시작
        else:
            # 새로운 섹션 아니면, 현재 섹션에 추가
            current.append(line)

    # 마지막 섹션 추가
    if current:
        sections.append("\n".join(current).strip())

    return sections

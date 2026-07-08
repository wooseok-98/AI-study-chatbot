# v2 — 노트 RAG (Multi-Source RAG)

학습 노트와 위키피디아를 검색해 **근거 기반으로 답하는** 한국어 RAG 챗봇
프레임워크 없이 RAG 파이프라인을 직접 구현 (임베딩·FAISS·청킹·검색·생성)

---

## 1. 개요

v1(순수 대화)에 **검색(Retrieval)**을 얹어, 질문 관련 자료를 찾아 근거로 답변
두 소스를 함께 검색하는 **멀티소스 RAG**

| 소스 | 내용 | 청킹 방식 |
|------|------|-----------|
| 📒 학습 노트 | `AI-study/**/*.md` (450 조각) | `##` 헤더 기준 |
| 📘 위키피디아 | AI/ML 주제 문서 (313 조각) | 문단 ~400자 |

**핵심 동작**
- 질문 관련 조각을 두 인덱스에서 검색 → 점수순 병합
- 검색 근거로만 답변, 없으면 "모른다" (할루시네이션 억제)
- 답변에 참고 출처(노트/위키) 표시
- v1의 멀티턴·DB 영속 유지

---

## 2. 동작 흐름

```
[준비 · 1회]  python -m shared.scripts.build_index
  노트/위키 문서 → 청킹 → 임베딩 → FAISS 저장
  결과물: notes_index, wiki_index (두 인덱스 폴더)

[서비스 · 매 질문]  POST /chat
  ① 질문 → 임베딩 (질문도 벡터로)
  ② 두 인덱스(노트·위키) 검색 → 병합 → 근거 조각 top_k
  ③ 근거 + 질문 → grounding 프롬프트 → Claude 호출
  ④ 답변 + 출처 반환
```

- **준비**: 재료를 미리 벡터로 바꿔 인덱스로 저장 (노트 바뀔 때만 다시)
- **서비스**: 매 질문마다 검색 후 근거 기반 생성

---

## 3. 폴더 구조

```
v2_rag/
├── main.py                    # FastAPI 앱 (루트 .env 로드 + shared 경로)
├── app/
│   ├── routers/               # /chat, /chat/{sid}/history, /health
│   ├── controllers/
│   │   └── chat_controller.py # RAG 흐름 + 멀티턴 + DB 연결
│   ├── core/
│   │   ├── rag.py             # 검색 (노트+위키 병합)
│   │   └── llm.py             # grounding 생성
│   └── schemas/
└── static/                    # 채팅 UI (v1 재활용)

../shared/                     # 버전 공통 자산
├── embedding.py               # 글→벡터 (ko-sroberta)
├── ingest/
│   ├── markdown_loader.py     # 노트 로딩·헤더 청킹
│   └── wiki_loader.py         # 위키 API(requests)·문단 청킹
├── scripts/build_index.py     # 인덱스 빌드 (1회)
└── data/
    ├── notes_index/           # 노트 벡터+메타
    └── wiki_index/            # 위키 벡터+메타
```

> v1과 달리 `core/`에 `rag.py` 추가, 데이터·인덱스 로직은 전부 `shared/`

---

## 4. 핵심 개념

**임베딩** — 글을 의미 벡터로 (비슷한 뜻 = 비슷한 벡터)
- 모델: `jhgan/ko-sroberta-multitask` (한국어, 768차원)
- 정규화 → 내적 = 코사인 유사도

**FAISS** — 벡터 수천 개 중 가까운 것 빠르게 검색
- `IndexFlatIP` (내적 기반 정확 검색)
- **벡터만 저장** → 원문·출처는 `chunks.json`에 따로 (위치로 짝맞춤)

**청킹** — 문서를 의미 조각으로
- 노트: `##` 헤더 기준 (섹션 구조 활용)
- 위키: 문단을 ~400자로 그룹핑

**멀티소스 병합** — "소스 하나 = 인덱스 하나"
```
질문 → 노트 검색(top_k) + 위키 검색(top_k) → 합쳐서 점수순 → 상위 top_k
```
- 두 소스 같은 모델로 임베딩 → 점수 직접 비교 가능
- 노트에 없는 주제는 위키가 보완

**grounding 프롬프트** — 근거 기반 답변
- "제공된 노트만 근거로 답해, 없으면 모른다고 해"

---

## 5. 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. API 키 (루트 .env)
cp v1_basic_llm/.env .env      # 또는 직접 ANTHROPIC_API_KEY 입력

# 3. 인덱스 빌드 (최초 1회, chatbot_project 에서)
python -m shared.scripts.build_index

# 4. 서버 실행
cd v2_rag
python main.py                 # http://localhost:8000
```

> 인덱스는 `shared/data/`에 생성 (git 제외). 노트/위키가 바뀌면 빌드만 다시

---

## 6. v1 대비 변경점

| | v1 | v2 |
|---|---|---|
| 답변 근거 | LLM 일반 지식 | **검색된 노트·위키** |
| 새 파일 | — | `rag.py`, 로더·임베딩·빌드(shared) |
| llm.py | `chat()` | `answer_with_context()` (grounding) |
| 소스 | 없음 | 노트 + 위키 (멀티소스) |
| 할루시네이션 | 그대로 | 근거 없으면 "모른다" |

---

## 7. 구현 체크리스트

- [x] 노트 로딩·청킹 (`markdown_loader`)
- [x] 임베딩 래퍼 (`embedding`)
- [x] FAISS 인덱스 빌드 (`build_index`)
- [x] 검색 (`rag.py`)
- [x] grounding 생성 (`llm.py`)
- [x] controller 연결 (멀티턴+DB+출처)
- [x] 위키 소스 추가 + 병합

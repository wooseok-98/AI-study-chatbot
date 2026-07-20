# 📚 AI 학습 도우미 챗봇 (Study Buddy Chatbot)

내 학습 노트와 위키피디아를 근거로 답하는 한국어 RAG 챗봇
`기본 대화 → RAG → LangChain → LangGraph 에이전트` 순으로 발전시킨 학습 프로젝트

---

## 1. 개요

부트캠프에서 정리한 학습 노트(`AI-study/**/*.md`)와 위키피디아를 검색해 **근거 기반으로 답하는** 챗봇
같은 챗봇을 4단계로 발전시키며 RAG·LangChain·LangGraph를 학습

| 소스 | 내용 |
|------|------|
| 📒 학습 노트 | RNN/LSTM, RAG, LangChain, FastAPI 등 (450 조각) |
| 📘 위키피디아 | AI/ML 주제 문서 (300+ 조각) |
| 🌐 웹 (v4) | DuckDuckGo 실시간 검색 |

**주요 기능**
- 근거 기반 답변 + **출처 인용**
- **할루시네이션 억제** — 근거 없으면 "모른다"
- **멀티턴 대화** — SQLite 영속 (새로고침·재시작에도 보존)
- **에이전트 도구 선택 (v4)** — 노트/위키/웹 중 LLM이 스스로 판단
- REST API + 채팅 UI

```
POST /chat
{ "question": "...", "session_id": "..." }
```

---

## 2. 기술 스택

| 구분 | 기술 |
|------|------|
| LLM | Claude (haiku) — v3+는 `langchain-anthropic` |
| 임베딩 | `jhgan/ko-sroberta-multitask` (한국어) |
| 벡터 스토어 | FAISS |
| 오케스트레이션 | LangChain (LCEL) · LangGraph (StateGraph / ReAct) |
| 웹 검색 | DuckDuckGo (v4) |
| 서빙 | FastAPI + Uvicorn |
| 저장 | SQLite (대화 영속) |
| 프론트 | 정적 채팅 UI (HTML/CSS/JS) |

---

## 3. 폴더 구조

동일 챗봇을 4개 버전으로 단계적 발전 (각 버전 독립 실행)

```
chatbot_project/
├── v1_basic_llm/          # 기본 대화 챗봇 (Claude + SQLite 멀티턴)     
├── v2_rag/                # 멀티소스 RAG (프레임워크 없이 직접 구현)     
├── v3_langchain/          # LCEL 체인으로 재구성                        
├── v4_langgraph/          # ReAct 에이전트 (도구 선택)                  
│   └── app/
│       ├── routers/       #   엔드포인트
│       ├── controllers/   #   흐름 제어 + DB
│       └── core/          #   llm / rag / (chains: v3) (tools·graph: v4)
│
└── shared/                # 버전 공통 인프라
    ├── db.py              #   대화 SQLite
    ├── embedding.py       #   글→벡터 (ko-sroberta)
    ├── ingest/            #   markdown_loader / wiki_loader
    ├── scripts/           #   build_index (v2) / build_index_lc (v3·v4)
    └── data/              #   *_index (git 제외, 빌드 산출물)

```

**설계 규칙**
- 3계층 분리: `routers → controllers → core`
- `core/` = **버전별 오케스트레이션** (raw → LangChain → LangGraph) — 버전 간 차이가 여기 집중
- 인덱스·DB·로더는 `shared/`에 공유, UI(static)는 버전별 유지

---

## 4. 구현 단계

버전별 커밋으로 발전 과정 기록

### v1 — 기본 대화 챗봇
- FastAPI 3계층 + Claude API 멀티턴 대화
- SQLite 대화 영속 (새로고침·재시작에도 보존)

### v2 — 멀티소스 RAG (프레임워크 없이 직접)
- 노트+위키 인덱싱(chunking → 임베딩 → FAISS), top-k 검색 → grounding 응답
- 출처 표시, 근거 없으면 "모름", 두 소스 점수순 병합
- RAG 원리를 밑바닥부터 직접 구현

### v3 — LangChain 리팩토링
- v2 로직을 LCEL 체인(`retrieve | prompt | llm | parser`)으로 재구성
- raw 구현 ↔ 프레임워크 구현 대조 (결과 동일 검증)

### v4 — LangGraph ReAct 에이전트
- 도구 3개(노트·위키·웹) + StateGraph ReAct 루프
- **LLM이 질문에 따라 도구를 스스로 선택** (개념→노트/위키, 실시간→웹)

---

## 5. 실행

각 버전 독립 실행. 공통: venv + 루트 `.env`(`ANTHROPIC_API_KEY`)

```bash
cp .env.example .env                        # 루트에 API 키 입력

# ── v2 (직접 구현 RAG) ──
pip install -r v2_rag/requirements.txt
python -m shared.scripts.build_index        # notes_index, wiki_index
cd v2_rag && python main.py                 # http://localhost:8000

# ── v3 (LangChain) / v4 (LangGraph 에이전트) ──
pip install -r v4_langgraph/requirements.txt
python -m shared.scripts.build_index_lc     # lc_notes_index, lc_wiki_index
cd v4_langgraph && python main.py           # (v3도 동일 인덱스 사용)
```

> 인덱스는 `shared/data/`에 생성 (git 제외, 빌드 최초 1회)
> v1은 인덱스 불필요 — `cd v1_basic_llm && python main.py`

---

## 6. 회고
[AI 학습 도우미 챗봇 프로젝트 - 벨로그 회고](https://velog.io/@dan9872/series/AI-%EC%B1%97%EB%B4%87-%EC%A0%9C%EC%9E%91-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-%EA%B8%B0%EC%B4%88%EB%B6%80%ED%84%B0-LangGraph%EA%B9%8C%EC%A7%80)

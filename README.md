# 📚 AI 학습 도우미 챗봇 (Study Buddy Chatbot)

학습 노트와 위키피디아를 근거로 답하는 한국어 RAG 챗봇
`RAG → LangChain → LangGraph` 순으로 발전시키는 학습용 프로젝트

> **진행 상태**: v1(기본 대화)·v2(멀티소스 RAG)·v3(LangChain) 완료 / v4(LangGraph)·v5(파인튜닝) 예정

---

## 1. 개요

한국어 질문에 대해 **두 소스**를 근거로 답하는 학습 도우미

| 소스 | 내용 |
|------|------|
| 📒 학습 노트 | `AI-study/**/*.md` (RNN/LSTM, RAG, LangChain, FastAPI 등) |
| 📘 공식 문서 | LangChain·FastAPI 등 공식 docs 또는 웹 검색 |

**주요 기능**
- 소스 선택 응답 — 노트 / 공식 문서 / 둘 다 (자동 라우팅 + 수동 지정)
- 근거 인용 — 답변마다 참고 출처 표시
- 할루시네이션 억제 — 검색 근거 기반 답변, 없으면 "모름" 응답
- 멀티턴 대화 — 이전 맥락 유지
- 에이전트 폴백 — 노트에 없으면 공식 문서/웹으로 전환
- REST API — FastAPI 서빙 + 채팅 UI

**소스 라우팅 흐름**

```
질의 ─▶ 라우터(소스 판단)
         ├─▶ 📒 노트 RAG
         ├─▶ 📘 공식문서 RAG
         └─▶ 🔀 둘 다 → 병합·리랭킹
                  └─▶ 생성(근거 + 출처)
```

```
POST /chat
{ "question": "...", "source": "auto|notes|docs|both", "session_id": "..." }
```

---

## 2. 기술 스택

| 구분 | 기술 |
|------|------|
| LLM (1차) | 외부 API — Gemini / Claude (provider 추상화로 스왑) |
| LLM (2차) | 한국어 오픈모델 LoRA/QLoRA 파인튜닝 |
| 임베딩 | `BAAI/bge-m3` 또는 `jhgan/ko-sroberta-multitask` |
| 벡터 스토어 | FAISS (`IndexFlatIP`) |
| 오케스트레이션 | LangChain (LCEL), LangGraph (StateGraph / ReAct) |
| 평가 | RAGAS (context_recall, faithfulness, factual_correctness) |
| 서빙 | FastAPI + Uvicorn |
| 프론트 | 정적 채팅 UI (HTML/CSS/JS) |

---

## 3. 폴더 구조

동일 챗봇을 4개 버전으로 단계적 발전

```
chatbot_project/
├── v1_basic_llm/          # 기본 대화 챗봇 (API + SQLite)          ✅
├── v2_rag/                # 노트+위키 RAG (프레임워크 없이 직접)   ✅
├── v3_langchain/          # LCEL 체인으로 재구성                   ✅
├── v4_langgraph/          # 소스 라우팅 에이전트                   (예정)
│   └── app/
│       ├── routers/       #   엔드포인트
│       ├── controllers/   #   흐름 제어
│       └── core/          #   llm.py / rag.py / chains.py / graph.py
│
├── shared/                # 버전 공통 자산 (인프라)
│   ├── db.py              #   대화 SQLite
│   ├── embedding.py       #   글→벡터 (ko-sroberta)
│   ├── ingest/            #   markdown_loader / wiki_loader
│   ├── scripts/           #   build_index (v2) / build_index_lc (v3)
│   └── data/              #   notes_index, wiki_index, lc_* (git 제외)
│
└── finetune/              # (v5 예정) make_dataset / train_lora / compare
```

**설계 규칙**
- 3계층 분리: `routers → controllers → core`
- `core/` = 버전별 오케스트레이션 (raw → LangChain → LangGraph)
- 인덱스·DB·로더는 `shared/`에 공유, UI(static)는 버전별 유지
- 실무는 git 브랜치/태그로 버전 관리가 정석. 비교 목적상 폴더 분리

---

## 4. 구현 단계

버전별 커밋으로 발전 과정 기록

### v1 — 기본 대화 챗봇
- FastAPI + LLM API 연동, 멀티턴 대화
- `core/llm.py` provider 추상화 우선 설계
- ✅ 채팅 UI에서 한국어 멀티턴 대화

### v2 — 노트 RAG (직접 구현)
- 노트 인덱싱(chunking → 임베딩 → FAISS), top-k 검색 → grounding 응답
- 출처 표시, 근거 없으면 "모름" 응답
- 프레임워크 없이 RAG 원리 직접 구현
- ✅ 노트 질문 정답 + 출처, RAGAS 점수 산출

### v3 — LangChain 리팩토링
- v2 로직을 LCEL 체인으로 재구성 (동일 기능)
- raw 구현 ↔ 프레임워크 구현 대조
- ✅ v2 대비 동일 품질, 코드 간결화

### v4 — LangGraph 에이전트
- 공식 문서/웹 소스 추가
- 라우터 노드(소스 판단) + ReAct 폴백
- `source` 파라미터로 수동 지정 지원
- ✅ 잡담/노트/최신정보 질의별 소스 라우팅

### v5 — 파인튜닝 (확장)
- 한국어 오픈모델 LoRA 파인튜닝 (데이터: 노트 기반 Q&A)
- `core/llm.py`로 API ↔ 파인튜닝 스왑, 비교 실험
- ✅ 품질·속도·비용 비교표

### 마무리
- README 보강(아키텍처 다이어그램, 데모, 평가표)
- 핵심 경로 테스트, (선택) Docker화

---

## 5. 실행

각 버전 독립 실행. 공통: venv + 루트 `.env`(ANTHROPIC_API_KEY)

```bash
cp v1_basic_llm/.env .env                 # 루트에 API 키

# ── v2 (직접 구현 RAG) ──
pip install -r v2_rag/requirements.txt
python -m shared.scripts.build_index      # notes_index, wiki_index 빌드
cd v2_rag && python main.py               # http://localhost:8000

# ── v3 (LangChain) ──
pip install -r v3_langchain/requirements.txt
python -m shared.scripts.build_index_lc   # lc_notes_index, lc_wiki_index 빌드
cd v3_langchain && python main.py
```

> 인덱스는 `shared/data/`에 생성 (git 제외). 빌드는 최초 1회

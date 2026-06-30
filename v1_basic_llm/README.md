# v1 — 기본 대화 챗봇 (Basic LLM Chatbot)

Claude API를 FastAPI로 감싼 한국어 멀티턴 대화 챗봇
RAG·프레임워크 없이 **순수 API 호출**로 동작하며, 대화는 SQLite에 영속 저장

---

## 1. 목표

한국어 멀티턴 대화 챗봇을 로컬에서 기동 + 대화 영구 보존
**완료 기준** — "내 이름은 우석이야" → "내 이름 뭐였지?" 맥락 기억 / 새로고침·서버재시작에도 대화 유지

---

## 2. 동작 흐름

```
[브라우저] ──POST /chat──▶ [router] ─▶ [controller] ─▶ [core/llm.py] ──▶ [Claude API]
                                          │ 저장/조회                    │
                                          ▼                            │
                                     [shared/db.py] (SQLite)           │
                                                                       │
[브라우저] ◀────────────────응답──────────────────────────────────────────┘
```

- 서버는 브라우저와 Claude 사이의 **중간 다리**
- Claude API는 상태 없음(stateless) → **이전 대화 전체를 매번 함께 전송**해 멀티턴 구현
- 대화는 메모리가 아닌 **DB(SQLite)에 저장** → 서버 꺼도 보존
- 페이지 열 때 DB에서 지난 대화를 불러와 화면 복원

---

## 3. 폴더 구조

```
v1_basic_llm/
├── README.md
├── requirements.txt
├── .env.example          # API 키 템플릿 (실제 키는 .env, 커밋 금지)
├── main.py               # FastAPI 앱 + uvicorn 런처 (shared 경로 추가 + DB 초기화)
├── app/
│   ├── routers/
│   │   ├── health_router.py   # GET /health (서버 생존 확인)
│   │   └── chat_router.py     # POST /chat, GET /chat/{session_id}/history
│   ├── controllers/
│   │   └── chat_controller.py # ⭐ 멀티턴 흐름 + DB 저장/조회 (직접 구현)
│   ├── core/
│   │   └── llm.py             # ⭐ Claude API 호출 (직접 구현, 모델 교체 단일 지점)
│   └── schemas/
│       └── chat.py            # 요청/응답 Pydantic 모델
└── static/                    # 채팅 UI (index.html / style.css / script.js)

../shared/                     # 버전 공통 자산 (v1~v4 공유)
└── db.py                      # SQLite 대화 영속 (init_db / save_message / get_history)
   └── data/chat.db            # DB 파일 (자동 생성, git 제외)
```

> ⭐ 표시(`core/llm.py`, `chat_controller.py`)는 학습 핵심 → **직접 구현**
> 나머지(라우터·스키마·골격·UI)는 보일러플레이트
> DB는 모든 버전이 공유하므로 `shared/`에 위치 (UI는 버전마다 달라질 수 있어 버전별 유지)

---

## 4. 핵심 개념

**messages 형식** — 대화의 본체

```python
messages = [
    {"role": "user",      "content": "안녕"},
    {"role": "assistant", "content": "안녕하세요"},
    {"role": "user",      "content": "오늘 날씨 어때"},  # 마지막은 항상 user
]
```

**멀티턴 = 이전 대화를 매번 다시 전송** (stateless 보완)

```
DB에서 이전 대화 조회 → 이번 질문 추가(user) → 전체 전송 → 답변 → DB에 질문·답변 저장
```

- 대화는 `session_id`별로 **SQLite(`shared/db.py`)에 영속 저장** → 서버 재시작에도 보존
- `session_id`는 브라우저 `localStorage`에 고정 → 새로고침해도 같은 세션 유지
- `core/llm.py` = LLM 교체 단일 지점 → 모델(haiku↔opus)·파인튜닝 버전 교체 시 이 파일만 수정

**엔드포인트**

| 메서드 | 경로 | 역할 |
|--------|------|------|
| GET | `/health` | 서버 생존 확인 |
| POST | `/chat` | 질문 보내고 답변 받기 |
| GET | `/chat/{session_id}/history` | 지난 대화 불러오기 (UI 복원용) |
| GET | `/` | 채팅 화면(static) |

---

## 5. 실행 방법

```bash
pip install -r requirements.txt

cp .env.example .env          # .env 열어 ANTHROPIC_API_KEY 입력

python main.py                # http://localhost:8000

# 채팅 화면: http://localhost:8000
# 생존 확인: http://localhost:8000/health → {"status":"ok"}
```

> DB(`shared/data/chat.db`)는 서버 시작 시 자동 생성 (별도 설정 불필요)

---

## 6. 구현 체크리스트

- [x] 골격 기동 — `/health` 200 응답
- [x] `core/llm.py` — Claude 호출 함수
- [x] `chat_controller.py` — 멀티턴 + DB 저장/조회
- [x] `chat_router.py` — `POST /chat` + `GET /chat/{id}/history` 연결
- [x] 채팅 UI(static) 연결 + 세션 복원
- [x] 멀티턴 + 영속(새로고침·재시작) 테스트

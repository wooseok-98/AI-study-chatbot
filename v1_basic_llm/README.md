# v1 — 기본 대화 챗봇 (Basic LLM Chatbot)

Claude API를 FastAPI로 감싼 한국어 멀티턴 대화 챗봇
RAG·프레임워크 없이 **순수 API 호출**만으로 동작하는 첫 단계

---

## 1. 목표

한국어로 멀티턴 대화가 되는 챗봇을 로컬에서 기동
**완료 기준** — "내 이름은 우석이야" → "내 이름 뭐였지?" 에 맥락 기억하고 응답

---

## 2. 동작 흐름

```
[브라우저] ──POST /chat──▶ [router] ─▶ [controller] ─▶ [core/llm.py] ──▶ [Claude API]
                                          │ history 관리         │
[브라우저] ◀────응답─────────────────────────┴─────────────────────┘
```

- 서버는 브라우저와 Claude 사이의 **중간 다리**
- Claude API는 상태 없음(stateless) → **이전 대화 전체를 매번 함께 전송**해 멀티턴 구현

---

## 3. 폴더 구조

```
v1_basic_llm/
├── README.md
├── requirements.txt
├── .env.example          # API 키 템플릿 (실제 키는 .env, 커밋 금지)
├── main.py               # FastAPI 앱 + uvicorn 런처
└── app/
    ├── routers/
    │   ├── health_router.py   # GET /health (서버 생존 확인)
    │   └── chat_router.py     # POST /chat
    ├── controllers/
    │   └── chat_controller.py # ⭐ 입력 검증 + 멀티턴 history 관리 (직접 구현)
    ├── core/
    │   └── llm.py             # ⭐ Claude API 호출 (직접 구현, 모델 교체 단일 지점)
    └── schemas/
        └── chat.py            # 요청/응답 Pydantic 모델
```

> ⭐ 표시(`core/llm.py`, `chat_controller.py`)는 학습 핵심 → **직접 구현**
> 나머지(라우터·스키마·골격)는 보일러플레이트

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
사용자 입력 → history 추가(user) → 전체 전송 → 답변 → history 추가(assistant)
```

- v1은 `session_id`별로 메모리 딕셔너리에 history 저장 (DB는 추후 단계)
- `core/llm.py` = LLM 교체 단일 지점 → 모델(haiku↔opus)·파인튜닝 버전 교체 시 이 파일만 수정

---

## 5. 실행 방법

```bash
pip install -r requirements.txt

cp .env.example .env          # .env 열어 ANTHROPIC_API_KEY 입력

python main.py                # http://localhost:8000

# 생존 확인: http://localhost:8000/health → {"status":"ok"}
```

---

## 6. 구현 체크리스트

- [ ] 골격 기동 — `/health` 200 응답 확인
- [ ] `core/llm.py` — Claude 호출 함수 (messages 받아 답변 텍스트 반환)
- [ ] `chat_controller.py` — 세션별 history 관리 + 멀티턴
- [ ] `chat_router.py` — `POST /chat` 연결
- [ ] 멀티턴 대화 테스트 (이름 기억 여부)

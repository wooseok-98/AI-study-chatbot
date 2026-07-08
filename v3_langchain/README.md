# v3 — LangChain 리팩토링 (LCEL)

v2의 RAG를 **LangChain으로 재구성** — 기능은 동일하고, 검색·생성 조립을 프레임워크로
"프레임워크 없이(v2) ↔ 프레임워크로(v3)"를 대조하는 버전

---

## 1. 개요

v2와 **완전히 같은 멀티소스 RAG**(노트 + 위키)를, 직접 짠 코드 대신 LangChain 부품 + **LCEL 체인**으로 구현
- 로더·청킹·DB·웹 골격은 v2 그대로 재사용
- 임베딩·검색·생성 조립만 LangChain으로 교체

---

## 2. 동작 흐름

```
[준비 · 1회]  python -m shared.scripts.build_index_lc
  노트/위키 → Document 변환 → FAISS.from_documents → save_local
  결과물: lc_notes_index, lc_wiki_index

[서비스 · 매 질문]  chains.answer()
  질문 → LCEL 체인 → 답변
       (retrieve → prompt → llm → parser 를 파이프 | 로 연결)
```

---

## 3. 폴더 구조

```
v3_langchain/
├── main.py
├── app/
│   ├── routers/               # v2 그대로
│   ├── controllers/
│   │   └── chat_controller.py # chains.answer() 한 번 호출 + DB
│   ├── core/
│   │   ├── llm.py             # ChatAnthropic (모델 단일 지점)
│   │   ├── rag.py             # FAISS 벡터스토어 검색·병합 (retriever)
│   │   └── chains.py          # LCEL 체인 (retrieve|prompt|llm|parser)
│   └── schemas/
└── static/                    # v2 재활용

../shared/                     # 공통 자산
├── ingest/                    # 로더 (v2 그대로 재사용)
├── scripts/build_index_lc.py  # LangChain FAISS 빌드
└── data/
    ├── lc_notes_index/        # LangChain FAISS (노트)
    └── lc_wiki_index/         # LangChain FAISS (위키)
```

---

## 4. 핵심 개념 — LangChain 부품

| 부품 | 역할 |
|------|------|
| `Document` | 조각의 LangChain 표현 (`page_content` + `metadata`) |
| `HuggingFaceEmbeddings` | 글→벡터 (ko-sroberta 래핑) |
| `FAISS` 벡터스토어 | 임베딩·인덱스·원문을 함께 관리 (`from_documents`) |
| `retriever` | 질문 → 관련 Document 검색 |
| `ChatPromptTemplate` | `{context}` `{question}` 빈칸 있는 프롬프트 양식 |
| `MessagesPlaceholder` | 이전 대화(멀티턴) 삽입 자리 |
| `ChatAnthropic` | LangChain용 Claude |
| **LCEL 체인** | `retrieve \| prompt \| llm \| parser` 파이프 연결 |

**LCEL 체인 = 데이터가 파이프를 타고 모양이 바뀌는 파이프라인**
```
질문 dict → (검색) context 추가 → (프롬프트) 메시지 목록 → (LLM) AI응답 → (파서) 텍스트
```

---

## 5. v2 대비 변경점

| | v2 (직접 구현) | v3 (LangChain) |
|---|---|---|
| 임베딩 | `embedding.py` (SentenceTransformer) | `HuggingFaceEmbeddings` |
| 인덱스 | `build_index` + `chunks.json` 수동 | `FAISS.from_documents` / `save_local` |
| 검색 | `rag.search` (faiss 직접) | `vectorstore.similarity_search` |
| 생성 | `llm.answer_with_context` (f-string) | `ChatPromptTemplate` + `ChatAnthropic` |
| 조립 | controller가 수동으로 이음 | **LCEL 체인 한 줄** |
| 결과 | — | **동일** (검증 완료) |

> 핵심: 여러 파일 수동 조립 → 부품 + 체인으로 압축. 기능·품질은 동일

---

## 6. 실행 방법

```bash
# 1. 의존성 (langchain 포함)
pip install -r requirements.txt

# 2. API 키 (루트 .env)
cp v1_basic_llm/.env .env

# 3. LangChain 인덱스 빌드 (chatbot_project 에서)
python -m shared.scripts.build_index_lc

# 4. 서버
cd v3_langchain
python main.py                 # http://localhost:8000
```

---

## 7. 구현 체크리스트

- [x] LangChain FAISS 빌드 (`build_index_lc`)
- [x] retriever (`rag.py`)
- [x] ChatAnthropic (`llm.py`)
- [x] LCEL 체인 (`chains.py`)
- [x] controller 연결 (멀티턴+DB)
- [x] v2와 동일 결과 검증

# v4 — LangGraph ReAct 에이전트

LLM이 **도구를 스스로 골라** 검색 루프를 도는 에이전트
질문에 따라 노트·위키·웹 중 필요한 도구를 판단해서 답변

---

## 1. 개요

v3까지는 정해진 흐름(무조건 노트+위키 검색)이었다면, v4는 **LLM이 흐름을 운전**
- 도구를 주고, LLM이 "어떤 도구를 / 몇 번 / 언제까지 쓸지" 스스로 결정
- 이게 **에이전트**의 핵심 (고정 워크플로우와의 차이)

| 도구 | 언제 쓰나 |
|------|-----------|
| `search_notes` | 사용자 학습 노트 (AI/ML 개념) |
| `search_wiki` | 위키피디아 (일반 개념 설명) |
| `web_search` | 최신·실시간 정보 (DuckDuckGo) |

---

## 2. 동작 흐름 (ReAct 루프)

```
START → agent(LLM) ──도구 원함?──▶ tools 실행 ─────┐
             │  아니면(답변)                       │ (결과 갖고)
             ▼                                  │
            END  ◀──────────────── agent 로 복귀 ┘
```

- **agent**: LLM이 도구 호출 또는 최종 답변을 결정
- **tools**: 결정된 도구 실행 → 결과를 agent로
- **`tools_condition`**: 도구 원하면 tools, 아니면 END (루프 제어)
- 이 루프를 **LLM이 스스로** 반복·종료

**예시**
```
"RAG가 뭐야?"    → search_notes + search_wiki → 노트·위키 기반 답변
"오늘 AI 뉴스?"  → web_search → 웹 결과 기반 답변
```

---

## 3. 폴더 구조

```
v4_langgraph/
├── main.py
├── app/
│   ├── routers/               # v3 그대로
│   ├── controllers/
│   │   └── chat_controller.py # graph.answer() 호출 + DB
│   ├── core/
│   │   ├── llm.py             # ChatAnthropic (도구 바인딩 대상)
│   │   ├── rag.py             # search_notes / search_wiki (도구가 호출)
│   │   ├── tools.py           # 도구 3개 (@tool)
│   │   └── graph.py           # ReAct 에이전트 (StateGraph)
│   └── schemas/
└── static/                    # v3 재활용

../shared/                     # 인덱스(lc_*) v3 것 그대로 재사용
```

---

## 4. 핵심 개념

**`@tool`** — 함수를 도구로. docstring이 도구 설명 → LLM이 읽고 선택
```python
@tool
def search_notes(query: str) -> str:
    """사용자 학습 노트에서 검색한다. ..."""
```

**`bind_tools`** — LLM에 도구 목록 부여 → LLM이 `tool_calls` 생성 가능
```python
llm_with_tools = llm.bind_tools(TOOLS)
```

**`StateGraph` + `MessagesState`** — 메시지 목록을 상태로 갖는 그래프

**ReAct 루프** — `agent` ↔ `tools` 를 `tools_condition`으로 제어
```python
builder.add_conditional_edges("agent", tools_condition)  # 도구? tools : END
builder.add_edge("tools", "agent")
```

---

## 5. v3 대비 변경점

| | v3 (체인) | v4 (에이전트) |
|---|---|---|
| 오케스트레이션 | LCEL 고정 파이프 | **LangGraph StateGraph** |
| 검색 | 무조건 두 인덱스 | **LLM이 도구 선택** |
| 새 파일 | — | `tools.py`, `graph.py` |
| 없어진 것 | `chains.py` | (그래프로 대체) |
| 인덱스 | lc_*_index | **그대로 재사용** |

---

## 6. 실행 방법

```bash
pip install -r requirements.txt          # langgraph, ddgs 포함
cp v1_basic_llm/.env .env                # 루트 API 키

# 인덱스는 v3 것 재사용 — 없으면 빌드
python -m shared.scripts.build_index_lc

cd v4_langgraph
python main.py                            # http://localhost:8000
```

---

## 7. 구현 체크리스트

- [x] 도구 3개 (`tools.py`)
- [x] ReAct 에이전트 그래프 (`graph.py`)
- [x] 도구 바인딩 + 루프
- [x] controller 연결 (멀티턴+DB)
- [x] 도구 선택 검증 (노트/위키/웹 분기)

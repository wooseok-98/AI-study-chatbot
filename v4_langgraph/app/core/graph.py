"""LangGraph ReAct 에이전트 — LLM이 도구를 스스로 골라 검색 루프를 돈다

v3의 고정 LCEL 체인 → v4의 에이전트(그래프)로 교체.
LLM이 '어떤 도구를 쓸지 / 몇 번 쓸지 / 언제 멈출지'를 스스로 결정.
"""

from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.core.llm import llm
from app.core.tools import TOOLS

SYSTEM = (
    "너는 AI 학습 도우미야. 반드시 도구로 근거를 찾은 뒤 답해. 추측으로 답하지 마.\n"
    "도구 사용 원칙:\n"
    "- AI/ML 개념 질문: 먼저 search_notes(사용자 노트)를 쓰고, 부족하면 search_wiki 도 사용\n"
    "- 최신·실시간 정보(날씨, 뉴스, 최근 사건 등): 반드시 web_search 를 사용\n"
    "- 도구 결과에 답이 없을 때만 모른다고 해\n"
    "답변에 참고한 출처를 밝혀."
)

# LLM에 도구 바인딩 → LLM이 tool_calls(도구 호출 지시)를 만들 수 있게
llm_with_tools = llm.bind_tools(TOOLS)


def agent_node(state: MessagesState):
    """LLM 호출 — 도구를 부를지, 최종 답변할지 스스로 결정"""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# ── 그래프 조립 (ReAct 루프) ──
builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(TOOLS))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)  # 도구 원하면 tools, 아니면 END
builder.add_edge("tools", "agent")                        # 도구 결과 갖고 다시 agent
graph = builder.compile()


def answer(question: str, history_dicts: list) -> str:
    """controller 진입점 — 메시지 구성 → 그래프 실행 → 최종 답변"""
    messages = [SystemMessage(SYSTEM)]
    for m in history_dicts:
        messages.append(
            AIMessage(m["content"]) if m["role"] == "assistant" else HumanMessage(m["content"])
        )
    messages.append(HumanMessage(question))

    result = graph.invoke({"messages": messages})
    return result["messages"][-1].content   # 루프 끝난 뒤 마지막 AI 답변

import json
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection
from django.conf import settings
from .models import InquirySession

class GraphState(TypedDict):
    """
    대화의 전체 상태(이력, 단계, 메타데이터 등)를 담는 데이터 구조.
    """
    session_id: str
    messages: List[Dict[str, str]]
    current_step: int
    metadata: Dict[str, Any]
    logical_leaps: List[str]
    hidden_assumptions: List[str]

from .nodes import analyzer_node, questioner_node

def should_continue(state: GraphState):
    """
    질문 단계가 5회에 도달했거나 근본 원인이 파악되었는지 판단합니다.
    """
    if state["current_step"] > 5:
        return "end"
    return "continue"

async def summary_node(state: GraphState):
    """
    최종 근본 원인을 요약하고 사용자에게 동의를 구합니다.
    """
    return {"messages": state["messages"] + [{"role": "ai", "content": "지금까지의 대화를 바탕으로 근본 원인을 요약했습니다. 진단을 종료하고 기술서를 생성할까요?"}]}

def create_graph() -> StateGraph:
    """
    최종 완결된 LangGraph 상태 머신 구조를 생성합니다.
    """
    builder = StateGraph(GraphState)
    
    builder.add_node("analyzer", analyzer_node)
    builder.add_node("questioner", questioner_node)
    builder.add_node("summary", summary_node)
    
    builder.add_edge(START, "analyzer")
    builder.add_edge("analyzer", "questioner")
    
    # 조건부 전이 추가 (T023)
    builder.add_conditional_edges(
        "questioner",
        should_continue,
        {
            "continue": END, # API에서 다시 호출됨
            "end": "summary"
        }
    )
    builder.add_edge("summary", END)
    
    return builder

graph_builder = create_graph()

def get_compiled_graph(conn: Connection) -> Any:
    """
    PostgresSaver를 체크포인터로 사용하여 그래프를 컴파일합니다.
    """
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()
    return graph_builder.compile(checkpointer=checkpointer)

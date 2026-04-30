import logging
from typing import Any, TypedDict

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph
from psycopg import AsyncConnection

from .nodes import analyzer_node, questioner_node
from .state import GraphState

logger = logging.getLogger(__name__)


def router(state: GraphState) -> str:
    """
    다음 노드를 결정하는 라우팅 함수입니다.
    """
    if state.get("is_final_diagnosis", False) or state.get("current_step", 0) >= 5:
        return "await_consent"
    return END  # 사용자 입력 대기를 위해 END로 나감


async def await_consent_node(state: GraphState) -> dict[str, Any]:
    """
    사용자에게 진단 종료 동의를 요청하는 노드입니다.
    """
    return {
        "awaiting_consent": True,
        "messages": [
            {
                "role": "assistant",
                "content": "문제의 본질이 충분히 파악된 것 같습니다. "
                "진단을 종료하고 보고서를 생성할까요?",
            }
        ],
    }


def create_inquiry_graph() -> StateGraph:
    """
    진단 프로세스를 위한 LangGraph 워크플로우를 생성합니다.
    """
    workflow = StateGraph(GraphState)

    # 노드 추가
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("questioner", questioner_node)
    workflow.add_node("await_consent", await_consent_node)

    # 엣지 정의
    workflow.add_edge(START, "analyzer")
    workflow.add_edge("analyzer", "questioner")

    # 조건부 엣지
    workflow.add_conditional_edges(
        "questioner",
        router,
        {
            "await_consent": "await_consent",
            "analyzer": END,  # 루프는 외부(View)에서 제어
        },
    )
    workflow.add_edge("await_consent", END)

    return workflow


def get_compiled_graph(conn: AsyncConnection) -> Any:
    """
    체크포인터가 설정된 컴파일된 그래프를 반환합니다.
    """
    checkpointer = AsyncPostgresSaver(conn)
    workflow = create_inquiry_graph()
    return workflow.compile(checkpointer=checkpointer)

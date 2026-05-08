import logging
from typing import Any, Literal

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph

from .nodes import analyzer_node, questioner_node
from .state import InquiryState

logger = logging.getLogger(__name__)


def should_continue(
    state: InquiryState,
) -> Literal["questioner", "await_extension", "END"]:
    """
    현재 상태를 기반으로 다음 단계(노드)를 결정합니다.
    """
    root_cause = state.get("root_cause")
    turn_count = state.get("turn_count", 0)
    is_extension_approved = state.get("is_extension_approved", False)
    invalid_count = state.get("invalid_response_count", 0)

    # 1. 무의미한 답변 반복 시 종료
    if invalid_count >= 3:
        logger.info("Invalid response limit reached.")
        return "END"

    # 2. 근본 원인 도출됨 (상세화 가능 시 상세화 시도 로직은 nodes/edges에서 추가 처리 가능)
    if root_cause and root_cause.get("root_cause_found"):
        if not root_cause.get("can_detail"):
            return "END"
        # 상세화 가능한 경우 questioner로 보내서 상세 질문 생성
        return "questioner"

    # 3. 질의 횟수 제한 체크
    if turn_count >= 5 and not is_extension_approved:
        return "await_extension"

    return "questioner"


async def await_extension_node(_state: InquiryState) -> dict[str, Any]:
    """
    사용자에게 질의 연장 승인을 요청하는 노드입니다.
    """
    return {
        "messages": [
            {
                "role": "assistant",
                "content": "원인 파악을 위해 추가 질의가 필요합니다. 계속 진행할까요?",
            }
        ],
    }


def create_inquiry_graph() -> StateGraph:
    """
    진단 프로세스를 위한 LangGraph 워크플로우를 생성합니다.
    """
    workflow: StateGraph = StateGraph(InquiryState)

    # 노드 추가
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("questioner", questioner_node)
    workflow.add_node("await_extension", await_extension_node)

    # 엣지 정의
    workflow.add_edge(START, "analyzer")

    # analyzer 이후 다음 행방 결정
    workflow.add_conditional_edges(
        "analyzer",
        should_continue,
        {
            "questioner": "questioner",
            "await_extension": "await_extension",
            "END": END,
        },
    )

    # questioner에서 사용자 입력을 기다리기 위해 END로 나감
    workflow.add_edge("questioner", END)
    # 연장 승인 노드 후에도 사용자 입력을 기다림
    workflow.add_edge("await_extension", END)

    return workflow


async def get_compiled_graph(conn: Any) -> Any:
    """
    체크포인터가 설정된 컴파일된 그래프를 반환합니다.
    """
    checkpointer = AsyncPostgresSaver(conn)
    workflow = create_inquiry_graph()
    return workflow.compile(checkpointer=checkpointer)

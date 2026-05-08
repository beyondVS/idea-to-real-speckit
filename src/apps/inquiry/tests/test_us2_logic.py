import pytest
from langchain_core.messages import HumanMessage

from apps.inquiry.graph import create_inquiry_graph
from apps.inquiry.state import InquiryState


@pytest.mark.asyncio
async def test_inquiry_extension_transition():
    """
    T016: 질의 횟수가 5회에 도달했을 때 await_extension 노드로 전이되는지 확인합니다.
    """
    workflow = create_inquiry_graph()
    app = workflow.compile()

    # 5회 도달 상태 시뮬레이션
    state: InquiryState = {
        "messages": [HumanMessage(content="답변")],
        "turn_count": 5,
        "invalid_response_count": 0,
        "is_extension_approved": False,
        "root_cause": None,
        "metadata": {},
    }

    # analyzer 노드를 거친 후 should_continue 에지에 의해 await_extension으로 가야 함
    # 여기서는 간소화를 위해 가상 실행 경로 확인 또는 실제 invoke 결과 검증
    # (노드 로직이 mock 처리되지 않았으므로 turn_count가 6이 될 수 있음)

    # turn_count=5인 상태에서 analyzer 실행 시 should_continue는 'await_extension' 반환해야 함
    from apps.inquiry.graph import should_continue

    # state["root_cause"]가 없는(미도출) 상태여야 함
    result = should_continue(state)
    assert result == "await_extension"


@pytest.mark.asyncio
async def test_invalid_response_limit_termination():
    """
    T017: 무의미한 답변이 3회 반복될 때 END로 전이되는지 확인합니다.
    """
    from apps.inquiry.graph import should_continue

    state: InquiryState = {
        "messages": [HumanMessage(content="모름")],
        "turn_count": 3,
        "invalid_response_count": 3,
        "is_extension_approved": False,
        "root_cause": None,
        "metadata": {},
    }

    result = should_continue(state)
    assert result == "END"

import pytest
from langchain_core.messages import HumanMessage

from apps.inquiry.graph import should_continue
from apps.inquiry.state import InquiryState


@pytest.mark.asyncio
async def test_detailing_potential_transition():
    """
    T022: 근본 원인이 도출되었고 상세화가 가능한 경우(can_detail=True) questioner로 전이되는지 확인합니다.
    """
    state: InquiryState = {
        "messages": [HumanMessage(content="원인 도출 완료")],
        "turn_count": 3,
        "invalid_response_count": 0,
        "is_extension_approved": False,
        "root_cause": {
            "root_cause_found": True,
            "content": "추상적인 원인",
            "can_detail": True,
            "detailing_guide": "더 자세히 물어보세요",
        },
        "metadata": {},
    }

    result = should_continue(state)
    # can_detail이 True이므로 다시 질문 생성을 위해 questioner로 가야 함
    assert result == "questioner"


@pytest.mark.asyncio
async def test_no_detailing_potential_termination():
    """
    근본 원인이 명확하여 상세화가 불필요한 경우(can_detail=False) END로 전이되는지 확인합니다.
    """
    state: InquiryState = {
        "messages": [HumanMessage(content="원인 도출 완료")],
        "turn_count": 3,
        "invalid_response_count": 0,
        "is_extension_approved": False,
        "root_cause": {
            "root_cause_found": True,
            "content": "매우 구체적인 원인",
            "can_detail": False,
        },
        "metadata": {},
    }

    result = should_continue(state)
    assert result == "END"

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import HumanMessage

from apps.inquiry.nodes import analyzer_node
from apps.inquiry.state import InquiryState


@pytest.mark.asyncio
async def test_analyzer_node_metadata_and_root_cause():
    """
    T010: Analyzer Node가 사용자의 답변을 분석하여 메타데이터와 근본 원인(있을 경우)을 추출하는지 확인합니다.
    """
    state: InquiryState = {
        "messages": [HumanMessage(content="서버 로그에 권한 오류가 계속 찍혀요.")],
        "turn_count": 1,
        "invalid_response_count": 0,
        "is_extension_approved": False,
        "root_cause": None,
        "metadata": {},
    }

    with patch("apps.inquiry.nodes.safe_invoke_llm") as mock_invoke:
        # analyzer_node가 기대하는 평면 JSON 구조
        mock_invoke.return_value = (
            '{"persona": "개발자", "issue": "권한 오류", '
            '"root_cause_found": true, "content": "설정 파일 권한 오설정", '
            '"confidence_score": 0.9, "can_detail": true, "detailing_guide": "파일 소유자 확인"}'
        )

        new_state = await analyzer_node(state)

        assert new_state["metadata"]["persona"] == "개발자"
        assert new_state["root_cause"]["root_cause_found"] is True
        assert new_state["root_cause"]["content"] == "설정 파일 권한 오설정"
        assert new_state["root_cause"]["confidence_score"] == 0.9

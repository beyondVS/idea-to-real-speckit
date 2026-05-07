from unittest.mock import MagicMock, patch

import pytest

from apps.inquiry.nodes import analyzer_node


@pytest.mark.asyncio
async def test_analyzer_node_metadata_extraction():
    """
    T010: Analyzer Node가 사용자의 텍스트에서 메타데이터(페르소나)와 논리적 비약을 추출하는지 확인합니다.
    """
    state = {
        "session_id": "test-session",
        "messages": [
            {"role": "user", "content": "우리 팀의 생산성이 너무 낮은 것 같아요."}
        ],
        "current_step": 1,
        "metadata": {},
        "logical_leaps": [],
        "hidden_assumptions": [],
    }

    with patch("apps.inquiry.nodes.invoke_llm_with_retry") as mock_invoke:
        mock_response = MagicMock()
        mock_response.content = '{"metadata": {"persona": "팀 리더", "background": "생산성 저하 고민"}, "logical_leaps": ["생산성 저하의 구체적 지표 누락"], "hidden_assumptions": ["생산성이 높아야만 한다"]}'
        mock_invoke.return_value = mock_response

        # analyzer_node는 dict 형식의 상태를 업데이트하여 반환해야 함
        new_state = await analyzer_node(state)

        assert new_state["metadata"]["persona"] == "팀 리더"
        assert "생산성 저하의 구체적 지표 누락" in new_state["logical_leaps"]
        assert "생산성이 높아야만 한다" in new_state["hidden_assumptions"]

from unittest.mock import MagicMock, patch

import pytest

from apps.inquiry.nodes import questioner_node


@pytest.mark.asyncio
async def test_questioner_node_generation():
    """
    T016: Questioner Node가 이전 분석 결과를 바탕으로 심층 질문을 생성하는지 확인합니다.
    """
    state = {
        "session_id": "test-session",
        "messages": [{"role": "user", "content": "생산성이 낮아요."}],
        "current_step": 1,
        "metadata": {"persona": "팀장"},
        "logical_leaps": ["지표 부재"],
        "hidden_assumptions": ["도구 문제"],
    }

    with patch("apps.inquiry.nodes.invoke_llm_with_retry") as mock_invoke:
        mock_response = MagicMock()
        mock_response.content = "생산성을 측정하는 구체적인 지표가 있나요?"
        mock_invoke.return_value = mock_response

        new_state = await questioner_node(state)

        assert "생산성" in new_state["messages"][-1]["content"]
        assert new_state["current_step"] == 2

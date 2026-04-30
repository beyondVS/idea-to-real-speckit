from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse

from apps.inquiry.models import InquirySession


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_initial_chat_endpoint(async_client):
    """
    T011: 최초 채팅 시작 엔드포인트 통합 테스트.
    새로운 세션을 생성하고 초기 AI 응답을 반환하는지 검증합니다.
    """
    url = reverse("chat_api")

    with patch("apps.inquiry.graph.get_compiled_graph") as mock_get_graph:
        mock_graph = MagicMock()
        # Mocking the async stream or invoke response from graph
        mock_graph.ainvoke.return_value = {
            "messages": [{"role": "ai", "content": "어떤 생산성 문제가 있나요?"}],
            "current_step": 1,
        }
        mock_get_graph.return_value = mock_graph

        response = await async_client.post(
            url,
            {
                "session_id": None,
                "user_input": "우리 팀의 생산성이 너무 낮은 것 같아요.",
            },
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "session_id" in data["data"]
        assert data["data"]["ai_response"] == "어떤 생산성 문제가 있나요?"
        assert data["data"]["current_step"] == 1

        # Session should be created
        session_exists = await InquirySession.objects.filter(
            id=data["data"]["session_id"]
        ).aexists()
        assert session_exists is True

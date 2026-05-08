import uuid
from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from django.urls import reverse
from langchain_core.messages import HumanMessage
from psycopg import AsyncConnection


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_root_cause_presentation(async_client):
    """
    T011: 근본 원인 도출 시 UI에 리포트가 정상적으로 전달되는지 확인합니다.
    """
    session_id = str(uuid.uuid4())
    url = reverse("chat_api", kwargs={"session_id": session_id})

    with patch("apps.inquiry.graph.get_compiled_graph") as mock_get_graph, \
         patch("psycopg.AsyncConnection.connect", new_callable=AsyncMock) as mock_connect, \
         patch("apps.inquiry.views.llm_queue.enqueue", new_callable=AsyncMock) as mock_enqueue:
        
        # AsyncConnection mock 설정
        mock_conn = MagicMock(spec=AsyncConnection)
        mock_connect.return_value = mock_conn
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock()
        
        # enqueue 결과 mock 설정
        final_state = {
            "messages": [HumanMessage(content="원인이 도출되었습니다.")],
            "root_cause": {
                "root_cause_found": True,
                "content": "테스트 원인",
                "confidence_label": "매우 높음",
                "can_detail": False,
            },
            "turn_count": 3,
        }
        mock_enqueue.return_value = final_state

        response = await async_client.post(
            url,
            {
                "answer": "결과 보여줘",
            },
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["root_cause"]["content"] == "테스트 원인"
        assert data["root_cause"]["confidence_label"] == "매우 높음"

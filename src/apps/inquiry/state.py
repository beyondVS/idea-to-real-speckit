from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


class InquiryState(TypedDict):
    """
    진단 에이전트의 상태를 정의하는 클래스입니다.
    langchain-core의 AnyMessage와 langgraph의 add_messages를 활용합니다.
    """

    messages: Annotated[list[AnyMessage], add_messages]
    turn_count: int
    invalid_response_count: int
    is_extension_approved: bool
    root_cause: dict[str, Any] | None  # RootCause 엔티티 데이터
    metadata: dict[str, Any]  # 사용자 페르소나, 배경 지식 등

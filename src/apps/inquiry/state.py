import operator
from typing import Any, Annotated, TypedDict


class GraphState(TypedDict):
    """
    진단 에이전트의 상태를 정의하는 클래스입니다.
    """

    initial_input: str
    messages: Annotated[list[dict[str, str]], operator.add]
    current_step: int
    is_final_diagnosis: bool
    metadata: dict[str, Any]
    causal_chain: list[dict[str, str]]
    identified_assumptions: list[str]
    final_root_cause: str | None
    awaiting_consent: bool

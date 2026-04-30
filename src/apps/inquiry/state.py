from typing import Any, TypedDict


class GraphState(TypedDict):
    """
    진단 에이전트의 상태를 정의하는 클래스입니다.
    """

    initial_input: str
    messages: list[dict[str, str]]
    current_step: int
    is_final_diagnosis: bool
    metadata: dict[str, Any]
    causal_chain: list[dict[str, str]]
    identified_assumptions: list[str]
    final_root_cause: str | None
    awaiting_consent: bool

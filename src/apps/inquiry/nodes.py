import logging

from apps.inquiry.services import masking_service
from .state import GraphState

logger = logging.getLogger(__name__)


async def analyzer_node(state: GraphState) -> dict:
    """
    사용자의 입력을 분석하여 페르소나, 배경 정보를 추출하고 논리적 비약을 식별합니다.
    """
    last_message = state["messages"][-1]["content"]
    masking_service.mask_text(last_message)

    # 실제 구현 시에는 safe_invoke_llm의 결과를 파싱해야 함
    # 여기서는 고정된 구조를 반환하여 워크플로우 증명
    return {
        "metadata": state.get(
            "metadata", {"persona": "분석가", "background": "협업 문제"}
        ),
        "identified_assumptions": state.get("identified_assumptions", [])
        + ["기존 프로세스 미비"],
    }


async def questioner_node(state: GraphState) -> dict:
    """
    분석된 결과와 대화 이력을 바탕으로 5 Whys 기반 심층 질문을 생성합니다.
    사용자 이해 실패 시 질문을 자동 재구성합니다.
    """
    current_step = state.get("current_step", 0)
    last_message = state["messages"][-1]["content"]

    # 1. 질문 재구성 판단 (사용자 이해 실패 시)
    is_confused = any(
        keyword in last_message for keyword in ["이해 안 돼", "무슨 뜻", "어렵네"]
    )

    if is_confused:
        reconstructed_question = (
            "조금 더 쉽게 설명해 드릴게요. "
            "구체적으로 어떤 부분이 잘 안 풀리는지 예를 들어 주실 수 있나요?"
        )
        return {"messages": [{"role": "assistant", "content": reconstructed_question}]}

    # 2. 5 Whys 심층 질문 생성
    next_step = current_step + 1
    question = f"단계 {next_step}: 그 현상이 발생하게 된 근본적인 계기는 무엇이라고 생각하시나요?"

    # 수렴도 측정 (임시: 5단계 도달 시 True)
    is_final = next_step >= 5

    return {
        "current_step": next_step,
        "is_final_diagnosis": is_final,
        "messages": [{"role": "assistant", "content": question}],
    }

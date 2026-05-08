import json
import logging
import re
from typing import Any

from langchain_core.messages import SystemMessage

from core.llm import safe_invoke_llm

from .services import get_confidence_label, masking_service
from .state import InquiryState

logger = logging.getLogger(__name__)


async def analyzer_node(state: InquiryState) -> dict[str, Any]:
    """
    사용자의 답변을 분석하여 페르소나를 추출하고, 근본 원인 도출 여부 및 상세화 가능성을 판단합니다.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    # 마지막 사용자 메시지 추출 및 타입 안전성 확보
    last_msg = messages[-1]
    last_user_message = (
        last_msg.content if hasattr(last_msg, "content") else str(last_msg)
    )
    if not isinstance(last_user_message, str):
        last_user_message = str(last_user_message)

    masked_input = masking_service.mask_text(last_user_message)

    # 유효하지 않은 답변 감지 (FR-006)
    invalid_keywords = ["모름", "글쎄", "잘 기억 안 남", "모르겠어요", "생각 안 나요"]
    is_invalid = any(kw in last_user_message for kw in invalid_keywords)
    invalid_increment = 1 if is_invalid else 0

    prompt = f"""
    당신은 문제의 본질을 파악하는 숙련된 비즈니스 분석가입니다. 
    5-Why 기법을 활용하여 사용자의 답변을 분석하고 다음 정보를 추출하세요.
    
    [사용자 입력]
    {masked_input}
    
    [분석 요구사항]
    1. 사용자의 페르소나(역할)를 한 단어로 추출하세요.
    2. 현재까지의 맥락을 바탕으로 '근본 원인'이 도출되었는지 판단하세요.
    3. 근본 원인이 도출되었다면, 확신도(0.0~1.0)와 추가 상세 분석 가능 여부(can_detail)를 판단하세요.
    
    반드시 아래 JSON 형식으로만 응답하세요:
    {{
        "persona": "페르소나",
        "root_cause_found": true/false,
        "content": "도출된 근본 원인 내용 (없으면 null)",
        "confidence_score": 0.85,
        "can_detail": true/false,
        "detailing_guide": "상세화가 필요한 경우의 가이드 (없으면 null)"
    }}
    """

    response_text = safe_invoke_llm([SystemMessage(content=prompt)])

    try:
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        data = (
            json.loads(json_match.group()) if json_match else json.loads(response_text)
        )

        root_cause = None
        if data.get("root_cause_found"):
            score = data.get("confidence_score", 0.0)
            root_cause = {
                "root_cause_found": True,
                "content": data.get("content"),
                "confidence_score": score,
                "confidence_label": get_confidence_label(score),
                "can_detail": data.get("can_detail", False),
                "detailing_guide": data.get("detailing_guide"),
            }

        return {
            "metadata": {"persona": data.get("persona", "알 수 없음")},
            "root_cause": root_cause,
            "invalid_response_count": state.get("invalid_response_count", 0)
            + invalid_increment,
            "turn_count": state.get("turn_count", 0) + 1,
        }
    except Exception as e:
        logger.error(f"Analyzer Node 파싱 실패: {e}")
        return {
            "turn_count": state.get("turn_count", 0) + 1,
            "invalid_response_count": state.get("invalid_response_count", 0) + 1,
        }


async def questioner_node(state: InquiryState) -> dict[str, Any]:
    """
    현재까지의 분석 결과와 대화 이력을 바탕으로 다음 질의를 생성합니다.
    상세화가 필요한 경우 detailing_guide를 활용합니다.
    """
    turn_count = state.get("turn_count", 0)
    messages = state.get("messages", [])
    root_cause = state.get("root_cause")

    system_prompt = f"""
    당신은 문제의 근본 원인을 파악하는 5 Whys 전문가입니다. 
    현재 질의 단계: {turn_count}/5
    
    [가이드라인]
    - 친절하고 전문적인 톤을 유지하세요.
    - {f"현재 도출된 원인: {root_cause['content']}. 이 원인을 더 구체화하기 위한 질문을 던지세요. 가이드: {root_cause['detailing_guide']}" if root_cause and root_cause.get("can_detail") else "다음 심층 질문을 하나만 던지세요."}
    """

    response_content = safe_invoke_llm(
        [{"role": "system", "content": system_prompt}, *messages[-5:]]
    )

    return {
        "messages": [{"role": "assistant", "content": response_content}],
    }

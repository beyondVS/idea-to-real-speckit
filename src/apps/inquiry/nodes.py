import logging

from apps.inquiry.services import masking_service
from .state import GraphState

logger = logging.getLogger(__name__)


import json
import logging
import re
from typing import Any

from core.llm import safe_invoke_llm
from apps.inquiry.services import masking_service
from .state import GraphState

logger = logging.getLogger(__name__)


async def analyzer_node(state: GraphState) -> dict[str, Any]:
    """
    사용자의 입력을 분석하여 페르소나, 배경 정보를 추출하고 논리적 비약을 식별합니다. (FR-001)
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_user_message = messages[-1]["content"]
    # 마스킹 처리 (NFR-004)
    masked_input = masking_service.mask_text(last_user_message)

    prompt = f"""
    당신은 숙련된 비즈니스 분석가입니다. 사용자의 입력에서 문제의 본질을 파악하기 위한 기초 분석을 수행하세요.
    
    [사용자 입력]
    {masked_input}
    
    [분석 요구사항]
    1. 사용자의 페르소나(역할, 처지)를 한 단어로 추출하세요.
    2. 문제의 환경적 배경을 짧게 기술하세요.
    3. 사용자의 진술 이면에 깔린 '숨겨진 전제'나 '논리적 비약'을 최소 하나 이상 찾으세요.
    
    반드시 아래 JSON 형식으로만 응답하세요:
    {{
        "persona": "추출된 페르소나",
        "background": "추출된 배경 정보",
        "assumptions": ["전제1", "전제2"]
    }}
    """

    response_text = safe_invoke_llm([{"role": "system", "content": prompt}])
    
    try:
        # JSON 추출 (LLM이 마크다운 블록을 포함할 수 있으므로 정규식 사용)
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = json.loads(response_text)
            
        return {
            "metadata": {
                "persona": data.get("persona", "알 수 없음"),
                "background": data.get("background", "정보 부족"),
            },
            "identified_assumptions": state.get("identified_assumptions", []) + data.get("assumptions", []),
        }
    except Exception as e:
        logger.error(f"Analyzer Node 파싱 실패: {e}, 원문: {response_text}")
        return {
            "metadata": {"persona": "분석 실패", "background": "분석 실패"},
            "identified_assumptions": state.get("identified_assumptions", []) + ["분석 오류 발생"],
        }


async def questioner_node(state: GraphState) -> dict[str, Any]:
    """
    분석된 결과와 대화 이력을 바탕으로 5 Whys 기반 심층 질문을 생성합니다. (FR-002)
    """
    current_step = state.get("current_step", 0)
    messages = state.get("messages", [])
    metadata = state.get("metadata", {})
    assumptions = state.get("identified_assumptions", [])
    
    last_user_message = messages[-1]["content"] if messages else ""

    # 1. 질문 재구성 판단 (사용자 이해 실패 시)
    is_confused = any(
        keyword in last_user_message for keyword in ["이해 안 돼", "무슨 뜻", "어렵네", "모르겠어"]
    )

    system_prompt = f"""
    당신은 문제의 근본 원인을 파악하는 5 Whys 전문가입니다. 
    현재 단계: {current_step + 1}/5
    사용자 페르소나: {metadata.get('persona')}
    배경: {metadata.get('background')}
    식별된 전제/비약: {', '.join(assumptions[-3:])}
    
    [가이드라인]
    - 공감 어린 태도로 시작하되, 날카롭게 인과관계를 파고드세요.
    - 이전 답변의 논리적 허점이나 전제를 확인하는 질문을 우선하세요.
    - { "사용자가 이전 질문을 이해하지 못했습니다. 더 쉬운 용어와 구체적인 맥락을 사용하여 질문을 재구성하세요." if is_confused else "다음 심층 질문을 생성하세요." }
    - 질문은 짧고 명확하게 하나만 던지세요.
    """

    response_content = safe_invoke_llm([
        {"role": "system", "content": system_prompt},
        *messages[-5:] # 최근 대화 문맥 포함
    ])

    next_step = current_step + 1
    # 수렴도 측정은 실제로는 LLM이 판단해야 하나, 여기서는 단계 기반으로 우선 처리
    is_final = next_step >= 5

    return {
        "current_step": next_step,
        "is_final_diagnosis": is_final,
        "messages": [{"role": "assistant", "content": response_content}],
    }

import time
import logging
from typing import Any, Dict
from core.llm import get_llm, invoke_llm_with_retry
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)

async def analyzer_node(state: dict) -> Dict[str, Any]:
    """
    사용자의 답변을 분석하여 페르소나, 논리적 비약, 숨겨진 전제를 추출합니다.
    """
    start_time = time.time()
    import json
    messages = state.get("messages", [])
    last_user_message = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
    
    prompt = f"""
    당신은 문제 해결 전문가입니다. 다음 사용자의 답변을 분석하여, 
    페르소나, 논리적 비약, 숨겨진 전제를 JSON 형식으로 추출하세요.
    반드시 JSON 형식으로만 응답하세요.
    예시: {{"metadata": {{"persona": "...", "background": "..."}}, "logical_leaps": ["..."], "hidden_assumptions": ["..."]}}
    
    사용자 입력: {last_user_message}
    """
    
    llm = get_llm()
    try:
        response = invoke_llm_with_retry(llm, [SystemMessage(content=prompt)])
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        parsed_data = json.loads(content)
        
        duration = time.time() - start_time
        logger.info(f"Analyzer Node 실행 완료 (소요시간: {duration:.2f}s)") # T030 관련 로깅
        
        return {
            "logical_leaps": state.get("logical_leaps", []) + parsed_data.get("logical_leaps", []),
            "hidden_assumptions": state.get("hidden_assumptions", []) + parsed_data.get("hidden_assumptions", []),
            "metadata": {**state.get("metadata", {}), **parsed_data.get("metadata", {})}
        }
    except Exception as e:
        logger.error(f"Analyzer Node 실패: {e}")
        return {}

async def questioner_node(state: dict) -> Dict[str, Any]:
    """
    분석 결과를 바탕으로 근본 원인을 파헤치는 날카로운 질문을 생성합니다.
    """
    start_time = time.time()
    messages = state.get("messages", [])
    current_step = state.get("current_step", 1)
    
    prompt = f"""
    당신은 날카로운 질문을 던지는 분석가입니다. 
    현재까지 파악된 정보:
    - 페르소나: {state.get('metadata', {})}
    - 논리적 비약: {state.get('logical_leaps', [])}
    - 숨겨진 전제: {state.get('hidden_assumptions', [])}
    
    5 Whys 기법을 활용하여 사용자의 이전 답변에서 더 깊은 인과관계를 파고드는 질문을 하나만 던지세요.
    """
    
    llm = get_llm()
    try:
        response = invoke_llm_with_retry(llm, [SystemMessage(content=prompt)])
        duration = time.time() - start_time
        logger.info(f"Questioner Node 실행 완료 (소요시간: {duration:.2f}s)")
        
        return {
            "messages": messages + [{"role": "ai", "content": response.content}],
            "current_step": current_step + 1
        }
    except Exception as e:
        logger.error(f"Questioner Node 실패: {e}")
        return {"messages": messages + [{"role": "ai", "content": "죄송합니다. 분석 중 오류가 발생했습니다."}]}

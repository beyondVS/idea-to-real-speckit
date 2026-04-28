import logging
from typing import Any, Dict, Optional, List
from langchain_ollama import ChatOllama
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from django.conf import settings

logger = logging.getLogger(__name__)

def get_llm() -> ChatOllama:
    """
    ChatOllama 인스턴스를 반환합니다.
    """
    base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
    return ChatOllama(
        model="gemma4:e4b",
        base_url=base_url,
        temperature=0.7,
    )

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def invoke_llm_with_retry(llm: ChatOllama, messages: list) -> Any:
    """
    지수 백오프(Exponential Backoff)를 적용하여 LLM을 호출합니다.
    """
    try:
        return llm.invoke(messages)
    except Exception as e:
        logger.warning(f"LLM API 호출 실패, 재시도 중... Error: {e}")
        raise

def safe_invoke_llm(messages: list) -> str:
    """
    LLM 호출을 수행하고, 최종 실패 시 Fallback 전략을 수행합니다.
    """
    llm = get_llm()
    try:
        response = invoke_llm_with_retry(llm, messages)
        return response.content
    except Exception as e:
        logger.error(f"LLM 호출 최종 실패. Fallback 적용. Error: {e}")
        # Fallback 전략: 현재 세션 상태를 유지하고 사용자에게 양해를 구하는 메시지 반환
        return "죄송합니다. 현재 AI 진단 엔진 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요."

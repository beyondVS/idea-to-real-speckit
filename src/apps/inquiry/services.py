import json
import logging
from typing import Dict, Any
from .models import InquirySession, ProblemSpecification

logger = logging.getLogger(__name__)

async def generate_problem_specification(session_id: str, state: Dict[str, Any]) -> ProblemSpecification:
    """
    진단 결과를 바탕으로 구조화된 Markdown 및 JSON 기술서를 생성합니다.
    
    이 함수는 LangGraph 상태에 저장된 페르소나, 논리적 비약, 숨겨진 전제 및
    전체 대화 이력을 가공하여 최종 결과물 엔티티를 생성합니다. (T024 완결)
    
    Args:
        session_id: 진단 세션 UUID
        state: LangGraph 최종 상태 객체
        
    Returns:
        ProblemSpecification: 생성된 명세서 객체
    """
    try:
        session = await InquirySession.objects.aget(id=session_id)
        
        metadata = state.get("metadata", {})
        logical_leaps = state.get("logical_leaps", [])
        hidden_assumptions = state.get("hidden_assumptions", [])
        messages = state.get("messages", [])
        
        # 1. JSON 구조화 (Full Spec)
        content_json = {
            "session_id": session_id,
            "analysis": {
                "persona": metadata.get("persona", "미확인"),
                "background": metadata.get("background", "미확인"),
                "logical_leaps": logical_leaps,
                "hidden_assumptions": hidden_assumptions
            },
            "conversation_history": messages
        }
        
        # 2. Markdown 생성 (요약 보고서)
        causal_chain_md = "\n".join([f"- {msg['content']}" for msg in messages if msg['role'] == 'user'])
        
        content_markdown = f"""
# 📋 문제 진단 보고서 (Problem Specification)

## 1. 개요 및 페르소나
- **추론된 페르소나**: {metadata.get('persona', '알 수 없음')}
- **배경 상황**: {metadata.get('background', '입력된 정보가 부족합니다.')}

## 2. 심층 분석 결과
### 식별된 논리적 비약 (Logical Leaps)
{chr(10).join([f"- {leap}" for leap in logical_leaps]) if logical_leaps else "- 식별된 비약 없음"}

### 숨겨진 전제 (Hidden Assumptions)
{chr(10).join([f"- {asm}" for leap in hidden_assumptions]) if hidden_assumptions else "- 식별된 전제 없음"}

## 3. 원인 추론 과정 (5 Whys Chain)
{causal_chain_md}

---
*본 보고서는 AI 진단 에이전트에 의해 자동 생성되었습니다.*
"""
        
        # 3. 데이터베이스 저장
        spec = await ProblemSpecification.objects.acreate(
            session=session,
            content_markdown=content_markdown.strip(),
            content_json=content_json
        )
        
        # 세션 완료 처리
        session.is_completed = True
        await session.asave()
        
        logger.info(f"세션 {session_id}에 대한 문제 기술서 생성 완료.")
        return spec
        
    except Exception as e:
        logger.error(f"기술서 생성 중 오류 발생: {e}")
        raise

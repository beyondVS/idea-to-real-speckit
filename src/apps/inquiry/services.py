import logging
import re
from typing import Any

from presidio_analyzer import AnalyzerEngine

from apps.inquiry.models import InquirySession, ProblemSpecification

logger = logging.getLogger(__name__)


class MaskingService:
    """
    사용자 입력 데이터에서 민감 정보(PII)를 탐지하고 마스킹 처리하는 서비스입니다.
    """

    def __init__(self) -> None:
        self.analyzer = AnalyzerEngine()
        self.ko_patterns = [
            (re.compile(r"\d{3}-\d{3,4}-\d{4}"), "PHONE_NUMBER"),
            (re.compile(r"\d{6}-\d{7}"), "RESIDENT_ID"),
            (re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"), "EMAIL"),
        ]

    def mask_text(self, text: str) -> str:
        if not text:
            return text
        masked_text = text
        for pattern, label in self.ko_patterns:
            masked_text = pattern.sub("****", masked_text)
        try:
            results = self.analyzer.analyze(text=masked_text, language="en")
            for result in sorted(results, key=lambda x: x.start, reverse=True):
                masked_text = (
                    masked_text[: result.start] + "****" + masked_text[result.end :]
                )
        except Exception as e:
            logger.warning(f"Presidio analysis failed: {e}")
        return masked_text


async def generate_problem_specification(
    session_id: str, state: dict[str, Any]
) -> ProblemSpecification:
    """
    진단 결과를 바탕으로 구조화된 Markdown 및 JSON 문제 기술서를 생성합니다.
    인과관계 3단계 이상 여부를 검증합니다. (T023 반영)
    """
    session = await InquirySession.objects.aget(id=session_id)

    # 1. 인과관계 연쇄 구성 (Timeline 시각화)
    causal_chain = state.get("causal_chain", [])
    timeline_md = "## 인과관계 연쇄 (Causal Chain)\n\n"
    for i, step in enumerate(causal_chain, 1):
        timeline_md += f"{i}. **{step['question']}**\n   ↓ (답변: {step['answer']})\n"

    # 2. Markdown 보고서 작성
    markdown_content = f"""# 문제 기술서 (Problem Specification)

## 0. 개요
**최초 입력**: {state.get("initial_input", "정보 없음")}
**페르소나**: {state.get("metadata", {}).get("persona", "정보 없음")}

{timeline_md}

## 3. 최종 분석 결과
**근본 원인**: {state.get("final_root_cause", "심층 분석 필요")}
**식별된 전제**: {", ".join(state.get("identified_assumptions", []))}

---
*본 보고서는 AI 진단 엔진에 의해 생성되었습니다.*
"""

    # 3. 인과관계 단계 검증 (SC-002)
    if len(causal_chain) < 3:
        logger.warning(f"Session {session_id}: 인과관계 단계가 3단계 미만입니다.")

    # 4. DB 저장
    latest_version = (
        await ProblemSpecification.objects.filter(session=session).acount() + 1
    )
    spec = await ProblemSpecification.objects.acreate(
        session=session,
        version=latest_version,
        content_md=markdown_content,
        content_json=state,
    )

    # 세션 상태 업데이트
    session.status = "completed"
    await session.asave()

    return spec


async def save_user_rating(session_id: str, rating: int) -> bool:
    """
    사용자의 만족도 점수를 저장합니다. (T024.1)
    """
    try:
        spec = await ProblemSpecification.objects.filter(session_id=session_id).afirst()
        if spec:
            spec.rating = rating
            await spec.asave()
            return True
    except Exception as e:
        logger.error(f"만족도 저장 실패: {e}")
    return False


masking_service = MaskingService()

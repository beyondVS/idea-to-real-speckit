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
    """
    session = await InquirySession.objects.aget(id=session_id)
    root_cause_data = state.get("root_cause")

    # 1. 인과관계 연쇄 구성 (메시지 이력 활용)
    messages = state.get("messages", [])
    timeline_md = "## 대화 및 분석 이력 (Inquiry Timeline)\n\n"
    for m in messages:
        role_label = "질문" if (hasattr(m, "type") and m.type == "ai") else "답변"
        content = m.content if hasattr(m, "content") else str(m)
        timeline_md += f"- **[{role_label}]**: {content}\n"

    # 2. Markdown 보고서 작성
    final_cause = (
        root_cause_data.get("content") if root_cause_data else "심층 분석 필요"
    )
    confidence = (
        root_cause_data.get("confidence_label") if root_cause_data else "알 수 없음"
    )

    markdown_content = f"""# 문제 기술서 (Problem Specification)

## 0. 개요
**페르소나**: {state.get("metadata", {}).get("persona", "정보 없음")}

{timeline_md}

## 3. 최종 분석 결과
**근본 원인**: {final_cause}
**분석 확신도**: {confidence}

---
*본 보고서는 AI 진단 엔진에 의해 생성되었습니다.*
"""

    # 3. DB 저장
    latest_version = (
        await ProblemSpecification.objects.filter(session=session).acount() + 1
    )
    spec = await ProblemSpecification.objects.acreate(
        session=session,
        version=latest_version,
        content_md=markdown_content,
        content_json=state,
    )

    # 4. RootCause 객체 생성/업데이트
    if root_cause_data and root_cause_data.get("root_cause_found"):
        from apps.inquiry.models import RootCause

        await RootCause.objects.aupdate_or_create(
            session=session,
            defaults={
                "content": root_cause_data.get("content", ""),
                "confidence_score": root_cause_data.get("confidence_score", 0.0),
                "confidence_label": root_cause_data.get("confidence_label", ""),
                "can_detail": root_cause_data.get("can_detail", False),
                "detailing_guide": root_cause_data.get("detailing_guide"),
            },
        )

    # 세션 상태 업데이트
    session.status = "COMPLETED"
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


def get_confidence_label(score: float) -> str:
    """
    연구 결과(research.md)에 따라 수치적 확신도를 텍스트 라벨로 변환합니다.
    """
    if score >= 0.85:
        return "매우 높음"
    if score >= 0.60:
        return "보통"
    return "낮음"


masking_service = MaskingService()

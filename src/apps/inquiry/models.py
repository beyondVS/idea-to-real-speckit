import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class InquirySession(models.Model):
    """
    진단 세션을 관리하는 모델. 대화의 전체 흐름과 메타데이터를 관리합니다.
    """

    STATUS_CHOICES = [
        ("IN_PROGRESS", "진행 중"),
        ("AWAITING_EXTENSION_APPROVAL", "연장 승인 대기 중"),
        ("COMPLETED", "완료"),
        ("FAILED_LIMIT_REACHED", "질의 제한 도달"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="inquiry_sessions",
        help_text="세션 소유 사용자",
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="IN_PROGRESS",
        help_text="세션 상태",
    )
    turn_count = models.PositiveIntegerField(default=0, help_text="현재 질의 횟수")
    max_turns = models.PositiveIntegerField(default=5, help_text="기본 질의 제한 횟수")
    is_extended = models.BooleanField(default=False, help_text="질의 연장 여부")
    invalid_response_count = models.PositiveIntegerField(
        default=0, help_text="유효하지 않은 답변 반복 횟수"
    )
    metadata = models.JSONField(
        default=dict, blank=True, help_text="사용자 페르소나, 배경 지식 등"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="세션 시작 시간")
    updated_at = models.DateTimeField(auto_now=True, help_text="마지막 활동 시간")

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"Session {self.id} ({self.get_status_display()})"


class RootCause(models.Model):
    """
    도출된 근본 원인 분석 결과를 저장하는 모델.
    """

    session = models.OneToOneField(
        InquirySession,
        on_delete=models.CASCADE,
        related_name="root_cause",
        help_text="연결된 진단 세션",
    )
    content = models.TextField(help_text="도출된 근본 원인 내용")
    confidence_score = models.FloatField(help_text="분석 확신도 점수 (0.0 ~ 1.0)")
    confidence_label = models.CharField(
        max_length=20, help_text="사용자 노출용 확신도 라벨"
    )
    can_detail = models.BooleanField(default=False, help_text="상세화 가능 여부")
    detailing_guide = models.TextField(
        blank=True, null=True, help_text="상세화가 가능할 경우의 분석 방향 가이드"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="분석 결과 생성 시각"
    )

    def __str__(self) -> str:
        return f"RootCause for Session {self.session_id} ({self.confidence_label})"


class ProblemSpecification(models.Model):
    """
    진단 완료 시 생성되는 최종 결과물 레코드.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        InquirySession,
        on_delete=models.CASCADE,
        related_name="specifications",
        help_text="연결된 진단 세션",
    )
    version = models.PositiveIntegerField(help_text="동일 세션 내 생성 버전")
    content_md = models.TextField(help_text="사용자용 Markdown 요약 보고서", default="")
    content_json = models.JSONField(help_text="시스템 연동용 상세 데이터", default=dict)
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="사용자 만족도 점수 (1~5)"
    )
    is_deleted = models.BooleanField(
        default=False, help_text="사용자 삭제 여부 (영구 보관 정책 대응)"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성 시간")

    class Meta:
        unique_together = ("session", "version")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Spec v{self.version} for Session {self.session_id}"

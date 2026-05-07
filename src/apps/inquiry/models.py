import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class InquirySession(models.Model):
    """
    진단 세션을 관리하는 모델. 대화의 전체 흐름과 메타데이터를 관리합니다.
    """

    STATUS_CHOICES = [
        ("in_progress", "진행중"),
        ("waiting", "대기중"),
        ("completed", "완료"),
        ("error", "오류"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="inquiry_sessions",
        help_text="세션 소유 사용자",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="in_progress",
        help_text="세션 상태",
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

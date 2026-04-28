import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class InquirySession(models.Model):
    """
    진단 세션을 관리하는 모델.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    final_root_cause = models.TextField(blank=True, null=True)
    
    def __str__(self) -> str:
        return f"Session {self.id}"

class ProblemSpecification(models.Model):
    """
    최종 결과물인 문제 기술서 엔티티.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField(InquirySession, on_delete=models.CASCADE, related_name='specification')
    content_markdown = models.TextField()
    content_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"Spec for Session {self.session_id}"

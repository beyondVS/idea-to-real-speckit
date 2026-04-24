# 인터페이스 계약 (Interface Contracts): AJAX API

## 개요
사용자의 브라우저와 Django 서버 간의 비동기 통신 규약을 정의합니다.

## 엔드포인트: `POST /api/inquiry/chat/`

### 요청 (Request)
- **Method**: POST
- **Header**: `Content-Type: application/json`, `X-CSRFToken: [token]`
- **Body**:
```json
{
  "session_id": "uuid-string (null if new session)",
  "user_input": "모호한 문제 설명 또는 답변"
}
```

### 응답 (Response - 성공)
- **Status**: 200 OK
- **Body**:
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid-string",
    "ai_response": "AI의 질문 또는 요약 내용",
    "current_step": 1,
    "is_completed": false,
    "show_agreement": false
  }
}
```

### 응답 (Response - 대화 종료 제안)
- **Status**: 200 OK
- **Body**:
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid-string",
    "ai_response": "파악된 근본 원인 요약...",
    "current_step": 5,
    "is_completed": false,
    "show_agreement": true
  }
}
```

## UI 상호작용 지침
1. **요청 전**: 버튼 비활성화, '답변 중...' 인디케이터 활성화.
2. **응답 후**: 답변을 대화창에 추가, 인디케이터 비활성화, 버튼 활성화.
3. **오류 시**: 사용자 친화적인 에러 메시지 노출 및 재시도 버튼 제공.

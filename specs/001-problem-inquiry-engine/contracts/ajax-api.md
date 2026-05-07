# AJAX API 규약 (Contracts): Problem Inquiry Engine (진단 엔진)

## 개요
본 문서는 프론트엔드(AJAX)와 백엔드(Django Async View) 간의 통신 규약을 정의합니다. 모든 요청은 `application/json` 형식을 사용하며, 헌법의 '한국어 최우선' 원칙에 따라 에러 메시지는 한국어로 제공됩니다.

---

## 1. 진단 세션 시작 (POST /api/inquiry/start/)

- **설명**: 새로운 진단 세션을 생성하고 최초 질문을 요청합니다.

### Request
```json
{
  "initial_input": "우리 팀의 생산성이 너무 낮은 것 같아요."
}
```

### Response (201 Created)
```json
{
  "session_id": "uuid-v4-string",
  "status": "in_progress",
  "question": "생산성이 낮다고 느끼시는 구체적인 상황을 한 가지만 말씀해 주시겠어요?",
  "step": 1
}
```

---

## 2. 메시지 전송 및 분석 (POST /api/inquiry/<session_id>/chat/)

- **설명**: 사용자의 답변을 전송하고 다음 단계의 질문 또는 종료 동의를 요청합니다.

### Request
```json
{
  "answer": "팀원들 간의 업무 공유가 잘 안 되고 있어요."
}
```

### Response (200 OK)
```json
{
  "status": "in_progress",
  "question": "업무 공유가 안 되는 것이 도구의 문제인가요, 아니면 프로세스의 문제인가요?",
  "step": 2,
  "is_final_diagnosis": false
}
```

---

## 3. 상태 롤백 (POST /api/inquiry/<session_id>/rollback/)

- **설명**: 이전 단계로 대화 상태를 되돌립니다.

### Request
```json
{
  "target_step": 1
}
```

### Response (200 OK)
```json
{
  "current_step": 1,
  "last_question": "생산성이 낮다고 느끼시는 구체적인 상황을 한 가지만 말씀해 주시겠어요?"
}
```

---

## 4. 결과물 조회 및 다운로드 (GET /api/inquiry/<session_id>/result/)

- **설명**: 완료된 진단의 Markdown 및 JSON 데이터를 조회합니다.

### Response (200 OK)
```json
{
  "session_id": "uuid",
  "markdown_content": "# 진단 결과 보고서...",
  "json_content": { ... },
  "download_url": "/api/inquiry/uuid/download-md/"
}
```

---

## 5. 만족도 점수 제출 (POST /api/inquiry/<session_id>/rate/)

- **설명**: 진단 결과에 대한 사용자의 만족도 점수를 저장합니다.

### Request
```json
{
  "rating": 5
}
```

### Response (200 OK)
```json
{
  "status": "success",
  "message": "만족도 조사가 완료되었습니다."
}
```

---

## 6. 공통 에러 응답 (4xx, 5xx)

```json
{
  "error_code": "LLM_CONNECTION_FAILED",
  "message": "LLM 서버와의 연결이 원활하지 않습니다. 잠시 후 다시 시도해 주세요.",
  "retry_allowed": true
}
```

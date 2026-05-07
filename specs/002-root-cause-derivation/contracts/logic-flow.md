# 상태 머신 계약 (State Machine Contract): Inquiry Logic

## 1. 입력 상태 스키마 (Input State)
LangGraph 상태 머신이 입력으로 받는 데이터 구조입니다.

```python
class InquiryState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    turn_count: int
    invalid_response_count: int
    is_extension_approved: bool
    root_cause: Optional[dict]  # RootCause 엔티티 데이터
```

## 2. 분석 노드 출력 스키마 (Analyzer Node Output)
분석 에이전트가 반환해야 하는 정형화된 응답 구조입니다.

```json
{
  "root_cause_found": true,
  "content": "시스템 설정 파일의 권한 설정 오류",
  "confidence_score": 0.88,
  "can_detail": true,
  "detailing_guide": "특정 디렉토리(/etc/config)의 쓰기 권한 소유자 확인 필요"
}
```

## 3. 대화 인터페이스 계약 (UI Interaction)

### 질의 연장 승인 요청
- **Type**: `APPROVAL_REQUEST`
- **Message**: "원인 파악을 위해 추가 질의가 필요합니다. 계속 진행할까요?"
- **Options**: `["Yes", "No"]`

### 분석 결과 리포트
- **Type**: `ANALYSIS_REPORT`
- **Data**:
  - `root_cause`: 원인 내용
  - `confidence`: "매우 높음" | "보통" | "낮음"
  - `can_detail`: 상세화 가능 여부

# 데이터 모델 (Data Model): Problem Inquiry Engine (진단 엔진)

## 엔티티 (Entities)

### 1. 진단 세션 (InquirySession)
- **id**: UUID (Primary Key)
- **user_id**: ForeignKey (Django User 모델)
- **started_at**: DateTime
- **is_completed**: Boolean (진단 완료 여부)
- **final_root_cause**: TextField (최종 파악된 근본 원인)

### 2. 대화 상태 (GraphState - JSON 필드로 저장)
- **session_id**: ForeignKey (InquirySession)
- **messages**: JSONField (대화 이력: role, content)
- **current_step**: Integer (1~5)
- **metadata**: JSONField (추출된 페르소나, 배경 정보)
- **logical_leaps**: JSONField (식별된 논리적 비약 목록)

### 3. 문제 기술서 (ProblemSpecification)
- **id**: UUID
- **session_id**: ForeignKey (InquirySession)
- **content_markdown**: TextField (사람이 읽기 좋은 보고서)
- **content_json**: JSONField (구조화된 Full Spec)
- **created_at**: DateTime

## 관계 (Relationships)
- `InquirySession` : `GraphState` = 1 : 1 (실시간 상태 업데이트)
- `InquirySession` : `ProblemSpecification` = 1 : 1 (진단 완료 후 생성)

## 상태 전환 (State Transitions)
1. **INIT**: 사용자의 최초 문제 입력 → 세션 생성
2. **INQUIRY**: 5 Whys 질문 및 분석 루프 (Step 1~5)
3. **SUMMARY**: 근본 원인 요약 및 사용자 종료 동의 대기
4. **COMPLETED**: 문제 기술서 생성 및 세션 종료

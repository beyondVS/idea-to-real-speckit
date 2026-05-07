# 데이터 모델 (Data Model): root-cause-derivation

## 1. 엔티티 정의 (Entities)

### InquirySession (Extended)
기존 `InquirySession` 모델에 질의 제어 및 분석 상태를 위한 필드를 확장합니다.

- **turn_count** (Integer): 현재 세션의 질의 횟수 (기본값: 0)
- **max_turns** (Integer): 기본 질의 제한 횟수 (기본값: 5)
- **is_extended** (Boolean): 사용자에 의해 질의가 연장되었는지 여부
- **invalid_response_count** (Integer): 의미 없는 답변(FR-006) 반복 횟수 (최대 3회)
- **status** (Choice): `IN_PROGRESS`, `AWAITING_EXTENSION_APPROVAL`, `COMPLETED`, `FAILED_LIMIT_REACHED`

### RootCause (New Entity)
분석 결과 및 상세화 정보를 담는 객체입니다. DB 저장 시 JSONField 또는 별도 테이블로 관리합니다.

- **content** (Text): 도출된 근본 원인 내용
- **confidence_score** (Float): 내부 확신도 점수 (0.0 ~ 1.0)
- **confidence_label** (String): 사용자 노출용 라벨 (매우 높음, 보통, 낮음)
- **can_detail** (Boolean): 상세화 가능 여부
- **detailing_guide** (Text): 상세화가 가능할 경우의 분석 방향 가이드
- **created_at** (DateTime): 생성 시각

## 2. 상태 전환 모델 (State Transitions)

| 현재 상태 | 이벤트 | 조건 | 다음 상태 |
|-----------|--------|------|-----------|
| `IN_PROGRESS` | 답변 수신 | `turn_count` < 5 AND 원인 도출 안됨 | `IN_PROGRESS` (turn_count++) |
| `IN_PROGRESS` | 답변 수신 | 원인 도출됨 | `COMPLETED` |
| `IN_PROGRESS` | 답변 수신 | `turn_count` == 5 AND 원인 미도출 | `AWAITING_EXTENSION_APPROVAL` |
| `AWAITING_EXTENSION_APPROVAL` | 연장 승인 | 사용자 동의 | `IN_PROGRESS` |
| `AWAITING_EXTENSION_APPROVAL` | 연장 거부 | 사용자 거부 | `COMPLETED` (현재까지 결과 리포트) |
| `IN_PROGRESS` | 의미 없는 답변 | `invalid_response_count` == 3 | `FAILED_LIMIT_REACHED` |

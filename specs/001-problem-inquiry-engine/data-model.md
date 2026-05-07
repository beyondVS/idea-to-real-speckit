# 데이터 모델 설계 (Data Model): Problem Inquiry Engine (진단 엔진)

## 엔티티 관계도 (ERD)

```text
User (Django Auth)
  └── InquirySession (1:N)
        ├── ProblemSpecification (1:N, Versioned)
        └── CausalStep (1:N, LangGraph Internal via PostgresSaver)
```

---

## 1. InquirySession (진단 세션)

- **상태 관리**: 대화의 전체 흐름과 메타데이터를 관리하는 핵심 엔티티.

| 필드명 | 타입 | 설명 | 제약 사항 |
|--------|------|------|------------|
| `id` | UUID | 세션 고유 식별자 | Primary Key |
| `user` | FK(User) | 세션 소유 사용자 | Not Null, On Delete Cascade |
| `status` | Choice | 세션 상태 (진행중, 대기중, 완료, 오류) | Default: 진행중 |
| `metadata` | JSONField | 사용자 페르소나, 배경 지식 등 | Default: {} |
| `created_at` | DateTime | 세션 시작 시간 | Auto Now Add |
| `updated_at` | DateTime | 마지막 활동 시간 | Auto Now |

---

## 2. ProblemSpecification (문제 기술서)

- **결과 보존**: 진단 완료 시 생성되는 최종 결과물 레코드.

| 필드명 | 타입 | 설명 | 제약 사항 |
|--------|------|------|------------|
| `id` | UUID | 기술서 고유 식별자 | Primary Key |
| `session` | FK(InquirySession) | 연결된 진단 세션 | Not Null |
| `version` | Integer | 동일 세션 내 생성 버전 | Not Null |
| `content_md` | TextField | 사용자용 Markdown 요약 보고서 | Not Null |
| `content_json` | JSONField | 시스템 연동용 상세 데이터 | Not Null |
| `rating` | Integer | 사용자 만족도 점수 (1~5) | Nullable |
| `is_deleted` | Boolean | 사용자 삭제 여부 (영구 보관 정책 대응) | Default: False |
| `created_at` | DateTime | 생성 시간 | Auto Now Add |

### JSON 스키마 필수 필드 (content_json)
- `initial_input`: 사용자의 최초 입력 텍스트
- `causal_chain`: `[{"step": 1, "question": "...", "answer": "..."}, ...]`
- `identified_assumptions`: 추출된 논리적 전제 목록
- `final_root_cause`: 최종 도출된 근본 원인
- `metadata`: 세션에서 추출된 메타데이터 스냅샷

---

## 3. 유효성 검사 및 상태 전환 규칙

- **상태 롤백**: 사용자가 이전 단계로 돌아갈 경우, `InquirySession`의 `updated_at`을 갱신하고 LangGraph 체크포인트를 해당 시점으로 이동함.
- **마스킹 규칙**: 모든 메시지 저장 전 `Presidio` 필터를 거쳐 PII(개인식별정보)를 `****`로 교체함.
- **종료 전이**: `is_final_diagnosis: true` 또는 `step == 5` 시 사용자 동의 프로세스(`await_agreement`) 상태로 전환.

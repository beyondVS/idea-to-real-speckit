# 작업 목록 (Tasks): root-cause-derivation

**입력 (Input)**: `/specs/002-root-cause-derivation/`에서 가져온 설계 문서
**선행 조건 (Prerequisites)**: plan.md (필수), spec.md (사용자 스토리용 필수), research.md, data-model.md, contracts/

**테스트 (Tests)**: 이 작업 목록에는 명세서의 '독립적 테스트' 기준을 충족하기 위한 테스트 작업이 포함되어 있습니다. 모든 테스트는 Django 프레임워크 및 Pytest 권장 방식을 따릅니다.

**조직 (Organization)**: 각 스토리를 독립적으로 구현하고 테스트할 수 있도록 사용자 스토리별로 작업이 그룹화됩니다.

## 형식: `[ID] [P?] [Story] 설명`

- **[P]**: 병렬 실행 가능 (서로 다른 파일, 의존성 없음)
- **[Story]**: 이 작업이 속한 사용자 스토리 (예: US1, US2, US3)
- 설명에 정확한 파일 경로를 포함하십시오

---

## Phase 1: 설정 (공통 인프라)

**목적**: 프로젝트 초기화 및 헌법 기반 환경 설정

- [x] T001 [P] `src/config/settings.py`에 Django 5.2 LTS 및 PostgreSQL 연결 설정 확인
- [x] T002 [P] `pyproject.toml`에 Python 3.13 및 필요한 의존성(langgraph, django-environ 등) 추가
- [x] T003 [P] `uv lock`을 통한 의존성 버전 확정
- [x] T004 [P] `.ruff.toml` 또는 `pyproject.toml`에 Ruff 린트 및 포맷팅 규칙 설정

---

## Phase 2: 기반 작업 (차단 선행 조건)

**목적**: 어떠한 사용자 스토리도 구현되기 전에 반드시 완료되어야 하는 핵심 인프라

**⚠️ 중요(CRITICAL)**: 이 단계가 완료될 때까지 어떠한 사용자 스토리 작업도 시작할 수 없습니다.

- [x] T005 [P] `src/apps/inquiry/models.py`에 `InquirySession` 확장 필드(turn_count, max_turns 등) 및 `RootCause` 모델 정의
- [x] T006 `python src/manage.py makemigrations inquiry`로 마이그레이션 생성 및 DB 반영
- [x] T007 `src/apps/inquiry/state.py`에 `InquiryState` TypedDict 정의 (contracts/logic-flow.md 준수)
- [x] T008 `src/apps/inquiry/graph.py`에 LangGraph 워크플로우 기본 뼈대 및 상태 관리 로직 구축
- [x] T009 [P] `src/core/llm.py` 또는 유틸리티에 지수 백오프(Exponential Backoff) 적용된 LLM 래퍼 구현

**체크포인트**: 기반 준비 완료 - 이제 사용자 스토리 구현을 시작할 수 있습니다.

---

## Phase 3: 사용자 스토리 1 - 근본 원인 도출 (우선순위: P1) 🎯 MVP

**목표**: 대화 이력을 분석하여 문제의 핵심 원인을 식별하고 확신도 라벨과 함께 제시함

**독립적 테스트 (Independent Test)**: 가상의 답변 세트를 입력했을 때 시스템이 `RootCause` 객체를 생성하고 타당한 원인 및 확신도 라벨을 반환하는지 검증

### 사용자 스토리 1을 위한 테스트

- [x] T010 [P] [US1] `src/apps/inquiry/tests/test_nodes.py`에 Analyzer 노드의 원인 도출 논리 단위 테스트 작성
- [x] T011 [US1] `src/apps/inquiry/tests/test_views.py`에 원인 도출 시 대화 종료 및 결과 표시 통합 테스트 작성

### 사용자 스토리 1 구현

- [x] T012 [US1] `src/apps/inquiry/nodes.py`에 `analyzer` 노드 구현 (5-Why 기법 프롬프트 적용)
- [x] T013 [US1] `src/apps/inquiry/services.py`에 `confidence_score`를 텍스트 라벨로 변환하는 유틸리티 구현
- [x] T014 [US1] `src/apps/inquiry/graph.py`에 `analyzer` 노드 등록 및 원인 도출 시 종료 에지 연결
- [x] T015 [US1] `src/templates/inquiry/chat.html` 및 관련 View에 분석 결과 리포트 표시 로직 구현

**체크포인트**: 이 시점에서 사용자 스토리 1은 독립적으로 작동하며 원인 도출 기능을 제공해야 합니다.

---

## Phase 4: 사용자 스토리 2 - 질의 제한 및 연장 제어 (우선순위: P1)

**목표**: 5회 질의 제한 도달 시 사용자 승인을 받아 연장하거나, 무의미한 답변 반복 시 강제 종료함

**독립적 테스트 (Independent Test)**: 질의 횟수 카운터가 5에 도달했을 때 연장 승인 UI가 노출되고, 승인 여부에 따라 루프가 지속되거나 종료되는지 검증

### 사용자 스토리 2를 위한 테스트

- [x] T016 [P] [US2] `src/apps/inquiry/tests/test_us2_logic.py`에 질의 횟수 제한 및 연장 승인 상태 전이 테스트 작성
- [x] T017 [P] [US2] `src/apps/inquiry/tests/test_us2_logic.py`에 무의미한 답변 3회 반복 시 강제 종료 테스트 작성

### 사용자 스토리 2 구현

- [x] T018 [US2] `src/apps/inquiry/graph.py`에 `turn_count` 증가 로직 및 `should_continue` 조건부 에지 구현
- [x] T019 [US2] `src/apps/inquiry/nodes.py`에 무의미한 답변(invalid response) 감지 로직 구현
- [x] T020 [US2] `src/apps/inquiry/views.py`에 연장 승인 요청(`APPROVAL_REQUEST`) 처리 및 상태 업데이트 API 구현
- [x] T021 [US2] `src/templates/inquiry/chat.html`에 연장 승인 버튼(Yes/No) UI 및 AJAX 연동 구현

**체크포인트**: 질의 횟수 제어 및 사용자 승인 기반 연장 워크플로우가 완성되어야 합니다.

---

## Phase 5: 사용자 스토리 3 - 근본 원인 상세화 가능성 판단 (우선순위: P2)

**목표**: 도출된 원인이 추상적일 경우 상세화 가능 여부를 판단하고 즉시 추가 질의를 시도함

**독립적 테스트 (Independent Test)**: 원인 도출 시 `can_detail` 플래그가 설정된 경우 시스템이 즉시 상세 분석 질의 노드로 전이하는지 확인

### 사용자 스토리 3을 위한 테스트

- [x] T022 [P] [US3] `src/apps/inquiry/tests/test_us3_logic.py`에 상세화 가능 여부 판단 및 후속 질의 생성 테스트 작성

### 사용자 스토리 3 구현

- [x] T023 [US3] `src/apps/inquiry/nodes.py`의 `analyzer` 노개에 `can_detail` 및 `detailing_guide` 생성 로직 추가
- [x] T024 [US3] `src/apps/inquiry/graph.py`에 `can_detail`인 경우 상세화 질의 생성 노드로 즉시 전이하는 에지 추가
- [x] T025 [US3] `src/apps/inquiry/nodes.py`에 `detailing_guide`를 활용한 구체적 질의 생성 프롬프트 고도화

**체크포인트**: 모든 사용자 스토리가 통합되어 지능적인 질의 연장 및 상세화 분석이 가능해야 합니다.

---

## Phase 6: 마무리 및 횡단 관심사

**목적**: 코드 품질 확보 및 문서화 마무리

- [x] T026 [P] 모든 신규 코드에 대해 Ruff 포맷팅 및 mypy 타입 체크 수행
- [x] T027 [P] 모든 클래스와 함수에 한국어 Google Style Docstring 누락 여부 최종 확인
- [x] T028 `README.md`에 새로운 분석 기능 및 질의 제어 로직 사용법 업데이트
- [x] T029 최종 통합 테스트 및 성능(응답 지연 시간) 측정
- [x] T030 [US1] 전문가 리뷰용 테스트 시나리오(10종 이상) 수행 및 결과 일치율(85% 이상) 측정

---

## 의존성 및 실행 순서 (Dependencies & Execution Order)

### 단계별 의존성 (Phase Dependencies)

- **Phase 1 (Setup)**: 완료
- **Phase 2 (Foundational)**: 완료
- **Phase 3~5 (User Stories)**: 완료
- **Phase 6 (Polish)**: 완료

### 사용자 스토리 의존성 (User Story Dependencies)

- **US1 (Root Cause)**: 완료
- **US2 (Control)**: 완료
- **US3 (Detailing)**: 완료

---

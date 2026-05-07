# 작업 목록 (Tasks): Problem Inquiry Engine (진단 엔진)

**입력 (Input)**: `specs/001-problem-inquiry-engine/`에서 가져온 설계 문서
**선행 조건 (Prerequisites)**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/ajax-api.md](contracts/ajax-api.md)

**테스트 (Tests)**: `spec.md`에서 정의된 '독립적 테스트' 기준에 따라 각 사용자 스토리별 검증 작업을 포함합니다. 모든 테스트는 Django `TestCase` 및 `pytest-django` (비동기 지원) 환경을 가정합니다.

**조직 (Organization)**: 핵심 가치인 '진단 프로세스'를 MVP 증분으로 인도할 수 있도록 사용자 스토리별로 작업을 그룹화했습니다.

## 형식: `[ID] [P?] [Story] 설명`

- **[P]**: 병렬 실행 가능 (서로 다른 파일, 의존성 없음)
- **[Story]**: 이 작업이 속한 사용자 스토리 (US1, US2, US3)
- 설명에 정확한 파일 경로를 포함함

---

## Phase 1: 설정 (공통 인프라) - Phase 1: Setup (Shared Infrastructure)

**목적**: 프로젝트 초기화 및 헌법 기반 환경 설정

- [x] T001 `plan.md`의 구조에 따라 프로젝트 디렉토리 및 앱 생성 (`src/config/`, `src/apps/inquiry/`, `src/core/`, `src/templates/inquiry/`)
- [x] T002 `uv init`으로 프로젝트 초기화 및 Python 3.13 의존성 설정 (Django 5.2, langchain, langgraph, psycopg, ollama-python, presidio-analyzer)
- [x] T003 [P] `pyproject.toml` 내 Ruff(Lint/Format) 및 mypy(Type Safety) 도구 설정
- [x] T004 [P] `.env` 템플릿 생성 (DATABASE_URL, OLLAMA_BASE_URL, SECRET_KEY 포함)

---

## Phase 2: 기반 작업 (차단 선행 조건) - Phase 2: Foundational (Blocking Prerequisites)

**목적**: 진단 엔진 구동을 위한 핵심 LLM 연동, 데이터 저장소 및 보안 인프라 구축

**⚠️ 중요(CRITICAL)**: 이 단계가 완료될 때까지 사용자 스토리 작업을 시작할 수 없습니다.

- [x] T005 PostgreSQL 데이터베이스 연결 및 Django `settings.py` 비동기 DB 설정 (`src/config/settings.py`)
- [x] T006 [P] ChatOllama 설정, LLM 추상화 및 지수 백오프 유틸리티 구현 (`src/core/llm.py`, `src/core/backoff.py`)
- [x] T007 `data-model.md`에 정의된 핵심 Django 모델 구현 (`src/apps/inquiry/models.py`: `InquirySession`, `ProblemSpecification`)
- [x] T008 [P] LangGraph 상태 머신(GraphState) 기초 구조 및 `PostgresSaver` 체크포인터 설정 (`src/apps/inquiry/graph.py`)
- [x] T009 [P] `asyncio.Queue` 기반 로컬 작업 큐(Task Queue) 유틸리티 구현 (`src/core/queue.py`)
- [x] T010 [P] 개인정보 자동 탐지 및 마스킹(Masking) 서비스 구현 (`src/apps/inquiry/services.py`)
- [x] T011 초기 데이터베이스 마이그레이션 실행 (`python manage.py makemigrations inquiry && python manage.py migrate`)
- [x] T012 [P] LLM 최종 실패 시 세션을 안전하게 보존하기 위한 Fallback 로직 구현 (`src/core/llm.py`)
- [x] T013 [P] 민감 정보 유출 방지를 위한 보안 로깅 필터(Log Redactor) 구현 (`src/config/logging.py`)

**체크포인트**: 기반 인프라 준비 완료 - 이제 진단 로직 구현을 시작할 수 있습니다.

---

## Phase 3: 사용자 스토리 1 - 문제 입력 및 진단 시작 (우선순위: P1) 🎯 MVP

**목표**: 사용자 입력을 분석하여 페르소나를 추출하고 첫 번째 질문을 제시함

**독립적 테스트 (Independent Test)**: 모호한 문장 입력 시 메타데이터(페르소나)가 추출되고 첫 번째 "Why" 질문이 응답되는지 확인

### 사용자 스토리 1 구현

- [x] T014 [US1] Analyzer Node 구현: 텍스트 내 논리적 비약 및 페르소나 추출 로직 (다국어 입력 케이스 포함) (`src/apps/inquiry/nodes.py`)
- [x] T015 [US1] LangGraph 워크플로우 정의: START -> Analyzer -> Questioner 진입 구조 (`src/apps/inquiry/graph.py`)
- [x] T016 [US1] `ajax-api.md`를 준수하는 Async Chat API View 초기 구현 (세션 생성 및 첫 응답) (`src/apps/inquiry/views.py`)
- [x] T017 [US1] AJAX 기반 대화 UI 및 "분석 대기 중" 인디케이터 템플릿 구현 (`src/templates/inquiry/chat.html`)

---

## Phase 4: 사용자 스토리 2 - 5 Whys 심층 문답 진행 (우선순위: P1)

**목표**: 최대 5회의 문답을 통해 인과관계를 심층적으로 탐색하고 질문 재구성을 지원함

**독립적 테스트 (Independent Test)**: 3~5회 문답 동안 질문의 깊이가 점진적으로 깊어지며 `current_step`이 정상 증가하고, 이해 실패 시 재구성이 일어나는지 확인

### 사용자 스토리 2 구현

- [x] T018 [US2] Questioner Node 구현: 이전 답변 분석 및 5 Whys 기반 심층 질문 생성 (다국어 대응 확인) (`src/apps/inquiry/nodes.py`)
- [x] T019 [US2] 질문 재구성 로직 추가: 사용자 이해 실패 시 쉬운 용어로 재생성 (`src/apps/inquiry/nodes.py`)
- [x] T020 [US2] LangGraph 루프 구성: Questioner -> User Input -> Analyzer 반복 순환 구조 (`src/apps/inquiry/graph.py`)
- [x] T021 [US2] Async View 고도화: 작업 큐 연동 및 지속적인 대화 상태 업데이트 로직 (`src/apps/inquiry/views.py`)

---

## Phase 5: 사용자 스토리 3 - 진단 종료 및 문제 기술서 생성 (우선순위: P1)

**목표**: 진단 완료 후 구조화된 Markdown 및 JSON 기술서를 생성하고 시각화함

**독립적 테스트 (Independent Test)**: 종료 조건 도달 시 '순차적 타임라인'이 포함된 MD 파일 다운로드 확인

### 사용자 스토리 3 구현

- [x] T022 [US3] Edge Logic 구현: `is_final_diagnosis` 플래그 및 수렴도(0.8) 기반 종료 제어 (`src/apps/inquiry/graph.py`)
- [x] T023 [US3] 결과 생성 서비스 구현: Markdown(타임라인 시각화), JSON 생성 및 인과관계 3단계 이상 검증 로직 포함 (`src/apps/inquiry/services.py`)
- [x] T024 [US3] UI 결과 화면 구현: 종료 동의 팝업, 만족도 설문 UI 및 MD 다운로드 기능 포함 (`src/templates/inquiry/chat.html`)
- [x] T024.1 [US3] 사용자 만족도 점수 저장 API 구현 (`src/apps/inquiry/views.py`, `src/apps/inquiry/services.py`)

---

## Phase 6: 사용자 스토리 4 - 롤백, 분기 관리 및 세션 재개 (우선순위: P1)

**목표**: 이전 단계 롤백, 새로운 대화 분기 생성 및 중단된 세션의 목록화/재개 지원

**독립적 테스트 (Independent Test)**: 이전 단계로 롤백 시 분기가 생성되는지 확인하고, 대시보드에서 기존 세션 재개가 가능한지 검증

### 사용자 스토리 4 구현

- [x] T025 [US4] LangGraph 롤백 로직 및 분기 관리 기능 구현 (`src/apps/inquiry/graph.py`)
- [x] T026 [US4] UI '분기 탐색기' 구현: 트리/드롭다운 기반 분기 시각화, 선택 시 상태 전환 및 롤백 인터페이스 통합 (`src/templates/inquiry/chat.html`)
- [x] T027 [US4] 사용자 대시보드 구현: 진행 중인 세션 목록 노출 및 자동 재개 엔드포인트 (`src/apps/inquiry/views.py`)

---

## Phase N: 마무리 및 횡단 관심사 - Phase N: Polish & Cross-Cutting Concerns

**목적**: 품질 검증, 보안 강화 및 헌법 준수 마무리

- [x] T028 [P] 전체 코드에 대해 Ruff check 및 mypy 엄격 모드 검증 수행
- [x] T029 모든 클래스 및 노드 메서드에 한국어 Google Style Docstring 적용 여부 전수 조사
- [x] T030 다국어 입력 시 LLM의 유연한 처리에 대한 최종 수용성 테스트 (FR-006 준수 확인)
- [x] T031 [P] `uv lock`으로 의존성 버전 고정 및 `README.md` 설치 가이드 업데이트

---

## 의존성 및 실행 순서 (Dependencies & Execution Order)

### 단계별 의존성 (Phase Dependencies)

- **Phase 1 (Setup)**: 즉시 시작 가능
- **Phase 2 (Foundational)**: Phase 1 완료 후 시작. 모든 사용자 스토리의 필수 선행 조건.
- **Phase 3~6 (User Stories)**: Phase 2 완료 후 순차 또는 병렬 진행 가능.
  - 논리적 흐름상 US1 -> US2 -> US3 -> US4 순서 권장.

### 사용자 스토리 내부 순서

- **데이터 → 로직 → 인터페이스**: Models -> Nodes/Services -> Views -> Templates 순서로 구현

### 병렬 실행 기회 (Parallel Opportunities)

- [P] 표시된 모든 작업은 완료되지 않은 타 작업에 대한 의존성이 없어 병렬로 진행 가능
- Phase 2 내의 LLM 인터페이스(T006), 작업 큐(T009), 마스킹 서비스(T010)는 병렬 개발 가능

---

## 구현 전략 (Implementation Strategy)

### MVP 우선 (사용자 스토리 1 위주)

1. Phase 1 & 2를 완료하여 기본 인프라 및 보안 필터 구축
2. Phase 3(US1)을 구현하여 "사용자 입력 -> 분석 -> 첫 질문"의 루프 완성
3. **중단 및 검증**: Ollama 연동 및 작업 큐 동작 확인

### 점진적 인도 (Incremental Delivery)

1. 기반 준비 완료 (Phase 2)
2. 시작 기능 제공 (US1) -> 심층 문답 추가 (US2) -> 결과 시각화/생성 (US3) -> 분기/재개 UX 완성 (US4)
3. 각 단계마다 `Independent Test`를 수행하여 회귀 오류 방지

---

## 참고 (Notes)

- 모든 코드는 헌법에 따라 한국어 주석 및 Docstring을 포함해야 함
- 마스킹 로직(T010)은 개인정보 유출 방지를 위해 최우선적으로 안정성 검증 필요
- 무제한 세션/메시지 정책에 따라 DB 인덱싱 및 쿼리 최적화에 유의함

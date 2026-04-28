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
- [x] T002 `uv init`으로 프로젝트 초기화 및 Python 3.13 의존성 설정 (Django 5.2, langchain, langgraph, psycopg, ollama-python)
- [x] T003 [P] `pyproject.toml` 내 Ruff(Lint/Format) 및 mypy(Type Safety) 도구 설정
- [x] T004 [P] `.env` 템플릿 생성 (DATABASE_URL, OLLAMA_BASE_URL 포함)

---

## Phase 2: 기반 작업 (차단 선행 조건) - Phase 2: Foundational (Blocking Prerequisites)

**목적**: 진단 엔진 구동을 위한 핵심 LLM 연동 및 데이터 저장소 구축

**⚠️ 중요(CRITICAL)**: 이 단계가 완료될 때까지 사용자 스토리 작업을 시작할 수 없습니다.

- [x] T005 PostgreSQL 데이터베이스 연결 및 Django `settings.py` 비동기 DB 설정 (`src/config/settings.py`)
- [x] T006 [P] ChatOllama 설정 및 LLM 추상화 인터페이스 구현 (`src/core/llm.py`)
- [x] T007 `data-model.md`에 정의된 핵심 Django 모델 구현 (`src/apps/inquiry/models.py`: `InquirySession`, `ProblemSpecification`)
- [x] T008 [P] LangGraph 상태 머신(GraphState) 기초 구조 및 `PostgresSaver` 체크포인터 설정 (`src/apps/inquiry/graph.py`)
- [x] T009 초기 데이터베이스 마이그레이션 실행 (`python manage.py makemigrations inquiry && python manage.py migrate`)
- [x] T009.1 [P] LLM 최종 실패 시 세션을 안전하게 보존하기 위한 Fallback 로직 구현 (`src/core/llm.py`)
- [x] T009.2 [P] 민감 정보 유출 방지를 위한 보안 로깅 필터(Log Redactor) 구현 (`src/config/logging.py`)

**체크포인트**: 기반 인프라 준비 완료 - 이제 진단 로직 구현을 시작할 수 있습니다.

---

## Phase 3: 사용자 스토리 1 - 문제 입력 및 진단 시작 (우선순위: P1) 🎯 MVP

**목표**: 사용자 입력을 분석하여 페르소나를 추출하고 첫 번째 질문을 제시함

**독립적 테스트 (Independent Test)**: 모호한 문장 입력 시 메타데이터(페르소나)가 추출되고 첫 번째 "Why" 질문이 응답되는지 확인

### 사용자 스토리 1을 위한 테스트

- [x] T010 [P] [US1] Analyzer Node의 메타데이터 추출 로직 단위 테스트 작성 (`src/apps/inquiry/tests/test_nodes.py`)
- [x] T011 [P] [US1] `ajax-api.md` 규약에 따른 최초 채팅 시작 엔드포인트 통합 테스트 작성 (`src/apps/inquiry/tests/test_views.py`)

### 사용자 스토리 1 구현

- [x] T012 [US1] Analyzer Node 구현: 텍스트 내 논리적 비약 및 페르소나 추출 로직 (`src/apps/inquiry/nodes.py`)
- [x] T013 [US1] LangGraph 워크플로우 정의: START -> Analyzer -> Questioner 진입 구조 (`src/apps/inquiry/graph.py`)
- [x] T014 [US1] `ajax-api.md`를 준수하는 Async Chat API View 초기 구현 (세션 생성 및 첫 응답) (`src/apps/inquiry/views.py`)
- [x] T015 [US1] AJAX 기반 대화 UI 및 인디케이터 템플릿 구현 (`src/templates/inquiry/chat.html`)

**체크포인트**: 사용자 스토리 1 완료 - 시스템이 사용자의 입력을 받고 대화를 시작할 수 있습니다.

---

## Phase 4: 사용자 스토리 2 - 5 Whys 심층 문답 진행 (우선순위: P1)

**목표**: 최대 5회의 문답을 통해 인과관계를 심층적으로 탐색함

**독립적 테스트 (Independent Test)**: 3~5회 문답 동안 질문의 깊이가 점진적으로 깊어지며 `current_step`이 정상 증가하는지 확인

### 사용자 스토리 2를 위한 테스트

- [x] T016 [P] [US2] Questioner Node의 인과관계 추론 및 질문 생성 단위 테스트 작성 (`src/apps/inquiry/tests/test_nodes.py`)
- [x] T017 [P] [US2] 문답 반복 시 GraphState의 `current_step` 무결성 검증 테스트 작성 (`src/apps/inquiry/tests/test_graph.py`)

### 사용자 스토리 2 구현

- [x] T018 [US2] Questioner Node 구현: 이전 답변 분석 및 5 Whys 기반 심층 질문 생성 (`src/apps/inquiry/nodes.py`)
- [x] T019 [US2] LangGraph 루프 구성: Questioner -> User Input -> Analyzer 반복 순환 구조 (`src/apps/inquiry/graph.py`)
- [x] T020 [US2] Async View 고도화: 기존 세션 유지 및 지속적인 대화 상태 업데이트 로직 (`src/apps/inquiry/views.py`)

**체크포인트**: 사용자 스토리 2 완료 - 사용자와 AI가 심층적인 문답을 주고받으며 문제를 파고들 수 있습니다.

---

## Phase 5: 사용자 스토리 3 - 진단 종료 및 문제 기술서 생성 (우선순위: P1)

**목표**: 진단 완료 후 구조화된 Markdown 및 JSON 기술서를 생성함

**독립적 테스트 (Independent Test)**: 종료 조건 도달 시 파일 생성 및 '인과관계 연쇄'가 기술서에 포함되었는지 검증

### 사용자 스토리 3을 위한 테스트

- [x] T021 [P] [US3] Edge Logic의 종료 조건(5단계 도달 또는 근본 원인 파악) 판단 테스트 작성 (`src/apps/inquiry/tests/test_graph.py`)
- [x] T022 [P] [US3] 최종 문제 기술서(Markdown/JSON) 스키마 유효성 검사 테스트 작성 (`src/apps/inquiry/tests/test_services.py`)

### 사용자 스토리 3 구현

- [x] T023 [US3] Edge Logic 구현: 사용자의 종료 동의 여부를 확인하고 상태를 전이하는 제어 로직 (`src/apps/inquiry/graph.py`)
- [x] T024 [US3] 결과 생성 서비스 구현: 수집된 정보를 바탕으로 기술서 생성 (`src/apps/inquiry/services.py`)
- [x] T025 [US3] UI 결과 화면 구현: 생성된 기술서 다운로드 및 요약 보고서 노출 (`src/templates/inquiry/chat.html`)

**체크포인트**: 모든 사용자 스토리 완료 - 전체 진단 프로세스가 완결되어 결과물을 제공합니다.

---

## Phase N: 마무리 및 횡단 관심사 - Phase N: Polish & Cross-Cutting Concerns

**목적**: 품질 검증 및 헌법 준수 마무리

- [x] T026 [P] 전체 코드에 대해 Ruff check 및 mypy 엄격 모드 검증 수행
- [x] T027 모든 클래스 및 노드 메서드에 한국어 Google Style Docstring 적용 여부 전수 조사
- [x] T028 [P] `uv lock`으로 의존성 버전 고정 및 `README.md` 설치 가이드 업데이트
- [x] T029 LLM 호출 실패 시 지수 백오프(Exponential Backoff) 및 Fallback 동작 최종 검증 (`src/core/llm.py`)
- [x] T030 NFR-003 성능 지표(P95 5초 이내) 준수 여부 확인을 위한 부하 테스트 수행

---

## 의존성 및 실행 순서 (Dependencies & Execution Order)

### 단계별 의존성 (Phase Dependencies)

- **Phase 1 (Setup)**: 즉시 시작 가능
- **Phase 2 (Foundational)**: Phase 1 완료 후 시작. 모든 사용자 스토리의 필수 선행 조건.
- **Phase 3~5 (User Stories)**: Phase 2 완료 후 우선순위(P1)에 따라 진행. 
  - 세 스토리는 모두 P1이나, 논리적 흐름상 US1 -> US2 -> US3 순차 진행 권장.

### 사용자 스토리 내부 순서

- **테스트 우선**: 각 스토리 구현 전 `tests/` 내 테스트 코드를 먼저 작성하여 실패 확인
- **데이터 → 로직 → 인터페이스**: Models -> Nodes/Services -> Views -> Templates 순서로 구현

### 병렬 실행 기회 (Parallel Opportunities)

- [P] 표시된 모든 테스트 작업은 구현과 병렬로 진행 가능
- Phase 2의 DB 설정(T005)과 LLM 인터페이스(T006)는 병렬로 진행 가능
- 각 스토리의 프론트엔드 템플릿(T015, T025)은 백엔드 로직과 어느 정도 병렬로 진행 가능

---

## 병렬 실행 예시: 사용자 스토리 1

```bash
# 개발자 A: Analyzer Node 로직 구현 및 테스트
작업: T010 [US1] Analyzer Node 단위 테스트 작성
작업: T012 [US1] Analyzer Node 구현

# 개발자 B: UI 및 API 인터페이스 구현
작업: T015 [US1] AJAX 기반 대화 UI 템플릿 구현
작업: T014 [US1] Async Chat API View 초기 구현
```

---

## 구현 전략 (Implementation Strategy)

### MVP 우선 (사용자 스토리 1 위주)

1. Phase 1 & 2를 신속히 완료하여 진단 가능 환경 구축
2. Phase 3(US1)을 구현하여 "사용자 입력 -> AI 첫 반응"의 핵심 루프 검증
3. **중단 및 검증**: 로컬 Ollama 연동 및 메타데이터 추출 정확도 확인

### 점진적 인도 (Incremental Delivery)

1. 기반 준비 완료 (Phase 2)
2. 시작 기능 제공 (US1) -> 문답 기능 추가 (US2) -> 결과 보고서 추가 (US3)
3. 각 단계마다 `Independent Test`를 수행하여 회귀 오류 방지

---

## 참고 (Notes)

- 모든 코드는 헌법에 따라 한국어 주석 및 Docstring을 포함해야 함
- 비동기 처리(`AsyncView`, `LangGraph`) 시 스레드 안정성 및 DB 세션 관리에 유의함
- `uv`를 사용하여 의존성 혼선을 방지하고 일관된 환경 유지

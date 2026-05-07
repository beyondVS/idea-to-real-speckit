# 구현 계획 (Implementation Plan): root-cause-derivation

**브랜치 (Branch)**: `002-featurename-root-cause-derivation` | **날짜 (Date)**: 2026-05-07 | **명세서 (Spec)**: [spec.md](./spec.md)
**입력 (Input)**: `/specs/002-root-cause-derivation/spec.md`에서 가져온 기능 명세서

## 요약 (Summary)

사용자의 질의 답변을 바탕으로 **문제의 본질(Root Cause)**을 추론하고, LangGraph 상태 머신을 통해 **질의 횟수(기본 5회)** 및 **연장 승인 워크플로우**를 제어하는 기능을 구현합니다. 도출된 원인에 대해서는 **확신도 라벨링**과 **상세화 가능성 판단**을 수행하여 분석의 깊이를 조절합니다.

## 기술적 문맥 (Technical Context)

**언어/버전 (Language/Version)**: Python 3.13 (Type Hints 준수 의무)
**프레임워크 (Framework)**: Django 5.2 LTS (Backend), LangGraph (State Machine)
**데이터베이스 (Database)**: PostgreSQL (JSONField를 활용한 분석 결과 저장)
**패키지 관리 (Package Management)**: `uv` (0.6.x 이상)
**도구 (Tooling)**: `Ruff` (Lint & Format)
**대상 플랫폼 (Target Platform)**: Web Interface (Django Templates + AJAX)
**성능 목표 (Performance Goals)**: LLM 분석 노드 응답 시간 3초 이내 (P95), 상태 전이 지연 < 100ms
**제약 사항 (Constraints)**: 헌법상 실용주의 원칙 준수, 무한 루프 방지(의미 없는 답변 3회 제한)

## 헌법 준수 확인 (Constitution Check)

*게이트(GATE): Phase 0 연구 전에 통과해야 함. Phase 1 설계 후 다시 확인.*

- [x] **Problem Space First**: 명세서에서 문제의 본질 도출 및 상세화 가능성 판단을 핵심 가치로 정의함.
- [x] **Pragmatism**: 복잡한 아키텍처 대신 LangGraph의 노드와 에지 조건을 활용한 명확한 흐름 제어 설계.
- [x] **Type Safety**: `InquiryState` 및 `RootCause` 데이터 구조에 TypedDict 적용 계획.
- [x] **Documentation**: 모든 분석 로직 및 상태 전이 함수에 한국어 Google Style Docstring 적용.
- [x] **Django Standard**: `InquirySession` 확장 시 Django ORM 표준 필드 사용.
- [x] **Reliability**: LLM 호출 실패 시 지수 백오프 적용 (LangGraph built-in retry 또는 커스텀 wrapper).

## 프로젝트 구조 (Project Structure)

### 문서 (이 기능 관련)

```text
specs/002-root-cause-derivation/
├── plan.md              # 이 파일
├── research.md          # 연구 결과 (RCA 패턴, 확신도 매핑 등)
├── data-model.md        # InquirySession 확장 및 RootCause 엔티티 설계
├── quickstart.md        # 로직 테스트 시나리오 가이드
├── contracts/           
│   └── logic-flow.md    # 상태 머신 입출력 및 UI 계약
└── checklists/
    └── requirements.md  # 명세 품질 체크리스트
```

### 소스 코드 (저장소 루트)

```text
src/
├── apps/inquiry/
│   ├── graph.py         # LangGraph 워크플로우 정의 (Analyzer 노드 추가)
│   ├── nodes.py         # 분석 및 질의 생성 로직 구현
│   ├── models.py        # 세션 및 분석 결과 모델
│   └── tests/
│       └── test_root_cause_logic.py  # 시나리오 기반 로직 검증
```

## 복잡성 추적 (Complexity Tracking)

*특이사항 없음. 모든 설계가 헌법 및 프로젝트 표준을 준수함.*

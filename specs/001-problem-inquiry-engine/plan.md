# 구현 계획 (Implementation Plan): Problem Inquiry Engine (진단 엔진)

**브랜치 (Branch)**: `main` (전환 예정) | **날짜 (Date)**: 2026-04-24 | **명세서 (Spec)**: [specs/001-problem-inquiry-engine/spec.md](spec.md)
**입력 (Input)**: 사용자 설명, Ollama gemma4:e4b 모델, Django AJAX 통신 요구사항

## 요약 (Summary)
사용자의 모호한 문제를 분석하여 구조화된 명세서를 생성하는 시스템을 구현합니다. LangChain 및 LangGraph를 사용하여 상태 기반 에이전트 아키텍처를 구축하고, 로컬 Ollama 서버와 통신합니다. 사용자 인터페이스는 Django 비동기 뷰와 AJAX를 통해 실시간 피드백을 제공합니다.

## 기술적 문맥 (Technical Context)

**언어/버전 (Language/Version)**: Python 3.13 (Type Hints 준수)
**프레임워크 (Framework)**: Django 5.2 LTS (Backend)
**데이터베이스 (Database)**: PostgreSQL (세션 및 상태 저장)
**LLM 도구 (LLM Tooling)**: LangChain, LangGraph, Ollama (gemma4:e4b)
**패키지 관리 (Package Management)**: `uv`
**도구 (Tooling)**: `Ruff` (Lint & Format), `mypy` (Type Check)
**성능 목표 (Performance Goals)**: LLM 응답 대기 중 AJAX 인디케이터 표시, 5단계 이내 진단 완결

## 헌법 준수 확인 (Constitution Check)

- [x] **Problem Space First**: 해결책 이전에 문제 본질 분석 로직(Analyzer Node)이 설계됨.
- [x] **Pragmatism**: 복잡한 소켓 통신 대신 단순한 AJAX 패턴 채택.
- [x] **Type Safety**: Python 3.13 기반 Type Hints 설계 완료.
- [x] **Documentation**: 모든 코드에 한국어 Google Style Docstring 적용 예정.
- [x] **Django Standard**: Django 5.2 표준 레이아웃 및 마이그레이션 도구 활용.
- [x] **Reliability**: LangChain의 재시도 전략 및 지수 백오프 적용 예정.

## 프로젝트 구조 (Project Structure)

### 문서 (이 기능 관련)
```text
specs/001-problem-inquiry-engine/
├── spec.md              # 기능 명세서
├── plan.md              # 이 파일
├── research.md          # 기술 조사 보고서
├── data-model.md        # 데이터베이스 및 엔티티 설계
├── contracts/
│   └── ajax-api.md      # AJAX 인터페이스 규약
└── tasks.md             # 작업 목록 (다음 단계에서 생성)
```

### 소스 코드 레이아웃
```text
src/
├── config/              # Django settings (Async 지원)
├── apps/
│   └── inquiry/         # 진단 엔진 핵심 앱
│       ├── models.py    # InquirySession, ProblemSpecification
│       ├── views.py     # Async Chat API View
│       ├── nodes.py     # LangGraph Nodes (Analyzer, Questioner)
│       └── graph.py     # LangGraph 상태 머신 정의
├── core/
│   └── llm.py           # ChatOllama 설정 및 추상화 인터페이스
└── templates/
    └── inquiry/
        └── chat.html    # AJAX 기반 대화 UI
```

## 복잡성 추적 (Complexity Tracking)
- **Django Async + LangGraph**: 비동기 환경에서 상태 머신을 안정적으로 구동하기 위해 세심한 동기화 처리가 필요함. `research.md`의 패턴을 엄격히 준수함.

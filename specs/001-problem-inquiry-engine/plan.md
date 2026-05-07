# 구현 계획 (Implementation Plan): Problem Inquiry Engine (진단 엔진)

**브랜치 (Branch)**: `001-problem-inquiry-engine` | **날짜 (Date)**: 2026-04-29 | **명세서 (Spec)**: [spec.md](spec.md)
**입력 (Input)**: `/specs/001-problem-inquiry-engine/spec.md`에서 가져온 기능 명세서

## 요약 (Summary)

사용자의 모호한 아이디어를 입력받아 **지능형 인쿼리 엔진(LangGraph)**과 논리적 추론을 통해 문제의 본질을 파악하고, 구조화된 **'문제 기술서'**를 생성하는 시스템입니다. Django 5.2와 PostgreSQL을 기반으로 대화 상태를 관리하며, Ollama(gemma4:e4b)를 연동하여 실시간 심층 문답(5 Whys)을 수행합니다. 사용자는 자신의 진단 이력을 관리하고 최종 결과물을 Markdown 형식으로 다운로드할 수 있습니다.

## 기술적 문맥 (Technical Context)

**언어/버전 (Language/Version)**: Python 3.13 (Type Hints 준수 의무)
**프레임워크 (Framework)**: Django 5.2 LTS (Backend)
**데이터베이스 (Database)**: PostgreSQL (InquirySession 및 상태 저장)
**패키지 관리 (Package Management)**: `uv` (버전 명시 필수)
**도구 (Tooling)**: `Ruff` (Lint & Format), `mypy` (Type Safety 검증)
**대상 플랫폼 (Target Platform)**: Linux 서버 (Docker 환경 권장)
**성능 목표 (Performance Goals)**: 질문 생성 응답 시간 P95 5초 이내, 작업 큐를 통한 동시성 제어  
**제약 사항 (Constraints)**: 헌법상 실용주의 원칙 준수, Over-engineering 금지, 개인정보 마스킹 필수

## 헌법 준수 확인 (Constitution Check)

*게이트(GATE): Phase 0 연구 전에 통과해야 함. Phase 1 설계 후 다시 확인.*

- [x] **Problem Space First**: 해결책 이전에 문제의 본질(Root Cause)이 명확히 정의되었는가?
- [x] **Pragmatism**: Over-engineering 없이 가장 단순하고 명확한 해결책인가?
- [x] **Type Safety**: 모든 함수 인자와 반환값에 Type Hints가 설계되었는가?
- [x] **Documentation**: 한국어 Google Style Docstring 작성이 계획되었는가?
- [x] **Django Standard**: 마이그레이션 도구(makemigrations) 사용 및 ORM 우선주의를 따르는가?
- [x] **Reliability**: 외부 API 호출 시 지수 백오프 및 Fallback 전략이 포함되었는가?

## 프로젝트 구조 (Project Structure)

### 문서 (이 기능 관련)

```text
specs/001-problem-inquiry-engine/
├── spec.md              # 기능 명세서 (최종 개정 2026-04-29)
├── plan.md              # 이 파일
├── research.md          # Phase 0 출력 (기술 조사 및 결정)
├── data-model.md        # Phase 1 출력 (엔티티 설계)
├── quickstart.md        # Phase 1 출력 (실행 가이드)
├── contracts/           # Phase 1 출력 (인터페이스 규약)
│   └── ajax-api.md      # AJAX 기반 채팅 API 계약
└── tasks.md             # Phase 2 출력 (/speckit.tasks 명령 생성)
```

### 소스 코드 (저장소 루트)

```text
# Django 표준 레이아웃 (헌법 준수)
src/
├── config/              # settings (Async 지원), logging (보안 필터)
├── apps/                # Django Applications
│   └── inquiry/         # 진단 엔진 핵심 앱
│       ├── models.py    # InquirySession, ProblemSpecification
│       ├── views.py     # Async Chat API Views
│       ├── services.py  # Result Generation, Masking Service
│       ├── nodes.py     # LangGraph Nodes (Analyzer, Questioner)
│       └── graph.py     # LangGraph 상태 머신 정의 및 롤백 로직
├── core/                # llm.py (Ollama 추상화), backoff 유틸리티
└── templates/
    └── inquiry/
        └── chat.html    # AJAX 기반 분기 탐색 UI
```

## 복잡성 추적 (Complexity Tracking)

| 위반 사항 | 필요성 | 더 간단한 대안을 거부한 이유 |
|-----------|------------|-------------------------------------|
| [Django Async + LangGraph] | [비동기 스트리밍 및 상태 관리] | [동기 방식으로는 UX 요구사항(5초 이내 피드백) 충족 불가] |

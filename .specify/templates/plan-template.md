# 구현 계획 (Implementation Plan): [FEATURE]

**브랜치 (Branch)**: `[###-feature-name]` | **날짜 (Date)**: [DATE] | **명세서 (Spec)**: [link]
**입력 (Input)**: `/specs/[###-feature-name]/spec.md`에서 가져온 기능 명세서

**참고**: 이 템플릿은 `/speckit.plan` 명령에 의해 채워집니다. 실행 워크플로우는 `.specify/templates/plan-template.md`를 참조하십시오.

## 요약 (Summary)

[기능 명세서에서 추출: 주요 요구사항 + 연구 결과에 따른 기술적 접근 방식]

## 기술적 문맥 (Technical Context)

**언어/버전 (Language/Version)**: Python 3.13 (Type Hints 준수 의무)
**프레임워크 (Framework)**: Django 5.2 LTS (Backend)
**데이터베이스 (Database)**: PostgreSQL
**패키지 관리 (Package Management)**: `uv` (버전 명시 필수)
**도구 (Tooling)**: `Ruff` (Lint & Format)
**대상 플랫폼 (Target Platform)**: [예: Linux 서버, AWS 등]
**성능 목표 (Performance Goals)**: [도메인별, 예: 1000 req/s, <200ms p95]  
**제약 사항 (Constraints)**: [헌법상 실용주의 원칙 준수, Over-engineering 금지]

## 헌법 준수 확인 (Constitution Check)

*게이트(GATE): Phase 0 연구 전에 통과해야 함. Phase 1 설계 후 다시 확인.*

- [ ] **Problem Space First**: 해결책 이전에 문제의 본질(Root Cause)이 명확히 정의되었는가?
- [ ] **Pragmatism**: Over-engineering 없이 가장 단순하고 명확한 해결책인가?
- [ ] **Type Safety**: 모든 함수 인자와 반환값에 Type Hints가 설계되었는가?
- [ ] **Documentation**: 한국어 Google Style Docstring 작성이 계획되었는가?
- [ ] **Django Standard**: 마이그레이션 도구(makemigrations) 사용 및 ORM 우선주의를 따르는가?
- [ ] **Reliability**: 외부 API 호출 시 지수 백오프 및 Fallback 전략이 포함되었는가?

## 프로젝트 구조 (Project Structure)

### 문서 (이 기능 관련)

```text
specs/[###-feature]/
├── plan.md              # 이 파일 (/speckit.plan 명령 출력)
├── research.md          # Phase 0 출력 (/speckit.plan 명령)
├── data-model.md        # Phase 1 출력 (/speckit.plan 명령)
├── quickstart.md        # Phase 1 출력 (/speckit.plan 명령)
├── contracts/           # Phase 1 출력 (/speckit.plan 명령)
└── tasks.md             # Phase 2 출력 (/speckit.tasks 명령 - /speckit.plan에 의해 생성되지 않음)
```

### 소스 코드 (저장소 루트)

```text
# Django 표준 레이아웃 (헌법 준수)
src/
├── config/              # settings, wsgi, asgi
├── apps/                # Django Applications
│   └── [app_name]/
│       ├── models.py    # ORM 우선주의 준수
│       ├── views.py     # Async Views 활용
│       └── services.py  # 비즈니스 로직 (BaseAgent 추상화 등)
├── core/                # 공통 유틸리티, 상태 머신(LangGraph)
└── tests/               # 프레임워크 권장 TDD
```

## 복잡성 추적 (Complexity Tracking)

> **헌법 준수 확인에서 정당화되어야 하는 위반 사항이 있는 경우에만 작성하십시오.**

| 위반 사항 | 필요성 | 더 간단한 대안을 거부한 이유 |
|-----------|------------|-------------------------------------|
| [예: Raw SQL 사용] | [특정 성능 문제] | [ORM으로 해결 불가능한 사유] |

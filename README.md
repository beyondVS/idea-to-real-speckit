# idea-to-real-speckit

아이디어에서 실제 구현까지, 명세 기반 개발(Specification Driven Development)을 지원하는 도구입니다.

## 核心 철학 (Core Philosophy)

1. **Problem Space First**: 해결책 이전에 문제의 본질(Root Cause)을 정의합니다.
2. **실용주의 (Pragmatism)**: 단순하고 명확한 해결책을 지향하며 Over-engineering을 금지합니다.
3. **한국어 최우선 (Language First)**: 모든 대화, 문서, 커밋 메시지 및 코드 내 주석은 한국어를 사용합니다.

## 기술 스택 (Tech Stack)

- **언어**: Python 3.13 (Type Hints 필수)
- **프레임워크**: Django 5.2 LTS
- **데이터베이스**: PostgreSQL
- **패키지 관리**: `uv`
- **코드 품질**: `Ruff` (Lint & Format)

## 개발 규율 (Engineering Excellence)

- **Stateful Architecture**: LangGraph 상태 머신을 통한 대화 흐름 관리
- **Type Safety**: 엄격한 타입 힌트 적용 및 검증
- **Documentation**: Google Style Docstring (한국어) 필수 적용
- **Django Standard**: ORM 우선주의 및 도구 기반 마이그레이션 관리
- **Reliability**: 지수 백오프 기반 재시도 전략 적용

---
*이 프로젝트는 [프로젝트 헌법](.specify/memory/constitution.md)을 엄격히 준수합니다.*

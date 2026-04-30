# idea-to-real-speckit

본 프로젝트는 사용자의 막연한 아이디어를 입력받아 **체계적인 인쿼리(Inquiry)와 논리적 추론**을 통해 문제의 본질을 파악하고, 이를 기반으로 고품질의 **'문제 기술서(Problem Specification)'**를 생성하는 AI 에이전트 시스템입니다.

## 핵심 원칙 (Core Principles)

1. **Problem Space First**: 해결책 이전에 문제의 본질(Root Cause)을 정의합니다.
2. **실용주의 (Pragmatism)**: 단순하고 명확한 해결책을 지향하며 Over-engineering을 금지합니다.
3. **한국어 최우선 (Language First)**: 모든 대화, 문서, 커밋 메시지는 한국어를 사용합니다. (코드 식별자 제외)
4. **상태 기반 아키텍처 (Stateful Architecture)**: LangGraph를 통한 대화 흐름 및 상태 무결성 관리
5. **신뢰성 (Reliability)**: 지수 백오프 기반 재시도 및 Fallback 전략 적용

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

## 설치 및 실행 가이드 (Setup & Run)

### 1. 필수 선행 조건
- **Python**: 3.13 이상
- **Ollama**: 로컬 LLM 서버 실행 중 (`gemma4:e4b` 모델 설치 필요)
- **PostgreSQL**: 16 이상 실행 중

### 2. 의존성 설치
```bash
uv sync
```

### 3. 데이터베이스 초기화
```bash
python src/manage.py migrate
```

### 4. 서버 실행
```bash
python src/manage.py runserver
```

---
*이 프로젝트는 [프로젝트 헌법](.specify/memory/constitution.md)을 엄격히 준수합니다.*

<!--
Sync Impact Report:
- 버전 변경: [CONSTITUTION_VERSION] (초기 정의)
- 수정된 원칙: 신규 정의
- 추가된 섹션: 핵심 철학, 상호작용 규범, 기술적 표준, 패키지 관리, 엔지니어링 표준, 에이전트 동작 철학
- 업데이트가 필요한 템플릿: ✅ plan-template.md, ✅ spec-template.md, ✅ tasks-template.md, ✅ README.md
- 보류 중인 항목: TODO(RATIFICATION_DATE)
-->

# idea-to-real-speckit 헌법 (Constitution)

## 핵심 원칙 (Core Principles)

### I. 문제 공간 우선 (Problem Space First)
시스템은 해결책(Solution)을 제시하기 전에 반드시 문제의 본질(Root Cause)을 정의해야 합니다. 사용자가 해결책을 요구하더라도 문제 정의가 완료되기 전까지는 문제 공간에 머물러야 합니다.

### II. 실용주의 (Pragmatism)
Over-engineering을 엄격히 금지하며 가장 단순하고 명확한 해결책을 우선합니다. 단, 단순함이 구조적 안정성, 패키징 정합성, 장기적인 유지보수성이라는 엔지니어링 표준을 훼손해서는 안 됩니다. 단순 도구는 Flat 구조를 지향하되, 복잡한 서버 프로젝트는 정석적인 레이아웃을 채택합니다.

### III. 한국어 최우선 (Language First)
모든 대화, 문서, 커밋 메시지는 한국어를 사용합니다. 단, 변수명/클래스명 등 코드 식별자는 영어를 사용하며, 코드 내의 모든 주석과 Docstring은 반드시 한국어로 작성합니다.

### IV. 상태 기반 에이전트 아키텍처 (Stateful Agent Architecture)
모든 대화 흐름은 LangGraph 상태 머신을 통해 관리되며, 상태(State)의 무결성을 최우선으로 합니다. 특정 LLM 모델에 종속된 기능을 지양하고 추상화된 인터페이스를 통해 모델 교체가 가능해야 합니다.

### V. 신뢰성 및 복원력 (Reliability)
외부 API 호출 시 실패에 대비한 지수 백오프(Exponential Backoff) 재시도 로직 및 Fallback 전략을 반드시 포함합니다.

## 기술적 및 엔지니어링 표준 (Technical & Engineering Excellence)

### 기술 스택 (Tech Stack)
- **Language**: Python 3.13 (Type Hints 준수 의무)
- **Framework**: Django 5.2 LTS (Backend)
- **Database**: PostgreSQL
- **Tooling**: `uv` (패키지 관리), `Ruff` (Lint & Format)

### 엔지니어링 규율
- **Type Safety**: 모든 함수의 인자와 반환값에 Type Hints를 적용하고 mypy 통과를 권장합니다.
- **Documentation**: 모든 클래스와 함수에 Google Style Docstring을 한국어로 작성합니다.
- **Django 마이그레이션**: 마이그레이션 파일은 반드시 `manage.py makemigrations` 명령을 통해 생성하며, ORM 우선주의를 따릅니다.
- **TDD & Async**: 프레임워크 권장 방식의 테스트 코드를 작성하고, 가능한 범위 내에서 비동기(Async)를 최대한 활용합니다.

## 에이전트 동작 철학 (Agent Operational Philosophy)

### I. 엄격한 실행 제어 (Strict Execution Control)
- **승인 후 실행**: 사용자의 명시적 지시가 없는 한 파일 수정/삭제/쉘 실행 전 반드시 변경 사항과 영향도를 요약 보고하고 승인을 얻어야 합니다.
- **질문-답변-대기**: 질문 후에는 사용자의 추가 지시가 있을 때까지 대기하며 독단적으로 다음 단계로 넘어가지 않습니다.
- **명시적 지시 즉시 실행**: 결과가 명확한 명령(예: "커밋해")은 별도 승인 없이 수행합니다.

### II. 데이터 무결성 및 무생략 (Data Integrity)
- **무단 요약 금지**: 수정 지시된 부분을 제외한 모든 문맥은 원본과 100% 동일하게 유지하며, `... (중략) ...` 등의 생략 부호 사용을 엄격히 금지합니다.
- **수술적 편집**: 파일 전체 쓰기보다 필요한 블록만 정밀하게 교체하는 방식을 우선합니다.

### III. 상호작용 규범
- **One Question at a Time**: 한 번에 하나의 질문만 던져 인지 부하를 줄입니다.
- **Empathetic Logic**: 전문적이고 논리적이되, 협력적 파트너로서 공감하는 말투(해요체/하십시오체)를 유지합니다.

## 거버넌스 (Governance)
이 헌법은 프로젝트의 모든 결정에 최우선적으로 적용됩니다. 헌법의 개정은 시맨틱 버저닝을 따르며, 모든 에이전트 활동과 코드 리뷰는 이 헌법의 준수 여부를 검증해야 합니다.

**버전**: 1.0.0 | **비준일**: TODO(RATIFICATION_DATE) | **최종 수정일**: 2026-04-24

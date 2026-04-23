# 구현 계획 (Implementation Plan): [FEATURE]

**브랜치 (Branch)**: `[###-feature-name]` | **날짜 (Date)**: [DATE] | **명세서 (Spec)**: [link]
**입력 (Input)**: `/specs/[###-feature-name]/spec.md`에서 가져온 기능 명세서

**참고**: 이 템플릿은 `/speckit.plan` 명령에 의해 채워집니다. 실행 워크플로우는 `.specify/templates/plan-template.md`를 참조하십시오.

## 요약 (Summary)

[기능 명세서에서 추출: 주요 요구사항 + 연구 결과에 따른 기술적 접근 방식]

## 기술적 문맥 (Technical Context)

<!--
  작업 필요: 이 섹션의 내용을 프로젝트의 기술적 세부 사항으로 교체하십시오.
  여기에 제시된 구조는 반복 프로세스를 안내하기 위한 자문 역할을 합니다.
-->

**언어/버전 (Language/Version)**: [예: Python 3.11, Swift 5.9, Rust 1.75 또는 확인 필요(NEEDS CLARIFICATION)]  
**주요 의존성 (Primary Dependencies)**: [예: FastAPI, UIKit, LLVM 또는 확인 필요(NEEDS CLARIFICATION)]  
**저장소 (Storage)**: [해당하는 경우, 예: PostgreSQL, CoreData, 파일 또는 해당 없음(N/A)]  
**테스트 (Testing)**: [예: pytest, XCTest, cargo test 또는 확인 필요(NEEDS CLARIFICATION)]  
**대상 플랫폼 (Target Platform)**: [예: Linux 서버, iOS 15+, WASM 또는 확인 필요(NEEDS CLARIFICATION)]
**프로젝트 유형 (Project Type)**: [예: 라이브러리/CLI/웹 서비스/모바일 앱/컴파일러/데스크톱 앱 또는 확인 필요(NEEDS CLARIFICATION)]  
**성능 목표 (Performance Goals)**: [도메인별, 예: 1000 req/s, 10k lines/sec, 60 fps 또는 확인 필요(NEEDS CLARIFICATION)]  
**제약 사항 (Constraints)**: [도메인별, 예: <200ms p95, <100MB 메모리, 오프라인 지원 가능 또는 확인 필요(NEEDS CLARIFICATION)]  
**규모/범위 (Scale/Scope)**: [도메인별, 예: 1만 사용자, 100만 LOC, 50개 화면 또는 확인 필요(NEEDS CLARIFICATION)]

## 헌법 준수 확인 (Constitution Check)

*게이트(GATE): Phase 0 연구 전에 통과해야 함. Phase 1 설계 후 다시 확인.*

[헌법 파일을 기반으로 결정된 게이트들]

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
<!--
  작업 필요: 아래의 플레이스홀더 트리를 이 기능에 대한 구체적인 레이아웃으로 교체하십시오.
  사용하지 않는 옵션은 삭제하고 선택한 구조를 실제 경로(예: apps/admin, packages/something)로 확장하십시오.
  최종 계획에는 옵션 레이블이 포함되어서는 안 됩니다.
-->

```text
# [사용하지 않는 경우 삭제] 옵션 1: 단일 프로젝트 (기본값)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [사용하지 않는 경우 삭제] 옵션 2: 웹 애플리케이션 ("frontend" + "backend"가 감지된 경우)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [사용하지 않는 경우 삭제] 옵션 3: 모바일 + API ("iOS/Android"가 감지된 경우)
api/
└── [위의 backend와 동일]

ios/ 또는 android/
└── [플랫폼별 구조: 기능 모듈, UI 흐름, 플랫폼 테스트]
```

**구조 결정**: [선택한 구조를 문서화하고 위에서 캡처한 실제 디렉토리를 참조하십시오]

## 복잡성 추적 (Complexity Tracking)

> **헌법 준수 확인에서 정당화되어야 하는 위반 사항이 있는 경우에만 작성하십시오.**

| 위반 사항 | 필요성 | 더 간단한 대안을 거부한 이유 |
|-----------|------------|-------------------------------------|
| [예: 4번째 프로젝트] | [현재 요구사항] | [3개 프로젝트로는 부족한 이유] |
| [예: Repository 패턴] | [특정 문제] | [직접 DB 액세스로는 부족한 이유] |

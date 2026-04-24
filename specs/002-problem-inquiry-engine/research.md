# 연구 보고서 (Research Report): Problem Inquiry Engine (진단 엔진)

## 개요 (Outline)
이 보고서는 진단 엔진 구현을 위한 핵심 기술적 결정 사항과 근거를 정리합니다. 헌법에 정의된 기술 스택과 사용자가 제시한 추가 제약 사항(Ollama, Django AJAX)을 통합합니다.

## 기술적 결정 (Technical Decisions)

### 1. LLM 연동 및 프레임워크
- **결정(Decision)**: `LangChain` + `ChatOllama` 인터페이스 사용.
- **근거(Rationale)**: 헌법의 'Provider Agnostic' 원칙을 준수하며, 로컬 Ollama 서버의 `gemma4:e4b` 모델과 표준화된 방식으로 통신 가능함. 향후 모델 교체가 용이함.
- **고려된 대안(Alternatives)**: Ollama Python Library 직접 사용 (추상화 수준이 낮아 헌법 위배 가능성으로 반려).

### 2. Django 비동기 상호작용
- **결정(Decision)**: Django `AsyncView` + `Vanilla JS AJAX` (Fetch API) + `Indicator UI`.
- **근거(Rationale)**: Django 5.2의 비동기 기능을 활용하여 LLM 응답 대기 시간 동안 서버 리소스를 효율적으로 관리함. 프론트엔드에서 요청 전 인디케이터를 활성화하고 응답 후 비활성화하는 단순하고 명확한 패턴(Pragmatism) 채택.
- **고려된 대안(Alternatives)**: Django Channels (실시간 양방향성이 필수적이지 않은 현 단계에서는 오버엔지니어링으로 판단되어 반려).

### 3. 상태 관리 및 저장소
- **결정(Decision)**: `LangGraph` + `PostgresSaver` (Checkpointer).
- **근거(Rationale)**: 헌법의 'Stateful Agent Architecture'를 구현하기 위해 LangGraph의 상태 관리 기능을 사용하며, 데이터 보존 정책에 따라 PostgreSQL을 영구 저장소로 활용함.

### 4. 코드 품질 및 문서화
- **결정(Decision)**: `Ruff` + `mypy` + `Google Style Docstring` (한국어).
- **근거(Rationale)**: 엔지니어링 표준 엄격 준수.

## 연구 작업 (Research Tasks)
- [x] Ollama `gemma4:e4b` 모델 가용성 및 LangChain 호환성 확인
- [x] Django Async View 내에서 LangGraph 실행 패턴 검증
- [x] PostgreSQL을 이용한 LangGraph 상태 체크포인트 설정 가이드 작성

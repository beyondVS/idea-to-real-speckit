# 기술 조사 보고서 (Research): Problem Inquiry Engine (진단 엔진)

## 개요 및 목적
본 문서는 구현 계획 수립을 위한 핵심 기술적 불확실성을 해소하고, 선택된 기술적 접근 방식에 대한 근거를 기록합니다.

---

## 1. Django Async + LangGraph 동기화 패턴

### 결정 (Decision)
Django의 비동기 뷰(`AsyncView`)와 LangGraph의 비동기 스트리밍(`astream`)을 통합하여 실시간 대화 상태를 관리합니다.

### 근거 (Rationale)
- 사용자의 질문 생성 응답 시간(P95 5초)을 준수하기 위해서는 LLM 응답을 기다리는 동안 블로킹되지 않는 비동기 처리가 필수적입니다.
- LangGraph는 비동기 상태 전이를 기본적으로 지원하므로, Django `ASGI` 환경과 완벽하게 호환됩니다.

### 고려된 대안 (Alternatives considered)
- **Celery 기반 비동기 처리**: 작업 완료 후 웹소켓으로 알림을 주는 방식은 구조가 복잡해지며, 단순 AJAX 패턴이라는 헌법의 '실용주의' 원칙에 위배될 수 있어 기각함.

---

## 2. PostgreSQL PostgresSaver를 이용한 체크포인팅

### 결정 (Decision)
LangGraph의 `PostgresSaver`를 사용하여 대화의 모든 스냅샷을 PostgreSQL에 실시간 저장하고, 이를 통해 자동 복구 및 롤백 기능을 구현합니다.

### 근거 (Rationale)
- 명세(`FR-003`)의 상태 롤백 및 네트워크 단절 시 자동 재개 요구사항을 충족하는 가장 효율적인 도구입니다.
- Django의 기본 DB인 PostgreSQL을 공유함으로써 인프라 복잡성을 낮출 수 있습니다.

---

## 3. 개인정보 자동 탐지 및 마스킹 전략

### 결정 (Decision)
`Microsoft Presidio` 또는 정규식 기반의 커스텀 필터링 서비스를 `src/apps/inquiry/services.py`에 구현하여 저장 전 마스킹을 수행합니다.

### 근거 (Rationale)
- 사용자가 직접 입력한 민감 정보를 LLM에 전송하거나 DB에 원문 저장하는 위험을 방지합니다.
- 한국어 특정 패턴(전화번호, 주민번호 등)에 최적화된 정규식을 결합하여 정확도를 높입니다.

---

## 4. Ollama 서버 부하 관리 및 작업 큐

### 결정 (Decision)
Django 내부의 `asyncio.Queue`를 사용한 메모리 내 작업 큐를 초기 단계로 도입하고, 대기 상태를 세션 모델의 `status` 필드로 관리합니다.

### 근거 (Rationale)
- 다중 사용자의 동시 요청 시 로컬 Ollama 서버의 부하를 순차적으로 제어할 수 있습니다.
- 별도의 Redis 없이도 `asyncio` 루프 내에서 간단하게 구현 가능하여 실용적입니다.

---

## 5. 지수 백오프 및 Fallback 전략

### 결정 (Decision)
`langchain.adapters.openai` 또는 `tenacity` 라이브러리를 사용하여 LLM API 호출에 대해 지수 백오프 재시도 로직을 적용합니다.

### 근거 (Rationale)
- 헌법 V조(신뢰성) 준수 및 일시적인 네트워크/서버 장애 상황에서도 사용자 세션을 보호합니다.
- 최종 실패 시에는 현재까지 분석된 데이터를 기반으로 '제한적 진단 결과'를 생성하여 제공합니다.

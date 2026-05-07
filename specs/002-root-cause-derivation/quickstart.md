# 퀵스타트 (Quickstart): root-cause-derivation

## 1. 개요
이 기능은 사용자의 답변을 분석하여 근본 원인을 도출하고, 질의 횟수를 5회로 제어하며 필요시 연장하는 로직을 포함합니다.

## 2. 테스트 환경 설정
1. 가상 환경 활성화: `uv venv` & `.venv/Scripts/activate`
2. 의존성 확인: `uv sync`
3. 환경 변수 설정: `.env` 파일에 `OPENAI_API_KEY` 또는 `GOOGLE_API_KEY` 설정 확인

## 3. 로직 테스트 (Mock 대화)
핵심 로직을 테스트하기 위한 시나리오입니다.

### 시나리오 A: 5회 이내 원인 도출 및 상세화 시도
1. `InquirySession` 생성 (max_turns=5)
2. 3회의 유의미한 답변 입력
3. `Analyzer` 노드에서 `root_cause_found: true`, `can_detail: true` 반환 확인
4. 시스템이 즉시 상세 분석 질의를 생성하는지 확인

### 시나리오 B: 5회 도달 시 연장 승인 프로세스
1. 5회의 답변 입력 시까지 원인 미도출 상황 연출
2. 상태가 `AWAITING_EXTENSION_APPROVAL`로 전이되는지 확인
3. 사용자 "Yes" 입력 시 `turn_count` 유지 및 질의 계속 진행 확인

## 4. 관련 명령어
- 테스트 실행: `pytest src/apps/inquiry/tests/test_root_cause_logic.py` (구현 후)
- 서버 실행: `python src/manage.py runserver`

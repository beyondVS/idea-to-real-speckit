# 연구 결과 (Research): root-cause-derivation

**기능**: 근본 원인 도출 및 질의 제어 로직
**작성일**: 2026-05-07

## 1. 근본 원인 분석 패턴 (Root Cause Analysis Pattern)

**결정(Decision)**: LangGraph의 전용 `analyzer` 노드를 생성하여, 대화 이력을 바탕으로 `RootCause` 엔티티를 생성하도록 구성함.

**근거(Rationale)**: 헌법 IV(Stateful Agent Architecture)에 따라 대화 흐름을 상태 머신으로 관리해야 하므로, 분석 로직을 독립된 노드로 분리하여 응집도를 높임. LLM 프롬프트에는 '5-Why' 기법이나 'Fishbone' 분석 프레임워크를 참고하도록 지시하여 분석의 논리적 깊이를 확보함.

**고려된 대안(Alternatives considered)**: 대화 생성 노드 내에서 인라인으로 분석 수행 (상태 관리가 복잡해지고 책임 분리가 어려워 기각).

## 2. 확신도 라벨링 정책 (Confidence Labeling Policy)

**결정(Decision)**: LLM이 0.0 ~ 1.0 사이의 float 값을 반환하도록 하고, 시스템에서 다음과 같이 매핑함:
- 0.85 이상: **매우 높음**
- 0.60 이상 0.85 미만: **보통**
- 0.60 미만: **낮음**

**근거(Rationale)**: 명확화 세션에서 확정된 '텍스트 라벨 노출' 요구사항을 충족하기 위해 수치적 확신도를 내부적으로 관리하고 사용자에게는 직관적인 용어로 변환하여 제공함.

**고려된 대안(Alternatives considered)**: LLM이 직접 텍스트 라벨을 생성하도록 함 (모델별로 용어가 일관되지 않을 수 있어 수치 기반 매핑을 채택).

## 3. 질의 제어 및 연장 워크플로우 (Inquiry Control & Extension Workflow)

**결정(Decision)**: LangGraph의 `State`에 `turn_count`를 추가하고, 5회 도달 시 `should_continue` 에지에서 사용자 승인 상태(`AWAITING_APPROVAL`)로 전이하도록 설계함.

**근거(Rationale)**: 사용자 스토리 2의 '5회 제한 및 승인 후 연장' 로직을 상태 머신의 천이 조건으로 명확하게 표현 가능함. 무제한 연장 요구사항에 따라, 승인된 경우 `turn_count`를 유지하거나 확장하여 루프를 지속함.

**고려된 대안(Alternatives considered)**: 뷰(View) 레벨에서 횟수 제한 체크 (상태 머신의 일관성을 위해 코어 로직에서 처리하는 것이 타당함).

## 4. 상세화 가능성 판단 로직 (Detailing Potential Judgment)

**결정(Decision)**: 분석 노드에서 `can_detail` 플래그와 `detailing_guide`를 함께 생성하도록 함. 상세화 가능 여부는 원인의 구체성(추상적/구체적)과 하위 레벨로의 분해 가능성을 기준으로 LLM이 판단함.

**근거(Rationale)**: 명확화 세션에서 '상세화 가능 시 즉시 시도'하기로 결정함에 따라, 분석 결과에 이 정보가 포함되어야 다음 노드(상세화 질의 생성)로 즉시 전이할 수 있음.

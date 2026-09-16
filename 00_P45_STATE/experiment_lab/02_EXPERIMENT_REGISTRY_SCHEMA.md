# P45 EXPERIMENT Registry Schema

## 1. 필수 필드

|필드|형식|필수|고정 시점|의미|
|---|---|---:|---|---|
|experiment_id|string|예|REGISTERED|불변 고유 ID|
|supersedes_experiment_id|string/null|예|REGISTERED|대체한 이전 실험|
|research_domain|enum|예|REGISTERED|DRAW/CROWD/PRIZE_SHARE/DRAW_CROWD_CROSS_TEST|
|lab_name|enum|예|REGISTERED|독립 LAB|
|research_name|string|예|REGISTERED|연구명|
|research_purpose|string|예|DESIGNED|추첨효과·선택행동·상금분할 중 명확한 목적|
|hypothesis|string|예|DESIGNED|검증 가설|
|counter_hypothesis|string|예|DESIGNED|반대가설|
|data_range|object|예|READY_FOR_TEST|시작·종료·제외구간|
|input_data|array|예|READY_FOR_TEST|경로·필드·snapshot hash|
|calculation_method|string/object|예|READY_FOR_TEST|결과 전 고정 계산법|
|result_metrics|array|예|READY_FOR_TEST|PRIMARY/SUPPORT 분리|
|success_criteria|array|예|READY_FOR_TEST|사전 성공 기준|
|failure_criteria|array|예|READY_FOR_TEST|실패·중단 기준|
|minimum_sample|integer/object|예|READY_FOR_TEST|최소 표본|
|validation_windows|object|예|READY_FOR_TEST|전체/최근100/50/20 등의 역할|
|future_data_block|string/object|예|READY_FOR_TEST|R에서 1..R-1 강제|
|walkforward_required|boolean|예|DESIGNED|walkforward 여부|
|random_null_required|boolean|예|DESIGNED|random/null 비교 여부|
|multiple_testing_risk|enum+text|예|DESIGNED|LOW/MEDIUM/HIGH와 통제법|
|overfitting_risk|enum+text|예|DESIGNED|LOW/MEDIUM/HIGH와 통제법|
|protocol_version|string|예|READY_FOR_TEST|사전등록 버전|
|canonical_protocol_hash|string/null|예|READY_FOR_TEST|SHA-256 잠금|
|locked_at|string/null|예|READY_FOR_TEST|결과 전 잠금 시각|
|research_result|object/null|예|실행 후|성공·실패 포함 결과|
|failure_reason|array|예|실행 후|실패·중단 원인|
|reproducibility_status|enum|예|실행 후|NOT_TESTED/REPRODUCED/NOT_REPRODUCED|
|status|enum|예|항상|공식 상태 vocabulary|
|promotion_eligible|boolean|예|검토 후|PROMOTION_CANDIDATE에서만 true 가능|
|official_effect|string|예|항상|항상 NONE, 별도 공식 승인 전 변경 불가|
|official_isolation_verified|boolean|예|항상|공식 엔진 격리 확인|
|created_at|string|예|REGISTERED|생성 시각|
|updated_at|string|예|변경 시|마지막 상태변경 시각|
|record_hash|string|예|변경 시|레코드 hash|

요청된 25개 설계요소는 모두 위 필드에 포함된다.

## 2. Enum

### status

`IDEA`, `REGISTERED`, `DESIGNED`, `READY_FOR_TEST`, `TESTING`, `BACKTESTED`, `WALKFORWARD_TESTED`, `SUPPORTED`, `INCONCLUSIVE`, `FAILED`, `RETIRED`, `PROMOTION_CANDIDATE`

### research_domain

`DRAW`, `CROWD`, `PRIZE_SHARE`, `DRAW_CROWD_CROSS_TEST`

### reproducibility_status

`NOT_TESTED`, `REPRODUCED`, `NOT_REPRODUCED`, `REPRODUCTION_INCOMPLETE`

## 3. 불변 제약

- `promotion_eligible=true`는 status가 `PROMOTION_CANDIDATE`일 때만 허용한다.
- `official_effect`는 별도 공식 승인 전 항상 `NONE`이다.
- READY_FOR_TEST 이후 protocol 의미 변경을 같은 ID에서 금지한다.
- 결과가 있는 레코드를 삭제하지 않는다.
- CROWD/PRIZE_SHARE 결과에는 DRAW gate 또는 공식 pick 영향 필드를 허용하지 않는다.
- CROSS 연구는 DRAW 결과와 CROWD/PRIZE_SHARE 결과를 별도 하위 객체로 저장한다.

## 4. 기계 판독 Schema

동일 구조의 초안 JSON Schema는 `EXPERIMENT_REGISTRY.schema.json`에 저장한다. 이 schema는 계산기를 실행하지 않고 Registry 형식만 검증한다.


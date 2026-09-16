# P45 연구 Coverage Audit 002

## 결론

- formal registry rows: `68`
- DRAW-domain snapshot rows: `53`
- broader formal Registry records: `68`
- 53/68 reconciliation status: `COUNT_DISCREPANCY_FULLY_RECONCILED`
- difference: `15 = CROWD 9 + PRIZE 6`
- executed research without evidence: `0`
- unexecuted idea without local result evidence: `1` (`REHEARSAL`; 결과가 없어야 정상인 사용자 패스 아이디어)
- unmapped result files: `0` at research-family level
- unsupported executed master entries: `0`

## 53의 정확한 의미

`P45_FORMAL_EXP_REGISTRY_SNAPSHOT_001.csv`는 53행 모두 `EXP-DRAW-*`다. 따라서 이는 전체 formal Registry가 아니라 DRAW 도메인 snapshot이다. snapshot 파일의 행 자체는 정확하며 Registry를 수정할 이유가 없다.

## 68의 정확한 의미

Authoritative Registry `00_P45_STATE/experiment_lab/06_INITIAL_EXPERIMENT_REGISTRY.md`를 canonical ID 규칙으로 파싱하면 physical/version rows는 68이다.

- DRAW 53
- CROWD 9
- PRIZE 6
- V1 65
- V2 3

Registry line 376의 EXP-020 append note가 현재 canonical count 68을 명시한다. 2026-08-23 count audit의 58은 당시 point-in-time 값이며 후속 append로 증가했다.

## 차이 15건

DRAW snapshot에서 제외된 15개는 실제 canonical non-DRAW rows다.

- CROWD 9: `EXP-CROWD-20260816-001..004-V1`, `EXP-CROWD-20260823-005..008-V1`, `EXP-CROWD-20260824-009-V1`
- PRIZE 6: `EXP-PRIZE-20260816-001-V1/V2`, `EXP-PRIZE-20260821-004/005-V1`, `EXP-PRIZE-20260816-002/003-V1`

중복/obsolete/retired/planned-only 15건을 임의로 더한 것이 아니다.

## 실행 및 비실행 분리

- actual executed/completed formal rows: `27`
- registered/designed/waiting/blocked formal rows: `41`
- protocol/execution blocked: `2` (PRIZE source semantics 1, EXP-018 V1 bootstrap ambiguity 1)
- closed-axis rows: `1` (EXP-018 V2)
- non-EXP executed research axes: `27`
- official internal studies: `12`
- unexecuted reviewed ideas: `2`
- latest numbered EXP: `EXP-020`

실행 완료 27에는 결과 상태가 있는 formal rows와 공식 repair change-control 1행이 포함된다. REGISTERED 36, DESIGNED 1, READY_FOR_TEST 1, source-semantics blocked 1, prospective waiting 2는 실행 완료에 포함하지 않는다.

## REHEARSAL 및 DRAW-ORDER

- REHEARSAL: `USER_DECISION / CONVERSATION_ORIGIN_IDEA / NO_RESULT_EXPECTED`; EXP-021 아님, 미실행, 패스.
- DRAW-ORDER: `REVIEWED_IDEA / LOCAL_FEASIBILITY_EVIDENCE`; 정식 EXP와 효과 검증은 미실행.
- unsupported executed research: `0`.
- unexecuted idea without result evidence: `1`인 REHEARSAL은 오류나 누락 결과가 아니다.

## Counting policy

1. formal Registry count는 canonical physical/version row `68`을 쓴다.
2. `53`은 DRAW-domain row count로만 표기한다.
3. 마지막 EXP 번호, physical/version rows, 실행 완료 rows, non-EXP axes를 서로 대체하지 않는다.
4. Registry 원문과 결과는 변경하지 않고 point-in-time count 기록을 보존한다.


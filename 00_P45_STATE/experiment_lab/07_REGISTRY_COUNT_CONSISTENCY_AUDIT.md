# P45 REGISTRY COUNT CONSISTENCY AUDIT

- audit date: `2026-08-23`
- status: `REGISTRY_STATE_COUNT_MISMATCH_CONFIRMED`
- scope: Experiment Registry 원문, CURRENT_STATE, 최근 experiment-count 변경 Decision/state-history만 사용
- official engine: `FROZEN`

## Baseline

- state version: `1.0.75`
- latest decision: `DECISION-20260823-082`
- `EXP-CROWD-TOPO-001 V1`: `FAILED`
- `DRAW_DISCOVERY_PAUSE`: `ACTIVE`
- prospective protocol: unchanged
- state check: `STATE_HANDOFF_VERIFIED`

## 관측값의 원문 범위

|값|원문|정확한 문맥과 범위|현재성|
|---:|---|---|---|
|55|`06_INITIAL_EXPERIMENT_REGISTRY.md` 상단의 `현재 총 55건` 및 `experiment_lab.registered_experiments`|2026-08-21 `DECISION-20260821-076`까지 정식 ID physical/version row 수. 실패·차단·지지·V2 포함.|이후 3행 추가로 stale|
|44|동 문서 `역사 아이디어 복구 종료 기록`의 `Registry 총수: 44 유지`|`DECISION-20260816-066` 당시의 point-in-time Registry 행 수. 복구 아이디어를 새 Experiment로 추가하지 않았다는 역사 기록.|역사 기록으로 valid, 현재 총계 아님|
|48|state-history `DECISION-20260821-079`~`081`의 `research_memory_policy.experiment_registry_total`|역사 복구 종료 카운터 46에 이후 PRIZE 연구 2건만 증분한 값. EXP-004~016 정산의 신규 8행이 같은 카운터에 반영되지 않음.|현재 총계로 stale|
|49|CURRENT_STATE `research_memory_policy.experiment_registry_total`|위 stale 48에 `EXP-CROWD-TOPO-001 V1` 1건을 더한 값.|동일 scope 실제 행 58과 불일치|

## 독립 파싱 결과

- canonical row rule: 행 첫 필드가 `EXP-(DRAW|CROWD|PRIZE|CROSS)-YYYYMMDD-NNN-Vn`인 경우만 집계
- total physical rows: `58`
- unique experiment IDs: `58`
- unique logical experiment families: `56`
- version rows: `V1 56`, `V2 2`
- domain: `DRAW 47`, `CROWD 5`, `PRIZE_SHARE 6`
- status:
  - `REGISTERED 36`
  - `DESIGNED 1`
  - `FAILED 9`
  - `FAILED_EARLY 8`
  - `PROTOCOL_BLOCKED_SOURCE_SEMANTICS 1`
  - `PROSPECTIVE_LOCKED_WAITING_FOR_DATA 1`
  - `SUPPORTED_WITHIN_EXPERIMENT 1`
  - `SUPPORTED_CROSS_OUTCOME 1`
- blocked/failed/supported rows: 모두 포함
- logical family 중 version row 중복: `EXP-DRAW-20260816-038` V1/V2, `EXP-PRIZE-20260816-001` V1/V2
- canonical registry DB: `없음`. 개별 실험 DB는 일부 namespace의 결과 저장소이며 전체 Registry count source가 아니므로 DB row 수와 직접 비교하지 않음.

## Root cause와 정정

두 개의 current-state 카운터가 서로 다른 시점에 수동 증분되면서 동기화가 끊겼다.

1. `registered_experiments`는 55에서 이후 정식 Registry 3행을 반영하지 않았다.
2. `experiment_registry_total`은 EXP-004~016 정산에서 새로 추가된 8행을 반영하지 않은 46을 바탕으로 PRIZE 2건과 CROWD 1건만 증분하여 49가 되었다.
3. Registry의 정식 ID 행이 canonical evidence이므로 두 current counter를 physical/version row 정의 `58`로 정합화한다.
4. 역사적 `44`와 `55` 원문은 삭제하지 않고 시점과 범위를 명시하는 append-only note를 추가한다.

## 보호 확인

- EXP-CROWD-TOPO-001 locked/result/failure: 변경 없음
- official engine: `FROZEN` 유지
- DRAW discovery pause: `ACTIVE` 유지
- prospective protocol/ledger: 변경 없음
- 새 Experiment: 생성 없음
- Registry row 삭제: 없음
- pre-audit backup: `v27_storage/backups/registry_count_audit_20260823_010/06_INITIAL_EXPERIMENT_REGISTRY.pre_audit.md`
- backup SHA-256: `d9d37688a5cf4777434a2ddb84c854391d5bed7352e0f23aae467c8cad5a8375`

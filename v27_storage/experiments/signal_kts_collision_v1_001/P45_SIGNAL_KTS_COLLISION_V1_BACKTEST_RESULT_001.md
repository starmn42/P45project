# P45 SIGNAL KTS COLLISION V1 BACKTEST RESULT 001

## FINAL_JUDGMENT

`FAILED_NOT_SUPPORTED`

## Locked inputs and preflight

- Protocol SHA-256: `8d3a7d1a3ae80083aad2ce132c228dd4901b1a406c2983c2b3bb30801d9d5a98`
- KTS source / SHA: `E:\P45 프로젝트\v27_storage\experiments\trio_orbit_v1_001\P45_TRIO_ORBIT_V1_KTS45_SCHEDULE_001.csv` / `5f212342c6c27fca8eafbc75d20a55fc4be4ca2961a9c70c3a7af0eca26f1075` (`PASS`)
- Canonical source / SHA: `E:\P45 프로젝트\v27_storage\audits\current_1239_predraw_rerun_001\STAGING_CONTIGUOUS_DRAW_1_1238.csv` / `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Data range / evaluated targets: `1..1238 / 2..1238 = 1237`
- Data checks: `{"continuous": true, "duplicate_rounds_0": true, "main_range_unique": true, "bonus_valid": true}`
- HISTORICAL_ONE_STEP_WALKFORWARD: `YES`
- FUTURE_LEAKAGE: `0`

## Exhaustive structural audit

- Status: `PASS`
- Enumerated: `8145060`
- Candidate count min/max / vote max: `0/6/3`
- count>6 / vote>3: `0/0`

|candidate_count|all-source-set count|rate|
|---:|---:|---:|
|0|2323710|28.529071609049%|
|1|3791340|46.547723405352%|
|2|1572840|19.310354988177%|
|3|390300|4.791861570081%|
|4|58320|0.716016824922%|
|5|7200|0.088397138879%|
|6|1350|0.016574463540%|

## Historical output availability

|candidate_count|rounds|rate|
|---:|---:|---:|
|0|337|27.243330638642%|
|1|584|47.210994341148%|
|2|248|20.048504446241%|
|3|55|4.446240905416%|
|4|12|0.970088924818%|
|5|1|0.080840743735%|
|6|0|0.000000000000%|

- Nonzero output: `900/1237 = 72.756669361358%`
- Average candidate count: `1.049312853678`
- Total candidate exposures: `1298`

## SIGNAL_VALIDITY_PRIMARY

- Observed hits / rate: `160/1298 = 12.326656394453%`
- Simple 6/45 reference: `13.333333333333%`
- Carryover-matched exact-null expected hits / rate: `172.705128205130 / 13.305479830904%`
- Exact one-sided p `P(H_null >= H_observed)`: `0.863655309594332`
- This is the single confirmatory test.

## P45 TRIO support (descriptive only)

- Research A exact3 / exact2 rounds: `0 / 5`
- Research B exact3 / exact2 rounds: `0 / 0`
- A or B at least one exact3: `0`
- Leftover individual exposures / hits: `14 / 3`
- These metrics do not alter SIGNAL_VALIDITY_PRIMARY.

## Protection boundary

- OFFICIAL ENGINE / EXP-017 / DRAW_DISCOVERY_PAUSE: `FROZEN / NOT_CREATED / ACTIVE`
- Official code/DB/gate/threshold/signature/semantics/State/Decision/Registry changes: `0`
- V1 threshold and rules were not changed after observing results.

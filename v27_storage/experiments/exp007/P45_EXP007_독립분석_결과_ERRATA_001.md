# EXP-007 RESULT ERRATA

- 발견일/정정일: `2026-08-21`
- ORIGINAL_RESULT: `P45_EXP007_독립분석_결과_001.md`
- ORIGINAL_PROTOCOL_SHA256: `09f4edeb35112c0d3429ee2b2685e3544bf43349c579cecdefb3d043e6c5e80c`
- DATA_RANGE: `1~1237`
- DATA_CANONICAL_SHA256: `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`

## Corrected field

- ERROR_FIELD: `WALKFORWARD.SIGNAL_EXPOSED_ROUNDS`
- ORIGINAL_REPORTED_VALUE: `1013`
- LOCKED_RULE_REPRODUCED_VALUE: `0`
- CORRECT_WALKFORWARD_STATUS: `NO_SIGNAL_EXPOSURE`
- CORRECT_SIGNAL_EXPOSED_ROUNDS: `0`
- CORRECT_WALKFORWARD_DIRECTIONAL_P: `NONE`

## Root cause

기존 계산/결과 문서에서 minimum-training 이후 평가 가능 회차 수를
training analytical `p<=0.05` gate를 통과한 signal exposure 수로 잘못
기록했다. 평가 가능 회차는 1,013회였지만 잠금 관문 통과 회차는 0회다.

## Unchanged research result

- LOCKED_PROTOCOL_CHANGED: `NO`
- DATA_CHANGED: `NO`
- THRESHOLD_CHANGED: `NO`
- POSTHOC_RETUNE: `NO`
- PRIMARY_ANALYTICAL_P: `0.602916381`
- PRIMARY_BOOTSTRAP_P: `0.600963990`
- ORIGINAL_FINAL: `FAILED`
- CORRECTED_FINAL: `FAILED`
- FINAL_JUDGMENT_CHANGED: `NO`
- RECOMMENDATION_CONNECTION_ALLOWED: `NO`
- OFFICIAL_ENGINE_CHANGED: `NO`

## Audit linkage

- mismatch report: `v27_storage/experiments/batch_exp004_016/REPRODUCTION_MISMATCH_EXP007.md`
- original raw log: `v27_storage/experiments/batch_exp004_016/reproduction_raw.json`
- corrected reproduction log: `v27_storage/experiments/batch_exp004_016/reproduction_errata_004.json`
- adjudication: `v27_storage/experiments/batch_exp004_016/adjudication_errata_004.json`
- original calculator SHA-256: `508971e38d76e19d938ac10b1214d644d25f3c6b8dd426a791b9e84c1f896769`
- correction calculator: `src/p45_experiments/batch_settlement_exp004_016_errata.py`
- correction calculator SHA-256: `04ec09949104644ca4b7efb0603c3448042d6a1561b49117f1c3f3535e8198e2`
- ERRATA SHA-256: recorded in `P45_EXP007_독립분석_결과_ERRATA_001.md.sha256` and settlement DB

The original result is preserved unchanged as historical evidence. This
ERRATA is additive and does not overwrite, rename, or delete it.

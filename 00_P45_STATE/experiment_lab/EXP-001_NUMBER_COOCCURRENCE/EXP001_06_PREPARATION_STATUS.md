# EXP-001 백테스트 준비 상태

- experiment_id: `EXP-DRAW-20260816-002-V1`
- short_id: `EXP-001`
- status: `READY_FOR_TEST`
- official_effect: `NONE`
- official_engine: `FROZEN`
- actual_backtest_run: `false`
- actual_pair_results_viewed: `false`
- recommendation_numbers_created: `false`

## Data snapshot lock

- range: `1~1237`
- rows: `1237`
- MAIN width: `6`
- INTEGRATED width: `7`
- duplicate rounds: `0`
- missing rounds: `0`
- snapshot: `v27_storage/experiments/exp001/data/exp001_draws_1_1237.csv`
- snapshot SHA-256: `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`

## Protocol lock

- version: `EXP001-PROTOCOL-1.0`
- files locked: `5`
- canonical protocol SHA-256: `2d4e723b87bc2f44a7a0d763ee4779ded40b007f3cbf4b093b9e771c9248dd9d`
- lock manifest: `EXP001_PROTOCOL_LOCK.json`
- mutation policy: 결과 확인 후 수정 금지; 변경 필요 시 새 experiment version 또는 ID 발급

## Calculator and storage

- calculator version: `EXP001-CALCULATOR-1.0`
- code hash: `8f59c96589f400c0fa625b053e0e7947a31b1e52755206475fce74bcfafb97e8`
- package: `src/p45_experiments/exp001`
- storage: `v27_storage/experiments/exp001/exp001_research.sqlite3`
- schema version: `1001`
- pair result rows: `0`
- integrity/FK: `ok / 0`

## Preflight

- focused unit tests: `16/16 PASS`
- formal preflight checks: `17/17 PASS`
- report: `v27_storage/experiments/exp001/exp001_preflight_report.json`
- failed checks: `0`

`READY_FOR_TEST`는 실행 준비 완료만 뜻한다. `BACKTESTED`, `WALKFORWARD_TESTED`, `SUPPORTED`, `PROMOTION_CANDIDATE`가 아니다.


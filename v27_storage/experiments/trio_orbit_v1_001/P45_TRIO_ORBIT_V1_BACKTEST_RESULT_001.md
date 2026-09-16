# P45 TRIO ORBIT V1 BACKTEST RESULT 001

## Final judgment

`FAILED_NOT_SUPPORTED`

## Preflight

- Canonical source: `E:\P45 프로젝트\v27_storage\audits\current_1239_predraw_rerun_001\STAGING_CONTIGUOUS_DRAW_1_1238.csv`
- Canonical SHA-256: `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Data range / evaluated targets: `1..1238 / 2..1238 (1237)`
- Data checks: `{"continuity": true, "duplicate_rounds_0": true, "main_errors_0": true, "bonus_range_errors_0": true, "bonus_main_overlap_0": true}`
- KTS schedule SHA-256: `5f212342c6c27fca8eafbc75d20a55fc4be4ca2961a9c70c3a7af0eca26f1075`
- Expected SHA match: `PASS`
- KTS invariants: `{"parallel_classes_22": true, "each_class_15": true, "each_class_partitions_1_45": true, "total_trios_330": true, "unique_trios_330": true, "unordered_pairs_990": true, "each_pair_once": true, "each_number_22": true, "no_within_trio_duplicate": true, "number_range_1_45": true, "latin_cells_valid": true}`
- Future leakage: `0`

## Primary exact 3/3

- Fixed: `5/1237 = 0.404203719%`
- Linked: `7/1237 = 0.565885206%`
- Delta linked-fixed: `2` rounds; `0.161681487%` percentage-point difference; `40.000000%` relative count change
- Paired both / fixed-only / linked-only / neither: `0 / 5 / 7 / 1225`
- McNemar exact two-sided p: `0.7744140625`

## Fair-null Monte Carlo

- Histories / seed: `20000 / 20260826`
- Each history: `1238` fair sequential MAIN6+BONUS draws, `1237` evaluated targets
- Statistic: `linked_primary_count - fixed_primary_count`
- Simulated deltas >= observed: `6387`
- One-sided plus-one p: `0.319384030798`
- Simulation code SHA-256 is recorded in `SHA256SUMS_001.txt`.

## Separate exact 2/3 support

- Fixed exact2 TRIO count / rounds with at least one exact2: `161 / 159`
- Linked exact2 TRIO count / rounds with at least one exact2: `175 / 174`
- This support metric does not alter the primary judgment.

## Linked reset and exposure diagnostics

- Reset count: `21`
- Reset interval mean / median / min / max: `57.76190476190476 / 59 / 43 / 63`
- Mean used TRIO count immediately before reset: `173.14285714285714`
- Number exposure min / max / population std: `227 / 264 / 10.510100962`
- Pair output-frequency distribution: `{"5": 3, "6": 6, "7": 39, "8": 81, "9": 114, "10": 111, "11": 177, "12": 177, "13": 120, "14": 81, "15": 45, "16": 27, "17": 9}`
- TRIO output-frequency distribution: `{"5": 1, "6": 2, "7": 13, "8": 27, "9": 38, "10": 37, "11": 59, "12": 59, "13": 40, "14": 27, "15": 15, "16": 9, "17": 3}`
- Per-reset details are in `P45_TRIO_ORBIT_V1_RESET_TRACE_001.csv`.

## Protection boundary

- OFFICIAL ENGINE / official gate / official DB / recommendation promotion: `UNCHANGED / 0 / 0 / NO`
- State / Decision / Registry / protected manifest changes: `0 / 0 / 0 / 0`
- This is an independent Experiment Lab result and is not evidence that an existing R-1 predictive signal succeeded.

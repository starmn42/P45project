# P45 CURRENT 1239 PREDRAW RERUN RESULT 001

## Final

- FINAL_VERDICT: `CURRENT_1239_RERUN_NO_OUTPUT_TRACED`
- VALID_BASELINE_1_1237: `PASS`
- ROUND_1238_AUTHORITATIVE: `PASS`
- MAX_SOURCE_ROUND / TARGET_ROUND: `1238 / 1239`
- OFFICIAL_OUTPUT: `NO`
- TWO_SET_CONSTRUCTIBLE: `NO`
- FIRST_FATAL_BOTTLENECK: `NUMBER_EXTINCTION`
- Fatal predicate: frozen NUMBER finalization received only `5` eligible source numbers, below required minimum `6`, and published no NUMBER pool.
- FORCED_PICK: `NO`

## Protected-state preflight

- State / Decision / Registry physical rows: `1.0.88 / DECISION-20260824-095 / 63`
- Official PAIR lifecycle repair: `APPLIED_AND_VERIFIED`
- OFFICIAL ENGINE / NO-PICK / DRAW_DISCOVERY_PAUSE / EXP-017: `FROZEN / UNRESOLVED / ACTIVE / NOT_CREATED`
- Preflight result: `PASS`; no protected-state mismatch.

## Authoritative round 1238

- Round/date: `1238 / 2026-08-22`
- MAIN: `2, 13, 18, 32, 38, 42`
- BONUS: `22`
- MAIN six unique/range, BONUS range/non-membership: `PASS`
- Approved source payload SHA-256: `99d44e493a357785f976e37d99b1e0d2ae179b161cc1aa4a5665f9606ec0c119`
- Existing approved raw-capture ledger and prior provenance match: `PASS`
- Conflicts: `0`
- New web or unofficial source use: `0`

## Contiguous staging integrity

- Path: `v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv`
- New staging SHA-256: `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Baseline SHA-256: `ad69ec8d28b4e5cdb40d468ad758c5f23acaeb6225f525c5201c8027952701e6`
- Rows / unique / range / missing / duplicates: `1238 / 1238 / 1..1238 / 0 / 0`
- MAIN/BONUS structural errors: `0`
- First 1,237 rows exact equality with baseline: `PASS`
- First 1,237 canonical-content SHA-256: `a6592ec8d9441b162858bcf26aa3db2c71410a8a4b672daccc9f69124a14e374`
- Baseline canonical-content SHA-256: `a6592ec8d9441b162858bcf26aa3db2c71410a8a4b672daccc9f69124a14e374`
- Round 1238 authoritative equality: `PASS`
- Round 1238 canonical hash: `2d301f8fb550733eafc8b63adf40f1304125e7db75ee44de28ed7c0a178e2c4b`
- Prior artifact disposition: `INVALID_FOR_TARGET_1239_CAUSAL_USE - MISSING_1236_1237`; it was preserved, not deleted or committed to official storage.

## Frozen official engine rerun

### NUMBER

- Input: `45`
- Lifecycle distribution: `NUMBER_HOLD 40 / NUMBER_WEAKEN 5`
- Eligible before minimum-pool gate: `5` — identities `13, 18, 20, 24, 27`
- Selected/output count: `0`; selected identities: `none`
- Structure distribution: `SEVERE 45`
- PRIMARY integrated evidence distribution: `NEGATIVE_TENTATIVE 12 / POSITIVE_TENTATIVE 28 / POSITIVE_CONFIRMED 5`
- SUPPORT at NUMBER level: `NOT_APPLICABLE`
- First fatal NUMBER predicate: `eligible count 5 < required 6`

### Structure ledger

| Structure | State | Overall percentile |
|---|---|---:|
| UNIT_3 | NORMAL | 69.11883589329022 |
| UNIT_5 | NORMAL | 57.47776879547292 |
| UNIT_9 | NORMAL | 62.4090541632983 |
| UNIT_10 | NORMAL | 65.40016168148748 |
| END_DIGIT | SEVERE | 100.0 |

- END_DIGIT decisive metrics: `zero_group_count 100.0`, `realized_return_depth 100.0`, and `max_abs_standardized_occupancy 99.91915925626516` independently meet the canonical SEVERE boundary.

### Downstream stages

- TRIO: `NOT_ENTERED`; universe/statuses/eligible: `0 / none / 0`
- TRIO member_structure_summary/final_structure_state: `not materialized`
- PAIR universe/statuses/eligible: `0 / none / 0`
- PRIMARY 3/3 survivors: `0`
- SUPPORT exact 2/3 survivors: `0`
- Final 3-number candidate-set count: `0`
- TWO_SET_CONSTRUCTIBLE / OFFICIAL_OUTPUT: `NO / NO`

PRIMARY and SUPPORT were counted separately and were not mixed.

## Comparison with invalid target-1239 result

- SAME_AS_INVALID_1239_RESULT: `YES` for the categorical official result and first fatal stage.
- INVALID_RESULT_FIELDS_RECONFIRMED: `NUMBER_HOLD 40`, `NUMBER_WEAKEN 5`, eligible `5`, selected `0`, NUMBER structure `SEVERE 45`, UNIT_5 `NORMAL`, END_DIGIT `SEVERE / 100.0`, TRIO `NOT_ENTERED`, PAIR eligible `0`, PRIMARY/SUPPORT survivors `0/0`, `TWO_SET_CONSTRUCTIBLE NO`, `OFFICIAL_OUTPUT NO`, `NUMBER_EXTINCTION`, and deterministic latent all-member-SEVERE premise if a NUMBER pool existed.
- INVALID_RESULT_FIELDS_REVERSED: the old staging integrity/through-1238 claim and its SHA are rejected; UNIT_5 percentile changes `56.8421052631579 → 57.47776879547292`; END_DIGIT component percentiles change, including max standardized occupancy `99.91902834008097 → 99.91915925626516`, max annihilation streak `78.78542510121457 → 58.124494745351655`, and recent50 shift `20.647773279352226 → 34.76151980598222`. No categorical lifecycle or final-output field was reversed.

The prior result is not retroactively treated as valid; the matching categorical findings above are newly established by this validated rerun.

## Integrity and change control

- Future leakage / target-1239 outcome access / scoring: `0 / 0 / 0`
- Historical lifecycle updates used in normal prior-round context: `22`; historical outcome scoring in this Work: `0`
- Official source / DB changes: `0 / 0`
- State / Decision / Registry changes: `0 / 0 / 0`
- Gate / threshold / signature changes: `0 / 0 / 0`
- NUMBER/TRIO/PAIR/CORE semantics changes: `0`
- EXP-017 creation / pause release / hidden score / arbitrary weight: `0 / 0 / 0 / 0`
- PROJECT_SOURCES_ACTION_REQUIRED: `YES`

## NEXT_ACTION

`READ_ONLY_CURRENT_1239_NUMBER_EXTINCTION_CAUSAL_DECOMPOSITION_001`

Trace only the newly validated five eligible NUMBER identities and the canonical HOLD reasons under the unchanged frozen semantics; do not manufacture a sixth number or relax any gate.

`CURRENT_1239_RERUN_NO_OUTPUT_TRACED`

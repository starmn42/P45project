# P45 OPPOSITE-PERIOD STABILITY FILTER VALIDATION RESULT 001

## Final

- FINAL_VERDICT: `OPPOSITE_PERIOD_STABILITY_FILTER_VALIDATION_COMPLETE`
- PRIMARY_VERDICT: `INCONCLUSIVE`
- PROTOCOL_LOCKED: `YES`
- PROTOCOL_SHA256: `03bb3ba7c472955b0f7825dc9ed348a865f7b3d42dfc19611bdd5a705a09ff4b`
- RESULT_JSON_SHA256: `ffc166ae4257c8e53bf3a2240d8f4c7301fb659940496304a54f95e731c377c1`
- EVIDENCE_CSV_SHA256: `8136dad4557757b759193e2376b8ed041849f98d27dc4468095aa5ee8be14279`

The locked primary test does not show that blocked-only candidates are significantly below or above random MAIN6 probability. Their observed rate is slightly below `6/45`, but the round-cluster 95% CI for the difference includes zero. The minimum sample condition passes, so the correct verdict is `INCONCLUSIVE`, not a minimum-sample fallback. There is no evidence basis here for changing the frozen official filter.

## Protocol and walk-forward integrity

- FIRST_VALID_TARGET / LAST_TARGET: `3 / 1238`
- Historical targets processed: `1236`
- FIRST_VALID_TARGET was determined from canonical prerequisite availability without outcome scoring before the protocol lock.
- Each target `t` used features from source `<=t-1`; MAIN6 was accessed only after official, fixed-variant, and blocked-only sets were frozen.
- Bonus excluded from primary outcome: `YES`
- Target 1239 scoring / future-source access: `0 / 0`
- Input: validated contiguous `1..1238`, SHA-256 `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Protocol hash after execution equals locked hash: `PASS`

## Primary result

- Activated target rounds: `1026`
- Blocked-only observations: `7117`
- Minimum sample requirements: rounds `>=100` and observations `>=300` — `PASS`
- Blocked-only MAIN hits: `916`
- BLOCKED_ONLY_MAIN_HIT_RATE: `0.12870591541379794`
- RANDOM_BASELINE: `6/45 = 0.13333333333333333`
- DELTA_RANDOM: `-0.004627417919535387`
- Round-cluster bootstrap: `10,000` replicates, seed `20260825`
- 95% CI for DELTA_RANDOM: `[-0.011270296084049669, 0.0018200657746542392]`
- CI upper is not below zero; CI lower is not above zero. Therefore neither `SAFEGUARD_SUPPORTED` nor `FILTER_HARM_SIGNAL` is met.

## Survivor-count distributions

All counts cover the same `1236` historical targets.

| Eligible survivors | Official | Fixed variant |
|---|---:|---:|
| 0 | 51 | 40 |
| 1 | 34 | 0 |
| 2 | 25 | 0 |
| 3 | 10 | 0 |
| 4 | 18 | 1 |
| 5 | 7 | 0 |
| >=6 | 1091 | 1195 |

- Official average eligible count: `22.330906148867314`
- Fixed-variant average eligible count: `36.65857605177994`
- Official eligible observations/hits/rate: `27601 / 3698 / 0.13398065287489583`
- Blocked-only observations/hits/rate: `7117 / 916 / 0.12870591541379794`
- Fixed-variant eligible observations/hits/rate: `45310 / 6057 / 0.13367909953652615`
- Blocked-only average candidates per activated round: `6.936647173489279`
- Official average MAIN hits captured per target: `2.9919093851132685`
- Fixed-variant average MAIN hits captured per target: `4.900485436893204`

These are descriptive secondary results only. The larger fixed-variant pool naturally captures more total MAIN hits and is not evidence of superior candidate quality. None of these fields changes the primary verdict.

## Multiple testing policy

- Primary hypothesis / pattern / metric: `1 / 1 / 1`
- Threshold search / lookback search / subgroup rescue / parameter tuning: `0 / 0 / 0 / 0`
- Good-result cherry-picking or secondary rescue: `0`
- MULTIPLE_TESTING_POLICY: `PASS`

## PARTIAL_SURVIVOR_REPORTING latest policy

- ID: `PARTIAL_SURVIVOR_REPORTING`
- Status: `REPORTING_POLICY_DIRECTION_CONFIRMED`
- REPORTING_MINIMUM: `NONE`
- Report the actual eligible survivor count `0..N`, including zero, without a separate minimum reporting gate.
- Exactly three may later be considered for a natural `PARTIAL_TRIO` display without a selection problem.
- For four or five, do not arbitrarily select three or manufacture a set.
- For six or more, the survivor pool itself may still be displayed.
- Survivor reporting remains completely separate from the frozen official 3×2 contract.
- Forced picks, hidden scores, arbitrary weighting, and arbitrary overlapping groups remain forbidden.
- This policy direction record is not an official engine change.

## Protected state and interpretation

- State / Decision / Registry: `1.0.88 / DECISION-20260824-095 / 63`
- OFFICIAL ENGINE / NO-PICK / DRAW_DISCOVERY_PAUSE / EXP-017: `FROZEN / UNRESOLVED / ACTIVE / NOT_CREATED`
- Official gate / threshold / signature changes: `0 / 0 / 0`
- Official source / DB changes: `0 / 0`
- State / Decision / Registry changes: `0 / 0 / 0`
- Target 1239 outcome access/scoring: `0 / 0`
- EXP-017 creation / pause release: `0 / 0`
- PROJECT_SOURCES_ACTION_REQUIRED: `YES`

## NEXT_ACTION

`NO_OFFICIAL_FILTER_CHANGE_MAINTAIN_FROZEN_SEMANTICS_001`

Maintain the current official opposite-period semantics because the locked validation is inconclusive; do not relax or promote the filter from these results.

`OPPOSITE_PERIOD_STABILITY_FILTER_VALIDATION_COMPLETE`

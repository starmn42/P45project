# P45 ENDING × CUMULATIVE FREQUENCY INTERACTION V1 — PROTOCOL LOCKED 001

## Status and protection

- Status: `LOCKED_BEFORE_OUTCOME_CALCULATION`
- Work ID: `P45_WORK_ENDING_FREQUENCY_INTERACTION_V1_001`
- Scope: a new independent interaction study. EXP-006 remains `FAILED`; EXP-013 remains `FAILED_EARLY`. Neither source experiment is modified, rerun, rescued, or reinterpreted.
- EXP-017 is not created. No recommendation, signal, threshold, hidden score, arbitrary weight, subgroup, or OFFICIAL connection is permitted.
- Canonical input: `v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv`; its actual SHA-256 and latest round must be verified before analysis.

## Fixed evaluation design

- Targets: `R = 201..canonical latest`; if latest is 1238, exactly `201..1238` (1,038 targets).
- Only MAIN6 is used. For target R, every predictor uses rounds `1..R-1` only. BONUS and all future outcomes are unused.
- Let `D_R` be the distinct end digits (`n mod 10`, including 10/20/30/40 as ending 0) in MAIN(R-1).
- Candidate set: `C_R = {n in 1..45: n mod 10 in D_R and n not in MAIN(R-1)}`. This is the EXP-006 candidate definition.
- Historical frequency: `F_R(n)` is n's cumulative MAIN count in rounds `1..R-1`.
- Within C_R only, rank F_R from low to high using average ranks for ties. Let raw rank be `A_R(n)`. Let `Q_R(n) = A_R(n) - mean_{j in C_R} A_R(j)`. Thus negative means relatively less frequent and positive relatively more frequent within the same-ending candidates.
- No top/bottom count, threshold, ending subgroup, rolling window, decay, weighting, or post-result rule is allowed.

## Primary statistic and descriptive quantities

- `ROUND_SCORE_R = sum_{n in MAIN(R) intersect C_R} Q_R(n)`.
- `TOTAL_SCORE = sum_R ROUND_SCORE_R`; primary direction is fixed two-sided.
- Negative TOTAL_SCORE means relatively less frequent candidates hit more; positive means relatively more frequent candidates hit more.
- Report evaluated rounds, total candidate exposures, total candidate hits, candidate hit rate, difference from EXP-006 fair marginal expectation `6/45`, TOTAL_SCORE, mean centered rank among hit candidates (`TOTAL_SCORE / total hits` when hits > 0), and mean raw within-candidate frequency rank among hits.

## Primary full-sequence fair-draw Monte Carlo

- Simulations: exactly `100,000` independent histories.
- For every simulation, generate the entire MAIN6 sequence through canonical latest as independent uniform 6-subsets of 1..45.
- For every simulated target, regenerate the prior-round ending candidate set, cumulative frequencies from simulated rounds `1..R-1`, average-tied ranks within candidates, and the identical TOTAL_SCORE.
- `PRIMARY_TWO_SIDED_MC_P = (1 + count(|TOTAL_SCORE_sim| >= |TOTAL_SCORE_obs|)) / (100000 + 1)`.
- Deterministic seed: interpret the first 16 hexadecimal characters of this locked protocol's SHA-256 as an unsigned 64-bit integer. Record SHA and seed before any outcome calculation.

## Conditional randomization support

- Run exactly `100,000` repetitions using actual target structures.
- At each target preserve candidate set C_R and actual candidate hit count k_R, but uniformly choose k_R identities without replacement from C_R and sum their fixed Q_R scores.
- Sum across all targets and use the same add-one two-sided p-value against observed absolute TOTAL_SCORE.
- This is supporting evidence; the full-sequence Monte Carlo remains primary.

## Stability and judgment

- Record TOTAL_SCORE and mean round score for full, chronological first half, chronological second half, recent100, recent50, and recent20. Recent windows are descriptive only.
- `STRONG_INTERACTION_CANDIDATE` requires primary p <= 0.05, conditional p <= 0.05, no strong opposite first/second reversal, FUTURE_LEAKAGE=0, and structural validation PASS.
- `INTERESTING_WATCHLIST` requires 0.05 < primary p <= 0.10 and no severe period-direction conflict.
- Otherwise: `FAILED_NOT_INTERESTING`.
- Results may not alter these rules or select a direction/subgroup after observation.

## Required validation and outputs

- Validate contiguous unique rounds, MAIN uniqueness/range, BONUS validity (data integrity only), latest, canonical SHA, target boundaries, ending-0 fixture, exact prior MAIN exclusion, average-tie ranking, centered candidate-score sum zero, deterministic repeatability, and future leakage zero.
- Save the locked protocol, result Markdown, detailed trace CSV if generated, calculation source, structured JSON if generated, and `SHA256SUMS_001.txt` under `v27_storage/experiments/ending_frequency_interaction_v1_001/`.
- Final protection assertions: FUTURE_LEAKAGE=0; EXP-006/013 changes=0; EXP-017 not created; OFFICIAL ENGINE/gate/threshold/signature/DB and NUMBER/TRIO/PAIR/CORE changes=0; hidden score/arbitrary weighting/post-result subgroup=0.

## Lock declaration

This document is the immutable result-blind V1 definition. Its SHA-256 and derived seed must be recorded before outcome calculation. Any later research-definition change requires a new version and cannot alter this V1.

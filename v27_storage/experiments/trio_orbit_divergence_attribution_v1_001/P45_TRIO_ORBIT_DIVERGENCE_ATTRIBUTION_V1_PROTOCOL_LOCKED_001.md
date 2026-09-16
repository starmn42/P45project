# P45 TRIO ORBIT DIVERGENCE ATTRIBUTION V1 — PROTOCOL LOCKED 001

## Status and immutable sources

- Status: `LOCKED_BEFORE_ATTRIBUTION_CALCULATION`
- Work ID: `P45_WORK_TRIO_ORBIT_DIVERGENCE_ATTRIBUTION_V1_001`
- This is descriptive/diagnostic attribution of the already completed TRIO ORBIT V1. It does not regenerate its KTS schedule, fixed orbit, linked orbit, or round selections.
- Sole round-selection source: `v27_storage/experiments/trio_orbit_v1_001/P45_TRIO_ORBIT_V1_ROUND_TRACE_001.csv`.
- Canonical outcome source: `v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv` only for target MAIN6 and anchor reappearance checks.
- Required KTS schedule SHA-256: `5f212342c6c27fca8eafbc75d20a55fc4be4ca2961a9c70c3a7af0eca26f1075`.
- Existing TRIO ORBIT V1 result remains fixed: fixed primary 5/1237, linked primary 7/1237, round-classification fixed-only 5 / linked-only 7, original one-sided fair-null p 0.319384030798, FINAL `FAILED_NOT_SUPPORTED`.

## Evaluation and decomposition

- Evaluate exactly targets `2..1238` (1,237 rounds), matching the source trace.
- Parse each trace row's `fixed_A/B/C`, `linked_A/B/C`, and corresponding hit counts. Each side must contain exactly three distinct normalized TRIOs.
- For each round define COMMON as set intersection, FIXED_ONLY as fixed minus linked, and LINKED_ONLY as linked minus fixed.
- Validate `fixed-only count = linked-only count = 3-common count`; otherwise stop with STRUCTURE ERROR.
- For COMMON, FIXED_ONLY, and LINKED_ONLY separately report TRIO exposures; exact3 count/rate; exact2 count/rate; rounds with at least one exact3; and rounds with at least one exact2.
- Attribute every original fixed and linked exact3 success round and successful TRIO to COMMON, FIXED_ONLY, or LINKED_ONLY. Separately explain how original round-level paired categories (fixed-only 5 / linked-only 7) correspond to successful-TRIO source categories.
- Group rounds by common count 0/1/2/3 and report round count plus fixed/linked exact3 TRIO counts and fixed/linked exact2 TRIO counts. These groups are diagnostic only.
- Replacement interpretation is fixed: REMOVED_BY_LINK = FIXED_ONLY and ADDED_BY_LINK = LINKED_ONLY.

## Anchor contribution

- The source trace directly pairs `anchor_A/B/C` with `linked_A/B/C`. Validate that each anchor belongs to its paired linked TRIO.
- For each LINKED_ONLY successful TRIO, record whether its assigned anchor reappeared in target MAIN6 and how many of the other two members hit.
- Summarize LINKED_ONLY exact3 successes with anchor hit versus anchor miss. No inferred mapping is permitted if the validation fails.

## Primary paired randomization

- Primary outcome is the total exact3 TRIO-count difference `LINKED_ONLY - FIXED_ONLY`.
- Preserve every round and both equal-sized divergent sets. For each of exactly 100,000 repetitions, independently swap the fixed-only and linked-only labels within each round with probability 1/2; sum the resulting exact3 difference.
- Primary one-sided alternative is fixed before results: linked-only > fixed-only.
- Use add-one p-value `(1 + count(simulated difference >= observed difference)) / 100001`.
- Use the same paired swaps to report exact2 observed difference, one-sided p for linked-only > fixed-only, and two-sided p by absolute difference. Also report primary exact3 two-sided p as support.
- Deterministic seed: interpret the first 16 hexadecimal characters of this locked protocol SHA-256 as unsigned 64-bit integer. Record SHA and seed before attribution calculations.

## Judgment

- `DIVERGENCE_SUPPORTED`: linked-only exact3 > fixed-only exact3, primary one-sided p <= 0.05, FUTURE_LEAKAGE=0, structure PASS.
- `DIVERGENCE_INTERESTING`: linked-only exact3 > fixed-only exact3 and 0.05 < p <= 0.10.
- Otherwise: `DIVERGENCE_NOT_SUPPORTED`.
- This judgment cannot modify or replace the original TRIO ORBIT V1 p-value or FINAL.

## Prospective schema and protection

- Produce a prospective logging schema containing target round, fixed/linked 3TRIO, common decomposition, per-TRIO exact0/1/2/3, fixed/linked success, divergent contributions, and reset status. It changes logging fields only, never V1 rules.
- No KTS schedule regeneration/change, fixed/linked rule tuning, outcome-driven subgroup recommendation, EXP-017 creation, recommendation, or OFFICIAL ENGINE/gate/threshold/signature/DB/NUMBER/TRIO/PAIR/CORE change.
- Required final assertions: FUTURE_LEAKAGE=0; original TRIO ORBIT V1 FINAL unchanged; all protected changes=0.

## Lock declaration

This document is the immutable result-blind attribution protocol. Its SHA-256 and deterministic seed must be recorded before any performance decomposition or paired randomization is calculated.

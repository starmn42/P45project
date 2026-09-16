# P45 OPPOSITE-PERIOD STABILITY FILTER VALIDATION — LOCKED PROTOCOL 001

## Lock declaration

- Status: `PROTOCOL_LOCKED_BEFORE_OUTCOME_SCORING`
- FIRST_VALID_TARGET: `3`
- LAST_TARGET: `1238`
- FIRST_VALID_TARGET basis: target 3 is the earliest round for which the frozen canonical `diagnose_stage6` prerequisite path completes using source rounds `1..2`; this was established without reading or scoring target outcomes.
- Source: validated contiguous staging `1..1238`, SHA-256 `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Target 1239 scoring: forbidden.

This file is immutable after its SHA-256 is recorded. No outcome-derived choice may alter this protocol.

## Hypotheses

- `H_SAFEGUARD`: blocked-only candidates have next-round MAIN6 probability below random `6/45`; the filter is a meaningful stability safeguard.
- `H_OVERFILTER`: blocked-only probability is not below random; a rate above random may indicate over-filtering.

## Single locked pattern and variant

The only primary pattern is a NUMBER that:

1. has PRIMARY overall integrated evidence `POSITIVE_TENTATIVE`;
2. has PRIMARY recent100 integrated evidence `INSUFFICIENT`;
3. is HOLD under current `_opposite_directions` semantics;
4. changes to `NUMBER_WEAKEN` or higher when only `_opposite_directions` is disabled; and
5. is not still blocked by HIGH opposite risk or another independent HOLD predicate.

The sole fixed variant treats `recent100 == INSUFFICIENT` as lack of period evidence, not negative direction. Genuine positive-versus-negative evidence polarity remains unchanged. This variant is historical shadow analysis only and cannot alter official semantics.

## Walk-forward boundary

- Historical targets: `3..1238` inclusive.
- Features for target `t`: source rounds only `<=t-1`.
- Candidate set is frozen before accessing target `t` MAIN6.
- Bonus is excluded from the primary outcome.
- Missing or noncontiguous source boundaries cause STOP; no imputation.
- Future-source access count must be zero; target 1239 is never scored.

## Primary sample and outcome

- `BLOCKED_ONLY(t)` is the locked five-condition set above.
- Observation unit: `(target, number)`.
- `Y=1` only when the frozen number occurs in target MAIN6; otherwise `0`.
- Random baseline: `p0=6/45`.
- Primary metric: `DELTA_RANDOM = mean(Y_BLOCKED_ONLY) - 6/45`.

## Locked uncertainty calculation and verdict

- Round-cluster bootstrap: resample activated target rounds with replacement; include all blocked-only observations belonging to each sampled round.
- Replicates: `10,000`.
- PRNG seed: `20260825`.
- 95% CI: empirical percentile interval at `2.5%` and `97.5%` of bootstrap `DELTA_RANDOM`.
- If CI upper `<0`: `SAFEGUARD_SUPPORTED`.
- If CI lower `>0`: `FILTER_HARM_SIGNAL`.
- Otherwise: `INCONCLUSIVE`.
- No p-value is designated or required.

Primary verdict requires both activated target rounds `>=100` and blocked-only observations `>=300`; otherwise `INCONCLUSIVE_MIN_SAMPLE` overrides effect size.

## Descriptive-only secondary outputs

- Official and fixed-variant eligible survivor-count distributions: `0,1,2,3,4,5,>=6`.
- Average eligible count and average MAIN hits captured per target.
- Official eligible, blocked-only, and fixed-variant eligible MAIN hit rates.
- Partial-survivor reporting context.

Secondary results cannot change or rescue the primary verdict.

## Multiple testing and change control

- Primary hypotheses/patterns/metrics: `1/1/1`.
- Threshold search/lookback search/subgroup rescue/parameter tuning: `0/0/0/0`.
- Official gate, threshold, signature, source, code, DB, State, Decision, Registry, and engine semantics changes: forbidden.
- EXP-017 creation and DRAW_DISCOVERY_PAUSE release: forbidden.
- Forced picks, hidden scores, arbitrary weighting, six-number generation, and target-1239 outcome access: forbidden.

## Reporting-policy context

`PARTIAL_SURVIVOR_REPORTING` is stored as `REPORTING_POLICY_DIRECTION_CONFIRMED` with `REPORTING_MINIMUM=NONE`: report the actual `0..N` eligible survivor count, including zero; do not select an arbitrary trio from 4–5; exactly three may later be considered for a natural `PARTIAL_TRIO` display; survivor reporting remains separate from frozen official 3×2 output.

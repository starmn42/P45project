# P45 SURVIVOR POOL ACTIONABILITY — LOCKED PROTOCOL 001

## Lock declaration

- Status: `PROTOCOL_LOCKED_BEFORE_ACTIONABILITY_OUTCOME_CALCULATION`
- Valid historical targets: `3..1238` inclusive (`1236` targets)
- FIRST_VALID_TARGET basis: target 3 is the earliest frozen canonical `diagnose_stage6` target that completes with source rounds `1..2`; determined from prerequisite availability, not outcomes.
- Discovery size: `floor(0.70 × 1236) = 865`
- DISCOVERY_RANGE: `3..867`
- CONFIRMATION_RANGE: `868..1238`
- Source: validated contiguous `1..1238`, SHA-256 `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Target 1239 outcome access/scoring: forbidden.

This file is immutable after SHA-256 recording.

## Fixed definitions

- `RAW_SURVIVOR_POOL(t)`: all frozen official NUMBER rows in `NUMBER_PASS`, `NUMBER_WEAKEN`, or valid `NUMBER_TEST` before minimum-six finalization.
- `RAW_SURVIVOR_COUNT N_t`: size of that exact pool.
- For K, `ACTIONABLE`: `1 <= N_t <= K`; `BROAD_POOL`: `N_t > K`; `ZERO_POOL`: `N_t=0`.
- BROAD_POOL is never truncated or ranked; raw survivors remain audit evidence.
- MAIN6 is accessed only after the target's raw pool is frozen; bonus is excluded.

## Hypotheses and baseline

- `H_ACTIONABLE`: there is a maximum K for which actionable candidate MAIN hit density exceeds random `6/45` reproducibly.
- `H_NULL`: it does not exceed random.
- Candidate-level metric: `DELTA_RANDOM = total survivor MAIN hits / total survivor observations - 6/45`.

## Discovery K search

- Candidate K values: every integer `1..45`, once, discovery only.
- Minimum per K: actionable rounds `>=100` and candidate observations `>=300`.
- Round-cluster bootstrap: resample actionable target rounds with replacement, retaining each round's survivor count and hits.
- Replicates: `10,000` per K.
- PRNG seed for K: `20260825 + K`.
- 95% CI: empirical percentile interval at 2.5% and 97.5% of bootstrap DELTA_RANDOM.
- `K_DISCOVERY`: largest eligible K whose CI lower bound is strictly greater than zero.
- If none: `NO_DISCOVERY_K`; do not run a confirmation predictive test.

## Confirmation

- Only if K_DISCOVERY exists, freeze that single K before reading confirmation outcomes.
- Minimum: actionable rounds `>=50`, candidate observations `>=150`.
- Round-cluster bootstrap replicates/seed/CI: `10,000 / 20260826 / percentile 2.5%,97.5%`.
- CI lower `>0`: `MAX_ACTIONABLE_POOL_SUPPORTED`; otherwise `MAX_ACTIONABLE_POOL_NOT_CONFIRMED`.
- No retuning after confirmation.

## Descriptive-only outputs

- Exact N profile.
- Fixed bins: `0`, `1–2`, `3–5`, `6–9`, `10–14`, `15–19`, `20–29`, `30–39`, `40–45`.
- Round count, observations, hits, candidate hit rate, delta, average pool size, average captured MAIN hits, random expected hits, and lift as applicable.
- These outputs cannot change K or rescue confirmation.

## Future blocking and anti-overfit

- Target t features use only source `<=t-1`; source boundary must equal `t-1`.
- Candidate pool freezes before target MAIN6 access.
- K search only in discovery; one fixed-K confirmation; no subgroup rescue, period/metric/gate change, favorable-period selection, hidden score, weighting, ranking, or top-K.

## Protected policy

- This is reporting/actionability research, separate from official 3×2.
- Official source/code/DB, gates, thresholds, signatures, NUMBER/TRIO/PAIR/CORE semantics, State, Decision, Registry remain unchanged.
- OFFICIAL ENGINE remains `FROZEN`; DRAW_DISCOVERY_PAUSE `ACTIVE`; EXP-017 `NOT_CREATED`.
- `PARTIAL_SURVIVOR_REPORTING / REPORTING_MINIMUM=NONE` remains.
- `SURVIVOR_POOL_ACTIONABILITY_POLICY`: preserve all raw `0..45`; user-facing actionable display may use only a confirmed MAX; above MAX report `BROAD_POOL / NO_ACTIONABLE_PICK`; never truncate; if MAX is unconfirmed keep `NOT_CONFIRMED`.

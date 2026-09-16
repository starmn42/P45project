# P45 EXP-017 — TRIO ORBIT CONSENSUS NUMBER EFFECT V1 PROTOCOL 001

## Registration

- Experiment ID: `EXP-017`
- Canonical registry ID: `EXP-DRAW-20260827-017-V1`
- Title: `TRIO ORBIT CONSENSUS NUMBER EFFECT V1`
- Domain: `DRAW / NUMBER-LEVEL INDEPENDENT HYPOTHESIS`
- Protocol version: `V1 / 001`
- Status after valid lock: `READY_FOR_TEST`
- Lifecycle completed here: `IDEA -> REGISTERED -> DESIGNED -> READY_FOR_TEST`
- No backtest, walkforward outcome, hit count, hit rate, or p-value is calculated by this registration work.

## Research boundary

This experiment asks whether individual numbers selected by both locked TRIO ORBIT Fixed and Linked V1 for the same target are included in the next MAIN6 more often than the fair 6/45 expectation. It is not a rerun of divergence attribution and does not compare Linked-only with Fixed-only, rank the two orbits, or reassess exact-TRIO performance or any existing verdict.

## Hypotheses

- H1: pre-draw consensus candidates have an inclusion rate above `6/45` in target MAIN6.
- H0/opposite hypothesis: consensus candidates have no special predictive information and their inclusion rate does not exceed `6/45`.
- Direction: one-sided upper-tail only.
- Alpha: `0.05`.

## Candidate definition

For target `t`, form `F_t` as the sorted unique union of all numbers in the three locked Fixed TRIOs, and `L_t` as the sorted unique union of all numbers in the three locked Linked V1 TRIOs. Define `C_t = F_t intersection L_t` and `k_t = |C_t|`. Repetition within an orbit counts once. No filter, weighting, score, rank, supplementation, or truncation is allowed.

## Inputs and future-data block

- Historical candidate source: `v27_storage/experiments/trio_orbit_v1_001/P45_TRIO_ORBIT_V1_ROUND_TRACE_001.csv`
- Required source trace SHA-256 at design: `bcf54e5f13bc3b3ab73eb23d936030648b7da63f9264a10bcdf715bc5ea091e7`
- Canonical snapshot at lock: `v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv`
- Required canonical SHA-256 at lock: `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Candidate generation for target `t` may use only information available before the target outcome. The locked Fixed/Linked trace is reused without algorithm changes.
- Historical universe: targets `2..1238`, exactly `1237` targets.
- Development/backtest split: targets `2..867`, exactly `866` targets.
- Historical walkforward split: targets `868..1238`, exactly `371` targets.
- Split boundaries are immutable in V1.

## Primary metric and exact null

- For each target, `h_t = |C_t intersection MAIN6_t|`.
- `TOTAL_EXPOSURES X = sum(k_t)` and `TOTAL_HITS H = sum(h_t)`.
- Primary metric: `CONSENSUS_INCLUSION_RATE = H / X`.
- Null rate: `6/45`.
- Effect size: absolute lift in percentage points; relative lift may be secondary descriptive context.
- Per-target null: `H_t ~ Hypergeometric(N=45, K=k_t, n=6)`.
- Primary null distribution: exact dynamic-programming convolution of all per-target hypergeometric PMFs.
- Primary p-value: `P(H_null >= H_observed)`, one-sided upper-tail.
- Exact calculation cannot be replaced by binomial or Monte Carlo without reporting the numerical blocker and obtaining separate approval.

## Secondary robustness

Target shuffle is context only. Keep `C_t` fixed, permute the MAIN6 target sequence inside the evaluated split, use exactly `100000` permutations and seed `20260827`, and compute a one-sided upper-tail value. Label it `ROBUSTNESS_CONTEXT_ONLY`; it cannot rescue a failed primary test.

## Minimum sample and structural blocks

- Entire historical: active rounds `>=100` and exposures `>=300`.
- Development: active rounds `>=70` and exposures `>=200`.
- Walkforward: active rounds `>=30` and exposures `>=100`.
- Any failure gives `PROTOCOL_BLOCKED_INSUFFICIENT_SAMPLE`; thresholds cannot be lowered in V1.
- Historical `max(k_t)` must be `<=6`; otherwise `PROTOCOL_BLOCKED_OUTPUT_SIZE_INCOMPATIBLE` and no V1 backtest.
- Source integrity failure, future leakage risk, or non-reproducible candidates also blocks READY_FOR_TEST.

## Output rule

- `k=0`: output zero numbers and PASS.
- `1<=k<=6`: output every member of `C_t` in ascending order.
- Future `k>6`: record `OUTPUT_SIZE_BLOCKED`, emit no consensus signal, and do not truncate or rank. Any redesign requires V2.

## Multiple-testing policy

There is exactly one confirmatory primary hypothesis: total consensus-number inclusion above `6/45`. No k subgroup, individual number, period, reset status, anchor, KTS class, overlap size, recent window, calendar group, or favorable split is a separate success test. Any such diagnostic is exploratory only and cannot change the EXP-017 verdict.

## Locked historical verdict rules

- Development `2..867`: require rate `>6/45` and exact primary `p<=0.05`. Both true gives `DEVELOPMENT_SCREEN_POSITIVE`; otherwise `FAILED_NOT_SUPPORTED` and walkforward cannot rescue it.
- Only after development passes, evaluate walkforward `868..1238` with the same two conditions. Pass gives `HISTORICAL_WALKFORWARD_POSITIVE`; failure gives `FAILED_NOT_REPRODUCED`.
- Both historical stages passing yields at most `HISTORICAL_SCREEN_AND_WALKFORWARD_POSITIVE / PROSPECTIVE_REQUIRED`, never final support.

## Prospective confirmation

- If canonical latest is `1238`, target 1239 remains unavailable, and this lock predates outcome availability, prospective start is `1239`; otherwise it remains `PENDING` until the next truly unobserved sealed target.
- Prospective evaluation occurs once only after both `MIN_PROSPECTIVE_TARGETS=120` and `MIN_PROSPECTIVE_EXPOSURES=360` are met. Before then: `TRACKING_ONLY / INSUFFICIENT_PROSPECTIVE_SAMPLE`.
- Formal prospective confirmation is retained only if both historical stages pass.
- Rate `>6/45` and exact primary `p<=0.05` gives `SUPPORTED_PROSPECTIVE_CONFIRMED`; otherwise `FAILED_PROSPECTIVE_NOT_REPRODUCED`.
- No early success declaration and no retrospective rescue are allowed.

## Promotion and protection

Even `SUPPORTED_PROSPECTIVE_CONFIRMED` permits only `PROMOTION_CANDIDATE`; official promotion requires separate user approval. OFFICIAL ENGINE remains `FROZEN`; NO-PICK remains `UNRESOLVED`; DRAW_DISCOVERY_PAUSE remains `ACTIVE`; verified independent signal remains `NONE`. Fixed V1, Linked V1, KTS45 schedule, official gates/thresholds/signatures/code/DB/NUMBER/TRIO/PAIR/CORE, existing historical and divergence verdicts, sealed prospective records, and prospective result fields are immutable under this protocol. FUTURE_LEAKAGE must remain `0`.

## V1 immutability

After SHA-256 locking, this V1 protocol must not be edited to fit outcomes. Any semantic change requires `EXP-017 V2` or a separate experiment.

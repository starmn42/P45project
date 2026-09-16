# P45 EXP-018 — RESIDUAL NEIGHBOR EFFECT / ADJACENCY AXIS CLOSURE V1 PROTOCOL 001

## Registration and purpose

- Short ID: `EXP-018`
- Canonical registry ID: `EXP-DRAW-20260827-018-V1`
- Title: `RESIDUAL NEIGHBOR EFFECT / ADJACENCY AXIS CLOSURE V1`
- Domain: `DRAW / NUMBER-LEVEL CLOSURE DIAGNOSTIC`
- Protocol version: `V1 / 001`
- Status after a valid pre-outcome lock: `READY_FOR_TEST`
- Lifecycle in registration work: `IDEA -> REGISTERED -> DESIGNED -> READY_FOR_TEST`
- This experiment tests conditional association, not causality or physical ball adjacency. Its purpose is to decide whether the numerical-label `T-1 MAIN6 -> ±1 -> T MAIN6` research axis merits continued study or can be closed against a predeclared practically relevant positive effect.
- This protocol creates no recommendation or signal output.

## Exact question and hypotheses

- Question: Within the same target and exact Return-age, does numerical-label ±1 adjacency to `T-1 MAIN6` provide additional positive association with inclusion in `T MAIN6`?
- H1: Neighbor status carries a positive, practically relevant residual conditional association after exact Return-age control.
- H0/opposite: Within target and exact Return-age margins, Neighbor status provides no additional positive information.
- No mechanical, causal, physical-position, friction, or draw-machine claim is permitted.

## Historical universe and immutable split

- Historical targets: `2..1238`.
- Development: `2..867`, exactly `866` targets.
- Holdout/Historical Walkforward: `868..1238`, exactly `371` targets.
- Undefined-age numbers are excluded from formal matched analysis.
- Split boundaries cannot change in V1.

## Predictor timing and Return-age

All predictors for target `T` must be available before its outcome. For number `x`, using MAIN6 only through `T-1`, let `last_seen_T(x)` be its last MAIN6 round. If defined, `AGE_T(x)=(T-1)-last_seen_T(x)`. A number in `T-1 MAIN6` has age 0 but is excluded from both treatment and control. A number never seen through `T-1` is `AGE_UNDEFINED` and excluded from formal matching. BONUS is never used.

## Eligible universe, Neighbor, and Control

- `PREV_T = MAIN6_(T-1)`.
- `E_T = {1..45} minus PREV_T`.
- Form raw numerical neighbors `y-1` and `y+1` for every `y in PREV_T`, retain only `1..45`, do not wrap 1 and 45, deduplicate, and remove `PREV_T`.
- Treatment `N_T` is that final Neighbor set.
- `CONTROL_POOL_T = E_T minus N_T`.
- Return-age is a matching/stratification control only, never a signal, threshold, rank, weight, or selection rule.

## Exact-age matching

- A stratum is exactly `s=(T, exact AGE)`.
- `N_(T,a)` contains Neighbor numbers with exact age `a`; `C_(T,a)` contains Control numbers with exact age `a`.
- A valid formal stratum requires `n_neighbor>=1` and `n_control>=1`.
- Use every Neighbor and every Control in each valid stratum. No 1:1 sampling, random control choice, nearest-age matching, approximate binning, or favorable-age selection is allowed.
- Neighbor exposures with undefined age or without a same-target same-age control are excluded from formal matched analysis and reported structurally.

## Outcome definition

For eligible number `x`, `Y_T(x)=1` iff `x` is in `MAIN6_T`, else 0. Registration/preflight must not combine this outcome with predictors. Actual hits, rates, deltas, p-values, confidence bounds, or split verdicts are prohibited before lock.

## Primary conditional exact test

For valid stratum `s=(T,a)`, define Neighbor count `n1_s`, Control count `n0_s`, Neighbor hits `a_s`, Control hits `c_s`, and total hits `m_s=a_s+c_s`. Under H0 and fixed margins, `A_s` follows the conditional Hypergeometric allocation of `m_s` hits among `n1_s+n0_s` positions with `n1_s` Neighbor positions. The primary statistic is `TOTAL_NEIGHBOR_HITS=sum(a_s)`. Its exact null distribution is the dynamic-programming convolution of every stratum-specific Hypergeometric PMF. The primary p-value is `P(TOTAL_NEIGHBOR_HITS_NULL >= observed)`, one-sided upper-tail, with `ALPHA=0.05`.

Exact DP is structurally feasible for the locked matched strata. It cannot be replaced by an approximate, asymptotic, binomial, or Monte Carlo primary test without reporting a blocker and obtaining separate approval.

## Matched effect size

Within stratum `s`, let `pN_s=a_s/n1_s`, `pC_s=c_s/n0_s`, and `w_s=(n1_s*n0_s)/(n1_s+n0_s)`. Define:

`DELTA_MATCH = sum[w_s*(pN_s-pC_s)] / sum(w_s)`.

Report it as an absolute probability difference and in percentage points. A simple pooled rate difference is not the primary matched effect size.

## Practical threshold and closure precision

- Locked practical threshold: `DELTA_PRACTICAL=+0.0100`, exactly `+1.00 percentage point`.
- This is a research-continuation threshold, not statistical alpha, and cannot change after outcomes.
- Uncertainty method: target-round cluster bootstrap. All matched age strata belonging to one target are resampled as one cluster with replacement inside the evaluated split.
- `N_BOOTSTRAP=100000`.
- `RANDOM_SEED=20260827`.
- Report the one-sided 95% upper confidence bound `U95_DELTA`.
- Number-level observations or same-target strata cannot be bootstrapped as independent clusters.

## Split-level verdicts

- `POSITIVE_PRACTICALLY_RELEVANT`: `p_primary<=0.05` AND `DELTA_MATCH>=+0.0100`.
- `NO_PRACTICALLY_USEFUL_EFFECT`: `U95_DELTA<+0.0100`. This excludes a positive effect large enough for continued P45 study; it does not prove an exactly zero effect.
- `INCONCLUSIVE`: every other result, including `p_primary>0.05` with `U95_DELTA>=+0.0100`.

## Historical final verdict matrix

1. Development and Holdout both `NO_PRACTICALLY_USEFUL_EFFECT` -> `AXIS_CLOSED_NO_PRACTICALLY_USEFUL_RESIDUAL_NEIGHBOR_EFFECT`.
2. Both `POSITIVE_PRACTICALLY_RELEVANT` -> `HISTORICAL_RESIDUAL_NEIGHBOR_EFFECT_POSITIVE / SIGNALIZATION_PROTOCOL_REQUIRED / PROSPECTIVE_REQUIRED`; never call this SUPPORTED.
3. Exactly one split positive -> `FAILED_NOT_REPRODUCED / NO_AXIS_CLOSURE`.
4. Every other combination -> `INCONCLUSIVE / NO_AXIS_CLOSURE / NO_SIGNAL_CLAIM`.

Development and Holdout are both evaluated under the same locked rules; no favorable split selection is allowed.

## Exact closure scope

If the closure verdict is reached, close only the `T-1 MAIN6 -> numerical label ±1 adjacency -> T MAIN6 predictive axis`. Without new independent external evidence, do not re-propose old/recent/thresholded/specific-age/weighted/+1-only/-1-only/favorable-period/favorable-number ±1 variants or ±1 combinations with frequency, Return-age, extinction, or an existing failed axis.

This experiment does not close ±2 or larger distances, same-round consecutive pairs, sorted-position adjacency, TRIO-internal adjacency, actual physical ball position, mechanical adjacency, other spatial structures, or other independent transition structures.

## Positive-result limitations and signalization separation

Historical positivity establishes only replicated conditional historical association. It cannot generate Top 6 numbers, choose a favorable age, select +1 versus -1, create recommendations, modify Fixed/Linked, or enter the official engine. Any output module requires a new experiment, new locked 0–6 output rule, and truly future data after that new lock.

## Prospective policy

This V1 is a closure diagnostic. It does not automatically designate 1239 as prospective evidence and does not create a signalization module. If a later positive result motivates a separately locked signalization protocol, only targets genuinely unobserved after that later lock are eligible; 1239 cannot be used retrospectively if already observed.

## Multiple-testing policy

There is one formal question. Age, number, +1/-1, period, recent window, decade, odd/even, KTS, Fixed, Linked, reset, and BONUS subgroups are not success tests. Any later view is `EXPLORATORY_ONLY` and cannot alter EXP-018.

## Future-data block and existing-axis protection

- Target T predictors use only MAIN6 through T-1.
- No target outcome may be joined during preflight.
- Existing EXP-004, Return-age, R-1/movement, CLOSED/FAILED axes and all prior verdicts remain unchanged.
- Return-age is never a signal and no Age threshold, oldest-number selection, weighting, or post-outcome rescue is allowed.

## Official protection and forbidden changes

OFFICIAL ENGINE remains `FROZEN`. Official gates, thresholds, signatures, code, DB, NUMBER/TRIO/PAIR/CORE, Fixed V1, Linked V1, KTS45, the current KTS schedule, sealed 1239, prospective outcome fields, and existing historical results/verdicts are immutable. No hidden score, forced number generation, threshold relaxation, matching relaxation, failed-result deletion, future leakage, or result-driven protocol edit is allowed. `FUTURE_LEAKAGE=0` is mandatory.

## V1 immutability

After SHA-256 locking, this V1 protocol must not be edited. Any semantic change requires preserved V1 plus `EXP-018 V2` or a separate experiment.

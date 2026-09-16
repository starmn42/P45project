# P45 EXP-018 V2 — RESIDUAL NEIGHBOR EFFECT / ADJACENCY AXIS CLOSURE PROTOCOL 001

## Version identity and outcome-blind lineage

- Experiment family: `EXP-018`
- Version: `V2`
- Full registry ID: `EXP-DRAW-20260827-018-V2`
- Title: `RESIDUAL NEIGHBOR EFFECT / ADJACENCY AXIS CLOSURE V2`
- Status after valid lock: `READY_FOR_TEST`
- V1 protocol SHA-256: `d64b3ec3bdf5c65006236cefc67432333bc5edbc61dbe3b5db90d85a614d527c`
- V1 lock SHA-256: `08006727b6b83f6d903cc1216c24be64a8bf21fbc027a7e471162da10aeab906`
- V1 execution verdict: `EXP_018_EXECUTION_BLOCKED_BOOTSTRAP_AMBIGUITY`
- V1 historical outcome access: `0`
- V1 Neighbor/Control hits, rates, observed DELTA_MATCH, primary p-value, bootstrap distribution, U95, and split/final verdicts: `NOT CALCULATED`
- V1 is preserved and is not FAILED, overwritten, or edited by V2.

## Sole V2 clarification

V2 retains the same research axis, hypothesis, opposite hypothesis, target universe, split, predictors, exact matching, primary test, effect formula, practical threshold, verdict matrix, closure scope, multiple-testing limits, prospective separation, and official protections as V1. The sole substantive clarification is the complete deterministic construction of bootstrap `U95_DELTA`.

## Unchanged research question and boundaries

The sole question remains whether numerical-label ±1 adjacency to `T-1 MAIN6` carries a positive, practically relevant residual conditional association with `T MAIN6` inclusion after exact Return-age control. This is association, not causality, physical ball position, friction, or machine mechanism. It creates no signal or recommendation.

- Historical universe: targets `2..1238`.
- Development: `2..867`, 866 targets.
- Holdout/Historical Walkforward: `868..1238`, 371 targets.
- MAIN6 only; BONUS unused.
- `AGE_T(x)=(T-1)-last_seen_T(x)` using MAIN6 through T-1 only.
- `AGE_UNDEFINED` is excluded from formal matched analysis.
- `E_T={1..45} minus MAIN6_(T-1)`; prior MAIN6 is excluded from treatment and control.
- Treatment is the unique in-range numerical ±1 neighbors of prior MAIN6, minus prior MAIN6, with no 1↔45 wrap-around.
- Control is every other eligible number.
- Formal stratum is `(target T, exact Return-age a)` with Neighbor count >=1 and Control count >=1.
- Use all Neighbor and Control members; no sampling, approximate/nearest-age matching, age threshold, rank, weighting, or favorable subgroup selection.

## Unchanged primary conditional exact test

For matched stratum `s`, fix Neighbor count `n1_s`, Control count `n0_s`, and total hits `m_s=a_s+c_s`. Under H0, Neighbor hits follow the corresponding conditional Hypergeometric allocation. Convolve all stratum PMFs by exact dynamic programming for `TOTAL_NEIGHBOR_HITS=sum(a_s)`. Primary p-value is the one-sided upper tail `P(null total >= observed total)`. `ALPHA=0.05`. Bootstrap never replaces this primary exact test.

## Unchanged matched effect and practical threshold

For every stratum:

- `pN_s=a_s/n1_s`
- `pC_s=c_s/n0_s`
- `w_s=(n1_s*n0_s)/(n1_s+n0_s)`
- `DELTA_MATCH=sum[w_s*(pN_s-pC_s)]/sum(w_s)`

Locked practical threshold remains `DELTA_PRACTICAL=+0.0100`, exactly `+1.00 percentage point`.

## V2 locked bootstrap method

- Method: `TARGET-ROUND CLUSTER PERCENTILE BOOTSTRAP`.
- Purpose: one-sided 95th-percentile upper bound for `DELTA_MATCH`, named `U95_DELTA`.
- Replicates: exactly `B=100000` per split.
- Seed: `20260827`.
- Do not use basic, BCa, studentized, normal-approximation, bootstrap-t, or any library-default percentile implementation.

## Sampling population and cluster unit

Within each split, include only target rounds having at least one valid matched exact-age stratum. The sampling population is the target numbers sorted strictly ascending. Each target round and all its matched age strata form one indivisible cluster.

- `DEV_MATCHED_ROUNDS`: ascending Development targets with >=1 valid matched stratum; length `N_DEV`.
- `HOLD_MATCHED_ROUNDS`: ascending Holdout targets with >=1 valid matched stratum; length `N_HOLD`.
- File order, mapping order, database return order, hash order, or any unsorted order is forbidden.

## RNG and with-replacement sampling

Use Python standard-library `random.Random` only.

- Development RNG: a fresh `random.Random(20260827)`.
- Holdout RNG: a separate fresh `random.Random(20260827)`.
- The two splits are independently initialized from the same locked seed.
- For each replicate in a split with population size `N_SPLIT`, generate exactly `N_SPLIT` indices sequentially by `rng.randrange(N_SPLIT)`.
- Sampling is with replacement. If a round index appears multiple times, include every matched stratum contribution from that round the same number of times.
- NumPy RNG, operating-system randomness, system time, hash-dependent state, and implicit library RNGs are forbidden.

## Replicate DELTA_MATCH

For each selected cluster occurrence, repeat all its matched-stratum numerator and weight contributions. Calculate:

`DELTA_b = sum_selected[w_s*(pN_s-pC_s)] / sum_selected(w_s)`.

This is exactly the V1 effect formula. Cluster multiplicity repeats every constituent contribution with identical multiplicity.

## Invalid replicate policy

If any replicate has total weight `sum(w_s)<=0`, NaN, infinity, or any computation failure, do not drop it, redraw it, replace it, impute it, or silently continue. Stop the entire execution with `EXP_018_EXECUTION_BLOCKED_BOOTSTRAP_INVALID_REPLICATE`, record the invalid replicate count/index available at detection, and calculate no verdict.

## Exact U95 order statistic

For a split with all 100,000 valid replicate deltas:

1. Sort all deltas ascending using their numeric values.
2. Select the 95,000th value in 1-based order.
3. In Python zero-based indexing select exactly `sorted_bootstrap_delta[94999]`.
4. Set that value to `U95_DELTA`.

Interpolation is prohibited. `np.percentile`, library percentile/quantile defaults, method options, basic/BCa/studentized transformations, and averaging adjacent order statistics are prohibited.

## Unchanged split verdicts

- `POSITIVE_PRACTICALLY_RELEVANT`: `p_primary<=0.05` AND `DELTA_MATCH>=+0.0100`.
- `NO_PRACTICALLY_USEFUL_EFFECT`: `U95_DELTA<+0.0100`.
- `INCONCLUSIVE`: every other result.

Both Development and Holdout must be evaluated regardless of the other split's result unless lock, structure, source, primary-test, or bootstrap integrity blocks the entire run.

## Unchanged final verdict matrix

1. Both splits `NO_PRACTICALLY_USEFUL_EFFECT` -> `AXIS_CLOSED_NO_PRACTICALLY_USEFUL_RESIDUAL_NEIGHBOR_EFFECT`.
2. Both splits `POSITIVE_PRACTICALLY_RELEVANT` -> `HISTORICAL_RESIDUAL_NEIGHBOR_EFFECT_POSITIVE / SIGNALIZATION_PROTOCOL_REQUIRED / PROSPECTIVE_REQUIRED`; never SUPPORTED.
3. Exactly one split positive -> `FAILED_NOT_REPRODUCED / NO_AXIS_CLOSURE`.
4. Every other combination -> `INCONCLUSIVE / NO_AXIS_CLOSURE / NO_SIGNAL_CLAIM`.

## Closure, non-closure, and positive-result limits

Closure, if reached, applies only to `T-1 MAIN6 -> numerical label ±1 adjacency -> T MAIN6 predictive axis` and the outcome-mined ±1 derivatives enumerated in V1. It does not close ±2 or larger distances, same-round consecutive pairs, sorted-position adjacency, TRIO-internal adjacency, physical-ball adjacency, or other independent spatial/transition structures.

Historical positivity permits no Age/number/+1/-1 selection, Top 6, 0–6 signal, retrospective 1239 use, 1240 recommendation, official change, or Fixed/Linked change. Signalization requires a new experiment and future-data lock after its own protocol.

## Multiple testing, no rescue, and prospective separation

There is one formal question. Age, number, direction, period, recent window, decade, odd/even, KTS, Fixed, Linked, BONUS, reset, or other subgroup results are not success tests and cannot rescue or alter V2. No post-hoc mining is part of the locked execution. V2 is a historical closure diagnostic and does not automatically designate target 1239 for prospective evidence.

## Outcome-blind preflight evidence

- V1 predictor/matching structural preflight SHA-256: `ca2a8055eeda0f7c3c8c8217f9dd966b614e5fb51f2c7be54a7250364d074190`.
- V2 dummy-data bootstrap implementation preflight SHA-256: `d2d7b73dfee923da80da217479376fca95c74010b176f40ef431721f7837de30`.
- Dummy preflight uses no P45 historical outcomes and verifies B, seed, sorted populations, split-independent RNG initialization, `rng.randrange`, replacement, cluster duplication, invalid replicate blocking, direct sorting, index 94999, no interpolation, and deterministic reproduction.

## Future-data and official protection

Target T predictors use only MAIN6 through T-1. Registration and lock work cannot join target outcomes. V1 files and all existing results/verdicts are immutable. OFFICIAL ENGINE remains `FROZEN`; official gate/threshold/signature/code/DB, NUMBER/TRIO/PAIR/CORE, Fixed V1, Linked V1, KTS45, sealed 1239, prospective outcome/log fields, and failed results are unchanged. `FUTURE_LEAKAGE=0` is mandatory.

## V2 immutability

After SHA-256 lock, this V2 protocol cannot be edited to fit outcomes. Any further semantic change requires preserved V1/V2 plus a new version registered and locked before outcome access.

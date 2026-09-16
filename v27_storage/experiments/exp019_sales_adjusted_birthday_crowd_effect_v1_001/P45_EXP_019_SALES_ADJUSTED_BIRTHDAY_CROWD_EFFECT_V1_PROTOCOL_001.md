# P45 EXP-019 — SALES-ADJUSTED BIRTHDAY-RANGE CROWD EFFECT V1 PROTOCOL 001

## Registration and scope

- Short ID: `EXP-019`
- Full ID: `EXP-DRAW-20260827-019-V1`
- Title: `SALES-ADJUSTED BIRTHDAY-RANGE CROWD EFFECT V1`
- Short purpose: `SALES-ADJUSTED CROWD SELECTION BIAS`
- Domain: `EXTERNAL HUMAN-BEHAVIOR / CROWD-SELECTION METADATA`
- Lifecycle after a valid data preflight: `IDEA -> REGISTERED -> DESIGNED -> READY_FOR_TEST`
- This is not a draw-probability or Official P45 recommendation study. It tests whether winning combinations containing more day-of-month-range labels are held by more winning games after adjustment for sales volume.
- Existing extinction, Return-age, transition, ±1 adjacency, consensus, Fixed, Linked, KTS, CLOSED, and FAILED axes are not retuned or reassessed.

## External hypothesis and interpretation boundary

The hypothesis is motivated by external lottery-choice evidence that people do not always select combinations uniformly and may prefer low, personally meaningful, or date-related numbers. V1 has exactly one confirmatory structural predictor.

- H1: `beta > 0`; more labels in `1..31` are associated with more first-prize winning games after sales adjustment.
- H0/opposite: `beta <= 0`; the predictor supplies no additional positive crowd-popularity information.
- A positive result concerns human selection/combination popularity only. It never means numbers `1..31` are more likely to be drawn.

## Official source and fields

- External source must be the official Korean Donghaeng Lottery domain `dhlottery.co.kr`.
- Required formal fields per draw: draw number/date, MAIN6, BONUS, first-prize winning game count, first-prize total prize, first-prize prize per game, and total sales amount.
- Primary calculation fields: draw, MAIN6, first-prize winning games, total sales.
- No third-party substitute is allowed without separate user approval.
- Existing P45 canonical MAIN6 is read-only and used solely for exact cross-checking against acquired official MAIN6.

## Price regime, historical universe, and split

- Formal historical universe: draws `88..1238`, exactly `1151` rounds.
- Draws `<=87` are excluded because of the earlier 2,000 KRW price regime.
- Price per game: exactly `1000 KRW` throughout the formal universe.
- Development: draws `88..867`, exactly `780` rounds.
- Holdout/Historical Walkforward: draws `868..1238`, exactly `371` rounds.
- Draw `1239` and later are forbidden.
- Every formal draw must be complete; missing rounds cannot be dropped to reduce the sample.

## Predictor

For draw `t`, define `B_t` as the count among MAIN6 satisfying `1<=number<=31`. Name: `BIRTHDAY_RANGE_COUNT`; support `0..6`. Threshold 31 is the calendar day-of-month boundary and cannot be changed after outcomes. V1 prohibits alternative low-number thresholds or additional features including 1..12, 1..30, lucky 7, primes, parity, sums, runs, endings, decades, spans, endpoints, visual patterns, individual labels, winner bands, and manual/automatic purchase breakdown.

## Outcome and sales-adjusted fair baseline

- `W_t`: official first-prize winning game count, not an inferred person count.
- `SALES_t`: official total sales amount in KRW.
- Require `SALES_t mod 1000 = 0`; no rounding or silent exclusion.
- `G_t=SALES_t/1000`, an exact integer number of games sold.
- Combination universe `M=8,145,060`.
- `LAMBDA_t=G_t/8,145,060`.

## Primary model and effect

Use a Poisson log-linear count model with offset and one predictor:

`log(E[W_t]) = log(LAMBDA_t) + alpha + beta*B_t`.

Report `beta_hat` and `exp(beta_hat)`. The latter is the multiplicative sales-adjusted expected first-prize game-count ratio for one additional birthday-range number.

### Deterministic beta estimator

No statistical-library optimizer or implicit defaults are allowed. Profile out the intercept at each beta:

- `A(beta)=sum[LAMBDA_t*exp(beta*B_t)]`
- `exp(alpha_hat(beta))=sum(W_t)/A(beta)`
- `mu_t(beta)=LAMBDA_t*exp(alpha_hat(beta)+beta*B_t)`
- profile score `S(beta)=sum[B_t*(W_t-mu_t(beta))]`

Solve `S(beta)=0` by deterministic bisection on the fixed bracket `[-20,+20]`. Evaluate sums with Python `math.fsum` and exponentials with `math.exp`. Require finite values and a bracketed zero (`S(-20)>=0` and `S(+20)<=0`, allowing an exact endpoint zero). At each iteration choose `mid=(low+high)/2`; if `S(mid)>0`, set `low=mid`, otherwise set `high=mid`. Stop when `high-low<=1e-12`; use `beta_hat=(low+high)/2`. Maximum iterations: `1000`. Any nonfinite value, nonpositive `sum(W_t)`, missing bracket, or nonconvergence blocks execution as `EXP_019_EXECUTION_BLOCKED_EFFECT_ESTIMATOR` rather than changing the solver.

## Primary permutation score test

Within each evaluated split, keep ordered `(W_t,LAMBDA_t)` pairs fixed and permute only the ordered `B_t` values across round labels.

- H0 global scale: `c=sum(W_t)/sum(LAMBDA_t)`.
- Observed score: `U_obs=sum[B_t*(W_t-c*LAMBDA_t)]`, evaluated with `math.fsum` in ascending draw order.
- Permutations: exactly `100000`.
- Seed: `20260827`.
- RNG: Python standard-library `random.Random`.
- Development uses a fresh `random.Random(20260827)`.
- Holdout, only if the Development gate passes, uses a separate fresh `random.Random(20260827)`.
- For each permutation, copy the original ordered `B_t` list exactly once, call `rng.shuffle(copy)` exactly once, then compute `U_perm` against the unchanged ordered residual list using `math.fsum`.
- One-sided upper p-value: `(1+count(U_perm>=U_obs))/(100000+1)`.
- No alternative correction, centering choice, RNG, approximate p-value, or asymptotic Poisson standard error can replace the primary test.

## Development gate and conditional Holdout

- Development success requires both `beta_hat>0` and `p_perm<=0.05`, yielding `DEVELOPMENT_SCREEN_POSITIVE`.
- Otherwise final is `FAILED_NOT_SUPPORTED`; formal Holdout is not executed and reason is `DEVELOPMENT_FAILED_PROTOCOL_GATE`.
- Only after Development passes, evaluate Holdout `868..1238` with the identical estimator and permutation test.
- Holdout success requires `beta_hat>0` and `p_perm<=0.05`, yielding `HISTORICAL_SCREEN_AND_WALKFORWARD_POSITIVE / CROWD_BIAS_HISTORICALLY_REPRODUCED`.
- Holdout failure yields `FAILED_NOT_REPRODUCED`.
- Historical positivity is not SUPPORTED and permits no draw-probability claim.

## Multiple-testing and winner-band separation

V1 has one confirmatory predictor only. No other structural or purchase-mode feature is calculated for success or rescue. The separate idea of mining number structure among rounds with 10–15 first-prize games is excluded from EXP-019 and may only be considered under a distinct future experiment locked before outcomes.

## Positive and failure interpretation

A positive historical result allows only an observation about sales-adjusted human combination popularity. Recommendation generation, Official Engine integration, Fixed/Linked/NUMBER/TRIO/PAIR/CORE changes, and draw-probability claims are prohibited. Any payout-sharing or crowd-avoidance application needs a separate protocol and prospective validation.

Failure means only that the predeclared positive `1..31` effect on sales-adjusted first-prize game count was not supported under V1. It does not deny every form of human selection bias or close unrelated CROWD features.

## Data acquisition and integrity gates

This protocol must be SHA-256 locked before bulk winner/sales acquisition. After lock, acquire official draws `88..1238` without bypassing access controls or excessive requests. If official access is unavailable, stop with `DATA_ACQUISITION_BLOCKED`; do not substitute third-party data.

Required gates:

- exactly 1151 unique ascending draws; Development 780 and Holdout 371;
- no missing or duplicate draws;
- official MAIN6 exactly matches read-only P45 canonical MAIN6 for every draw;
- every required official field is present and parseable;
- every sales amount is an integer divisible by 1000;
- games sold and lambda are deterministically derived;
- source URLs/method and retrieval timestamp are recorded;
- experiment-only dataset and source manifest are SHA-256 hashed.

Any failure blocks READY_FOR_TEST without trimming rounds or editing official/canonical data.

## Outcome-blind acquisition rule

Raw winner count and sales may be stored after protocol lock, and `B_t` may be structurally tabulated. This acquisition/preflight work must not calculate or preview any relation between `B_t` and winners/sales: no grouped winner summaries, adjusted ratios, correlations, regression beta, score U, permutation, p-value, split verdict, chart, or qualitative result preview.

## Future-data and project protection

Use no draw >=1239. External metadata remains experiment-only and is never merged into the Official DB. OFFICIAL ENGINE remains `FROZEN`; official gate/threshold/signature/code/DB, NUMBER/TRIO/PAIR/CORE, Fixed V1, Linked V1, KTS, sealed prospective files, and all existing experiment verdicts remain unchanged. `FUTURE_LEAKAGE=0` is mandatory.

## V1 immutability

After SHA-256 locking, this V1 protocol cannot be edited to fit data or outcomes. Any semantic revision requires preserved V1 plus a separately registered V2.

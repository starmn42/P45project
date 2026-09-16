# EXP-PRIZE-002 V1 LOCKED_PROTOCOL

## Identity and boundary

- Logical ID: `EXP-PRIZE-002-V1`
- Domain: `PRIZE_SHARE`
- Title: `SECOND-PRIZE CROSS-OUTCOME CORROBORATION`
- This is cross-outcome corroboration, not independent empirical replication and not DRAW research.
- Historical data: exactly rounds 1~1237; round 1238+ forbidden.

## Locked source fields

- round: `ltEpsd`
- main: `tm1WnNo`~`tm6WnNo`
- bonus: `bnsWnNo`
- second-prize games: `rnk2WnNope`
- total sales: `wholEpsdSumNtslAmt`
- price/game: 2,000 KRW for 1~87; 1,000 KRW for 88~1237
- sold lines: total sales divided by price/game

## Locked hypothesis and predictor

For round r, let `m_r` be the count of six main numbers at most 31 and `b_r=1` when bonus is at most 31, otherwise 0. The six exact second-prize tickets are formed by omitting each main number once and adding the bonus.

- `X2_r = (5*m_r + 6*b_r)/6`
- Direct enumeration of the six tickets must equal the closed form for all rounds.
- `MU_B = 6*31/45`
- `Z2_r = X2_r - MU_B`
- H1: higher X2 is associated with more second-prize winning games after conditioning on sold lines.
- H0/opposite: association is zero or negative.

## Outcome and model

- `K2_r = rnk2WnNope`
- `N_r = sold lines`
- `M = C(45,6) = 8,145,060`
- uniform baseline `E[K2|N] = 6*N/M`
- descriptive `SHARE2_INDEX = K2*M/(6*N)`
- effect model: `log(E[K2]) = log(6*N) + alpha + beta2*Z2`
- Poisson parametric p-values are not primary inference.

## Fixed validation and split

- rows 1~1237 exactly; missing/duplicate/canonical mismatch 0
- valid unique main six and distinct valid bonus
- K2 nonnegative integer, sales positive, N positive integer
- TRAIN 1~800; confirmatory HOLDOUT 801~1237
- no post-hoc exclusions or split changes

## Locked gates

1. TRAIN direction: `beta2_train > 0`; otherwise `FAILED_EARLY_TRAIN_DIRECTION` and no holdout permutation or WF.
2. HOLDOUT: `beta2_holdout > 0` and block-permutation one-sided `p <= 0.05`.
3. Primary block permutation: within 801~900, 901~1000, 1001~1100, 1101~1237; 100,000; seed 2026082103; `(1+exceed)/100001`.
4. Secondary global permutation: 100,000; seed 2026082104; diagnostic only.
5. WF only after holdout success, with the same four frozen OOS blocks. Pass iff total ALT-minus-NULL Poisson log-likelihood is positive.
6. Holdout fail = `FAILED`; holdout pass and WF fail = `INCONCLUSIVE`; both pass = `SUPPORTED_CROSS_OUTCOME`.

## Multiplicity and interpretation lock

- Primary family contains only X2. No threshold, main-only, bonus-only, max/min, weighted, parity, end digit, consecutive, sum, multiple, purchase-mode, period, or other feature search.
- No within-experiment multiplicity adjustment; global permutation is not a decision test.
- PASS may only be described as `Cross-outcome corroboration supported.`
- No causal, birthday-selection-proven, DRAW-probability, official-promotion, or automatic promotion-candidate claim.
- Prospective confirmation or genuinely independent external data remains necessary.

## Preserved state

- OFFICIAL ENGINE: FROZEN
- DRAW_DISCOVERY_PAUSE: ACTIVE
- EXP-017 DRAW: NOT_CREATED
- NO-PICK: UNRESOLVED
- EXP-PRIZE-001 V1/V2/reproduction evidence immutable


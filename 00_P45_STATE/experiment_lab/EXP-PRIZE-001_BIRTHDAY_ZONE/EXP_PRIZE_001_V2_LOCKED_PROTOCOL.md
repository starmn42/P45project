# EXP-PRIZE-001-V2 LOCKED PROTOCOL

## Identity and V1 preservation

- Logical ID: `EXP-PRIZE-001-V2`
- Registry lineage: `EXP-PRIZE-20260816-001-V1` / V2 revision
- Title: `BIRTHDAY-ZONE CONCENTRATION — FIRST-PRIZE SHARE RISK`
- Domain: `PRIZE_SHARE`
- Version: `EXP-PRIZE-001-PROTOCOL-2.0`
- Historical range: rounds `1~1237` only
- Round `1238+`: forbidden from historical analysis
- V1 remains immutable and blocked. V2 changes only source semantics and sold-line conversion.
- Official DRAW engine effect: `NONE`

This experiment measures conditional crowd concentration/prize-sharing risk, never DRAW probability.

## Locked source semantics

- Official result page: `https://www.dhlottery.co.kr/lt645/result`
- Official/internal result endpoint: `https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do`
- `K_r = rnk1WnNope`, bound by the official page under `1등 / 당첨게임 수`.
- `SALES_AMOUNT_r = wholEpsdSumNtslAmt`, the field that the official page binds to its `총판매금액` display.
- `rlvtEpsdSumNtslAmt` is retained for source audit only and is forbidden from the inferential denominator.
- Price per Lotto 6/45 game:
  - rounds `1~87`: `2,000 KRW`
  - rounds `88~1237`: `1,000 KRW`
- `N_r = SALES_AMOUNT_r / PRICE_PER_GAME_r`.
- `N_r` must be a positive integer for every round.
- If official binding, price-boundary evidence, or conversion is not confirmed, stop before outcome analysis.

## Fixed semantic audit

After this protocol is hashed, audit rounds `1,10,87,88,1201,1237` before any hypothesis calculation. Confirm required API fields, positive whole-sales amount, price regime, integer sold lines, main/K consistency, and the 87/88 transition. Preserve official/public evidence for the price boundary and raw payload evidence. Any ambiguity blocks V2.

## Hypotheses and fixed predictor

- `B_r = count(main_i <= 31)` using the main six only; bonus is excluded.
- H1: increasing `B_r` increases `K_r/N_r`.
- H0/opposite: the relationship is zero or negative.
- Centering constant: `6*31/45`.
- Descriptive only: `SHARE_INDEX_r = K_r * 8,145,060 / N_r`.
- The 1~31 boundary is a birthday/date-choice proxy, not proof of buyer intent.

## Frozen data split and completeness

- TRAIN: rounds `1~800`, exactly `800` valid rows.
- CONFIRMATORY HOLDOUT: rounds `801~1237`, exactly `437` valid rows.
- Required: round, six unique main numbers in 1~45, integer `K_r >= 0`, integer positive sales amount, locked price, positive integer `N_r`.
- Rounds must be exactly `1~1237`, duplicate `0`, missing `0`, future `1238+` rows `0`.
- All main numbers must match the canonical P45 draw source.
- No row skipping, range alteration, post-hoc exclusion, or imputation.

## Primary statistic

For every fitted segment:

`log(E[K_r]) = log(N_r) + alpha + beta * (B_r - 6*31/45)`

Poisson log-link is an effect-statistic estimator only; its parametric variance is not primary inference.

### TRAIN direction gate

- Compute `beta_train` on `1~800`.
- If `beta_train <= 0`, stop as `FAILED_EARLY_TRAIN_DIRECTION`.
- HOLDOUT inference and walkforward are forbidden after this early stop.

### Confirmatory HOLDOUT gate

Run only if TRAIN passes:

- Compute `beta_holdout` on `801~1237`.
- Permute `B_r` labels among HOLDOUT rounds, holding `K_r,N_r` fixed.
- Permutations: `100,000`.
- Seed: `2026082101`.
- One-sided p: `(1 + count(beta_perm >= beta_obs)) / 100001`.
- Success requires `beta_holdout > 0` and `p <= 0.05`; otherwise FINAL=`FAILED`.

## Historical block walkforward

Run only after HOLDOUT success. Fixed blocks:

- `801~900`
- `901~1000`
- `1001~1100`
- `1101~1237`

At each block start, fit only rounds preceding the block and freeze parameters:

- ALT: intercept plus centered B, offset `log(N)`.
- NULL: intercept only, offset `log(N)`.
- `DELTA_LL_block = LL_ALT - LL_NULL` on that block.
- `WF_DELTA_LL_TOTAL = sum(DELTA_LL_block)`.
- Pass only if total `>0`.
- HOLDOUT success with WF total `<=0`: `INCONCLUSIVE`.
- HOLDOUT and WF success: `SUPPORTED_WITHIN_EXPERIMENT`.
- No automatic promotion.

## Multiplicity, outcome blindness, and future blocking

- The only V2 predictor is `count(1..31)`; within-experiment multiplicity adjustment is not needed.
- No alternate threshold, feature, subperiod, winner type, or pattern may be explored to rescue V2.
- Protocol hash precedes semantic audit and all hypothesis calculations.
- Historical results stop at 1237. Future results require a separately approved prospective version.

## Status vocabulary

`PROTOCOL_BLOCKED_SOURCE`, `PROTOCOL_BLOCKED_SOURCE_SEMANTICS_V2`, `DATA_BLOCKED_MISSING_REQUIRED_FIELD`, `DATA_BLOCKED_MISMATCH`, `FAILED_EARLY_TRAIN_DIRECTION`, `FAILED`, `INCONCLUSIVE`, `SUPPORTED_WITHIN_EXPERIMENT`.

## Immutable safeguards

- Promotion candidate: `NO` without independent reproduction/prospective confirmation and approval.
- Official engine: `FROZEN`.
- DRAW_DISCOVERY_PAUSE: `ACTIVE`.
- EXP-017 DRAW: `NOT_CREATED`.
- NO-PICK: `UNRESOLVED`.

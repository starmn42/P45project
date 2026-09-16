# EXP-PRIZE-001-V1 LOCKED PROTOCOL

## Identity and boundary

- Logical ID: `EXP-PRIZE-001-V1`
- Registry mapping: `EXP-PRIZE-20260816-001-V1`
- Title: `BIRTHDAY-ZONE CONCENTRATION — FIRST-PRIZE SHARE RISK`
- Domain: `PRIZE_SHARE`
- Version: `EXP-PRIZE-001-PROTOCOL-1.0`
- Official DRAW engine effect: `NONE`
- Historical range: rounds `1~1237` only
- Round `1238+`: forbidden from historical analysis
- Bonus number: excluded
- Exact target: main six-number winning combination

This experiment measures conditional crowd concentration/prize-sharing risk. It does not test or change DRAW probability.

## Source semantics lock

- Primary source page: `https://www.dhlottery.co.kr/lt645/result`
- Primary source API: `https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do`
- `rnk1WnNope`: official first-prize winning game count `K_r`; the official page places it under `1등 / 당첨게임 수`.
- `rlvtEpsdSumNtslAmt`: official relevant-round total sales amount; the official page labels the rendered value `총판매금액` and its script describes it as `해당 회차 판매금액`.
- `N_r = rlvtEpsdSumNtslAmt / 1000`, only when the amount is an exact positive multiple of KRW 1,000.
- If these semantics, units, or exact conversion fail validation, stop as `PROTOCOL_BLOCKED_SOURCE_SEMANTICS`.

## Hypotheses

- `B_r = count(main_i <= 31)`.
- H1: increasing `B_r` increases `K_r / N_r`.
- H0/opposite: the relationship is zero or negative.
- Centering constant: `6*31/45`.
- Descriptive only: `SHARE_INDEX_r = K_r * 8,145,060 / N_r`.

## Frozen split and completeness

- TRAIN: `1~800`, required valid rows `800`.
- CONFIRMATORY HOLDOUT: `801~1237`, required valid rows `437`.
- Required per round: round, six unique main numbers in 1~45, integer `K_r >= 0`, integer `N_r > 0`.
- Missing/duplicate/mismatched rows are not skipped. Any such defect blocks V1.
- Canonical main-number comparison: all rounds `1~1237` must match the P45 canonical draw snapshot.

## Model and primary inference

For each fitted segment:

`log(E[K_r]) = log(N_r) + alpha + beta * (B_r - 6*31/45)`

The Poisson log-link is the statistic estimator only. Parametric Poisson p-values are not inferential evidence.

### TRAIN gate

- Compute `beta_train` on rounds `1~800`.
- If `beta_train <= 0`: stop `FAILED_EARLY_TRAIN_DIRECTION`; do not calculate HOLDOUT inference or walkforward.

### HOLDOUT gate

Only after TRAIN passes:

- Compute `beta_holdout` on rounds `801~1237`.
- Permute `B_r` labels among HOLDOUT rounds while holding `K_r,N_r` fixed.
- Permutations: `100,000`.
- Seed: `2026082101`.
- One-sided p: `(1 + count(beta_perm >= beta_obs)) / 100001`.
- Success requires `beta_holdout > 0` and `p <= 0.05`; otherwise FINAL=`FAILED`.

## Historical block-walkforward

Run only after HOLDOUT success. Fixed blocks:

- `801~900`
- `901~1000`
- `1001~1100`
- `1101~1237`

At each block start, fit using rounds strictly before the block:

- ALT: offset `log(N)` plus intercept and centered `B`.
- NULL: offset `log(N)` plus intercept only.
- Freeze parameters throughout the block.
- `DELTA_LL_block = LL_ALT - LL_NULL`.
- `WF_DELTA_LL_TOTAL = sum(DELTA_LL_block)`.
- WF passes only when total is greater than zero.
- HOLDOUT success with WF total `<=0` gives FINAL=`INCONCLUSIVE`.
- HOLDOUT and WF success gives `SUPPORTED_WITHIN_EXPERIMENT`, never automatic promotion.

## Outcome blindness and ordering

1. Lock this protocol and its SHA-256.
2. Only afterward ingest K, sales, and main-number outcomes.
3. Validate immutable rounds `1~1237` snapshot and hash.
4. Evaluate TRAIN direction.
5. Only if allowed, evaluate HOLDOUT permutation.
6. Only if allowed, evaluate block walkforward.
7. Preserve negative/blocking results without retuning.

No 1~30/1~32 variants, subperiod selection, alternate patterns, result-driven exclusions, threshold changes, or DRAW-engine connections are permitted in V1.

## Prospective reserve

The first not-yet-published draw after protocol lock is reserve only. Reserve outcomes are excluded from this historical judgment. A separate approved prospective experiment/version is required even if V1 is supported.

## Status vocabulary

`PROTOCOL_BLOCKED_SOURCE`, `PROTOCOL_BLOCKED_SOURCE_SEMANTICS`, `DATA_BLOCKED_MISSING_REQUIRED_FIELD`, `DATA_BLOCKED_MISMATCH`, `FAILED_EARLY_TRAIN_DIRECTION`, `FAILED`, `INCONCLUSIVE`, `SUPPORTED_WITHIN_EXPERIMENT`.

## Immutable safeguards

- Promotion candidate: `NO` unless separately reproduced/confirmed and separately approved.
- Official engine: `FROZEN`.
- DRAW_DISCOVERY_PAUSE: `ACTIVE`.
- EXP-017 DRAW: `NOT_CREATED`.
- NO-PICK: `UNRESOLVED`.

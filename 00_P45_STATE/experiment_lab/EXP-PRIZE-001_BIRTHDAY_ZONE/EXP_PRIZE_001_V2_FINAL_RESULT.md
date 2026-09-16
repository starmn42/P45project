# EXP-PRIZE-001-V2 FINAL RESULT

- STATUS: `SUPPORTED_WITHIN_EXPERIMENT`
- FINAL_JUDGMENT: `SUPPORTED_WITHIN_EXPERIMENT`
- PROMOTION_CANDIDATE: `NO`
- PROTOCOL_VERSION: `EXP-PRIZE-001-PROTOCOL-2.0`
- PROTOCOL_SHA256: `479c83f5905d1bcd928e5b388420a41259c413836711202fd30704e7b4b9d5b7`
- DATA_RANGE: `1~1237`
- DATA_SHA256: `86b14968aca3ad10b854f9d5c53eba00a786627f73e353938e1e801dc888fa21`
- ROUND_1238_PLUS_USED: `NO`

## Source and conversion

- Official source: Donghaeng Lottery result page/internal JSON endpoint.
- Total-sales field: `wholEpsdSumNtslAmt`.
- Forbidden inferential denominator: `rlvtEpsdSumNtslAmt`.
- Rounds 1~87: `2,000 KRW/game`.
- Rounds 88~1237: `1,000 KRW/game`.
- Fixed semantic audit: `PASS`.
- Integer sold-line conversion: `1237/1237 PASS`.
- Canonical main-number comparison: `1237/1237 PASS`.
- Missing/duplicate/future rows: `0/0/0`.

## Locked analysis

- TRAIN beta: `0.01432804646661183`.
- TRAIN gate: `PASS`.
- HOLDOUT beta: `0.040262627684254704`.
- Multiplicative effect per additional birthday-zone number: `1.0410841558129813`.
- HOLDOUT one-sided permutation p: `0.01999980000199998`.
- Permutations: `100,000`.
- Seed: `2026082101`.

Walkforward block delta log-likelihood:

|Block|Delta LL|
|---|---:|
|801~900|0.7178853096791045|
|901~1000|0.6662083655314746|
|1001~1100|1.6408221686568254|
|1101~1237|0.44557742872586914|

- WF_DELTA_LL_TOTAL: `3.4704932725932736`.
- WF gate: `PASS`.

## Interpretation boundary

Within this single pre-registered experiment, more main numbers in 1~31 were associated with a higher sales-adjusted first-prize winning-game rate. This is evidence about conditional crowd concentration/prize-sharing risk, not a change in number-draw probability. It does not prove that individual buyers used birthdays, does not authorize DRAW scoring or recommendation changes, and is not automatically a promotion candidate.

Independent reproduction or separately approved prospective confirmation is required before promotion review. V1 remains immutable as `PROTOCOL_BLOCKED_SOURCE_SEMANTICS` evidence.

## Reproducibility and protection

- Identical full analysis rerun result SHA-256: `cd5529c36fc83213e6efb8ddc9b1010c2ab7c1a5f82c31f7e00d927c3aae8397`.
- Future leakage: `0`.
- Official engine changed: `NO`.
- DRAW_DISCOVERY_PAUSE: `ACTIVE`.
- EXP-017 DRAW: `NOT_CREATED`.
- NO-PICK: `UNRESOLVED`.

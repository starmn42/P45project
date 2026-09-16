# EXP-PRIZE-001-V1 BLOCKED RESULT

- STATUS: `PROTOCOL_BLOCKED_SOURCE_SEMANTICS`
- PROTOCOL_VERSION: `EXP-PRIZE-001-PROTOCOL-1.0`
- PROTOCOL_SHA256: `38d6059a52ac5af59d94b964774f2c4430fae8a5167740c409031224e25ef1b7`
- OUTCOME_ANALYSIS_STARTED: `NO`
- BACKTEST_STARTED: `NO`
- HISTORICAL_RANGE_REQUESTED: `1~1237`
- ROUND_1238_PLUS_USED: `NO`
- OFFICIAL_ENGINE_CHANGED: `NO`

## First blocking discrepancy

The locked V1 protocol assigned the displayed official total-sales amount to API field `rlvtEpsdSumNtslAmt`.

The preserved official result page instead renders:

`$("#rlvtEpsdSumNtslAmt").text(cmmUtil.addComma(data.wholEpsdSumNtslAmt) + "원");`

The same page labels this rendered value `총판매금액` and comments that it is the applicable round's sales amount. Therefore the page's official display semantics point to `wholEpsdSumNtslAmt`, while the already locked V1 protocol points to `rlvtEpsdSumNtslAmt`. Recent official payloads contain both fields with materially different values.

Changing the locked field after seeing the source payload would violate the outcome-blind lock and the explicit no-retuning rule. No substitution, conversion, backtest, TRAIN beta, HOLDOUT statistic, permutation, or walkforward was performed.

## Required next action

A separately approved V2 protocol must be authored and locked before outcome analysis. It must explicitly identify the official total-sales field and preserve the original V1 as blocked evidence. V1 must not be silently amended or reused.

## Preserved boundaries

- DRAW_DISCOVERY_PAUSE remains `ACTIVE`.
- EXP-017 DRAW remains `NOT_CREATED`.
- NO-PICK remains `UNRESOLVED`.
- Official P45 engine remains `FROZEN`.
- PRIZE_SHARE remains separated from DRAW probability and recommendation gates.

# EXP-PRIZE-PROSPECTIVE-001 V1 LOCKED_PROTOCOL

## Lock identity

- Logical ID: `EXP-PRIZE-PROSPECTIVE-001-V1`
- Domain: `PRIZE_SHARE`
- Title: `BIRTHDAY-ZONE CROWD CONCENTRATION — PROSPECTIVE CONFIRMATION`
- Lock timestamp: `2026-08-21T20:35:44.0250684+09:00`
- Latest officially published round at lock: `1237`
- START_ROUND: `1238`
- START_ROUND result published at lock: `NO`
- Stage 1 end: `1289`
- Final end: `1341`
- This is not DRAW research and does not modify the official engine.

## Fixed research question and roles

PRIMARY asks whether, in future consecutive rounds, the mean count of numbers 1~31 across the six exact second-prize ticket combinations is positively associated with the total second-prize winning-game count after conditioning on sold lines.

- PRIMARY outcome: official second-prize winning games, `rnk2WnNope`.
- PRIMARY predictor: X2 defined below.
- SECONDARY: first-prize winning games, directional corroboration only; it cannot rescue or promote PRIMARY.
- The 1~31 boundary is a birthday/date-choice proxy, not direct evidence of purchaser intent, causality, or DRAW probability.

## Locked predictor and outcome

For future round r:

- `m_r = count(main_i <= 31)` among the six main numbers.
- `b_r = 1` if bonus <=31, otherwise 0.
- `X2_r = (5*m_r + 6*b_r)/6`.
- `MU_B = 6*31/45`.
- `Z2_r = X2_r - MU_B`.
- `K2_r = rnk2WnNope`.
- total sales = `wholEpsdSumNtslAmt`.
- game price = 1,000 KRW.
- `N_r = wholEpsdSumNtslAmt/1000`.
- PRIMARY offset = `log(6*N_r)`.
- PRIMARY model: `log(E[K2_r]) = log(6*N_r) + alpha + beta2*Z2_r`.
- PRIMARY effect = beta2; effect per +1 X2 = exp(beta2).
- Poisson parametric p-values are not PRIMARY inference.

H1 is beta2 > 0. H0/opposite is no positive association, beta2 <= 0.

## Fixed prospective sample and inferential looks

The sequence contains consecutive official rounds beginning at 1238. No retrospective inclusion is permitted.

### Stage 1

- N = 52, rounds 1238~1289.
- Four consecutive 13-round blocks.
- Permute Z2 labels only within each block; K2 and N remain attached to their rounds.
- 200,000 permutations; seed 2026082105.
- one-sided `p1=(1+count(beta_perm>=beta_obs))/200001`.
- Early confirmation requires beta2_stage1 >0 and p1 <=0.01.
- Success status: `PROSPECTIVE_PRIMARY_CONFIRMED_EARLY`.
- Otherwise status is `STAGE1_CONTINUE_TO_FINAL`, not failure; no rule change is allowed.

### Stage 2 final

- N = 104 cumulative, rounds 1238~1341.
- Eight consecutive 13-round blocks.
- 200,000 within-block permutations; seed 2026082106.
- one-sided `p2=(1+count(beta_perm>=beta_obs))/200001`.
- Confirmation requires beta2_final >0 and p2 <=0.04.
- Success: `PROSPECTIVE_PRIMARY_CONFIRMED`; otherwise `PROSPECTIVE_NOT_CONFIRMED`.
- No automatic extension, retuning, alternative cutoff, or additional look.

The two-look union-bound alpha upper limit is 0.01+0.04=0.05.

## Locked SECONDARY first-prize analysis

- `B1_r = count(main_i <=31)`.
- `K1_r = rnk1WnNope`.
- offset `log(N_r)`.
- model `log(E[K1_r]) = log(N_r) + alpha1 + beta1*(B1_r-6*31/45)`.
- It may be calculated only at an allowed PRIMARY look.
- Same 13-round blocks; 100,000 permutations.
- Stage 1 seed 2026082107; final seed 2026082108.
- Secondary p-values are descriptive/supportive and do not alter PRIMARY alpha or status.

## Peeking, multiplicity, and research-degree lock

- Before all 52 Stage-1 rounds are officially published: no beta, p-value, signal plot, effect direction, outcome trend, subgroup, or partial signal summary.
- Before an allowed look, only source availability, row count, missing/duplicate, schema, hash, and integrity may be checked.
- Predictor family is exactly X2. Alternative birthday cutoffs, main-only, bonus-only, max/min, weighted variants, parity, end digit, consecutive numbers, sum, purchase mode, channel, season, sales subgroup, period selection, block change, sample-size change, or alpha redistribution are prohibited.
- Historical effect proximity cannot rescue a failed prospective gate.
- START_ROUND or later outcomes must never be merged back into historical EXP-PRIZE-001/002.

## Data ledger lock

For each future round, append-only evidence must eventually record round, main six, bonus, rnk2WnNope, rnk1WnNope, wholEpsdSumNtslAmt, retrieval timestamp, source endpoint/schema, and batch hash.

- Existing rows cannot be edited.
- Corrections are new records that preserve and link the original.
- No outcome-derived signal fields are stored before an allowed look.
- This lock creates only a zero-row manifest/schema. It does not retrieve or create future outcome rows.
- Existing updater and scheduler are unchanged.

## Interpretation and protection

- Even a PASS is not causality, direct birthday-choice proof, DRAW signal, official promotion, or automatic promotion candidate.
- Separate program-level promotion review remains required.
- OFFICIAL ENGINE remains FROZEN.
- DRAW_DISCOVERY_PAUSE remains ACTIVE.
- EXP-017 DRAW remains NOT_CREATED.
- NO-PICK remains UNRESOLVED.
- EXP-PRIZE-001/002 locked, result, and reproduction evidence remains immutable.


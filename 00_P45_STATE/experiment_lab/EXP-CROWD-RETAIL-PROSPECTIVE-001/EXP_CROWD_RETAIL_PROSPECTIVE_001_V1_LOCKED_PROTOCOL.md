# EXP-CROWD-RETAIL-PROSPECTIVE-001-V1 — LOCKED PROTOCOL

- Lock timestamp: `2026-08-24T10:53:59+09:00`
- Latest official published round at lock: `1238`
- START round: `1239`
- START result published at lock: `NO`
- Evidence class: `PROSPECTIVE_CONFIRMATION`
- Title: `PROSPECTIVE MANUAL SAME-RETAILER JACKPOT COLLISION`
- Historical frozen base: rounds `262~1237`, SHA-256 `854ca7256219eadf574ac32ad256b84e9a5bfa42ceece09f0a09dd1eed79cd50`
- Round 1238 is excluded from analysis, propensity history, nuisance fitting and signal inspection because it was published before this lock.
- Known regime marker: `ROUND_1238`; it is not a predictor, split rule or threshold input.

## Population and identity

Future rounds 1239+, first-prize winner rows, offline physical retailers, AUTO/MANUAL only. SEMIAUTO and the official online channel are excluded. Retailer identity uses official stable retailer ID first, otherwise exact normalized official name plus address. Fuzzy matching is forbidden.

## Primary

For each round and retailer, count a cell when at least two first-prize winner rows are MANUAL. Cumulative `S_CELL` is the sole PRIMARY statistic. H1 is positive excess over the locked null; the opposite is excess <= 0.

## Frozen nuisance model

- alpha: `2.3854957135043726`
- beta: `5.04582203071465`
- prior mean: `0.3210057483223752`
- prior concentration: `7.431317744219022`
- initial histories: eligible rows 262~1237 only

Before future round R, propensity uses only historical 262~1237 and completed prospective rounds 1239~R-1. Round R updates history only after its raw record is complete. Alpha/beta are never re-estimated.

## Conditional null

Fix actual retailer slot multiplicities, actual round manual total, and pre-round retailer propensities. Conditional subset probability is proportional to the product of slot odds. Exact conditional Bernoulli sampling uses elementary-symmetric-polynomial dynamic programming. PPS, simple weighted without replacement and Wallenius approximations are forbidden.

## Sequential design

- Stage 1: rounds `1239~1290`, 52 rounds, alpha `0.01`, 500,000 repetitions, seed `2026082401`.
- Stage 1 exposure: duplicate-capable cells >= 10 and expected S_CELL >= 3. Otherwise `STAGE1_NO_DECISION_LOW_EXPOSURE`, with no p-value.
- Final: rounds `1239~1342`, 104 rounds, alpha `0.04`, 500,000 repetitions, seed `2026082402`.
- Final exposure: duplicate-capable cells >= 20 and expected S_CELL >= 5. Otherwise `PROSPECTIVE_INCONCLUSIVE_LOW_EXPOSURE`.
- Early success requires exposure PASS, positive excess, p <= .01 and deterministic rerun. Final success similarly uses p <= .04.
- Sample size, boundaries, thresholds, null, primary and seeds may not change after results. Any change requires V2.

## Signal blindness

Before an approved stage analysis, no S_CELL, expected S_CELL, excess, enrichment, p-value, trend, collision plot, signal direction, propensity summary tied to signal, or same-store manual multiplicity summary may be computed or displayed. Raw source fields are stored solely for later approved analysis. Collector output is limited to availability, captured rounds, raw row counts, schema consistency, source hashes, correction/version status and operational status.

## Raw ledger

Append-only, official-source-only storage begins at round 1239. Equal hashes produce `NO_WRITE`; changed official payloads append a correction/version record without deleting originals. Network, source, lock or schema failures produce fail-safe no-write. Existing updater and PRIZE prospective records are isolated.

## Interpretation and protection

Even prospective success does not identify a person or causal mechanism, imply manipulation, affect DRAW probability, generate recommendations, establish novelty, or create a promotion candidate. Official P45 remains FROZEN and DRAW_DISCOVERY_PAUSE remains ACTIVE.

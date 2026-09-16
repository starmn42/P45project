# P45 DRAW SOURCE-OF-TRUTH NORMALIZATION + 1239 SETTLEMENT RESULT 001

## Final

- FINAL_VERDICT: `DRAW_SOURCE_TRUTH_1_1239_NORMALIZED_AND_SETTLED`
- CANONICAL_DRAW_RANGE / ROWS: `1..1239 / 1239`
- MISSING / DUPLICATE: `0 / 0`
- CSV_SQLITE_EQUAL: `YES`
- FUTURE_LEAKAGE: `0`

## Root cause

Round 1238 authoritative data existed and was verified. The validated `1..1238` artifact was intentionally created under an audit job whose explicit change control was `Official source / DB changes = 0 / 0`. Its report labels the file a contiguous staging snapshot and records the first 1,237 rows as exactly equal to live. Therefore live remaining at 1237 was the expected consequence of a staging-only, no-live-write task, not loss of round 1238.

## Authoritative procedure and observed updater boundary

- launcher: `00_PROJECT_CONTROL/TOOLS/P45 회차 업데이트.cmd`
- module: `src/p45_v27/draw_update.py`
- official endpoint: `https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do?srchDir=center&srchLtEpsd={round}`
- parser: `parse_official`; validation: `validate_draw`; updater: `run_update`
- provenance fields: `source_url`, raw-payload SHA-256, `fetched_at` in SQLite `draw_result`

The approved 1238 row was passed through `run_update` and committed successfully. The next 1239 run verified the preserved official payload with the same parser, but failed while constructing the unrelated next-round analysis snapshot because lifecycle history lacked `a_integrated_hits`. This failure occurred before the 1239 draw transaction committed. No engine code, gate, threshold, signature, or semantics were changed. The authorized draw-result-only normalization then inserted the verified 1239 row, backfilled SQLite rounds 1..1235 from the existing official raw bundle, and atomically published the already-validated canonical CSV.

## Provenance

- 1238: `2026-08-22 / 2,13,18,32,38,42 / BONUS 22`
- approved 1238 payload SHA-256: `99d44e493a357785f976e37d99b1e0d2ae179b161cc1aa4a5665f9606ec0c119`
- approved staging SHA-256: `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- 1238 provenance: `PASS`
- 1239: `2026-08-29 / 11,13,22,32,33,36 / BONUS 8`
- 1239 raw payload SHA-256: `4c0c600801ddeef24d98b54206bac807eaf623c7031bac35c035d4892d6c109a`
- 1239 canonical row SHA-256: `86055d9da5ae5bbefd17cb52d1f9b7232184d1df7a2430b3f172a78b732b445d`
- 1239 provenance: `PASS`

## Canonical stores

- canonical audit CSV: `v27_storage/audits/draw_source_truth_normalization_1239_001/CANONICAL_DRAW_1_1239.csv`
- canonical/live CSV SHA-256: `56748e0192252706d2cf90c6306aff9b8c6c88381a90624c27f4fb23713ca27c`
- live SQLite SHA-256: `fc8d4fcd364520480121cd629499b706915ba1abd6425bc2676706e754fdc20e`
- baseline 1..1237 exact equality: `PASS`
- CSV and SQLite round/date/MAIN6/bonus equality across all 1,239 rounds: `PASS`

## Source-of-truth operating rule

- canonical live draw CSV is `v27_storage/live/p45_live_draws.csv`.
- canonical draw-result database is `v27_storage/live/p45_new_draw_update_v1.sqlite3`, table `draw_result`.
- staging/audit snapshots are validation evidence, not canonical live stores.
- a staged new draw reaches live only after provenance, structural validity, contiguity, baseline equality, backup, and CSV–SQLite equality checks pass.
- latest canonical max is checked with the final CSV round and `SELECT MAX(draw_round) FROM draw_result`.
- synchronization is checked by comparing every round's date, six MAIN numbers, and bonus across both stores.

## 1239 sealed settlement

- sealed SHA before/after: `ed23691c5b9f1715c85b6d3362735dfa8cebb72b31dc258e2aa43bc299c94ead / same`
- Fixed PRIMARY 3/3: `0`
- Fixed SUPPORT exact 2/3: `1`
- Linked PRIMARY 3/3: `0`
- Linked SUPPORT exact 2/3: `0`
- historical/prospective combination: `NO`
- KTS/rule regeneration: `0`

## LZ76 and protection

- LZ76: `FAILED_NOT_SUPPORTED`; p1 `0.014598540145985401` PASS; p2 `0.43745625437456254` FAIL; joint `NO`; reproducibility `PASS`; future leakage `0`.
- Research Master 003 non-EXP executed axes: `28`.
- Evidence Inventory 002 contains the 16 actual LZ76 files; Inventory 001 is preserved.
- Formal Registry SHA-256: `a4eba0de3e5045d966b068e76d466a574be01bb02ec2f35801af9712f7bc4b8a`; rows `68`, unchanged.
- latest numbered experiment: `EXP-020`.
- Official Engine: `FROZEN / UNCHANGED`.

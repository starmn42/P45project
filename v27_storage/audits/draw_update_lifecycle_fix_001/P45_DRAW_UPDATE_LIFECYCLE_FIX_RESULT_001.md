# P45 DRAW UPDATE LIFECYCLE FIX RESULT 001

## Final verdict

`FIXED_AND_REGRESSION_VERIFIED`

## Symptom and exact failure path

The 1239 updater path completed official acquisition, parsing, validation, and evaluation loading. It failed before the 1239 draw transaction while building the next-round snapshot:

`run_update → build_next_snapshot → ProductionPairPipeline.build_prediction_context → restore_lifecycle_gate_data → materialize_historical_lifecycle → _primary → KeyError('a_integrated_hits')`

The earlier normalization subsequently stored the verified 1239 draw independently. This work did not reinsert it.

## Confirmed root cause and field meaning

- classification: `PAIR_REPAIR_COMPATIBILITY_GAP`
- `a_integrated_hits` is the count, 0..3, of member set A against MAIN6+BONUS. Its B counterpart and the MAIN-only A/B counts are official historical outcome inputs used to keep PRIMARY and exact-2/3 SUPPORT separate.
- It is not obsolete and is not a nullable diagnostic default. `wf_outcome` contains all four canonical hit columns for 258 historical rows.
- Official repair additionally reconstructs `representative_conflict` from locked `rank_key_json[8][1]` before lifecycle materialization.
- The operational updater loaded the canonical DB rows but appended its newest evaluated outcome using compact keys `ia/ib/ma/mb`, and did not restore `representative_conflict`. It therefore mixed two structures in one lifecycle history.

## Minimal code change

- modified: `src/p45_v27/draw_update.py`
- before SHA-256: `0e9d3ce56cebae9b04ca93ead8ec7712b96be5916811f8df63e78d2ae46efa60`
- after SHA-256: `e3c0d0a406cbe78b5f5d1159a1148d82242d2e96036fdae94004a5dcafbcfea6`
- added a strict outcome-shape normalizer; compact updater keys map to their exact canonical counterparts.
- historical conflict is reconstructed with the same locked rank-vector rule used by the repair.
- missing required values raise `PAIR_LIFECYCLE_OUTCOME_SCHEMA_INVALID`; no zero/null/skip/try-except fallback was added.
- current production conflict input remains the locked `conflict_columns=0`; it is recorded explicitly, not inferred from outcome.
- canonical CSV/SQLite equality and continuity are checked before acquisition. Divergence raises `STOP_DRAW_SOURCE_OUT_OF_SYNC` before the fetcher is called.
- canonical CSV materialization now writes the full SQLite draw sequence once, preventing baseline duplication after SQLite became a complete 1..N store.

## Tests

- new regression: `tests_v27/test_draw_update_lifecycle_compat.py`
- CASE 1 canonical lifecycle shape: PASS
- CASE 2 compact updater shape: PASS
- CASE 3 repair storage shape without materialized conflict: PASS; locked rank restores it
- CASE 4 truly damaged shape: PASS; explicit failure
- source mismatch before fetch: PASS
- no-new-draw preserves draw rows: PASS
- existing pair-shadow-repair tests: `5/5 PASS`
- Python compilation: PASS

## 1239 post-update recovery

- used existing canonical round 1239; acquisition and draw insertion were not repeated.
- evaluations restored: `22`
- analysis snapshot: `1240`, source end `1239`
- status: `LIVE_ANALYSIS_READY`
- valid_for_core: `0`
- prediction hash: `3b9447dca2d579cc47bebe08c2e83129757a766d987ec59c89369423734a4fc2`
- prior draw_result rows: exact equality before/after `PASS`
- prior snapshots through 1239: exact equality `PASS`
- prior evaluations through 1238: exact equality `PASS`

## No-new-draw live-clone test

- official 1240 lookup result: no target row
- updater result: `DRAW_ALREADY_CURRENT`
- CSV unchanged: YES
- SQLite file unchanged: YES
- draw_result unchanged: YES
- rows/duplicates: `1239 / 0`
- snapshot 1240 preserved: YES
- SQLite integrity / FK: `ok / 0`

## Protection

- canonical draw range: `1..1239`
- live CSV SHA-256: `56748e0192252706d2cf90c6306aff9b8c6c88381a90624c27f4fb23713ca27c`
- live SQLite after post-update recovery SHA-256: `c4e131a47518c54ddc7c2a50b21bdaa95ae102743aac64da5b6ebf63723a7404`
- draw_result content changed: `NO`
- live SQLite file SHA changed only because the missing 22 evaluations, snapshot 1240, and recovery run record were added.
- Official semantics / gate / threshold / signature changes: `0 / 0 / 0 / 0`
- Fixed / Linked / KTS45 / sealed prospective changes: `0 / 0 / 0 / 0`
- formal Registry: `68`, unchanged
- latest numbered EXP: `EXP-020`
- future leakage: `0`

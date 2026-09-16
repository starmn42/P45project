# WHOLE-ENGINE SYNTHETIC REPLAY SEMANTICS SPEC 001

Status: `LOCKED_BEFORE_REBUILD`

## Authority and scope

This specification does not add a lifecycle rule. It records the single lifecycle already applied to the frozen Official Engine by `official_repair_apply_001` and the strict history adapter subsequently verified by `draw_update_lifecycle_fix_001`.

- Draw boundary for target `R`: canonical rows `1..R-1` only.
- UNIT/NUMBER: recompute from that draw prefix through the current frozen diagnostics path.
- TRIO: run the existing resumable walk-forward from target 43 through 1235. Before each target, construct candidates from `1..R-1`; persist representative-signature exposure only after the prediction hash is locked; then attach the target outcome. Synthetic histories use the same operation in the same order.
- PAIR: run the existing `ProductionPairPipeline` and `PairWalkforwardRunner` from target 43 through 1235 against the rebuilt TRIO database. PAIR prediction receives only prior PAIR outcomes (`evaluation_round < R`).
- PAIR lifecycle: materialize the already-defined prior-outcome evidence, recent-support state, structure state, risk and existing gate inputs using `pairs/lifecycle_v12.py::materialize_historical_lifecycle` and `restore_lifecycle_gate_data`; then use the existing `decide_state` path. No gate, threshold, signature, ranking, scoring or recommendation rule is changed.
- PAIR outcome schema: canonical fields are `a_integrated_hits`, `b_integrated_hits`, `a_main_hits`, `b_main_hits`; `representative_conflict` is deterministically recovered from the locked representative rank vector at index 8 (`rank_key_json[8][1] > 0`), exactly as in the approved repair and updater compatibility fix.
- Empty/insufficient histories use the existing code-defined states and baselines. No null-specific fallback is permitted.
- Outcome access occurs only after the pre-result prediction is persisted. Future leakage must remain zero.
- Rebuild identifiers and timestamps are storage metadata, not semantic state. Comparison excludes UUIDs, timestamps, cache/code/source file hashes and hashes that recursively include those storage identifiers. All deterministic domain fields, candidate/selection identities, gate vectors, lifecycle inputs, NUMBER/TRIO/PAIR/CORE stop decisions and target statuses must match.

## Canonical equivalence acceptance

- exact valid targets: `369..1235`, count `867`
- `OUTPUT_AVAILABLE = 0`
- `NO_PICK = 867`
- target-by-target stop gate: exact match
- deterministic NUMBER/TRIO/PAIR/CORE relevant state: exact match after the metadata exclusions above
- protected Official files: byte hashes unchanged

Any mismatch yields `SEMANTICS_REBUILD_NOT_EQUIVALENT`. The EXP-035 B=2000 simulation is outside this work and must remain unexecuted.

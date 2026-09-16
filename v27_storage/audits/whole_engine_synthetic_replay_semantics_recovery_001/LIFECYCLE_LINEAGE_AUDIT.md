# WHOLE-ENGINE SYNTHETIC REPLAY LIFECYCLE LINEAGE AUDIT

## Historical semantics

The historical PAIR database was built with placeholder lifecycle evidence. At target 662, candidate `10-13-27__14-17-43` has exposure 100, `integrated_primary_evidence=null`, `main_primary_evidence=null`, PG07/PG08 `INCOMPLETE`, and `PAIR_SYSTEM_HOLD`.

## Repair semantics

`pair_shadow_repair_001` reconstructed prior-outcome evidence and `representative_conflict` from the locked representative rank vector. `official_repair_phase_a_b_001` validated that path, and `official_repair_apply_001/OFFICIAL_APPLY_REPORT.json` records `official_repair_applied=true` for `pairs/lifecycle_v12.py` and `pairs/production.py`, with unexpected Official file and DB changes both zero. `draw_update_lifecycle_fix_001` subsequently fixed the operational history adapter to normalize canonical hit fields and recover conflict from `rank_key_json[8][1] > 0`.

## Current authoritative semantics

The approved repair code is the single current forward semantics; no new lifecycle rule is needed. However, the authoritative historical PAIR DB was explicitly not rewritten by that repair. In addition, the generic `PairWalkforwardRunner._history` query still omits `rank_key_json`/`representative_conflict`; the audit-only adapter used the already-approved locked-rank recovery without modifying Official code.

## Determination

- feasibility verdict: `SEMANTICS_RECOVERED_EXISTING`
- rebuild equivalence verdict: `SEMANTICS_REBUILD_NOT_EQUIVALENT`
- reason: current repaired forward semantics cannot reproduce the retained historical placeholder PAIR state target-by-target.
- new semantics added: `NO`
- rule adjustment after observing results: `NO`


# PAIR REPAIR SPECIFICATION 001

REPAIR_SPECIFIABLE = `YES`

CLASSIFICATION = `ORIGINAL_RULE_IMPLEMENTATION_RECOVERY`

This is a design specification only. It authorizes no official or shadow execution.

## Minimum repair components

1. Add a historical metric materializer called by `ProductionPairPipeline` before gate evaluation.
2. Inputs: official prior `wf_selection_exposure` joined to `wf_outcome`, keyed by v1.2 base rule signature, restricted to evaluation_round < r; pre-result member/unit context from the existing production pipeline.
3. Outputs: four endpoint period ledgers, stat-test records/evidence labels, recent state, bonus dependence, pair rule/final risk, pair rule/final structure, sample-band and provenance hashes.
4. Calculation time: after candidate/signature formation and prior-history lookup, before PRELOCK/gates and before outcome r access.
5. Replace placeholder gate inputs only with deterministic materialized values; do not alter PG predicates or thresholds.
6. Route the completed official gate vector through existing `decision.decide_state()` (or an exactly single-source equivalent) so SYSTEM_HOLD→RESEARCH_HOLD→READY→TEST_READY is honored.
7. TEST_READY conditions are exactly Gate Amendment §11.4/11.4.1; no output-driven relaxation.
8. Warm-up: `<50` RESEARCH_HOLD; `50..199` may at most TEST_READY; `<200` evidence label remains INSUFFICIENT where canonical statistic requires it. Missing required input is SYSTEM_HOLD, not a fabricated value.
9. Future block: contract V1, source_end_round r-1, selection outcomes strictly <r, outcome r accessed after finalization only.
10. Determinism: canonical input/exposure-ID list and payload JSON hash, 10-run equality, rollback/resume equality.
11. Persistence namespace for a future prototype: new shadow-only DB and run ID; never overwrite official v1.2 raw evidence, active CORE/AUDIT, or live update DB.
12. Verification before any replay: lock this specification, implementation code hash, schema hash, source hash, and expected invariants. Then run a separately approved shadow prototype and compare without changing official state.

## No canonical changes required

- Gate change: NO
- Threshold change: NO
- Signature change: NO
- State vocabulary change: NO
- Outcome definition change: NO
- Historical evidence definition change: NO


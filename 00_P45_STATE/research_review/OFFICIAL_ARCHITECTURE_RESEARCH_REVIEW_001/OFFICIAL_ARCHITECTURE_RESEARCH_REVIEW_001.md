# P45 OFFICIAL ARCHITECTURE RESEARCH REVIEW 001

STATUS = `ARCHITECTURE_REPAIR_SPECIFIABLE`

## Scope and baseline

- Review mode: read-only architecture review; no official implementation, DB, gate, threshold, signature, output, or Experiment change.
- Baseline: state `1.0.85`, decision `DECISION-20260824-092`, registry physical rows `62`.
- Input root cause: `NO_PICK_ROOT_CAUSE = IMPLEMENTATION_OR_DEFINITION_ANOMALY`.
- Baseline evidence: 867 valid rounds; NUMBER/TRIO/PAIR shadow availability 763/271/258; 148,215 raw PAIR candidates in 258 rounds; official CORE/output 0.

## Findings

1. The canonical PAIR amendment defines the four state precedence, PG01–PG14, evidence labels inherited from TRIO, selection-exposure bands (`<50`, `50..199`, `>=200`), recent100/recent50 support collapse, and both TEST_READY paths.
2. `production.py` calculates historical integrated/main primary rates from prior selection exposures, but explicitly passes both evidence fields as `None` and `recent_state` as `INSUFFICIENT_SAMPLE` for every candidate.
3. `trio_engine.statistic()` and `final_aggregation.aggregate()` contain the exact Wilson/binomial evidence primitive and a current-round materialization implementation. There is no per-historical-round materializer connected to `ProductionPairPipeline`.
4. `decision.decide_state()` implements canonical TEST_READY logic. `lifecycle_v12.build_official_prediction_audit()` does not call it; it independently returns only SYSTEM_HOLD, READY, or RESEARCH_HOLD. Thus TEST_READY is implemented but unreachable through the actual walk-forward/live lifecycle.
5. PG01 is independently and correctly defined as “both member TRIOs are TRIO_PASS.” Its 100% FAIL is caused by the actual member states, not by the missing evidence. That FAIL is allowed on canonical TEST_READY path A; the lifecycle omission prevents that intended route.
6. PG07/PG08 are INCOMPLETE because their required evidence labels are explicitly supplied as `None`, not because the observed rates are absent.
7. The same `ProductionPairPipeline` is called by walk-forward, current diagnostic/final aggregation context building, and `draw_update.py`; therefore the live/current path shares the anomaly unless a caller post-materializes all metrics (only final aggregation currently does so for round 1236).

## Required questions

1. `integrated_primary_evidence=None`: direct cause is the literal `None` assignment in `ProductionPairPipeline.build_prediction_context`; no historical statistic materializer is invoked.
2. `main_primary_evidence=None`: same direct cause for MAIN PRIMARY.
3. `recent_state=INSUFFICIENT_SAMPLE`: literal fixed value in the production gate payload; prior exposure windows are not evaluated there.
4. PG01 100% FAIL: an intended gate result from non-PASS member TRIO states, not a derivative of missing evidence. What is anomalous is the missing TEST_READY lifecycle route.
5. PG07/PG08 100% INCOMPLETE: both require non-null rate, baseline, and evidence; evidence is always null.
6. PAIR_TEST_READY canonical existence: YES, Gate Amendment §11.4/11.4.1.
7. Historical materialization builder: `PARTIAL_CURRENT_ONLY`; generic statistic/recent primitives and final-current aggregation exist, but no per-r producer is connected to walk-forward/live production.
8. Why not executed: `production.py` supplies placeholders and `lifecycle_v12.py` bypasses `decide_state()`.
9. Canonical specification sufficiency: YES for PRIMARY evidence, recent state, sample bands, gates, and state transition.
10. Repair without gate/threshold change: YES.
11. Research legitimacy of replay: YES only if the repair specification is locked before replay and every target r uses selection exposures/outcomes strictly before r.
12. Classification: implementation recovery of existing official rules, not a new research rule.
13. Live/current affected: YES; it calls the same production lifecycle.
14. Prior 0/867: retain raw stage availability/count facts; suspend PAIR gate-performance, CORE conversion, and end-to-end no-pick rate as evidence of intended canonical behavior.

## Architecture classification

| Item | Classification | Basis |
|---|---|---|
| integrated primary evidence definition | DEFINED_BUT_NOT_IMPLEMENTED | Defined by PAIR §10.3/TRIO inherited statistic; no per-r producer call |
| main primary evidence definition | DEFINED_BUT_NOT_IMPLEMENTED | Same |
| recent state definition | DEFINED_BUT_NOT_IMPLEMENTED | PAIR §10.1–10.2 and `recent_support_state`; production fixed placeholder |
| PG01 | IMPLEMENTED_AND_REACHABLE | `evaluate_gates`; observed FAIL is valid |
| PG07/PG08 predicates | IMPLEMENTED_BUT_UNREACHABLE | Predicate exists; required evidence never materialized in production |
| TEST_READY decision | IMPLEMENTED_BUT_UNREACHABLE | `decide_state` exists; official lifecycle does not call it |
| historical per-r materializer | DEFINED_BUT_NOT_IMPLEMENTED | Current-only aggregation exists; per-r connection absent |

## Static reachability proof

`TEST_READY_REACHABLE_BY_DEFINED_RULES = YES`.

Path A is satisfiable with two valid member TRIOs in PASS/WEAKEN/TEST, exposure >=50, no research-hold risk/structure/bonus/recent/conflict condition, complete evidence, and at least one non-PASS member (or expanded pool or exposure 50..199). PG01 may FAIL while canonical TEST_READY remains permitted. Path B is satisfiable with two PASS members, exposure >=200, nonempty failed-gate set contained in {PG07, PG08}, neither PRIMARY evidence INFERIOR_CONFIRMED, and no higher-priority hold. This is a symbolic proof only; no historical output was calculated.

## Final report fields

- BASELINE_STATE: `1.0.85 / DECISION-20260824-092`
- ROOT_CAUSE_INPUT: `IMPLEMENTATION_OR_DEFINITION_ANOMALY`
- INTEGRATED_PRIMARY_EVIDENCE_STATUS: `DEFINED_BUT_NOT_IMPLEMENTED_PER_R`
- INTEGRATED_PRIMARY_EVIDENCE_PRODUCER: `required historical materializer using statistic(); current-only producer exists in final_aggregation.aggregate()`
- MAIN_PRIMARY_EVIDENCE_STATUS: `DEFINED_BUT_NOT_IMPLEMENTED_PER_R`
- MAIN_PRIMARY_EVIDENCE_PRODUCER: same materializer, MAIN PRIMARY endpoint
- RECENT_STATE_STATUS: `DEFINED_BUT_NOT_IMPLEMENTED_PER_R`
- RECENT_STATE_RULE: selection-exposure RECENT100/50; RECENT20 TEST_ONLY
- PG01_ROOT_CAUSE: `MEMBER_TRIOS_NOT_BOTH_PASS; INTENDED GATE RESULT`
- PG07_ROOT_CAUSE: `integrated_primary_evidence literal None`
- PG08_ROOT_CAUSE: `main_primary_evidence literal None`
- PAIR_TEST_READY_DEFINED: `YES`
- PAIR_TEST_READY_IMPLEMENTED: `YES_IN_DECISION_PRIMITIVE`
- PAIR_TEST_READY_REACHABLE: `NO_IN_PRODUCTION_LIFECYCLE / YES_BY_DEFINED_RULES`
- HISTORICAL_MATERIALIZER_EXISTS: `PARTIAL_CURRENT_ONLY`
- MATERIALIZER_EXECUTION_PATH: `final_aggregation round-1236 only; absent from per-r production`
- MATERIALIZER_FUTURE_SAFE: `YES_BY_CONTRACT; CURRENT RAW RATE LOOKBACK IS <R`
- CANONICAL_SEMANTICS_COMPLETE: `YES`
- REPAIR_SPECIFIABLE: `YES`
- REPAIR_REQUIRES_THRESHOLD_CHANGE: `NO`
- REPAIR_REQUIRES_GATE_CHANGE: `NO`
- REPAIR_CLASSIFICATION: `ORIGINAL_RULE_IMPLEMENTATION_RECOVERY`
- TEST_READY_REACHABLE_BY_DEFINED_RULES: `YES`
- AFFECTED_VALID_ROUNDS: `867 coverage interpretations`
- AFFECTED_RAW_PAIR_CANDIDATES: `148215`
- AFFECTED_PAIR_ROUNDS: `258`
- AFFECTED_CORE_ENTRY_ROUNDS: `258 direct PAIR-containing rounds`
- LIVE_CURRENT_PATH_AFFECTED: `YES`
- HISTORICAL_COVERAGE_INTERPRETATION: `PARTIALLY_VALID`
- NUMBER_STAGE_EVIDENCE_STILL_VALID: `YES, raw availability/count only`
- TRIO_STAGE_EVIDENCE_STILL_VALID: `YES, raw availability/count only`
- PAIR_STAGE_EVIDENCE_STILL_VALID: `RAW CANDIDATE AVAILABILITY ONLY; GATE/STATE PERFORMANCE ON HOLD`
- END_TO_END_OUTPUT_RATE_EVIDENCE_VALID: `NO FOR INTENDED GATE PERFORMANCE`
- ARCHITECTURE_FINAL_JUDGMENT: `ARCHITECTURE_REPAIR_SPECIFIABLE`
- EVIDENCE_BASED_NEXT_PATH: lock repair spec/hash, then separately approved shadow repair prototype; never official apply automatically

## Protection

- OFFICIAL_ENGINE: `FROZEN`
- OFFICIAL_CHANGED: `0`
- EXP_017: `NOT_CREATED`
- DRAW_DISCOVERY_PAUSE: `ACTIVE`
- NO_PICK: `UNRESOLVED`
- historical/shadow output calculated: `0`


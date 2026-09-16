# PAIR EVIDENCE PROVENANCE MAP

| Symbol | Canonical definition | Code definition / producer | Consumer | Persistence | Type / nullability | Intended time and lookback | Future dependency | Status |
|---|---|---|---|---|---|---|---|---|
| `integrated_primary_evidence` | PAIR §10.3 inherits TRIO evidence labels; integrated exact 3/3 PRIMARY, separate from exact2/3 SUPPORT | Primitive: `trio_engine.statistic`; current-only producer: `final_aggregation.aggregate`; production passes literal `None` | `evaluate_gates` PG07; `decide_state`; risk/bonus | Canonical proposal `pair_stat_test.evidence_state`; walk-forward gate input/context JSON | enum label; required/non-null for completed gate, null means missing input | Before outcome r, using representative selection exposures with evaluation_round < r; minimum 200 for evidence classification used by READY | NO under contract | `DEFINED_BUT_NOT_IMPLEMENTED` per-r |
| `main_primary_evidence` | same label rules for MAIN exact 3/3 PRIMARY | same producer pattern; production literal `None` | PG08; `decide_state`; risk/bonus | same | enum label; required/non-null for completed gate | same `<r` exposure history | NO | `DEFINED_BUT_NOT_IMPLEMENTED` per-r |
| `recent_state` | PAIR §10.1–10.2: representative selection exposure windows 100/50; RECENT20 TEST_ONLY | `decision.recent_support_state`; current-only call in final aggregation; production fixed `INSUFFICIENT_SAMPLE` | PG09; research hold; TEST_READY safety; risk/ranking | Canonical `pair_period_metric` plus gate/context; no normalized per-r materialization in runner | `STABLE/WARNING/SEVERE` with explicit insufficient sample handling; required for completed PG09 | Before outcome r, window ending at last prior exposure (<r) | NO | `DEFINED_BUT_NOT_IMPLEMENTED` per-r |
| `PAIR_TEST_READY` | Gate Amendment §11.4 and §11.4.1, after SYSTEM_HOLD→RESEARCH_HOLD→READY precedence | `decision.decide_state` returns it; `lifecycle_v12` does not call that function and has no TEST_READY return branch | CORE transition permits CORE_TEST_SET_READY | schema accepts value in pair candidate/ledger and walk-forward candidate row | enum, exactly one final state | after PG01–PG14 pre-result completion and before outcome | NO | `IMPLEMENTED_BUT_UNREACHABLE` in production lifecycle |
| PG01 | both member states `TRIO_PASS` | `decision.evaluate_gates` | READY gate vector; TEST_READY may tolerate its FAIL on path A | gate result/context JSON; canonical `pair_gate_result` | PASS/FAIL/INCOMPLETE, non-null final gate | pre-result, member TRIO states formed from data <=r-1 | NO | `IMPLEMENTED_AND_REACHABLE` |
| PG07 | integrated PRIMARY rate > exact baseline and evidence != INFERIOR_CONFIRMED | `decision.evaluate_gates`; rate produced in `production.py`, evidence missing | READY and baseline-only TEST_READY path | gate result/context; canonical stat table | PASS/FAIL/INCOMPLETE | pre-result from prior representative exposures only | NO | predicate implemented, completion unreachable in production |
| PG08 | main PRIMARY rate >= exact main baseline and evidence != INFERIOR_CONFIRMED | same | same | same | same | same | NO | predicate implemented, completion unreachable in production |

## Evidence label semantics

- Sample unit: one representative `pair_selection_rule_exposure` for one signature in one evaluation round, not every candidate identity.
- Integrated PRIMARY success: member A or B has integrated 3/3; MAIN PRIMARY success: member A or B has main 3/3.
- Exact2/3 SUPPORT is stored and tested separately and is never added to PRIMARY.
- Labels use exact one-sided binomial tails and Wilson 95% against the endpoint baseline. `<200` is `INSUFFICIENT` for the official overall evidence classification.
- At r, only exposure outcomes from rounds `<r` are eligible.


# PAIR LIFECYCLE STATE MACHINE

This reconstruction uses only canonical names and existing code states.

```text
valid TRIO inputs
  -> disjoint PAIR candidate
  -> base rule signature + identity exposure
  -> prior representative selection history (< r)
  -> sample band (<50 / 50..199 / >=200)
  -> PRIMARY/SUPPORT statistics + recent/risk/structure/bonus
  -> PRELOCK / PG05
  -> PG01..PG12 / PG13 preliminary / PG14 / PG13 final
  -> complete PG01..PG14 vector
  -> precedence decision
       SYSTEM_HOLD
       else RESEARCH_HOLD
       else READY if all 14 PASS
       else TEST_READY if canonical path A or B and safety conditions pass
       else RESEARCH_HOLD
  -> READY/TEST_READY may be CORE eligible
  -> outcome r is read only after final pre-result state
  -> result contributes from r+1 onward
```

| Transition | Canonical condition | Current actual path |
|---|---|---|
| candidate → history lookup | same v1.2 rule signature, evaluation_round < r | implemented |
| history → rates | representative selection outcomes, PRIMARY and SUPPORT separate | primary rates partially implemented |
| rates → evidence labels | Wilson/exact binomial, minimum sample 200 | missing per-r |
| history → recent | exposure-order RECENT100/50, RECENT20 diagnostic | missing per-r |
| gates → SYSTEM_HOLD | any required gate incomplete or system/persistence failure | implemented |
| gates → RESEARCH_HOLD | exposure <50 or canonical severe/high/inferior conditions | implemented in `decide_state`, bypassed by lifecycle |
| gates → READY | all 14 PASS and no higher hold | implemented in both paths |
| gates → TEST_READY | §11.4 path A/B and safety conditions | decision primitive implemented; lifecycle branch missing |
| READY/TEST_READY → CORE candidate | only corresponding PAIR state plus report/hash conditions | schema/rule defined; no affected output observed |

`PG01 FAIL` is not itself a terminal state. It blocks READY, while canonical TEST_READY path A can still accept valid WEAKEN/TEST members if all TEST_READY safety conditions are met.


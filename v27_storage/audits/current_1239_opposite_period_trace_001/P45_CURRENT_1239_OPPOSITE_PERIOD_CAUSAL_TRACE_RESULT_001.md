# P45 CURRENT 1239 OPPOSITE-PERIOD CAUSAL TRACE RESULT 001

## Final

- FINAL_VERDICT: `CURRENT_1239_OPPOSITE_PERIOD_CAUSAL_TRACE_COMPLETE`
- OPPOSITE_PERIOD_HOLD_COUNT: `28`
- HIGH_RISK_PLUS_OPPOSITE_COUNT: `1` (number `2`)
- UNIQUE_OPPOSITE_PATTERN_COUNT: `1`
- ROOT_CAUSE_CLASS: `CURRENT_NUMBER_EXTINCTION_CAUSED_BY_PERIOD_STABILITY_FILTER`
- OPPOSITE_PERIOD_PREDICATE_IS_NECESSARY_FOR_CURRENT_NUMBER_EXTINCTION: `YES`
- DEFECT_EVIDENCE_FOUND: `NO`

All 28 rows share one canonical pattern: PRIMARY overall integrated evidence is `POSITIVE_TENTATIVE` while PRIMARY recent100 integrated evidence is `INSUFFICIENT`. With only the `_opposite_directions` predicate forced false and every input and other predicate fixed, 27 rows change HOLD→WEAKEN; number 2 remains HOLD because HIGH opposite risk is an independent earlier OR term. Shadow eligible rises from 5 to 32, so the predicate is causally necessary for the current `5<6` extinction.

## Boundary and protected state

- State / Decision / Registry: `1.0.88 / DECISION-20260824-095 / 63`
- Validated source: contiguous `1..1238`, SHA-256 `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Target / source maximum: `1239 / 1238`
- OFFICIAL ENGINE / NO-PICK / DRAW_DISCOVERY_PAUSE / EXP-017: `FROZEN / UNRESOLVED / ACTIVE / NOT_CREATED`
- Target outcome access / outcome scoring / future leakage: `0 / 0 / 0`

## Canonical predicate

- CANONICAL_MODULE_FUNCTION: `p45_v27.number_engine._opposite_directions`, called by `decide_number`
- Source fields: PRIMARY context `overall.integrated.evidence_label` and `recent100.integrated.evidence_label`
- Evidence ranks: `POSITIVE_CONFIRMED=5`, `POSITIVE_TENTATIVE=4`, `NEUTRAL=3`, `NEGATIVE_TENTATIVE=2`, `NEGATIVE_CONFIRMED=1`, `INSUFFICIENT=0`
- Exact predicate: `(overall rank >=4 and recent100 rank <=2) OR (overall rank <=2 and recent100 rank >=4)`
- HOLD connection: `_opposite_directions(ctx)` and overall integrated label not in `(POSITIVE_CONFIRMED, NEGATIVE_CONFIRMED)`.
- Sign/tie/zero: no numeric sign, rate-zero, or rate-tie comparison is used. “Direction” is determined solely by ordinal evidence-label polarity. Rank 3 is neither polarity; equal ranks cannot satisfy the opposite inequalities.
- Period pair: only `overall` versus `recent100`. `recent50` and `recent20` do not enter `_opposite_directions`; they are recorded below for context.
- HIGH risk combination: `number_opposite_risk == HIGH` is a separate earlier HOLD OR term. Number 2 satisfies both; removing opposite-period alone does not release it.
- Predicate order: FAIL is evaluated first, then the HOLD OR expression. Within HOLD source order, HIGH risk precedes opposite-period. Canonical `first_limited_gate` records `NUMBER_HOLD_RULE`, not an individual HOLD OR subterm; the first failed PASS gate remains diagnostic rather than the HOLD attribution.

## Pattern taxonomy

| OPPOSITE_PATTERN | COUNT | PERIOD_A | PERIOD_B | CANONICAL_HOLD_EFFECT |
|---|---:|---|---|---|
| POSITIVE_TENTATIVE → INSUFFICIENT | 28 | overall integrated | recent100 integrated | opposite-period HOLD OR term |

- The 28 are one identical evidence-state mismatch pattern.
- Dominant comparison: overall vs recent100, `28/28`.
- PRIMARY `POSITIVE_TENTATIVE`: `28/28`.
- HIGH opposite risk: `1/28`; it is an independent blocker for number 2.
- Important semantic observation: several recent100 rates are numerically positive or high, but their evidence state remains `INSUFFICIENT` because the samples are only 2 or 3. The predicate uses the evidence state, not the raw rate. This supports the classification as a period-stability/sample-sufficiency filter rather than a raw-rate sign filter.

## 28-number full decomposition

Period cells are `evidence_state; sample_count; rate`. The exact opposite pair is overall vs recent100 for every row.

| No. | Primary unit | Overall | Recent100 | Recent50 | Recent20 | Risk | Conflict | First failed | Exact HOLD predicate | Shadow lifecycle |
|---:|---|---|---|---|---|---|---|---|---|---|
| 2 | UNIT_9 | PT;22;.1818 | INSUFF;2;.5 | INSUFF;0;null | INSUFF;0;null | HIGH | NONE | G06 | HIGH_RISK + OPPOSITE_PERIOD | HOLD |
| 3 | UNIT_9 | PT;22;.1818 | INSUFF;2;0 | INSUFF;0;null | INSUFF;0;null | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 4 | UNIT_9 | PT;22;.1818 | INSUFF;2;0 | INSUFF;0;null | INSUFF;0;null | MEDIUM | NONE | G07 | OPPOSITE_PERIOD | WEAKEN |
| 6 | UNIT_10 | PT;32;.15625 | INSUFF;3;.6667 | INSUFF;2;.5 | PT;2;.5 | MEDIUM | MEDIUM | G08 | OPPOSITE_PERIOD | WEAKEN |
| 7 | UNIT_9 | PT;22;.2273 | INSUFF;2;.5 | INSUFF;0;null | INSUFF;0;null | MEDIUM | MEDIUM | G07 | OPPOSITE_PERIOD | WEAKEN |
| 8 | UNIT_9 | PT;22;.2727 | INSUFF;2;0 | INSUFF;0;null | INSUFF;0;null | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 10 | UNIT_10 | PT;32;.15625 | INSUFF;3;0 | INSUFF;2;0 | NT;2;0 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 15 | UNIT_10 | PT;32;.15625 | INSUFF;3;.3333 | INSUFF;2;.5 | PT;2;.5 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 16 | UNIT_10 | PT;32;.15625 | INSUFF;3;.3333 | INSUFF;2;.5 | PT;2;.5 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 17 | UNIT_10 | PT;32;.1875 | INSUFF;3;0 | INSUFF;2;0 | NT;2;0 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 19 | UNIT_10 | PT;32;.21875 | INSUFF;3;0 | INSUFF;2;0 | NT;2;0 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 21 | UNIT_10 | PT;32;.1875 | INSUFF;3;.3333 | INSUFF;2;0 | NT;2;0 | MEDIUM | MEDIUM | G09 | OPPOSITE_PERIOD | WEAKEN |
| 22 | UNIT_10 | PT;32;.15625 | INSUFF;3;.3333 | INSUFF;2;0 | NT;2;0 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 23 | UNIT_9 | PT;22;.1818 | INSUFF;2;0 | INSUFF;0;null | INSUFF;0;null | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 28 | UNIT_10 | PT;32;.1875 | INSUFF;3;.3333 | INSUFF;2;0 | NT;2;0 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 29 | UNIT_10 | PT;32;.15625 | INSUFF;3;.3333 | INSUFF;2;0 | NT;2;0 | MEDIUM | MEDIUM | G08 | OPPOSITE_PERIOD | WEAKEN |
| 30 | UNIT_10 | PT;32;.1875 | INSUFF;3;0 | INSUFF;2;0 | NT;2;0 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 31 | UNIT_9 | PT;22;.1818 | INSUFF;2;0 | INSUFF;0;null | INSUFF;0;null | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 32 | UNIT_10 | PT;32;.21875 | INSUFF;3;.3333 | INSUFF;2;.5 | PT;2;.5 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 33 | UNIT_10 | PT;32;.1875 | INSUFF;3;.3333 | INSUFF;2;.5 | PT;2;.5 | MEDIUM | MEDIUM | G09 | OPPOSITE_PERIOD | WEAKEN |
| 35 | UNIT_9 | PT;22;.2273 | INSUFF;2;0 | INSUFF;0;null | INSUFF;0;null | MEDIUM | MEDIUM | G07 | OPPOSITE_PERIOD | WEAKEN |
| 36 | UNIT_10 | PT;32;.1875 | INSUFF;3;0 | INSUFF;2;0 | NT;2;0 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 39 | UNIT_9 | PT;22;.2727 | INSUFF;2;0 | INSUFF;0;null | INSUFF;0;null | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 40 | UNIT_9 | PT;22;.2273 | INSUFF;2;0 | INSUFF;0;null | INSUFF;0;null | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 42 | UNIT_10 | PT;32;.21875 | INSUFF;3;0 | INSUFF;2;0 | NT;2;0 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 43 | UNIT_10 | PT;32;.21875 | INSUFF;3;.3333 | INSUFF;2;.5 | PT;2;.5 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 44 | UNIT_10 | PT;32;.1875 | INSUFF;3;0 | INSUFF;2;0 | NT;2;0 | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |
| 45 | UNIT_9 | PT;22;.2273 | INSUFF;2;0 | INSUFF;0;null | INSUFF;0;null | MEDIUM | MEDIUM | G06 | OPPOSITE_PERIOD | WEAKEN |

Legend: `PT=POSITIVE_TENTATIVE`, `NT=NEGATIVE_TENTATIVE`, `INSUFF=INSUFFICIENT`. Full-precision values, lifecycle fields, and unshortened gate names are preserved in `OPPOSITE_PERIOD_CAUSAL_TRACE.json`.

## Dependency-only shadow

- Intervention: patch only `_opposite_directions` to return false; no input field, other HOLD predicate, gate, threshold, signature, structure, risk, conflict, or evidence value changed.
- SHADOW_NUMBER_COUNTS: `HOLD 13 / WEAKEN 32 / TEST 0 / PASS 0`
- SHADOW_ELIGIBLE_COUNT: `32`
- SHADOW_ELIGIBLE_IDENTITIES: `3, 4, 6, 7, 8, 10, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 27, 28, 29, 30, 31, 32, 33, 35, 36, 39, 40, 42, 43, 44, 45`
- Minimum six met: `YES`
- Added lifecycle class: 27 current HOLD rows become `NUMBER_WEAKEN`; number 2 remains HOLD.
- Official selection/output generated: `NO / NO`
- This result is not a recommendation, ranking, hidden score, sixth-number selection, or gate-relaxation proposal.

## PARTIAL_SURVIVOR_REPORTING

- ID / status: `PARTIAL_SURVIVOR_REPORTING / REPORTING_POLICY_IDEA_REGISTERED`
- Current validated partial survivor pool: `13, 18, 20, 24, 27` (`5`)
- The official 3×2 contract remains unchanged; minimum below six remains `NO_OUTPUT`.
- The registered idea is to consider displaying 1–5 eligible survivors separately as research information rather than hiding them.
- Survivors must remain explicitly separate from official recommendations.
- Arbitrary `3+2+2`, `3+2`, overlapping groups, hidden scoring, weighting, and forced picks remain forbidden until independently validated.
- Historical survivor-count distribution and practical utility may be evaluated separately. Registration itself changes no engine semantics.

## Change control

- Official source / DB changes: `0 / 0`
- State / Decision / Registry changes: `0 / 0 / 0`
- Gate / threshold / signature changes: `0 / 0 / 0`
- NUMBER/TRIO/PAIR/CORE semantics changes: `0`
- Forced pick / hidden score / sixth-number manufacture: `0 / 0 / 0`
- EXP-017 creation / pause release: `0 / 0`
- PROJECT_SOURCES_ACTION_REQUIRED: `YES`

## NEXT_ACTION

`DESIGN_LOW_DOF_OPPOSITE_PERIOD_STABILITY_FILTER_VALIDATION_001`

Design only a low-degree-of-freedom validation that distinguishes whether the overall-vs-recent100 evidence-state mismatch is a useful stability safeguard or an independent predictive signal. Do not create EXP-017, alter the filter, or score target 1239.

`CURRENT_1239_OPPOSITE_PERIOD_CAUSAL_TRACE_COMPLETE`

# P45 NUMBER MEMBER STRUCTURE SEVERE CAUSAL TRACE RESULT 001

## Final

- FINAL_VERDICT: `NUMBER_MEMBER_STRUCTURE_SEVERE_CAUSAL_TRACE_COMPLETE`
- NUMBER_SURVIVOR_COUNT: `12`
- NUMBER identities: `13, 24, 27, 37, 34, 12, 19, 20, 28, 21, 6, 39`
- NUMBER lifecycle distribution: `NUMBER_WEAKEN 12`
- NUMBER structure-state distribution: `SEVERE 12`
- UNIQUE_NUMBER_STRUCTURE_REASON_COUNT: `1`
- TOP_NUMBER_STRUCTURE_REASON: `UNIT_5 + END_DIGIT global structure SEVERE → number_structure_state SEVERE` (`12`)
- FIRST_FATAL_UPSTREAM_PREDICATE: `max_abs_standardized_occupancy percentile >= 99`
- STRUCTURAL_ROOT_CAUSE_CLASS: `NUMBER_GLOBAL_STRUCTURE_SEVERE`
- DEFECT_EVIDENCE_FOUND: `NO`

## Canonical propagation rule

1. `p45_v27.structure_collapse.calculate_structure_ledger` calculates five structure metrics for each unit family, converts each current metric to its historical percentile, and uses the maximum percentile without weighting.
2. `_state(overall_percentile)` returns `SEVERE` when the percentile is `>=99`.
3. `p45_v27.number_engine.combine_number_risk` assigns each NUMBER the maximum structure state across its five evaluable unit inputs using `STRUCTURE_RANK`.
4. `p45_v27.trio_engine.build_current_trios` assigns `member_structure_summary` as the maximum of its three NUMBER structure states.
5. One `SEVERE` member is sufficient; two or three are not required.
6. `final_structure_state` is the maximum of member summary and trio-rule structure, except that an insufficient trio-rule sample leaves the member summary unchanged.

No separate weighting or hidden score participates in this propagation.

## 12 NUMBER survivor trace

| NUMBER | NUMBER STATE | STRUCTURE | OVERALL PRIMARY | OPPOSITE RISK | CONTEXT CONFLICT | FIRST FAILED PASS GATE |
|---:|---|---|---|---|---|---|
| 13 | NUMBER_WEAKEN | SEVERE | POSITIVE_CONFIRMED | MEDIUM | NONE | NUMBER_PASS_GATE_09 |
| 24 | NUMBER_WEAKEN | SEVERE | POSITIVE_TENTATIVE | MEDIUM | MEDIUM | NUMBER_PASS_GATE_10 |
| 27 | NUMBER_WEAKEN | SEVERE | POSITIVE_TENTATIVE | MEDIUM | MEDIUM | NUMBER_PASS_GATE_17 |
| 37 | NUMBER_WEAKEN | SEVERE | POSITIVE_TENTATIVE | MEDIUM | MEDIUM | NUMBER_PASS_GATE_08 |
| 34 | NUMBER_WEAKEN | SEVERE | POSITIVE_CONFIRMED | MEDIUM | MEDIUM | NUMBER_PASS_GATE_06 |
| 12 | NUMBER_WEAKEN | SEVERE | POSITIVE_CONFIRMED | MEDIUM | MEDIUM | NUMBER_PASS_GATE_06 |
| 19 | NUMBER_WEAKEN | SEVERE | POSITIVE_TENTATIVE | MEDIUM | MEDIUM | NUMBER_PASS_GATE_06 |
| 20 | NUMBER_WEAKEN | SEVERE | POSITIVE_TENTATIVE | MEDIUM | NONE | NUMBER_PASS_GATE_06 |
| 28 | NUMBER_WEAKEN | SEVERE | POSITIVE_TENTATIVE | MEDIUM | MEDIUM | NUMBER_PASS_GATE_06 |
| 21 | NUMBER_WEAKEN | SEVERE | POSITIVE_TENTATIVE | MEDIUM | MEDIUM | NUMBER_PASS_GATE_06 |
| 6 | NUMBER_WEAKEN | SEVERE | POSITIVE_TENTATIVE | MEDIUM | MEDIUM | NUMBER_PASS_GATE_06 |
| 39 | NUMBER_WEAKEN | SEVERE | POSITIVE_TENTATIVE | MEDIUM | MEDIUM | NUMBER_PASS_GATE_06 |

- PRIMARY evidence: `POSITIVE_CONFIRMED 3 / POSITIVE_TENTATIVE 9`
- Exact 3/3 and exact 2/3 TRIO outcome states are not inputs to NUMBER structure; they remain `NOT_A_NUMBER_STRUCTURE_INPUT` at this level.
- The selected pool is `EXPANDED_TEST_POOL`; all 12 survive because they are eligible `NUMBER_WEAKEN` candidates and rank within the official top 12.
- NUMBER survivor does not mean NUMBER_PASS. Severe structure blocks the structure PASS gate, but positive/tentative primary evidence prevents the severe-plus-nonpositive HOLD predicate. The mandatory-weaken branch can therefore legitimately keep them in the expanded pool.
- The same severe state is still propagated as member structure to TRIO. Survival at NUMBER and severe treatment at TRIO are distinct official rules and are consistent by design.

Full records: `NUMBER_SURVIVOR_12_RECORDS.json`.

## NUMBER-level structure taxonomy

| NUMBER_STRUCTURE_REASON | COUNT | CANONICAL_PREDICATE | REQUIRED | OBSERVED SUMMARY |
|---|---:|---|---|---|
| `UNIT_5_AND_END_DIGIT_MAX_PERCENTILE_SEVERE` | 12 | maximum evaluable unit structure equals `SEVERE` | every evaluable unit must be `WARNING` or better | UNIT_5 and END_DIGIT are both SEVERE for every NUMBER |

Unit structure evidence:

- `UNIT_5`: overall percentile `99.19093851132686`; decisive `max_abs_standardized_occupancy` percentile `99.19093851132686`; current metric `2.875878420888012`; sample `1236`.
- `END_DIGIT`: overall percentile `99.19093851132686`; decisive `max_abs_standardized_occupancy` percentile `99.19093851132686`; current metric `3.3981877782208976`; sample `1236`.
- `UNIT_3`, `UNIT_9`, and `UNIT_10` are `WARNING`, not SEVERE.
- Canonical threshold: percentile `<99` is `WARNING` or better; no threshold was changed.

The structure ledger is unit-family-wide at this stage. Therefore all 12 NUMBERs independently receive the same two SEVERE unit inputs; this is not a small severe subset contaminating every combination.

## Combinatorial propagation audit

- SEVERE NUMBER count `s = 12`
- non-SEVERE count `12-s = 0`
- TRIOs containing no SEVERE member: `C(0,3) = 0`
- TRIOs containing at least one SEVERE member: `C(12,3) - C(0,3) = 220`
- Observed severe TRIO summaries: `220`
- Mathematical/canonical equivalence: `PASS`

## Legitimate release conditions

- Both UNIT_5 and END_DIGIT must cease being SEVERE, because either remaining SEVERE is sufficient to keep every NUMBER SEVERE under the maximum rule.
- At least `3` NUMBERs must become non-SEVERE for one all-non-SEVERE TRIO to exist.
- At least `10` must become non-SEVERE for a majority of the 220 TRIOs to avoid member SEVERE (`C(10,3)=120`).
- All `12` must become non-SEVERE for all 220 TRIOs to avoid member SEVERE.
- Because the decisive unit ledgers are global inputs, the present implementation will normally transition all affected NUMBERs together when both unit states improve; candidate-by-candidate overrides are neither canonical nor allowed.
- The 1236-sample maturity requirement is already satisfied. This is not sample-age starvation.
- Future pre-result draws can naturally change the current metrics and historical percentile distributions. No existing evidence shows that improvement requires a new scoring signal, but it cannot be asserted in advance.

These are structural calculations, not relaxation proposals.

## Change control

- Gate/threshold changed: `NO / NO`
- Official source/DB changes: `0 / 0`
- State/Decision/Registry changes: `0 / 0 / 0`
- Future leakage/outcome scoring: `0 / 0`
- NO-PICK: `UNRESOLVED`
- OFFICIAL ENGINE: `FROZEN`
- DRAW_DISCOVERY_PAUSE: `ACTIVE`
- EXP-017: `NOT_CREATED`

## NEXT_ACTION

`READ_ONLY_UNIT_5_END_DIGIT_OCCUPANCY_SEVERE_CAUSAL_TRACE_001`

This single next action should decompose the current `max_abs_standardized_occupancy` values and the exact historical percentile tie that places UNIT_5 and END_DIGIT at `99.19093851132686`, using only the sealed 1238 boundary.

`NUMBER_MEMBER_STRUCTURE_SEVERE_CAUSAL_TRACE_COMPLETE`

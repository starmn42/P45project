# P45 TRIO HOLD CAUSAL DECOMPOSITION RESULT 001

## Final

- FINAL_VERDICT: `TRIO_HOLD_CAUSAL_DECOMPOSITION_COMPLETE`
- TRIO_UNIVERSE_COUNT: `220`
- TRIO_HOLD_COUNT: `220`
- UNIQUE_HOLD_REASON_COUNT: `4` unmet HOLD predicates (`2` primary reason classes)
- FIRST_FATAL_PREDICATE: `final_structure_state == SEVERE`
- CANONICAL_MODULE_FUNCTION: `p45_v27.trio_engine.classify_trio`
- STRUCTURAL_BOTTLENECK_CLASS: `SINGLE_PREDICATE_GLOBAL_HOLD`
- DEFECT_EVIDENCE_FOUND: `NO`

All 220 TRIOs have `member_structure_summary = SEVERE`, which propagates to `final_structure_state = SEVERE`. The canonical `hold` predicate in `classify_trio` treats `structure == SEVERE` as sufficient for `TRIO_HOLD`. This single predicate therefore causes global extinction even though additional lifecycle deficits overlap many candidates.

## Candidate universe

- Target/source boundary: `1238 / <=1237`
- Input snapshot SHA-256: `ad69ec8d28b4e5cdb40d468ad758c5f23acaeb6225f525c5201c8027952701e6`
- NUMBER survivors: `12`
- Official combinatorial universe: `C(12,3) = 220`
- Reconstructed official TRIO records: `220`
- Identity duplicates: `0`
- Future leakage: `0`
- Target outcome access/scoring: `0 / 0`

The full per-TRIO records are stored in `TRIO_HOLD_220_RECORDS.json` and were produced by one bulk lifecycle build using the existing 1238 snapshot and a single pre-1238 history read.

## HOLD reason taxonomy

| HOLD_REASON | COUNT | SHARE | CANONICAL_PREDICATE | REQUIRED | OBSERVED DISTRIBUTION |
|---|---:|---:|---|---|---|
| `FINAL_STRUCTURE_SEVERE` | 220 | 100.00% | `structure == "SEVERE"` | final structure must be `WARNING` or better for HOLD release | final `SEVERE` 220; member summary `SEVERE` 220; trio-rule structure `INSUFFICIENT_SAMPLE` 218 / `SEVERE` 2 |
| `SELECTION_RULE_EXPOSURE_LT50` | 216 | 98.18% | `n < 50` | `n >= 50` for potential valid `TRIO_TEST` | exposure min 0, median 3, max 185; only 4 reach ≥50 |
| `TRIO_RULE_OPPOSITE_RISK_HIGH` | 148 | 67.27% | `risk == "HIGH"` | risk must not be `HIGH` | `HIGH` 148 / `MEDIUM` 72 |
| `UNIT_CONFLICT_COUNT_GE2` | 148 | 67.27% | `conf >= 2` | conflict count `<2` | 2: 148 / 1: 68 / 0: 4 |

Non-causes in this universe:

- `BONUS_DEPENDENCE_HIGH`: `0` (`BONUS_DEPENDENCE_NONE` 220)
- incomplete unit count: `0` for all 220

## Primary and secondary conditions

Using the canonical HOLD expression order for primary attribution:

- Primary `SELECTION_RULE_EXPOSURE_LT50`: `216`
- Primary `FINAL_STRUCTURE_SEVERE`: `4` (these four already have exposure ≥50)

Secondary conditions overlap. The causal global predicate is nevertheless `FINAL_STRUCTURE_SEVERE`, because it is true for 220/220 and is independently sufficient to assign HOLD.

The gate audit separately reports `first_failed_gate = TRIO_PASS_GATE_01` for 220/220. This gate requires all three member NUMBER states to be `NUMBER_PASS`; it is the first failed PASS gate, but it is not by itself the canonical HOLD-state predicate. The HOLD-state cause and first failed PASS gate are therefore recorded separately.

## HOLD → eligible conditions

The nearest eligible lifecycle route is a valid `TRIO_TEST`, not an override:

- `selection_rule_exposure_count >= 50`
- integrated PRIMARY and SUPPORT evidence are not `INFERIOR_CONFIRMED`
- `trio_rule_opposite_risk != HIGH`
- `final_structure_state != SEVERE`
- `bonus_dependency_state != BONUS_DEPENDENCE_HIGH`
- incomplete unit count `= 0`
- unit conflict count `< 2`
- future boundary and determinism checks remain true

If all are satisfied, the exact next eligible status is `TRIO_TEST` with `valid_trio_test = true` and `valid_for_pair = true`. `TRIO_PASS` and `TRIO_WEAKEN` have stricter evidence and maturity requirements and are not inferred here.

## Distance to pass summary

- Exposure distance to 50: min `0`, median `47`, max `50`
- Exposure pass-adjacent (gap 1): `0`
- Exposure already ≥50: `4`
- Candidates satisfying every other valid-TEST condition now: `0`
- Structure distance: categorical; all `220` require at least `SEVERE → WARNING-or-better`
- Risk distance: `148` require `HIGH → MEDIUM-or-LOW`
- Conflict distance: `148` require `2 → <=1`

Exposure can increase naturally only when the same rule signature receives additional pre-result recurrence. However, time/exposure alone cannot release any current candidate because every candidate also has severe final structure. The severe final structure is inherited from `member_structure_summary = SEVERE` for all 220, so legitimate resolution requires new independent pre-result evidence that changes the upstream member structure state under unchanged rules.

These distances describe the locked predicates; they are not threshold-relaxation proposals.

## Change control

- Gate/threshold changed: `NO / NO`
- Official source/DB changes: `0 / 0`
- State/Decision/Registry changes: `0 / 0 / 0`
- NO-PICK: `UNRESOLVED`
- OFFICIAL ENGINE: `FROZEN`
- DRAW_DISCOVERY_PAUSE: `ACTIVE`
- EXP-017: `NOT_CREATED`

## NEXT_ACTION

`READ_ONLY_NUMBER_MEMBER_STRUCTURE_SEVERE_CAUSAL_TRACE_001`

This single next action should trace why all 12 NUMBER survivors supply `member_structure_summary = SEVERE`, using the same sealed 1238 boundary and without changing gates, thresholds, or State.

`TRIO_HOLD_CAUSAL_DECOMPOSITION_COMPLETE`

# P45 CURRENT 1239 END_DIGIT SEVERE CAUSAL TRACE RESULT 001

## Final verdict

- Status: `CURRENT_1239_END_DIGIT_SEVERE_CAUSAL_TRACE_NOT_CONFIRMED`
- Root-cause class: `DEFECT_EVIDENCE_FOUND_NEEDS_REVIEW`
- Defect evidence found: `YES`
- Reason: the mandated immutable staging snapshot named `...THROUGH_1238.csv` is not a contiguous `1..1238` source. It contains 1,236 unique rows with `min=1`, `max=1238`, and is missing rounds `1236` and `1237`.
- Consequence: the previously reported target-1239 END_DIGIT `SEVERE / 100.0`, NUMBER `5/40`, and downstream propagation were computed from an invalid input boundary and are not confirmed for canonical source rounds `<=1238`.

## Protected-state preflight

- State / Decision / Registry: `1.0.88 / DECISION-20260824-095 / 63`
- OFFICIAL ENGINE / NO-PICK / DRAW_DISCOVERY_PAUSE / EXP-017: `FROZEN / UNRESOLVED / ACTIVE / NOT_CREATED`
- Requested max source / target / mode: `1238 / 1239 / STAGING_PREDRAW`
- State drift: `NONE OBSERVED`

## Input-integrity evidence

| Artifact | SHA-256 | Rows | Range | Missing |
|---|---|---:|---|---|
| valid prior snapshot `CURRENT_INPUT_SNAPSHOT.csv` | `ad69ec8d28b4e5cdb40d468ad758c5f23acaeb6225f525c5201c8027952701e6` | 1,237 | `1..1237` | none |
| mandated target-1239 staging snapshot | `8779cb28068de1ee6ed69ef7d76ab3e0c30b64e17c3993f9622bda6261dd8c97` | 1,236 | `1..1238` | `1236, 1237` |

- Duplicate rounds in either snapshot: `0`
- The after-snapshot is therefore not the prior contiguous snapshot plus draw 1238.
- A valid 1237→1238 one-draw deterministic comparison cannot be performed from the mandated artifact.
- No replacement snapshot was invented and no official/staging source was repaired in this work.

## Required END_DIGIT decomposition disposition

- END_DIGIT state / overall percentile: `NOT CONFIRMED ON VALID 1..1238 INPUT` (the observed `SEVERE / 100.0` belongs only to the defective artifact)
- Decisive metric count: `NOT CONFIRMED`
- Decisive metrics: `NOT CONFIRMED`
- Raw current END_DIGIT structure: `INVALID INPUT BOUNDARY — rounds 1236 and 1237 absent`
- Historical reference sample: expected target-1239 reference cannot be certified; defective calculation used `1,235`, while the valid target-1238 baseline used `1,236`
- Canonical percentile rule traced in code: `100 × count(reference_value <= current_value) / N`; END_DIGIT aggregation is the unweighted maximum of component percentiles; `SEVERE` begins at `>=99.0`.
- The requested observed values (`zero_group=100.0`, `realized_return_depth=100.0`, `max_abs_standardized_occupancy=99.91902834008097`) are reproducible only on the defective snapshot and are not accepted as target-1239 causal facts.
- Zero-group identity, occupancy, return depth, strict-max/tie status, and decisive raw groups: `NOT CONFIRMED`, because each is downstream of the invalid sequence.

## 1237→1238 metric change

- Summary: `NOT VALID / NOT CONFIRMED`.
- The defective after-snapshot drops rounds 1236 and 1237 while adding 1238, so its metric deltas are not attributable solely to draw 1238.
- UNIT_5 `SEVERE→NORMAL` versus END_DIGIT `SEVERE→SEVERE(100.0)` is consequently not a certified one-round transition.
- Defect evidence: `YES`; deterministic canonical update itself is not accused—the supplied sequence boundary is invalid.

## NUMBER and latent TRIO disposition

- NUMBER_WEAKEN identities: `NOT CONFIRMED` (previous target-1239 result invalidated pending contiguous rerun)
- NUMBER_HOLD primary reason distribution: `NOT CONFIRMED` (previous `40` total invalidated pending contiguous rerun)
- `LATENT_TRIO_GLOBAL_SEVERE_IF_NUMBER_POOL_EXISTS = NOT CONFIRMED`
- The propagation rule remains deterministic: one SEVERE member is sufficient under maximum-rank member aggregation. Its current target-1239 premise (`NUMBER structure SEVERE 45/45`) is not certified on valid input.

## Compliance and disposition

- Future leakage / outcome scoring: `0 / 0`
- Official source / DB changes: `0 / 0`
- State / Decision / Registry changes: `0 / 0 / 0`
- Gate, threshold, signature, NUMBER/TRIO/PAIR/CORE semantics changes: `0`
- EXP-017 creation / forced pick / hidden score: `0 / 0 / 0`
- PROJECT_SOURCES_ACTION_REQUIRED: `YES`

## NEXT_ACTION

`REBUILD_CONTIGUOUS_STAGING_1_1238_AND_RERUN_CURRENT_1239_PREDRAW_001`

This is the single minimum repair-evidence action: construct and verify a contiguous staging-only `1..1238` snapshot from approved sources, then rerun the frozen target-1239 predraw before repeating any causal decomposition. It does not authorize an official source, DB, State, Decision, Registry, gate, or threshold change.

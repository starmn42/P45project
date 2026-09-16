# EXP-CROWD-TOPO-003-V1 FINAL RESULT

- Final status: `EXPLORATORY_NOT_SUPPORTED`
- Registry ID: `EXP-CROWD-20260823-007-V1`
- Data: official rounds 1..1237 only; holdout 801..1237 (437 = 23x19).
- Snapshot SHA-256: `1fb570c8205596a73777c8a19ace5276b3299e05f5e3b191788cec15b04818a9`
- Protocol SHA-256: `f71bc94dee31f4e5b297d7fb2d5343b7920e25226c17c8bdeedc6b5696c07aef`
- Calculator SHA-256: `a1c22f3bd735281979f48984916cbff6662ff4c6bfb59938a5b6fc994a8945d6`
- Canonical result hash: `52ebe5960d73241c7d7fb45787ccdc2d56a1229432d14072ff9653018455a7ac`

## Preregistered primary result

- T components d2..d6: `[-1.9205012586, -1.8106160487, 0.5039634375, -1.4124621965, 1.3482012593]`
- T_MAX: `1.9205012586094152`
- common-sign block wild bootstrap: `200,000`, seed `2026082306`
- exceedances: `11,249`
- two-sided omnibus p: `0.05624971875140624`
- decision at fixed alpha .05: `EXPLORATORY_NOT_SUPPORTED`

No threshold was changed. No individual contrast p-value was created. The result is not a promotion candidate and has no official-engine effect.

## Required validation

- official source semantics / fixed six rounds: PASS
- Johnson coefficient reconstruction: PASS
- 10x7 exact rank: 7
- listed F13/F23/F33 inversion coefficients: exact match
- float64 vs Decimal aggregate contrast means: PASS (relative 1e-8 or absolute 1e-10)
- deterministic same-input rerun: PASS
- focused direct tests: 4/4 PASS (`pytest` package unavailable in the local runtime; no dependency was installed)
- 1238+ used: 0
- prospective signal peeking: 0
- official DRAW engine changed: 0

## Interpretation boundary

This test did not cross its preregistered omnibus threshold. Even a positive result could only have been labeled `EXPLORATORY_TOPOLOGY_DEVIATION`; it would not identify a topology-specific mechanism or authorize official promotion. Existing EXP-001, EXP-002, prospective, draw-pause, and no-pick states remain unchanged.

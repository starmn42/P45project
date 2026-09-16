# P45 SIGNAL KTS COLLISION V1 PROTOCOL LOCKED 001

- LOCKED_AT: `2026-08-26 KST`, before structure enumeration and outcome scoring.
- Scope: independent Experiment Lab research; OFFICIAL ENGINE remains `FROZEN`; EXP-017 remains `NOT_CREATED`.
- Canonical data: `v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv`; expected SHA `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`.
- KTS schedule: reuse `v27_storage/experiments/trio_orbit_v1_001/P45_TRIO_ORBIT_V1_KTS45_SCHEDULE_001.csv`; required SHA `5f212342c6c27fca8eafbc75d20a55fc4be4ca2961a9c70c3a7af0eca26f1075`; do not regenerate.
- Signal for target R: use only R-1 MAIN6. For its 15 unordered pairs, map each through the unique KTS completion. Vote threshold is fixed at `>=2`; include source MAIN members; do not use BONUS; order by vote descending then number ascending; no fill or filters.
- Structural audit before backtest: exhaust all `C(45,6)=8,145,060` source sets; candidate count must be within `0..6`, vote max within `3`, pair map exactly 990 unique pairs.
- Primary: pooled candidate exposures/hits over targets `2..latest`; compare to the exact carryover-matched conditional null. Each round conditions on candidate count k, source-member count r, and observed source-target overlap c. Convolve independent Hypergeom(6,c,r) and Hypergeom(39,6-c,k-r), then dynamically convolve all rounds. One-sided exact p is `P(H_null >= H_observed)`.
- Confirmatory test count: exactly one, `SIGNAL_VALIDITY_PRIMARY`.
- Minimums: evaluated targets `>=1000`; exposures `>=500`; leakage `0`; all structural checks PASS.
- Supported only if observed hits exceed exact-null expectation and one-sided p `<=0.05`. Otherwise `FAILED_NOT_SUPPORTED`; low exposures yield `INCONCLUSIVE_LOW_OUTPUT`; any invariant/data/leakage mismatch yields `PROTOCOL_BLOCKED`.
- TRIO support: for candidate count >=3, top3 is research A; when count=6 next3 is research B; count4..5 leftovers remain individual signals. Exact3 and exact2 are descriptive and cannot rescue primary.
- Multiple-testing policy: vote subgroup, count subgroup, recent periods, number bands, parity, source membership, TRIO support, uniform-k comparator, and alternative thresholds are descriptive only and cannot change judgment.
- HISTORICAL_ONE_STEP_WALKFORWARD: `YES`.
- Forbidden after lock: threshold/ranking/filter change, subgroup rescue, outcome-driven tuning, official promotion, or edits to TRIO ORBIT V1 artifacts.

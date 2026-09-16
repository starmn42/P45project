# P45 BONUS × LAG-2 INTERACTION V1 PROTOCOL LOCKED 001

- LOCKED_AT: `2026-08-27 KST`, before interaction outcome calculation.
- Scope: new independent interaction research. EXP-005 remains `FAILED`; EXP-015 remains `FAILED_EARLY`. Neither is rerun, modified, or rescued. EXP-017 is not created. No recommendation or official-engine connection.
- Canonical input: latest validated contiguous local MAIN6+BONUS history; verify SHA before analysis.
- Evaluation targets: `3..latest`. For target R use MAIN(R-2), MAIN6+BONUS(R-1), and MAIN(R) only as outcome. BONUS(R) is unused.
- `BONUS_RANK(R-1)=1..7` within the sorted integrated seven; `BONUS_SCORE=4-rank`, preserving all ranks and using no threshold.
- `OVERLAP_R=|MAIN(R-2)∩MAIN(R)|`, preserving EXP-005's exact lag-2 definition and fair expectation 0.8.
- Primary statistic: population-form sample covariance after centering both observed series by their actual sample means, `mean[(BONUS_SCORE-mean_score)(OVERLAP-mean_overlap)]`. Report OLS slope `cov/var(BONUS_SCORE)`, Pearson correlation, and direction. Primary is two-sided.
- Full-sequence fair null: `100,000` independent histories. Each round draws MAIN6 uniformly from C(45,6) and BONUS uniformly from the remaining 39. For each simulated history recompute prior BONUS rank, lag-2 overlap, and centered covariance exactly as for actual data. Primary p is plus-one `P(|cov_sim|>=|cov_obs|)`.
- Deterministic seed rule: after writing this protocol, interpret its SHA-256 first 16 hexadecimal characters as unsigned 64-bit integer; record SHA and seed before outcome calculation.
- Conditional check: use every circular shift of the observed overlap series relative to the observed BONUS_SCORE series, preserving both marginal series and their internal circular structure. `CONDITIONAL_SHIFT_P` is the fraction of all N shifts, including zero shift, with absolute centered covariance at least observed. It is support only.
- Stability: full, chronological first half, second half, recent100, recent50, recent20. Report the same covariance/slope/correlation. Recent windows cannot rescue judgment.
- Descriptive only: BONUS rank 1..7 count, mean overlap, and difference from 0.8. No rank threshold or subgroup primary may be created.
- STRONG_INTERACTION_CANDIDATE: primary MC p<=0.05, first/second directions same or one nearly zero without strong reversal, conditional shift p<=0.05, leakage0, validations PASS.
- INTERESTING_WATCHLIST: primary MC p in `(0.05,0.10]` and first/second directions do not strongly conflict.
- Otherwise `FAILED_NOT_INTERESTING`.
- No hidden score, arbitrary weight, post-result subgroup, rank threshold, signal output, or recommendation.
- Protected changes: official code/DB/gate/threshold/signature/semantics/NUMBER/TRIO/PAIR/CORE/State/Decision/Registry `0`.

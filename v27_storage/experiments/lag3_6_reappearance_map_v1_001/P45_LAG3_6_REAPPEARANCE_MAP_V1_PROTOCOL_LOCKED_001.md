# P45 LAG3–6 REAPPEARANCE MAP V1 PROTOCOL LOCKED 001

- LOCKED_AT: `2026-08-26 KST`, before any L3–L6 outcome calculation.
- Research status: separate exploratory lag-map; not EXP-005 V2, rescue, or rerun; not EXP-017; not connected to OFFICIAL ENGINE.
- Existing EXP-005 L2 protocol/result are read-only reference. Its FINAL remains `FAILED` and L2 is excluded from the L3–L6 family calculation.
- Canonical source: latest validated contiguous local MAIN6+BONUS CSV. MAIN6 only is used; BONUS is excluded from signal and outcome.
- Lags tested simultaneously and exhaustively: `L={3,4,5,6}`. For target R, `X(R,L)=|MAIN(R-L)∩MAIN(R)|`; valid targets are `L+1..latest`.
- Direction fixed before results: positive, one-sided. Expected overlap `0.8`; expected number-level recurrence `6/45`.
- Per-lag analytical null: `X~Hypergeom(N=45,K=6,n=6)`. Because each lag graph is a union of disjoint paths and the conditional overlap law is constant, edge overlaps are independent under the fair-draw null; total-hit exact one-sided tails use the hypergeometric probability-generating function raised to the valid-target count.
- Per-lag Monte Carlo: fair independent MAIN6 sequences of the same length; `100,000` simulations minimum; one-sided plus-one p for total overlap.
- Family correction: in every simulation compute all four lags and record the maximum positive standardized statistic `max_L[(H_L-0.8*n_L)/sqrt(n_L*Var(X))]`. `FAMILY_MAXT_ONE_SIDED_P` is the plus-one exceedance probability relative to the observed maximum.
- Deterministic RNG seed rule: after this file is written, take the first 16 hexadecimal characters of this file's SHA-256 as an unsigned 64-bit integer. Record the protocol SHA and derived seed before outcome calculation. No human seed selection.
- Holm adjustment: apply Holm step-down adjustment to the four exact analytical one-sided raw p-values; descriptive alongside family maxT.
- Stability windows per lag: full, chronological first half, chronological second half, recent100, recent50, recent20. Recent windows and subgroup results are descriptive only and cannot rescue judgment.
- STRONG_CANDIDATE: best observed mean >0.8, family maxT p<=0.05, that lag's first/second-half effects both nonnegative, leakage0, validations PASS.
- INTERESTING_WATCHLIST: at least one lag has raw one-sided p<=0.10 and mean>0.8, but family maxT p>0.05.
- Otherwise: `FAILED_NOT_INTERESTING`.
- No post-result lag expansion, threshold creation, direction reversal, subgroup selection, or protocol modification.
- Protection: official code/DB/gate/threshold/signature/NUMBER/TRIO/PAIR/CORE/State/Decision/Registry changes `0`; EXP-005 FINAL unchanged; EXP-017 not created.

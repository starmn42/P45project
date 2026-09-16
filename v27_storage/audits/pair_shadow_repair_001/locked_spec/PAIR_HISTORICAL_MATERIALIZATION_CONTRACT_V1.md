# PAIR HISTORICAL MATERIALIZATION CONTRACT V1

STATUS = `REVIEW_SPECIFICATION_ONLY_NOT_OFFICIAL`

For each target evaluation round `r`:

1. Freeze `source_end_round = r-1` and its data-prefix hash before candidate formation.
2. Build UNIT→NUMBER→TRIO→valid_for_pair→disjoint PAIR only from source rows through r-1.
3. Compute base PAIR rule signature from the official v1.2 rule payload; dynamic outcomes/context do not alter the signature.
4. Query only COMPLETE representative selection exposures with the same signature and `evaluation_round < r`. Candidate identity exposures are not performance samples.
5. Materialize, separately, integrated PRIMARY, main PRIMARY, integrated exact2/3 SUPPORT, and main exact2/3 SUPPORT counts/rates for OVERALL, RECENT100, RECENT50, RECENT20.
6. Compute Wilson 95%, upper/lower one-sided exact binomial p-values, and canonical evidence labels. PRIMARY and SUPPORT remain separate.
7. If exposure is below the canonical minimum, store explicit `INSUFFICIENT`; do not substitute neutral, fail, zero evidence, or a constant.
8. Compute recent support from the last 100 and 50 prior representative exposures. RECENT20 remains TEST_ONLY. Missing windows are explicit insufficient sample, not a severe result.
9. Compute pair historical risk, bonus dependence, and structure from the same `<r` history; member risk/structure come from their already pre-result contexts.
10. Produce a canonical materialization payload containing signature/version, r, source_end_round, prefix hash, exposure IDs/range, endpoint counts/statistics/evidence, recent state, risk/structure/bonus, and deterministic hash.
11. Stage the payload before PG07/PG08/PG09/risk/structure evaluation and before any access to outcome r.
12. Run the official two-phase prelock/timing/PG13 sequence, then invoke the canonical state precedence including TEST_READY.
13. Finalize prediction/state, verify outcome access count zero, then and only then read outcome r.
14. Add outcome r to history only for r+1 and later.
15. Rollback removes the whole round. Resume recomputes the same materialization hash from the locked `<r` prefix; mismatch is fail-fast.

Forbidden dependencies: outcome r, any round >r, candidate identity as a substitute for selection exposure, current/full-run aggregate reused for an earlier r, or post-outcome rank/state changes.


# P45 TRIO ORBIT V1 PROTOCOL LOCKED 001

- Locked before outcome evaluation: `2026-08-26 KST`
- Scope: independent Experiment Lab research; OFFICIAL ENGINE unchanged and frozen.
- Canonical input: `v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv`
- Expected input SHA-256: `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Evaluation: targets `2..1238`; only target `R-1` MAIN6+BONUS may drive linked selection.
- KTS45 schedule construction, L01..L17, P1..P5, corrected L08 `(2,6,4)`, normalization and ordering: exactly as specified in `P45_WORK_TRIO_ORBIT_V1_고정대연동_백테스트_001.md`.
- Expected schedule SHA-256: `5f212342c6c27fca8eafbc75d20a55fc4be4ca2961a9c70c3a7af0eca26f1075` using UTF-8, LF, terminal newline.
- Fixed competitor: classes `1..22`, five lexicographic groups per class, repeated every 110 targets, target 2 at schedule position 1.
- Linked competitor: seven locked anchor-position patterns, class scan pointer, unused-TRIO eligibility, and reset semantics exactly as specified.
- Primary: per target, at least one of A/B/C is exact `3/3` against MAIN6.
- Support: exact `2/3` is reported separately and cannot rescue primary.
- Paired auxiliary test: exact McNemar.
- Fair-null Monte Carlo: `20,000` histories, seed `20260826`, sequential fair 6/45 plus bonus histories, statistic `linked-primary minus fixed-primary`, one-sided plus-one p-value.
- Judgment: sample under 1000 is low-sample inconclusive; otherwise SUPPORTED only when delta > 0, Monte Carlo p <= 0.05, leakage 0, and all implementation preflights pass. Delta <= 0 or p > 0.05 is `FAILED_NOT_SUPPORTED`.
- Forbidden: outcome-driven rule changes, subgroup rescue, hidden score, successful-TRIO removal, official code/DB/gate/threshold/signature changes, EXP-017 creation, or predictive promotion.

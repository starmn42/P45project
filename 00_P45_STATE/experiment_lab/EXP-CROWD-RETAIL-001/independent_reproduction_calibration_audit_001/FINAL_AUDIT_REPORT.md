# CROWD RETAIL EXP-001 — independent reproduction and propensity calibration audit

## Independence and source

- Parent status preserved: `EXPLORATORY_RETAILER_MODE_CONCENTRATION`.
- Immutable source range: `262~1237`; rounds `1238+` used: `NO`.
- Source SHA-256: `854ca7256219eadf574ac32ad256b84e9a5bfa42ceece09f0a09dd1eed79cd50`.
- Independent implementation does not import the original calculator and uses fresh seeds.

## Independent original-null reproduction

- Deterministic counts: `PASS`.
- S_CELL: original `132`, reproduced `132`.
- E_CELL: original `56.97188240042372`, reproduced `56.97188240042372`.
- S_PAIR / E_PAIR: `469 / 168.8878974918936`.
- Fresh null: `300,000` repetitions, seed `2026082308`, exceedances `0`.
- Fresh p: `0.0000033333222222592593`; null mean `56.97893`.
- q95/q99/q999: `64 / 67 / 71`.
- Status: `INDEPENDENT_REPRODUCTION_PASS`.

## Retailer-propensity calibration

- Train/evaluation: `262~749 / 750~1237`.
- Empirical-Bayes alpha/beta: `2.3854957135043726 / 5.04582203071465`.
- Prior mean/concentration: `0.3210057483223752 / 7.431317744219022`.
- Optimizer: converged, non-boundary, positive-definite observed negative-log-likelihood Hessian.
- Exact conditional sampler toy validation: `PASS`; maximum absolute empirical error `0.00048144278606965935`.
- Evaluation unique retailers: `3,182`; seen-row share: `0.5695437053326003`.
- Duplicate-capable cells: `115`; exposure gate: `PASS`.
- Observed / expected S_CELL: `102 / 45.75567801672646`.
- Excess / enrichment: `56.24432198327354 / 2.2292315275650125`.
- Calibrated null: `300,000`, seed `2026082309`, exceedances `0`, p `0.0000033333222222592593`.
- Null mean and q95/q99/q999: `45.75535333333333`, `52 / 55 / 58`.
- Fixed halves excess: `17.475286776063157 / 38.76903520721037`.
- Top-1/top-5 removed excess: `56.244122349598165 / 55.8007633221721`.
- Deterministic full rerun: `PASS`.
- Final status: `RETAILER_PROPENSITY_ROBUST_EXPLORATORY_CONCENTRATION`.

This does not identify a same person or causal mechanism. It is not a DRAW signal, promotion candidate, official rule, or engine change.

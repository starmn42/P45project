# EXP-CROWD-TOPO-002 CALIBRATION AUDIT 001 — LOCKED NOTE

- audit type: `POST-POSITIVE-RESULT METHODOLOGY/CALIBRATION AUDIT`
- new Experiment: `NO`
- lock timing: `BEFORE CALIBRATION STATISTIC CALCULATION`
- statistic/split/bootstrap/threshold modification after lock: `FORBIDDEN`
- historical data: exactly rounds `1~1237`
- snapshot SHA-256: `1a03abc4babec2cd64eda8c426429747352e412bc1f63e5513f7794aa980ef32`

## Exact combinatorial identity

Let `c(v)` be the arbitrary fixed ticket count at each of the `M=C(45,6)=8,145,060` vertices. No iid purchase assumption is made. For uniform winning main combination W and uniform bonus selection, the selected bonus column contains six distance-1 neighbors forming a clique. Across all `(W,bonus)` states, each exact vertex appears in a selected column 234 times and every unordered Johnson-distance-1 pair appears in the same selected column 5 times.

Therefore:

`E[K2(K2-1)] = 6 E[K1(K1-1)] + (5/39) E[K1*K23]`

where `K23=K2+K3`.

The identity permits arbitrary nonuniform popularity, duplicate purchases, joint purchases, and repeated purchases. It proves that K1-only marginal-heterogeneity calibration is not identifiable: the selected column's second moment necessarily depends on both the exact duplicate term and the Johnson D1 pair term.

## Locked residual

For each round r:

- `RAW_RESID = K2(K2-1) - 6 K1(K1-1) - (5/39) K1 K23`
- `CAL_RESID = M^2 RAW_RESID / [N(N-1)]`
- price/game: rounds 1~87 = 2,000 KRW; rounds 88~1237 = 1,000 KRW
- N is the pre-draw number of sold lines and must exceed 1.

Under a fair main draw, fair bonus, and purchases fixed before the draw, the conditional expectation of CAL_RESID is zero.

## Fixed split and primary audit

- TRAIN diagnostic: rounds `1~800`
- PRIMARY calibration HOLDOUT: rounds `801~1237`, n=437
- holdout geometry: exactly 23 blocks × 19 rounds
- `T_CAL = sqrt(n) mean(CAL_RESID) / sd(CAL_RESID)`
- residuals for bootstrap: `e=CAL_RESID-mean(CAL_RESID)`
- bootstrap: independent Rademacher sign per 19-round block, applied to all residuals in the block
- repetitions: `200000`
- seed: `2026082305`
- two-sided p: `(1 + count(|T*| >= |T_obs|))/200001`

Audit conclusion:

- `P_CAL > 0.01` → `NO_CALIBRATION_TENSION_DETECTED`
- `P_CAL <= 0.01` → `CALIBRATION_IDENTITY_TENSION`

No calibration deviation is a new crowd signal. A tension result requires implementation/source/denominator/temporal/fairness cause audit and blocks further topology extension.

## Locked diagnostics

Report means of selected-column, center-duplicate, D1-pair, predicted sum, and observed-minus-predicted components on the normalized pair-probability scale. Also report TRAIN mean, two HOLDOUT halves, positive mean count across 23 blocks, ten rounds with largest absolute CAL_RESID, and their share of total absolute contribution. No extra p-value or rescue analysis is permitted.

## Interpretation guard

Regardless of outcome, record `K1_ONLY_CALIBRATION_IDENTIFIABLE = NO`. If no tension is found, preserve EXP-002 and its computational reproduction but limit the program interpretation to:

`STRONG INDEPENDENT-UNIFORM NULL REJECTED; TOPOLOGY-SPECIFIC MECHANISM NOT IDENTIFIED.`

The audit does not create an Experiment, confirm novelty, support promotion, change DRAW/official rules, or inspect prospective signal data.


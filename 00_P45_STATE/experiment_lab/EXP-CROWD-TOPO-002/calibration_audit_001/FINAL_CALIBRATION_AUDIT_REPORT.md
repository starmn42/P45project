# EXP-CROWD-TOPO-002 CALIBRATION AUDIT 001

## Final conclusion

- status: `NO_CALIBRATION_TENSION_DETECTED`
- original EXP-002 status: `SUPPORTED_WITHIN_EXPERIMENT` unchanged
- independent reproduction: `INDEPENDENT_REPRODUCTION_PASS` unchanged
- program interpretation: `STRONG INDEPENDENT-UNIFORM NULL REJECTED; TOPOLOGY-SPECIFIC MECHANISM NOT IDENTIFIED`
- new Experiment: `NO`

## Exact identity and identifiability

The audit locked and evaluated:

`E[K2(K2-1)] = 6 E[K1(K1-1)] + (5/39) E[K1*K23]`.

This identity allows arbitrary fixed ticket popularity and purchase dependence. K1-only marginal-heterogeneity calibration is **not identifiable**, because selected-column second moments require both:

1. exact duplicate term `K1(K1-1)`;
2. Johnson distance-1 pair term `K1*K23`.

## Locked primary audit

- data: rounds `1~1237`, SHA-256 `1a03abc4babec2cd64eda8c426429747352e412bc1f63e5513f7794aa980ef32`
- audit protocol SHA-256: `b13666657e524a555a6387f180e2aa4fff1a1860366ac72bd120ab3cc0ba91ff`
- M: `8,145,060`
- D1 degree: `234`
- TRAIN mean CAL_RESID: `-1.6541259380883246`
- HOLDOUT mean CAL_RESID: `6.039406338771726`
- HOLDOUT T_CAL: `1.1281510037684361`
- bootstrap: `200000`, seed `2026082305`
- two-sided exceedances: `39540`
- P_CAL: `0.1977040114799426`
- locked tension threshold: `0.01`

Because P_CAL is greater than 0.01, the audit did not detect clear tension with the arbitrary-crowd exact combinatorial identity. This does not prove equality.

## Decomposition diagnostics

- selected-column component mean: `42.077843660300175`
- center-duplicate component mean: `6.2331612059814585`
- D1-pair component mean: `29.805276115546988`
- predicted component mean: `36.03843732152845`
- observed minus predicted: `6.039406338771726`

## Temporal and spike diagnostics

- HOLDOUT first-half mean: `2.6369587558403387`
- HOLDOUT second-half mean: `9.426317631370093`
- positive 19-round blocks: `14/23`
- top-10 absolute residual share: `38.33000557369263%`
- largest absolute residual: round `1057`, CAL_RESID `2256.686107995233`

These diagnostics do not alter the primary audit and no additional p-values were calculated.

## Interpretation restriction

EXP-002 rejected an independent-and-uniform 39-column occupancy null. Once generic exact duplicate concentration and D1-pair concentration are allowed, the rejection cannot be interpreted as independent evidence for a topology-specific crowd mechanism. It does not identify popularity, numbers, combinations, causality, DRAW effects, or novelty.

- novelty: `NOVELTY_NOT_CONFIRMED`
- promotion candidate: `NO`
- prospective signal peeking: `0`
- official/DRAW engine changes: `0`
- focused tests: `5/5 PASS`


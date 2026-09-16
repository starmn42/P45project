# EXP-CROWD-TOPO-002-V1 Independent Reproduction Result

## Final status

- status: `INDEPENDENT_REPRODUCTION_PASS`
- independent calculator: `src/p45_reproductions/crowd_topology_exp002_v1_reproduction.py`
- original calculator imported: `NO`
- fresh null path: `39-category Multinomial → fixed column index 0`
- independent empirical/external replication: `NO`
- novelty: `NOVELTY_NOT_CONFIRMED`
- promotion candidate: `NO`

## Protected input and original evidence

- data: exactly rounds `1~1237`, 1,237 rows
- round 1238+ used: `NO`
- snapshot SHA-256: `1a03abc4babec2cd64eda8c426429747352e412bc1f63e5513f7794aa980ef32`
- original protocol SHA-256: `7d32357ff787a50e7ef67ecbcf8e38780b2886b0bf6d4ffedb1871cf35edd8c3`
- original report SHA-256: `fa249ddd3872773a4e5491c6849532be3d17b05724f8a777c7edaba1da594065`
- original calculator SHA-256: `6b7a39481ccb0e799b56aed32634c7d4128c698e18a1411ec9df99e41a77da03`
- original result SHA-256: `993a3ef157a149e4d2dfb846e3aaf7a105e5f1c316d4e68dd564e83ca62dbe58`
- all original hashes before/after reproduction: `IDENTICAL`

## Deterministic reproduction

|Metric|Original|Reproduced|Absolute delta|
|---|---:|---:|---:|
|TRAIN D|0.757709658462612|0.7577096584626122|2.220446049250313e-16|
|HOLDOUT D|10.198417703972382|10.198417703972382|0|
|HOLDOUT Q|4893.708536635931|4893.708536635931|0|
|H1 D|0.962145939528479|0.962145939528479|0|
|H2 D|19.392514711501015|19.392514711501015|0|
|Top 1 removed D|1.9686179886970279|1.9686179886970279|0|
|Top 5 removed D|1.0316948798049101|1.0316948798049101|0|
|Top 10 removed D|0.7751211403504912|0.7751211403504912|0|

- positive 19-round blocks: `22/23`, exact match
- tolerance: `1e-10`
- deterministic target comparison: `PASS`

## Fresh primary null simulation

- repetitions: `300000`
- seed: `2026082304` (original seed not reused)
- exceedances: `0`
- one-sided p: `0.0000033333222222592593`
- Monte Carlo standard error: `0.0000033333222222592593`
- null D mean: `-0.00010782564430489311`
- null D q95: `0.11396841934682223`
- null D q99: `0.16427996975756956`
- null D q99.9: `0.22195703771186281`
- observed D greater than q99.9: `YES`

## Spike concentration

- top 10 observed contributions account for `84.51120001824396%` of HOLDOUT Q.
- the prespecified top-1, top-5, and top-10 removed D values remain positive.
- no observations were removed from PRIMARY and no new trimmed p-value was calculated.

## STRONG-NULL LIMITATION

The PRIMARY H0 is not merely that the bonus draw is uniform. `K2 | K23 ~ Binomial(K23,1/39)` assumes D1-shell winning-ticket occupancy is both independent and uniform across 39 columns. Rejection may arise from non-uniformity, clustering, correlated ticket choices, mixtures of player strategies, or other mechanisms. EXP-002 does not identify which mechanism caused the rejection.

This result computationally reproduces the locked experiment. It does not validate Johnson topology generally, reverse EXP-CROWD-TOPO-001 V1, recover the 8.1-million-combination popularity surface, identify particular numbers/combinations, establish causality, affect DRAW probability/recommendations, or confirm novelty.

## Guards

- focused tests: `6/6 PASS`
- prospective protocol changed: `NO`
- prospective signal peeking: `0`
- DRAW engine changed: `0`
- official engine: `FROZEN`
- original experiment status: `SUPPORTED_WITHIN_EXPERIMENT` unchanged


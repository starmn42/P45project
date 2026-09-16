# EXP-CROWD-TOPO-002-V1 Independent Implementation Reproduction 001

- purpose: computationally reproduce the locked EXP-CROWD-TOPO-002-V1 result through an independent implementation
- new discovery hypothesis: `NO`
- original calculator import: `FORBIDDEN`
- original calculator/result/protocol/snapshot modification: `FORBIDDEN`
- historical range: exactly `1~1237`
- round 1238+ use: `NO`
- immutable snapshot SHA-256: `1a03abc4babec2cd64eda8c426429747352e412bc1f63e5513f7794aa980ef32`

## Independent calculation

Read raw K2 and K3 from the immutable CSV. Recompute `n=K2+K3`, `x=K2`, `p0=1/39`, `mu=np0`, `var=np0(1-p0)`, `R=(x-mu)^2/var`, and `D=mean(R)-1` without importing the original calculator. Calculate TRAIN, HOLDOUT, half-period, 19-round block signs, and locked top-1/5/10 removal diagnostics first. Only after those values exist may the original result JSON be opened for tolerance comparison.

Deterministic target tolerance is absolute delta `<=1e-10`; block count must match exactly.

## Fresh primary null

- method: for every holdout round and simulation, generate a full 39-category Multinomial with equal probabilities and read fixed column index 0
- repetitions: `300000`
- seed: `2026082304`
- one-sided p: `(1 + count(D* >= D_obs))/300001`
- PASS requires deterministic targets match, observed D positive, and fresh p `<=0.05`.

The original MC cache, random stream, and seed are not used.

## Strong-null limitation

`K2 | K23 ~ Binomial(K23,1/39)` is not merely a uniform bonus-draw null. It assumes independent and uniform occupancy of D1-shell winning tickets across 39 columns. Rejection can arise from non-uniformity, clustering, correlated purchases, or mixtures of player strategies. This reproduction cannot identify which mechanism is causal.

The result cannot establish Johnson topology generally, reverse EXP-001, recover ticket popularity, identify numbers/combinations, affect DRAW probability/recommendations, or confirm novelty. Promotion candidate remains NO.


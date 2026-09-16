# EXP-CROWD-TOPO-001-V1 LOCKED PROTOCOL

## Authority and boundary

- Logical ID: `EXP-CROWD-TOPO-001-V1`
- Title: `JOHNSON J(45,6) DISTANCE-1 LOCAL AUTOCORRELATION`
- Domain: `CROWD / PRIZE_SHARE`, separate from DRAW
- Idea linkage: `IDEA-20260823-CROWD001`
- Status at publication: `LOCKED_BEFORE_OUTCOME_RELATION_ANALYSIS`
- Historical range: exactly rounds 1–1237
- Future rounds 1238+: forbidden
- Novelty: `NOVELTY_NOT_CONFIRMED`
- Official effect: `NONE`

## Graph and shell

- `M = C(45,6) = 8,145,060`
- graph: Johnson `J(45,6)`
- `d_J(A,B) = 6 - |A ∩ B|`
- distance-1 degree: `D1 = C(6,1) C(39,1) = 234`
- K2 shell size: 6
- K3 shell size: 228
- K23: `K2 + K3`, the complete distance-1 shell winning-ticket count

Distance 1 is the single V1 primary family. Distance 2 or higher, split K2/K3 selection, feature conditioning, marginal residualization, custom similarity, weighted adjacency, threshold tuning, and period selection are prohibited.

## Target and primary observable

For market `t`, exact-ticket choice probability is `q_t(v)`. Define the distance-1 neighbor average `A1_t(v)` and target the historical average of `Cov(q_t(v), A1_t(v))` over uniform vertices.

- H1: mean distance-1 local covariance > 0
- H0: mean distance-1 local covariance = 0
- opposite: mean distance-1 local covariance < 0

For round r:

- `N_r = wholEpsdSumNtslAmt / price_per_game`
- `K1_r = rnk1WnNope`
- `K23_r = rnk2WnNope + rnk3WnNope`
- `LOCAL_EXCESS_r = M^2 K1_r K23_r / (N_r (N_r-1) D1) - 1`
- primary effect `THETA = mean(LOCAL_EXCESS_r)`

## Secondary diagnostic

- `VAR_EXCESS_r = M^2 K1_r(K1_r-1)/(N_r(N_r-1)) - 1`
- `V_HAT = mean(VAR_EXCESS_r)`
- only when `V_HAT > 0`, report `RHO1_HAT = THETA / V_HAT`

This diagnostic cannot rescue the primary result. No clipping or alternative post-hoc normalization is allowed.

## Fixed data and split

- immutable snapshot rows: 1,237, exactly rounds 1–1237
- price: rounds 1–87 at 2,000 KRW; rounds 88–1237 at 1,000 KRW
- TRAIN: 1–800
- confirmatory HOLDOUT: 801–1237, n=437
- no post-hoc exclusion or period change

## Sequential gate and inference

1. Compute `THETA_TRAIN`.
2. If `THETA_TRAIN <= 0`, stop as `FAILED_EARLY_TRAIN_DIRECTION`; do not run holdout inference or uniform MC.
3. If TRAIN passes, compute holdout `THETA`, studentized `T_OBS`, and the primary block-wild p-value.

Primary bootstrap:

- 23 fixed consecutive blocks of 19 rounds covering 801–1237
- residual `e_r = x_r - mean(x)`
- one Rademacher sign per block, shared by all 19 residuals
- `x*_r = sign_block e_r`
- `T* = sqrt(n) mean(x*) / sd(x*)`
- 100,000 repetitions
- seed `2026082301`
- one-sided `P_BLOCK_WILD = (1 + count(T* >= T_OBS))/100001`

Primary pass requires both `THETA_HOLDOUT > 0` and `P_BLOCK_WILD <= 0.05`.

Secondary uniform MC, only after TRAIN passes:

- for each actual holdout N, sample multinomial `(K1,K23,REST)` with probabilities `(1/M, 234/M, 1-235/M)`
- 100,000 sequences
- seed `2026082302`
- one-sided `P_UNIFORM_MC`
- diagnostic only; never part of the primary judgment

Temporal diagnostics: 23 block THETAs, positive-block count, median, first-11-block mean, and last-12-block mean. They cannot alter the final judgment.

## Final judgment

- TRAIN fail: `FAILED_EARLY_TRAIN_DIRECTION`
- TRAIN pass but holdout direction or p-value fail: `FAILED`
- TRAIN and holdout pass: `SUPPORTED_WITHIN_EXPERIMENT`

Even if supported: promotion candidate remains NO, independent reproduction and separate prospective/external confirmation are required, novelty is not confirmed, and no recommendation or DRAW connection is permitted.

## Determinism and protection

- Re-run the locked snapshot/calculator/seeds and require matching primary and secondary outputs within numerical tolerance.
- Any mismatch is `REPRODUCTION_MISMATCH` and stops the run.
- Official engine, DRAW engine, Prospective-001, NUMBER/TRIO/PAIR/CORE, gates, thresholds, signatures, and historical evidence are read-only.

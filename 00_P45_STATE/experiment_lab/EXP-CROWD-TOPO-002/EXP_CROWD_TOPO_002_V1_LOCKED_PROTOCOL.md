# EXP-CROWD-TOPO-002-V1 LOCKED PROTOCOL

- protocol version: `EXP-CROWD-TOPO-002-PROTOCOL-1.0`
- logical ID: `EXP-CROWD-TOPO-002-V1`
- title: `RANDOM-BONUS COLUMN PROBE — D1-SHELL OVERDISPERSION`
- lock timing: `BEFORE OUTCOME ANALYSIS`
- outcome viewed before lock: `NO`
- domain: `CROWD / PRIZE-SHARE LAB`, isolated from DRAW
- novelty: `NOVELTY_NOT_CONFIRMED`

## Structure identity

For a winning main set W in `J(45,6)`, one main number is removed in 6 ways and one outside number is inserted in 39 ways. The distance-1 degree is `6 × 39 = 234`. Each outside number is one column of 6 exact neighbors. The official bonus selects one column: K2 shell size 6. The other 38 columns form the K3 shell: `38 × 6 = 228`. Therefore `K23 = K2 + K3` and the selected-column null probability is exactly `p0 = 6/234 = 1/39`.

Required assertions: D1 degree 234; K2 size 6; K3 size 228; p0 1/39; official prize mapping PASS. Any failure yields `DESIGN_BLOCKED_SHELL_IDENTITY`.

## Data lock

- immutable input: `v27_storage/experiments/crowd_topology_exp001_v1/exp_crowd_topo_001_v1_draws_1_1237.csv`
- required SHA-256: `1a03abc4babec2cd64eda8c426429747352e412bc1f63e5513f7794aa980ef32`
- historical range: exactly `1~1237`
- K2 source field: `rnk2WnNope`; K3 source field: `rnk3WnNope`
- source semantics evidence: `EXP_CROWD_TOPO_001_V1_SOURCE_SCHEMA_PREFLIGHT.md`, PASS before prior outcome relation analysis
- round 1238+: forbidden
- K2/K3 must be complete nonnegative integers and K23 must be positive for every round.

## Hypothesis and primary statistic

For each round r, fix `n_r = K2_r + K3_r`, observe `x_r = K2_r`, and set `p0 = 1/39`.

- H0: `X_r | n_r ~ Binomial(n_r, 1/39)`, independent between tickets and rounds under the simulation null.
- H1: K2 conditional on K23 is overdispersed relative to that null.
- opposite: binomial-level dispersion or underdispersion.
- `mu_r = n_r p0`
- `var_r = n_r p0(1-p0)`
- `R_r = (x_r-mu_r)^2/var_r`
- primary effect: `D = mean(R_r)-1`
- primary direction: one-sided overdispersion only.

Descriptive only: `Q=sum(R)`, `MAX_ABS_Z`, `TOP10_Q_SHARE`. They do not affect judgment.

## Fixed split and sequential gate

- TRAIN: rounds `1~800`
- CONFIRMATORY HOLDOUT: rounds `801~1237`, N=437
- TRAIN PASS iff `D_TRAIN > 0`.
- If `D_TRAIN <= 0`, final is `FAILED_EARLY_TRAIN_DIRECTION`; holdout inferential Monte Carlo is forbidden.

## Holdout primary Monte Carlo

Only after TRAIN PASS, independently simulate each holdout round with its observed n fixed:

- `X_r* ~ Binomial(n_r,1/39)`
- `D* = mean(R_r*)-1`
- repetitions: `200000`
- seed: `2026082303`
- one-sided p: `(1 + count(D* >= D_observed))/200001`
- PASS iff `D_HOLDOUT > 0` and `P_MC <= 0.05`.
- record exceedance count and Monte Carlo standard error.

## Prespecified diagnostics

- holdout H1 `801~1018` (218), H2 `1019~1237` (219): report D and sign consistency only.
- split holdout into exactly 23 consecutive blocks of 19 and report positive block count; no extra p-value.
- remove the largest 1, 5, and 10 observed holdout R contributions and report D on the remaining observations; no trimming of the primary analysis.

## Researcher degrees of freedom

The primary family contains exactly one statistic: `mean Pearson contribution - 1`. This V1 forbids K1, D2/D3, birthday/number categories, bonus categories or specific bonus identity, column feature search, ratio thresholds, alternative primary statistics, period selection, result-driven trimming, and sales-type splits.

## Final status

- baseline conflict: `EXP_CROWD_TOPO_002_BLOCKED_BASELINE_CONFLICT`
- identity failure: `DESIGN_BLOCKED_SHELL_IDENTITY`
- data failure: `DATA_BLOCKED` or `DATA_BLOCKED_ZERO_K23`
- train failure: `FAILED_EARLY_TRAIN_DIRECTION`
- train pass but holdout direction/p-value failure: `FAILED`
- train pass, holdout D positive, p<=0.05, deterministic rerun PASS: `SUPPORTED_WITHIN_EXPERIMENT`
- rerun mismatch: `REPRODUCTION_MISMATCH`

SUPPORTED does not establish a mechanism, causality, particular popular numbers/combinations, DRAW probability, recommendation relevance, or novelty. Promotion candidate remains NO and independent reproduction remains NOT_YET.

## Deterministic rerun and protection

The same locked input, code, and seed must be run twice. All primary and diagnostic outputs must match exactly. The official engine remains FROZEN; DRAW_DISCOVERY_PAUSE remains ACTIVE; EXP-017 remains NOT_CREATED; NO-PICK remains UNRESOLVED; prospective protocol/ledger and EXP-CROWD-TOPO-001 evidence remain immutable.


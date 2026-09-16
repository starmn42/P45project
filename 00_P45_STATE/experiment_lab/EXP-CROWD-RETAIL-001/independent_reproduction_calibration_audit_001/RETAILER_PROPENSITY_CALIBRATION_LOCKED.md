# RETAILER PROPENSITY CALIBRATION AUDIT 001 — LOCKED

- Parent experiment: `EXP-CROWD-RETAIL-001-V1`
- This is an audit, not a new experiment and not an official-engine rule.
- Immutable input: rounds `262~1237`, SHA-256 `854ca7256219eadf574ac32ad256b84e9a5bfa42ceece09f0a09dd1eed79cd50`.
- Rounds `1238+` are forbidden.
- Nuisance training: `262~749`; evaluation: `750~1237`.
- Fit one Beta-Binomial empirical-Bayes prior by marginal likelihood on training retailers; freeze alpha/beta thereafter.
- At evaluation round R, retailer propensity uses winner rows strictly before R. R labels update history only after its null distribution is fixed.
- Condition on the observed round manual total. Subset probability is proportional to the product of pre-round retailer odds.
- Exact conditional Bernoulli sampling is defined by elementary-symmetric-polynomial dynamic programming; PPS and Wallenius approximations are forbidden.
- PRIMARY: evaluation-period count of retailer-round cells with manual multiplicity at least two.
- Monte Carlo: `300,000`, seed `2026082309`, upper one-sided p-value `(1+exceedances)/300001`.
- Exposure: duplicate-capable cells at least 20 and expected PRIMARY at least 5.
- Robust status requires exposure PASS, positive excess, p <= 0.01, and deterministic rerun PASS.
- Fixed diagnostics only: `750~993`, `994~1237`, top-1 and top-5 multiplicity removal. No extra p-values.
- No same-person inference, DRAW signal, promotion, tuning, subgroup search, or official-engine effect.

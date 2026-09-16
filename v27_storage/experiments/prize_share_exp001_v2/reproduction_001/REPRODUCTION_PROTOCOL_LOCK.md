# EXP-PRIZE-001-V2 INDEPENDENT REPRODUCTION 001

- Type: independent reproduction audit; not a new discovery hypothesis
- Source of rules: locked V2 protocol SHA `479c83f5905d1bcd928e5b388420a41259c413836711202fd30704e7b4b9d5b7`
- Input snapshot SHA: `86b14968aca3ad10b854f9d5c53eba00a786627f73e353938e1e801dc888fa21`
- Historical range: exactly `1~1237`
- Round 1238+: forbidden
- Fresh permutation seed: `2026082102`
- Fresh permutations: `100,000`

## Independence

The calculator in this directory must not import, call, copy, or read the original calculator, original result JSON, original permutation cache, or original walkforward intermediates. It reads only the immutable CSV snapshot and independently derives birthday count, historical game price, and sold lines from raw snapshot columns.

## Frozen acceptance

- `abs(beta_train_new - 0.0143280465) <= 1e-8`
- `abs(beta_holdout_new - 0.0402626277) <= 1e-8`
- `abs(wf_delta_ll_new - 3.4704933) <= 1e-6`
- fresh permutation p `<=0.05`
- fresh beta holdout `>0`
- `abs(p_fresh - 0.0199998) <=0.005`
- data/future/original-file protection checks all pass

Failure is preserved without solver, seed, row, threshold, or rounding retuning.

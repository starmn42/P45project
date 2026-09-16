# P45 EXP-019 PROTOCOL LOCK RECORD 001

- Experiment ID: `EXP-019`
- Full ID: `EXP-DRAW-20260827-019-V1`
- Title: `SALES-ADJUSTED BIRTHDAY-RANGE CROWD EFFECT V1`
- Protocol path: `v27_storage/experiments/exp019_sales_adjusted_birthday_crowd_effect_v1_001/P45_EXP_019_SALES_ADJUSTED_BIRTHDAY_CROWD_EFFECT_V1_PROTOCOL_001.md`
- Protocol SHA-256: `220d59aa8c50e11c74f6146061784b8f5e0413c5a7013758a47891404e2f4d5c`
- Lock timestamp: `2026-08-27T21:50:04+09:00`
- Canonical latest: `1238`
- Canonical source SHA-256: `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Price regime: `1000 KRW per game`
- Historical universe: `88..1238`
- Development: `88..867`
- Holdout: `868..1238`
- Primary predictor: `BIRTHDAY_RANGE_COUNT / MAIN6 labels 1..31`
- Combination universe: `8,145,060`
- Primary model: `Poisson log-linear count model with log(LAMBDA) offset, intercept, and B_t`
- Primary statistic: `U=sum[B_t*(W_t-c*LAMBDA_t)]`
- Permutations: `100000`
- Seed: `20260827`
- RNG: `Python random.Random; independently initialized per evaluated split`
- P-value: `(1+count(U_perm>=U_obs))/100001`, one-sided upper
- Outcome relation peek: `0`
- Historical relation calculation: `NO`
- Official engine: `FROZEN`
- FUTURE_LEAKAGE: `0`

Bulk official winner/sales acquisition may begin only after this lock. The V1 protocol is immutable after this record.

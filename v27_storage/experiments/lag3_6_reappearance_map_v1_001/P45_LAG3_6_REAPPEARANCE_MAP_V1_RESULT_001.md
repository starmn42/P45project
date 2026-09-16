# P45 LAG3–6 REAPPEARANCE MAP V1 RESULT 001

## Summary

|LAG|실제 평균 재등장수|무작위 기대|차이|우연 가능성(raw)|4개 동시검사 maxT p|판정|
|---|---:|---:|---:|---:|---:|---|
|L=3|0.788663968|0.800000000|-0.011336032|0.699813155|0.862161378|FAMILY_MEMBER|
|L=4|0.768233387|0.800000000|-0.031766613|0.925829425|0.862161378|FAMILY_MEMBER|
|L=5|0.806163828|0.800000000|+0.006163828|0.397005514|0.862161378|FAILED_NOT_INTERESTING|
|L=6|0.775162338|0.800000000|-0.024837662|0.871024388|0.862161378|FAMILY_MEMBER|
|L=2 REFERENCE ONLY|0.840485830|0.800000000|+0.040485830|PRIMARY two-sided 0.069534898|family 제외|Walkforward NOT_REPRODUCED / FINAL FAILED|

## Precheck and lock

- PRECHECK: `PASS`
- Canonical latest / SHA-256: `1238 / 1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Protocol SHA-256: `f8d72775f2e3de92f1cdfa2c58a0ff7a2e4ff2681624044d8619ae3589d870ec`
- Monte Carlo histories / deterministic seed: `100000 / 17930843828938595986`
- MAIN6 only / BONUS usage: `YES / 0`

## Per-lag results

### L=3

- Target / valid rounds / exposures: `4..1238 / 1235 / 7410`
- Hits / mean / expected / difference: `974 / 0.788663968 / 0.800000000 / -0.011336032`
- Reappearance rate / expected / difference: `13.144399460% / 13.333333333% / -0.188933873%`
- Analytical one-sided p: `0.699813155042` — 우연 가능성 약 69.98% — 무작위 실험 100번 중 약 70.0번 이 정도 이상으로 좋아 보일 수준
- Fair-sequence Monte Carlo one-sided p: `0.69814301857`
- Holm-adjusted p: `1`

### L=4

- Target / valid rounds / exposures: `5..1238 / 1234 / 7404`
- Hits / mean / expected / difference: `948 / 0.768233387 / 0.800000000 / -0.031766613`
- Reappearance rate / expected / difference: `12.803889789% / 13.333333333% / -0.529443544%`
- Analytical one-sided p: `0.925829425115` — 우연 가능성 약 92.58% — 무작위 실험 100번 중 약 92.6번 이 정도 이상으로 좋아 보일 수준
- Fair-sequence Monte Carlo one-sided p: `0.926430735693`
- Holm-adjusted p: `1`

### L=5

- Target / valid rounds / exposures: `6..1238 / 1233 / 7398`
- Hits / mean / expected / difference: `994 / 0.806163828 / 0.800000000 / +0.006163828`
- Reappearance rate / expected / difference: `13.436063801% / 13.333333333% / +0.102730468%`
- Analytical one-sided p: `0.39700551435` — 우연 가능성 약 39.70% — 무작위 실험 100번 중 약 39.7번 이 정도 이상으로 좋아 보일 수준
- Fair-sequence Monte Carlo one-sided p: `0.39670603294`
- Holm-adjusted p: `1`

### L=6

- Target / valid rounds / exposures: `7..1238 / 1232 / 7392`
- Hits / mean / expected / difference: `955 / 0.775162338 / 0.800000000 / -0.024837662`
- Reappearance rate / expected / difference: `12.919372294% / 13.333333333% / -0.413961039%`
- Analytical one-sided p: `0.871024387691` — 우연 가능성 약 87.10% — 무작위 실험 100번 중 약 87.1번 이 정도 이상으로 좋아 보일 수준
- Fair-sequence Monte Carlo one-sided p: `0.869131308687`
- Holm-adjusted p: `1`


## Family correction

- Observed best lag / max standardized statistic: `L=5 / 0.276092779286`
- FAMILY_MAXT_ONE_SIDED_P: `0.862161378386`
- Holm adjusted p L3/L4/L5/L6: `1 / 1 / 1 / 1`

## Period stability (mean and difference from 0.8)

|lag|full|first half|second half|recent100|recent50|recent20|
|---|---:|---:|---:|---:|---:|---:|
|L=3|0.788663968 (-0.011336032)|0.786407767 (-0.013592233)|0.790923825 (-0.009076175)|0.730000000 (-0.070000000)|0.620000000 (-0.180000000)|0.500000000 (-0.300000000)|
|L=4|0.768233387 (-0.031766613)|0.753646677 (-0.046353323)|0.782820097 (-0.017179903)|0.720000000 (-0.080000000)|0.680000000 (-0.120000000)|0.850000000 (+0.050000000)|
|L=5|0.806163828 (+0.006163828)|0.807131280 (+0.007131280)|0.805194805 (+0.005194805)|0.840000000 (+0.040000000)|0.820000000 (+0.020000000)|0.800000000 (+0.000000000)|
|L=6|0.775162338 (-0.024837662)|0.784090909 (-0.015909091)|0.766233766 (-0.033766234)|0.680000000 (-0.120000000)|0.680000000 (-0.120000000)|0.350000000 (-0.450000000)|

Recent windows are descriptive only and do not change the judgment.

## Final judgment

- Best lag: `L=5`
- FINAL: `FAILED_NOT_INTERESTING`
- Easy interpretation: `우연 가능성 약 39.70% — 무작위 실험 100번 중 약 39.7번 이 정도 이상으로 좋아 보일 수준`. Four-lag selection is controlled by family maxT; no favorable lag or period was selectively promoted.
- EXP-005 L2 FINAL: `FAILED` unchanged; not rerun and not included in this family.
- FUTURE_LEAKAGE: `0`
- EXP-017: `NOT_CREATED`
- OFFICIAL ENGINE, code, DB, gate, threshold, signature, NUMBER/TRIO/PAIR/CORE, State/Decision/Registry changes: `0`

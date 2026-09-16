# P45 ENDING × CUMULATIVE FREQUENCY INTERACTION V1 RESULT 001

## Easy result first

- 같은 끝수 후보 안에서 과거 누적 출현빈도가 낮은 번호가 약간 더 적중한 방향이었지만, 공정추첨으로 충분히 흔하게 생길 수 있는 차이다.
- 관측 `TOTAL_SCORE = -254.5`; 적중 후보당 평균 centered rank 위치는 `-0.114074`이다.
- 100,000개 전체 공정 시퀀스 중 약 25.04%가 관측값 이상으로 극단적이었다. 후보 구조와 적중 개수까지 고정한 조건부 검산도 약 25.00%였다.
- FINAL: `FAILED_NOT_INTERESTING`

## Precheck and lock

- PRECHECK: `PASS`
- Canonical latest / SHA-256: `1238 / 1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- EXP-006 / EXP-013 source verification: `PASS / PASS`
- EXP-006 / EXP-013 FINAL: `FAILED / FAILED_EARLY` unchanged
- Protocol SHA-256: `3db9d2fb4c82f1d858f49369da5ea8bfbc3268017528a4b25b903dee64489de1`
- Deterministic seed / simulations: `4447818083767349720 / 100000`
- Evaluated targets: `201..1238 = 1038`

## Candidate structure and primary effect

- Total candidate exposures: `16698`
- Total candidate hits: `2231`
- Candidate hit rate: `0.133608815427`
- EXP-006 fair expectation `6/45`: `0.133333333333`
- Rate difference: `+0.000275482094` (`+0.027548%p`)
- TOTAL_SCORE: `-254.5`
- Mean centered frequency-rank among hit candidates: `-0.114074406096`
- Mean raw within-candidate frequency rank among hit candidates: `8.834603316898`
- Direction: `LOW_FREQUENCY_CANDIDATES_MORE_HITS`

The raw within-candidate rank is descriptive because candidate-set sizes vary. The centered rank is the comparable interaction quantity and is the registered primary score component.

## Random-null tests

- PRIMARY full-sequence fair-draw Monte Carlo: extreme `25039 / 100000`; add-one two-sided p `0.250397496025`
- Conditional candidate-identity randomization: extreme `24996 / 100000`; add-one two-sided p `0.249967500325`
- Full-sequence null mean score: `0.008545`
- Conditional null mean score: `0.547310`

## Period stability

| period | targets | TOTAL_SCORE | mean round score |
|---|---:|---:|---:|
| full | 1038 | -254.5 | -0.245183044 |
| first half (201..719) | 519 | -60.5 | -0.116570328 |
| second half (720..1238) | 519 | -194.0 | -0.373795761 |
| recent100 | 100 | -97.5 | -0.975000000 |
| recent50 | 50 | -64.0 | -1.280000000 |
| recent20 | 20 | -27.5 | -1.375000000 |

First and second halves have the same negative direction. Recent windows are descriptive only and do not alter the judgment.

## Validation and protection

- Structure validation: `PASS`
- Candidate score sum-zero checks: `PASS` for every target
- Target trace: exactly `1038` rows, `201..1238`
- FUTURE_LEAKAGE: `0`
- EXP-006 / EXP-013 changes: `0 / 0`
- EXP-017: `NOT_CREATED`
- Recommendation, threshold, hidden score, arbitrary weighting, post-result subgroup: `0`
- OFFICIAL ENGINE/gate/threshold/signature/DB and NUMBER/TRIO/PAIR/CORE changes: `0`

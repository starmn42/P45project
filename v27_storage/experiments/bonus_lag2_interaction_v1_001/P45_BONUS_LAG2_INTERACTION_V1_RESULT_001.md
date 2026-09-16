# P45 BONUS × LAG-2 INTERACTION V1 RESULT 001

## Easy result first

- 관측 covariance는 -0.033316이고 방향은 직전 BONUS가 높을수록 재등장이 늘어나는 쪽. 아무 관계 없는 공정 시퀀스에서도 100번 중 약 45.64번 이 정도 이상의 관계가 나타날 수 있다.
- Effect: covariance `-0.033315528744`, slope `-0.008070384356`, correlation `-0.020655395968`.
- First/second covariance: `-0.035182392308 / -0.030267801971`; same direction: `YES`.
- FINAL: `FAILED_NOT_INTERESTING`

## Precheck and lock

- PRECHECK: `PASS`
- Canonical latest / SHA: `1238 / 1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- EXP-005 / EXP-015 source verification: `PASS / PASS`
- Protocol SHA: `d3f271d0869dbba0da466cb77835b8b7638c39fe99d7da8f7fe3c5ddffcac6c3`
- MC seed / simulations: `15272394426792393632 / 100000`
- Evaluated targets: `3..1238 = 1236`

## Primary

- Covariance / regression slope / correlation: `-0.033315528744 / -0.008070384356 / -0.020655395968`
- Direction: `NEGATIVE_HIGH_BONUS_MORE_REAPPEARANCE`
- PRIMARY_TWO_SIDED_MC_P: `0.456445435546`; extreme `45644/100000`
- Conditional circular-shift p: `0.483009708738`; extreme `597/1236`

## BONUS rank descriptive only

|rank|rounds|mean lag2 overlap|difference from 0.8|
|---:|---:|---:|---:|
|1|204|0.843137255|+0.043137255|
|2|175|0.800000000|+0.000000000|
|3|192|0.822916667|+0.022916667|
|4|144|0.854166667|+0.054166667|
|5|184|0.826086957|+0.026086957|
|6|166|0.885542169|+0.085542169|
|7|171|0.865497076|+0.065497076|

## Stability

|period|N|covariance|slope|correlation|
|---|---:|---:|---:|---:|
|full|1236|-0.033315529|-0.008070384|-0.020655396|
|first_half|618|-0.035182392|-0.008193228|-0.020552310|
|second_half|618|-0.030267802|-0.007639520|-0.020156223|
|recent100|100|-0.387800000|-0.093753022|-0.271537015|
|recent50|50|-0.460800000|-0.108382727|-0.312810223|
|recent20|20|-0.340000000|-0.095505618|-0.281424556|

Recent windows and rank rows are descriptive only and do not change the judgment.

## Protection

- FUTURE_LEAKAGE: `0`
- EXP-005 / EXP-015 FINAL: `FAILED / FAILED_EARLY` unchanged
- EXP-017: `NOT_CREATED`
- Recommendation, rank threshold, hidden score: `0 / 0 / 0`
- Official protected changes: `0`

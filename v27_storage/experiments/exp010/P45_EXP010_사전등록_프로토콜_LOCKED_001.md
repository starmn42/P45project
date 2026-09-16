# P45 EXP-010 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-010`
- 연구명: `DRAW-SUM LAG-1 AUTOCORRELATION — PERSISTENCE / REVERSAL`
- Family: `SERIAL_COMPOSITION_FAMILY_V1`
- Family Members: `EXP-009 PARITY-LOAD`, `EXP-010 DRAW-SUM`
- 상태: `LOCKED / READY_FOR_BACKTEST`
- LOCK 승인일: `2026-08-21`
- 실제 EXP-010 outcome 조회 전 LOCK: `YES`
- 백테스트 실행 전 LOCK: `YES`
- Walkforward 실행 전 LOCK: `YES`
- 추천번호 생성: `NO`
- 공식 ENGINE 변경: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

> `BATCH_WHEN_SAFE`에 따라 DRAFT 사용자 산출물 없이 실제 outcome 계산 전에 이 LOCKED 기준본을 먼저 생성했다.
> EXP-009 결과를 이미 알고 있으므로, EXP-010은 EXP-009와 함께 `SERIAL_COMPOSITION_FAMILY_V1`로 묶어 family-wise 보정을 사전 고정한다.
> EXP-010 종료 후 range/median/SD 등 scalar-summary lag-1 지표를 결과 따라 연속 추가하는 것은 금지한다.

## 1. 연구 목적
회차 MAIN 6개 번호의 합 `S_T`가 직전 회차에서 다음 회차로
지속(persistence) 또는 반전(reversal)되는 lag-1 serial dependence를 가지는지 검증한다.

EXP-009는 parity-load, EXP-010은 전체 numerical load(sum)이며,
둘은 `SERIAL_COMPOSITION_FAMILY_V1`이라는 하나의 작은 연구 family로 관리한다.

## 2. 가설 / 반대가설
### H1
`S_(R-1)`의 공정추첨 평균 대비 편차와 `S_R` 편차 사이 lag-1 covariance가 0이 아니다.

### H0
공정추첨에서 각 회차는 독립이고 draw-sum lag-1 covariance는 0이다.

PRIMARY: `two-sided`
- positive = high/low sum 상태의 persistence
- negative = reversal
결과 후 방향 선택 금지.

## 3. 데이터
- Draw Range: `1~1237`
- PRIMARY: MAIN 6
- SECONDARY: MAIN+BONUS 7
- canonical SHA-256:
  `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`
- target transitions: `R=2~1237` = `1,236`

## 4. 공정추첨 sum null
1~45 population:
- N = 45
- population mean `μ_pop = 23`
- population variance (denominator N):
  `σ_pop² = (45²-1)/12`

MAIN 6 sum:
`S_T = Σ MAIN(T)`

이론 평균:
`μ6 = 6*23 = 138`

이론 분산:
`V6 = 6*σ_pop²*((45-6)/(45-1))`

또한 exact MAIN6 sum PMF는
1~45에서 6개를 중복 없이 선택하는 모든 조합을 동등확률로 두는 DP/combinatorial distribution으로 계산한다.

## 5. PRIMARY lag product
각 R:
`X_R = S_(R-1)-μ6`
`Y_R = S_R-μ6`
`L_R = X_R*Y_R`

IID fair-draw null:
`E[L_R]=0`

## 6. 효과크기
`LAG1_COVARIANCE = mean(L_R)`

`NORMALIZED_LAG1_COVARIANCE = mean(L_R)/V6`

## 7. Analytical statistic
IID centered sums에서:
`Var(L_R)=V6²`

adjacent lag-products의 covariance는 0.

`T = ΣL_R / (sqrt(N)*V6)`

two-sided normal p.

## 8. Exact-PMF full-sequence Monte Carlo
각 simulation:
1. exact fair-draw MAIN6 sum PMF에서 `1~1237` sum sequence를 IID 생성
2. 동일 lag product와 T 계산

- simulation: `100,000`
- seed: LOCKED protocol hash 기반 deterministic
- two-sided MC p

## 9. SERIAL_COMPOSITION_FAMILY_V1 다중검정
Family:
1. EXP-009 PARITY-LOAD lag-1
2. EXP-010 DRAW-SUM lag-1

EXP-009 고정 결과:
- analytical p = `0.705960045`
- full-sequence MC p = `0.703852961`

EXP-010 종료 후:
- analytical p 두 개에 Holm FWER 0.05
- MC p 두 개에 Holm FWER 0.05

EXP-010이 내부 SUPPORTED가 되려면:
- local analytical p<=0.05
- local MC p<=0.05
- family Holm analytical p<=0.05
- family Holm MC p<=0.05
를 모두 충족해야 한다.

EXP-010 종료로 `SERIAL_COMPOSITION_FAMILY_V1`은 CLOSED.
결과를 보고 range/median/SD 등의 lag-1 scalar summary를 추가하지 않는다.

## 10. 기간 안정성
- Overall `2~1237`
- First Half `2~619`
- Second Half `620~1237`
- Recent100 `1138~1237`
- Recent50 `1188~1237`
- Recent20 `1218~1237` TEST_ONLY

SUPPORTED 후보:
1. Overall/First/Second 방향 동일
2. Recent100/50이 둘 다 Overall 반대가 아님
3. Recent20은 성공판정 제외

## 11. SECONDARY — INTEGRATED
`J_R = MAIN(R)+BONUS(R)`의 7개 합.

`μ7 = 7*23`
`V7 = 7*σ_pop²*((45-7)/(45-1))`

SECONDARY:
`(S_(R-1)-μ6)*(J_R-μ7)`의 평균과 analytical p.
MAIN 실패를 뒤집지 않는다.

## 12. Walkforward
최소 training `200 prior transitions`.

각 R:
1. training `2~R-1`
2. training local analytical p<=0.05일 때만 signal
3. direction = sign(training covariance)
4. R outcome 전에 source R-1, S_(R-1), boundary, direction, state hash 고정
5. `score = direction*(S_(R-1)-μ6)*(S_R-μ6)`

conditional variance:
`(S_(R-1)-μ6)^2*V6`

평가:
- analytical one-sided p
- exact sum-PMF 기반 `100,000` conditional MC
- exposed>=100

## 13. 최종 판정
### SUPPORTED
모두 충족:
1. local Overall analytical p<=0.05
2. local full-sequence MC p<=0.05
3. SERIAL_COMPOSITION_FAMILY Holm analytical<=0.05
4. SERIAL_COMPOSITION_FAMILY Holm MC<=0.05
5. Overall/First/Second 방향 동일
6. Recent100/50 모두 반대가 아님
7. WF exposed>=100
8. WF analytical p<=0.05
9. WF conditional MC p<=0.05
10. future leakage=0
11. hash mismatch=0

### INCONCLUSIVE
local/family retrospective 신호는 있으나 기간 또는 WF가 충분치 않은 경우.

### FAILED
local/family PRIMARY가 null과 구별되지 않거나 충분한 WF에서 미재현.

## 14. 사전등록 EARLY-STOP
- local analytical 또는 local MC가 0.05를 넘고 family Holm까지 고려해 SUPPORTED가 불가능하면 Walkforward 생략 가능.
- analytical 구현 검증을 위해 full-sequence MC는 수행.
- 기간 통계는 설명용 계산 가능.

## 15. PROGRAM_LEVEL_DISCOVERY_GUARD
- 단일 EXP SUPPORTED만으로 Promotion Candidate 금지.
- family 통과도 자동 Promotion 금지.
- 별도 독립 재현 / prospective confirmation 필요.
- 공식 ENGINE 자동 승격 금지.

## 16. 사후 금지
- sum threshold 생성
- high-sum/low-sum subset 선택
- 특정 기간 cherry-pick
- range/median/SD lag-1을 EXP-010 구제용 후속으로 연속 실행
- 번호 추천 직접 연결
- 다른 실패축과 결합

## 17. 공식 보호
- OFFICIAL ENGINE = FROZEN
- gate/threshold/signature/공식 코드/DB 변경 금지
- NUMBER/TRIO/PAIR/CORE 변경 금지
- hidden score/weight 금지
- 추천번호 생성 금지

## 18. Preflight
1. 데이터 1~1237 / 중복0 / 누락0
2. MAIN6 unique / 1~45 / BONUS valid
3. snapshot hash
4. μ_pop=23
5. exact population variance
6. μ6/V6 formula
7. exact MAIN6 sum PMF count total = C(45,6)
8. PMF mean/variance = μ6/V6
9. target 2~1237 / lag boundary
10. deterministic MC
11. period boundary
12. family Holm implementation
13. WF future block/state hash
14. official P45 변경 0

치명적 실패 시 분석 중단.

# P45 EXP-009 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-009`
- 연구명: `PARITY-LOAD LAG-1 AUTOCORRELATION — PERSISTENCE / REVERSAL`
- 상태: `LOCKED / READY_FOR_BACKTEST`
- LOCK 승인일: `2026-08-21`
- 실제 EXP-009 outcome 조회 전 LOCK: `YES`
- 백테스트 실행 전 LOCK: `YES`
- Walkforward 실행 전 LOCK: `YES`
- 추천번호 생성: `NO`
- 공식 ENGINE 변경: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

> `BATCH_WHEN_SAFE` 운영에 따라 DRAFT를 사용자 산출물로 만들지 않고,
> 연구 정의를 먼저 고정한 뒤 실제 결과 분석 전에 이 LOCKED 기준본을 생성했다.
> 결과 확인 후 조건 수정은 금지한다.

## 1. 연구 목적
각 MAIN 6개 회차의 **홀수 개수(odd-number count)** 가 직전 회차에서 다음 회차로
지속(persistence) 또는 반전(reversal)되는 lag-1 serial dependence를 가지는지 검증한다.

기존 EXP의 exact-number, movement, extinction, ending, historical analog, pairwise-gap 연구와 분리된
**composition-state transition** 연구다.

## 2. 가설 / 반대가설
### H1
직전 회차 홀수 개수 편차와 다음 회차 홀수 개수 편차 사이 lag-1 covariance가 0이 아니며,
그 방향이 기간 분할과 Walkforward에서 재현된다.

### H0
공정추첨에서 각 회차는 독립이며 lag-1 covariance는 0이다.

PRIMARY는 `two-sided`.
- positive = persistence
- negative = reversal
결과 후 방향 선택 금지.

## 3. 데이터 경계
- Draw Range: `1~1237`
- PRIMARY: MAIN 6
- SECONDARY: MAIN+BONUS 7
- canonical SHA-256:
  `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`
- target transitions: `R=2~1237` = `1,236`

## 4. 홀수 개수 null
1~45에는 홀수 23개, 짝수 22개.

`O_T = MAIN(T)의 홀수 개수`

공정추첨:
`O_T ~ Hypergeometric(N=45,K=23,n=6)`

`μ6 = 6*23/45`

`σ6² = 6*(23/45)*(22/45)*((45-6)/(45-1))`

## 5. PRIMARY lag product
각 R:
`X_R = O_(R-1)-μ6`
`Y_R = O_R-μ6`
`L_R = X_R*Y_R`

공정 IID null에서 `E[L_R]=0`.

## 6. 효과크기
`LAG1_COVARIANCE = mean(L_R)`

`NORMALIZED_LAG1_COVARIANCE = mean(L_R)/σ6²`

## 7. Analytical statistic
IID null에서 `Var(L_R)=σ6^4`.
centered iid 구조에서 adjacent lag-product covariance도 0.

`T = ΣL_R / (sqrt(N)*σ6²)`

two-sided normal p.

## 8. Full-sequence Monte Carlo
각 simulation에서 `1~1237` odd-count sequence를
IID `Hypergeometric(45,23,6)`로 생성하고 동일 T 계산.

- simulation: `100,000`
- deterministic seed: protocol hash 기반
- two-sided p

## 9. 다중검정
V1 PRIMARY는 `MAIN odd-count lag-1 covariance` 하나.

사후 PRIMARY 승격 금지:
- O=0~6 개별 상태
- O>=4 등 threshold
- odd-heavy/even-heavy subset
- parity pattern string
- 특정 번호대/끝수/전멸/gap/analog 결합

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
`I_R = INTEGRATED(R) 7개의 홀수 개수`

`μ7=7*23/45`

SECONDARY:
`(O_(R-1)-μ6)*(I_R-μ7)`의 평균과 analytical p.
MAIN 실패를 뒤집지 않는다.

## 12. Walkforward
최소 training `200 prior transitions`.

각 R:
1. training은 `2~R-1`
2. training PRIMARY two-sided p<=0.05일 때만 signal
3. direction = sign(training covariance)
4. R outcome 전에 source R-1, O_(R-1), training boundary, direction, state hash 고정
5. score:
   `S_R = direction*(O_(R-1)-μ6)*(O_R-μ6)`

conditional null:
`E[S_R|F_(R-1)]=0`

conditional variance:
`(O_(R-1)-μ6)^2*σ6²`

평가:
- analytical one-sided p
- `100,000` conditional MC
- exposed >=100 필요

## 13. 최종 판정
### SUPPORTED
모두 충족:
1. Overall analytical p<=0.05
2. full-sequence MC p<=0.05
3. Overall/First/Second 방향 동일
4. Recent100/50 둘 다 반대 아님
5. WF exposed>=100
6. WF analytical p<=0.05
7. WF conditional MC p<=0.05
8. future leakage=0
9. hash mismatch=0

### INCONCLUSIVE
retrospective signal은 있으나 기간/노출/최근구조가 충분치 않은 경우.

### FAILED
Overall PRIMARY 또는 full-sequence null 실패,
혹은 충분한 WF에서 재현 실패.

## 14. 사전등록 EARLY-STOP
- Overall analytical p>0.05이면 SUPPORTED 불가능.
- analytical 구현 검증을 위해 full-sequence MC까지는 수행.
- analytical와 MC가 모두 실패하면 Walkforward는 생략 가능.
- 기간 통계는 설명용으로 계산 가능.

## 15. PROGRAM_LEVEL_DISCOVERY_GUARD
EXP-009부터:
- 단일 Experiment `SUPPORTED`는 Experiment 내부 판정일 뿐.
- 단일 p<=0.05만으로 `PROMOTION_CANDIDATE` 금지.
- Promotion 검토에는 별도 독립 재현 또는 prospective confirmation 필요.
- 공식 ENGINE 자동 승격 금지.

## 16. 사후 금지
- O>=4 등 threshold 생성
- 특정 parity state 선택
- 기간 cherry-pick
- positive/negative 한 방향 사후 채택
- odd/even 번호 직접 추천
- 다른 실패축과 결합하여 EXP-009 구제
- 공식 NUMBER/TRIO/PAIR/CORE 연결

## 17. 공식 보호
- OFFICIAL ENGINE = FROZEN
- gate/threshold/signature 변경 금지
- 공식 코드/DB 변경 금지
- hidden score/임의 weighting 금지
- 추천번호 생성 금지
- 성공해도 자동 승격 금지

## 18. Preflight
1. 데이터 1~1237
2. 중복 0
3. 누락 0
4. MAIN 6 unique
5. 번호 1~45
6. BONUS valid
7. snapshot hash
8. odd population 23 / even 22
9. μ6 / σ6²
10. target 2~1237
11. lag off-by-one
12. analytical variance
13. MC deterministic seed
14. period boundary
15. WF future-block
16. prediction hash pre-outcome
17. 공식 P45 변경 0

치명적 실패 시 분석 중단.

# P45 EXP-016 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-016`
- 연구명: `NUMBER-IDENTITY MARGINAL EXCHANGEABILITY — GLOBAL HETEROGENEITY + HALF-SPLIT PERSISTENCE`
- Family: `NUMBER_IDENTITY_EXCHANGEABILITY_V1`
- 상태: `LOCKED / READY_FOR_BACKTEST`
- LOCK 승인일: `2026-08-21`
- 실제 EXP-016 outcome 계산 전 LOCK: `YES`
- 백테스트/holdout 실행 전 LOCK: `YES`
- 추천번호 생성: `NO`
- 공식 ENGINE 변경: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

> `BATCH_WHEN_SAFE`에 따라 실제 EXP-016 결과 계산 전에 이 LOCKED 기준본을 생성했다.
> EXP-013과의 중복 위험 때문에 후보 판정은 `ACCEPT_WITH_MODIFICATION`.
> 이번 V1은 global number-label heterogeneity와 고정 half-split persistence만 검정한다.
> 결과 후 hot/cold threshold, 특정 번호 선택, rolling frequency, decay를 추가하지 않는다.

## 1. NEGATIVE-PROGRAM STOP RULE 사전 판정

판정:
`ACCEPT_WITH_MODIFICATION`

### 독립성
EXP-013:
- 매 target 직전까지의 cumulative frequency **rank**
- 현재 MAIN이 그 rank에서 어디를 선택하는지
- prequential hot/cold hazard

EXP-016:
- 45개 **번호 label 자체의 장기 marginal selection propensity**
- 전반부의 45차원 deviation vector가 후반부에도 같은 번호 정체성으로 재현되는지
- target별 hot/cold rank를 만들지 않음

따라서 질문은 다르지만 관련성이 있으므로 범위를 하나의 global family로 제한한다.

### 자유도 제한
PRIMARY/CONFIRMATORY는 정확히 두 단계:
1. global 45-label heterogeneity
2. 사전고정 half-split identity persistence

금지:
- 특정 번호 선택
- top5/top10/bottom5/bottom10
- threshold
- rolling window
- decay
- 최근구간 tuning
- 번호별 개별 p-value

### 명확한 null
공정추첨에서 각 회차 MAIN은 1~45 중 uniform 6-subset.
따라서 모든 번호 label은 동일 marginal probability `6/45`.

### 표본
- Overall: 1~1237
- Training: 1~618
- Holdout: 619~1237

### 독립 확인
전반부에서 deviation vector를 고정한 뒤 후반부에서 동일 label 방향을 one-sided로 검정한다.

## 2. 연구 목적

질문 1:
> 45개 번호의 장기 MAIN 출현빈도가 공정추첨의 동일확률 구조보다 과도하게 이질적인가?

질문 2:
> 전반부에서 상대적으로 많이/적게 나온 **같은 번호들**이 후반부에서도 같은 방향을 유지하는가?

이 연구는 추천번호를 만들기 위한 hot-number ranking 연구가 아니다.
global calibration / stable number-identity bias 검정이다.

## 3. 데이터

- Draw Range: `1~1237`
- MAIN 6 only
- canonical SHA-256:
  `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`

Blocks:
- Overall: `1~1237`, N=`1237`
- Training: `1~618`, N=`618`
- Holdout: `619~1237`, N=`619`

BONUS는 사용하지 않는다.

## 4. Number counts

block B, 번호 n:

`C_B(n) = count{R in B : n ∈ MAIN(R)}`

fair expected count:

`mu_B = 6*N_B/45`

deviation:

`D_B(n) = C_B(n) - mu_B`

항상:

`Σ_n D_B(n)=0`

## 5. GLOBAL HETEROGENEITY statistic

한 fair draw의 번호 indicator vector에서:

`p = 6/45`

single-number variance:
`v = p(1-p)`

different-number covariance:
`c = -v/44`

sum-zero 44차원 subspace의 단일회차 covariance eigenvalue:

`lambda = v - c = v*45/44`

N-round block에서 global statistic:

`Q_B = Σ_n D_B(n)^2 / (N_B*lambda)`

large-sample fair null:
`Q_B ~ chi-square(df=44)`

PRIMARY analytical p:
upper-tail chi-square(44).

## 6. Exact-draw Monte Carlo calibration

global Q의 finite-sample robustness를 위해
실제 fair mechanism을 그대로 시뮬레이션한다.

각 simulation:
- N_B개의 independent uniform 6-subsets from 1..45
- 45개 aggregate counts
- 동일 Q 계산

B:
`20,000`

Blocks:
- Training N=618
- Overall N=1237

Seed:
LOCKED protocol hash 기반 deterministic.

Monte Carlo p:
`(1 + # {Q* >= Q_obs})/(B+1)`

20,000은 global calibration robustness용이며,
PRIMARY analytical chi-square를 대체하지 않는다.

## 7. GLOBAL success gate

Retrospective heterogeneity가 유효하려면:

Training:
- chi-square p<=0.05
- exact-draw MC p<=0.05

Overall:
- chi-square p<=0.05
- exact-draw MC p<=0.05

네 조건을 모두 충족해야 holdout confirmatory 단계가 promotion-relevant signal 후보가 된다.

통과하지 못하면 `FAILED_EARLY`.

## 8. HOLDOUT identity-persistence test

Training deviation vector:

`d_n = D_train(n)`

은 rounds 1~618 종료 시 고정한다.

각 holdout round R=619~1237:

`H_R = Σ_{n∈MAIN(R)} d_n`

Training vector는 이미 sum 0이므로 fair null에서:

`E[H_R | d] = 0`

positive:
전반부에서 많이 나온 번호들은 후반부에서도 상대적으로 많이 나오고,
적게 나온 번호들은 후반부에서도 상대적으로 적게 나오는 방향.

negative:
전반/후반 label pattern reversal.

CONFIRMATORY direction은 결과 전부터:
`positive persistence only`

로 고정한다.

## 9. HOLDOUT analytical variance

training d population variance:

`sigma_d² = (1/45) Σ d_n²`

uniform 6-subset에서 한 holdout round score의 분산:

`Var(H_R | d) = 6*((45-6)/(45-1))*sigma_d²`

619 independent holdout rounds:

`T_H = ΣH_R / sqrt(619*Var(H_R|d))`

one-sided upper-tail normal p.

## 10. HOLDOUT exact conditional Monte Carlo

training d는 고정한 채,
공정추첨의 uniform 6-subset에서 가능한 **한 회차 score 분포**를
combinatorial DP로 정확히 계산한다.

Training N=618에서는:
`mu_train = 82.4`

따라서:
`5*d_n`은 정수.

DP:
- 45개 fixed integer weights `w_n=5*d_n`
- 정확히 6개를 선택한 subset-sum count distribution
- total combinations = `C(45,6)`

검증:
- PMF sum=1
- mean=0
- variance가 section 9 공식과 일치

그 exact one-round PMF에서
619개의 iid holdout scores를 생성하여 total score를 평가.

B:
`100,000`

one-sided:
`P(total_score* >= observed total_score)`

Seed:
LOCKED protocol hash 기반 deterministic.

SUPPORTED에는:
- holdout analytical p<=0.05
- holdout exact-conditional MC p<=0.05

둘 다 필요.

## 11. Holdout와 deviation vector 관계

holdout count deviation을:

`D_hold(n)=C_hold(n)-6*619/45`

라 하면:

`Σ_R H_R = Σ_n D_train(n)*D_hold(n)`

이다.

따라서 holdout test는
전반부/후반부의 **같은 번호 label deviation vector 내적**을 검정한다.

cosine similarity는 descriptive only.

## 12. 효과크기 / descriptive

보고:
- RMS count deviation
- max/min count와 번호는 descriptive only
- training-holdout dot product
- cosine similarity

금지:
- max/min 번호를 별도 hypothesis로 승격
- 상위/하위 번호 집합 추천
- 번호별 p-value

## 13. 기간 subgroup

이번 EXP는 **최근100/50/20 subgroup을 만들지 않는다.**

이유:
stable label heterogeneity hypothesis의 confirmatory 구조는
사전고정 `1~618 → 619~1237` half split 하나로 충분하다.

사후 최근기간을 추가하면 researcher degrees of freedom만 증가한다.

## 14. SECONDARY

`NONE_BY_DESIGN`

다음은 계산하지 않는다:
- BONUS frequency heterogeneity
- rolling frequency
- recent-long difference
- parity/ending subgroup
- pair/co-occurrence 결합

## 15. Family

`NUMBER_IDENTITY_EXCHANGEABILITY_V1`

EXP-016 종료와 동시에 CLOSED.

결과 후 구제 금지:
- top/bottom number subsets
- 특정 번호
- 특정 번호대
- window 20/50/100
- decay
- z-threshold
- EXP-013 hot/cold rank와 결합
- official NUMBER gate 연결

## 16. 최종 판정

### SUPPORTED
모두:
1. Training global chi-square p<=0.05
2. Training exact-draw MC p<=0.05
3. Overall global chi-square p<=0.05
4. Overall exact-draw MC p<=0.05
5. Holdout identity-persistence analytical one-sided p<=0.05
6. Holdout exact-conditional MC p<=0.05
7. future leakage=0
8. hash mismatch=0

### INCONCLUSIVE
Training/Overall global heterogeneity는 있으나 holdout identity persistence 미재현 또는 불충분.

### FAILED
global heterogeneity 자체가 null과 구별되지 않거나,
충분한 holdout에서 stable label pattern 미재현.

## 17. 사전등록 EARLY-STOP

Training 또는 Overall의 global analytical/MC gate 중 하나라도 실패하면:
- final `FAILED_EARLY`
- holdout exact-conditional 100k MC는 생략 가능
- holdout descriptive/analytical은 계산 가능

## 18. PROGRAM_LEVEL_DISCOVERY_GUARD

- 단일 EXP SUPPORTED만으로 Promotion Candidate 금지.
- 별도 독립 재현 또는 prospective future confirmation 필요.
- 공식 ENGINE 자동 승격 금지.

## 19. NEGATIVE-PROGRAM STOP RULE 유지

다음 후보도:
1. 독립성
2. 낮은 자유도
3. 명확한 null
4. 충분한 표본
5. holdout/WF/prospective 가능

을 모두 통과해야 한다.

없으면:
`DRAW_DISCOVERY_PAUSE`

EXP-016 실패 시 특히
marginal number-label bias의 top/bottom subgroup을 새 EXP로 구제하지 않는다.

## 20. 공식 보호

- OFFICIAL ENGINE=FROZEN
- gate/threshold/signature/code/DB 변경 금지
- NUMBER/TRIO/PAIR/CORE 변경 금지
- hidden score/arbitrary weight 금지
- 추천번호 생성 금지

## 21. Preflight

1. 데이터 1~1237 / 중복0 / 누락0
2. MAIN6 unique / range
3. snapshot hash
4. block exactly 1~618 / 619~1237
5. counts total = 6*N
6. deviation sum = 0
7. covariance lambda derivation fixture
8. Q implementation fixture
9. exact 6-subset sampler uniformity fixture
10. deterministic global MC
11. holdout score identity fixture
12. scaled training weights 5*d integer
13. exact subset-sum DP total = C(45,6)
14. DP mean/variance = formula
15. deterministic holdout MC
16. future leakage 0
17. official P45 변경 0

치명적 실패 시 outcome 분석 중단.

# P45 EXP-015 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-015`
- 연구명: `BONUS RELATIVE-RANK EXCHANGEABILITY — WITHIN-ROUND DRAW-ORDER BIAS`
- Family: `WITHIN_DRAW_ROLE_EXCHANGEABILITY_V1`
- 상태: `LOCKED / READY_FOR_BACKTEST`
- LOCK 승인일: `2026-08-21`
- 실제 EXP-015 outcome 계산 전 LOCK: `YES`
- 백테스트 실행 전 LOCK: `YES`
- 추천번호 생성: `NO`
- 공식 ENGINE 변경: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

> `BATCH_WHEN_SAFE`에 따라 실제 EXP-015 결과 계산 전에 이 LOCKED 기준본을 생성했다.
> 결과를 본 뒤 rank category 선택, low/high threshold, 특정 번호대, 특정 기간을 추가하지 않는다.

## 1. NEGATIVE-PROGRAM STOP RULE 사전 판정

EXP-015 후보:
`ACCEPT`

### 1) 기존 축과 독립
EXP-014는:
`BONUS(R-1) → MAIN(R)`의 다음회차 exact transition.

EXP-015는:
`동일 회차의 7개 공 안에서 BONUS의 숫자상 상대순위`
를 검정한다.

즉:
- cross-round transition이 아님
- MAIN movement가 아님
- gap carryover가 아님
- ending / age / cumulative frequency / analog가 아님

검정 대상은 **draw order role exchangeability**다.

### 2) 낮은 researcher degrees of freedom
PRIMARY는 하나:
`BONUS relative numerical rank의 centered mean`

- rank threshold 없음
- 특정 rank 선택 없음
- weighting 없음
- subgroup 없음

### 3) 명확한 fair-draw null
한 회차의 7개 서로 다른 번호가 정해졌다고 조건부로 보더라도,
추첨순서가 교환가능(exchangeable)하다면
7번째 공인 BONUS가 그 7개 중 어느 numerical rank일 확률도 정확히 `1/7`.

따라서:
`J_R ~ DiscreteUniform{1,2,3,4,5,6,7}`

### 4) 충분한 표본
- rounds `1~1237`
- N=`1237`

### 5) 독립 holdout 검증 가능
- first 618 rounds에서 방향 고정
- remaining 619 rounds에서 exact one-sided holdout

따라서 EXP-015에서는:
`DRAW_DISCOVERY_PAUSE = NOT_TRIGGERED`

## 2. 연구 목적

각 회차 R의 MAIN 6개와 BONUS 1개를 합친 integrated 7에서
BONUS의 **숫자 크기 상대순위**를 계산한다.

질문:

> 7번째 추첨 역할인 BONUS가 숫자상 낮은 쪽 또는 높은 쪽에
> 공정추첨 기대보다 체계적으로 치우치는가?

이 검정은 번호 자체의 인기도나 과거빈도가 아니라
**동일 회차 draw-order role과 numerical value 사이의 관계**를 본다.

## 3. BONUS relative rank 정의

회차 R:

`J_R = 1 + #{ n ∈ MAIN(R) : n < BONUS(R) }`

따라서:
- BONUS가 integrated 7 중 가장 작으면 `J_R=1`
- 가장 크면 `J_R=7`

MAIN과 BONUS는 서로 다른 번호이므로 tie 없음.

## 4. 조건부 exact null

공정추첨의 순서 exchangeability 하에서,
unordered integrated 7-set을 고정해도
7번째 위치(BONUS)가 그 7개 원소 중 어느 것일 확률은 동일하다.

따라서 정확히:

`P(J_R=j | integrated 7-set) = 1/7`
for `j=1,...,7`.

회차 간 독립 fair draw 하에서는:
`J_R iid Uniform{1,...,7}`.

이 null은 전체 번호분포를 추정할 필요가 없다.

## 5. PRIMARY centered score

`Z_R = J_R - 4`

가능값:
`{-3,-2,-1,0,1,2,3}`

null:
`E[Z_R]=0`

`Var(Z_R)=4`

positive:
BONUS가 상대적으로 큰 numerical rank에 치우침.

negative:
BONUS가 상대적으로 작은 numerical rank에 치우침.

PRIMARY:
`two-sided`

결과 후 방향 선택 금지.

## 6. PRIMARY 효과크기

`MEAN_BONUS_RELATIVE_RANK = mean(J_R)`

fair expectation:
`4`

PRIMARY effect:
`MEAN_RANK_SHIFT = mean(J_R)-4`

별도 threshold effect를 만들지 않는다.

## 7. PRIMARY analytical statistic

N=1237에서:

`S = ΣZ_R`

`Var(S)=4N`

`T = S / sqrt(4N)`

two-sided normal p는 설명/검산용으로 계산한다.

PRIMARY finite-sample 판정은 section 8의 exact discrete-convolution p를 사용한다.

## 8. PRIMARY exact finite-sample distribution

한 회차 Z의 exact PMF:

각 `-3,-2,-1,0,1,2,3`에 확률 `1/7`.

N회 합:
`S_N = Σ Z_R`

의 PMF를 위 7-point PMF의 N-fold discrete convolution으로 계산한다.

PRIMARY exact two-sided p:

`P(|S_N| >= |S_observed|)`

대칭 null이므로 이 tail을 사용한다.

성공 후보:
`EXACT_TWO_SIDED_P <= 0.05`

구현 검증:
- PMF sum = 1
- expected sum = 0
- variance = `4N`
- symmetry check

## 9. 시간순 고정 Holdout

총 N=1237.

결과 전에 고정:

### Direction-training
- rounds `1~618`
- N=`618`

training direction:
- mean rank >4 → `HIGH_RANK_BONUS`
- mean rank <4 → `LOW_RANK_BONUS`
- exactly 4 → `ZERO_DIRECTION`

### Holdout
- rounds `619~1237`
- N=`619`

training direction만 사용.

- HIGH_RANK_BONUS → holdout `P(S_hold >= observed)`
- LOW_RANK_BONUS → holdout `P(S_hold <= observed)`
- ZERO_DIRECTION → `NO_DIRECTION`

holdout도 동일 uniform rank PMF의 exact discrete convolution으로 계산한다.

SUPPORTED에는:
`HOLDOUT_EXACT_ONE_SIDED_P <= 0.05`

필수.

## 10. 기간 안정성

- Overall `1~1237`
- First Half / Training `1~618`
- Second Half / Holdout `619~1237`
- Recent100 `1138~1237`
- Recent50 `1188~1237`
- Recent20 `1218~1237` TEST_ONLY

각 기간:
- N
- mean rank
- rank shift
- score sum
- exact two-sided p

SUPPORTED 후보:
1. Overall direction = First Half direction
2. Overall direction = Second Half direction
3. Recent100/50이 둘 다 Overall 반대면 INCONCLUSIVE 이하
4. Recent20은 성공 판정 제외

## 11. rank-category counts

J=1~7 빈도는 **descriptive only**로 보고한다.

금지:
- 가장 많이/적게 나온 rank를 PRIMARY로 선택
- category별 별도 p-value family 생성
- category residual로 EXP-015를 구제

PRIMARY는 centered mean rank 하나다.

## 12. SECONDARY

`NONE_BY_DESIGN`

추가하지 않는다:
- BONUS absolute value mean
- MAIN sum과 BONUS 관계
- rank 1/7 extremes
- low3/high3 threshold
- BONUS ending/parity
- draw-specific subgroup

## 13. Family

`WITHIN_DRAW_ROLE_EXCHANGEABILITY_V1`

EXP-015 종료와 동시에 CLOSED.

결과 후 구제 금지:
- rank<=3 / >=5 threshold
- extreme rank 1/7
- 특정 BONUS value
- 특정 integrated-set shape
- 특정 기간
- MAIN/BONUS role swap의 다른 statistic
- EXP-014 transition과 결합

새 역할/순서 가설은 독립 새 Experiment + 새 family로만 가능.

## 14. 사전등록 EARLY-STOP

- Overall exact p>0.05이면 SUPPORTED 불가능.
- 전체/기간/holdout descriptive exact 통계까지 계산한다.
- Overall 실패 후 subgroup/category rescue 금지.

## 15. 최종 판정

### SUPPORTED
모두:
1. Overall exact two-sided p<=0.05
2. Overall/First/Second direction 동일
3. Recent100/50 둘 다 Overall 반대가 아님
4. training direction nonzero
5. holdout exact one-sided p<=0.05
6. future leakage=0
7. hash mismatch=0

### INCONCLUSIVE
Overall signal은 있으나 기간/holdout 재현 부족.

### FAILED
Overall exact null과 구별되지 않거나
고정 방향 holdout에서 재현되지 않음.

## 16. PROGRAM_LEVEL_DISCOVERY_GUARD

- 단일 EXP SUPPORTED만으로 Promotion Candidate 금지.
- 별도 독립 재현 / prospective future confirmation 필요.
- 공식 ENGINE 자동 승격 금지.

## 17. NEGATIVE-PROGRAM STOP RULE 유지

다음 후보도:
1. 독립성
2. 낮은 자유도
3. 명확한 null
4. 충분한 표본
5. holdout/WF/prospective 가능

을 모두 통과해야 한다.

없으면:
`DRAW_DISCOVERY_PAUSE`

연속 실패 해석:
`NO_REPRODUCIBLE_SIGNAL_FOUND_IN_TESTED_FAMILIES`

## 18. 공식 보호

- OFFICIAL ENGINE=FROZEN
- gate/threshold/signature/code/DB 변경 금지
- NUMBER/TRIO/PAIR/CORE 변경 금지
- hidden score/arbitrary weight 금지
- 추천번호 생성 금지

## 19. Preflight

1. 데이터 1~1237 / 중복0 / 누락0
2. MAIN6 unique / range
3. BONUS range / same-round MAIN exclusion
4. snapshot hash
5. J_R formula fixture
6. J_R always 1~7
7. conditional uniform-rank reasoning check
8. Z mean 0 / variance 4 fixture
9. N-fold convolution PMF sum/mean/variance/symmetry
10. target exactly 1~1237
11. split exactly 1~618 / 619~1237
12. deterministic repeat
13. future leakage 0
14. official P45 변경 0

치명적 실패 시 outcome 분석 중단.

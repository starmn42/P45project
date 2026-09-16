# P45 EXP-014 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-014`
- 연구명: `BONUS-TO-NEXT-MAIN EXACT CARRYOVER — R-1 BONUS → R MAIN`
- Family: `BONUS_SOURCE_TRANSITION_V1`
- 상태: `LOCKED / READY_FOR_BACKTEST`
- LOCK 승인일: `2026-08-21`
- 실제 EXP-014 outcome 조회 전 LOCK: `YES`
- 백테스트 실행 전 LOCK: `YES`
- 추천번호 생성: `NO`
- 공식 ENGINE 변경: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

> `BATCH_WHEN_SAFE`에 따라 실제 EXP-014 결과 계산 전에 이 LOCKED 기준본을 생성했다.
> 결과를 본 뒤 다른 lag, BONUS subgroup, MAIN→BONUS, BONUS→BONUS로 확장하지 않는다.

## 1. NEGATIVE-PROGRAM STOP RULE 사전 판정

EXP-014 후보 판정:
`ACCEPT`

이유:

1. **독립성**
   - 기존 transition 연구들은 MAIN을 predictor source로 사용했다.
   - EXP-014는 `직전 BONUS 1개`를 독립 predictor source로 사용한다.
   - EXP-003/005의 MAIN→MAIN exact recurrence 재튜닝이 아니다.

2. **낮은 researcher degrees of freedom**
   - source = BONUS(R-1) 한 개
   - target = MAIN(R)
   - exact identity 하나
   - lag = 1 하나
   - threshold / weighting / subgroup 없음

3. **명확한 fair-draw null**
   - 공정추첨에서 다음 회차 MAIN은 직전 BONUS와 독립
   - 특정 번호 하나가 MAIN 6개에 포함될 확률은 정확히 `6/45`

4. **충분한 표본**
   - targets `R=2~1237` = `1,236`

5. **검증 가능**
   - 전체 exact binomial
   - 결과 전 고정된 시간순 half-split holdout
   - future leakage 0 검증 가능

따라서 이번 EXP-014에서는 `DRAW_DISCOVERY_PAUSE`를 발동하지 않는다.

## 2. 연구 목적

각 target R에서:

`B_(R-1) = BONUS(R-1)`

가 다음 회차:

`MAIN(R)`

6개 안에 정확히 포함되는 빈도가 공정추첨 기대와 다른지 검증한다.

핵심 질문:

> 직전 회차 BONUS 번호가 다음 회차 MAIN으로 특별히 승격/회귀하는 구조가 있는가?

## 3. 기존 연구와 분리

### EXP-003
- source: 직전 MAIN 6개
- cross-round number movement / distance

### EXP-005
- source: R-2 MAIN 6개
- exact lag-2 reappearance

### EXP-014
- source: 직전 BONUS 1개
- target: 다음 MAIN 6개
- exact lag-1 identity only

따라서 predictor source와 질문이 다르다.

## 4. 데이터

- Draw Range: `1~1237`
- PRIMARY outcome: MAIN 6
- predictor: prior-round BONUS 1
- canonical SHA-256:
  `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`

Target:
`R=2~1237`

N:
`1,236`

각 R predictor는 오직 `BONUS(R-1)`만 사용한다.

## 5. PRIMARY 관측값

각 R:

`Y_R = 1{ BONUS(R-1) ∈ MAIN(R) }`

가능값:
`0/1`

전체 hits:

`X = ΣY_R`

observed rate:

`X/N`

fair expected rate:

`p0 = 6/45 = 2/15`

PRIMARY effect:

`RD = X/N - 6/45`

## 6. EXACT NULL

공정추첨에서 target R 직전 history 전체가 주어졌을 때
BONUS(R-1)는 이미 고정된 번호다.

다음 MAIN(R)은 1~45 중 uniform 6-subset이므로:

`P(Y_R=1 | F_(R-1)) = 6/45`

이 값이 과거 history와 무관하게 상수이므로,
연속 target의 Y_R sequence는 fair-draw null에서
iid Bernoulli(`6/45`)다.

따라서:

`X ~ Binomial(N=1236, p=6/45)`

가 exact null이다.

## 7. PRIMARY exact test

PRIMARY:
`two-sided exact binomial test`

- H0: `p=6/45`
- H1: `p != 6/45`
- alpha `0.05`

성공 후보:
`EXACT_TWO_SIDED_P <= 0.05`

정규근사를 PRIMARY로 사용하지 않는다.

## 8. 100,000회 Monte Carlo robustness

exact binomial 구현을 독립적으로 검증하기 위해:

- `X*_b ~ Binomial(1236,6/45)`
- B=`100,000`
- LOCKED protocol hash 기반 deterministic seed

two-sided MC는 exact-binomial probability-ordering과 같은 방식으로:

`P_null(X*)`가 observed `P_null(X)` 이하인 simulation 비율

로 계산한다.

PRIMARY success에는:
- exact p<=0.05
- MC p<=0.05

둘 다 필요.

## 9. 시간순 고정 Half-Split Holdout

N=1236을 결과 전에 정확히 반으로 고정:

### Direction-training
- `R=2~619`
- N=`618`

training effect direction:
- observed rate > 6/45 → `POSITIVE_CARRYOVER`
- observed rate < 6/45 → `NEGATIVE_CARRYOVER`
- 정확히 같으면 `ZERO_DIRECTION`

### Direction-holdout
- `R=620~1237`
- N=`618`

training에서 고정한 방향만 사용한다.

- POSITIVE면 holdout exact binomial `greater`
- NEGATIVE면 holdout exact binomial `less`
- ZERO면 `NO_DIRECTION / INCONCLUSIVE`

SUPPORTED에는 holdout one-sided exact p<=0.05 필요.

전체 결과에서 방향을 고른 뒤 같은 데이터에 재사용하지 않는다.

## 10. 기간 안정성

- Overall `2~1237`
- First Half / Training `2~619`
- Second Half / Holdout `620~1237`
- Recent100 `1138~1237`
- Recent50 `1188~1237`
- Recent20 `1218~1237` TEST_ONLY

각 기간은:
- hits
- rate
- RD
- exact two-sided p

를 보고한다.

SUPPORTED 후보:
1. Overall direction = First Half direction
2. Overall direction = Second Half direction
3. Recent100/50이 둘 다 Overall 반대면 INCONCLUSIVE 이하
4. Recent20 성공판정 제외

## 11. SECONDARY

`NONE_BY_DESIGN`

이번 EXP는 BONUS→다음 MAIN exact carryover 하나만 검정한다.

다음은 계산하지 않는다:
- BONUS→BONUS
- MAIN→BONUS
- BONUS→INTEGRATED
- 특정 BONUS 번호별
- 특정 번호대별

PRIMARY 실패를 다른 BONUS 관계로 구제하지 않는다.

## 12. 다중검정 / Family

`BONUS_SOURCE_TRANSITION_V1` PRIMARY hypothesis는 하나:

`BONUS(R-1) exact identity → MAIN(R)`

따라서 configuration multiple testing은 없다.

EXP-014 종료와 동시에:
`BONUS_SOURCE_TRANSITION_V1 = CLOSED`

결과 후 추가 금지:
- lag 2/3/4 BONUS carryover
- 특정 BONUS 번호
- 홀/짝 BONUS
- high/low BONUS
- ending family of BONUS
- ±1 / ±2 이동
- BONUS→BONUS
- MAIN→BONUS
- 다른 실패축과 결합

## 13. 사전등록 EARLY-STOP

- Overall exact p>0.05 또는 MC p>0.05이면 SUPPORTED 불가능.
- exact + MC까지는 항상 계산한다.
- 기간 / training / holdout exact 통계는 설명과 재현성 점검을 위해 계산 가능.
- 실패 후 subgroup rescue 금지.

## 14. 최종 판정

### SUPPORTED
모두:
1. Overall exact two-sided p<=0.05
2. Overall MC p<=0.05
3. Overall / First / Second 방향 동일
4. Recent100/50 둘 다 Overall 반대가 아님
5. training direction nonzero
6. holdout directional exact one-sided p<=0.05
7. future leakage=0
8. hash mismatch=0

### INCONCLUSIVE
Overall 신호는 있으나 기간 또는 holdout 방향 재현 부족.

### FAILED
Overall exact/MC null과 구별되지 않거나
충분한 holdout에서 방향 미재현.

## 15. PROGRAM_LEVEL_DISCOVERY_GUARD

- 단일 EXP SUPPORTED만으로 Promotion Candidate 금지.
- 별도 독립 재현 또는 prospective future confirmation 필요.
- 공식 ENGINE 자동 승격 금지.

## 16. NEGATIVE-PROGRAM STOP RULE 유지

다음 EXP 후보도 다시:
1. 기존 closed/failed 축과 독립
2. low degrees of freedom
3. clear fair-draw null
4. 충분한 표본
5. WF/prequential/prospective 가능

을 모두 통과해야 한다.

없으면:
`DRAW_DISCOVERY_PAUSE`

## 17. 공식 보호

- OFFICIAL ENGINE = FROZEN
- gate/threshold/signature/code/DB 변경 금지
- NUMBER/TRIO/PAIR/CORE 변경 금지
- hidden score/arbitrary weight 금지
- 추천번호 생성 금지

## 18. Preflight

1. 데이터 1~1237
2. 회차 중복 0
3. 누락 0
4. MAIN 6 unique
5. MAIN range 1~45
6. BONUS range 1~45
7. BONUS not in same-round MAIN
8. snapshot hash
9. target exactly 2~1237
10. predictor exactly BONUS(R-1)
11. outcome exactly MAIN(R)
12. membership off-by-one fixture
13. conditional p=6/45 combinatorial fixture
14. iid Bernoulli sequential-null reasoning check
15. exact binomial implementation fixture
16. deterministic MC repeat
17. split 2~619 / 620~1237
18. future leakage 0
19. official P45 변경 0

치명적 실패 시 outcome 분석 중단.

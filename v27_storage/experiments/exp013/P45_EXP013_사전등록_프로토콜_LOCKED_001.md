# P45 EXP-013 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-013`
- 연구명: `CUMULATIVE FREQUENCY-RANK PREQUENTIAL PERSISTENCE — HOT/COLD NUMBER HAZARD`
- Family: `CUMULATIVE_FREQUENCY_HAZARD_V1`
- 상태: `LOCKED / READY_FOR_BACKTEST`
- LOCK 승인일: `2026-08-21`
- 실제 EXP-013 outcome 조회 전 LOCK: `YES`
- 백테스트 실행 전 LOCK: `YES`
- 추천번호 생성: `NO`
- 공식 ENGINE 변경: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

> `BATCH_WHEN_SAFE` 운영에 따라 실제 EXP-013 결과 계산 전에 이 LOCKED 기준본을 생성했다.
> 결과를 본 뒤 hot/cold threshold, window length, decay, number subgroup을 추가하지 않는다.

## 1. NEGATIVE-PROGRAM STOP RULE 사전 판정

EXP-013 후보는 다음 5개 조건을 충족하여 `ACCEPT`:

1. 기존 closed/failed 축과 실질적으로 독립:
   - co-occurrence network가 아닌 marginal cumulative frequency rank
   - return-age가 아닌 cumulative historical count
   - lag-1 scalar composition이 아닌 number-level cross-sectional predictor
2. low researcher degrees of freedom:
   - 단일 cumulative count
   - 단일 average-tied rank
   - threshold/window/decay 없음
3. fair-draw null 명확:
   - predictor는 R outcome 전에 고정
   - current MAIN은 uniform 6-subset
4. 충분한 표본:
   - 최소 200 prior rounds 이후 모든 target 사용
5. prequential/holdout 검증 가능

따라서 `DRAW_DISCOVERY_PAUSE`는 이번 EXP-013에서는 발동하지 않는다.

## 2. 연구 목적

각 번호 1~45에 대해 target R 직전까지 MAIN에 출현한
**누적 출현횟수(cumulative frequency)** 의 cross-sectional rank가
다음 회차 MAIN 출현과 관련되는지 검증한다.

핵심 질문:

> 과거에 상대적으로 많이 나온 번호가 계속 더 잘 나오는가(hot persistence),
> 아니면 상대적으로 덜 나온 번호가 따라잡는가(cold catch-up)?

## 3. 기존 연구와 분리

- EXP-001: pairwise co-occurrence network
- EXP-003: cross-round number movement
- EXP-004: contiguous extinction zone
- EXP-005: lag-2 exact reappearance
- EXP-006: ending family
- EXP-007: historical analog successor
- EXP-008: within-round gap-set
- EXP-009/010: parity/sum lag-1 scalar composition
- EXP-011: mirror transform
- EXP-012: time-since-last-occurrence rank

EXP-013은:
`전체 과거 cumulative marginal MAIN count rank → 다음 MAIN`

만 검정한다.

## 4. 데이터 경계

- Draw Range: `1~1237`
- PRIMARY: MAIN 6
- SECONDARY: MAIN+BONUS 7
- canonical SHA-256:
  `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`

최소 prior history:
`200 rounds`

Target:
`R = 201~1237`

예정 target:
`1,037`

각 R predictor는 오직 rounds `1~R-1` MAIN을 사용한다.

## 5. 누적 빈도 정의

각 target R, 번호 n:

`F_R(n) = count{t < R : n ∈ MAIN(t)}`

현재 R outcome은 F_R 계산에 절대 사용하지 않는다.

## 6. Cross-sectional frequency rank

45개 F_R(n)를 작은 순서로 rank한다.

tie:
`average rank`

rank:
`1~45`

centered score:

`Q_R(n) = RANK_R(n) - 23`

항상:

`Σ_n Q_R(n) = 0`

positive score:
historically hotter (higher cumulative frequency) numbers.

negative score:
historically colder numbers.

## 7. PRIMARY 회차 score

현재 MAIN 6개에 대해:

`H_R = Σ_{n∈MAIN(R)} Q_R(n)`

fair-draw conditional null:

`E[H_R | F_(R-1)] = 0`

positive:
hot persistence.

negative:
cold catch-up / mean reversion.

PRIMARY:
`two-sided`

결과 후 방향 선택 금지.

## 8. 정확한 조건부 분산

45개 centered Q score population variance:

`σ_R² = (1/45) Σ Q_R(n)^2`

uniform 6-subset score sum의 조건부 분산:

`Var_R = 6 * ((45-6)/(45-1)) * σ_R²`

brute-force fixture로 검증한다.

## 9. PRIMARY 효과크기

각 target의 selected rank mean을 계산한다.

전체:

`MEAN_SELECTED_FREQUENCY_RANK`

fair expectation:
`23`

효과:

`MEAN_RANK_SHIFT = MEAN_SELECTED_FREQUENCY_RANK - 23`

- positive = hot persistence
- negative = cold catch-up

임의 normalization/weight는 추가하지 않는다.

## 10. PRIMARY analytical statistic

predictable martingale score:

`T = ΣH_R / sqrt(ΣVar_R)`

two-sided normal p.

## 11. PRIMARY 100,000회 martingale multiplier bootstrap

self-normalized:

`T_SN = ΣH_R / sqrt(ΣH_R²)`

bootstrap:
- independent Rademacher `w_R ∈ {-1,+1}`
- `T*_b = Σ(w_R H_R)/sqrt(ΣH_R²)`

B:
`100,000`

Seed:
LOCKED protocol hash 기반 deterministic.

PRIMARY success:
- analytical p<=0.05
- bootstrap p<=0.05

둘 다 필요.

## 12. Prequential 성격

EXP-013 PRIMARY 자체가 target-by-target로
과거 `1~R-1`만 사용하여 R을 평가한다.

따라서 retrospective static fit이 아니라
`PREQUENTIAL_WALKFORWARD_BY_CONSTRUCTION`.

모든 target R=201~1237은 outcome 전에 predictor가 고정된다.

future leakage:
반드시 0.

## 13. 독립 방향 Holdout

PRIMARY 전체 신호가 통과하더라도 방향을 사후 이용하지 않기 위해,
target sequence를 결과 전에 시간순 2개로 고정한다.

N=1037일 때:
- Direction-training block: first `floor(N/2)=518` targets
- Direction-holdout block: remaining `519` targets

예정:
- training: `201~718`
- holdout: `719~1237`

training block에서:
`direction = sign(ΣH_train)`

이 direction만 이용하여 holdout score:

`S_R = direction * H_R`

를 평가한다.

Holdout analytical:
`T_H = ΣS_R / sqrt(ΣVar_R_holdout)`

one-sided p.

Holdout robustness:
holdout S_R에 `100,000회 Rademacher multiplier bootstrap` one-sided.

최종 SUPPORTED에는:
- holdout analytical p<=0.05
- holdout bootstrap p<=0.05
가 필요하다.

즉 전체데이터에서 방향을 정하고 같은 데이터로 확인하지 않는다.

## 14. 기간 안정성

- Overall `201~1237`
- First Half `201~718`
- Second Half / Holdout `719~1237`
- Recent100 `1138~1237`
- Recent50 `1188~1237`
- Recent20 `1218~1237` TEST_ONLY

SUPPORTED 후보:
1. Overall direction = First Half direction
2. Overall direction = Second Half direction
3. Recent100/50 모두 Overall 반대면 INCONCLUSIVE 이하
4. Recent20 성공판정 제외

## 15. SECONDARY — INTEGRATED

동일 Q_R로 INTEGRATED(R) 7개 score 합:

`H7_R`

conditional expectation:
0

variance:
`7*((45-7)/(45-1))*σ_R²`

SECONDARY만 사용.
MAIN 실패를 뒤집지 않는다.

## 16. 다중검정 / Family

`CUMULATIVE_FREQUENCY_HAZARD_V1` PRIMARY 하나:

`cumulative MAIN frequency average-tied rank`.

결과 후 추가 금지:
- last 20/50/100 window frequency
- exponential decay
- top5/top10 hot
- bottom5/bottom10 cold
- z-score threshold
- number-specific frequency test
- recent-frequency minus long-frequency
- ending/gap/age/analog 결합

EXP-013 종료와 동시에 family CLOSED.

## 17. 사전등록 EARLY-STOP

- Overall analytical 또는 bootstrap p>0.05이면 SUPPORTED 불가능.
- 둘 다 계산한 뒤 실패면 holdout directional bootstrap은 생략 가능.
- 기간/secondary는 설명용 계산 가능.

단, training/holdout descriptive statistics는 항상 계산한다.

## 18. 최종 판정

### SUPPORTED
모두:
1. Overall analytical p<=0.05
2. Overall multiplier-bootstrap p<=0.05
3. Overall/First/Second direction 동일
4. Recent100/50 둘 다 반대 아님
5. holdout analytical one-sided p<=0.05
6. holdout multiplier-bootstrap one-sided p<=0.05
7. future leakage=0
8. hash mismatch=0

### INCONCLUSIVE
Overall signal은 있으나 기간/holdout 재현 부족.

### FAILED
Overall null과 구별되지 않거나,
충분한 holdout에서 방향 미재현.

## 19. PROGRAM_LEVEL_DISCOVERY_GUARD

- 단일 EXP SUPPORTED만으로 Promotion Candidate 금지.
- 별도 독립 재현 또는 prospective future confirmation 필요.
- 공식 ENGINE 자동 승격 금지.

## 20. NEGATIVE-PROGRAM STOP RULE 유지

EXP-013 결과와 관계없이 다음 후보는 다시:
1. 독립성
2. 낮은 자유도
3. 명확한 null
4. 충분한 표본
5. WF/prospective 가능성

을 모두 통과해야 한다.

통과 후보가 없으면:
`DRAW_DISCOVERY_PAUSE`

연속 실패 해석:
`NO_REPRODUCIBLE_SIGNAL_FOUND_IN_TESTED_FAMILIES`

## 21. 공식 보호

- OFFICIAL ENGINE=FROZEN
- gate/threshold/signature/code/DB 변경 금지
- NUMBER/TRIO/PAIR/CORE 변경 금지
- hidden score/arbitrary weighting 금지
- 추천번호 생성 금지

## 22. Preflight

1. 데이터 1~1237 / 중복0 / 누락0
2. MAIN6 unique / 1~45 / BONUS valid
3. snapshot hash
4. target exactly 201~1237
5. cumulative count uses only 1~R-1
6. average-tied rank fixture
7. centered score sum 0
8. SRSWOR variance brute-force fixture
9. analytical T fixture
10. deterministic bootstrap
11. first/holdout boundary 201~718 / 719~1237
12. predictor hash pre-outcome
13. official P45 변경 0

치명적 실패 시 분석 중단.

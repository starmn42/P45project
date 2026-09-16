# P45 EXP-012 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-012`
- 연구명: `INDIVIDUAL RETURN-AGE RANK HAZARD — NEXT-ROUND OCCURRENCE`
- Family: `RETURN_AGE_HAZARD_V1`
- 상태: `LOCKED / READY_FOR_BACKTEST`
- LOCK 승인일: `2026-08-21`
- 실제 EXP-012 outcome 조회 전 LOCK: `YES`
- 백테스트 실행 전 LOCK: `YES`
- Walkforward 실행 전 LOCK: `YES`
- 추천번호 생성: `NO`
- 공식 ENGINE 변경: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

> `BATCH_WHEN_SAFE` 운영에 따라 DRAFT 사용자 산출물 없이 실제 EXP-012 결과 계산 전에 이 LOCKED 기준본을 먼저 생성했다.
> 결과를 본 뒤 age threshold, cap, 특정 번호군, 특정 기간을 추가하지 않는다.

## 1. 연구 목적

각 번호 1~45에 대해 현재 target 회차 R 직전까지의
**마지막 MAIN 출현 이후 경과회차(return age)** 가
다음 회차 MAIN 출현과 체계적으로 관련되는지 검증한다.

핵심 질문:

> 오래 안 나온 번호가 다음 회차에 상대적으로 더 잘 나오거나,
> 반대로 최근 나온 번호가 상대적으로 더 잘 나오는가?

이번 V1은 **age의 cross-sectional rank 하나만** 사용한다.
고정 threshold/lookback/cap을 두지 않는다.

## 2. EXP-004와의 분리

EXP-004:
- fixed lookback 5/10/20
- 그 기간에 한 번도 안 나온 숫자
- 숫자선상 contiguous extinction zone
- zone length threshold 2/3/4/5

EXP-012:
- 모든 개별 번호의 exact time-since-last-MAIN
- threshold 없음
- contiguous zone 없음
- lookback parameter 없음
- age의 45개 번호 내 순위만 사용

따라서 EXP-004의 사후 재튜닝이 아니다.

## 3. 가설 / 반대가설

### H1
직전 history에서 return age가 큰 번호와 작은 번호의
다음 회차 출현확률이 공정추첨 조건부 기대와 다르며,
그 방향이 기간과 Walkforward에서 재현된다.

### H0 / Opposite
공정추첨에서 다음 MAIN 6개는 history와 독립이므로
return-age rank는 다음 출현에 예측정보를 주지 않는다.

PRIMARY:
`two-sided`

- positive = 오래 미출현한 번호(age rank 높음)가 다음 회차에 더 출현
- negative = 최근 출현한 번호(age rank 낮음)가 더 출현

결과 후 방향 선택 금지.

## 4. 데이터

- Draw Range: `1~1237`
- PRIMARY: MAIN 6
- SECONDARY: MAIN+BONUS 7
- canonical SHA-256:
  `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`

### Target 시작
각 번호 1~45의 last-seen MAIN round가 모두 정의된 최초 target R부터 시작한다.

정확한 규칙:
`R0 = min R such that every n∈1..45 has appeared in MAIN within rounds 1..R-1`

R0는 결과 R을 사용하지 않고 과거 history만으로 결정한다.

Target:
`R0~1237`

R0를 결과 확인 후 임의 변경하지 않는다.

## 5. Return age 정의

각 target R, 번호 n:

`LAST_R(n) = max{t < R : n ∈ MAIN(t)}`

`AGE_R(n) = R - LAST_R(n)`

따라서:
- R-1에 나왔으면 age=1
- 오래 안 나왔을수록 age가 큼

R0 이후 모든 번호에 age가 정의된다.

## 6. Cross-sectional rank score

각 R에서 45개 AGE 값을 작은 순서로 rank한다.

tie:
`average rank`

rank 범위:
`1~45`

centered score:

`Q_R(n) = RANK_R(n) - 23`

average-rank tie 처리 후에도:

`Σ_n Q_R(n) = 0`

이 된다.

이 방식으로:
- raw age scale
- arbitrary cap
- arbitrary threshold
- extreme-age subgroup
을 사용하지 않는다.

## 7. PRIMARY 관측값

회차 R의 MAIN 6개에 대해:

`H_R = Σ_{n∈MAIN(R)} Q_R(n)`

공정추첨 conditional null에서,
Q_R는 R outcome 전에 고정된 45개 score vector이고
MAIN(R)은 45개 중 균등한 6-subset이므로:

`E[H_R | F_(R-1)] = 0`

positive H:
older-ranked numbers가 많이 선택됨.

negative H:
recent-ranked numbers가 많이 선택됨.

## 8. 정확한 조건부 분산

회차 R의 45개 centered score population variance:

`σ_R² = (1/45) Σ_n Q_R(n)^2`

simple random sample without replacement에서
6개 score 합의 분산:

`Var_R = 6 * ((45-6)/(45-1)) * σ_R²`

이 공식을 unit test / brute-force fixture로 검증한다.

## 9. PRIMARY 효과크기

`MEAN_SELECTED_AGE_RANK =`
각 target의 MAIN 6개 selected rank 평균을 전체 exposure로 평균.

공정추첨 기대 rank:
`23`

PRIMARY effect:
`MEAN_RANK_SHIFT = MEAN_SELECTED_AGE_RANK - 23`

보조 normalized effect:
`ΣH_R / Σ(6*22)` 같은 임의척도는 만들지 않는다.

PRIMARY 효과크기는 rank shift 하나만 사용한다.

## 10. PRIMARY analytical statistic

martingale residual:
`e_R = H_R`

predictable score vector이므로:

`E[e_R|F_(R-1)] = 0`

PRIMARY:

`T = ΣH_R / sqrt(ΣVar_R)`

two-sided normal p.

## 11. PRIMARY 100,000회 martingale multiplier bootstrap

full historical age path 자체가 outcome에 적응하므로,
observed predictable score path를 보존하는 martingale robustness를 사용한다.

self-normalized statistic:

`T_SN = ΣH_R / sqrt(ΣH_R^2)`

각 bootstrap:
- independent Rademacher `w_R ∈ {-1,+1}`
- `T*_b = Σ(w_R H_R)/sqrt(ΣH_R^2)`

B=`100,000`

two-sided p.

Seed:
LOCKED protocol hash 기반 deterministic.

PRIMARY success:
- analytical p<=0.05
- multiplier-bootstrap p<=0.05

둘 다 필요.

## 12. 다중검정 / Family

`RETURN_AGE_HAZARD_V1`의 PRIMARY는 하나:
`cross-sectional average-tied return-age rank`.

결과 후 추가 금지:
- age>=5 / >=10 / >=20 threshold
- top 5 oldest / top 10 oldest
- youngest subgroup
- raw age linear score
- log age
- capped age
- number-specific hazard
- ending/zone/gap/analog 결합

EXP-012 종료와 동시에 `RETURN_AGE_HAZARD_V1 = CLOSED`.

## 13. 기간 안정성

Target 시작 R0를 기준으로 전체 target을 시간순 반분한다.

- Overall: `R0~1237`
- First Half: target count 기준 앞 절반
- Second Half: 나머지 절반
- Recent100: 마지막 100 targets
- Recent50: 마지막 50 targets
- Recent20: 마지막 20 targets TEST_ONLY

SUPPORTED 후보:
1. Overall/First/Second 방향 동일
2. Recent100/50이 둘 다 Overall 반대가 아님
3. Recent20 성공판정 제외

## 14. SECONDARY — INTEGRATED

동일 Q_R를 사용하여
INTEGRATED(R) 7개 score 합:

`H7_R`

conditional expectation 0.

분산:
`7*((45-7)/(45-1))*σ_R²`

SECONDARY만 사용.
MAIN 실패를 뒤집지 않는다.

## 15. Walkforward

최소 training:
`200 target rounds`

각 target R:
1. training은 R 이전 target outcomes만
2. training analytical two-sided p<=0.05일 때만 signal
3. direction=sign(training mean H)
4. R outcome 전에:
   - last-seen vector hash
   - age vector hash
   - rank-score vector hash
   - predicted direction
   - training boundary
   - prediction/state hash
   고정
5. 이후 H_R 평가

score:
`S_R = direction * H_R`

conditional variance:
`Var_R`

## 16. Walkforward 평가

observed exposed rounds:
- minimum `100`

analytical:
`T_WF = ΣS_R / sqrt(ΣVar_R_exposed)`
one-sided p.

robustness:
`100,000회 Rademacher martingale multiplier bootstrap`
on exposed S_R.

성공:
- exposed>=100
- analytical p<=0.05
- bootstrap p<=0.05
- future leakage=0
- hash mismatch=0

## 17. 사전등록 EARLY-STOP

- Overall analytical 또는 bootstrap p>0.05이면 SUPPORTED 불가능.
- 둘 다 계산한 뒤 실패면 Walkforward는 생략 가능.
- 기간/secondary는 설명용 계산 가능.

## 18. 최종 판정

### SUPPORTED
모두:
1. Overall analytical p<=0.05
2. Overall multiplier-bootstrap p<=0.05
3. Overall/First/Second 방향 동일
4. Recent100/50 둘 다 반대 아님
5. WF exposed>=100
6. WF analytical p<=0.05
7. WF bootstrap p<=0.05
8. leakage=0
9. hash mismatch=0

### INCONCLUSIVE
retrospective 신호 있으나 기간 또는 WF exposure 불충분.

### FAILED
Overall PRIMARY가 null과 구별되지 않거나
충분한 WF에서 재현 실패.

## 19. PROGRAM_LEVEL_DISCOVERY_GUARD

- 단일 EXP SUPPORTED만으로 Promotion Candidate 금지.
- 별도 독립 재현 / prospective confirmation 필요.
- 공식 ENGINE 자동 승격 금지.

## 20. NEGATIVE-PROGRAM STOP RULE

EXP-012부터 운영규칙:

`NO_CREDIBLE_NEXT_HYPOTHESIS => DRAW_DISCOVERY_PAUSE`

다음 Experiment 후보는 최소:
1. 기존 closed/failed 축과 실질적으로 독립
2. low researcher degrees of freedom
3. 명확한 fair-draw null
4. 충분한 역사 표본
5. walkforward 또는 prospective 검증 가능

을 만족해야 한다.

만족하는 후보가 없으면
Experiment 번호를 억지로 늘리지 않고
`DRAW_DISCOVERY_PAUSE`로 전환한다.

연속 실패의 공식 해석은:
`NO_REPRODUCIBLE_SIGNAL_FOUND_IN_TESTED_FAMILIES`

이며 공식 gate 완화 근거가 아니다.

## 21. 공식 보호

- OFFICIAL ENGINE=FROZEN
- gate/threshold/signature/code/DB 변경 금지
- NUMBER/TRIO/PAIR/CORE 변경 금지
- hidden score/arbitrary weight 금지
- 추천번호 생성 금지

## 22. Preflight

1. 데이터 1~1237 / 중복0 / 누락0
2. MAIN6 unique / range / BONUS valid
3. snapshot hash
4. R0 deterministic history-only calculation
5. all ages defined from R0
6. age=R-last_seen off-by-one fixture
7. average-tied rank fixture
8. centered rank sum exactly 0
9. SRSWOR variance formula brute-force fixture
10. analytical T fixture
11. deterministic bootstrap
12. period boundary
13. WF future-block hashes
14. official P45 변경 0

치명적 실패 시 분석 중단.

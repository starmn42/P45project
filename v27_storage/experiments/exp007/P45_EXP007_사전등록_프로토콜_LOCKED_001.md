# P45 EXP-007 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-007`
- 연구명: `MAX-OVERLAP HISTORICAL ANALOG FOLLOWER — TWIN/SIMILAR ROUND TRANSITION`
- 상태: `LOCKED / READY_FOR_BACKTEST`
- 실제 결과 조회: `NO`
- 백테스트 실행: `NO`
- Walkforward 실행: `NO`
- 추천번호 생성: `NO`
- 공식 ENGINE 변경: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

> 이 문서는 2026-08-20 형님 승인으로 실제 결과 분석 전에 잠겼다.
> PRIMARY null은 결과 조회 전에 predictable-set martingale + 100,000회 multiplier bootstrap으로 보강했다.
> 이후 결과에 맞춘 수정은 금지한다. 변경이 필요하면 새 version 또는 새 Experiment로 처리한다.

---

## 1. 연구 목적

현재 직전 회차 `R-1`과 MAIN 번호 구성이 가장 유사한
**완전히 과거에 종료된 회차들**을 historical analog로 정의하고,

그 analog들의 실제 다음 회차(`H+1`)에 등장했던 번호 집합이
현재 회차 `R` MAIN에서 공정추첨 기대보다 더 또는 덜 출현하는지 검증한다.

핵심 질문:

> `과거에 비슷했던 회차들의 다음 회차가 현재 다음 회차에 재현 가능한 정보를 주는가?`

이번 V1은 이 질문 하나만 검증한다.

공식 추천번호, NUMBER/TRIO/PAIR/CORE/FALLBACK에는 연결하지 않는다.

---

## 2. 연구가설과 반대가설

### H1 — 연구가설
`R-1`과 최대 exact-overlap을 갖는 historical analog들의
실제 successor 번호 합집합이 `R` MAIN에 출현하는 비율은
공정추첨 조건부 기대와 체계적으로 다르며,
기간 분할 및 Walkforward에서도 재현된다.

### H0 / Opposite Hypothesis
historical analog successor 집합의 관찰 적중 차이는
과거 유사도 탐색, tie 수, candidate-set 크기 변동 및
공정추첨 변동으로 설명되며 미래에는 재현되지 않는다.

### 방향
PRIMARY:
양·음 양방향(two-sided).

- positive: analog successor 집합의 R 출현이 기대보다 많음
- negative: 기대보다 적음

결과 후 한 방향만 선택하지 않는다.

---

## 3. 데이터 경계

예정 데이터:
- Draw Range: `1~1237`
- PRIMARY: MAIN 6
- SECONDARY: MAIN + BONUS 7
- canonical SHA-256:
  `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`

### 평가 시작
Target:
`R = 4~1237`

이유:
회차 R에서 query는 R-1이고,
historical analog episode는 **successor까지 query 이전에 완전히 종료**되어야 한다.

따라서 analog base round H는:

`1 <= H <= R-3`

만 허용한다.

즉:
`H+1 <= R-2`

를 강제한다.

`H = R-2`는 금지한다.
그 successor가 R-1 자체가 되어 self-successor 성격이 생기는 것을 막는다.

예정 target rounds:
`1,234회`

---

## 4. Query round

각 target R에서:

`Q_R = MAIN(R-1)`

Q_R의 6개 MAIN만 사용한다.

R MAIN/BONUS는 candidate 생성에 절대 사용하지 않는다.

---

## 5. Historical analog similarity

각 허용 과거 base round H에 대해:

`S(H,R) = | MAIN(H) ∩ Q_R |`

즉 exact MAIN overlap count.

가능한 값:
`0~6`

다른 거리, 끝수, 가중치, 번호 위치는 사용하지 않는다.

---

## 6. 최대 유사회차 선택

각 R에서:

`M_R = max_{1 <= H <= R-3} S(H,R)`

historical analog set:

`A_R = { H : 1 <= H <= R-3 and S(H,R) = M_R }`

즉 **최대 exact overlap을 가진 모든 과거 회차를 사용**한다.

### Tie 정책
- tie 하나를 임의 선택하지 않는다.
- 최신/최초 analog 우선 규칙을 두지 않는다.
- 모든 max-overlap ties를 동일하게 포함한다.

따라서 사후 tie-breaking 자유도를 만들지 않는다.

---

## 7. Analog successor candidate set

각 analog H의 실제 다음 회차:

`MAIN(H+1)`

를 사용한다.

PRIMARY candidate set:

`C_R = union_{H in A_R} MAIN(H+1)`

즉 최대 유사회차들의 다음 회차 MAIN 번호 **합집합**이다.

### 중요
- Q_R 숫자를 별도로 빼지 않는다.
- Q_R 숫자를 별도로 더하지 않는다.
- successor 빈도 weighting을 하지 않는다.
- analog별 가중치도 없다.
- 합집합 여부만 사용한다.

---

## 8. 회차 단위 관측값

각 target R:

- `z_R = |C_R|`
- `k_R = |MAIN(R) ∩ C_R|`

candidate set이 45개 전체가 되어 분산이 0이면:

`NON_INFORMATIVE`

로 기록한다.

candidate set이 0이 되는 것은 정상 구조상 발생하지 않아야 한다.
발생하면 구현 오류 확인 후 중단한다.

---

## 9. 조건부 공정추첨 기대

회차 R의 history가 주어진 상태에서 C_R은 R 결과 전에 고정된다.

공정추첨 null:

`K_R ~ Hypergeometric(N=45, K=z_R, n=6)`

기대값:

`E_R = 6*z_R/45`

분산:

`Var_R = 6*(z_R/45)*(1-z_R/45)*((45-6)/(45-1))`

---

## 10. PRIMARY 효과크기

informative target rounds에서:

`TOTAL_EXPOSURE = Σ z_R`

`TOTAL_HITS = Σ k_R`

`OBSERVED_RATE = TOTAL_HITS / TOTAL_EXPOSURE`

공정추첨 marginal expected rate:

`EXPECTED_RATE = 6/45`

PRIMARY effect size:

`RISK_DIFFERENCE = OBSERVED_RATE - 6/45`

별도로 회차 평균 excess hit:

`MEAN_EXCESS_HIT = mean(k_R - E_R)`

도 보고한다.

---

## 11. PRIMARY 통계량

informative rounds에 대해:

`T = Σ(k_R - E_R) / sqrt(ΣVar_R)`

PRIMARY analytical:
two-sided.

이 T는 history에 적응적으로 생성된 candidate set을 대상으로 한
predictable-set / martingale-style 표준화 통계량으로 사용한다.

---

## 12. PRIMARY MARTINGALE NULL + MULTIPLIER BOOTSTRAP

회차 R의 candidate set `C_R`은 R 결과를 보기 전에
`R-1` 이하 history만으로 완전히 결정되는 **predictable set**이다.

따라서 fair-draw null에서:

`E[k_R - E_R | F_(R-1)] = 0`

이며, 회차별 residual:

`e_R = k_R - E_R`

은 martingale-difference 구조를 가진다.

PRIMARY analytical statistic:

`T = Σe_R / sqrt(ΣVar_R)`

을 사용한다.

### 100,000회 multiplier bootstrap robustness

실제 outcome에서 계산된 회차별 standardized martingale residual structure를 보존하고,
각 bootstrap b에서 independent Rademacher multiplier:

`w_R ∈ {-1,+1}`

를 확률 1/2로 부여한다.

bootstrap statistic:

`T*_b = Σ(w_R * e_R) / sqrt(ΣVar_R)`

을 계산한다.

two-sided bootstrap p:

`p_boot = (1 + count(|T*_b| >= |T_obs|)) / (1 + B)`

B:
`100,000회`

Seed:
LOCKED protocol hash로 deterministic 파생.

이 방식은 결과 전에 형성되는 실제 analog/tie/candidate 구조를 그대로 보존하면서,
그 위에서 발생한 martingale residual의 방향 변동을 검증한다.

PRIMARY success에는:
- analytical two-sided p <= 0.05
- multiplier-bootstrap p <= 0.05

를 모두 요구한다.

PRIMARY alpha:
`0.05`

---

## 13. 다중검정 정책

EXP-007 V1의 PRIMARY hypothesis는 하나다.

사전등록된 유사도:
`exact MAIN overlap maximum`

사전등록 candidate:
`all max-overlap analog successor MAIN union`

따라서 PRIMARY configuration family는 없다.

아래 하위분석은 PRIMARY 승격 금지:
- M_R = 1/2/3/4 별
- tie count별
- candidate size별
- 가장 최근 analog
- 가장 오래된 analog
- analog 하나만 선택
- successor frequency ranking
- overlap threshold >=2/3 등

결과 후 잘 나온 subgroup을 골라 재해석하지 않는다.

---

## 14. 최소 정보 기준

각 R마다 보고:
- max overlap `M_R`
- analog count `|A_R|`
- candidate size `z_R`

Overall에서 다음 분포를 별도 보고:
- M_R distribution
- analog-count distribution
- z_R distribution
- NON_INFORMATIVE count

### confirmatory target
`z_R < 45`

인 회차만 T/RD의 informative exposure에 포함한다.

전체 informative target rounds가 `200 미만`이면:
`INCONCLUSIVE — INSUFFICIENT_INFORMATION`

---

## 15. SECONDARY — INTEGRATED

동일 C_R에 대해:

`k7_R = |INTEGRATED(R) ∩ C_R|`

null:

`Hypergeometric(N=45, K=z_R, n=7)`

SECONDARY/SUPPORT로만 보고한다.

MAIN 실패를 뒤집지 않는다.

---

## 16. 기간 안정성

Overall:
- `4~1237`

First Half:
- `4~620`

Second Half:
- `621~1237`

Recent100:
- `1138~1237`

Recent50:
- `1188~1237`

Recent20:
- `1218~1237`
- `TEST_ONLY`

SUPPORTED 후보는:

1. Overall direction = First Half direction
2. Overall direction = Second Half direction
3. Recent100/Recent50이 모두 Overall 반대면 `INCONCLUSIVE` 이하
4. Recent20은 성공판정에 사용하지 않는다.

---

## 17. Walkforward 설계

Walkforward는 historical analog 정보가
실제 미래 target에서도 재현되는지 검증한다.

### 최소 training
`200 informative target rounds`

### 각 target R
1. 오직 과거 target outcomes `4~R-1`로 training effect를 계산한다.
2. R의 current C_R은 오직 R-1 및 H<=R-3 history로 생성한다.
3. training analytical two-sided p <= 0.05일 때만 historical signal 형성.
4. 없으면 `NO_WALKFORWARD_SIGNAL`.
5. 있으면 training RD 방향을 잠근다.
6. R outcome 전에 다음을 고정:
   - query round R-1
   - M_R
   - analog round IDs
   - successor round IDs
   - C_R
   - predicted direction
   - training boundary
   - prediction hash
7. 이후 R outcome을 평가한다.

---

## 18. Walkforward 성과

각 exposed R:

positive direction:
`S_R = k_R - E_R`

negative direction:
`S_R = E_R - k_R`

전체:

`S_TOTAL = ΣS_R`

### Walkforward null
노출이 일어난 실제 시점과
각 시점의 사전 고정 candidate size z_R를 보존한다.

one-sided Hypergeometric simulation으로
directional p를 계산한다.

최소 signal-exposed rounds:
`100`

성공:
- exposed >= 100
- directional p <= 0.05
- future leakage = 0
- prediction hash mismatch = 0

---

## 19. 최종 성공 / 실패 기준

### SUPPORTED
모두 충족:
1. informative target rounds >= 200
2. Overall MAIN analytical two-sided p <= 0.05
3. martingale multiplier-bootstrap p <= 0.05
4. Overall/First/Second 방향 동일
5. Recent100/50 모두 반대가 아님
6. Walkforward exposed >= 100
7. Walkforward directional p <= 0.05
8. future leakage = 0
9. hash mismatch = 0

### INCONCLUSIVE
- informative rounds 부족
- overall 신호는 있으나 기간 불안정
- overall 신호 있으나 WF exposure 부족
- 최근구간이 강하게 반대
- 구현/계산 한계로 full-sequence null을 충분히 검증하지 못함

### FAILED
- Overall PRIMARY가 null과 구별되지 않음
- 또는 martingale bootstrap null에서 구별되지 않음
- 또는 충분한 Walkforward에서 재현 실패

---

## 20. 설명용 A/B/C/D

A:
Overall + martingale bootstrap + 기간 + Walkforward 재현

B:
retrospective signal 있으나 미래 재현 실패/불안정

C:
관찰 차이는 있으나 null과 구별 어려움

D:
실질적인 analog follower 효과가 거의 없음

---

## 21. 이번 V1 명시적 제외

- Jaccard / cosine / 거리 기반 similarity
- 번호 위치별 similarity
- 끝수 similarity
- sum/odd-even similarity
- gap/spacing similarity
- analog overlap threshold
- 최근 analog 가중치
- analog 하나만 선택
- successor frequency score/ranking
- top-N successor numbers
- exact repeat 제거/강제
- 전멸/END_DIGIT/movement와 결합
- NUMBER/TRIO/PAIR/CORE 연결
- 추천번호 생성
- 1238 맞춤

---

## 22. 사후 금지

결과 후:
- M_R 특정값만 선택
- tie가 적은 회차만 선택
- z_R 작은/큰 회차만 선택
- 최근 analog만 선택
- successor frequency로 순위 생성
- similarity metric 변경
- overlap threshold 생성
- 기간 cherry-pick
- 추천번호 직접 연결

금지.

새 질문은 새 Experiment/version으로만 처리한다.

---

## 23. 미래 데이터 차단

target R에서 허용:
- query: R-1
- analog base: H <= R-3
- analog successor: H+1 <= R-2

금지:
- H = R-2
- R MAIN/BONUS를 candidate 생성에 사용
- R 이후 데이터
- 결과 후 analog 정의 수정

---

## 24. 공식 P45 보호

- OFFICIAL ENGINE = FROZEN
- 공식 gate/threshold/signature 변경 금지
- NUMBER/TRIO/PAIR/CORE 변경 금지
- 공식 DB 변경 금지
- hidden score/임의 weighting 금지
- 성공해도 자동 공식 승격 금지
- 추천 연결은 별도 downstream Experiment 필요

---

## 25. Preflight

1. 데이터 1~1237
2. 중복 0
3. 누락 0
4. MAIN 6 유일
5. 번호 1~45
6. BONUS 유효
7. snapshot hash 일치
8. target 4~1237
9. analog H<=R-3 강제
10. successor H+1<=R-2 강제
11. exact overlap fixture PASS
12. max-overlap all-ties fixture PASS
13. successor union fixture PASS
14. z_R/k_R fixture PASS
15. Hypergeometric expectation/variance PASS
16. analytical T unit test
17. predictable-set / martingale future-block PASS
18. deterministic seed PASS
19. period boundary PASS
20. Walkforward training R-1 차단
21. prediction hash pre-outcome
22. official P45 변경 0

치명적 실패 시 outcome 분석 중단.

---

## 26. 결과 보고

- DATA_HASH_VERIFIED
- PROTOCOL_HASH_VERIFIED
- VALID_TARGET_ROUNDS
- INFORMATIVE_TARGET_ROUNDS
- NON_INFORMATIVE_ROUNDS
- MAX_OVERLAP_DISTRIBUTION
- ANALOG_COUNT_DISTRIBUTION
- CANDIDATE_SIZE_DISTRIBUTION
- TOTAL_EXPOSURE
- TOTAL_HITS
- OBSERVED_RATE
- EXPECTED_RATE
- RISK_DIFFERENCE
- MEAN_EXCESS_HIT
- PRIMARY_T
- ANALYTICAL_P
- MARTINGALE_BOOTSTRAP_P
- First Half
- Second Half
- Recent100
- Recent50
- Recent20 TEST_ONLY
- INTEGRATED SECONDARY
- WALKFORWARD_SIGNAL_EXPOSED_ROUNDS
- WALKFORWARD_DIRECTIONAL_P
- FUTURE_LEAKAGE
- HASH_MISMATCH
- FINAL_EXPERIMENT_JUDGMENT
- A/B/C/D
- DRAW_PREDICTION_SIGNAL_SUPPORTED
- RECOMMENDATION_CONNECTION_ALLOWED_NOW = NO
- OFFICIAL_ENGINE_CHANGED = NO

---

## 27. 현재 다음 단계

1. 이 LOCKED protocol은 실제 결과 분석 전에 확정됐다.
2. 동일한 `1~1237` snapshot을 사용한다.
3. ChatGPT가 preflight + retrospective + martingale bootstrap + Walkforward를 수행한다.
4. 로컬 P45 독립 재현·DB/Registry/Decision/STATE 반영이 필요할 때만 Work를 사용한다.

## 28. LOCK 선언

- LOCK 승인일: `2026-08-20`
- Human Alias: `EXP-007`
- Protocol status: `LOCKED`
- Outcome viewed before lock: `NO`
- Backtest run before lock: `NO`
- Walkforward run before lock: `NO`
- Recommendation created before lock: `NO`
- Official engine changed: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

이 파일이 EXP-007 V1의 결과 전 연구 정의 기준본이다.

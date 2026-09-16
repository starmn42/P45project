# P45 EXP-006 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-006`
- 연구명: `SAME-ENDING FAMILY CARRYOVER — R-1 → R`
- 상태: `LOCKED / READY_FOR_BACKTEST`
- 실제 결과 조회: `NO`
- 백테스트 실행: `NO`
- Walkforward 실행: `NO`
- 추천번호 생성: `NO`
- 공식 ENGINE 변경: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

> 이 문서는 2026-08-20 형님 승인으로 실제 결과 분석 전에 잠겼다.
> Monte Carlo는 결과 조회 전에 full-sequence fair-draw 방식으로 보강했다.
> 이후 결과에 맞춘 수정은 금지한다. 변경이 필요하면 새 version 또는 새 Experiment로 처리한다.

---

## 1. 연구 목적

회차 `R-1`의 MAIN 6개가 가진 **끝수(end digit)** 와 같은 끝수를 가지되,
`R-1`에 실제로 나온 숫자 자체는 제외한 다른 숫자들이
회차 `R` MAIN에 출현하는 비율이 공정추첨 기대와 재현 가능하게 다른지 검증한다.

이 연구는 공식 P45의 END_DIGIT unit/gate와 독립된 Experiment다.

이번 V1은:
`same-ending family carryover, excluding exact repeats`
하나만 검증한다.

공식 NUMBER/TRIO/PAIR/CORE/FALLBACK에는 연결하지 않는다.

---

## 2. 연구가설과 반대가설

### H1 — 연구가설
직전 회차에 존재했던 끝수 family의 다른 숫자들이 다음 회차 MAIN에
공정추첨 조건부 기대보다 체계적으로 더 많이 또는 더 적게 출현하며,
그 방향이 기간 분할과 Walkforward에서도 재현된다.

### H0 / Opposite Hypothesis
same-ending family의 다음 회차 출현 차이는
회차별 candidate-set 크기 차이와 공정추첨 변동으로 설명되며,
미래 구간에서는 재현되지 않는다.

### 방향
PRIMARY는 양·음 양방향(two-sided)으로 한다.

- positive: same-ending 다른 숫자들이 기대보다 많이 출현
- negative: 기대보다 적게 출현

결과 후 방향 선택 금지.

---

## 3. 데이터 경계

예정 데이터:
- Draw Range: `1~1237`
- PRIMARY outcome: MAIN 6개
- SECONDARY: MAIN + BONUS 7개
- 잠금 snapshot 예상 canonical SHA-256:
  `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`

평가 회차:
`R = 2~1237`

예정 target rounds:
`1,236회`

회차 R의 신호 생성에는 `R-1`까지만 사용한다.

---

## 4. 끝수 정의

번호 n의 끝수:

`d(n) = n mod 10`

단:
- 10,20,30,40의 끝수 = 0
- 1~45만 사용

회차 `R-1` MAIN의 distinct ending set:

`D_R = { d(n) : n ∈ MAIN(R-1) }`

---

## 5. PRIMARY candidate set

회차 R에 대해:

`C_R = { n ∈ 1..45 : d(n) ∈ D_R and n ∉ MAIN(R-1) }`

즉:
1. 직전 회차에 등장한 끝수와 같은 끝수를 가져야 하고
2. 직전 회차의 실제 6개 숫자 자체는 제외한다.

이 제외는 exact repeat 효과를 EXP-003/005와 분리하기 위한 사전 고정 조건이다.

### 예시
R-1 MAIN이:
`3, 13, 20, 27, 34, 41`

이면 distinct endings:
`{3,0,7,4,1}`

candidate set은 이 끝수들에 속하는 1~45 숫자 중
위 6개 실제 출현 숫자를 제외한 전부다.

---

## 6. 회차 단위 관측값

각 target round R:

- `z_R = |C_R|`
- `k_R = |MAIN(R) ∩ C_R|`

공정추첨 조건부 null:

`K_R ~ Hypergeometric(N=45, K=z_R, n=6)`

기대값:

`E[K_R] = 6*z_R/45`

회차마다 z_R가 달라질 수 있으므로
고정 6/45 Bernoulli 독립검정을 사용하지 않는다.

---

## 7. PRIMARY 효과크기

전체 target rounds에서:

`TOTAL_EXPOSURE = Σ z_R`

`TOTAL_HITS = Σ k_R`

number-level observed rate:

`OBSERVED_RATE = TOTAL_HITS / TOTAL_EXPOSURE`

expected marginal rate:

`6/45`

PRIMARY effect size:

`RISK_DIFFERENCE = OBSERVED_RATE - 6/45`

Risk Difference는 효과크기다.

유의성은 회차 단위 Hypergeometric 구조로 평가한다.

---

## 8. PRIMARY 통계량

각 회차:

`E_R = 6*z_R/45`

`Var_R = 6*(z_R/45)*(1-z_R/45)*((45-6)/(45-1))`

전체:

`T = Σ(k_R - E_R) / sqrt(ΣVar_R)`

PRIMARY:
two-sided.

---

## 9. NULL MODEL

### Analytical
각 회차의 실제 candidate-set size `z_R`를 고정한
Hypergeometric null.

### Monte Carlo PRIMARY robustness
`R-1`이 `R`의 candidate set을 만들기 때문에,
회차별 실제 `C_R`만 고정한 독립 simulation으로 시계열 구조를 단순화하지 않는다.

각 simulation에서:
1. `1~1237` 전체 MAIN draw sequence를 IID fair-draw로 새로 생성한다.
2. 각 simulated `R-1` MAIN에서 distinct ending set을 다시 만든다.
3. exact `R-1` 숫자를 제외하여 simulated `C_R`을 다시 만든다.
4. simulated `R` MAIN과 비교하여 `k_R`, `z_R`, 전체 T를 계산한다.

즉 candidate-set 생성 과정까지 null 안에서 재현한다.

simulation:
`100,000회`

Seed:
LOCKED protocol hash에서 deterministic 파생.

사람이 선택하지 않는다.

---

## 10. 다중검정 정책

V1 PRIMARY hypothesis는 하나:

`same-ending family carryover excluding exact repeats`

따라서 PRIMARY overall 자체에는 configuration multiple testing이 없다.

다음은 V1 성공판정에 사용하지 않는다:
- 개별 끝수 0~9
- distinct ending 개수별
- R-1에서 끝수가 1회/2회 이상 등장한 경우
- 특정 번호대
- 특정 숫자
- candidate-set size별
- exact repeats 포함 버전

결과 후 잘 나온 하위그룹을 PRIMARY로 승격하지 않는다.

---

## 11. SECONDARY — INTEGRATED

R의 MAIN+BONUS 7개에 대해:

`k7_R = |INTEGRATED(R) ∩ C_R|`

null:

`Hypergeometric(N=45, K=z_R, n=7)`

expected:

`7*z_R/45`

SECONDARY/SUPPORT만 사용한다.
MAIN 실패를 뒤집지 않는다.

---

## 12. 기간 안정성

Overall:
- `2~1237`

First Half:
- `2~619`

Second Half:
- `620~1237`

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
3. Recent100/Recent50이 둘 다 Overall 반대면 `INCONCLUSIVE` 이하
4. Recent20은 성공판정 제외

---

## 13. Walkforward 설계

### training 최소
`200 target rounds`

### 각 R
1. training은 `2~R-1` outcome만 사용
2. 과거 T와 two-sided p 계산
3. `p <= 0.05`일 때만 historical signal 형성
4. 없으면 `NO_WALKFORWARD_SIGNAL`
5. 있으면 training effect direction 잠금
6. current signal set `C_R`은 오직 R-1 MAIN으로 생성
7. R outcome 전:
   - R-1 source round
   - distinct ending set
   - candidate set
   - predicted direction
   - training boundary
   - prediction hash
   저장
8. 이후 R outcome 평가

---

## 14. Walkforward 성과

각 exposed R:

positive training direction:
`S_R = k_R - E_R`

negative:
`S_R = E_R - k_R`

전체:
`S_TOTAL = ΣS_R`

각 exposed round의 실제 `z_R`를 고정한
Hypergeometric Monte Carlo null로 one-sided 검정한다.

최소 exposed rounds:
`100회`

성공:
- exposed >= 100
- directional p <= 0.05
- future leakage = 0
- prediction hash mismatch = 0

---

## 15. 최종 성공 / 실패

### SUPPORTED
모두 충족:
1. Overall MAIN analytical two-sided p <= 0.05
2. full-sequence Monte Carlo p <= 0.05
3. First/Second Half 방향 동일
4. Recent100/50 둘 다 반대 아님
5. Walkforward exposed >= 100
6. Walkforward directional p <= 0.05
7. future leakage 0
8. hash mismatch 0

### INCONCLUSIVE
- overall 유의하지만 기간 불안정
- overall 신호 있으나 WF exposure 부족
- 최근 구조가 강하게 반대
- 구현/데이터 제약으로 결론 부족

### FAILED
- Overall PRIMARY가 null과 구별되지 않음
- 또는 충분한 Walkforward에서 재현 실패
- 또는 관찰 차이가 random/null로 설명됨

---

## 16. 설명용 A/B/C/D

A:
Overall + 기간 + Walkforward 재현

B:
Overall 신호 있으나 미래 재현 실패/불안정

C:
관찰 차이는 있으나 null과 구별 어려움

D:
실질적 효과가 거의 없음

---

## 17. 이번 V1에서 제외

- exact repeat 포함
- strict skip-one
- 개별 ending 0~9 분석을 PRIMARY로 사용
- ending 빈도 multiplicity weighting
- `R-1` ending pair/trio 조합
- END_DIGIT official score/gate 사용
- 끝수 + 전멸 결합
- 끝수 + movement 결합
- 끝수 + 유사회차 결합
- 특정 숫자 추천
- NUMBER/TRIO/PAIR/CORE 연결
- 1238 맞춤

---

## 18. 사후 금지

결과 후:
- 특정 ending만 선택
- distinct-ending-count threshold 생성
- R-1 ending multiplicity에 가중치
- exact repeat를 다시 포함
- 특정 기간만 선택
- candidate-set size threshold 선택
- 공식 END_DIGIT gate와 결합
- 추천번호 생성

금지.

새 질문은 새 Experiment/version으로 처리한다.

---

## 19. 미래 데이터 차단

R의 candidate set은 오직:
`MAIN(R-1)`

으로 생성한다.

R MAIN/BONUS 및 미래 회차 사용 금지.

Walkforward prediction hash는 R outcome 조회 전에 생성한다.

---

## 20. 공식 P45 보호

- OFFICIAL ENGINE = FROZEN
- 공식 END_DIGIT gate 변경 금지
- official threshold/signature 변경 금지
- NUMBER/TRIO/PAIR/CORE 변경 금지
- 공식 DB 변경 금지
- HOLD→PASS 금지
- hidden score/weight 금지
- 성공해도 자동 공식 승격 금지

---

## 21. Preflight

1. 데이터 1~1237
2. 회차 중복 0
3. 누락 0
4. MAIN 유일성
5. 번호범위 1~45
6. BONUS 유효
7. data hash 일치
8. target 2~1237
9. ending 0 정의 검증
10. distinct ending set fixture PASS
11. exact R-1 numbers 제외 fixture PASS
12. z_R candidate size fixture PASS
13. Hypergeometric 기대/분산 unit test
14. theoretical p 구현 검증
15. Monte Carlo deterministic seed
16. 기간 경계 고정
17. WF training R-1 차단
18. prediction hash pre-outcome
19. deterministic repeat
20. 공식 P45 변경 0

치명적 실패 시 outcome 분석 중단.

---

## 22. 결과 보고

- DATA_HASH_VERIFIED
- PROTOCOL_HASH_VERIFIED
- VALID_TARGET_ROUNDS
- TOTAL_EXPOSURE
- TOTAL_HITS
- OBSERVED_RATE
- EXPECTED_RATE
- RISK_DIFFERENCE
- PRIMARY_T
- PRIMARY_P
- MONTE_CARLO_P
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

## 23. 현재 다음 단계

1. 이 LOCKED protocol은 실제 결과 분석 전에 확정됐다.
2. 동일한 `1~1237` snapshot을 사용한다.
3. ChatGPT가 직접 preflight + retrospective + Walkforward를 수행한다.
4. 로컬 P45 독립 재현·DB/Registry/Decision/STATE 반영이 필요할 때만 Work를 사용한다.

## 24. LOCK 선언

- LOCK 승인일: `2026-08-20`
- Human Alias: `EXP-006`
- Protocol status: `LOCKED`
- Outcome viewed before lock: `NO`
- Backtest run before lock: `NO`
- Walkforward run before lock: `NO`
- Recommendation created before lock: `NO`
- Official engine changed: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

이 파일이 EXP-006 V1의 결과 전 연구 정의 기준본이다.

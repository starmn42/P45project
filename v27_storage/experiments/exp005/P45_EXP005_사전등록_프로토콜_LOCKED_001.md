# P45 EXP-005 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-005`
- 연구명: `ALTERNATE-ROUND EXACT REAPPEARANCE — R-2 → R`
- 상태: `LOCKED / READY_FOR_BACKTEST`
- 실제 결과 조회: `NO`
- 백테스트 실행: `NO`
- Walkforward 실행: `NO`
- 추천번호 생성: `NO`
- 공식 ENGINE 변경: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

> 이 문서는 2026-08-20 형님 승인으로 실제 결과 분석 전에 잠겼다.
> 이후 결과에 맞춘 수정은 금지한다. 변경이 필요하면 새 version 또는 새 Experiment로 처리한다.

---

## 1. 연구 목적

회차 `R-2`의 MAIN 6개 숫자가 회차 `R`의 MAIN 6개에
정확히 다시 출현하는 정도가 공정추첨 기준과 재현 가능하게 다른지 검증한다.

이번 V1은 **정확한 격회 재출현(exact lag-2 reappearance)** 하나만 검증한다.

공식 추천번호, NUMBER/TRIO/PAIR/CORE/FALLBACK에는 연결하지 않는다.

---

## 2. 연구가설과 반대가설

### H1 — 연구가설
회차 `R-2`의 MAIN 6개와 `R`의 MAIN 6개 사이 정확한 겹침 수가
공정추첨에서 기대되는 수준과 체계적으로 다르며,
그 방향과 효과가 기간 분할 및 Walkforward에서도 재현된다.

### H0 / Opposite Hypothesis
`R-2 → R` 겹침 수의 관찰 차이는 공정추첨 변동으로 설명되며,
기간을 나누거나 미래 Walkforward로 진행하면 재현되지 않는다.

### 방향
PRIMARY는 양·음 양방향(two-sided)으로 검정한다.

- 양의 효과: `R-2` 숫자의 `R` 재출현이 기대보다 많음
- 음의 효과: `R-2` 숫자의 `R` 재출현이 기대보다 적음

결과를 본 뒤 한 방향만 선택하지 않는다.

---

## 3. 데이터 경계

예정 데이터:
- Draw Range: `1~1237`
- PRIMARY outcome: MAIN 6개
- SECONDARY: MAIN + BONUS 7개
- 기존 잠금 snapshot 예상 SHA-256:
  `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`

평가 회차:
`R = 3~1237`

예정 평가 수:
`1,235회`

회차 R 평가 시:
- R 결과는 outcome으로만 사용
- 신호 정의는 `R-2`까지의 고정 정보만 사용
- R 이후 데이터 사용 금지

---

## 4. PRIMARY 관측값

각 회차 R에 대해:

`X_R = | MAIN(R-2) ∩ MAIN(R) |`

가능한 값:
`0~6`

공정추첨 하에서 `MAIN(R-2)`가 고정된 6개 숫자 집합일 때:

`X_R ~ Hypergeometric(N=45, K=6, n=6)`

기대 겹침 수:

`E[X_R] = 6 × 6 / 45 = 0.8`

---

## 5. PRIMARY 효과크기

전체 평가 회차 수를 `N`이라 할 때:

`OBSERVED_MEAN_OVERLAP = ΣX_R / N`

`EXPECTED_MEAN_OVERLAP = 0.8`

PRIMARY effect size:

`MEAN_OVERLAP_DIFFERENCE = OBSERVED_MEAN_OVERLAP - 0.8`

보조 효과크기:

`REAPPEARANCE_NUMBER_RATE = ΣX_R / (6N)`

공정추첨 기대:
`6/45 = 13.3333%`

Risk Difference:

`RD = REAPPEARANCE_NUMBER_RATE - 6/45`

단, p-value 계산에 번호 단위 독립 Bernoulli 가정을 사용하지 않는다.

---

## 6. PRIMARY 추론 통계

각 회차의 exact overlap `X_R`를 회차 단위 관측값으로 사용한다.

Hypergeometric 분산:

`Var(X_R) = n*(K/N)*(1-K/N)*((N-n)/(N-1))`

여기서는:

`N=45, K=6, n=6`

으로 모든 회차에 동일하다.

표준화 통계량:

`T = Σ(X_R - 0.8) / sqrt(N * Var(X_R))`

PRIMARY 검정:
two-sided.

---

## 7. PRIMARY NULL

### Exact / theoretical null
공정추첨의 exact hypergeometric 분포를 기준으로 한다.

### Monte Carlo robustness null
각 평가 회차에서:
- `R-2 MAIN` 6개는 고정
- R의 simulated MAIN 6개를 1~45에서 복원 없이 공정 추출

simulation:
`100,000회`

각 simulation에서 전체 T를 계산한다.

Seed:
LOCK된 protocol hash에서 deterministic하게 파생한다.

사람이 seed를 선택하지 않는다.

---

## 8. 다중검정 정책

EXP-005 V1의 PRIMARY hypothesis는 **하나**다.

즉:
`R-2 MAIN 6개 → R MAIN 6개 exact overlap`

따라서 PRIMARY overall 검정 자체에는
configuration family 다중검정이 없다.

다만 다음은 모두 SECONDARY / descriptive로 분리한다.

- overlap = 0
- overlap >= 1
- overlap >= 2
- overlap >= 3
- 개별 숫자별 lag-2 재출현
- 특정 번호대
- 특정 끝수
- 특정 gap

이 항목을 결과를 보고 PRIMARY로 승격하지 않는다.

추가 가설이 필요하면 새 Experiment로 처리한다.

---

## 9. SECONDARY — INTEGRATED

보너스 포함 7개 구조는 SECONDARY로만 본다.

정의:

`Y_R = | MAIN(R-2) ∩ INTEGRATED(R) |`

여기서:
- `MAIN(R-2)` = 6개
- `INTEGRATED(R)` = MAIN 6 + BONUS 1 = 7개

공정추첨 기대 겹침 수:

`E[Y_R] = 6 × 7 / 45 = 42/45 = 0.933333...`

SECONDARY 결과로 PRIMARY 실패를 뒤집지 않는다.

---

## 10. 기간 안정성

전체:
- `3~1237`

전반부:
- `3~620`

후반부:
- `621~1237`

Recent100:
- `1138~1237`

Recent50:
- `1188~1237`

Recent20:
- `1218~1237`
- `TEST_ONLY`

### 안정성 기준
SUPPORTED를 위해:
1. Overall effect direction과 전반부 direction이 같아야 한다.
2. Overall effect direction과 후반부 direction이 같아야 한다.
3. Recent100/Recent50이 둘 다 Overall과 반대 방향이면 `INCONCLUSIVE` 이하로 제한한다.
4. Recent20은 성공 판정에 사용하지 않는다.

---

## 11. Walkforward 설계

이번 V1에서 Walkforward는
과거 lag-2 효과가 실제 미래에 유지되는지 검증한다.

### training 최소 표본
`200회`

### 각 회차 R
1. `3~R-1`의 과거 transition outcome만 사용한다.
2. training T와 two-sided p를 계산한다.
3. `p <= 0.05`일 때만 historical signal이 형성됐다고 본다.
4. signal이 없으면:
   `NO_WALKFORWARD_SIGNAL`
5. signal이 있으면 training effect direction을 결과 전에 잠근다.
6. R의 `MAIN(R-2)` 6개를 lag-2 signal set으로 잠근다.
7. R 결과 전:
   - predicted direction
   - source round R-2
   - six-number signal set
   - training boundary
   - prediction hash
   를 저장한다.
8. 그 후 R outcome `X_R`을 평가한다.

---

## 12. Walkforward 성과

각 exposed round R에서:

training direction이 positive면:
`S_R = X_R - 0.8`

negative면:
`S_R = 0.8 - X_R`

전체:

`S_TOTAL = ΣS_R`

공정추첨 exact/simulation null로 one-sided 평가한다.

최소 exposed rounds:
`100회`

### Walkforward 성공
- signal-exposed rounds >= 100
- directional null p <= 0.05
- future leakage = 0
- prediction hash mismatch = 0

---

## 13. 최종 성공 / 실패 기준

### SUPPORTED
모두 충족:

1. Overall MAIN two-sided PRIMARY p <= 0.05
2. Monte Carlo robustness p <= 0.05
3. Overall direction = First Half direction
4. Overall direction = Second Half direction
5. Recent100/Recent50이 둘 다 반대 방향이 아님
6. Walkforward exposed rounds >= 100
7. Walkforward directional p <= 0.05
8. future leakage = 0
9. hash mismatch = 0

### INCONCLUSIVE
예:
- Overall 유의하지만 기간 안정성 부족
- Overall 신호는 있으나 Walkforward exposure 부족
- Walkforward 재현 실패지만 표본이 충분하지 않음
- 데이터/구현 제약으로 강한 결론 불가

### FAILED
- Overall PRIMARY가 공정추첨과 구별되지 않음
- 또는 충분한 Walkforward exposure에서 재현 실패
- 또는 관찰차이가 null에서 설명됨

---

## 14. 설명용 A/B/C/D

A:
Overall + 기간 + Walkforward 모두 재현

B:
Overall에서는 신호 있으나 Walkforward 미재현

C:
관찰 차이는 있으나 통계적으로 공정추첨과 구별 어려움

D:
실질적인 lag-2 효과 자체가 거의 없음

공식 Experiment 상태가 우선한다.

---

## 15. 이번 V1에서 명시적으로 제외

아래는 이번 EXP-005 V1에서 하지 않는다.

- `R-2에 출현했고 R-1에는 없었던 숫자`만 따로 보는 strict skip-one
- `R-2 ±1 / ±2 ...` 주변 이동
- R-3 이상의 lag
- 끝자리 조건
- 전멸 조건
- 가변 전멸과 결합
- 유사회차/쌍둥이 회차
- spacing/등차
- 번호별 가중치
- 특정 숫자 그룹
- NUMBER/TRIO/PAIR/CORE 연결
- 1238 추천번호 생성

---

## 16. 사후 금지

결과를 본 뒤:

- strict skip-one 정의로 슬쩍 변경
- overlap >= 2 등 가장 좋아 보이는 threshold만 선택
- 특정 번호만 선택
- 특정 기간만 선택
- 특정 lag만 선택
- 특정 ending/gap 조건 추가
- weight/score 추가
- 추천번호로 바로 연결

금지.

새 질문은 새 Experiment/version으로 처리한다.

---

## 17. 미래 데이터 차단

회차 R Walkforward에서:
- training은 `R-1`까지
- signal set은 `MAIN(R-2)`
- R 결과 조회 전에 prediction hash 생성

R MAIN/BONUS를 신호 생성에 사용하지 않는다.

---

## 18. 공식 P45 보호

- ENGINE = FROZEN
- 공식 gate 변경 금지
- threshold 변경 금지
- NUMBER/TRIO/PAIR/CORE 변경 금지
- 공식 DB 변경 금지
- HOLD→PASS 금지
- protected hash 변경 금지
- EXP-005 성공 시에도 자동 승격 금지

---

## 19. Preflight

실제 결과 분석 전 확인:

1. 데이터 1~1237
2. 회차 중복 0
3. 회차 누락 0
4. MAIN 6개 유일
5. 번호 1~45
6. BONUS 유효
7. snapshot hash 일치
8. 평가범위 3~1237
9. `R-2` 참조 off-by-one 오류 없음
10. exact overlap fixture PASS
11. Hypergeometric 기대값 0.8 검증
12. 분산 공식 unit test
13. theoretical p 구현 검증
14. Monte Carlo deterministic seed
15. 기간 경계 고정
16. Walkforward training boundary 검증
17. R 결과 전 prediction hash
18. 동일입력 deterministic repeat
19. 공식 P45 변경 0

치명적 실패가 있으면 outcome 분석 중단.

---

## 20. 결과 보고

최소 보고:

- DATA_HASH_VERIFIED
- PROTOCOL_HASH_VERIFIED
- VALID_TRANSITIONS
- TOTAL_OVERLAP
- OBSERVED_MEAN_OVERLAP
- EXPECTED_MEAN_OVERLAP
- RD
- PRIMARY_T
- PRIMARY_P
- MONTE_CARLO_P
- First Half
- Second Half
- Recent100
- Recent50
- Recent20 TEST_ONLY
- INTEGRATED SECONDARY
- WALKFORWARD_ROUNDS
- SIGNAL_EXPOSED_ROUNDS
- WALKFORWARD_DIRECTIONAL_P
- FUTURE_LEAKAGE
- HASH_MISMATCH
- FINAL_EXPERIMENT_JUDGMENT
- A/B/C/D
- DRAW_PREDICTION_SIGNAL_SUPPORTED
- RECOMMENDATION_CONNECTION_ALLOWED_NOW = NO

---

## 21. 현재 다음 단계

1. 이 LOCKED protocol은 실제 결과 분석 전에 확정됐다.
2. 동일한 `1~1237` snapshot 데이터를 사용한다.
3. ChatGPT가 직접 preflight + retrospective + Walkforward를 수행한다.
4. 로컬 P45 독립 재현·DB/Registry/Decision/STATE 반영이 필요할 때만 Work를 사용한다.

## 22. LOCK 선언

- LOCK 승인일: `2026-08-20`
- Human Alias: `EXP-005`
- Protocol status: `LOCKED`
- Outcome viewed before lock: `NO`
- Backtest run before lock: `NO`
- Walkforward run before lock: `NO`
- Recommendation created before lock: `NO`
- Official engine changed: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

이 파일이 EXP-005 V1의 결과 전 연구 정의 기준본이다.

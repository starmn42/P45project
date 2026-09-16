# P45 EXP-004 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-004`
- 연구명: `VARIABLE EXTINCTION ZONE — NEXT-ROUND RECOVERY`
- 상태: `LOCKED / READY_FOR_DATA_VALIDATION`
- 실제 데이터 결과 조회: `NO`
- 백테스트 실행: `NO`
- Walkforward 실행: `NO`
- 추천번호 생성: `NO`
- 공식 ENGINE 변경: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED` (로컬 Registry 반영 시 확정)

> 이 문서는 2026-08-20 형님 승인으로 결과 확인 전에 잠겼다.
> 이후 결과에 맞춘 수정은 금지한다. 변경이 필요하면 EXP-004의 새 version 또는 새 Experiment로 처리한다.

---

## 1. 연구 목적

최근 일정 기간 MAIN 당첨번호에 한 번도 출현하지 않은 **연속 숫자 구간**이 생겼을 때,
그 구간 내부 숫자가 바로 다음 회차 MAIN에 출현하는 비율이
공정추첨 기준과 재현 가능하게 다른지 검증한다.

이 연구는 공식 P45의 고정 3·5·9·10 UNIT 전멸 연구와 별개의 독립 Experiment다.

이번 V1의 목표는 **예측 신호 존재 여부 검증**이다.
추천번호, NUMBER/TRIO/PAIR/CORE, FALLBACK에는 연결하지 않는다.

---

## 2. 가설과 반대가설

### H1 — 연구가설
사전에 고정한 가변 전멸구간 configuration 중 적어도 하나에서,
다음 1회차 MAIN 출현이 공정추첨 조건부 기대와 차이를 보이며,
그 차이가 다중검정·기간 안정성·Walkforward에서도 재현된다.

### H0 / Opposite Hypothesis
관찰되는 차이는 공정추첨 변동,
회차별 zone 크기 차이,
configuration 간 중첩,
다중탐색 및 표본 변동으로 설명된다.

### 방향
PRIMARY 검정은 **양·음 양방향(two-sided)** 으로 한다.

- 양의 효과: 전멸구간 내부 숫자의 다음 회차 출현이 기대보다 높음
- 음의 효과: 전멸구간 내부 숫자의 다음 회차 출현이 기대보다 낮음

결과를 본 뒤 한 방향만 선택하지 않는다.

---

## 3. 데이터 경계

### 예정 데이터
- Draw Range: `1~1237`
- PRIMARY outcome: MAIN 6개
- SECONDARY outcome: MAIN + BONUS 7개
- 기존 P45 snapshot 예상 SHA-256:
  `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`

실제 분석 전에 업로드된 데이터의:
- 회차 수
- 중복
- 누락
- MAIN 6개 유일성
- BONUS 유효성
- 정렬
- SHA-256

을 검증한다.

예상 snapshot hash와 다르면 **분석 중단** 후 원인을 확인한다.

### 공통 평가 회차
모든 12 configuration이 같은 평가 범위를 사용하도록:

`R = 21~1237`

를 공통 retrospective target range로 고정한다.

이유:
최대 lookback 20회가 필요하므로 모든 configuration을 동일한 target rounds에서 비교한다.

총 예정 target rounds:
`1,217회`

---

## 4. 가변 전멸구간 정의

회차 R을 평가할 때 결과 R은 절대 사용하지 않는다.

lookback L에 대해:

`R-L ~ R-1`

MAIN 번호에 한 번도 출현하지 않은 숫자의 집합을 `A(R,L)`로 정의한다.

`A(R,L)`를 숫자 순서 1~45에서
서로 이어진 **maximal contiguous run**으로 분할한다.

예:
미출현 숫자 = {3,4,5, 11,12, 20}

maximal runs:
- [3,4,5] 길이 3
- [11,12] 길이 2
- [20] 길이 1

minimum zone length = M일 때
길이 `>= M`인 run만 eligible extinction zone으로 인정한다.

해당 configuration의 zone-number set:

`Z(R,L,M)`

은 eligible runs 내부 숫자의 합집합이다.

### 중요한 금지
- zone 경계 앞/뒤 숫자는 포함하지 않는다.
- 과거 폐기 연구인 `전멸구간 경계번호 우선`을 재도입하지 않는다.
- zone을 결과에 맞춰 합치거나 자르지 않는다.
- 최대 zone 하나만 사후 선택하지 않는다.

---

## 5. 사전등록 configuration family

### LOOKBACK
- 5
- 10
- 20

### MINIMUM ZONE LENGTH
- 2
- 3
- 4
- 5

총:
`3 × 4 = 12 configurations`

고정 목록:

1. L5-M2
2. L5-M3
3. L5-M4
4. L5-M5
5. L10-M2
6. L10-M3
7. L10-M4
8. L10-M5
9. L20-M2
10. L20-M3
11. L20-M4
12. L20-M5

결과 확인 후 L/M 값을 추가·삭제하지 않는다.

---

## 6. 회차 단위 관측값

각 target round R, configuration c에 대해:

- `z_R` = |Z(R,c)| : eligible zone 내부 숫자 수
- `k_R` = R회 MAIN 6개 중 Z(R,c)에 포함된 숫자 수

z_R = 0이면 해당 configuration의 그 회차는
`NO_ZONE / NON-INFORMATIVE`로 기록한다.

zone이 있는 회차만 effect exposure에 포함하되,
전체 target round 수와 NO_ZONE 회차 수도 별도 저장한다.

---

## 7. PRIMARY 효과크기

configuration c에 대해:

`TOTAL_EXPOSURE = Σ z_R`

`TOTAL_HITS = Σ k_R`

관측 number-level rate:

`OBSERVED_RATE = TOTAL_HITS / TOTAL_EXPOSURE`

공정추첨 marginal expected rate:

`EXPECTED_RATE = 6/45`

PRIMARY effect size:

`RISK_DIFFERENCE = OBSERVED_RATE - 6/45`

Risk Difference는 **효과크기**다.

중요:
같은 회차의 45개 숫자는 독립 Bernoulli가 아니므로
number exposure를 독립 표본처럼 취급하여 유의성을 계산하지 않는다.

---

## 8. PRIMARY 추론 통계

각 회차에서 zone size z_R가 고정되어 있을 때,
공정추첨 하의 MAIN zone hit count는:

`K_R ~ Hypergeometric(N=45, K=z_R, n=6)`

기대값:

`E[K_R] = 6*z_R/45`

분산:

`Var[K_R] = 6*(z_R/45)*(1-z_R/45)*((45-6)/(45-1))`

configuration c의 표준화 통계량:

`T_c = Σ(K_R - E[K_R]) / sqrt(Σ Var[K_R])`

을 사용한다.

이 통계는 회차 내부 비독립성과
회차별 zone 크기 차이를 반영한다.

---

## 9. NULL MODEL

### PRIMARY GLOBAL NULL
각 target round R의 실제 과거 zone set은 그대로 고정한다.

각 simulation에서 각 R에 대해
1~45 중 6개를 복원 없이 공정하게 추출한다.

그 simulated MAIN과
실제 사전 계산된 Z(R,c)를 비교하여
12개 configuration의 T_c를 모두 계산한다.

한 simulation마다:

`MAX_ABS_T = max_c |T_c|`

를 저장한다.

### Monte Carlo 횟수
`100,000회`

### Seed
LOCK된 protocol hash로부터 deterministic하게 생성한다.

예:
`seed = first_64_bits(SHA256(protocol_hash + "EXP004_MAXT"))`

사람이 seed를 선택하지 않는다.

### global maxT p-value
각 configuration의:

`p_maxT = (1 + count(MAX_ABS_T_sim >= |T_observed|)) / (1 + N_sim)`

으로 계산한다.

PRIMARY family-wise alpha:
`0.05`

---

## 10. MULTIPLE TESTING

### PRIMARY
`global maxT FWER 0.05`

12개 configuration 전체를 하나의 family로 취급한다.

configuration 간 중첩과 의존성을 simulation에서 함께 보존한다.

### SECONDARY ROBUSTNESS
각 configuration의 asymptotic two-sided raw p를 계산한 뒤:

`Holm FWER 0.05`

도 함께 보고한다.

최종 신호 판정에서
PRIMARY 기준은 maxT다.

Holm은 보강/불일치 확인용이며,
Holm만 통과하고 maxT가 실패하면 `SUPPORTED`로 판정하지 않는다.

---

## 11. SECONDARY — INTEGRATED

MAIN + BONUS 7개는 별도 SECONDARY/SUPPORT 분석으로만 사용한다.

EXPECTED_RATE:
`7/45`

회차 단위 null:
`Hypergeometric(N=45, K=z_R, n=7)`

MAIN 결과와 섞어 PRIMARY 성공으로 승격하지 않는다.

---

## 12. 기간 안정성

공통 target range `21~1237` 기준:

### Overall
- 21~1237

### First Half
- 21~628

### Second Half
- 629~1237

### Recent100
- 1138~1237

### Recent50
- 1188~1237

### Recent20 — TEST_ONLY
- 1218~1237

### 기간 안정성 최소 기준
최종 SUPPORTED 후보는:
1. Overall effect direction과 First Half direction이 같고
2. Overall effect direction과 Second Half direction이 같아야 한다.

Recent100 / Recent50은 보조 안정성으로 보고한다.
두 구간이 모두 Overall과 반대 방향이면 최종 판정은 `INCONCLUSIVE` 이하로 제한한다.

Recent20은 TEST_ONLY이며 성공 판정에 사용하지 않는다.

---

## 13. WALKFORWARD 설계

이번 Walkforward는 **신호 선택의 미래 데이터 차단**까지 검증한다.

### 시작 조건
각 configuration은 최소:
`200 informative training rounds`
(z_R > 0인 과거 회차)

가 있어야 training inference 대상이 된다.

### 각 target round R 절차

1. 오직 `21~R-1` target history만 사용한다.
2. 각 configuration의 training T와 two-sided p를 계산한다.
3. available configurations 전체에 Holm FWER 0.05를 적용한다.
4. Holm 통과 configuration이 없으면:
   `NO_WALKFORWARD_SIGNAL`
5. 하나 이상이면 다음 deterministic 순서로 1개 선택:
   - smallest Holm adjusted p
   - tie: largest |T|
   - tie: smaller LOOKBACK
   - tie: smaller MIN_ZONE_LENGTH
6. 선택 configuration의 training Risk Difference sign을 잠근다.
7. R회 결과를 보기 전에:
   - selected configuration
   - zone set
   - predicted direction
   - data boundary
   - state/prediction hash
   를 저장한다.
8. 그 후 R outcome을 평가한다.

### Walkforward 평가 통계

선택된 configuration의 R회 zone hit count k_R와 기대값 E_R에 대해:

positive prediction:
`S_R = k_R - E_R`

negative prediction:
`S_R = E_R - k_R`

즉 training에서 예측한 방향이 미래에 유지되면
양의 score가 된다.

전체 exposed rounds의:

`S_TOTAL = Σ S_R`

을 계산하고,
각 exposed round의 zone size를 고정한
공정추첨 simulation으로 one-sided p-value를 계산한다.

### Walkforward 최소 표본
`100 signal-exposed rounds`

미만이면:
`INCONCLUSIVE — INSUFFICIENT_WALKFORWARD_EXPOSURE`

### Walkforward 성공
- exposed rounds >= 100
- directional null p <= 0.05
- future leakage = 0
- prediction hash mismatch = 0

---

## 14. 최종 성공 / 실패 기준

### SUPPORTED
모두 충족해야 한다.

1. Overall MAIN에서 최소 한 configuration이 `maxT FWER <= 0.05`
2. 해당 효과 방향이 First Half와 Second Half에서 동일
3. Recent100/Recent50이 둘 다 반대 방향이 아님
4. Walkforward signal-exposed rounds >= 100
5. Walkforward directional null p <= 0.05
6. 미래 데이터 누수 0
7. hash mismatch 0

### INCONCLUSIVE
다음 중 하나:
- Overall maxT는 통과했지만 기간 안정성 부족
- Overall 신호는 있으나 Walkforward exposure <100
- Walkforward direction이 통계적으로 재현되지 않음
- 중요한 구현/데이터 제한이 존재하나 완전 실패로 단정 불가

### FAILED
다음 중 하나:
- Overall MAIN maxT 통과 configuration 0
- 또는 충분한 Walkforward exposure에도 방향 재현 실패
- 또는 효과가 random/null과 구별되지 않음

### RETIRED
연구 정의 자체의 치명적 결함이나 데이터 구조상 검증 불가능할 때만 사용.

---

## 15. 설명용 A/B/C/D

A:
Overall + multiplicity + period + Walkforward에서 재현 가능한 신호

B:
Overall에서는 신호가 있으나 Walkforward 미재현

C:
관찰 차이는 있으나 global null / multiplicity 이후 무작위와 구별 어려움

D:
실질적 효과 자체가 거의 없음

공식 Experiment 상태가 우선이고 A/B/C/D는 설명용이다.

---

## 16. 최소 표본 및 희소 configuration 처리

각 configuration별로 반드시 보고:
- informative rounds
- total zone exposures
- zone-size distribution
- total hits

Overall에서:
- informative rounds < 200이면 해당 configuration은
  `LOW_EXPOSURE / NON_CONFIRMATORY`
- maxT family 계산에는 포함하되
  단독 성공 근거로 사용하지 않는다.

희소 configuration의 큰 Risk Difference를
성과로 포장하지 않는다.

---

## 17. 사후 금지

결과를 본 뒤 다음을 하지 않는다.

- lookback 추가/삭제
- minimum zone length 추가/삭제
- 가장 좋아 보이는 configuration만 재실험
- positive 방향만 사후 선택
- zone 경계번호 추가
- zone 중심부/양끝 별도 분할
- 회복속도 3/5/10/20회 추가
- 이동×전멸 교차효과 추가
- weighting / hidden score 생성
- NUMBER/TRIO/PAIR/CORE에 연결
- 1238 맞춤 튜닝
- 실패 결과 삭제

새 질문은 새 Experiment 또는 새 version으로만 처리한다.

---

## 18. 미래 데이터 차단

회차 R의 zone은 오직 R-1까지의 MAIN으로 계산한다.

금지:
- R MAIN
- R BONUS
- R 이후 데이터
- 결과를 본 뒤 zone 정의 변경

Walkforward prediction/state hash는
R outcome 조회 전에 생성되어야 한다.

---

## 19. 공식 P45 보호

- ENGINE = FROZEN 유지
- 공식 gate 변경 금지
- threshold 변경 금지
- NUMBER_PASS 변경 금지
- HOLD→PASS 금지
- 공식 NUMBER/TRIO/PAIR/CORE 변경 금지
- 공식 DB 수정 금지
- protected canonical hash 변경 금지

EXP-004가 SUPPORTED여도
자동 공식 승격하지 않는다.

---

## 20. Preflight 필수 항목

실제 결과 분석 전 최소 확인:

1. 데이터 1~1237 정렬
2. 회차 중복 0
3. 회차 누락 0
4. 각 MAIN 6개 유일
5. 번호 범위 1~45
6. BONUS 유효
7. snapshot hash 일치
8. 12 configuration 정확 생성
9. maximal contiguous run 계산 fixture PASS
10. zone boundary 비포함 확인
11. R회 zone 계산에서 R outcome 미사용
12. Hypergeometric 기대값/분산 unit test
13. Risk Difference unit test
14. maxT 12-family 처리 확인
15. Holm 구현 확인
16. 기간 경계 고정 확인
17. Walkforward 1~R-1 차단 확인
18. prediction hash pre-outcome 생성 확인
19. 동일 입력 deterministic repeat PASS
20. 공식 P45 파일/DB 변경 0

하나라도 치명적 실패하면
실제 결과 분석을 시작하지 않는다.

---

## 21. 결과 보고 형식

최소 보고:

- DATA_HASH_VERIFIED
- PROTOCOL_HASH_VERIFIED
- VALID_TARGET_ROUNDS
- 12 configuration별 informative rounds / exposure / hit / RD / T / raw p / Holm / maxT
- MAIN maxT pass count
- MAIN Holm pass count
- BEST_OBSERVED_CONFIGURATION (관찰값일 뿐 추천 아님)
- First/Second/Recent100/Recent50/Recent20
- INTEGRATED secondary
- Walkforward rounds
- Walkforward signal-exposed rounds
- Walkforward directional p
- future leakage
- hash mismatch
- FINAL_EXPERIMENT_JUDGMENT
- A/B/C/D
- DRAW_PREDICTION_SIGNAL_SUPPORTED
- RECOMMENDATION_CONNECTION_ALLOWED_NOW = NO
- OFFICIAL_ENGINE_CHANGED = NO

---

## 22. 현재 다음 단계

1. 이 LOCKED protocol의 내용은 결과를 보기 전에 확정됐다.
2. 다음 단계는 동일한 `1~1237` draw snapshot 데이터의 검증이다.
3. 데이터 검증 전 실제 EXP-004 outcome 분석은 실행하지 않는다.
4. 데이터 snapshot이 예상 hash와 일치하면 ChatGPT가 가능한 분석을 직접 수행한다.
5. 로컬 P45 Registry/Decision/STATE 반영 및 독립 재현이 필요할 때만 Work를 사용한다.

## 23. LOCK 선언

- LOCK 승인일: `2026-08-20`
- Human Alias: `EXP-004`
- Protocol status: `LOCKED`
- Outcome viewed before lock: `NO`
- Backtest run before lock: `NO`
- Walkforward run before lock: `NO`
- Recommendation created before lock: `NO`
- Official engine changed: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED` — 로컬 Registry 반영 전까지 추측하지 않는다.

이 파일이 EXP-004 V1의 결과 전 연구 정의 기준본이다.

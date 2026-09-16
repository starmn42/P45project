# P45 EXP-008 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-008`
- 연구명: `PAIRWISE GAP-SET CARRYOVER — R-1 → R`
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

회차 `R-1`의 MAIN 6개 내부에서 관찰된
**고유 pairwise absolute gap 길이 집합**이
다음 회차 `R`의 MAIN 6개 내부 pairwise gap에도
공정추첨 기대보다 더 많이 또는 더 적게 재등장하는지 검증한다.

핵심 질문:

> `직전 회차의 "숫자 자체"가 아니라, 그 회차 내부 간격 구조가 다음 회차에 재현 가능한 정보를 주는가?`

이번 V1은 **gap-set carryover 하나만** 검증한다.

공식 NUMBER/TRIO/PAIR/CORE/FALLBACK에는 연결하지 않는다.

---

## 2. EXP-003과의 분리

EXP-003은:

`R-1의 각 번호 → R의 각 번호까지의 absolute distance`

라는 **회차 간 number movement**를 연구했다.

EXP-008은:

`R-1 내부 15개 pair의 gap 구조 → R 내부 15개 pair의 gap 구조`

를 연구한다.

즉:
- EXP-003 = cross-round number distance
- EXP-008 = within-round spacing-structure carryover

로 질문이 다르다.

EXP-003 결과를 살리기 위한 재튜닝이 아니다.

---

## 3. 연구가설과 반대가설

### H1 — 연구가설

직전 회차에 등장했던 고유 pairwise gap 길이들이
다음 회차 내부 pair들에서 공정추첨 조건부 기대와 다른 빈도로 나타나며,
그 방향과 효과가 기간 분할 및 Walkforward에서도 재현된다.

### H0 / Opposite Hypothesis

직전 회차 gap-set과 다음 회차 gap들의 겹침은
공정추첨에서 발생하는 구조적 빈도 차이로 설명되며,
미래 구간에서는 재현되지 않는다.

### 방향

PRIMARY:
`two-sided`

- positive = 직전 gap-set이 다음 회차에 기대보다 많이 재현
- negative = 기대보다 적게 재현

결과 후 방향 선택 금지.

---

## 4. 데이터 경계

예정 데이터:
- Draw Range: `1~1237`
- PRIMARY: MAIN 6
- SECONDARY: MAIN + BONUS 7
- canonical SHA-256:
  `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`

Target:
`R = 2~1237`

총 예정 target:
`1,236회`

회차 R의 signal structure는
오직 `MAIN(R-1)`에서 생성한다.

R MAIN/BONUS는 outcome으로만 사용한다.

---

## 5. Pairwise gap 정의

회차 T의 MAIN 6개를:

`x1 < x2 < ... < x6`

로 정렬한다.

모든 unordered pair:

`C(6,2) = 15개`

에 대해 absolute gap:

`g_ij = |xj - xi|`

를 계산한다.

가능한 gap:
`1~44`

---

## 6. 직전 회차 gap-set

회차 R의 predictor:

`G_R = { |a-b| : a,b ∈ MAIN(R-1), a<b }`

단:
**고유 gap 길이의 집합(set)** 으로 사용한다.

즉 같은 gap이 직전 회차에 여러 번 등장해도
가중치를 추가하지 않는다.

### 금지
- multiplicity weighting 금지
- adjacent gap만 별도 선택 금지
- 특정 gap 길이만 사후 선택 금지

---

## 7. PRIMARY 관측값

회차 R의 MAIN 6개 내부 15개 unordered pair 각각에 대해
그 pair의 absolute gap이 `G_R`에 속하는지 본다.

PRIMARY count:

`H_R = # { current MAIN unordered pairs whose gap ∈ G_R }`

가능한 값:
`0~15`

중요:
현재 회차에서 같은 gap이 여러 pair에 발생하면
각 pair는 실제 구조적 occurrence로 각각 1회 카운트한다.

직전 회차에서는 gap-set membership만 사용하고,
현재 회차에서는 matching pair occurrence 수를 센다.

---

## 8. Graph 표현

직전 gap-set `G_R`로 1~45 번호를 vertex로 하는 graph를 만든다.

edge:

`(u,v)`가 존재 iff `|u-v| ∈ G_R`

이 graph를 `A_R`라고 한다.

그러면 `H_R`은:
회차 R의 random 6-number vertex subset이
`A_R`에서 유도하는 edge 수와 같다.

이 표현을 이용해 공정추첨 조건부 기대와 분산을 정확히 계산한다.

---

## 9. 조건부 기대

`m_R` =
graph `A_R`의 전체 edge 수.

gap d 하나가 만드는 edge 수:
`45-d`

따라서:

`m_R = Σ_{d ∈ G_R} (45-d)`

공정추첨에서 임의의 특정 edge 두 endpoint가
MAIN 6개에 모두 포함될 확률:

`p2 = C(43,4) / C(45,6)`
`   = (6×5)/(45×44)`
`   = 1/66`

따라서 exact conditional expectation:

`E_R = E[H_R | F_(R-1)] = m_R * p2`

---

## 10. 조건부 분산

graph `A_R`에서:

- `m_R` = edge 수
- `deg(v)` = vertex v의 degree
- `A_R_shared = Σ_v C(deg(v),2)`
  = 한 vertex를 공유하는 unordered edge-pair 수
- `D_R = C(m_R,2) - A_R_shared`
  = 서로 vertex-disjoint인 unordered edge-pair 수

확률:

`p2 = P(특정 2 vertices 모두 선택)`
`p3 = P(특정 3 vertices 모두 선택)`
`p4 = P(특정 4 vertices 모두 선택)`

즉:

`p2 = (6×5)/(45×44)`

`p3 = (6×5×4)/(45×44×43)`

`p4 = (6×5×4×3)/(45×44×43×42)`

exact conditional variance:

`Var_R = m_R*p2*(1-p2)`
`      + 2*A_R_shared*(p3-p2^2)`
`      + 2*D_R*(p4-p2^2)`

이를 unit test로 검증한다.

---

## 11. PRIMARY 효과크기

전체 target rounds N에 대해:

`TOTAL_PAIR_OPPORTUNITIES = 15*N`

`TOTAL_MATCHED_PAIRS = ΣH_R`

관측 pair-match rate:

`OBSERVED_PAIR_MATCH_RATE = ΣH_R / (15*N)`

조건부 기대 pair-match rate:

`EXPECTED_PAIR_MATCH_RATE = ΣE_R / (15*N)`

PRIMARY effect size:

`PAIR_MATCH_RD = OBSERVED_PAIR_MATCH_RATE - EXPECTED_PAIR_MATCH_RATE`

추가:

`MEAN_EXCESS_MATCHED_PAIRS = mean(H_R - E_R)`

도 보고한다.

---

## 12. PRIMARY analytical statistic

회차 residual:

`e_R = H_R - E_R`

fair-draw null에서:

`E[e_R | F_(R-1)] = 0`

이므로 predictable martingale-difference 구조다.

PRIMARY exact-variance standardized statistic:

`T = Σe_R / sqrt(ΣVar_R)`

analytical p:
`two-sided normal approximation`

---

## 13. 100,000회 martingale multiplier bootstrap

analytical approximation만으로 성공 판정하지 않는다.

self-normalized observed statistic:

`T_SN = Σe_R / sqrt(Σe_R^2)`

각 bootstrap b에서 independent Rademacher multiplier:

`w_R ∈ {-1,+1}`

를 확률 1/2로 생성한다.

`T*_b = Σ(w_R*e_R) / sqrt(Σe_R^2)`

two-sided bootstrap p:

`p_boot = (1 + count(|T*_b| >= |T_SN|)) / (1+B)`

B:
`100,000`

Seed:
LOCKED protocol hash로 deterministic 파생.

PRIMARY success에는:
- analytical p <= 0.05
- multiplier-bootstrap p <= 0.05

둘 다 필요하다.

---

## 14. 다중검정 정책

EXP-008 V1 PRIMARY hypothesis는 하나:

`직전 unique pairwise gap-set의 다음 회차 pair occurrence carryover`

따라서 PRIMARY configuration family는 없다.

아래는 PRIMARY 승격 금지:

- gap 1만
- gap 2만
- gap 3만
- 특정 fixed gap
- adjacent gaps only
- 최대 gap / 최소 gap
- repeated gap multiplicity
- gap count가 많은/적은 회차
- 특정 gap-set 크기
- arithmetic progression 회차만
- consecutive-number 회차만

결과 후 잘 나온 subgroup을 선택하지 않는다.

---

## 15. 기간 안정성

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

1. Overall effect direction = First Half
2. Overall effect direction = Second Half
3. Recent100/50이 모두 Overall 반대면 `INCONCLUSIVE` 이하
4. Recent20은 성공판정 제외

---

## 16. SECONDARY — INTEGRATED 7

동일 직전 MAIN gap-set `G_R`를 사용한다.

현재 `INTEGRATED(R)` 7개 내부 unordered pair:

`C(7,2)=21개`

중 gap이 G_R에 속하는 pair occurrence 수를:

`H7_R`

로 정의한다.

공정추첨 7-subset 조건부 확률:

`q2 = (7×6)/(45×44)`
`q3 = (7×6×5)/(45×44×43)`
`q4 = (7×6×5×4)/(45×44×43×42)`

동일 graph counts `m_R, A_R_shared, D_R`를 이용해
E/Var를 계산한다.

SECONDARY/SUPPORT만 사용한다.

MAIN 실패를 뒤집지 않는다.

---

## 17. Walkforward 설계

### 최소 training
`200 target rounds`

각 target R에서:

1. training은 오직 `2~R-1` target outcomes 사용
2. training analytical T와 two-sided p 계산
3. `p <= 0.05`일 때만 historical signal 형성
4. 없으면 `NO_WALKFORWARD_SIGNAL`
5. 있으면 training effect direction 잠금
6. current `G_R`은 오직 MAIN(R-1)로 생성
7. R outcome 전에:
   - source round R-1
   - G_R
   - graph edge count m_R
   - E_R / Var_R
   - predicted direction
   - training boundary
   - prediction hash
   저장
8. 이후 R outcome H_R 평가

---

## 18. Walkforward 성과

각 exposed R:

positive direction:
`S_R = H_R - E_R`

negative direction:
`S_R = E_R - H_R`

전체:

`S_TOTAL = ΣS_R`

Walkforward analytical directional statistic:

`T_WF = S_TOTAL / sqrt(ΣVar_R_exposed)`

one-sided p를 계산한다.

추가 robustness:

`100,000회 directional martingale multiplier bootstrap`

을 수행한다.

최소 exposed:
`100회`

성공:
- exposed >= 100
- analytical one-sided p <= 0.05
- bootstrap one-sided p <= 0.05
- future leakage = 0
- prediction hash mismatch = 0

---

## 19. 최종 성공 / 실패 기준

### SUPPORTED

모두 충족:

1. Overall MAIN analytical p <= 0.05
2. Overall multiplier-bootstrap p <= 0.05
3. Overall/First/Second 방향 동일
4. Recent100/50 모두 반대가 아님
5. Walkforward exposed >= 100
6. WF analytical directional p <= 0.05
7. WF bootstrap directional p <= 0.05
8. future leakage = 0
9. hash mismatch = 0

### INCONCLUSIVE

- retrospective 신호 있으나 기간 불안정
- retrospective 신호 있으나 WF 노출 <100
- 최근구간 구조가 강하게 반대
- 계산/구현 검증에 치명적이지 않은 제한 존재

### FAILED

- Overall PRIMARY가 null과 구별되지 않음
- 또는 multiplier bootstrap에서 구별되지 않음
- 또는 충분한 Walkforward에서 재현 실패

---

## 20. 설명용 A/B/C/D

A:
Overall + bootstrap + 기간 + Walkforward 재현

B:
retrospective 신호 있으나 미래 재현 실패/불안정

C:
관찰 차이는 있으나 null과 구별 어려움

D:
실질적인 gap-set carryover 효과가 거의 없음

---

## 21. 이번 V1 명시적 제외

- fixed gap 하나씩 검정
- 1~44 gap family multiple testing
- adjacent-gap vector similarity
- arithmetic progression count
- 등차수열 3개/4개 여부
- consecutive-number 특화
- gap multiplicity weighting
- gap별 점수
- 직전 번호 자체의 이동
- exact repeat 제거/강제
- END_DIGIT 결합
- extinction 결합
- analog/similar-round 결합
- NUMBER/TRIO/PAIR/CORE 연결
- 추천번호 생성
- 1238 맞춤

---

## 22. 사후 금지

결과 후:

- 특정 gap만 선택
- gap-set size threshold 생성
- multiplicity 가중치 추가
- adjacent gap only로 변경
- arithmetic progression만 선택
- 특정 기간만 선택
- number movement와 결합
- 추천번호 직접 연결

금지.

새 질문은 새 Experiment/version으로만 처리한다.

---

## 23. 미래 데이터 차단

target R에서:

predictor:
`G_R = gap-set(MAIN(R-1))`

만 사용한다.

금지:
- R MAIN/BONUS로 predictor 생성
- R 이후 데이터
- 결과 후 gap 정의 수정

Walkforward prediction/state hash는 R outcome 조회 전에 생성한다.

---

## 24. 공식 P45 보호

- OFFICIAL ENGINE = FROZEN
- 공식 gate/threshold/signature 변경 금지
- 공식 PAIR 구조 변경 금지
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
8. target 2~1237
9. 15 unordered pair 생성 PASS
10. absolute gap 1~44 PASS
11. unique previous gap-set fixture PASS
12. current matching-pair count fixture PASS
13. graph edge count m_R fixture PASS
14. graph degree/shared-edge count fixture PASS
15. p2/p3/p4 exact probability unit test
16. expectation formula unit test
17. variance formula brute-force small-fixture 검증
18. analytical T unit test
19. multiplier bootstrap deterministic seed
20. period boundary PASS
21. WF training R-1 차단
22. prediction hash pre-outcome
23. 공식 P45 변경 0

치명적 실패 시 outcome 분석 중단.

---

## 26. 결과 보고

- DATA_HASH_VERIFIED
- PROTOCOL_HASH_VERIFIED
- VALID_TARGET_ROUNDS
- GAP_SET_SIZE_DISTRIBUTION
- GRAPH_EDGE_COUNT_DISTRIBUTION
- TOTAL_PAIR_OPPORTUNITIES
- TOTAL_MATCHED_PAIRS
- OBSERVED_PAIR_MATCH_RATE
- EXPECTED_PAIR_MATCH_RATE
- PAIR_MATCH_RD
- MEAN_EXCESS_MATCHED_PAIRS
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
- WALKFORWARD_ANALYTICAL_P
- WALKFORWARD_BOOTSTRAP_P
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
3. ChatGPT가 preflight + retrospective + 100,000회 multiplier bootstrap + Walkforward를 수행한다.
4. 로컬 P45 독립 재현·DB/Registry/Decision/STATE 반영이 필요할 때만 Work를 사용한다.

## 28. LOCK 선언

- LOCK 승인일: `2026-08-20`
- Human Alias: `EXP-008`
- Protocol status: `LOCKED`
- Outcome viewed before lock: `NO`
- Backtest run before lock: `NO`
- Walkforward run before lock: `NO`
- Recommendation created before lock: `NO`
- Official engine changed: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

이 파일이 EXP-008 V1의 결과 전 연구 정의 기준본이다.

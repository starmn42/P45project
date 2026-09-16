# P45 EXP-011 사전등록 프로토콜 LOCKED 001

## 문서 상태
- Human Alias: `EXP-011`
- 연구명: `MIRROR-COMPLEMENT CARRYOVER — n → 46-n, R-1 → R`
- Family: `DETERMINISTIC_MIRROR_TRANSFORM_V1`
- 상태: `LOCKED / READY_FOR_BACKTEST`
- LOCK 승인일: `2026-08-21`
- 실제 EXP-011 outcome 조회 전 LOCK: `YES`
- 백테스트 실행 전 LOCK: `YES`
- Walkforward 실행 전 LOCK: `YES`
- 추천번호 생성: `NO`
- 공식 ENGINE 변경: `NO`
- Canonical Experiment ID: `NOT_ASSIGNED`

> `BATCH_WHEN_SAFE` 운영에 따라 DRAFT 사용자 산출물 없이 실제 EXP-011 결과 계산 전에 이 LOCKED 기준본을 먼저 생성했다.
> 이번 V1은 자연대칭 변환 `m(n)=46-n` 하나만 검정하며, 결과를 본 뒤 다른 rotation/shift/transform을 추가하지 않는다.

## 1. 연구 목적
직전 회차 MAIN 숫자의 **1~45 중심 거울상**이 다음 회차 MAIN에
공정추첨 기대보다 더 많이 또는 더 적게 출현하는지 검증한다.

거울변환:
`m(n)=46-n`

예:
- 1 ↔ 45
- 2 ↔ 44
- ...
- 22 ↔ 24
- 23 ↔ 23

23은 유일한 fixed point다.
이번 V1은 exact-repeat 효과와 분리하기 위해 직전 회차 숫자 23이 있더라도 `23→23`은 candidate에서 제외한다.

## 2. EXP-003과의 분리
EXP-003은 cross-round absolute-distance 구조를 연구했다.
EXP-011의 변환은 source n마다 거리 `|46-2n|`가 달라진다.
따라서 하나의 고정-distance stratum이 아니며, `n→46-n`이라는 결정적 involution relation 자체를 검정한다.
EXP-003 실패를 특정 거리로 재튜닝하는 연구가 아니다.

## 3. 가설 / 반대가설
### H1
직전 MAIN의 nontrivial mirror counterparts가 다음 MAIN에서 공정추첨 조건부 기대와 다른 빈도로 출현하며,
기간 및 Walkforward에서도 재현된다.

### H0 / Opposite
관찰되는 mirror counterpart 출현 차이는 공정추첨 변동으로 설명된다.

PRIMARY: `two-sided`
- positive = mirror counterpart가 기대보다 많이 출현
- negative = 기대보다 적게 출현

결과 후 방향 선택 금지.

## 4. 데이터
- Draw Range: `1~1237`
- PRIMARY: MAIN 6
- SECONDARY: MAIN+BONUS 7
- canonical SHA-256:
  `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`
- target rounds: `R=2~1237` = `1,236`

## 5. PRIMARY candidate set
각 target R에서 직전 MAIN을 `P_R=MAIN(R-1)`로 둔다.

`C_R = {46-n : n ∈ P_R, n != 23}`

변환은 injective이므로:
- R-1에 23이 없으면 `z_R=6`
- R-1에 23이 있으면 `z_R=5`

23은 candidate에 포함하지 않는다.
추가 제거/가중치/threshold 없음.

## 6. 회차 관측값
`k_R = |MAIN(R) ∩ C_R|`

조건부 fair-draw null:
`K_R ~ Hypergeometric(N=45,K=z_R,n=6)`

`E_R = 6*z_R/45`

`Var_R = 6*(z_R/45)*(1-z_R/45)*((45-6)/(45-1))`

## 7. 효과크기
`TOTAL_EXPOSURE = Σz_R`
`TOTAL_HITS = Σk_R`

`OBSERVED_RATE = TOTAL_HITS/TOTAL_EXPOSURE`
`EXPECTED_RATE = 6/45`
`RISK_DIFFERENCE = OBSERVED_RATE - 6/45`

## 8. PRIMARY analytical statistic
회차 residual:
`e_R = k_R-E_R`

C_R은 R outcome 전에 R-1 history만으로 결정되므로 fair-draw null에서:
`E[e_R | F_(R-1)] = 0`

PRIMARY:
`T = Σe_R / sqrt(ΣVar_R)`

two-sided normal p.

## 9. PRIMARY exact-structure full-sequence Monte Carlo
23 fixed-point 제외 때문에 candidate size는 5/6으로만 변한다.

full-sequence null을 정확히 재현하기 위해 각 simulated path에서 다음 Markov-additive 구조를 사용한다.

초기:
- round 1의 `H_1 = I(23∈MAIN(1))`
- `P(H_1=1)=6/45`
- `z_2 = 5 if H_1=1 else 6`

각 target R에서 현재 z_R가 주어졌을 때:
1. `H_R = I(23∈MAIN(R))`
2. `P(H_R=1)=6/45`
3. H_R=1이면 남은 5개를 non-23 population 44개에서 뽑으므로
   `k_R ~ Hypergeometric(N=44,K=z_R,n=5)`
4. H_R=0이면 23을 제외한 44개에서 6개를 뽑으므로
   `k_R ~ Hypergeometric(N=44,K=z_R,n=6)`
5. `z_(R+1)=5 if H_R=1 else 6`

이 구조는 mirror candidate가 23을 포함하지 않는 점과 current round의 23 포함 여부가 다음 candidate size를 결정하는 점을 함께 재현한다.

simulation:
`100,000 full paths`

각 path에서 동일 T를 계산한다.

Seed:
LOCKED protocol hash 기반 deterministic.

PRIMARY success:
- analytical p<=0.05
- full-sequence MC p<=0.05

둘 다 필요.

## 10. 기간 안정성
- Overall `2~1237`
- First Half `2~619`
- Second Half `620~1237`
- Recent100 `1138~1237`
- Recent50 `1188~1237`
- Recent20 `1218~1237` TEST_ONLY

SUPPORTED 후보:
1. Overall/First/Second 방향 동일
2. Recent100/50이 둘 다 Overall 반대가 아님
3. Recent20은 성공판정 제외

## 11. SECONDARY — INTEGRATED
동일 C_R에 대해:
`k7_R = |INTEGRATED(R) ∩ C_R|`

null:
`Hypergeometric(45,z_R,7)`

SECONDARY만 사용.
MAIN 실패를 뒤집지 않는다.

## 12. Walkforward
최소 training:
`200 prior target rounds`

각 R:
1. training은 `2~R-1`
2. training PRIMARY analytical two-sided p<=0.05일 때만 signal
3. direction = sign(training RD)
4. R outcome 전에 source R-1, source MAIN, mirror candidate C_R, z_R, direction, training boundary, state hash 고정
5. 이후 R의 k_R 평가

score:
positive `S_R=k_R-E_R`
negative `S_R=E_R-k_R`

## 13. Walkforward null
Walkforward exposure/direction은 과거에 의해 적응적으로 결정되므로 robustness는 `100,000회 full adaptive null`을 사용한다.

각 null path에서:
1. section 9의 exact 23-state Markov 구조로 k/z path 생성
2. 각 R에서 그 null path의 과거 residual만으로 training p 계산
3. 동일 p<=0.05 signal rule과 direction rule 재적용
4. exposed score 합산
5. observed `T_WF` 이상을 one-sided 비교

observed minimum exposed:
`100`

성공:
- exposed>=100
- analytical martingale directional p<=0.05
- full-adaptive MC p<=0.05
- future leakage=0
- hash mismatch=0

## 14. 다중검정 / Transform family
EXP-011 V1 PRIMARY transform은 하나:
`n→46-n`, fixed point 23 제외.

`DETERMINISTIC_MIRROR_TRANSFORM_V1`은 EXP-011 종료와 동시에 CLOSED.

결과 후 다음을 EXP-011 구제용으로 추가하지 않는다:
- `45-n`
- modulo rotation
- +k / -k shift
- 23 포함 mirror
- 특정 source 숫자만 mirror
- 특정 mirror distance만
- 최근 mirror만
- mirror + ending/gap/extinction 결합

새 transform 연구가 필요하면 결과와 독립적인 새 family와 multiplicity policy가 먼저 필요하다.

## 15. 사전등록 EARLY-STOP
- Overall analytical 또는 full-sequence MC가 0.05를 넘으면 SUPPORTED 불가능.
- analytical 구현 확인을 위해 full-sequence MC까지 수행.
- 둘 중 하나라도 실패하면 expensive full-adaptive Walkforward MC는 생략 가능.
- 기간/secondary는 설명용 계산 가능.

## 16. 최종 판정
### SUPPORTED
모두:
1. Overall analytical p<=0.05
2. full-sequence MC p<=0.05
3. Overall/First/Second 방향 동일
4. Recent100/50 둘 다 반대 아님
5. WF exposed>=100
6. WF analytical p<=0.05
7. WF full-adaptive MC p<=0.05
8. leakage=0
9. hash mismatch=0

### INCONCLUSIVE
retrospective 신호 있으나 기간/WF 표본 또는 안정성 부족.

### FAILED
Overall PRIMARY가 null과 구별되지 않거나, 충분한 WF에서 미재현.

## 17. PROGRAM_LEVEL_DISCOVERY_GUARD
- 단일 EXP SUPPORTED만으로 Promotion Candidate 금지.
- 별도 독립 재현 또는 prospective confirmation 필요.
- 공식 ENGINE 자동 승격 금지.

## 18. 공식 보호
- OFFICIAL ENGINE = FROZEN
- gate/threshold/signature/code/DB 변경 금지
- NUMBER/TRIO/PAIR/CORE 변경 금지
- hidden score/arbitrary weight 금지
- 추천번호 생성 금지

## 19. Preflight
1. 데이터 1~1237 / 중복0 / 누락0
2. MAIN6 unique / 1~45 / BONUS valid
3. snapshot hash
4. mirror involution `m(m(n))=n`
5. unique fixed point =23
6. 23 candidate exclusion
7. z_R ∈ {5,6}
8. actual k fixture
9. Hypergeometric E/Var
10. full-sequence Markov null joint-distribution fixture
11. deterministic MC
12. target/period boundary
13. WF future block/state hash
14. official P45 변경 0

치명적 실패 시 분석 중단.

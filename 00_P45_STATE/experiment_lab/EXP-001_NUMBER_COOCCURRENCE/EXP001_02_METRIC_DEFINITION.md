# EXP-001 지표 정의

## 이론 기준

### MAIN 6/45

특정 pair가 한 회차 본번호에 함께 포함될 확률:

`p0_main = C(43,4) / C(45,6) = (6/45)×(5/44) = 1/66 = 0.015151515...`

`P(B|A, MAIN) = 5/44 = 0.11363636...`

### INTEGRATED 7/45

본번호+보너스를 순서 없는 7개 집합으로 볼 때:

`p0_integrated = C(43,5) / C(45,7) = (7/45)×(6/44) = 7/330 = 0.021212121...`

`P(B|A, INTEGRATED) = 6/44 = 3/22 = 0.13636363...`

두 scope 기준을 섞지 않는다.

## Count와 Exposure

- `round_exposure_count N`: 해당 scope에 적격인 회차 수
- `observation_count O`: pair가 함께 나온 회차 수
- `expected_count E = N×p0_scope`
- `observed_rate = O/N`
- 조건부 보조표: A가 나온 회차 수와 그중 B도 나온 회차 수를 별도 저장하되, unordered pair의 PRIMARY 판정에는 사용하지 않는다.

## 사전 고정 지표

### PRIMARY EFFECT METRIC

`risk_difference = observed_rate - p0_scope`

- 양수: 무작위 기준보다 과다 관측
- 음수: 무작위 기준보다 과소 관측
- 0 부근: 기준과 유사

### PRIMARY INFERENCE

- 귀무확률 `p0_scope`의 two-sided exact binomial test
- 불확실성: 95% Clopper-Pearson exact interval
- MAIN 990개의 raw p-value를 Holm으로 보정

### SECONDARY METRICS

- `lift = observed_rate / p0_scope`
- `standardized_residual = (O-E)/sqrt(N×p0×(1-p0))`
- `phi`는 A/B 2×2 출현표의 기술 지표로만 저장
- INTEGRATED의 동일 지표는 SUPPORT이며 MAIN을 대체하지 않는다.

SECONDARY 지표 중 가장 좋아 보이는 것을 사후 PRIMARY로 바꾸지 않는다.

## 방향 일치

- `POSITIVE`: risk_difference > 0
- `NEGATIVE`: risk_difference < 0
- `NEUTRAL`: 정확히 0

기간별 방향은 raw count와 함께 저장한다. 반올림값으로 방향을 정하지 않는다.

## Network 표현

edge는 `EXP001_05_SUCCESS_FAILURE_CRITERIA.md`의 모든 MAIN 기준을 통과한 pair에만 부여할 수 있다. node degree, centrality, community, clustering은 EXP-001 판정이나 추천에 사용하지 않으며 후속 별도 EXPERIMENT 대상이다.


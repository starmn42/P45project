# EXP-001 NULL 및 다중검정 정책

## PRIMARY NULL

`IID_FAIR_DRAW_NULL`

- 각 회차 MAIN은 1~45에서 균등한 6개 부분집합
- 각 회차 INTEGRATED는 균등한 7개 부분집합
- 회차 간 독립
- pair별 exact binomial p-value와 이론확률을 사용

## PRIMARY MULTIPLE-TEST POLICY

- 방법: `Holm FWER`, family alpha `0.05`, two-sided
- MAIN 990개를 하나의 primary family로 보정
- INTEGRATED 990개는 별도 support family로 보정
- OVERALL, FIRST_HALF, SECOND_HALF, RECENT_100, RECENT_50도 서로 다른 family로 보정하고 결과를 합치지 않는다.
- BH-FDR은 secondary sensitivity table로만 계산할 수 있고 Holm 실패를 뒤집지 못한다.

## GLOBAL / PERMUTATION NULL

### IID_SYNTHETIC_NULL

- 동일한 회차 수와 scope 크기를 가진 공정 추첨 dataset을 생성
- 각 dataset에서 990개 전체의 최대 절대 standardized residual을 기록하는 maxT family null
- 반복 수: 100,000
- PRNG algorithm/version과 seed `450990001`을 protocol lock에 포함
- global p-value는 `(1 + null_maxT >= observed_maxT인 반복 수)/(100001)`

### ROUND_ORDER_PERMUTATION

회차 순서 permutation은 OVERALL pair count를 바꾸지 않으므로 전체 동시출현 검정에는 사용하지 않는다. FIRST/SECOND, recent 및 walkforward의 시간 지속성이 우연한 순서로 설명되는지 평가하는 support null로만 사용한다.

- 반복 수: 100,000
- 전체 회차의 6개/7개 집합은 보존하고 시간 label만 섞음
- seed와 PRNG version을 사전 잠금

### FIXED_MARGINAL_NULL

숫자별 전체 출현빈도와 회차별 선택개수는 보존하면서 pair 연결만 바꾸는 이분 incidence matrix swap null을 support 분석으로 둔다.

- 서로 다른 두 회차와 두 숫자의 `1,0 / 0,1` 패턴을 `0,1 / 1,0`으로 바꾸는 valid switch만 허용
- row sum과 column sum 보존
- burn-in: `10×N×45` accepted switches
- sample 간 간격: `N×45` accepted switches
- 10,000 samples
- 수렴 진단 실패 시 이 null 결과는 `INCOMPLETE`, MAIN 판정을 변경하지 않음

## 다중검정 감사

- 전체 990개 raw/adjusted p-value를 저장한다.
- 양·음 방향 모두 공개한다.
- 유의 pair가 없어도 결과를 삭제하지 않는다.
- 보정법·family·alpha·반복 수를 결과 확인 후 바꾸지 않는다.


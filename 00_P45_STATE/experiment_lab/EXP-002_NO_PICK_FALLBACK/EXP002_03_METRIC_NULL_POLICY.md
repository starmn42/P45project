# EXP-002 지표와 null 정책

## 성과 분리

- PRIMARY: `MAIN AT_LEAST_ONE_TRIO_EXACT_3_OF_3`
- SECONDARY: `INTEGRATED AT_LEAST_ONE_TRIO_EXACT_3_OF_3`
- SUPPORT: MAIN/INTEGRATED의 `EXACT_2_OF_3`, TRIO A/B별 별도 저장
- 3/3과 exact 2/3는 합산하지 않는다.
- MAIN과 INTEGRATED도 합산하지 않는다.

## Coverage

- eligible NO-PICK rounds
- fallback prediction rounds
- experimental no-pick rounds
- fallback coverage rate

Coverage 자체는 성공 증거가 아니다.

## Null

- 무작위 1~45 비중복 두 TRIO의 exact combinatorial baseline
- IID fair-draw simulation
- 동일 eligibility 회차를 고정한 selection-label/permutation empirical null
- PRNG·seed·반복 수는 결과 접근 전 protocol lock metadata에 고정한다.
- 최소 IID repetitions: `100,000`
- family-wise error: scope·window별 Holm 0.05

## 불확실성

- Wilson 95% interval
- 단측 exact binomial superiority와 inferiority를 분리
- 전체, 전반부, 후반부, 최근100, 최근50을 분리
- 최근20은 `TEST_ONLY`


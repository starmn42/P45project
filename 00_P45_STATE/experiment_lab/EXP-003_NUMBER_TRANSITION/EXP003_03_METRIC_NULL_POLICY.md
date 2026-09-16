# EXP-003 지표와 null 정책

- PRIMARY scope: MAIN 6개
- PRIMARY metric: 거리 d별 `risk difference = observed hit rate - 6/45`
- SECONDARY scope: INTEGRATED 7개, 기준 `7/45`
- effect size, Wilson 95%, raw one-sided upper/lower p와 adjusted p를 별도 저장한다.

## Null

1. 각 R에서 1~45 중 MAIN 6개를 비복원 균등추출하는 IID fair-draw null
2. 동일 R-1 feature matrix를 고정한 outcome permutation/randomization null
3. 거리 0..44 전체의 최대 절대 통계량을 이용한 global maxT

- PRNG seed: `202608160310`
- repetitions: `100,000`
- multiple testing: MAIN/INTEGRATED와 window를 분리하고, 각 family의 45개 거리 raw p에 Holm FWER 0.05 적용
- maxT adjusted p도 함께 요구한다.
- 결과가 없는 거리의 상태는 `NO_EXPOSURE`이며 다른 거리와 합치지 않는다.

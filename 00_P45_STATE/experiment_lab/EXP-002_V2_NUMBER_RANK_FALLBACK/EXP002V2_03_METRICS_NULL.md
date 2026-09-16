# EXP-002 V2 지표와 null

- PRIMARY: MAIN에서 A 또는 B 중 최소 한 TRIO exact 3/3
- SECONDARY: INTEGRATED에서 A 또는 B 중 최소 한 TRIO exact 3/3
- SUPPORT: MAIN/INTEGRATED exact 2/3를 A/B별 별도 저장
- 3/3, exact2/3, MAIN, INTEGRATED는 합산하지 않는다.
- exact combinatorial baseline과 고정 seed IID 100,000회 및 동일 eligibility selection-label permutation 100,000회를 사용한다.
- seed: `202608160238`
- Wilson 95%, 단측 exact binomial, 전체·전반부·후반부·최근100·최근50을 분리한다. 최근20은 TEST_ONLY다.

# EXP-002 V2 성공·실패 기준

SUPPORTED는 다음을 모두 만족해야 한다.

1. coverage > 0, prediction exposure >= 200, 전·후반 각각 >= 75
2. MAIN primary rate > exact random baseline
3. MAIN 단측 exact binomial p < 0.05, Wilson lower > baseline
4. 고정 eligibility permutation p < 0.05
5. 전반부와 후반부 모두 효과 방향이 양수
6. 최근100 방향이 양수이고 최근50에 confirmed 반대방향이 없음
7. 미래누출, protocol/hash/official-isolation 위반 0
8. 동일 입력 prediction/result hash 10회 결정론 일치

coverage만 증가하고 MAIN이 random 수준이면 FAILED/B다. 회고 우위가 후반부·최근 구간에서 재현되지 않으면 FAILED/C다. 표본이 부족하면 INCONCLUSIVE/D다. exact2/3 또는 INTEGRATED는 MAIN 실패를 구제하지 않는다.

# EXP-003 성공·실패 기준

최소 평가회차 500, 전·후반 각각 200을 요구한다.

SUPPORTED는 최소 하나의 MAIN 거리 신호가 다음을 모두 만족해야 한다.

1. Holm-adjusted p < 0.05
2. global maxT adjusted p < 0.05
3. Wilson 95% 구간이 fair baseline 6/45를 우위 방향으로 벗어남
4. 전반부·후반부 effect 방향 동일
5. 워크포워드 순차검증에서 동일 방향
6. 최근100 동일 방향, 최근50 confirmed 반대방향 없음
7. future leakage, protocol/hash/official-isolation 위반 0
8. 독립 재현 전에는 최대 `SUPPORTED`이며 공식 승격은 별도 승인 필요

다중검정 후 신호가 없으면 FAILED, 방향이 불안정하거나 최소표본이 부족하면 INCONCLUSIVE다. INTEGRATED 결과는 MAIN 실패를 구제하지 않는다.

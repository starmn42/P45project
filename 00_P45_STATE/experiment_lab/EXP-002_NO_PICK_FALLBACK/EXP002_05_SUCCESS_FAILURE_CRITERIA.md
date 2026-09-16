# EXP-002 성공·실패 기준

## 최소 표본

- fallback prediction exposure `200` 이상
- 전반부·후반부 각각 `75` 이상
- 미달은 `INCONCLUSIVE`이며 기준을 완화하지 않는다.

## SUPPORTED

다음을 모두 만족해야 한다.

1. fallback coverage가 0보다 큼
2. MAIN 최소 한 TRIO 3/3 rate가 무작위 baseline보다 높음
3. MAIN 단측 exact test Holm-adjusted p < 0.05
4. MAIN Wilson 95% lower bound가 baseline보다 큼
5. IID maxT 또는 고정 eligibility empirical null p < 0.05
6. 전반부와 후반부 효과 방향 동일
7. 최근100 방향 동일, 최근50에 유의한 반대방향 없음
8. round-order permutation temporal support p < 0.05
9. future leakage·protocol violation·official isolation violation 0
10. 독립 재현 run의 결과·hash 일치

INTEGRATED와 exact2/3는 SUPPORT이며 MAIN 실패를 구제하지 않는다.

## FAILED

- 충분한 표본에서 MAIN primary가 무작위와 같거나 열등
- 회고 신호가 워크포워드에서 재현되지 않음
- coverage만 늘고 PRIMARY 우위 없음
- null 또는 반대가설이 결과를 충분히 설명

## 무효 run

미래누출, 결과 선조회, protocol 변경, official DB write, hash 불일치는 FAILED가 아니라 `PROTOCOL_VIOLATION` 또는 `SYSTEM_ERROR`다.


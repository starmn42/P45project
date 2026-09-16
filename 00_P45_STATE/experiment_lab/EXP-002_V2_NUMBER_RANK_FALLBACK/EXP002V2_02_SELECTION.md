# EXP-002 V2 eligibility와 선택

- 공식 coverage audit의 `RESEARCH_NO_PICK`만 대상이다.
- NUMBER_FAIL, NUMBER_RETIRED, 불완전 5-UNIT vector, 반대위험 HIGH, 구조 SEVERE를 제외한다.
- NUMBER_PASS, NUMBER_WEAKEN, NUMBER_TEST, NUMBER_HOLD는 상태를 바꾸지 않고 허용한다.
- 공식 NUMBER deterministic 14-key로 정렬하며 최대 pool은 12다.
- 후보가 6개 미만이면 `EXPERIMENTAL_NO_PICK`이다.
- 상위 1,2,3번은 TRIO A, 4,5,6번은 TRIO B다.
- 공식 TRIO calculator, TRIO 15-key, 신규 점수·가중치·숨은 tie-break를 사용하지 않는다.

# EXP-002 eligibility와 결정론적 선별

## Eligibility

다음 조건을 모두 만족해야 한다.

1. 공식 pipeline의 해당 회차 판정이 `RESEARCH_NO_PICK`
2. source boundary가 `R-1`
3. UNIT·NUMBER 원자료 계산 완료
4. 데이터·schema·system 오류 없음
5. warmup 종료 후 회차
6. 결과 접근 전 eligibility hash 생성 가능

## Fallback source pool

- 실제 존재하는 45개 NUMBER 장부만 읽는다.
- `NUMBER_FAIL`, `NUMBER_RETIRED`, UNIT vector 미완료, 반대위험 `HIGH`, 구조 `SEVERE`는 제외한다.
- `NUMBER_PASS`, `NUMBER_WEAKEN`, `NUMBER_TEST`, `NUMBER_HOLD`는 실험 후보가 될 수 있으나 상태는 바꾸지 않는다.
- 기존 공식 NUMBER 14-key tie-break를 그대로 사용한다.
- 점수·가중치·평균·다수결을 새로 만들지 않는다.
- 상위 최대 12개, 최소 6개가 있어야 다음 단계로 간다.

## TRIO A/B

1. source pool의 모든 3개 조합을 공식 TRIO 계산기로 평가한다.
2. 공식 TRIO 상태를 승격하거나 관문을 완화하지 않는다.
3. 기존 공식 TRIO 15-key 순서와 canonical stable key를 그대로 사용한다.
4. 첫 번째 TRIO를 A로 잠근다.
5. 이후 순서에서 A와 숫자가 겹치지 않는 첫 TRIO를 B로 잠근다.
6. B가 없으면 fallback을 생성하지 않는다.

결과를 본 뒤 A/B 위치, 후보 수, 제외 조건 또는 tie-break를 변경하면 새 Experiment ID가 필요하다.


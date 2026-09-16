# EXP-002 사전등록 워크포워드

각 회차 R에서 다음 순서를 강제한다.

1. `source_end_round=R-1` 잠금
2. 공식 pipeline의 출력 가용성과 `RESEARCH_NO_PICK` 여부 확정
3. fallback eligibility와 source pool 확정
4. 기존 NUMBER/TRIO 순서로 A/B 결정
5. canonical eligibility·selection payload와 prediction hash 저장
6. transaction staging과 hash 재검증
7. 그 후에만 R outcome 접근
8. MAIN/INTEGRATED 3/3과 exact2/3를 분리 저장
9. R 결과는 R+1부터 과거 자료로만 사용

동일 round 중복, outcome 선조회, source boundary 위반, prediction hash 누락은 run을 무효화한다. 중단·재개는 같은 run_id와 마지막 complete 다음 회차를 사용한다.


# EXP-002 V2 순차검증

각 R에서 source_end_round=R-1, eligibility, ordered NUMBER pool, TRIO A/B와 prediction hash를 먼저 전용 DB transaction으로 확정한다. 그 commit 이후에만 R 결과를 조회한다. R 결과는 이후 prediction feature에 사용되지 않는다. 동일 round 중복, 결과 선조회, 미래누출, hash 불일치는 run을 무효화한다.

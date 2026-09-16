# EXP-001 Walkforward 설계

## 기본 경계

평가 회차 R에서 사용할 수 있는 자료는 적격 회차 `1..R-1`뿐이다. R outcome loader는 prediction/network lock이 완료된 후에만 호출한다.

## 회차 처리 순서

1. evaluation_round R 설정
2. source_end_round=R-1 고정
3. 공식 draw source를 read-only snapshot으로 읽기
4. R-1까지 MAIN/INTEGRATED 990개 지표 계산
5. 사전 고정 Holm·기간재현 기준으로 candidate edge 선정
6. canonical prediction payload 생성
7. rule hash, data-prefix hash, 990-pair state hash, selected-edge hash 저장
8. outcome 접근 0 검증 및 atomic pre-result lock
9. 그 후에만 R 실제 결과 조회
10. selected pair의 MAIN/INTEGRATED occurrence를 분리 기록
11. commit 후 R 결과는 R+1부터 historical input에 포함

## 최초 평가

- R 이전 적격 회차가 500개 이상일 때만 평가 가능
- 하드코딩 회차가 아니라 적격 자료 수로 자동 결정
- 미달 회차는 `SKIPPED_INSUFFICIENT_TRAINING_SAMPLE`

## 사전 edge 선택 규칙

R 이전 MAIN 데이터에서 다음을 모두 만족하는 pair만 selection exposure를 만든다.

1. OVERALL MAIN Holm-adjusted p < 0.05
2. FIRST_HALF와 SECOND_HALF risk_difference 방향 동일
3. 두 half 각각 MAIN Holm-adjusted p < 0.05
4. RECENT_100 방향이 전체와 동일
5. RECENT_50에서 반대방향 Holm-adjusted p < 0.05가 아님
6. RECENT_20은 저장만 하고 선택에 사용하지 않음

조건을 만족하는 pair가 없으면 정상적으로 `NO_EDGE_SELECTED`를 기록한다. 기준을 완화하지 않는다.

## Walkforward 평가

- pair identity별 selection exposure와 occurrence outcome을 저장
- MAIN occurrence가 PRIMARY, INTEGRATED occurrence가 SUPPORT
- pair별 selection exposure 200 이상에서만 확정 검정 가능
- 선택된 회차의 baseline은 MAIN 1/66, INTEGRATED 7/330
- MAIN은 방향별 사전 가설에 맞춘 one-sided exact binomial 검정을 사용하되, 평가된 pair family에 Holm 0.05 적용
- 음의 관계는 비출현 성공률로 바꾸지 않고 occurrence rate가 baseline보다 낮은지를 직접 검정

## 결정론·재개

- run_id, protocol hash, code hash, data-prefix hash, schema version이 모두 같을 때만 resume
- round 단위 atomic transaction
- COMPLETE round 재계산 금지
- round/pair exposure unique constraint
- resume 결과는 연속 실행 결과와 동일해야 함
- 부분 결과로 SUPPORTED 또는 PROMOTION_CANDIDATE 확정 금지

## 누출·오류 처리

future leakage, outcome 선조회, hash mismatch, duplicate exposure, source write가 발생하면 FAIL-FAST하고 해당 run을 공식 실험결과로 사용하지 않는다.


# P45 PAIR 계산 운영 안전정책

연구 결과를 바꾸지 않는 실행 안전정책이다. 후보 수를 임의로 제한하지 않는다.

## 확인된 안전장치

- 전용 SQLite backtest DB에 run, round, candidate, identity exposure, selection exposure, prediction, outcome과 checkpoint를 저장한다.
- 동일 round, identity exposure, selection exposure의 중복을 UNIQUE 제약으로 차단한다.
- 한 회차를 하나의 원자적 transaction으로 처리하고 실패 시 rollback한다.
- COMPLETE·정당한 SKIPPED·FAILED 합계가 전체 대상 회차와 같을 때만 전체 COMPLETE가 가능하다.
- 완료 회차는 resume에서 재계산하지 않는다.
- rule/code/schema/signature/source hash가 다르면 같은 run을 재사용하지 않는다.
- R의 historical 조회는 `evaluation_round < R`로 제한한다.
- prediction/context를 저장한 뒤 outcome을 읽는다.
- 디스크 저장, checkpoint, resume, crash recovery는 구현되어 있다.

## 제한과 운영 판정

- 현재 구현은 회차 단위 checkpoint와 SQLite disk spill을 사용한다.
- 한 회차 내부의 모든 PAIR 후보는 메모리에서 구성되며 명시적인 candidate streaming 또는 고정 크기 batch 처리 계층은 확인되지 않았다.
- 현재 공식 후보 규모에서 완료 검증은 있었지만, 후보 공간이 크게 증가할 경우 메모리 상한과 회차 내 중간복구는 별도 검토가 필요하다.
- 이 제한 때문에 후보를 자르거나 일부만 계산해서는 안 된다.
- 전체 필요 계산이 끝나지 않으면 `INCOMPLETE`이며 `COMPLETE`가 아니다.

판정: checkpoint/resume/SQLite/rollback은 `ALREADY_EXISTS`, 회차 내부 streaming/batch는 `PARTIAL`. 향후 안전 보완은 계산 순서와 결과가 완전히 동일함을 입증하는 운영 변경으로만 제안하며, 연구 규칙 변경은 허용하지 않는다.


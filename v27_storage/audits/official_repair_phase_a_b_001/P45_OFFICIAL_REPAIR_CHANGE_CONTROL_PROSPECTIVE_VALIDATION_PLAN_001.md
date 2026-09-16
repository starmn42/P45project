# P45 OFFICIAL REPAIR CHANGE CONTROL / PROSPECTIVE VALIDATION PLAN 001

## Document lock

- Plan: `OFFICIAL REPAIR CHANGE CONTROL / PROSPECTIVE VALIDATION PLAN 001`
- Status: `LOCKED_BEFORE_OFFICIAL_REPAIR`
- Official Engine: `FROZEN`
- Official Repair Applied: `NO`
- Historical Outcome Scoring Allowed: `NO`
- User Approval Required Before Official Repair: `YES`

## Problem definition

기존 0/867 end-to-end coverage evidence는 PAIR historical lifecycle 구현 누락으로 오염됐다.

이 발견은 gate를 낮추라는 증거가 아니며, repaired shadow 100/867을 공식 성과로 바꾸는 근거가 아니다. 과거 결과에 맞춰 semantics를 바꾸는 근거도 아니다.

## Permitted repair purpose

`PAIR historical lifecycle의 누락된 구현을 기존 공식 semantics를 변경하지 않고 복원하는 것`

## Forbidden repair changes

- gate 완화
- threshold 변경
- signature 변경
- ranking logic 변경
- hidden score 또는 weighting 추가
- candidate rescue rule 추가
- historical outcomes에 맞춘 branching
- output 강제 생성
- NUMBER/TRIO/PAIR/CORE 의미 변경

## Change-control stages

### Phase A — RELEASE CANDIDATE BUILD

공식 baseline을 읽기 전용으로 보존한 채 별도 격리 RC에서 lifecycle repair를 재현한다. Phase A는 구조적·재현성 검증만 수행하며 historical outcome scoring은 하지 않는다.

### Phase B — PRE-DRAW CANARY

Phase A PASS RC를 이용해 아직 outcome이 존재하지 않는 미래 target에 대해 pre-draw artifact를 outcome 전에 고정한다. Canary는 출력 유무와 관계없이 그대로 보존하며 결과에 맞춘 재실행·수정을 금지한다.

### Phase C — USER REVIEW / APPROVAL GATE

이번 Work에서는 실행하지 않는다. Phase A+B evidence를 ChatGPT가 판독한 뒤 사용자가 명시 승인해야만 다음 official repair 작업을 설계할 수 있다.

### Phase D — OFFICIAL REPAIR

이번 Work 범위 밖이며 자동 실행을 금지한다.

## PASS interpretation

Phase A+B PASS는 `REPAIR_CANDIDATE_READY_FOR_USER_REVIEW`만 의미한다.

다음을 의미하지 않는다.

- 공식 repair 승인
- 공식 성과 확인
- prediction signal 확인
- historical coverage 성과
- gate 변경 승인

## Immutable execution rules

- 모든 historical target R은 `MAX_SOURCE_ROUND_USED <= R-1`을 만족한다.
- target MAIN/BONUS/outcome은 candidate/state construction에 사용하지 않는다.
- 3/3 PRIMARY와 exact 2/3 SUPPORT 성과 scoring을 실행하지 않는다.
- Phase A 핵심 pipeline은 동일 clean input으로 최소 2회 독립 재현한다.
- Phase B target은 local canonical/live source의 최신 확정 회차 L에 대해 `L+1`이며, target outcome 부재를 먼저 확인한다.
- Canary artifact는 pre-outcome 상태에서 hash 봉인하고 official DB에 기록하지 않는다.
- 결과를 보고 logic, threshold, gate, signature, ranking을 변경하지 않는다.
- STATE, Decision, Registry는 이 작업에서 변경하지 않는다.
- official engine은 계속 `FROZEN`이다.

## Final gate

`AWAITING_CHATGPT_REVIEW_AND_EXPLICIT_USER_APPROVAL`

`OFFICIAL REPAIR NOT APPLIED`

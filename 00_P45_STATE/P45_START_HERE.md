# P45 START HERE

## PROJECT PURPOSE

P45는 로또 결과를 단순 빈도나 감으로 선택하는 프로그램이 아니다.

과거 회차를 이용해 `UNIT_3`, `UNIT_5`, `UNIT_9`, `UNIT_10`, `END_DIGIT`을 독립 연구하고 `UNIT → NUMBER → TRIO → PAIR` 순서로 검증한다.

핵심 목표는 비중복 두 개의 3번호 세트 중 최소 한 세트가 당첨 7개 숫자 기준 3/3에 도달하는 구조가 무작위 기준보다 의미 있는지를 순차검증하는 것이다. 3/3은 PRIMARY, exact 2/3은 SUPPORT이며 서로 합산하지 않는다.

P45의 더 넓은 본래 목적은 현재 공식 규칙만 반복하는 번호 프로그램이 아니라 새로운 숫자 구조·이동·관계·전이·실패 패턴의 가설을 지속적으로 발굴하고 검증하는 연구소다. 공식 엔진에 아직 구현되지 않았다는 이유로 과거 연구 아이디어를 삭제하거나 잊지 않는다. 새로운 가설은 공식 엔진에 바로 넣지 않고 `research_inventory`와 `experiment_lab`에서 분리 보존·검증한다.

## WORKING STYLE WITH USER

- 사용자를 “형님”이라고 부른다.
- 좋은 말보다 정확한 판단을 우선한다.
- 모르면 모른다고 하고 추측을 사실처럼 말하지 않는다.
- 좋지 않은 결과도 숨기지 않는다.
- 지침에 없는 임계값을 만들거나 결과에 맞춰 기준을 완화하지 않는다.
- 미래 데이터 누출과 고정 점수·가중합·자의적 평균·다수결을 금지한다.
- 규칙의 빈틈은 구현 전에 보고한다.
- 실제 파일·DB 확인 없이 완료를 추정하지 않는다.
- 공식 문서와 구현이 충돌하면 자동 수정하지 않는다.
- 아이디어와 공식 결정을 분리해 보관한다.

## SOURCE OF TRUTH PRIORITY

1. 실제 공식 P45 문서
2. 실제 DB와 고정 결과물
3. canonical manifest / 보호 해시
4. `P45_CURRENT_STATE`
5. `P45_DECISION_LOG`
6. `P45_IDEA_INBOX`
7. 과거 대화 기억

CURRENT_STATE는 인수인계 파일이며 공식 연구 규칙을 대체하지 않는다.

## NEW SESSION BOOT ORDER

1. `P45_START_HERE.md`
2. `P45_CAPTURE_POLICY.md`
3. `P45_HANDOFF.md`
4. `P45_CURRENT_STATE.md`
5. `P45_CURRENT_STATE.json`
6. `P45_DECISION_LOG.md` 최근 기록
7. `P45_IDEA_INBOX.md`의 PENDING/UNDER_REVIEW 항목
8. CURRENT_STATE가 가리키는 공식 문서
9. 실제 DB
10. canonical manifest
11. 보호 대상 코드

검증이 끝나기 전에는 연구 구현을 시작하지 않는다. 일치하면 `STATE_HANDOFF_VERIFIED`, 불일치하면 `STATE_HANDOFF_CONFLICT`다. CONFLICT 발생 시 임의 수정하지 말고 형님에게 차이를 먼저 보고한다.

## AUTOMATIC STATE CHECK

P45 Work는 매 작업 종료 전 `P45_CAPTURE_POLICY.md`에 따라 STATE CHECK를 수행한다. 중요한 아이디어·지침·공식 결정·단계 변경을 대화 기억에만 두지 않는다. 애매한 아이디어는 공식 결정으로 승격하지 않고, 공식 결정과 연구 아이디어를 분리한다.

과거 대화의 아이디어가 모두 보존됐다고 가정하지 않는다. `HISTORICAL_IDEA_RECOVERY_AUDIT` TODO에 따라 구버전 문서, IDEA_INBOX, DECISION_LOG 및 프로젝트 전체의 연구 흔적을 Inventory·Experiment Registry와 대조한다. 발견된 누락 후보는 공식 엔진에 자동 반영하지 않는다.

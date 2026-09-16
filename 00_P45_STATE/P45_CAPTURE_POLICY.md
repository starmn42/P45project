# P45 CAPTURE POLICY

## PURPOSE

P45 Work/AI가 현재 처리 중인 대화와 작업에서 중요한 아이디어·지침·결정·상태변경을 분류하고, Stage 2 상태관리기를 통해 안전하게 보존하기 위한 운영 정책이다. 연구 계산 규칙 문서가 아니다.

## RESPONSIBILITY BOUNDARY

- Work/AI: 대화 의미를 이 정책에 따라 분류하고 구조화 이벤트를 만든다.
- state manager: 이벤트 형식·허용 전이·중복을 검증하고 transaction·rollback·snapshot·handoff 검증을 수행한다.
- Python 로컬 코드는 한국어 자유대화의 의미를 완벽하게 판단한다고 주장하지 않는다.
- 이 시스템은 Windows 전체나 다른 ChatGPT 대화를 감시하지 않는다. 현재 P45 Work가 실제로 처리하는 컨텍스트만 STATE CHECK한다.

## CLASSIFICATION

### CONVERSATION_ONLY

단순 질문·설명·확인. 저장하지 않고 `STATE_NO_CHANGE`로 끝낸다.

예: “왜 43회부터야?”, “지금 몇 %야?”, “이 결과가 무슨 뜻이야?”

### IDEA_PENDING

아직 승인되지 않은 연구 제안. IDEA_INBOX에 `PENDING`, `official_effect: NONE`으로 append한다. 공식 상태와 연구 규칙은 바꾸지 않는다.

예: “끝수하고 3단위를 같이 보는 것도 시험해볼까?”

### DECISION_CONFIRMED

형님이 지속 적용을 명확히 승인한 운영 결정·단계 승인·금지·상태변경. DECISION_LOG에 append하고 명시된 허용 상태만 갱신한다.

예: “앞으로 매 작업 종료 전 STATE CHECK를 하자.”, “PAIR 감사 전에는 PAIR를 만들지 마.”

### AMBIGUOUS_IMPORTANT

중요하지만 공식 승인인지 불분명한 발언. 공식 decision으로 승격하지 않는다. 필요하면 IDEA_INBOX에 `PENDING`, `official_effect: NONE`, `capture_classification: AMBIGUOUS_IMPORTANT`로 기록한다.

예: “이 방식으로 가는 게 낫지 않을까?”

## RESEARCH RULE FIREWALL

IDEA_PENDING과 AMBIGUOUS_IMPORTANT를 AI 판단만으로 공식 연구 규칙에 반영하지 않는다. 계산식·임계값·NUMBER/TRIO/PAIR gate·상태표·무작위 기준·통계검정·미래자료 차단 규칙의 변경은 다음 순서를 지킨다.

1. 신규 공식 amendment/version 작성
2. 검토
3. 형님 승인
4. 공식 문서 확정
5. CURRENT_STATE가 신규 문서를 가리킴

명확한 변경 승인 발언은 DECISION_LOG에 남길 수 있지만 공식 문서를 직접 수정하거나 CURRENT_STATE만 바꿔 적용하지 않는다.

## IDEA STORAGE AND LIFECYCLE

- 동일 canonical idea는 `idea_hash`로 중복 차단한다.
- 수정된 내용은 새 IDEA로 append하고 `supersedes_idea_id`로 연결할 수 있다.
- 기존 IDEA 기록은 수정·삭제하지 않는다.
- 승인·폐기·대체는 새 DECISION_CONFIRMED 이벤트로 연결한다.
- 상태: PENDING, UNDER_REVIEW, APPROVED, REJECTED, SUPERSEDED.
- PENDING 아이디어의 official_effect는 항상 NONE이다.

## P45 STATE CHECK

모든 P45 Work 종료 전에 다음을 확인한다.

1. 새 아이디어 또는 기존 아이디어 수정 여부
2. 공식 결정·지속 지침 변경 여부
3. 단계·status·next_action 변경 여부
4. blocker·forbidden action 변경 여부
5. 버전·schema·active DB·run_id·보호 기준 변경 여부

처리 순서:

1. 사용자 요청 수행
2. 실제 결과 검증
3. P45 STATE CHECK
4. 중요 이벤트 분류
5. 구조화 이벤트 생성
6. dry-run
7. 검증
8. commit
9. HANDOFF·snapshot 확인
10. `verify` 실행
11. 작업 완료 보고

결과 상태: `STATE_NO_CHANGE`, `IDEA_CAPTURED`, `STATE_UPDATE_REQUIRED`, `STATE_UPDATE_OK`, `STATE_UPDATE_FAILED`, `STATE_HANDOFF_CONFLICT`.

STATE_UPDATE_FAILED 또는 STATE_HANDOFF_CONFLICT면 모두 정상 완료라고 보고하지 않는다.

## STRUCTURED EVENT RULES

허용 event_type:

- CONVERSATION_ONLY
- IDEA_PENDING
- AMBIGUOUS_IMPORTANT
- DECISION_CONFIRMED

알 수 없는 event_type은 commit하지 않는다. IDEA 계열은 `official_effect: NONE`이어야 하며 `affected_state`, `promote_to_official`, 공식 문서 변경을 포함할 수 없다. DECISION_CONFIRMED는 `approval_explicit: true`가 필요하다.

## NEW SESSION ORDER

1. P45_START_HERE.md
2. P45_CAPTURE_POLICY.md
3. P45_HANDOFF.md
4. P45_CURRENT_STATE.md
5. P45_CURRENT_STATE.json
6. 최근 DECISION_LOG
7. PENDING/UNDER_REVIEW IDEA_INBOX
8. 공식 문서
9. 실제 DB
10. canonical manifest
11. 보호 hash

`STATE_HANDOFF_VERIFIED` 후에만 작업한다.

## AUTOMATIC MEMORY PRINCIPLE

형님과 P45를 연구하는 동안 중요한 아이디어·지침·공식 결정·단계 변경을 대화 기억에만 의존하지 않는다. 매 작업 종료 전 STATE CHECK를 수행하고 필요한 내용을 `00_P45_STATE`에 보존한다. 애매한 아이디어는 공식 결정으로 승격하지 않으며 공식 결정과 연구 아이디어를 분리한다.

## IMPORTANT RESEARCH MEMORY BOUNDARY

다음 내용은 `CONVERSATION_ONLY`로 끝내지 않는다.

- 새로운 연구 아이디어
- 연구 목적의 변경 또는 확장
- 중요한 지속 운영 원칙
- 공식 연구와 실험 연구의 경계 결정
- 향후 수행해야 할 연구
- 중요한 실패 원인
- 기존 연구 누락 발견
- 사용자가 명시적으로 보존을 요청한 내용

저장 위치는 성격에 따라 분리한다.

|내용|저장 위치|
|---|---|
|새 아이디어|`P45_IDEA_INBOX.md`; 필요 시 Experiment Registry|
|승인된 중요 결정|`P45_DECISION_LOG.md`|
|현재 운영 상태|`P45_CURRENT_STATE.md/json`|
|연구목록 변경·누락 후보|`research_inventory`|
|실험 후보·실험 상태|`experiment_lab` Registry|

단순 질문, 설명, UI 잡담처럼 연구 목적·규칙·아이디어·결정·미완료 작업에 영향을 주지 않는 내용은 저장하지 않는다.

공식 엔진에 구현되지 않은 연구 아이디어도 보존 대상이다. 단, 보존은 공식 승격이 아니며 IDEA/EXPERIMENT에서 공식 규칙으로 자동 이동할 수 없다.

## HISTORICAL IDEA RECOVERY

과거 대화의 모든 아이디어가 이미 보존됐다고 가정하지 않는다. 향후 `HISTORICAL_IDEA_RECOVERY_AUDIT`를 수행해 프로젝트 전체, 구버전 문서, IDEA_INBOX, DECISION_LOG의 연구 흔적을 현재 Research Inventory와 Experiment Registry에 대조한다.

누락이 발견되면 먼저 `누락 후보`로 기록한다. 형님의 별도 승인과 공식 절차 없이는 공식 엔진에 추가하지 않는다.

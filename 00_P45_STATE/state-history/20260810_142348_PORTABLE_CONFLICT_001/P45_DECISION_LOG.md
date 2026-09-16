# P45 DECISION LOG

APPEND ONLY. 아래 기록은 2026-08-10 bootstrap 시점에 확인 가능한 역사적 결정과 현재 결정을 정리한 것이다. 역사적 결정의 원래 시각은 `UNKNOWN_HISTORICAL`이다. `decision_hash`는 각 decision 문장의 UTF-8 SHA-256이다.

## DECISION-20260810-001
- timestamp: UNKNOWN_HISTORICAL (bootstrap: 2026-08-10T13:06:20+09:00)
- project_version: P45 v2.7.1+
- stage: UNIT
- category: RESEARCH_STRUCTURE
- decision: 다섯 UNIT을 서로 독립적인 필수 연구로 채택한다.
- reason: 단위별 구조를 합산점수 없이 검증하기 위해서다.
- evidence: 공식 지침 및 Stage 4 구현 기록
- affected_files: 공식 지침 참조
- affected_schema: unit tables
- previous_rule: UNKNOWN_HISTORICAL
- new_rule: FIVE_INDEPENDENT_REQUIRED_UNITS
- allowed_next_action: 독립 UNIT 연구
- forbidden_actions: 단위 점수·가중합
- approval_source: 형님 승인
- decision_hash: `71485efe4daccb0a60e08adcd39be64e1ee80a40308f63d2d4b72d265ec6bb67`

## DECISION-20260810-002
- timestamp: UNKNOWN_HISTORICAL (bootstrap: 2026-08-10T13:06:20+09:00)
- project_version: P45 v2.7.1+
- stage: PERFORMANCE
- category: PRIMARY_SUPPORT
- decision: 3/3을 PRIMARY, exact 2/3을 SUPPORT로 사용하며 합산하지 않는다.
- reason: 주성과와 보조성과를 분리하기 위해서다.
- evidence: 공식 지침
- affected_files: 공식 지침 참조
- affected_schema: separate exact-hit metrics
- previous_rule: UNKNOWN_HISTORICAL
- new_rule: PRIMARY_3_OF_3_SUPPORT_EXACT_2_OF_3
- allowed_next_action: 분리 집계
- forbidden_actions: 3/3·2/3 합산
- approval_source: 형님 승인
- decision_hash: `22dbf408da5077d2a3ad6086b7203a022f4ee97c2cc77fe2ffe2ca343f405d88`

## DECISION-20260810-003
- timestamp: UNKNOWN_HISTORICAL (bootstrap: 2026-08-10T13:06:20+09:00)
- project_version: P45 v2.7.2
- stage: 6
- category: NUMBER_GATE
- decision: NUMBER v2.7.2 결정표를 공식 번호 관문으로 채택한다.
- reason: 번호 상태와 후보군 규칙을 결정론적으로 확정하기 위해서다.
- evidence: Number Gate Amendment SHA-256 `6c268c09...f25cd`
- affected_files: P45_v2.7.2_Number_Gate_Amendment_UTF8_BOM_CRLF.md
- affected_schema: schema 272+
- previous_rule: v2.7.1 partial NUMBER rules
- new_rule: NUMBER_GATE_V272
- allowed_next_action: Stage 6 진단
- forbidden_actions: 점수·기준 완화
- approval_source: 형님 승인
- decision_hash: `49489d79f96a8ee956e4186d52e7e07ad0a3b7fcad40ee7a10d1b750f2de855f`

## DECISION-20260810-004
- timestamp: UNKNOWN_HISTORICAL (bootstrap: 2026-08-10T13:06:20+09:00)
- project_version: P45 v2.7.3
- stage: 7
- category: TRIO_GATE
- decision: TRIO v2.7.3 결정표를 공식 TRIO 관문으로 채택한다.
- reason: TRIO 상태·통계·위험·구조 규칙을 확정하기 위해서다.
- evidence: TRIO Gate Amendment SHA-256 `2ed0257c...bdecd9`
- affected_files: P45_v2.7.3_TRIO_Gate_Amendment_UTF8_BOM_CRLF.md
- affected_schema: schema 273
- previous_rule: v2.7.1 TRIO partial rules
- new_rule: TRIO_GATE_V273
- allowed_next_action: Stage 7 검증
- forbidden_actions: 관문 완화
- approval_source: 형님 승인
- decision_hash: `b82aa7e5b8e7d3ef54292c67d0100bac5f2c7e85259cab6af29df920efd27f59`

## DECISION-20260810-005
- timestamp: UNKNOWN_HISTORICAL (bootstrap: 2026-08-10T13:06:20+09:00)
- project_version: P45 v2.7.3
- stage: 7.1
- category: ELIGIBILITY
- decision: 외부 순차검증 최초 적격 평가 회차는 실제 관문을 통과한 43회다.
- reason: 2회는 이력 부족, 3~42회는 후보 0이기 때문이다.
- evidence: Stage 7.2 경계 재검증
- affected_files: walkforward DB 참조
- affected_schema: none
- previous_rule: 미확정
- new_rule: FIRST_ELIGIBLE_ROUND_43
- allowed_next_action: 43회 이후 평가
- forbidden_actions: 43회 하드코딩 주장
- approval_source: 형님 승인 및 실측
- decision_hash: `a26f84349c23030b9c4f744ca2fc1b8b15d64a1361d9e043eeba0a2d3585e4b9`

## DECISION-20260810-006
- timestamp: 2026-08-10 bootstrap 확인
- project_version: P45 v2.7.3
- stage: 7.1
- category: WALKFORWARD
- decision: 43~1235회 외부 순차검증을 WALKFORWARD_COMPLETE로 확정한다.
- reason: 1193회가 COMPLETE 1088, 정당한 SKIPPED 105, FAILED 0으로 닫혔다.
- evidence: run_id `b7a92876-4a55-4472-a738-f1edb74796ec`
- affected_files: p45_v273_trio_walkforward.sqlite3
- affected_schema: walkforward schema 1
- previous_rule: WALKFORWARD_INCOMPLETE
- new_rule: WALKFORWARD_COMPLETE
- allowed_next_action: Stage 7.2 집계
- forbidden_actions: 원본 DB 수정
- approval_source: 형님 승인
- decision_hash: `ec6091d002b5bece954bad5e20586c3da6203349129e0d23cd7d57f95aab0043`

## DECISION-20260810-007
- timestamp: 2026-08-10T13:06:20+09:00 bootstrap
- project_version: P45 v2.7.3
- stage: 7.2
- category: FINAL_AGGREGATION
- decision: Stage 7.2 TRIO 최종 집계와 무결성 검증을 완료한다.
- reason: 10회 결정론, 원본 불변, 집계 교차검증을 통과했다.
- evidence: p45_v273_trio_final.sqlite3 SHA-256 `1b7b86d8...5e9f59`
- affected_files: 별도 TRIO final DB
- affected_schema: final aggregation schema
- previous_rule: WALKFORWARD raw only
- new_rule: STAGE_7_2_COMPLETE
- allowed_next_action: PAIR 규칙 완결성 감사
- forbidden_actions: 자동 PAIR 생성
- approval_source: 형님 확인
- decision_hash: `0439e4d62c52931f4a460be0e279a3de1c95adb6be518e7d63bc8566d44e2bef`

## DECISION-20260810-008
- timestamp: 2026-08-10 bootstrap 확인
- project_version: P45 v2.7.3
- stage: 7.2
- category: TRIO_RESULT
- decision: 현재 TRIO_PASS는 0개이며 기준을 완화하지 않는다.
- reason: 현재 NUMBER_PASS가 1개라 PASS 관문 1을 충족할 수 없다.
- evidence: 현재 220개 TRIO 최종 상태
- affected_files: TRIO final DB 참조
- affected_schema: none
- previous_rule: 미확정
- new_rule: TRIO_PASS_0_AS_OBSERVED
- allowed_next_action: 결과 그대로 보고
- forbidden_actions: PASS 승격·관문 완화
- approval_source: 형님 승인 원칙
- decision_hash: `ec7c5c132db61cf1ff87f8b3a37d2f24a405d9ee7800807027faa98c8833a1ec`

## DECISION-20260810-009
- timestamp: 2026-08-10 bootstrap 확인
- project_version: P45 v2.7.3
- stage: 7.2
- category: PAIR_INPUT
- decision: 현재 valid_for_pair TRUE TRIO는 12개다.
- reason: 공식 유효 TRIO_TEST 조건을 통과했다.
- evidence: current_trio_final 220행
- affected_files: TRIO final DB 참조
- affected_schema: none
- previous_rule: 미확정
- new_rule: VALID_FOR_PAIR_12
- allowed_next_action: PAIR 규칙 감사의 입력 확인
- forbidden_actions: 최종 추천으로 표현
- approval_source: 형님 확인
- decision_hash: `65bbab395c3653aa28e6292a2c18ff8e6b575de6d8e9a0816232e755ebbfec60`

## DECISION-20260810-010
- timestamp: 2026-08-10T13:06:20+09:00
- project_version: P45 v2.7.3
- stage: PRE-PAIR
- category: APPROVAL
- decision: PAIR 구현과 생성은 아직 승인하지 않는다.
- reason: 공식 PAIR 규칙 완결성 감사가 먼저 필요하다.
- evidence: 형님 현재 요청
- affected_files: none
- affected_schema: none
- previous_rule: PAIR_NOT_STARTED
- new_rule: PAIR_NOT_APPROVED
- allowed_next_action: PAIR_RULE_COMPLETENESS_AUDIT
- forbidden_actions: PAIR·최종 6개·세트 생성
- approval_source: 형님 명시
- decision_hash: `da84e8b55c657a03b7251790481d72bf0c7fe3b72240fb9e61214a4bd3b90a1f`

## DECISION-20260810-011
- timestamp: 2026-08-10T13:06:20+09:00
- project_version: P45 v2.7.3
- stage: STATE_BASE_1
- category: CONTINUITY
- decision: P45 장기 상태·인수인계 시스템을 도입한다.
- reason: 새 대화·세션에서도 공식 상태와 금지사항을 검증 복구하기 위해서다.
- evidence: 형님 현재 승인 요청
- affected_files: 00_P45_STATE의 6개 기반 파일
- affected_schema: none
- previous_rule: 대화 중심 인수인계
- new_rule: FILE_BASED_STATE_HANDOFF
- allowed_next_action: 기반 파일 검증
- forbidden_actions: 자동 관리자·PAIR 자동 시작
- approval_source: 형님 명시
- decision_hash: `daed3258467e3e9fdbb9231ab43d56bf1d2bad30e315bf40ec6f75751eed1c29`

## DECISION-20260810-012
- timestamp: 2026-08-10T13:22:38+09:00
- project_version: P45 v2.7.3
- stage: STATE_SYSTEM_STAGE_2
- category: STATE_ENGINE
- decision: P45 state manager v1.0 safe storage engine adopted
- reason: Enable deterministic state, transactional updates, rollback, snapshots, locks, and handoff verification
- evidence: User-approved P45 State System Stage 2 request and 30-test specification
- affected_files: 00_P45_STATE managed state files and tools only
- affected_schema: none
- previous_rule: manual state files
- new_rule: STATE_MANAGER_V1_0
- allowed_next_action: PAIR_RULE_COMPLETENESS_AUDIT after state engine verification
- forbidden_actions: Stage 3 automation; PAIR generation; research rule changes
- approval_source: explicit user approval
- decision_hash: 5607d0dab27933f5e572a6b4462f0aae11eb33c383892035facfff5ecef16fcf

## DECISION-20260810-013
- timestamp: 2026-08-10T13:45:00+09:00
- project_version: P45 v2.7.3
- stage: STATE_SYSTEM_STAGE_3
- category: CAPTURE_POLICY
- decision: P45 Work는 앞으로 매 작업 종료 전 STATE CHECK를 수행하고 중요 아이디어·지침·상태변경을 00_P45_STATE에 자동 보존한다.
- reason: 대화 기억에 의존하지 않고 새 세션에서도 연구 상태와 운영 결정을 복구하기 위해서다.
- evidence: 형님의 P45 State System Stage 3 명시적 승인
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 Work는 앞으로 매 작업 종료 전 STATE CHECK를 수행하고 중요 아이디어·지침·상태변경을 00_P45_STATE에 자동 보존한다.
- allowed_next_action: PAIR_RULE_COMPLETENESS_AUDIT only after STATE CHECK and handoff verification
- forbidden_actions: ['IDEA_AUTO_PROMOTION', 'AMBIGUOUS_AUTO_DECISION', 'STAGE_4_AUTO_START', 'PAIR_GENERATION']
- approval_source: USER
- decision_hash: d7e6ccac32f93dc2ba4ad70409448ddc9dbc899ab79af12808af18265ac38f7a

## DECISION-20260810-014
- timestamp: 2026-08-10T14:10:00+09:00
- project_version: P45 v2.7.3
- stage: STATE_SYSTEM_STAGE_4
- category: HANDOFF_SYSTEM
- decision: P45 새 세션 Cold Start 및 Portable Handoff 시스템 검증을 완료한다.
- reason: 파일 전용 복구, 로컬 원본 검증, portable-only 구분, 결정론적 bundle 및 충돌 검사가 통과했다.
- evidence: explicit user statement
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 새 세션 Cold Start 및 Portable Handoff 시스템 검증을 완료한다.
- allowed_next_action: PAIR_RULE_COMPLETENESS_AUDIT after explicit approval
- forbidden_actions: ['PAIR_GENERATION', 'FINAL_SIX', 'OFFICIAL_LOCK', 'UNVERIFIED_RESEARCH_CHANGE']
- approval_source: USER
- decision_hash: f5382e29a6b1401cccf325ac2bb41aa4827c51341732d494aebda09c59ba04e9

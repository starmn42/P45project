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

## DECISION-20260810-015
- timestamp: 2026-08-10T14:26:49+09:00
- project_version: P45 v2.7.3
- stage: STATE_SYSTEM_PATCH_4_1
- category: BUG_FIX
- decision: 실제 Portable Handoff 시험에서 decision/state/bundle timestamp chronology conflict를 발견했고, 공통 timezone-aware clock과 시간순서 검증 규칙을 적용한다.
- reason: DECISION-014의 수동 미래 시각과 독립적으로 생성된 state/snapshot/bundle 시각 때문에 STATE_HANDOFF_CONFLICT가 발생했다.
- evidence: state-history/20260810_142348_PORTABLE_CONFLICT_001
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: 실제 Portable Handoff 시험에서 decision/state/bundle timestamp chronology conflict를 발견했고, 공통 timezone-aware clock과 시간순서 검증 규칙을 적용한다.
- allowed_next_action: PAIR_RULE_COMPLETENESS_AUDIT 승인 대기
- forbidden_actions: ['PAIR_GENERATION', 'RESEARCH_RULE_CHANGE', 'OFFICIAL_LOCK']
- approval_source: USER_APPROVED_STATE_SYSTEM_PATCH_4_1
- decision_hash: 16789d868384e79593ce44eb059a8b343acf63b0247765434a7b2a8715ff8b52

## DECISION-20260810-016
- timestamp: 2026-08-10T14:37:40+09:00
- project_version: P45 v2.7.3
- stage: STATE_SYSTEM_OPERATION
- category: PROTECTION_HANDOFF_OPERATION
- decision: P45 Portable Handoff가 실제 별도 ChatGPT 새 대화에서 STATE_HANDOFF_PORTABLE_ONLY로 정상 복구됨을 검증 완료했다.
- reason: 기존 대화 기억 없이 최신 P45_PORTABLE_HANDOFF.zip 내부만 사용한 외부 실전시험에서 내부 충돌 0건과 연구 상태의 정확한 복구가 확인됐다.
- evidence: 사용자 보고: 외부 새 ChatGPT 대화, STATE_HANDOFF_PORTABLE_ONLY, conflicts 0, chronology 정상
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 Portable Handoff가 실제 별도 ChatGPT 새 대화에서 STATE_HANDOFF_PORTABLE_ONLY로 정상 복구됨을 검증 완료했다.
- allowed_next_action: PAIR_RULE_COMPLETENESS_AUDIT 승인 대기
- forbidden_actions: ['PAIR_GENERATION', 'FINAL_SIX', 'OFFICIAL_LOCK', 'RESEARCH_RULE_CHANGE']
- approval_source: USER_REPORTED_EXTERNAL_CHATGPT_TEST
- decision_hash: c8a1b92981c562e17c3607afca36ba83fb5644811b44f8e721e6958b004c2224

## DECISION-20260810-017
- timestamp: 2026-08-10T14:42:50+09:00
- project_version: P45 v2.7.3
- stage: PAIR_RULE_COMPLETENESS_AUDIT
- category: RESEARCH_BLOCKER_PROTECTION
- decision: 공식 문서와 현재 저장자료를 감사한 결과 PAIR_SPEC_GAP으로 판정하며, 공식 PAIR 보완문서 승인 전까지 PAIR 구현과 생성을 금지한다.
- reason: PAIR signature, 완전한 상태 결정표, PAIR walkforward 노출 규칙, 위험·구조 계산식, 파레토·동점 비교식 및 필요한 과거 노출자료가 불완전하다.
- evidence: P45 v2.7.1 제1·2·6·7·8·12·21~26·30·31·35~36장, v2.7.3 제21~23장, schema 273 pair_ledger 및 Stage 7.2 final DB 읽기 전용 대조
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: 공식 문서와 현재 저장자료를 감사한 결과 PAIR_SPEC_GAP으로 판정하며, 공식 PAIR 보완문서 승인 전까지 PAIR 구현과 생성을 금지한다.
- allowed_next_action: PAIR 공식 보완문서의 규칙 정의 및 별도 승인
- forbidden_actions: ['PAIR_GENERATION', 'PAIR_IMPLEMENTATION', 'FINAL_SIX', 'SET_1_SET_2', 'CORE_SET_READY', 'OFFICIAL_LOCK']
- approval_source: USER_APPROVED_PAIR_RULE_COMPLETENESS_AUDIT
- decision_hash: acc4aca2587093d77dc09b35ee69e288a04cc451727aaf8346c7313f459913c3

## DECISION-20260810-018
- timestamp: 2026-08-10T14:56:31+09:00
- project_version: P45 v2.7.3
- stage: PAIR_SPEC_AMENDMENT_REQUIRED
- category: DRAFT_ARTIFACT_RECORD
- decision: P45 v2.7.4 PAIR Gate Amendment DRAFT와 Review Matrix를 작성했으며, DRAFT_SPEC_COMPLETE로 자체 검토됐지만 공식 규칙 권한은 없고 사용자 검토 대기 상태로 보존한다.
- reason: PAIR_SPEC_GAP의 15개 blocker를 제거하는 결정론적 보완규칙 초안 작성 요청을 완료했다.
- evidence: DRAFT sha256 ee6185f9dfb9aad4f6242f5d69d46e576deb650df90f04bac5b561f54d94ec2e; review matrix sha256 4cd8c1ab57657f44066f61710d36c7c20ca8e538fbbc63a4e9a301196651f3aa
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 v2.7.4 PAIR Gate Amendment DRAFT와 Review Matrix를 작성했으며, DRAFT_SPEC_COMPLETE로 자체 검토됐지만 공식 규칙 권한은 없고 사용자 검토 대기 상태로 보존한다.
- allowed_next_action: DRAFT 검토·수정 지시 또는 별도 공식 채택 승인
- forbidden_actions: ['DRAFT_AUTO_ADOPTION', 'PAIR_IMPLEMENTATION', 'PAIR_GENERATION', 'FINAL_SIX', 'OFFICIAL_LOCK']
- approval_source: USER_DIRECTED_PAIR_AMENDMENT_DRAFT
- decision_hash: e0fc706036620d0eca28c97df690605d4b65607477af06d46fe25c83973c90ef

## DECISION-20260810-019
- timestamp: 2026-08-10T15:13:12+09:00
- project_version: P45 v2.7.3
- stage: PAIR_SPEC_AMENDMENT_ADOPTION
- category: OFFICIAL_RULE_ADOPTION
- decision: 검증된 P45 v2.7.4 PAIR Gate Amendment를 공식 채택하고 PAIR SPEC blocker를 해소한다. PAIR 구현·생성은 별도 승인 전까지 시작하지 않는다.
- reason: 최종 검토 A~E PASS, OPEN_GAP 0, PAIR_DRAFT_APPROVAL_READY가 확인됐고 사용자가 공식 채택을 명시 승인했다.
- evidence: official document sha256 a31a065838f88c65d40605c1a170c13eb5fca7cf3d706de5eda088b43227ae6f; approved draft sha256 090765e23f3b4c87a24371a41526fa20f3a346af445fead0bce6ba43066ef73b
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: 검증된 P45 v2.7.4 PAIR Gate Amendment를 공식 채택하고 PAIR SPEC blocker를 해소한다. PAIR 구현·생성은 별도 승인 전까지 시작하지 않는다.
- allowed_next_action: P45 v2.7.4 PAIR 구현 계획·범위에 대한 별도 승인
- forbidden_actions: ['PAIR_IMPLEMENTATION_WITHOUT_APPROVAL', 'PAIR_GENERATION', 'WALKFORWARD', 'FINAL_SIX', 'SCHEMA_CHANGE', 'OFFICIAL_LOCK']
- approval_source: USER_EXPLICIT_V274_OFFICIAL_ADOPTION
- decision_hash: c367c28970d79f96483a24b7c06e0dd26df0cdfc042c28086da0a8926d2ede05

## DECISION-20260810-020
- timestamp: 2026-08-10T15:42:24+09:00
- project_version: P45 v2.7.4
- stage: PAIR_STAGE_1_2_COMPLETE
- category: IMPLEMENTATION_STAGE_COMPLETE
- decision: P45 v2.7.4 PAIR 구현 1단계 schema/storage와 2단계 candidate/canonical key/pair_rule_signature를 합성 fixture 한정으로 완료
- reason: 사용자가 PAIR 구현 1·2단계를 명시적으로 승인했고 관련 최소 검증 10건을 통과함
- evidence: schema274 standalone fixture integrity/FK/unique, storage rollback/reload, disjoint candidate, canonical key, identity-free deterministic signature tests PASS
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 v2.7.4 PAIR 구현 1단계 schema/storage와 2단계 candidate/canonical key/pair_rule_signature를 합성 fixture 한정으로 완료
- allowed_next_action: PAIR 3단계 gate/state/risk/structure/recent/Pareto/ranking 별도 승인 후 구현
- forbidden_actions: ['OFFICIAL_PAIR_GENERATION', 'PAIR_WALKFORWARD', 'FINAL_SIX', 'OFFICIAL_LOCK']
- approval_source: USER
- decision_hash: ad727e1decc73113079b6504e96c253e562d447c17331b97038e153657b66ec4

## DECISION-20260810-021
- timestamp: 2026-08-10T15:50:41+09:00
- project_version: P45 v2.7.4
- stage: PAIR_STAGE_3_COMPLETE
- category: IMPLEMENTATION_STAGE_COMPLETE
- decision: P45 v2.7.4 PAIR 구현 3단계 gate/state/risk/structure/recent/Pareto/ranking/SET assignment 엔진을 합성 fixture 한정으로 완료
- reason: 사용자가 3단계를 명시적으로 승인했고 PAIR 직접 관련 테스트 22건을 통과함
- evidence: PG01..PG14, four-state precedence, TEST_READY fixed cases, risk/structure/recent/bonus, structural Pareto, public ranking and deterministic SET assignment tests PASS
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 v2.7.4 PAIR 구현 3단계 gate/state/risk/structure/recent/Pareto/ranking/SET assignment 엔진을 합성 fixture 한정으로 완료
- allowed_next_action: 현재 회차 1236 PAIR 읽기 전용 진단 실행 별도 승인
- forbidden_actions: ['OFFICIAL_PAIR_GENERATION', 'PAIR_WALKFORWARD', 'FINAL_SIX', 'OFFICIAL_LOCK']
- approval_source: USER
- decision_hash: c6b7372ea1f35458cf4554b49fd69d8b612cb18505b6d04e1ca9ff1bcdba348a

## DECISION-20260810-022
- timestamp: 2026-08-10T16:04:06+09:00
- project_version: P45 v2.7.4
- stage: PAIR_STAGE_4_DIAGNOSTIC_COMPLETE
- category: DIAGNOSTIC_STAGE_COMPLETE
- decision: P45 v2.7.4 1236회 READ-ONLY PAIR 진단 완료; 실제 12 valid TRIO에서 비중복 후보 10개를 검증하고 운영 PAIR 0행 유지
- reason: 사용자가 PAIR 구현 4단계 읽기 전용 진단을 명시적으로 승인했고 미래누출 없이 10회 결정론을 확인함
- evidence: PAIR_DIAGNOSTIC_READY; valid TRIO 12, disjoint PAIR 10, PAIR_SYSTEM_HOLD 10 due absent PAIR walkforward inputs, deterministic 10/10
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 v2.7.4 1236회 READ-ONLY PAIR 진단 완료; 실제 12 valid TRIO에서 비중복 후보 10개를 검증하고 운영 PAIR 0행 유지
- allowed_next_action: PAIR walkforward 구현·실행 계획 별도 승인
- forbidden_actions: ['OFFICIAL_PAIR_GENERATION', 'PAIR_WALKFORWARD_WITHOUT_APPROVAL', 'FINAL_SIX', 'OFFICIAL_LOCK']
- approval_source: USER
- decision_hash: 3f59f76a5fb9d360bdcbd1e3e8094730d21ced6c648f716ba360ea3b0d17db17

## DECISION-20260810-023
- timestamp: 2026-08-10T16:09:27+09:00
- project_version: P45 v2.7.4
- stage: PAIR_STAGE_5_PREFLIGHT_FAILED
- category: IMPLEMENTATION_BLOCKER_CONFIRMED
- decision: P45 v2.7.4 PAIR WALKFORWARD 실행 승인에 따라 FAIL-FAST preflight를 수행했으나 공식 schema 열 누락과 signature/exposure bootstrap 미정의로 전체 실행을 시작하지 않음
- reason: 정확성 우선 및 preflight 하나라도 FAIL 시 전체 실행 금지라는 사용자 지시 준수
- evidence: PAIR engine 22/22 PASS, official SHA/integrity/FK PASS; PAIR_SCHEMA274_OUTCOME_GAP and PAIR_SIGNATURE_EXPOSURE_BOOTSTRAP_UNDEFINED detected
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 v2.7.4 PAIR WALKFORWARD 실행 승인에 따라 FAIL-FAST preflight를 수행했으나 공식 schema 열 누락과 signature/exposure bootstrap 미정의로 전체 실행을 시작하지 않음
- allowed_next_action: PAIR v2.7.4 보완규칙으로 outcome bonus columns 및 signature/exposure bootstrap 순서를 공식 확정
- forbidden_actions: ['PAIR_WALKFORWARD', 'PAIR_AGGREGATION', 'FINAL_SIX', 'OFFICIAL_LOCK']
- approval_source: USER
- decision_hash: ae3f6b0dd1ab30336c11a3de3abc6211e223268f44b0ec66590c1837675af073

## DECISION-20260810-024
- timestamp: 2026-08-10T16:16:17+09:00
- project_version: P45 v2.7.4
- stage: PAIR_WALKFORWARD_BOOTSTRAP_PATCH_DRAFT_COMPLETE
- category: DRAFT_AND_SCHEMA_PATCH_COMPLETE
- decision: PAIR schema274 bonus-assisted outcome 열 구현 누락을 수정하고 비순환 walkforward bootstrap PATCH DRAFT를 작성·검증함; DRAFT는 공식 권한 없음
- reason: 사용자가 preflight blocker 2건만 집중 보완하도록 승인함
- evidence: PAIR 관련 28/28 tests PASS; UTF-8 BOM/CRLF/replacement checks PASS; BOOTSTRAP_DRAFT_COMPLETE
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: PAIR schema274 bonus-assisted outcome 열 구현 누락을 수정하고 비순환 walkforward bootstrap PATCH DRAFT를 작성·검증함; DRAFT는 공식 권한 없음
- allowed_next_action: Bootstrap PATCH DRAFT 공식 검토·채택 여부 결정
- forbidden_actions: ['PAIR_WALKFORWARD', 'DRAFT_AS_OFFICIAL', 'PAIR_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: c556b53421eac3bf3444de4fb7a95952224ea6ad809b6544b8ef8eab004d9f90

## DECISION-20260810-025
- timestamp: 2026-08-10T16:21:52+09:00
- project_version: P45 v2.7.4
- stage: PAIR_BOOTSTRAP_PATCH_OFFICIAL
- category: OFFICIAL_RULE_PATCH_ADOPTION
- decision: P45 v2.7.4 PAIR Walkforward Bootstrap PATCH 최종 7개 검토 PASS 후 공식 보완문서로 채택
- reason: 사용자가 7개 전부 PASS일 때 조건부 공식 채택을 명시적으로 승인함
- evidence: 7/7 PASS; official PATCH SHA df85587a618e520064553456ec82feb87d5d72b1b3b29139d98fc2120d8dcd86; signature version PAIR-RULE-SIGNATURE-1.1
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 v2.7.4 PAIR Walkforward Bootstrap PATCH 최종 7개 검토 PASS 후 공식 보완문서로 채택
- allowed_next_action: PAIR WALKFORWARD fail-fast preflight 재실행
- forbidden_actions: ['PAIR_WALKFORWARD_WITHOUT_PREFLIGHT', 'PAIR_AGGREGATION', 'FINAL_SIX', 'OFFICIAL_LOCK']
- approval_source: USER
- decision_hash: be95f508159555a48663e5bdafdfa7bd152be9c005f2022473444d4e5c5813fc

## DECISION-20260810-026
- timestamp: 2026-08-10T16:29:12+09:00
- project_version: P45 v2.7.4
- stage: PAIR_WALKFORWARD_PREFLIGHT_RERUN_FAILED
- category: IMPLEMENTATION_BLOCKER_CONFIRMED
- decision: 공식 Bootstrap PATCH 기준 PAIR WALKFORWARD preflight 재검사 결과 signature v1.1과 전용 runner가 미구현되어 전체 실행을 시작하지 않음
- reason: 사용자의 PREFLIGHT ONLY 및 하나라도 FAIL 시 즉시 중단 지시 준수
- evidence: 15항목 중 PASS 8, FAIL/NOT_IMPLEMENTED 7; PAIR tests 28/28 PASS; rounds processed 0
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: 공식 Bootstrap PATCH 기준 PAIR WALKFORWARD preflight 재검사 결과 signature v1.1과 전용 runner가 미구현되어 전체 실행을 시작하지 않음
- allowed_next_action: PAIR-RULE-SIGNATURE-1.1 및 PAIR walkforward/checkpoint runner 구현 승인
- forbidden_actions: ['PAIR_WALKFORWARD', 'PAIR_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: ebecb970345a86f3219ca35b5973b19292d598e7003c1400da31b5b091b0e4c0

## DECISION-20260810-027
- timestamp: 2026-08-10T16:58:38+09:00
- project_version: P45 v2.7.4
- stage: PAIR_SIGNATURE_V11_READY
- category: IMPLEMENTATION_BLOCKER_RESOLVED
- decision: 공식 Bootstrap PATCH에 따라 PAIR base signature payload를 비순환 PAIR-RULE-SIGNATURE-1.1로 구현하고 검증함
- reason: 사용자가 blocker 1만 해결하도록 명시적으로 승인함
- evidence: PAIR 관련 35/35 PASS; v1.0 cyclic fields 0; deterministic 10/10
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: 공식 Bootstrap PATCH에 따라 PAIR base signature payload를 비순환 PAIR-RULE-SIGNATURE-1.1로 구현하고 검증함
- allowed_next_action: PAIR walkforward/checkpoint runner 구현 승인
- forbidden_actions: ['PAIR_WALKFORWARD', 'PAIR_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 204a45d928f854c4e68a6e3c0dea8f2dc4eeadff7e26c3dcb2c7b9cb46b39d46

## DECISION-20260810-028
- timestamp: 2026-08-10T17:10:00+09:00
- project_version: P45 v2.7.4
- stage: PAIR_WALKFORWARD_RUNNER_READY
- category: IMPLEMENTATION_BLOCKER_RESOLVED
- decision: P45 v2.7.4 PAIR walkforward 전용 atomic checkpoint/resume runner를 구현하고 합성 범위에서 검증함; full walkforward는 실행하지 않음
- reason: 사용자가 마지막 runner blocker만 해결하도록 승인함
- evidence: PAIR 관련 44/44 PASS; prediction-before-result, R+1 history, rollback/resume/duplicates/hash fail-fast verified
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 v2.7.4 PAIR walkforward 전용 atomic checkpoint/resume runner를 구현하고 합성 범위에서 검증함; full walkforward는 실행하지 않음
- allowed_next_action: PAIR WALKFORWARD fail-fast full preflight
- forbidden_actions: ['FULL_PAIR_WALKFORWARD_WITHOUT_PREFLIGHT', 'PAIR_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: d8d38b8886656360b9bd678b7dfbe27d6d436af66708fafe56b7a6a2d87cd60a

## DECISION-20260810-029
- timestamp: 2026-08-10T17:19:34+09:00
- project_version: P45 v2.7.4
- stage: PAIR_WALKFORWARD_FINAL_PREFLIGHT_FAILED
- category: IMPLEMENTATION_BLOCKER_CONFIRMED
- decision: P45 PAIR WALKFORWARD ?? preflight?? production pipeline adapter ??? ???? full ??? ???? ??
- reason: ???? 22?? FAIL-FAST? ??? ?? ?? ??
- evidence: 21 PASS, 1 FAIL; runner tests 44/44 PASS; production DB/run/round 0
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 PAIR WALKFORWARD ?? preflight?? production pipeline adapter ??? ???? full ??? ???? ??
- allowed_next_action: ?? P45 UNIT?NUMBER?TRIO?PAIR production pipeline adapter ? entrypoint ?? ??
- forbidden_actions: ['FULL_PAIR_WALKFORWARD', 'PAIR_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 170cd134f576081f23e69789877293d6ef518e4a2e792735a34d97317088132e

## DECISION-20260810-030
- timestamp: 2026-08-10T17:34:27+09:00
- project_version: P45 v2.7.4
- stage: PAIR_PRODUCTION_ADAPTER_READY
- category: IMPLEMENTATION_BLOCKER_RESOLVED
- decision: P45 v2.7.4 PAIR production pipeline adapter와 실행 진입점을 공식 기존 엔진의 얇은 연결 계층으로 구현하고 검증함; full walkforward는 실행하지 않음
- reason: 사용자가 마지막 production adapter blocker만 해결하도록 승인함
- evidence: PAIR 관련 48/48 PASS; R43/R1235/R1236 read-only smoke, R-1 boundary, prediction-before-outcome, 10회 결정론 및 임시 DB runner 연결 검증
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 v2.7.4 PAIR production pipeline adapter와 실행 진입점을 공식 기존 엔진의 얇은 연결 계층으로 구현하고 검증함; full walkforward는 실행하지 않음
- allowed_next_action: PAIR WALKFORWARD 최종 fail-fast preflight 재실행
- forbidden_actions: ['FULL_PAIR_WALKFORWARD_WITHOUT_PREFLIGHT', 'PAIR_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 86bc0388dfc4360eef4b9de3c12106bb174f4c877bd8340a369a092d51075c3e

## DECISION-20260810-031
- timestamp: 2026-08-10T17:38:35+09:00
- project_version: P45 v2.7.4
- stage: PAIR_WALKFORWARD_PREFLIGHT_READY
- category: PREFLIGHT_VERIFIED
- decision: P45 v2.7.4 PAIR WALKFORWARD 최종 fail-fast preflight 23개 항목을 모두 통과함; full walkforward는 실행하지 않음
- reason: 사용자가 production 실행 경로 중심의 최종 preflight만 승인함
- evidence: 23/23 PASS; focused tests 12/12 PASS; five historical blockers resolved; operational PAIR 0; production DB/run/round 0
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 v2.7.4 PAIR WALKFORWARD 최종 fail-fast preflight 23개 항목을 모두 통과함; full walkforward는 실행하지 않음
- allowed_next_action: 사용자 별도 승인 후 P45 v2.7.4 PAIR FULL WALKFORWARD 실행
- forbidden_actions: ['PAIR_AGGREGATION_BEFORE_WALKFORWARD_COMPLETE', 'FINAL_SIX', 'RULE_RELAXATION']
- approval_source: USER
- decision_hash: 974ea88641bc603adbb741898b109ed6dcc283927e0fcaf40ca99630033ae1f5

## DECISION-20260810-032
- timestamp: 2026-08-10T21:49:29+09:00
- project_version: P45 v2.7.4
- stage: PAIR_WALKFORWARD_EXECUTION_CONFLICT
- category: EXECUTION_VALIDATION_CONFLICT
- decision: P45 v2.7.4 PAIR full walkforward raw runner는 43~1235 전 범위를 완료했으나 필수 gate/state context가 후보 장부에 저장되지 않아 공식 완료 승인을 보류하고 PAIR_WALKFORWARD_CONFLICT로 판정함
- reason: 완료 후 단일 검증에서 148215개 candidate context에 gate/state 필드가 0개임을 확인함
- evidence: raw run COMPLETE 1193/1193, FAILED 0, integrity ok, FK 0, duplicate/missing/future leak 0; mandatory gate/state context absent
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 v2.7.4 PAIR full walkforward raw runner는 43~1235 전 범위를 완료했으나 필수 gate/state context가 후보 장부에 저장되지 않아 공식 완료 승인을 보류하고 PAIR_WALKFORWARD_CONFLICT로 판정함
- allowed_next_action: PAIR_WALKFORWARD_GATE_STATE_CONTEXT_NOT_STORED 충돌의 수정·기존 run 처리 방안 승인
- forbidden_actions: ['PAIR_FINAL_AGGREGATION', 'FINAL_SIX', 'NEW_WALKFORWARD_RUN_WITHOUT_APPROVAL', 'ALTER_COMPLETED_PREDICTION_CONTEXT']
- approval_source: USER
- decision_hash: 2920e3976a121ad7c45963bd0bd18faaa59d93c7084fc8a0d544f3bf945254b0

## DECISION-20260811-033
- timestamp: 2026-08-11T11:55:29+09:00
- project_version: P45 v2.7.4
- stage: PAIR_WALKFORWARD_REPAIR_NOT_SAFE
- category: REPAIR_SAFETY_DECISION
- decision: PAIR walkforward의 미래 저장 계층은 gate/state 필수 저장과 outcome 전 fail-fast로 보완했으나 기존 완료 run 148215 candidate는 공식 gate/state를 outcome 없이 정확히 재현할 근거가 부족하여 자동 repair를 금지함
- reason: 모든 candidate에 gate/state 및 핵심 pre-result 시계열 입력이 없고 signature exposure 최대값이 7이라 필수 충분표본 재현검사도 불가능함
- evidence: storage enforcement tests 26/26 PASS; source DB SHA unchanged; safe repair 0, unsafe/unproven 148215; outcome/future repair use 0; repaired DB not created
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: PAIR walkforward의 미래 저장 계층은 gate/state 필수 저장과 outcome 전 fail-fast로 보완했으나 기존 완료 run 148215 candidate는 공식 gate/state를 outcome 없이 정확히 재현할 근거가 부족하여 자동 repair를 금지함
- allowed_next_action: 공식 pre-result PAIR gate/state context builder 구현 및 검증 후 fresh walkforward 필요 여부 별도 승인
- forbidden_actions: ['BACKFILL_COMPLETED_RAW_RUN', 'FULL_PAIR_WALKFORWARD_WITHOUT_NEW_APPROVAL', 'PAIR_FINAL_AGGREGATION', 'FINAL_SIX', 'OUTCOME_ASSISTED_REPAIR']
- approval_source: USER
- decision_hash: b0ca03cac49f53e586e9c2f0c873a12e4e86ace5dd3c254f3654cdf019bd57d7

## DECISION-20260811-034
- timestamp: 2026-08-11T12:10:53+09:00
- project_version: P45 v2.7.4
- stage: PAIR_SIGNATURE_EXPOSURE_VIABILITY_AUDIT
- category: READ_ONLY_RESEARCH_DIAGNOSTIC
- decision: PAIR-RULE-SIGNATURE-1.1의 RAW walkforward exposure는 88498 selection이 82651 signature로 분산되고 최대 8회에 그쳐 공식 50/200 band에 도달하지 못한 PAIR_SIGNATURE_EXPOSURE_STARVATION으로 판정함
- reason: signature 94.41%가 1회 노출이며 반복 PAIR identity의 99.67%가 재등장 시 다른 signature로 분리됨
- evidence: ge50=0, ge200=0, median=1, p90=1, p95=2, p99=3; identity/selection exposure separation and uniqueness verified; raw DB read-only
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: PAIR-RULE-SIGNATURE-1.1의 RAW walkforward exposure는 88498 selection이 82651 signature로 분산되고 최대 8회에 그쳐 공식 50/200 band에 도달하지 못한 PAIR_SIGNATURE_EXPOSURE_STARVATION으로 판정함
- allowed_next_action: PAIR v1.1 signature granularity 공식 규칙 완전성 검토 및 payload auditability 보완안 설계
- forbidden_actions: ['SIGNATURE_RULE_CHANGE_WITHOUT_FORMAL_AMENDMENT', 'THRESHOLD_RELAXATION', 'FULL_PAIR_WALKFORWARD', 'PAIR_FINAL_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 2adcf597b62ceab2a7b1dddf1c8037dcd8c8c0762ef8b15fc29e026b0d517f08

## DECISION-20260811-035
- timestamp: 2026-08-11T12:16:52+09:00
- project_version: P45 v2.7.4
- stage: PAIR_SIGNATURE_V12_DRAFT_COMPLETE
- category: DRAFT_DESIGN_COMPLETE
- decision: PAIR-RULE-SIGNATURE의 반복 rule identity와 동적 context fingerprint를 분리하는 v1.2 PATCH DRAFT 및 Review를 작성했으며 공식 채택·구현은 하지 않음
- reason: v1.1 exposure starvation은 stable selection rule과 dynamic pre-result context가 하나의 signature에 혼합된 granularity 문제로 확인됨
- evidence: outcome-free shadow에서 EXPANDED_TEST_POOL rule bucket 1개가 eligible 258회와 50/200 band를 모두 형성; RAW DB SHA 불변
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: PAIR-RULE-SIGNATURE의 반복 rule identity와 동적 context fingerprint를 분리하는 v1.2 PATCH DRAFT 및 Review를 작성했으며 공식 채택·구현은 하지 않음
- allowed_next_action: PAIR Signature v1.2 DRAFT 최종 검토 및 공식 채택 여부 결정
- forbidden_actions: ['V12_OFFICIAL_WITHOUT_APPROVAL', 'SIGNATURE_CODE_CHANGE', 'FULL_PAIR_WALKFORWARD', 'RAW_DB_MODIFICATION', 'THRESHOLD_RELAXATION', 'PAIR_FINAL_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: e2c40b12e55de887fc43770f0d3dc4878e037a5e69b33b081b83f669770e5bf7

## DECISION-20260811-036
- timestamp: 2026-08-11T12:21:12+09:00
- project_version: P45 v2.7.4
- stage: PAIR_SIGNATURE_V12_REVISION_REQUIRED
- category: DRAFT_FINAL_REVIEW_FAILED
- decision: PAIR Signature v1.2 DRAFT의 rule/context 분리 방향과 258회 동일 configuration은 확인했으나 실제 selection 행동을 바꾸는 policy hash가 canonical rule payload에 누락되어 under-separation 위험이 있으므로 공식 채택하지 않음
- reason: eligibility, valid_for_pair, disjoint candidate, ranking, representative grouping, gate/bootstrap policy 변경 counterfactual에서 현재 DRAFT signature가 달라지지 않음
- evidence: dynamic-context counterfactual PASS; included 7 rule fields PASS; omitted rule-policy counterfactual FAIL; RAW run 258 rounds fixed rule/code/schema/source hashes and same pool path
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: PAIR Signature v1.2 DRAFT의 rule/context 분리 방향과 258회 동일 configuration은 확인했으나 실제 selection 행동을 바꾸는 policy hash가 canonical rule payload에 누락되어 under-separation 위험이 있으므로 공식 채택하지 않음
- allowed_next_action: v1.2 DRAFT canonical rule payload에 누락 policy hash와 exact context schema만 보완
- forbidden_actions: ['V12_OFFICIAL_ADOPTION', 'SIGNATURE_CODE_CHANGE', 'CONTEXT_BUILDER_IMPLEMENTATION', 'FULL_PAIR_WALKFORWARD', 'RAW_DB_MODIFICATION', 'THRESHOLD_CHANGE', 'PAIR_FINAL_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 5c520c7559d4d6783bc2908e19c1b696ff9fc90b2486bdbb63941511d42db01f

## DECISION-20260811-037
- timestamp: 2026-08-11T12:30:31+09:00
- project_version: P45 v2.7.4
- stage: PAIR_SIGNATURE_V12_DRAFT_REVISED_COMPLETE
- category: DRAFT_REVISION_COMPLETE
- decision: PAIR Signature v1.2 DRAFT의 누락된 6개 semantic policy identity와 exact canonical context audit schema를 보완 완료하되 공식 채택은 하지 않음
- reason: 이전 REVISION_REQUIRED의 두 항목만 보완하여 실제 selection 정책 변경은 signature를 바꾸고 동적 round context 변경은 context fingerprint만 바꾸도록 결정론적으로 정의함
- evidence: 6개 semantic policy descriptor counterfactual 6/6 PASS; dynamic context counterfactual 6/6 PASS; outcome columns read 0; 수정 DRAFT SHA b34702355ff1f209ca267ded95e2b8500370731ea09bd1a720dec09427250611; Review SHA c00a2526816cb8b991830e4cfbb98166456be4a0b364abb239c10e493b61365c
- affected_files: P45_v2.7.4_PAIR_Signature_v1.2_PATCH_DRAFT_UTF8_BOM_CRLF.md; P45_v2.7.4_PAIR_Signature_v1.2_PATCH_Review.md; state files
- affected_schema: none
- previous_rule: PAIR Signature v1.2 DRAFT REVISION_REQUIRED: policy identity와 exact context schema 누락
- new_rule: DRAFT에 6개 semantic policy hash와 exact canonical context schema를 추가했으며 공식 signature는 v1.1 유지
- allowed_next_action: 수정된 PAIR Signature v1.2 DRAFT의 최종 의미 검토와 조건부 공식 채택 여부 결정
- forbidden_actions: ['V12_OFFICIAL_ADOPTION_WITHOUT_REVIEW', 'SIGNATURE_CODE_CHANGE', 'CONTEXT_BUILDER_IMPLEMENTATION', 'FULL_PAIR_WALKFORWARD', 'RAW_DB_MODIFICATION', 'THRESHOLD_CHANGE', 'PAIR_FINAL_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: d00b265f29a524f84cec1f1f713cc8a56b56331729470ecfd6bfe8769e50718e

## DECISION-20260811-038
- timestamp: 2026-08-11T12:34:11+09:00
- project_version: P45 v2.7.4
- stage: PAIR_SIGNATURE_V12_REVISION_REQUIRED
- category: DRAFT_CONDITIONAL_ADOPTION_FAILED
- decision: PAIR Signature v1.2 수정 DRAFT의 최종 8항목 중 2,3,5,7이 FAIL하여 공식 채택하지 않고 REVISION_REQUIRED로 유지
- reason: 공식 15-key와 PG01~PG14 semantic descriptor가 향후 확장 지시로 남고 context input object와 field dictionary가 미확정이며 공식 context version에 DRAFT suffix가 남아 결정론적 공식 구현과 완전 감사가 불가능함
- evidence: 8항목 PASS/FAIL = PASS,FAIL,FAIL,PASS,FAIL,PASS,FAIL,PASS; DRAFT SHA b34702355ff1f209ca267ded95e2b8500370731ea09bd1a720dec09427250611; Adoption Review SHA 2c3e1aab3aad7a91b52c4614e4020875b9684d32b31cc1df87bd70c8c62370de; RAW DB SHA 1d7fe8ba1c50e454b57d5bfe86da1e1bfee1fd2c6577cce47ae3d72dd89cfd57 불변
- affected_files: P45_v2.7.4_PAIR_Signature_v1.2_PATCH_Adoption_Review.md; state files
- affected_schema: none
- previous_rule: PAIR_SIGNATURE_V12_DRAFT_REVISED_COMPLETE
- new_rule: PAIR_SIGNATURE_V12_REVISION_REQUIRED; 공식 v1.1 유지
- allowed_next_action: v1.2 DRAFT의 15-key·PG01~PG14 semantic descriptor, exact context input schema, 공식 context version만 보완
- forbidden_actions: ['V12_OFFICIAL_ADOPTION', 'SIGNATURE_V12_CODE_IMPLEMENTATION', 'CONTEXT_FINGERPRINT_CODE_IMPLEMENTATION', 'SCHEMA_CHANGE', 'CONTEXT_BUILDER_IMPLEMENTATION', 'FULL_PAIR_WALKFORWARD', 'RAW_DB_MODIFICATION', 'PAIR_FINAL_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 8b20193761b6ba9ef31019a8b238149b23cccc884f37085b8321aaaaa4bdee40

## DECISION-20260811-039
- timestamp: 2026-08-11T12:39:48+09:00
- project_version: P45 v2.7.4
- stage: PAIR_SIGNATURE_V12_DEFINITION_GAP
- category: DRAFT_DEFINITION_GAP
- decision: PAIR Signature v1.2 DRAFT 보완 중 공식 PG05와 PG14의 prediction/commit 시간 경계를 하나로 확정할 수 없어 GATE_DESCRIPTOR_GAP으로 중단
- reason: PG05는 gate/state 계산 뒤 저장되는 prediction hash의 선저장을 요구하고 PG14는 outcome을 포함한 회차 transaction commit 후에만 최종 PASS이므로 pre-result context의 gate 상태를 공식 원문만으로 결정할 수 없음
- evidence: Gate Amendment 제4장 순서, 제12장 PG05/PG14 predicate 및 PG13 부연의 시간 경계 대조; Definition Gap Review SHA 884db51d5439e96409ab74d9363362149b8750e57d4bd1f14fd5e4c9e55c1912; DRAFT와 Review SHA 불변
- affected_files: P45_v2.7.4_PAIR_Signature_v1.2_DEFINITION_GAP_Review.md; state files
- affected_schema: none
- previous_rule: PAIR_SIGNATURE_V12_REVISION_REQUIRED
- new_rule: PAIR_SIGNATURE_V12_DEFINITION_GAP; PG05/PG14 공식 시간 경계 보완 필요
- allowed_next_action: PG05 prediction prelock 평가 시점, PG14 staged/final 상태, 회차 transaction 경계를 공식 보완
- forbidden_actions: ['V12_OFFICIAL_ADOPTION', 'SIGNATURE_V12_CODE_IMPLEMENTATION', 'CONTEXT_FINGERPRINT_CODE_IMPLEMENTATION', 'SCHEMA_CHANGE', 'CONTEXT_BUILDER_IMPLEMENTATION', 'FULL_PAIR_WALKFORWARD', 'RAW_DB_MODIFICATION', 'PAIR_FINAL_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 9019bba77a2cbab564a5db22f327f43481f17fdc8ad80810d30d337328104a02

## DECISION-20260811-040
- timestamp: 2026-08-11T12:44:26+09:00
- project_version: P45 v2.7.4
- stage: PAIR_GATE_TIMING_REVISION_REQUIRED
- category: TIMING_SPEC_CONFLICT
- decision: PAIR PG05/PG14 Timing 보완안 내부에서 gate/state 확정과 prediction staging 순서가 순환하므로 공식 PATCH와 v1.2 DRAFT 후속 보완을 시작하지 않음
- reason: PG05와 PG14는 final gate/state를 포함한 payload staging 검증 뒤 PASS해야 하지만 고정 transaction 순서는 gate/state를 staging 전에 확정하도록 요구하여 비순환 canonical prediction payload를 만들 수 없음
- evidence: 제안 A PG05 단계 3~6과 제안 B transaction 단계 3~5 대조; v1.2 context payload의 gate/state 포함 조건; Timing Consistency Review SHA 43e9c222d2803bd8cece7dee89468b4eb56a50f938a34514ee5cee2cbabaeb3e
- affected_files: P45_v2.7.4_PAIR_Gate_Timing_Consistency_Review.md; state files
- affected_schema: none
- previous_rule: PAIR_SIGNATURE_V12_DEFINITION_GAP
- new_rule: PAIR_GATE_TIMING_REVISION_REQUIRED; 공식 v1.1 유지
- allowed_next_action: PG05/PG14 prelock payload와 final prediction payload의 분리 또는 결정론적 two-phase 평가 순서를 공식 선택
- forbidden_actions: ['TIMING_PATCH_OFFICIAL_ADOPTION', 'V12_DRAFT_FURTHER_FINALIZATION', 'SIGNATURE_CODE_CHANGE', 'CONTEXT_CODE_IMPLEMENTATION', 'SCHEMA_CHANGE', 'FULL_PAIR_WALKFORWARD', 'RAW_DB_MODIFICATION', 'PAIR_FINAL_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 8cdac8776c71bf43dc1f54d2f6ea04f1310a06b653da68d6d38a46ec99a88a2d

## DECISION-20260811-041
- timestamp: 2026-08-11T12:54:03+09:00
- project_version: P45 v2.7.4
- stage: PAIR_GATE_TIMING_PATCH_OFFICIAL
- category: OFFICIAL_TIMING_PATCH_ADOPTED
- decision: PAIR PG05·PG14 순환을 PRELOCK, FINAL-PREDICTION, FINALIZATION의 결정론적 three-layer two-phase 구조로 해소하고 timing/transaction PATCH를 공식 채택
- reason: 각 gate가 자신의 결과나 final state를 hash 입력으로 요구하지 않으며 PG01~PG14와 final state가 outcome 전에 확정되고 commit은 별도 ROUND_TRANSACTION_CERTIFIED 실행 인증으로 분리됨
- evidence: Timing 의미 검증 10/10 PASS; DRAFT SHA f10d6b1c8dbfd80117a419c25735932d7c2a5cec4636729e7507c5bcf231012f; 공식 PATCH SHA 0ecca7f3122cf9017df1d862f86662e851e70202052f994f440e3ffc113bafa7
- affected_files: P45_v2.7.4_PAIR_Gate_Timing_PATCH_DRAFT_UTF8_BOM_CRLF.md; P45_v2.7.4_PAIR_Gate_Timing_PATCH_UTF8_BOM_CRLF.md; state files
- affected_schema: none
- previous_rule: PG05/PG14 prediction staging timing 순환 미해결
- new_rule: PRELOCK→PG05→PG01~13→FINAL-PREDICTION→PG14→FINALIZATION→outcome→commit certification
- allowed_next_action: 공식 Timing PATCH를 source of truth로 사용해 중단된 15-key·PG descriptor와 exact Context DRAFT 보완
- forbidden_actions: ['SIGNATURE_V12_OFFICIAL_ADOPTION', 'SIGNATURE_CODE_CHANGE', 'CONTEXT_CODE_IMPLEMENTATION', 'SCHEMA_CHANGE', 'FULL_PAIR_WALKFORWARD', 'RAW_DB_MODIFICATION', 'PAIR_FINAL_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 5a01583048343149f36c48b4f31c9a0230e794fbc91135afd25be75496e5a023

## DECISION-20260811-042
- timestamp: 2026-08-11T13:02:16+09:00
- project_version: P45 v2.7.4
- stage: PAIR_SIGNATURE_V12_DEFINITION_GAP
- category: DESCRIPTOR_TIMING_CONFLICT
- decision: PAIR Signature v1.2 descriptor 완성 중 PG13 actual executed sequence와 공식 Timing PATCH의 PG14 후행 순서가 충돌하여 DRAFT FINALIZED 판정을 중단
- reason: PG13은 PG01~PG14 실제 실행 sequence를 요구하지만 FINAL-PREDICTION에는 PG01~PG13 결과가 PG14 실행 전에 들어가야 하므로 PG13을 진실하게 확정할 수 없음
- evidence: 15-key descriptor 15개 parse PASS, ranking candidate semantic hash b8965fbbf91b7cdb4423fdf9c35da70a9687def464df7fc5fddab1f045ab0d38, Context empty object 0; Draft SHA 75f0e851a48694cf2fddd3beaa3e46969355a38aff2d4d8183fbbdd456edbbd3; Review SHA b46a96bc04add1008f41f4d4147ab98e14dbcd092a10226509bf56a5247fd3af
- affected_files: P45_v2.7.4_PAIR_Signature_v1.2_PATCH_DRAFT_UTF8_BOM_CRLF.md; P45_v2.7.4_PAIR_Signature_v1.2_PATCH_Review.md; state files
- affected_schema: none
- previous_rule: 중단된 15-key·PG descriptor와 exact Context DRAFT 보완
- new_rule: PAIR_SIGNATURE_V12_DEFINITION_GAP; PG13/PG14 실행순서 공식 선택 필요
- allowed_next_action: PG13을 planned sequence, preliminary/final two-stage, 또는 PG14 후행 평가 중 하나로 공식 확정
- forbidden_actions: ['SIGNATURE_V12_OFFICIAL_ADOPTION', 'SIGNATURE_CODE_CHANGE', 'CONTEXT_CODE_IMPLEMENTATION', 'SCHEMA_CHANGE', 'FULL_PAIR_WALKFORWARD', 'RAW_DB_MODIFICATION', 'PAIR_FINAL_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 01a38d03058c5f98ecc75ad74b8e359d3d06e727178e2663e76ea4d7a483a6f4

## DECISION-20260811-043
- timestamp: 2026-08-11T13:10:19+09:00
- project_version: P45 v2.7.4
- stage: PAIR_SIGNATURE_V12_DRAFT_FINALIZED
- category: OFFICIAL_SEQUENCE_PATCH_AND_DRAFT_FINALIZATION
- decision: PG13 preliminary/final certification lifecycle을 공식 Sequence PATCH로 채택하고 이를 반영한 PAIR Signature v1.2 descriptor/context DRAFT를 최종 완성
- reason: PG13은 13번째 activation에서 PENDING_FINAL을 잠그고 PG14 14번째 실행 뒤 동일 PG13 record를 outcome 전 final certification하여 실제 sequence를 인증하므로 자기참조 없이 전체 gate/state를 확정할 수 있음
- evidence: PG13 sequence 10/10 PASS; 공식 Sequence PATCH SHA 4412b86bf7ad322c6e3e4cc3a33023a3b09fa4083195e22f9f1c023b513cbc19; ranking hash b8965fbbf91b7cdb4423fdf9c35da70a9687def464df7fc5fddab1f045ab0d38; gate hash 3dce8b886556f952af5c8f401fd2db02cec0527e10647cdbde6747bd543359c5; dynamic 9/9 PASS; rule 6/6 PASS; Draft SHA 0de4035611b2dd56bb65102f4df16000e1f410e4406e9cfbb58f3dd16740f934; Review SHA 06531532b7e7a947ccf52894854fa9209dec97ab302ac05ebb8a8eb04061f906
- affected_files: P45_v2.7.4_PAIR_PG13_Sequence_PATCH_DRAFT_UTF8_BOM_CRLF.md; P45_v2.7.4_PAIR_PG13_Sequence_PATCH_UTF8_BOM_CRLF.md; P45_v2.7.4_PAIR_Signature_v1.2_PATCH_DRAFT_UTF8_BOM_CRLF.md; P45_v2.7.4_PAIR_Signature_v1.2_PATCH_Review.md; state files
- affected_schema: none
- previous_rule: PG13 actual sequence를 PG14 전 확정할 수 없는 definition gap
- new_rule: PG13 PRELIMINARY 13번째 activation, PG14 14번째, PG13 FINAL certification 후 final vector/state
- allowed_next_action: PAIR Signature v1.2 finalized DRAFT의 최종 의미 검토와 조건부 공식 채택 여부 결정
- forbidden_actions: ['SIGNATURE_V12_OFFICIAL_ADOPTION_WITHOUT_REVIEW', 'SIGNATURE_CODE_CHANGE', 'CONTEXT_CODE_IMPLEMENTATION', 'SCHEMA_CHANGE', 'FULL_PAIR_WALKFORWARD', 'RAW_DB_MODIFICATION', 'PAIR_FINAL_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 1e6a369643b05c1e31f9b4d2ad2ef9990f2d17582eafda575e4580bf7eeb76a2

## DECISION-20260811-044
- timestamp: 2026-08-11T13:16:12+09:00
- project_version: P45 v2.7.4
- stage: PAIR_SIGNATURE_V12_OFFICIAL
- category: OFFICIAL_SIGNATURE_PATCH_ADOPTION
- decision: PAIR Signature v1.2 finalized DRAFT의 최종 의미 검토 8/8 PASS에 따라 signature v1.2와 fixed 21-field Context fingerprint v1.0을 공식 채택
- reason: 반복 가능한 연구정책과 동적 context가 완전히 분리되고 Timing/Sequence PATCH, canonical audit payload, counterfactual 및 기존 연구규칙 불변성이 모두 확인됨
- evidence: Finalized DRAFT SHA 0de4035611b2dd56bb65102f4df16000e1f410e4406e9cfbb58f3dd16740f934; final review 8/8 PASS; official PATCH SHA 0c91315ef0cc7d1638a61f321faf3e62079f9545a1386bd3271710b27e113316; Timing/Sequence linkage PASS; dynamic 9/9 and rule-change 6/6 PASS; outcome read 0
- affected_files: P45_v2.7.4_PAIR_Signature_v1.2_PATCH_UTF8_BOM_CRLF.md; P45_v2.7.4_PAIR_Signature_v1.2_Official_Adoption_Review.md; state files
- affected_schema: none
- previous_rule: PAIR-RULE-SIGNATURE-1.1 official; v1.2 finalized DRAFT not official
- new_rule: PAIR-RULE-SIGNATURE-1.2 and PAIR-CONTEXT-FINGERPRINT-1.0 official publication; fixed 21-field schema unchanged
- allowed_next_action: PAIR-RULE-SIGNATURE-1.2 및 PAIR-CONTEXT-FINGERPRINT-1.0 코드·schema 구현을 별도 승인 후 진행
- forbidden_actions: ['SIGNATURE_V12_CODE_IMPLEMENTATION_WITHOUT_APPROVAL', 'CONTEXT_SCHEMA_IMPLEMENTATION_WITHOUT_APPROVAL', 'FULL_PAIR_WALKFORWARD', 'RAW_V11_RUN_REUSE', 'PAIR_FINAL_AGGREGATION', 'FINAL_SIX']
- approval_source: USER
- decision_hash: ef39672cd449406479dc949f3fcae0b4ed5f3095ed5dbfe00c4d37877ee5daf2

## DECISION-20260811-045
- timestamp: 2026-08-11T13:38:03+09:00
- project_version: P45 v2.7.4
- stage: PAIR_V12_IMPLEMENTATION_READY
- category: PAIR_SIGNATURE_CONTEXT_IMPLEMENTATION
- decision: 공식 PAIR-RULE-SIGNATURE-1.2와 PAIR-CONTEXT-FINGERPRINT-1.0을 production adapter 및 전용 walkforward schema2743에 구현하고 관련 검증을 완료
- reason: 공식 6개 semantic policy hash, fixed 21-field Context, Timing/Sequence lifecycle, audit JSON 재hash, runner 저장·resume 및 소규모 production smoke가 모두 통과함
- evidence: PAIR 관련 54/54 PASS; schema2743; smoke R369/R751/R1233/R1236 PASS; outcome 선조회 0; 운영 PAIR 0행; v1.1 RAW SHA 1d7fe8ba1c50e454b57d5bfe86da1e1bfee1fd2c6577cce47ae3d72dd89cfd57 불변; report SHA 448d99bd56f15cec35d9aeba71f7e3e7b8b78e226ac871cda82fc7e26d2c291d
- affected_files: src/p45_v27/pairs/audit_v12.py; src/p45_v27/pairs/lifecycle_v12.py; src/p45_v27/pairs/engine.py; src/p45_v27/pairs/production.py; src/p45_v27/pairs/walkforward.py; src/p45_v27/pair_walkforward.py; related PAIR tests; verification report; state files
- affected_schema: dedicated walkforward schema 2742 to 2743 for future v1.2 runs; operating schema273 unchanged
- previous_rule: official v1.2 documentation adopted but code remained v1.1 and walkforward schema2742
- new_rule: official v1.2/v1.0 implementation ready in schema2743; FULL WALKFORWARD not run
- allowed_next_action: PAIR v1.2 FULL WALKFORWARD 최종 fail-fast preflight를 별도 승인 후 수행
- forbidden_actions: ['FULL_PAIR_WALKFORWARD_WITHOUT_PREFLIGHT_APPROVAL', 'PAIR_FINAL_AGGREGATION', 'RAW_V11_RUN_REUSE', 'OPERATING_PAIR_INSERT', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 5b09e676333e18b17147118bbe1f9a8750c92525b9e1f8c3c50bbd8398d682df

## DECISION-20260811-046
- timestamp: 2026-08-11T13:42:08+09:00
- project_version: P45 v2.7.4
- stage: PAIR_V12_WALKFORWARD_PREFLIGHT_READY
- category: PAIR_V12_FAIL_FAST_PREFLIGHT
- decision: PAIR v1.2 FULL WALKFORWARD 최종 fail-fast preflight 35/35 PASS로 실행 준비 완료
- reason: 공식 문서 해시, v1.2/v1.0/schema2743, semantic policy, Timing/Sequence, audit rehash, exposure, transaction/resume, READ-ONLY 보호를 production 경로에서 확인함
- evidence: 35/35 PASS; focused tests 11/11 PASS; R369/R751 동일 rule signature; outcome access 0; 운영 PAIR 0행; v1.1 RAW SHA 불변; report SHA b281be1df76d1e04fc381af8884edb1d00f8677f38f48332afc78221a398cefa
- affected_files: v27_storage/reports/p45_v274_pair_v12_walkforward_final_preflight.json; state files
- affected_schema: none; schema2743 validated in temporary DB only
- previous_rule: PAIR_V12_IMPLEMENTATION_READY
- new_rule: PAIR_V12_WALKFORWARD_PREFLIGHT_READY; FULL WALKFORWARD not started
- allowed_next_action: PAIR v1.2 FULL WALKFORWARD 실행을 별도 승인 후 시작
- forbidden_actions: ['FULL_PAIR_WALKFORWARD_WITHOUT_USER_APPROVAL', 'PAIR_FINAL_AGGREGATION', 'RAW_V11_RUN_REUSE', 'OPERATING_PAIR_INSERT', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 21d8ba7cfdff8738643e7b105e7c6f3a72a330c3bae4f2c9c58dbc41b6857a2d

## DECISION-20260811-047
- timestamp: 2026-08-11T17:47:35+09:00
- project_version: P45 v2.7.4
- stage: PAIR_V12_WALKFORWARD_COMPLETE
- category: PAIR_V12_FULL_WALKFORWARD_COMPLETION
- decision: 기존 단일 run_id의 PAIR v1.2 FULL WALKFORWARD 43~1235회 완료와 재부팅 후 복구·최종 무결성 검증을 확정
- reason: 기존 DB에서 1,193회가 모두 COMPLETE 또는 정당한 SKIPPED로 닫혔고 중복·누락·누출·audit missing·rehash mismatch가 0이며 integrity/FK가 정상임
- evidence: run 2f61c1b7-2cb6-4d33-92c8-520691af3e76; COMPLETE 258, SKIPPED 935, FAILED 0; selection 258, identity 148215; signature 1개 max 258, >=50 1, >=200 1; DB SHA e2f7b6291bc3d0ecea6a170eda11bc47f04aa65cb9686d556ebd6b1b12f61740; report SHA 1f77cc0c3553e6920ea7d6e2ccf087853c904efd602d3e326280ec48e49e51c8
- affected_files: v27_storage/backtests/p45_v274_pair_walkforward_v12.sqlite3; completion verification report; state files
- affected_schema: dedicated schema2743 only; operating schema273 unchanged
- previous_rule: PAIR_V12_WALKFORWARD_PREFLIGHT_READY; FULL run not recorded complete
- new_rule: PAIR_V12_WALKFORWARD_COMPLETE; aggregation not started
- allowed_next_action: PAIR v1.2 최종 aggregation을 별도 승인 후 수행
- forbidden_actions: ['PAIR_FINAL_AGGREGATION_WITHOUT_USER_APPROVAL', 'OPERATING_PAIR_INSERT', 'RAW_V11_RUN_REUSE', 'FINAL_SIX']
- approval_source: USER
- decision_hash: 1e35a58008c504c9e633a9aa3bd9435fc86fa324f88e66a052c0ffed6cdd1613

## DECISION-20260811-048
- timestamp: 2026-08-11T18:12:17+09:00
- project_version: P45 v2.7.4
- stage: PAIR FINAL AGGREGATION
- category: RESEARCH/PAIR/AGGREGATION
- decision: 공식 PAIR v1.2 WALKFORWARD run만 사용한 최종 집계를 완료하고 1236회 PAIR 10개를 모두 PAIR_RESEARCH_HOLD로 확정했다.
- reason: 공식 258 selection exposure의 분리 통계와 1236 pre-result context에 v2.7.4 관문을 적용했으며 기준 완화 없이 READY와 TEST_READY가 0개였다.
- evidence: aggregation hash b9403f1ce2b416ca1b4256b4d7c6e4c58f6e8fa593e7c6ccc19a1d0a1b584453; report SHA f7a705a6d0684e0cc2137c99691f692583930dd0ad543a6f61404a0e23f1c1b6; integrity ok; FK 0; future leak 0
- affected_files: src/p45_v27/pairs/final_aggregation.py; src/p45_v27/pair_final_aggregation.py; dedicated aggregation DB/report
- affected_schema: dedicated aggregation schema only; operating schema unchanged
- previous_rule: PAIR_V12_WALKFORWARD_COMPLETE
- new_rule: PAIR_V12_FINAL_AGGREGATION_COMPLETE
- allowed_next_action: PAIR v1.2 최종 연구 결과 승인 및 CORE 단계 진행 여부 결정
- forbidden_actions: FINAL_SIX; UI; OPERATING_PAIR_INSERT; OFFICIAL_LOCK; AUDIT_RUN; RULE_RELAXATION
- approval_source: 사용자 명시 승인
- decision_hash: c85db53d3aa7f77859eb2c9834caf54ebab11233d4b7f66dfe6d74079b437cb1

## DECISION-20260811-049
- timestamp: 2026-08-11T18:19:16+09:00
- project_version: P45 v2.7.4
- stage: RESEARCH ENGINE FREEZE / WEB HANDOFF
- category: OPERATIONS/PROTECTION/HANDOFF
- decision: P45 v2.7.4 연구 엔진을 P45_RESEARCH_ENGINE_FROZEN_WEB_READY 상태로 동결하고 웹프로그램 인계용 운영상태를 확정했다.
- reason: 공식 PAIR 집계에서 valid_for_core가 0이므로 CORE 및 최종 6개를 생성하지 않으며, 진단 결과와 공식 결과를 분리한 상태로 웹 연동한다.
- evidence: PAIR_READY 0; PAIR_TEST_READY 0; PAIR_RESEARCH_HOLD 10; PAIR_SYSTEM_HOLD 0; valid_for_core 0; operating PAIR/CORE/AUDIT 0 rows
- affected_files: P45_FINAL_OPERATION_STATE.md; P45_CURRENT_STATE.md/json; P45_HANDOFF.md; P45_PORTABLE_HANDOFF.zip
- affected_schema: NONE
- previous_rule: PAIR_V12_FINAL_AGGREGATION_COMPLETE
- new_rule: P45_RESEARCH_ENGINE_FROZEN_WEB_READY
- allowed_next_action: WEB PROGRAM INTEGRATION
- forbidden_actions: CORE generation; FINAL_SIX; gate/threshold/signature mutation; WALKFORWARD rerun; arbitrary promotion
- approval_source: 사용자 명시 승인
- decision_hash: 7021efdfc42d148422c17b8a53e16fbcd6062e053e02582d5bd69518e4ab0293

## DECISION-20260811-050
- timestamp: 2026-08-11T18:38:51+09:00
- project_version: P45 v2.7.4
- stage: WEB PROGRAM INTEGRATION V1
- category: IMPLEMENTATION/WEB/READ_ONLY
- decision: 동결된 P45 연구 상태를 단일 읽기 전용 어댑터로 제공하는 최소 반응형 웹프로그램 V1을 완료했다.
- reason: 웹은 CURRENT_STATE와 최종 aggregation 보고서만 읽으며 official_final_numbers는 빈 배열, 진단 PAIR는 DIAGNOSTIC ONLY로 분리한다.
- evidence: adapter tests 2/2 PASS; HTTP 200; POST 405; mobile 360px no horizontal scroll; protected manifest unchanged; operating CORE/AUDIT 0
- affected_files: src/p45_v27/web_adapter.py; src/p45_v27/webapp.py; web/index.html; web/app.js; web/styles.css; P45 시작.cmd
- affected_schema: NONE
- previous_rule: P45_RESEARCH_ENGINE_FROZEN_WEB_READY
- new_rule: P45_WEB_INTEGRATION_V1_READY
- allowed_next_action: 휴대폰 접속 방식 또는 공개 배포 방식 결정
- forbidden_actions: research rule mutation; WALKFORWARD rerun; operating DB write; diagnostic promotion; final six generation
- approval_source: 사용자 명시 승인
- decision_hash: e53bff8dc14cbbb8220fe06fbd1e3a80079e2dd9b5977e7e388c5208102369b7

## DECISION-20260812-051
- timestamp: 2026-08-12T10:34:22+09:00
- project_version: P45 v2.7.4
- stage: WEB PROGRAM UI V2
- category: IMPLEMENTATION/WEB/UI/READ_ONLY
- decision: 첨부 디자인 지침에 맞춰 P45 웹을 다크 네이비·시안·퍼플 연구실 UI V2로 전면 개편하고 PC 및 세 가지 휴대폰 화면을 검증했다.
- reason: 동결 연구 엔진을 수정하지 않고 공식 결과 없음, PAIR 상태, 진단 전용 PAIR 및 역사적 성과를 한 화면에서 명확히 구분한다.
- evidence: adapter tests 2/2 PASS; 1365x900, 360x800, 390x844, 430x932 PASS; horizontal overflow 0; overlap 0; JavaScript errors 0; refresh PASS; protected canonical manifest unchanged; operating CORE/AUDIT 0 rows
- affected_files: src/p45_v27/web_adapter.py; web/index.html; web/app.js; web/styles.css; tests_v27/test_web_integration.py; v27_storage/reports/p45_web_ui_v2_verification.json; P45_FINAL_OPERATION_STATE.md; state files; portable bundle
- affected_schema: NONE
- previous_rule: P45_WEB_INTEGRATION_V1_READY
- new_rule: P45_WEB_UI_V2_READY
- allowed_next_action: 휴대폰 접속 방식 또는 공개 배포 방식 결정
- forbidden_actions: research rule mutation; WALKFORWARD rerun; operating DB write; diagnostic promotion; final six generation
- approval_source: 사용자 명시 승인
- decision_hash: f2fdd881daff7dc42052b6de80499c201679bc10c5c3dcdd1fb8120ef412067f

## DECISION-20260812-052
- timestamp: 2026-08-12T11:28:55+09:00
- project_version: P45 v2.7.4
- stage: WEB PROGRAM UI V2
- category: IMPLEMENTATION/WEB/UI/REFERENCE
- decision: 첨부 HTML 디자인 시안을 P45 공식 데이터 원칙에 맞게 변환하여 좌측 연구 메뉴, 네온 연구 카드, 모바일 상·하단 메뉴 UI로 적용했다.
- reason: 시안의 시각 구조는 반영하되 공식 상태와 충돌하는 예시 추천번호, 확률, 신뢰도는 제거하고 읽기 전용 공식 상태와 진단 전용 자료만 표시한다.
- evidence: web tests 2/2 PASS; PC and 360x800/390x844/430x932 PASS; horizontal overflow 0; JavaScript errors 0; protected manifest unchanged
- affected_files: web/index.html; web/styles.css; web/app.js; p45_web_ui_v2_verification.json; state files; portable bundle
- affected_schema: NONE
- previous_rule: P45_WEB_UI_V2_READY
- new_rule: P45_WEB_UI_V2_READY_REFERENCE_ADAPTED
- allowed_next_action: 휴대폰 접속 방식 또는 공개 배포 방식 결정
- forbidden_actions: research rule mutation; fake official recommendation; operating DB write; final six generation
- approval_source: 사용자 명시 요청
- decision_hash: 4585d3bee906867cb4918b3b43ca33e3ac9e1a8726888ab37c3d4edb3ca83a9f

## DECISION-20260812-053
- timestamp: 2026-08-12T11:58:38+09:00
- project_version: P45 v2.7.4
- stage: WEB STITCH REAL DATA
- category: IMPLEMENTATION/WEB/UI/READ_ONLY
- decision: Stitch 시각 디자인을 실제 P45 읽기 전용 API 데이터와 통합하고 모든 샘플 추천·확률·신뢰도를 제거했다.
- reason: 공식 결과 없음과 진단 전용 TOP3를 명확히 분리하고 진단 6개 집합 및 실제 TRIO A/B 구조를 함께 표시한다.
- evidence: web tests 2/2 PASS; PC and 360/390/430 PASS; fake score 0; range violation 0; JS error 0; horizontal overflow 0; protected manifest unchanged
- affected_files: web/index.html; web/styles.css; web/app.js; state files; portable bundle
- affected_schema: NONE
- previous_rule: P45_WEB_UI_V2_READY
- new_rule: P45_WEB_STITCH_REAL_DATA_READY
- allowed_next_action: 휴대폰 접속 방식 또는 공개 배포 방식 결정
- forbidden_actions: research mutation; DB write; WALKFORWARD; aggregation; CORE promotion; final six
- approval_source: 사용자 명시 승인
- decision_hash: 1abfa6c67e3578f224a68b5587c91dd663058fa408d1b4bf2d1b56351e532064

## DECISION-20260812-054
- timestamp: 2026-08-12T12:07:43+09:00
- project_version: P45 v2.7.4
- stage: WEB LAN MOBILE PREVIEW
- category: IMPLEMENTATION/WEB/LAN/READ_ONLY
- decision: 회원가입과 외부 서비스 없이 같은 Wi-Fi의 휴대폰에서 P45를 확인하는 별도 LAN 미리보기 실행을 완료했다.
- reason: 기존 localhost 실행을 보존하면서 별도 CMD가 현재 LAN IPv4를 자동 감지하고 0.0.0.0:8045 읽기 전용 서버를 시작한다.
- evidence: LAN API HTTP 200; 360/390/430 PASS; horizontal overflow 0; JavaScript error 0; firewall rule not required; no port forwarding or tunnel
- affected_files: P45 휴대폰 미리보기.cmd; p45_lan_mobile_preview_verification.json; state files; portable bundle
- affected_schema: NONE
- previous_rule: P45_WEB_STITCH_REAL_DATA_READY
- new_rule: P45_LAN_MOBILE_PREVIEW_READY
- allowed_next_action: same-Wi-Fi phone preview
- forbidden_actions: internet publishing; port forwarding; tunnel; research mutation; DB write
- approval_source: 사용자 명시 승인
- decision_hash: 1ade68ae5c7c22508ed708423fe30dc2b6cfffad66bce5ffc14d04237b521f9c

## DECISION-20260812-055
- timestamp: 2026-08-12T13:28:22+09:00
- project_version: P45 v2.7.4
- stage: NEW DRAW OPERATION AUTOMATION V1
- category: IMPLEMENTATION/OPERATIONS/DRAW_UPDATE/FROZEN_ENGINE
- decision: 동행복권 공식 새 회차를 자동 확인·검증하고 별도 운영 저장소에서 직전 예측 복기와 다음 회차 사전 상태 생성을 수행하는 P45_NEW_DRAW_UPDATE_V1을 운영 적용했다.
- reason: 사용자 수동 번호 입력 없이 공식 결과를 안전하게 반영하되 동결 연구자료와 규칙은 수정하지 않고 실패 시 기존 정상 상태를 보존하기 위함이다.
- evidence: official draw 1236 main 12,18,21,29,34,38 bonus 10; validation PASS; duplicate rerun DRAW_ALREADY_CURRENT; evaluation rows 10; analysis round 1237; valid_for_core 0; API fields PASS; protected canonical manifest unchanged
- affected_files: src/p45_v27/draw_update.py; src/p45_v27/web_adapter.py; tests_v27/test_draw_update.py; P45 회차 업데이트.cmd; v27_storage/live; state files; portable bundle
- affected_schema: P45 live operational schema v1 only; research schema 273/2743 unchanged
- previous_rule: P45_LAN_MOBILE_PREVIEW_READY
- new_rule: P45_NEW_DRAW_UPDATE_V1_READY
- allowed_next_action: next official draw update or web display verification
- forbidden_actions: research rule mutation; threshold relaxation; signature/context change; historical walkforward rerun; diagnostic promotion; forced CORE; fake draw
- approval_source: 사용자 명시 승인
- decision_hash: 5d0cc060b865b0d249db13b8b3d8dd76809e6b49bff9c7bd678a0c1a85d0c3cc

## DECISION-20260812-056
- timestamp: 2026-08-12T13:39:34+09:00
- project_version: P45 v2.7.4
- stage: WEEKLY AUTO DRAW UPDATE
- category: IMPLEMENTATION/OPERATIONS/WINDOWS_SCHEDULER
- decision: Windows 작업 스케줄러에 P45 Weekly Draw Update를 현재 사용자 일반 권한으로 등록하고 토요일 22:30 1차 및 일요일 09:00 백업 확인을 자동화했다.
- reason: 사용자 수동 실행 없이 새 공식 회차를 확인하면서 놓친 예약은 가능한 즉시 실행하고 동일 작업 중복 실행 및 동일 회차 중복 저장을 차단하기 위함이다.
- evidence: two weekly triggers exact 22:30:00 and 09:00:00; StartWhenAvailable true; MultipleInstances IgnoreNew; RunLevel Limited; manual scheduled run result 0; DRAW_ALREADY_CURRENT; duplicate draw rows 0; protected canonical manifest unchanged
- affected_files: P45 회차 업데이트.cmd; P45 자동업데이트 설치.ps1; P45 자동업데이트 설치.cmd; P45 자동업데이트 삭제.cmd; Windows scheduled task P45 Weekly Draw Update; state files; portable bundle
- affected_schema: NONE
- previous_rule: P45_NEW_DRAW_UPDATE_V1_READY
- new_rule: P45_WEEKLY_AUTO_DRAW_UPDATE_READY
- allowed_next_action: automatic weekly execution or schedule removal using the dedicated delete CMD
- forbidden_actions: other Windows task mutation; research rule mutation; threshold/signature/context change; historical walkforward rerun; forced CORE; duplicate draw insertion
- approval_source: 사용자 명시 승인
- decision_hash: 2e046b0c56c26e4e48d46c359505201156d52c3270fb4a2b12ceb84f9cd09bf6

## DECISION-20260812-057
- timestamp: 2026-08-12T13:48:47+09:00
- project_version: P45 v2.7.4
- stage: WEB DIAGNOSTIC RANK1 UI
- category: IMPLEMENTATION/WEB/UI/READ_ONLY
- decision: 웹 진단 영역에서 TOP3 카드 표시를 제거하고 API의 DIAGNOSTIC RANK 1 PAIR만 TRIO A와 TRIO B 두 줄로 표시하도록 단순화했다.
- reason: 내부 TOP3 연구자료를 보존하면서 일반 화면에서는 가장 우선인 진단 PAIR의 실제 두 TRIO 구조만 명확히 보여주기 위함이다.
- evidence: API diagnostic_top_pairs 3 retained; UI cards 1; TRIO rows 2; combined six-number row 0; PC and 360/390/430 overflow 0; JavaScript errors 0; protected canonical manifest unchanged
- affected_files: web/index.html; web/app.js; web/styles.css; state files; portable bundle
- affected_schema: NONE
- previous_rule: P45_WEEKLY_AUTO_DRAW_UPDATE_READY
- new_rule: P45_WEB_DIAGNOSTIC_RANK1_READY
- allowed_next_action: continue automatic draw operations and read-only web display
- forbidden_actions: research engine mutation; DB mutation; diagnostic calculation change; API TOP3 deletion; hardcoded diagnostic numbers; forced official promotion
- approval_source: 사용자 명시 승인
- decision_hash: 7ace4317b5ca1c7d18070784e313611b4ed71dbe7508a3b72377ade78a538173

## DECISION-20260812-058
- timestamp: 2026-08-12T14:02:47+09:00
- project_version: P45 v2.7.4
- stage: WEB DATA CONSISTENCY
- category: IMPLEMENTATION/WEB/CONSISTENCY/READ_ONLY
- decision: localhost 전용 구형 서버와 LAN 전용 최신 서버가 동시에 8045를 점유하던 구성을 제거하고, 단일 0.0.0.0 서버가 localhost와 LAN 모두에 동일한 API와 화면을 제공하도록 고정했다.
- reason: 화면 크기나 접속 주소와 무관하게 현재 DIAGNOSTIC RANK 1과 출처·상태 버전이 완전히 같아야 하기 때문이다.
- evidence: duplicate listeners 2 to 1; localhost/LAN /api/status byte-equivalent; draw 1237; TRIO A 11,26,37; TRIO B 8,19,24; PAIR_SYSTEM_HOLD; static asset version v31; no-store cache; hardcoded/fallback/sample diagnostic numbers 0; protected canonical manifest unchanged
- affected_files: src/p45_v27/webapp.py; P45 시작.cmd; web/index.html; state files; portable bundle
- affected_schema: NONE
- previous_rule: P45_WEB_DIAGNOSTIC_RANK1_READY
- new_rule: P45_WEB_DATA_CONSISTENCY_FIXED
- allowed_next_action: continue automatic draw operations and read-only web display
- forbidden_actions: research engine mutation; DB mutation; diagnostic calculation change; duplicate web server; hardcoded diagnostic numbers; forced official promotion
- approval_source: 사용자 명시 승인
- decision_hash: 361600660e3a3ff991fcec19ebc000df4be854715d06c7ec43f2b9e465348ba3

## DECISION-20260812-059
- timestamp: 2026-08-12T15:15:13+09:00
- project_version: P45 v2.7.4
- stage: PROJECT FILE CLEANUP
- category: OPERATIONS/PROTECTION/CLEANUP
- decision: 실행·상태·공식문서·보호 Manifest 참조를 전수 확인하고, 참조 0이며 공식본이 별도 존재하는 PAIR Amendment Review Matrix 1개만 삭제했다. 과거 연구 폴더와 나머지 초안·검토본은 보호 또는 상태 참조 때문에 보존했다.
- reason: 실제 당첨결과와 연구 장부를 손상시키지 않으면서 명백히 불필요한 중복 검토 파일만 제거하기 위함이다.
- evidence: deleted 1 file/3092 bytes; deleted folders 0; web and /api/status PASS; draw updater status DRAW_ALREADY_CURRENT; scheduled task retained; active DB integrity ok/FK 0; canonical protected hash unchanged 7c1458328a17a0824622c00ce1f54996e22ed4c2e9d04180be4ad9029ba8febb
- affected_files: P45_v2.7.4_PAIR_Amendment_Review_Matrix.md deleted; state files; portable bundle
- affected_schema: NONE
- previous_rule: P45_WEB_DATA_CONSISTENCY_FIXED
- new_rule: P45_CLEANUP_COMPLETE
- allowed_next_action: continue automated draw operations and read-only web display
- forbidden_actions: research rule mutation; research result deletion; draw data deletion; DB mutation; protected path deletion; unreviewed draft deletion
- approval_source: 사용자 명시 승인
- decision_hash: 14e0ac95857b76bc5464414d4dda4ddbc19971a9341209861fe9386d7659253b

## DECISION-20260814-060
- timestamp: 2026-08-14T15:07:00+09:00
- project_version: P45 v2.7.4
- stage: RESEARCH_REVIEW_HARDENING
- category: GOVERNANCE_PROTECTION_RESEARCH_REVIEW
- decision: 외부 AI 검토 의견은 P45의 기존 연구 목적과 공식 규칙을 기준으로 심사하며, 도움이 되는 제안만 범위를 제한해 수용하고 핵심 기준과 충돌하는 제안은 거부한다. 요약 누락을 새 규칙으로 보충하지 않고 성과보다 신뢰성·재현성·누수 방지를 우선한다.
- reason: 동결 연구 엔진을 변경하지 않고 외부 검토를 일관되게 심사하고, 확인된 운영 안전성과 미확인 전이를 명확히 구분하기 위함.
- evidence: 공식 v2.7.1/v2.7.2/v2.7.4 문서와 Timing/Sequence/Signature PATCH, src/p45_v27 UNIT/NUMBER/PAIR/CORE/AUDIT 저장 코드를 대조했고 6개 research_review 문서에 근거와 판정을 기록함.
- affected_files: 00_P45_STATE/research_review/*.md; P45_CURRENT_STATE.md/json; P45_HANDOFF.md; P45_DECISION_LOG.md; portable handoff
- affected_schema: none
- previous_rule: 외부 AI 검토에 대한 단일 통합 운영 요약 문서 없음
- new_rule: 기존 공식 규칙 우선, 연구 의미 변경은 승인 gate, 성과보다 재현성·누수 방지 우선
- allowed_next_action: DOCUMENT_ONLY; unresolved implementation requires explicit research-rule/change approval review
- forbidden_actions: ['FROZEN_ENGINE_CHANGE', 'THRESHOLD_OR_GATE_CHANGE', 'HISTORICAL_WALKFORWARD_RERUN', 'AGGREGATION_RERUN', 'CORE_FORCE_PROMOTION']
- approval_source: USER_EXPLICIT_REQUEST
- decision_hash: 8a4339152a7d9e775f0c6a53bd4b20bdb57952b8060bda10394e84b5ea080901

## DECISION-20260816-061
- timestamp: 2026-08-16T13:25:38+09:00
- project_version: P45 v2.7.4
- stage: WEB_OPERATIONS
- category: OPERATIONS_LAUNCHER_REPAIR
- decision: P45 데스크톱 실행 CMD를 ASCII 명령과 CRLF 줄바꿈으로 복구하고 localhost 127.0.0.1:8045 단일 서버 및 중복 실행 방지를 검증했다.
- reason: 기존 LF/no-BOM 한글 배치 파일이 Windows cmd에서 명령 단위로 잘못 해석될 수 있었고 중복 서버 방지 검사가 없었다.
- evidence: 실제 cmd.exe 호출 exit 0, HTTP 200, /api/status PASS, 8045 LISTENING PID 1개, protected canonical hash 동일.
- affected_files: P45 시작.cmd; P45 휴대폰 미리보기.cmd encoding only; state files; portable handoff
- affected_schema: none
- previous_rule: P45 시작.cmd UTF-8 no BOM/LF and no duplicate-server check
- new_rule: ASCII no-BOM CRLF localhost launcher with API health check and single-server protection
- allowed_next_action: KEEP
- forbidden_actions: ['RESEARCH_ENGINE_CHANGE', 'RESEARCH_DB_CHANGE', 'RULE_CHANGE', 'WALKFORWARD_RERUN']
- approval_source: USER_EXPLICIT_REQUEST
- decision_hash: ebf60ac504b7d70b9cabfa1f6240e12480b7b0bdb6302dcf31e27cda9e8e2272

## DECISION-20260816-062
- timestamp: 2026-08-16T15:03:10+09:00
- project_version: P45 v2.7.4
- stage: EXPERIMENT_LAB_STAGE_1_GOVERNANCE_AND_REGISTRY_DESIGN
- category: GOVERNANCE_PROTECTION_EXPERIMENT
- decision: P45 EXPERIMENT LAB Stage 1 거버넌스와 Registry 설계를 승인하고 DRAW, CROWD, PRIZE_SHARE 연구영역을 공식 엔진과 분리한다.
- reason: 신규 연구를 결과에 맞춰 변경하거나 성공 사례만 보존하는 위험 없이 등록, 검증, 실패 보존, 승격후보화하기 위함이다.
- evidence: 00_P45_STATE/experiment_lab/01_EXPERIMENT_LAB_GOVERNANCE.md; 02_EXPERIMENT_REGISTRY_SCHEMA.md; 03_EXPERIMENT_STATUS_TRANSITION.md; 04_EXPERIMENT_PROMOTION_POLICY.md; 05_EXPERIMENT_FAILURE_AND_NEGATIVE_RESULT_POLICY.md; 06_INITIAL_EXPERIMENT_REGISTRY.md; research_inventory/06_P45_CROWD_PRIZE_SHARE_RESEARCH_DESIGN.md
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 EXPERIMENT LAB Stage 1 거버넌스와 Registry 설계를 승인하고 DRAW, CROWD, PRIZE_SHARE 연구영역을 공식 엔진과 분리한다.
- allowed_next_action: EXPERIMENT_PROTOCOL_DESIGN_REQUIRES_SEPARATE_APPROVAL
- forbidden_actions: ['EXPERIMENT_CALCULATION_WITHOUT_APPROVAL', 'EXPERIMENT_AUTOMATIC_OFFICIAL_PROMOTION', 'DRAW_CROWD_PRIZE_SCORE_MERGE', 'OFFICIAL_ENGINE_MUTATION', 'RESULT_AWARE_PROTOCOL_CHANGE']
- approval_source: USER_EXPLICIT_APPROVAL
- decision_hash: 0acad92c228924bd76798eac4507f288961f191c70be1e3df2da522ad75da0be

## DECISION-20260816-063
- timestamp: 2026-08-16T15:09:43+09:00
- project_version: P45 v2.7.4
- stage: EXPERIMENT_LAB_EXP001_PREREGISTRATION_DESIGN
- category: EXPERIMENT_GOVERNANCE_PROTECTION
- decision: EXP-001 숫자 동시출현 관계망의 사전등록 설계를 승인 범위대로 완성하고 Registry 상태를 REGISTERED에서 DESIGNED로 전환한다.
- reason: 실제 결과를 보기 전에 연구질문, MAIN/INTEGRATED 분리, 지표, null, 다중검정, walkforward, 성공·실패 기준을 고정하기 위함이다.
- evidence: 00_P45_STATE/experiment_lab/EXP-001_NUMBER_COOCCURRENCE/EXP001_01_PREREGISTRATION.md through EXP001_05_SUCCESS_FAILURE_CRITERIA.md
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: EXP-001 숫자 동시출현 관계망의 사전등록 설계를 승인 범위대로 완성하고 Registry 상태를 REGISTERED에서 DESIGNED로 전환한다.
- allowed_next_action: EXP001_PROTOCOL_LOCK_AND_BACKTEST_IMPLEMENTATION_REQUIRES_SEPARATE_APPROVAL
- forbidden_actions: ['EXP001_BACKTEST_WITHOUT_SEPARATE_APPROVAL', 'EXP001_RESULT_LOOKUP_DURING_DESIGN', 'EXP001_PROTOCOL_CHANGE_AFTER_OUTCOME', 'EXP001_AUTOMATIC_OFFICIAL_PROMOTION', 'EXP001_RECOMMENDATION_GENERATION']
- approval_source: USER_EXPLICIT_APPROVAL
- decision_hash: f715bde278b076bea0a4a8c780eddd4e48c6642da12126b4616380a2cba93131

## DECISION-20260816-064
- timestamp: 2026-08-16T15:16:14+09:00
- project_version: P45 v2.7.4
- stage: RESEARCH_MEMORY_GOVERNANCE
- category: GOVERNANCE_PROTECTION_HANDOFF
- decision: P45를 지속적인 연구소로 운영하고 중요한 연구 아이디어·목적·경계·실패·누락·미완료 연구를 대화에만 남기지 않고 성격별 공식 보존 위치에 기록한다.
- reason: 공식 엔진 미구현을 이유로 과거 연구 아이디어가 사라지는 것을 방지하고 향후 누락 복구 감사를 가능하게 하기 위함이다.
- evidence: P45_START_HERE.md; P45_CAPTURE_POLICY.md; research_inventory/07_HISTORICAL_IDEA_RECOVERY_AUDIT_TODO.md
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45를 지속적인 연구소로 운영하고 중요한 연구 아이디어·목적·경계·실패·누락·미완료 연구를 대화에만 남기지 않고 성격별 공식 보존 위치에 기록한다.
- allowed_next_action: CURRENT_APPROVED_NEXT_ACTION_UNCHANGED; HISTORICAL_IDEA_RECOVERY_AUDIT_REQUIRES_SEPARATE_APPROVAL
- forbidden_actions: ['IMPORTANT_RESEARCH_MEMORY_LEFT_CHAT_ONLY', 'MISSING_IDEA_AUTOMATIC_OFFICIAL_PROMOTION', 'HISTORICAL_IDEA_RECOVERY_WITHOUT_SEPARATE_APPROVAL', 'OFFICIAL_ENGINE_MUTATION']
- approval_source: USER_EXPLICIT_PRESERVATION_REQUEST
- decision_hash: 6c4891eb0573eb11d30663b67f6a43cf6ac5c0c660f47eb597a1f9e869b9e570

## DECISION-20260816-065
- timestamp: 2026-08-16T15:32:55+09:00
- project_version: P45 v2.7.4
- stage: HISTORICAL_IDEA_RECOVERY_AUDIT
- category: RESEARCH_MEMORY_GOVERNANCE
- decision: P45 과거 아이디어 복구 감사를 완료하고 복구·부분복구·역사적 폐기 항목을 별도 장부로 보존한다. 복구 항목은 기존 Inventory/Registry나 공식 엔진에 자동 승격하지 않는다.
- reason: 현재 86개 Research Inventory와 44개 Experiment Registry가 완전하다고 가정하지 않고 구버전·상태·연구 문서의 아이디어 흔적을 대조해 누락을 보존하기 위해서다.
- evidence: research_inventory/07_HISTORICAL_IDEA_RECOVERY_AUDIT.md; research_inventory/08_RECOVERED_HISTORICAL_IDEAS.md; research_inventory/09_HISTORICAL_IDEA_CROSSCHECK_MATRIX.md
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45 과거 아이디어 복구 감사를 완료하고 복구·부분복구·역사적 폐기 항목을 별도 장부로 보존한다. 복구 항목은 기존 Inventory/Registry나 공식 엔진에 자동 승격하지 않는다.
- allowed_next_action: RECOVERED_IDEA_ADD_CANDIDATE_REVIEW_REQUIRES_SEPARATE_APPROVAL
- forbidden_actions: ['OFFICIAL_ENGINE_CHANGE', 'AUTOMATIC_EXPERIMENT_REGISTRATION', 'BACKTEST_EXECUTION', 'GATE_OR_THRESHOLD_CHANGE']
- approval_source: USER_EXPLICIT_APPROVAL_2026-08-16
- decision_hash: c4a817e0ffafb6adc1c826fa0534d5029090be36563133cfdffd43cf889a9661

## DECISION-20260816-066
- timestamp: 2026-08-16T15:38:49+09:00
- project_version: P45 v2.7.4
- stage: HISTORICAL_IDEA_RECOVERY_FINAL_INTEGRATION
- category: RESEARCH_INVENTORY_GOVERNANCE
- decision: 역사 아이디어 복구 감사를 최종 종결하고 선정 안정성 감사를 Research Inventory 87번 PARTIAL 공식 감사 연구로 복구하며, 부분 포착 6건은 기존 항목 의미만 보강한다. 신규 Experiment는 등록하지 않는다.
- reason: 선정 안정성 감사는 v2.7.1에 이미 존재하는 공식 연구이므로 중복 Experiment가 아니며, 나머지 여섯 의미도 기존 연구 질문 안에서 보존 가능하기 때문이다.
- evidence: research_inventory/01_P45_FULL_RESEARCH_INVENTORY.md; 02_P45_RESEARCH_STATUS_MATRIX.md; 03_P45_MISSING_AND_PARTIAL_RESEARCH.md; 07_HISTORICAL_IDEA_RECOVERY_AUDIT.md; experiment_lab/06_INITIAL_EXPERIMENT_REGISTRY.md
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: 역사 아이디어 복구 감사를 최종 종결하고 선정 안정성 감사를 Research Inventory 87번 PARTIAL 공식 감사 연구로 복구하며, 부분 포착 6건은 기존 항목 의미만 보강한다. 신규 Experiment는 등록하지 않는다.
- allowed_next_action: EXP001_PROTOCOL_LOCK_AND_BACKTEST_IMPLEMENTATION_REQUIRES_SEPARATE_APPROVAL
- forbidden_actions: ['ADDITIONAL_HISTORICAL_FULL_AUDIT', 'BACKTEST_EXECUTION_WITHOUT_APPROVAL', 'AUTOMATIC_EXPERIMENT_REGISTRATION', 'OFFICIAL_ENGINE_CHANGE', 'GATE_OR_THRESHOLD_CHANGE']
- approval_source: USER_EXPLICIT_APPROVAL_2026-08-16
- decision_hash: d0e0ffdaeb2d3e14f11968fd7bacd9f1d15474f3b8dbe97baf66dd1cbe0647ab

## DECISION-20260816-067
- timestamp: 2026-08-16T15:54:22+09:00
- project_version: P45 v2.7.4
- stage: EXPERIMENT_LAB_EXP001_PREPARATION
- category: EXPERIMENT_GOVERNANCE
- decision: EXP-001의 1~1237 데이터 snapshot과 5개 사전등록 문서를 해시 잠금하고, 공식 엔진과 분리된 전용 계산기·빈 저장소의 preflight를 완료하여 READY_FOR_TEST로 전환한다.
- reason: 실제 결과를 보기 전에 데이터 경계, 연구 규칙, 계산·저장 구현을 결정론적으로 고정하고 공식 엔진과의 격리를 검증하기 위해서다.
- evidence: EXP001_PROTOCOL_LOCK.json; EXP001_06_PREPARATION_STATUS.md; v27_storage/experiments/exp001/data/exp001_data_snapshot_manifest.json; exp001_preflight_report.json; tests/test_exp001_preflight.py
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: EXP-001의 1~1237 데이터 snapshot과 5개 사전등록 문서를 해시 잠금하고, 공식 엔진과 분리된 전용 계산기·빈 저장소의 preflight를 완료하여 READY_FOR_TEST로 전환한다.
- allowed_next_action: EXP001_ACTUAL_BACKTEST_REQUIRES_SEPARATE_EXPLICIT_APPROVAL
- forbidden_actions: ['ACTUAL_EXP001_BACKTEST_WITHOUT_APPROVAL', 'ACTUAL_PAIR_RANKING_OR_TOP_PAIR_VIEW', 'RECOMMENDATION_GENERATION', 'OFFICIAL_ENGINE_CONNECTION', 'PROTOCOL_MUTATION_AFTER_RESULT', 'UNIT_NUMBER_TRIO_PAIR_CORE_CHANGE']
- approval_source: USER_EXPLICIT_APPROVAL_2026-08-16
- decision_hash: 3b799cad235991de68a66206acc5b2d0f1e9533ff48451609ce048ec151dbe92

## DECISION-20260816-068
- timestamp: 2026-08-16T16:36:23+09:00
- project_version: P45 v2.7.4
- stage: EXPERIMENT_LAB_EXP001_LOCKED_RUN
- category: EXPERIMENT_RESULT
- decision: EXP-001 단일 봉인 실행의 회고검증과 사전등록 워크포워드를 완료하고, 정적 MAIN 신호와 워크포워드 재현이 없어 FAILED/D로 판정한 negative result를 영구 보존한다.
- reason: 잠긴 1~1237 데이터와 프로토콜로 990개 pair, null 통제 및 501~1237 워크포워드를 완료했으며 Holm/maxT 공식 관문과 재현 기준을 충족한 pair가 0개였다.
- evidence: EXP001_07_LOCKED_RUN_RESULT.md; run_id 6cb93fa4-2d29-4deb-8229-c7febcac0255; exp001_research.sqlite3 SHA-256 bc20ae1e80c05297485a3f0fb9d98946eda94c2b54d1fc3865be992b0a52c6fd
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: EXP-001 단일 봉인 실행의 회고검증과 사전등록 워크포워드를 완료하고, 정적 MAIN 신호와 워크포워드 재현이 없어 FAILED/D로 판정한 negative result를 영구 보존한다.
- allowed_next_action: SELECT_NEXT_EXPERIMENT_FOR_PREREGISTRATION_REVIEW
- forbidden_actions: ['EXP001_OFFICIAL_PROMOTION', 'EXP001_PAIR_AS_NUMBER_RECOMMENDATION', 'OFFICIAL_ENGINE_CHANGE', 'THRESHOLD_RELAXATION', 'RESULT_DRIVEN_PROTOCOL_CHANGE', 'AUTOMATIC_NEXT_EXPERIMENT_START']
- approval_source: USER_EXPLICIT_APPROVAL
- decision_hash: a691c3d68d68871d1d0ba8f41085cf39fa22ea16e1f65f617a8dcb2ddefa4a95

## DECISION-20260816-069
- timestamp: 2026-08-16T17:36:22+09:00
- project_version: P45 v2.7.4
- stage: EXPERIMENT_LAB_EXP002_DESIGN
- category: EXPERIMENT_GOVERNANCE_AND_DESIGN
- decision: P45의 빈번한 NO-PICK을 단순 정상으로 넘기지 않고 연구 대상으로 보존하되 공식 gate를 완화하지 않는다. 43~1235 coverage 감사를 완료하고 EXP-002 NO-PICK COVERAGE & QUALIFIED RESEARCH FALLBACK을 별도 실험으로 등록·사전설계한다.
- reason: warmup 제외 유효 867회에서 공식 출력 가능 0회와 RESEARCH_NO_PICK 867회가 확인되어, 강제 출력이 아닌 검증 가능한 별도 fallback 연구가 필요하다.
- evidence: EXP002_07_NO_PICK_COVERAGE_AUDIT.md; audit hash 26718433a8ceeba2545ac01e8757841290b61504c5736c539f25ceaf046cb0a2; focused preflight 12/12 PASS
- affected_files: state files
- affected_schema: none
- previous_rule: unspecified
- new_rule: P45의 빈번한 NO-PICK을 단순 정상으로 넘기지 않고 연구 대상으로 보존하되 공식 gate를 완화하지 않는다. 43~1235 coverage 감사를 완료하고 EXP-002 NO-PICK COVERAGE & QUALIFIED RESEARCH FALLBACK을 별도 실험으로 등록·사전설계한다.
- allowed_next_action: EXP002_PROTOCOL_LOCK_AND_BACKTEST_APPROVAL
- forbidden_actions: ['EXP002_ACTUAL_BACKTEST_WITHOUT_EXPLICIT_APPROVAL', 'EXP002_FALLBACK_AS_OFFICIAL_PICK', 'OFFICIAL_GATE_RELAXATION', 'OFFICIAL_THRESHOLD_RELAXATION', 'ROUND1238_SPECIAL_RULE', 'HOLD_AUTO_PROMOTION', 'OFFICIAL_ENGINE_CHANGE', 'AUTOMATIC_NEXT_EXPERIMENT_START']
- approval_source: USER_EXPLICIT_APPROVAL
- decision_hash: cc4f2287ee8050f5cd4785675a850f6bbb3a2cfe584d55ac92cefd939ce375fe

## DECISION-20260816-070
- timestamp: 2026-08-16T19:51:30+09:00
- project_version: P45 v2.7.4
- stage: EXPERIMENT_LAB_EXP002_PROTOCOL_BLOCKED
- category: EXPERIMENT_PROTOCOL_CONFLICT
- decision: EXP-002 봉인 RUN은 NUMBER_HOLD를 허용한 source pool과 공식 TRIO ranking의 NUMBER_HOLD 미정의가 충돌하여 PROTOCOL_BLOCKED로 중단한다. 임의 순위나 상태 승격 없이 부분 결과를 무효 evidence로 보존한다.
- reason: 평가회차 964의 사전 prediction 단계에서 공식 trio_engine.NUMBER_RANK가 NUMBER_HOLD를 처리하지 못해 KeyError가 발생했다. 임의 순위를 추가하면 사전등록 이후 규칙 변경이므로 금지된다.
- evidence: EXP002_08_PROTOCOL_BLOCKED_RUN.md; run_id 95a29030-3ec3-435b-9696-e869c69c456f; prediction locks 595; outcomes 290; final judgment rows 0
- affected_files: EXP-002 isolated code, protocol lock, state files, EXP-002 research DB only
- affected_schema: EXP-002 schema 2002 only
- previous_rule: EXP-002 source pool permits NUMBER_HOLD and requires official TRIO 15-key ranking
- new_rule: No rule change. Protocol remains blocked pending separately approved HOLD ranking semantics or source-pool revision.
- allowed_next_action: EXP002_PROTOCOL_REVISION_REVIEW
- forbidden_actions: ['PARTIAL_RESULT_PERFORMANCE_USE', 'EXP002_OFFICIAL_PROMOTION', 'HOLD_IMPLICIT_RANK', 'HOLD_TO_TEST_OR_PASS', 'OFFICIAL_ENGINE_CHANGE', 'AUTOMATIC_EXP003_START']
- approval_source: USER_EXPLICIT_SINGLE_RUN_APPROVAL_WITH_FAIL_FAST_PROTOCOL_BLOCK
- decision_hash: 83c328ff2e6ece8305a7a9cb82968384846b6088f2e58e2987a081aac479ce64

## DECISION-20260816-071
- timestamp: 2026-08-16T20:22:20+09:00
- project_version: P45 v2.7.4
- stage: EXPERIMENT_LAB_EXP002_V2_LOCKED_RUN
- category: EXPERIMENT_RESULT
- decision: EXP-002 V2는 공식 NUMBER 14-key 상위 6개를 3+3으로 분할하는 별도 봉인 protocol로 검증했으며 coverage는 47.52%로 증가했지만 MAIN PRIMARY가 random 우위를 보이지 않아 FAILED/B로 판정한다.
- reason: 412회 fallback 중 MAIN 3/3은 1회(0.2427%)로 random baseline 0.2819%보다 낮고 exact p=0.6874, permutation p=0.7365였다. 따라서 coverage 증가는 성과 우위가 아니다.
- evidence: EXP002V2_06_LOCKED_RUN_RESULT.md; run_id e7049813-6e76-406a-9c0e-c599fc031c55; DB SHA-256 d8ef536a6fb421f72b84406148b36fdbe0ca85438eace25069c1916964d6e17d
- affected_files: EXP-002 V2 isolated protocol, code, DB, registry and state files
- affected_schema: experimental schema 2003 only
- previous_rule: EXP-002 V1 PROTOCOL_BLOCKED; no V2 result
- new_rule: No official rule change. EXP-002 V2 negative result is preserved and not promoted.
- allowed_next_action: REVIEW_EXP002_V2_NEGATIVE_RESULT_ONLY
- forbidden_actions: ['EXP002_V2_OFFICIAL_PROMOTION', 'ROUND1238_FORWARD_PICK', 'RESULT_DRIVEN_V2_RETUNING', 'OFFICIAL_GATE_CHANGE', 'OFFICIAL_ENGINE_CHANGE', 'AUTOMATIC_EXP003_START']
- approval_source: USER_EXPLICIT_SINGLE_LOCKED_RUN_APPROVAL
- decision_hash: 4096766720a9785b0950ffc81eec4d057360bf60b1faf173a31e8c9a0433b0d7

## DECISION-20260816-072
- timestamp: 2026-08-16T20:38:01+09:00
- project_version: P45 v2.7.4
- stage: EXPERIMENT_LAB_EXP003_PREPARATION
- category: EXPERIMENT_PROTOCOL_LOCK
- decision: EXP-002 V1은 PROTOCOL_BLOCKED 무효 종료, V2는 FAILED/COVERAGE_ONLY로 종료하고 재조정하지 않는다. EXP-003은 기존 숫자 이동 구조 ID를 중복 발급 없이 NUMBER 1-STEP TRANSITION / ROUND TRACE로 구체화하여 결과 전 protocol을 봉인하고 계산기·격리 저장소·사전검사까지만 준비한다.
- reason: EXP-002 V2의 coverage 증가는 MAIN PRIMARY random 우위로 재현되지 않았다. 다음 독립 연구는 R-1에서 R로의 1-step 숫자 이동 흔적만 사전정의하여 결과를 보기 전에 고정해야 한다.
- evidence: EXP003_PROTOCOL_LOCK.json; protocol feb78db79d1dbebbfe6f41b097651aa27acdc8b7b7d7d4260e1e6645e6035329; snapshot b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0; focused tests 4/4; preflight 13/13; result rows 0
- affected_files: EXP-003 isolated documents, calculator, storage, snapshot, empty experimental DB, registry and state files only
- affected_schema: experimental schema 3001 only
- previous_rule: EXP-002 V1 PROTOCOL_BLOCKED and EXP-002 V2 FAILED/COVERAGE_ONLY; EXP-DRAW-20260816-010-V1 registered as generic 숫자 이동 구조
- new_rule: No official rule change. EXP-003 protocol is locked for R-1 to R transition research only and requires separate approval before one actual backtest.
- allowed_next_action: EXP003_ACTUAL_BACKTEST_EXPLICIT_APPROVAL_REQUIRED
- forbidden_actions: ['EXP002_RETUNING', 'EXP002_V3_AUTOMATIC_CREATION', 'EXP003_BACKTEST_WITHOUT_EXPLICIT_APPROVAL', 'EXP003_RESULT_VIEW_BEFORE_LOCK', 'EXP003_RECOMMENDATION_GENERATION', 'OFFICIAL_ENGINE_CHANGE', 'OFFICIAL_GATE_OR_THRESHOLD_CHANGE']
- approval_source: USER_EXPLICIT_EXP002_CLOSE_AND_EXP003_PREPARATION_APPROVAL
- decision_hash: 5dc4b47e6361ab9fd0fb070fb3018098312c9197d7460299af15c08cb9f83e63

## DECISION-20260816-073
- timestamp: 2026-08-16T20:57:34+09:00
- project_version: P45 v2.7.4
- stage: EXPERIMENT_LAB_EXP003_LOCKED_RUN
- category: EXPERIMENT_RESULT
- decision: EXP-003 NUMBER 1-STEP TRANSITION / ROUND TRACE를 봉인 protocol로 정확히 1회 검증했으며 MAIN 거리 45개 중 Holm 및 global maxT를 통과한 거리가 0개여서 FAILED/C로 종료한다.
- reason: 1,236개 R-1→R 전이를 미래누수 없이 검증했으나 관찰상 거리 차이는 다중검정과 100,000회 고정-seed global null 이후 무작위와 구별되지 않았고 기간 방향도 안정적이지 않았다.
- evidence: run_id 14e11ba0-8760-4043-aa36-3d584a95b9cb; Holm 0; maxT 0; distance0 risk difference +0.4207%p, Holm 1.0, maxT 0.999930; DB SHA 571f327cf09e0d6743dd8e23bbadae1fed46c64a12502234974282e9d222a5a0
- affected_files: EXP-003 isolated result DB/JSON/document, registry and state files only
- affected_schema: experimental schema 3001 only
- previous_rule: EXP-003 protocol locked and ready for one backtest; no result
- new_rule: No official rule change. EXP-003 negative result is preserved and cannot be connected to recommendations or the official engine.
- allowed_next_action: REVIEW_EXP003_NEGATIVE_RESULT_ONLY
- forbidden_actions: ['EXP003_RETUNING', 'EXP003_DISTANCE_CHERRY_PICKING', 'EXP003_RERUN', 'EXP003_RECOMMENDATION_CONNECTION', 'EXP003_NUMBER_TRIO_PAIR_CORE_CONNECTION', 'AUTOMATIC_NEXT_EXPERIMENT_START', 'OFFICIAL_ENGINE_CHANGE', 'OFFICIAL_GATE_OR_THRESHOLD_CHANGE']
- approval_source: USER_EXPLICIT_SINGLE_LOCKED_BACKTEST_APPROVAL
- decision_hash: ac09c99a21803b1416d111074776c06e02d3dffc054e697715c38744f7d01b1c

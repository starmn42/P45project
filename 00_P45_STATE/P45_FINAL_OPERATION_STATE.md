# P45 FINAL OPERATION STATE

> 이 문서는 `P45_CURRENT_STATE.json`의 사람이 읽기 쉬운 운영 요약본이다. 독립적인 공식 원본이 아니며 충돌 시 `P45_CURRENT_STATE.json`이 우선한다.

## 프로젝트 및 엔진 상태

- project: P45
- project_version: P45 v2.7.4
- engine_status: P45_RESEARCH_ENGINE_FROZEN_WEB_READY
- research_mode: FROZEN_UNTIL_EXPLICIT_RESUME_DECISION
- web_integration_status: P45_WEB_UI_V2_READY
- web_ui: DARK_NAVY_CYAN_PURPLE_RESPONSIVE_RESEARCH_LAB
- verified_viewports: PC, 360x800, 390x844, 430x932
- next_action: 휴대폰 접속 방식 또는 공개 배포 방식 결정

## 단계별 완료 상태

- UNIT: 완료 — 다섯 필수 단위 및 상태·관계 엔진
- NUMBER: 완료 — 1236회 진단 후보군 12개, NUMBER_PASS 1개
- TRIO: 완료 — 총 220개, TEST 12개, HOLD 208개, valid_for_pair 12개
- PAIR: 완료 — v1.2 WALKFORWARD 및 FINAL AGGREGATION 완료

## 공식 PAIR 식별 규격

- pair_rule_signature: PAIR-RULE-SIGNATURE-1.2
- pair_context_fingerprint: PAIR-CONTEXT-FINGERPRINT-1.0

## 공식 WALKFORWARD

- run_id: 2f61c1b7-2cb6-4d33-92c8-520691af3e76
- evaluation_range: 43~1235
- DB: `E:\P45 프로젝트\v27_storage\backtests\p45_v274_pair_walkforward_v12.sqlite3`
- DB SHA-256: `e2f7b6291bc3d0ecea6a170eda11bc47f04aa65cb9686d556ebd6b1b12f61740`
- selection_exposure: 258

## 공식 FINAL AGGREGATION

- DB: `E:\P45 프로젝트\v27_storage\backtests\p45_v274_pair_v12_final_aggregation.sqlite3`
- DB SHA-256: `f00c1c27e92fc8f551ae4c0de6ae1c8f9c991ac37da155546dfd7eea83c0229a`
- report: `E:\P45 프로젝트\v27_storage\reports\p45_v274_pair_v12_final_aggregation.json`
- report SHA-256: `f7a705a6d0684e0cc2137c99691f692583930dd0ad543a6f61404a0e23f1c1b6`
- aggregation hash: `b9403f1ce2b416ca1b4256b4d7c6e4c58f6e8fa593e7c6ccc19a1d0a1b584453`

### Historical 성능 요약

- Integrated PRIMARY exact 3/3: 1/258, 0.3876%, INFERIOR_TENTATIVE
- Integrated SUPPORT exact 2/3: 44/258, 17.0543%, SUPERIOR_CONFIRMED
- Main PRIMARY exact 3/3: 1/258, 0.3876%, SUPERIOR_TENTATIVE
- Main SUPPORT exact 2/3: 29/258, 11.2403%, SUPERIOR_TENTATIVE
- 3/3 PRIMARY와 exact 2/3 SUPPORT는 합산하지 않는다.

## 현재 1236회 PAIR 상태

- candidate_count: 10
- PAIR_READY: 0
- PAIR_TEST_READY: 0
- PAIR_RESEARCH_HOLD: 10
- PAIR_SYSTEM_HOLD: 0
- valid_for_core: 0

### 진단 상위 PAIR — DIAGNOSTIC ONLY

1. `13-27-45__2-15-31`
2. `13-31-45__2-15-27`
3. `13-31-45__2-19-38`

위 세 항목은 진단 순서일 뿐 공식 추천, CORE 후보 또는 최종 6개가 아니다.

## 공식 출력 상태

- official_core_candidate: NONE
- official_final_six: NONE
- operating_pair_rows: 0
- operating_core_rows: 0
- operating_audit_rows: 0
- web_output_status: RESEARCH_HOLD
- web_public_result: NO_OFFICIAL_NUMBERS
- web_local_url: `http://127.0.0.1:8045/`

웹프로그램은 `공식 결과 없음/RESEARCH_HOLD`와 `DIAGNOSTIC ONLY`를 명확히 구분해야 한다. 진단 PAIR를 공식 추천이나 최종 번호로 표시하면 안 된다.

## 동결 규칙

명시적인 연구 재개 결정 전까지 다음을 금지한다.

- 공식 gate 변경
- threshold 변경
- signature 변경
- 과거 WALKFORWARD 재실행
- 기준 완화 또는 임의 CORE 승격
- 공식 최종 6개 생성

## 상태 및 인수인계 위치

- CURRENT_STATE: `E:\P45 프로젝트\00_P45_STATE\P45_CURRENT_STATE.json`
- CURRENT_STATE 요약: `E:\P45 프로젝트\00_P45_STATE\P45_CURRENT_STATE.md`
- HANDOFF: `E:\P45 프로젝트\00_P45_STATE\P45_HANDOFF.md`
- DECISION LOG: `E:\P45 프로젝트\00_P45_STATE\P45_DECISION_LOG.md`
- Portable Handoff: `E:\P45 프로젝트\00_P45_STATE\P45_PORTABLE_HANDOFF.zip`


# P45 GPT RECOVERY / HANDOFF 039

기준일: `2026-09-02`

## 문서 지위

이 문서는 `P45_GPT_RECOVERY_HANDOFF_038` 이후 확정된 1240 prospective / WEB V1 / 운칠기삼 브랜딩 상태를 반영한 최신 Recovery/Handoff다.

복구 우선순위:

1. 이 latest Recovery/Handoff
2. latest Core Guide
3. latest Research Master
4. Coverage Audit
5. 원본 Result / Registry / Evidence

`P45_NEW_CHAT_START_HERE`는 빠른 안내문이며 Recovery보다 상위 근거가 아니다.

## 1. 현재 단일 운영 루트

- `LOCAL PROJECT = E:\P45 프로젝트`
- `WORK SOURCE = E:\P45 프로젝트`
- `PC START = E:\P45 프로젝트\P45 시작.cmd`
- `PHONE START = E:\P45 프로젝트\P45 휴대폰 미리보기.cmd`
- `P45 HOME = REMOVED / DO NOT USE / DO NOT RECREATE`
- 프로젝트 폴더 구조는 미관을 이유로 이동·숨김·재배치·이름변경하지 않는다.

PC 웹 실행 구조:

`P45 시작.cmd → bundled Python → p45_v27.webapp → 127.0.0.1:8045 → static web + /api/status → browser`

휴대폰/LAN 실행 구조:

`P45 휴대폰 미리보기.cmd → p45_v27.lan_ip → p45_v27.webapp --host 0.0.0.0 --port 8045 → LAN URL`

최근 확인 LAN IP:

`172.30.1.20`

최근 사용 LAN URL:

`http://172.30.1.20:8045/`

주의:
- 휴대폰 미리보기 서버 창을 닫으면 8045 서버도 종료된다.
- 최신 1240 화면의 실제 휴대폰 기기 확인 완료: `DEVICE_SIDE_LATEST_1240 = PASS_PHONE_DEVICE_VERIFIED`.
- 과거 휴대폰 LAN 접속 자체는 실제 기기에서 열린 이력이 있다.

## 2. 프로젝트 불변 원칙

- P45는 단순 번호 생성기가 아니라 구조·전이·관계·복귀·반대가설을 검증하는 연구 시스템이다.
- Official Engine: `FROZEN`.
- `3/3 = PRIMARY`, `exact 2/3 = SUPPORT`.
- PRIMARY와 SUPPORT 성과를 혼합판정하지 않는다.
- NUMBER → TRIO → PAIR → CORE 보호계층을 우회하지 않는다.
- 사용자 명시 승인 없는 gate / threshold / signature / 공식 코드 / 공식 DB / Registry / sealed prospective 변경 금지.
- 미래 데이터 누수, 결과 후 규칙 수정, 사후 threshold 완화, 숨은 점수, 임의 가중치, 실패 삭제, 좋은 결과만 선택 보고 금지.
- 실패·음성 결과를 사후 rescue하지 않는다.
- historical과 prospective를 분리한다.

## 3. 연구 집계 및 현재 핵심 상태

기준 Research Master:

`P45_RESEARCH_MASTER_INDEX_003.md`

현재 집계:

- official internal studies: `12`
- formal Registry physical/version rows: `68 = DRAW 53 + CROWD 9 + PRIZE 6`
- actual executed/completed formal rows: `27`
- protocol/execution blocked: `2`
- closed axis: `1`
- non-EXP executed axes: `28`
- unexecuted reviewed ideas: `2`
- latest numbered experiment: `EXP-020`

현재 주요 연구 상태:

- EXP-017: `FAILED_NOT_SUPPORTED`
- EXP-018 V1: `EXECUTION_BLOCKED_BOOTSTRAP_AMBIGUITY`
- EXP-018 V2: `AXIS_CLOSED_NO_PRACTICALLY_USEFUL_RESIDUAL_NEIGHBOR_EFFECT`
- EXP-019: `FAILED_NOT_SUPPORTED`
- EXP-020: `FAILED_NO_SELECTION_SIGNAL`
- DRAW-ORDER: 정식 EXP 아님 / 미실행 / 보류
- REHEARSAL: EXP-021 아님 / 미실행 / 사용자 패스
- LZ76 macro complexity V1: `FAILED_NOT_SUPPORTED`

NO-PICK:

- `VALID_ROUNDS = 867`
- `OUTPUT_AVAILABLE_ROUNDS = 0`
- `RESEARCH_NO_PICK_ROUNDS = 867`
- `NO_PICK_RATE = 100%`
- 상태: `UNRESOLVED`

공식 gate를 억지로 완화해서 해결하지 않는다.

## 4. 1239 결과 및 prospective 보호

1239 official result:

- MAIN6: `11,13,22,32,33,36`
- BONUS: `8`

1239 TRIO ORBIT settlement:

- Fixed PRIMARY/SUPPORT: `0/1`
- Linked PRIMARY/SUPPORT: `0/0`
- settlement: `COMPLETE`
- sealed original: `UNCHANGED`

1239를 다시 수집·삽입·정산·seal·재생성하지 않는다.

Historical TRIO ORBIT:
- Fixed historical exact3: `5/1237`
- Linked historical exact3: `7/1237`
- Linked 우월성은 지지되지 않았다.

## 5. canonical draw source 상태

canonical live CSV:

`E:\P45 프로젝트\v27_storage\live\p45_live_draws.csv`

canonical draw-result SQLite:

`E:\P45 프로젝트\v27_storage\live\p45_new_draw_update_v1.sqlite3`

현재 확정:

- draw range: `1..1239`
- row count: `1239`
- missing: `0`
- duplicate: `0`
- CSV/SQLite canonical equality: `PASS`

1239 official payload SHA:

`4c0c600801ddeef24d98b54206bac807eaf623c7031bac35c035d4892d6c109a`

Draw updater lifecycle compatibility fix는 완료됐으며 Official Engine 의미 변경은 없었다.

## 6. 1240 TRIO ORBIT prospective — 현재 보호 상태

1240 authoritative prospective protocol은 확인되었고, 정식 preview → seal 절차를 통해 신규 prospective가 봉인됐다.

현재 상태:

- target: `1240`
- result_status: `PENDING`
- prospective_state: `POST_SELECTION_PRE_OUTCOME`
- outcome created: `0`
- duplicate: `0`
- future leakage: `0`
- deterministic repeat: `PASS`

1240 Fixed:

1. `15 31 44`
2. `16 29 45`
3. `17 19 33`

1240 Linked:

1. `15 36 39`
2. `8 35 41`
3. `13 34 37`

Anchors:

`36, 8, 13`

Preview SHA:

`655c4e174723a2467b5ae24c53568a2dff778cdbbbdbce08c589b6f82e3c8e70`

Sealed SHA:

`d8b7f0753500adf7fc62e894b1a8f2a9551f6bb90be0ec92d1fa3480082375fe`

Sealed record:

`E:\P45 프로젝트\v27_storage\prospective\trio_orbit_v1_001\P45_TRIO_ORBIT_TARGET_1240_SEALED_PREDRAW_001.md`

State:

`E:\P45 프로젝트\v27_storage\prospective\trio_orbit_v1_001\P45_TRIO_ORBIT_PROSPECTIVE_STATE_003.json`

1240 결과 발표 전 금지:

- prospective 재생성
- 번호 변경
- sealed record 수정
- 결과 없는 outcome 생성
- 사후 규칙 수정

1240 공식 결과 발표 후에만 sealed 원본과 분리된 절차로 settlement를 수행한다.

## 7. WEB V1 최종 상태

웹 기능 누락의 실제 원인은 다음과 같이 확인·수정됐다.

확정 root causes:

1. 1239 정산 완료 상태를 현재 미래검증 회차로 잘못 표시
2. backend/API의 preview/seal 기능은 존재했지만 frontend action 연결 누락
3. `EXP-017 NOT_CREATED` stale hardcoding
4. 외부 1239 정산 후 prospective manifest 미동기화로 write safety 차단
5. 운칠기삼 UI 누락
6. 휴대폰 CMD inline Python quoting/path 문제
7. append-only 1239 기록의 화면 projection 중복 표시

완료된 웹 수정:

- 1239 완료 기록과 current prospective lifecycle 분리
- 1240 preview API frontend 연결
- 1240 seal API frontend 연결
- current prospective target = 1240 표시
- 1239는 `미래검증 정산 완료 기록`으로 분리 표시
- stale EXP-017 표시 제거
- latest EXP = `EXP-020 / 선택 신호 없음`
- append-only 원본을 건드리지 않고 화면 projection에서 회차별 최신 행 표시
- LAN IP 동적 탐지
- 휴대폰 CMD quoting/path 수정
- PC/LAN web 실행 정상화

WEB acceptance:

- PC: `PASS`
- Backend: `PASS`
- Frontend: `PASS`
- API: `HTTP 200`
- Browser console: `0 errors`
- LAN: `0.0.0.0:8045 LISTENING`
- 1240 Fixed/Linked display: sealed record와 일치
- 1239 sealed/settlement: `UNCHANGED`
- Official Engine semantic change: `NO`

최종 웹 작업 결과:

`PASS_WEB_FINAL_COMPLETE_DEVICE_RETEST_REQUIRED`

PC 화면에서 1240 표시 및 최신 상태는 실제 캡처로 확인됐다.

최신 1240 화면의 휴대폰 실기기 재확인은:
`NOT_CONFIRMED`

## 8. 운칠기삼 브랜딩

최종 좌측 브랜드 영역:

```text
P45
운칠기삼
TRIO ORBIT
```

`운칠기삼`이 메인 강조 문구다.

본문 상단의 중복 운칠기삼 블록은 제거됐다.

브랜딩 수정 검증:

- sidebar brand: `PASS`
- menu/layout: `PASS`
- regression: `8/8 PASS`
- console errors: `0`
- 1240 state: `PENDING / 봉인 정상` 유지
- sealed/state/log/manifest SHA: `UNCHANGED`
- backend/API/prospective logic change: `NO`

판정:

`PASS_BRAND_AREA_UPDATED`

운칠기삼 의미:
- 운을 통제한다고 주장하지 않는다.
- 통제 가능한 선택·배치·실행·검증을 연구한다.
- TRIO 중심 구조 연구와 연결한다.
- 당첨 보장/예언/확률 우월 주장으로 해석하지 않는다.

## 9. 웹 관련 주요 audit / SHA

WEB FINAL result:

`E:\P45 프로젝트\v27_storage\audits\web_final_completion_1240_001\P45_WEB_FINAL_COMPLETION_1240_RESULT_001.md`

SHA list:

`E:\P45 프로젝트\v27_storage\audits\web_final_completion_1240_001\SHA256SUMS_001.txt`

WEB FINAL manifest SHA:

`c1448a935682ea6bff24b19891765872fb9544a86693af660a47dff5ee1942d9`

이전 WEB execution-path audit manifest SHA:

`c1c585957c57200deef3389968418b06d61cb29c161c0f5fafaa9163142fa57c`

## 10. 현재 완료/미완료 경계

### 완료

- 1239 official result 반영
- 1239 prospective settlement
- canonical draw 1..1239 정상화
- updater lifecycle compatibility repair
- 1240 prospective preview/seal
- 1240 sealed PENDING
- WEB V1 PC 화면 1240 전환
- stale EXP 표시 제거
- 운칠기삼 좌측 브랜드 반영
- PC web / LAN server / API 검증

### 아직 미확정 또는 대기

1. 최신 1240 화면의 실제 휴대폰 기기 재확인  
   `DEVICE_SIDE_LATEST_1240 = PASS_PHONE_DEVICE_VERIFIED`

2. 1240 outcome/settlement  
   아직 결과 발표 전이므로 `PENDING`

3. NO-PICK 867/867 문제  
   `UNRESOLVED`

4. 다음 신규 독립 연구가설  
   아직 formal EXP 등록 대상 확정 전. 임의로 EXP-021을 만들지 않는다.

## 11. 다음 작업 원칙

현재 WEB은 추가 수정하지 않는다.
새로운 실제 오류 증거가 없는데 재수정하지 않는다.

1240 결과 발표 전:
- sealed record 보호
- no outcome
- no regeneration

연구 쪽 다음 방향:
- Official gate 완화가 아니라 Experiment Lab에서 새로운 독립 신호 가설을 찾는다.
- 기존 Master 003에서 연구 중복 여부를 먼저 확인한다.
- 새 가설은 protocol / opposite hypothesis / data range / metric / success-failure / minimum sample / null/random / multiple-testing / walkforward / future-data blocking을 결과 전에 고정한다.

Work는 실제 로컬 파일·코드·DB·백테스트·Walkforward·SHA/manifest 반영이 필요할 때만 사용한다.

ChatGPT는 먼저:
- 연구 방향 판단
- 중복 연구 확인
- 가설 설계
- Work 결과 판독
- 다음 Work 지시문 작성

을 담당한다.

## 12. 복구 시 절대 착각 금지

- 1239는 `PENDING`이 아니다. settlement `COMPLETE`.
- 1240은 settlement 완료가 아니다. `PENDING`.
- 1240 prospective는 이미 sealed 됐다.
- 1240 결과는 아직 없다.
- 1240 번호를 다시 생성하지 않는다.
- EXP-017은 `NOT_CREATED`가 아니다.
- latest numbered EXP는 `EXP-020`.
- Official Engine은 계속 `FROZEN`.
- NO-PICK 문제는 해결되지 않았다.
- 웹 화면이 정상이라고 연구 성능 문제가 해결된 것은 아니다.

## 13. WHOLE-ENGINE synthetic replay semantics recovery audit

- resume point: 기존 SPEC과 TRIO rebuild를 재사용하고 PAIR target 662부터 재개.
- EXP-035 fair-null attempt: `STOP_NULL_SEMANTICS_NOT_VALID`; B=`0/2000`; hypothesis=`NOT_EVALUATED`.
- existing baseline: exact valid targets `369..1235 / 867`; output `0`; no-pick `867`.
- authoritative lifecycle lineage: approved Official repair + draw updater locked-rank conflict recovery; new semantics `NO`.
- TRIO sandbox rebuild: 1,193 rounds, 100,711 deterministic exposures exact equality `PASS`.
- decisive PAIR mismatch at target 662: historical baseline PG07/PG08 `INCOMPLETE/INCOMPLETE`, `PAIR_SYSTEM_HOLD`; repaired rebuild `PASS/PASS`, `PAIR_TEST_READY`.
- final: `SEMANTICS_REBUILD_NOT_EQUIVALENT`; result-driven rule change `NO`; B=2000 not executed.
- Registry: 035/036/037 `REGISTERED` unchanged; `REGISTRY_STATUS_UPDATE_NOT_CONFIRMED`.
- formal Registry rows `68`, executed count `27`, changes `0`.
- `LATEST_1240_PHONE_DEVICE = PASS_PHONE_DEVICE_VERIFIED`.
- evidence root: `E:\P45 프로젝트\v27_storage\audits\whole_engine_synthetic_replay_semantics_recovery_001`.

## 14. WEB 자동 업데이트 + 1240 정산 + 1241 전환 완료 (2026-09-06)

- ROOT CAUSE: 웹 서버에는 공식 결과 확인 trigger와 update→settlement→next preview/seal 연결 실행기가 없었다.
- fix: 시작 즉시 확인 + 300초 주기 coordinator를 추가했다. 이미 최신이면 `DRAW_ALREADY_CURRENT`이며 prospective write 0이다.
- canonical latest: 1240 (`11,13,19,20,31,44 + 27`).
- 1240 settlement: COMPLETE. 1240 sealed predraw original SHA `d8b7f0753500adf7fc62e894b1a8f2a9551f6bb90be0ec92d1fa3480082375fe` unchanged.
- current prospective: 1241 PENDING/SEALED, SHA `78db5180e8af1189fb815aef4ad8883eea0601c9198839a5a53dd0f73dc9b702`.
- web UI: 1240 결과 / 1241 출격 전환, 적중번호 강조, 한글 주적중·보조적중, 세트별 결과 반영.
- PC/LAN/API/restart PASS, listener `0.0.0.0:8045`, LAN URL `http://172.30.1.20:8045/`.
- integrity all_pass, future leakage 0, Official Engine semantics changes 0.
- evidence root: `E:\P45 프로젝트\v27_storage\audits\web_finalization_auto_update_ui_001`.

## 2026-09-06 — P45 JOSEON HERITAGE UI Work (시안 비교 대기)

- 이 추가 기록이 앞선 과거 회차/WEB 문구보다 현재 상태에 우선한다. 역사 기록은 삭제하지 않음.
- WEB DESIGN = P45 JOSEON HERITAGE, IMPLEMENTED. Previous CONCEPT03 neon direction = SUPERSEDED.
- 현재 메뉴 = 홈 / 미래검증 기록 / 안전 점검.
- HOME = 신규회차 추천픽 우선 / 지난회차 검수 보조. 두 상세는 홈 상단 버튼으로 진입.
- 현재 1240 settlement COMPLETE, 1241 PENDING / SEALED, future leakage 0. sealed/canonical 등 21개 대상 변경 전후 SHA 동일.
- 신규회차 상세 = 결과 대기 중 / 적중표시 없음. 지난회차 상세 = 결과·적중 검수 표시.
- Desktop 1366/1440, mobile 390/412/430, drawer 및 두 상세를 실제 rendered screenshot으로 확인. 총 23개 캡처 경계 검사: horizontal overflow 0, console errors 0.
- REFRESH_ROLE = REMOVED_REDUNDANT. 기존 load()는 /api/status 조회만 수행. 최초 load() 및 backend 300초 auto lifecycle은 unchanged. 기존 frontend polling 없음; 추가하지 않음.
- 이전 인수인계 판정: PASS_WEB_UI_DESKTOP_MOBILE_FINAL → PASS_WEB_UI_HOME_FINAL → PASS_WEB_HOME_NAV_FINAL; desktop/mobile responsive PASS; auto update PASS. 이는 전달된 역사적 판정이며 이번 조선풍 최종 승인으로 대체하지 않음.
- 현재 최종 UI 판정 = IMPLEMENTED_AND_VERIFIED_REFERENCE_COMPARISON_PENDING. 승인 시안 이미지가 없어 PASS_WEB_JOSEON_HERITAGE_FINAL 미발급.
- Evidence = E:\P45 프로젝트\v27_storage\audits\web_joseon_heritage_001\FINAL_REPORT.md, browser_checks.json, protected_comparison.json, screenshots/*.png.
- RESUME_FROM = APPROVED_REFERENCE_COMPARISON_ONLY. 승인 시안과 기존 캡처 비교부터 재개; 완료된 전체 검증/정산/생성 반복 금지.
- Official Engine FROZEN; NO-PICK 867/867 UNRESOLVED; latest numbered EXP-020; EXP-035 NOT_EVALUATED / STOP_NULL_SEMANTICS_NOT_VALID. 연구/Registry 수 변화 없음.

## 2026-09 runtime recovery / local cleanup

- `P45 시작.cmd` 0-byte 발견 및 복구 이력: `cd /d "%~dp0"`, `PYTHONPATH=%CD%\src`, bundled Python + `p45_v27.webapp` 실행 복원.
- live `p45_live_draws.csv` ACL inheritance 문제로 `Permission denied` 발생; CSV read permission만 복구.
- 당시 `DATA_CHANGED=NO`; before/after SHA256 동일: `882AA084BA6F5947C057D30DDC8AD3641396D9A697865657CCE24E5628C65655`.
- 당시 `/ HTTP 200`, `/api/status HTTP 200`, 1241 prospective 표시 PASS, 1240 result 표시 PASS, `DRAW_ALREADY_CURRENT`.
- 당시 최종 판정: `PASS_LIVE_CSV_READ_REPAIR`.
- WEB UI 최종 상태: `P45 JOSEON HERITAGE final`; detail page top button = `홈으로`; sidebar menu = `홈 / 과거 기록 / 안전 점검`; sidebar 표시 문구 `미래검증 기록 → 과거 기록`.
- local cleanup: 현재 운영 `web`에서 참조하지 않는 조선풍 단계별 설치 패키지 6개, 과거 디자인 백업 묶음, 빈 `P45_JOSEON_FINAL_PACKAGE` 폴더를 삭제. canonical/Official/Research evidence/DB/code/launcher/audits/prospective/sealed 파일 이동·삭제 없음.
- cleanup validation 시점의 실제 lifecycle은 1241 공식 결과를 감지한 뒤 1242 prospective / 1241 result로 정상 전환됨. launcher 재기동 후 `/` 및 `/api/status` HTTP 200, `DRAW_ALREADY_CURRENT`, future leakage 0, console error 0, current WEB asset missing 0.
- 1241 sealed predraw original SHA256: `78DB5180E8AF1189FB815AEF4AD8883EEA0601C9198839A5A53DD0F73DC9B702` UNCHANGED.
- cleanup 자체의 data/DB/content mutation: `NO`. 위 lifecycle 전환에 따른 canonical/DB/manifest/log 갱신은 기존 auto lifecycle 동작이며 cleanup 삭제 작업과 분리한다.

## 2026-09-06 — JOSEON visual correction
- WEB DESIGN: P45 JOSEON HERITAGE = CURRENT APPROVED DIRECTION.
- Previous neon concept: SUPERSEDED. 이전 JOSEON 구현의 사용자 REJECT를 반영해 한지/수묵/브랜드/프레임을 시각 보정.
- Implementation verdict: PASS_WEB_JOSEON_VISUAL_FINAL. 세 캡처 직접 확인: 한지, 수묵 산수, 달/소나무, 붓글씨 느낌 브랜드, red seal, 금빛 전통 프레임, seal-red 메뉴/CTA 확인.
- Final user visual approval: PENDING_SCREENSHOT_REVIEW. FINAL USER APPROVED 아님.
- 최소 기능 검사 정상, console errors 0, overflow 390/412/430 = 0/0/0. app.js·데이터·backend·research 변경 없음.
- Evidence: E:\P45 프로젝트\v27_storage\audits\web_joseon_visual_final_001\FINAL_REPORT.md
- Screenshots: 같은 evidence 폴더의 screenshots\desktop_1440.png, mobile_home_390.png, mobile_menu_390.png (최종 3장).

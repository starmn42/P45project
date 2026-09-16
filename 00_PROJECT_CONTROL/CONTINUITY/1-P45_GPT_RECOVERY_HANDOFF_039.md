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
- 최신 1240 화면의 실제 휴대폰 기기 재확인은 아직 별도 완료 증거가 없으므로 `DEVICE_SIDE_LATEST_1240 = NOT_CONFIRMED`.
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
   `DEVICE_SIDE_LATEST_1240 = NOT_CONFIRMED`

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

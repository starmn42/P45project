# P45 GPT RECOVERY / HANDOFF 037

## 현재 단일 운영 루트

- `LOCAL PROJECT = E:\P45 프로젝트`
- `WORK SOURCE = E:\P45 프로젝트`
- `PC START = E:\P45 프로젝트\P45 시작.cmd`
- `PHONE START = E:\P45 프로젝트\P45 휴대폰 미리보기.cmd`
- `P45 HOME = REMOVED / DO NOT USE / DO NOT RECREATE`
- `E:\P45 프로젝트`의 현재 폴더 구조는 미관을 이유로 이동·숨김·재배치·이름변경하지 않는다.

## 새 대화방 전달 순서

1. 이 latest Recovery/Handoff
2. `P45_NEW_CHAT_START_HERE_003.md`
3. `2-P45_PROJECT_CORE_GUIDE_TRIO_FIRST_ORBIT_009.md`
4. `P45_RESEARCH_MASTER_INDEX_003.md`
5. `P45_RESEARCH_COVERAGE_AUDIT_002.md`
6. `P45_FORMAL_EXP_REGISTRY_SNAPSHOT_001.csv`
7. `P45_RESEARCH_EVIDENCE_INVENTORY_002.csv`

문서 충돌 시 Recovery → Core Guide → Research Master → Coverage Audit → 원본 Result / Registry evidence 순으로 확인한다. Start Here는 빠른 안내문이며 최상위 복구 기준이 아니다.

## 프로젝트 불변 원칙

- P45는 번호 생성기가 아니라 구조·전이·관계·복귀·반대가설을 검증하는 연구 시스템이다.
- Official Engine: `FROZEN`.
- `3/3 = PRIMARY`, `exact 2/3 = SUPPORT`; 혼합판정 금지.
- 공식 승인 없는 code/DB/Registry/State/Experiment/sealed prospective 변경 금지.
- 실패·음성 결과 삭제 및 사후 rescue 금지.

## 연구 수 counting policy

- official internal studies: `12`.
- formal Registry physical/version rows: `68 = DRAW 53 + CROWD 9 + PRIZE 6`.
- actual executed/completed formal rows: `27`.
- protocol/execution blocked: `2`.
- closed axis: `1`.
- non-EXP executed axes: `28`.
- unexecuted reviewed ideas: `2`.
- latest numbered experiment: `EXP-020`.
- Registry Snapshot 001의 53은 DRAW-only snapshot이며 전체 formal Registry 수가 아니다.

## 현재 핵심 연구상태

- Official Engine: `FROZEN`.
- 역사 coverage: `VALID_ROUNDS=867`, `OUTPUT_AVAILABLE_ROUNDS=0`, `RESEARCH_NO_PICK_ROUNDS=867`, `NO_PICK_RATE=100%`.
- NO-PICK: `UNRESOLVED`.
- UNIT_3, UNIT_5, UNIT_9, UNIT_10 연구가 존재한다. 특히 UNIT_5/9/10 전멸구간 연구를 누락하지 않는다.
- EXP-017: `FAILED_NOT_SUPPORTED`.
- EXP-018 V1: bootstrap ambiguity로 outcome peek 0에서 실행 차단.
- EXP-018 V2: numerical ±1 adjacency axis `AXIS_CLOSED_NO_PRACTICALLY_USEFUL_RESIDUAL_NEIGHBOR_EFFECT`.
- EXP-019: `FAILED_NOT_SUPPORTED`.
- EXP-020: `FAILED_NO_SELECTION_SIGNAL`; Selection 통과 0, Holdout NOT RUN, rescue 금지.
- DRAW-ORDER: 정식 EXP 아님, 미실행·보류.
- REHEARSAL: EXP-021 아님, 미실행, 사용자 판단 패스.

## TRIO ORBIT 및 prospective 보호

- Historical Fixed/Linked와 prospective를 분리한다.
- Historical exact3: Fixed 5/1237, Linked 7/1237; Linked 우월성은 지지되지 않았다.
- 1239 prospective sealed original: `UNCHANGED`; 별도 outcome 정산 `COMPLETE`.
- 1239 MAIN6 `11,13,22,32,33,36`, BONUS `8`; Fixed PRIMARY/SUPPORT `0/1`, Linked PRIMARY/SUPPORT `0/0`.
- KTS45 schedule, sealed record, prospective log/state는 결과 후 재생성·사후수정하지 않는다.

## Draw source-of-truth 정상화

- canonical live CSV: `E:\P45 프로젝트\v27_storage\live\p45_live_draws.csv`
- canonical draw-result SQLite: `E:\P45 프로젝트\v27_storage\live\p45_new_draw_update_v1.sqlite3`
- 두 저장소는 `1..1239`, `1239`행, missing/duplicate `0`, canonical equality `PASS`.
- staging/audit snapshot은 검증 근거이며 canonical live source가 아니다.
- 1238 approved payload SHA: `99d44e493a357785f976e37d99b1e0d2ae179b161cc1aa4a5665f9606ec0c119`.
- 1239 official payload SHA: `4c0c600801ddeef24d98b54206bac807eaf623c7031bac35c035d4892d6c109a`.
- updater의 1240 analysis snapshot 생성은 lifecycle history schema 불일치로 실패했으나 draw-result store는 승인 범위 안에서 별도 검증·동기화했다. 엔진 로직은 변경하지 않았다.
- LZ76 macro complexity V1: `FAILED_NOT_SUPPORTED`; Master에는 non-EXP executed axis 28번으로 기록했다.

## 최신 기준문서

- Start Here: `E:\P45 프로젝트\00_PROJECT_CONTROL\CONTINUITY\P45_NEW_CHAT_START_HERE_003.md`
- Core Guide: `E:\P45 프로젝트\00_PROJECT_CONTROL\CONTINUITY\2-P45_PROJECT_CORE_GUIDE_TRIO_FIRST_ORBIT_009.md`
- Research Master: `E:\P45 프로젝트\90_RESEARCH\P45_RESEARCH_MASTER_INDEX_003.md`
- Coverage Audit: `E:\P45 프로젝트\90_RESEARCH\P45_RESEARCH_COVERAGE_AUDIT_002.md`
- Registry Snapshot: `E:\P45 프로젝트\90_RESEARCH\P45_FORMAL_EXP_REGISTRY_SNAPSHOT_001.csv`
- Evidence Inventory: `E:\P45 프로젝트\90_RESEARCH\P45_RESEARCH_EVIDENCE_INVENTORY_002.csv`

## 다음 작업 원칙

- 기존 연구 여부는 Master 003에서 먼저 확인하고 실제 판정은 원본 Result/locked protocol로 확인한다.
- 새 독립 가설은 결과 전에 protocol과 SHA를 잠근다.
- prospective 결과 반영은 공식 발표 뒤 sealed 원본과 분리된 절차로만 수행한다.
- 별도 사용자 홈 생성, 프로젝트 루트 미관 정리, Hidden 정리, 경로 이관을 하지 않는다.

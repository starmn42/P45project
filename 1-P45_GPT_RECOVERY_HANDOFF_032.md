# 1-P45 GPT 복구 인수인계 032

## Project Sources용 최신 복구 요약

- 버전: `032`
- 기준일: `2026-08-27`
- 이전 `031` 보존 및 local sync: `PASS`
- 핵심 지침 `005` 보존 및 local sync: `PASS`
- OFFICIAL ENGINE: `FROZEN`
- NO-PICK: `UNRESOLVED`
- DRAW_DISCOVERY_PAUSE: `ACTIVE`
- EXP-017: `NOT_CREATED`

## 1. 가장 중요한 현재 상태 — prospective 시작

TRIO ORBIT V1의 순수 고정 궤도와 직전회차 연동 궤도를 다음 미관측 회차부터 별도로 prospective 기록한다. 역사 backtest 결과와 prospective 결과를 합치지 않는다.

- Canonical latest at seal: `1238`
- Canonical SHA-256: `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Prospective target: `1239`
- Target result at seal: `UNAVAILABLE / PENDING`
- Sealed record: `E:\P45 프로젝트\v27_storage\prospective\trio_orbit_v1_001\P45_TRIO_ORBIT_TARGET_1239_SEALED_PREDRAW_001.md`
- Sealed SHA-256: `ed23691c5b9f1715c85b6d3362735dfa8cebb72b31dc258e2aa43bc299c94ead`
- Prospective log: `E:\P45 프로젝트\v27_storage\prospective\trio_orbit_v1_001\P45_TRIO_ORBIT_PROSPECTIVE_LOG_001.csv`
- Prospective state: `E:\P45 프로젝트\v27_storage\prospective\trio_orbit_v1_001\P45_TRIO_ORBIT_PROSPECTIVE_STATE_001.json`

### Target 1239 locked dispatch

- FIXED_A/B/C: `9 38 40` / `11 13 27` / `12 41 43`
- ANCHOR_A/B/C: `38 / 42 / 13`
- LINKED_A/B/C: `11 38 44` / `3 39 42` / `2 13 30`
- RESET: `NO`
- COMMON_COUNT: `0`
- FIXED_ONLY: `9-38-40; 11-13-27; 12-41-43`
- LINKED_ONLY: `11-38-44; 3-39-42; 2-13-30`
- RESULT_STATUS: `PENDING`
- FUTURE_LEAKAGE: `0`

이 출격은 1239 결과 전에 잠겼다. sealed pre-draw 파일은 수정하지 않고, 결과가 canonical에 들어온 뒤 별도 outcome record 또는 append-only log update로만 평가한다.

## 2. 현재 세 가지 연구축

### ① 순수 고정 궤도

- 숫자 3개 × 3세트 대조군.
- KTS45 330 TRIO와 기존 고정순서를 변경하지 않는다.
- 직전연동과 prospective 병행 기록한다.
- 예측력이 검증됐다고 주장하지 않는다.

### ② 직전회차 연동 V1

- 실전 우선 운용 후보이나 통계적 우월성 결론은 아니다.
- 기존 7회 anchor-position 순환, class scan, unused-TRIO, reset 규칙을 그대로 유지한다.
- 정상배치 불가능 시 강제배분 없이 기존 V1 방식으로 reset한다.
- 성공 TRIO를 제거하지 않는다.
- 순수 고정 대조군과 prospective 병행 기록한다.

### ③ 신호 연구 궤도

- 플랫폼은 유지하지만 현재 검증된 독립 신호는 없다.
- 출력은 근거가 있을 때만 0~6개이며 강제충원하지 않는다.
- 억지 신규 아이디어와 기존 실패축의 단순결합 탐색은 잠시 중단한다.
- 정말 새로운 독립가설이 사전필터를 통과할 때만 재개한다.

## 3. TRIO ORBIT 역사판정과 attribution

- V1 역사범위: targets `2..1238 = 1237`
- Fixed exact3: `5`; linked exact3: `7`
- Original fair-null Monte Carlo one-sided p: `0.319384030798`
- Original FINAL: `FAILED_NOT_SUPPORTED` 유지
- Divergence attribution: linked-only exact3 `7`, fixed-only exact3 `5`, 차이 `+2`
- Paired one-sided p: `0.386906131`
- Exact2: linked-only `174`, fixed-only `160`; one-sided p `0.226027740`
- Linked 7회 성공은 전부 LINKED_ONLY, fixed 5회 성공은 전부 FIXED_ONLY였다.
- 역사적 +2가 실제 교체 TRIO에서 발생한 것은 맞지만 우위는 통계적으로 지지되지 않았다.
- Attribution FINAL: `DIVERGENCE_NOT_SUPPORTED`

## 4. 최근 완료 negative results

### KTS 쌍완성 충돌 신호 V1

- FINAL: `FAILED_NOT_SUPPORTED`
- Evaluated `1237`, candidate exposures `1298`, observed hits `160`
- Matched-null expected `172.705128`, exact one-sided p `0.863655309594`
- Future leakage / official changes: `0 / 0`

### LAG 3~6 재등장 지도

- FINAL: `FAILED_NOT_INTERESTING`
- L3/L4/L5/L6 모두 지지 없음
- 최고 L5 raw 우연 가능성 약 `39.7%`; 4개 동시검사 반영 약 `86.2%`
- EXP-005 실패판정 유지

### EXP-004 × EXP-015 상호작용

- FINAL: `FAILED_NOT_INTERESTING`
- Family maxT 약 `44.15%`; 의미 있는 상호작용 없음

### EXP-005 × EXP-015 상호작용

- FINAL: `FAILED_NOT_INTERESTING`
- Full-sequence MC 약 `45.64%`; conditional shift 약 `48.30%`

### EXP-006 × EXP-013 상호작용

- FINAL: `FAILED_NOT_INTERESTING`
- 후보 적중률 `13.360882%`, 공정 기대 `13.333333%`, 차이 `+0.027548%p`
- Full-sequence MC 약 `25.04%`; conditional 약 `25.00%`

### TRIO ORBIT divergence attribution

- FINAL: `DIVERGENCE_NOT_SUPPORTED`
- Exact3 `7 vs 5`, paired one-sided p `0.386906131`
- Exact2 `174 vs 160`, one-sided p `0.226027740`

기존 각 연구의 실패판정은 변경하거나 구제하지 않는다.

## 5. 신규 DRAW 연구 사전필터

Work 실행 전 모두 확인한다.

1. 기존 실패축과 실질적으로 다른가.
2. 현재 역사자료로 표본이 충분한가.
3. 공정 무작위 비교를 결과 전에 명확히 고정할 수 있는가.
4. 결과 후 조건·기간·threshold 변경 없이 검증 가능한가.
5. 성공 시 숫자 3개 또는 0~6개 신호로 연결 가능한가.
6. 실패 연구를 이름만 바꿔 구제하는 것이 아닌가.

중요한 문제가 하나라도 있으면 Work를 사용하지 않는다.

## 6. 실패축 결합 운영원칙

- 기존 실패판정은 절대 변경하지 않는다.
- 논리적으로 독립적인 새 상호작용 가설만 별도 사전등록 실험으로 검토할 수 있다.
- 결과 좋은 부분만 고르는 결합, 숨은 점수, 임의가중치, 무작정 조합 탐색은 금지한다.
- 최근 결합실험들이 모두 실패했으므로 단순 실패축 결합 탐색은 현재 `PAUSE`다.

## 7. 다음 행동

1. 1239 결과가 canonical에 들어오기 전 sealed 출격을 수정하지 않는다.
2. 결과 확인 후 sealed SHA를 대조하고 prospective log의 1239 outcome 필드만 append/update한다.
3. Fixed와 linked를 같은 회차에서 계속 병행하되 역사 backtest와 prospective 성과를 분리한다.
4. 새 DRAW 연구는 사전필터를 모두 통과할 때만 제안·실행한다.
5. 추첨기·추첨볼 외부자료 연구는 현재 연구계획에서 제외하며 자동 재제안하지 않는다.

## 8. Project Sources

로컬 최신 권장:

1. `1-P45_GPT_RECOVERY_HANDOFF_032.md`
2. `2-P45_PROJECT_CORE_GUIDE_TRIO_FIRST_ORBIT_006.md`
3. `3-P45_OFFICIAL_REPAIR_APPLY_RESULT_001.md`

로컬 파일 생성과 Project Sources 실제 업로드는 구분한다. UI 업로드가 수행되지 않았다면 `PROJECT_SOURCES_UPLOAD = USER_UI_REQUIRED`다. 과거 031/005 및 역사파일은 삭제하지 않는다.

# 1-P45 GPT 복구 인수인계 031
## Project Sources용 최신 복구 요약
날짜: 2026-08-26

## 1. 현재 세 가지 핵심 연구축

### ① 순수 고정 궤도 — 대조군
- 숫자3개 × 3세트
- KTS45 330 TRIO 고정 창고
- 당첨결과와 무관한 고정 출격순서
- 계속 비교 기준으로 유지
- 예측력이 있다고 주장하지 않음

### ② 직전회차 연동 궤도 — 실전 우선 운용 후보
- 숫자3개 × 3세트
- ①과 동일한 330 TRIO 창고
- 직전 MAIN6+BONUS 7개에서 사전 고정 7회 순환규칙으로 기준숫자3개 선택
- 번호 자체를 새로 만들지 않고 출격시점만 변경
- 정상배치 불가능 시 강제배분 금지 / 즉시 리셋
- 리셋 후 기존 TRIO 재사용 허용
- 3/3 성공 TRIO 제거하지 않음

TRIO ORBIT V1 역사검증에서 ②가 관측상 7회, ①이 5회였지만 Monte Carlo one-sided p=0.319384로 사전 성공기준 p<=0.05를 통과하지 못했다. 역사적 연구판정은 `FAILED_NOT_SUPPORTED`로 보존한다.

②를 앞으로의 `실전 우선 운용 후보`로 선택할 수 있으나, 이는 통계적 우수성 결론이나 과거 결과의 성공 재분류가 아니다. 다음 미관측 회차부터 새로운 prospective 운용을 시작하며 ①은 계속 대조군으로 유지한다.

### ③ 신호 연구 궤도 — 다음 핵심 연구
- 출력 0~6개 가변, 최대 6개, 강제충원 금지, 0개면 패스
- 1~2개 개별신호, 3개 연구 A, 4~5개 상위3 연구 A와 잔여 추가신호, 6개 상위3 연구 A와 다음3 연구 B
- 순위는 사전 정의한 공개 근거만 사용
- 현재 검증된 독립 신호 없음

## 2. TRIO ORBIT V1 역사검증 확정 결과

- PRECHECK / KTS SCHEDULE: `PASS / PASS`
- schedule SHA-256: `5f212342c6c27fca8eafbc75d20a55fc4be4ca2961a9c70c3a7af0eca26f1075`
- DATA RANGE / EVALUATED: `1..1238 / 2..1238 = 1,237회`
- 순수 고정 3/3: `5/1237 = 0.404204%`
- 직전연동 3/3: `7/1237 = 0.565885%`
- 차이: `+2회`, `+0.161681%p`, 관측 건수 `+40%`
- fixed-only / linked-only: `5 / 7`
- Monte Carlo one-sided p: `0.319384`
- exact2/3: fixed `161건/159회`, linked `175건/174회`
- reset: `21회`; interval mean/median/min/max `57.76/59/43/63`
- FUTURE_LEAKAGE: `0`
- FINAL_JUDGMENT: `FAILED_NOT_SUPPORTED`
- official protected changes: `0`
- 결과: `E:\P45 프로젝트\v27_storage\experiments\trio_orbit_v1_001\`

V1 결과를 사후튜닝하여 성공으로 바꾸지 않는다.

## 3. 앞으로 ①과 ②의 역할

- ① 순수 고정 궤도: 대조군·기준선으로 계속 병행기록.
- ② 직전회차 연동 궤도: 실전 우선 운용 후보. 동일 V1 규칙을 고정하고 다음 미관측 회차부터 prospective 결과를 별도 누적한다.
- 과거 backtest와 prospective 결과를 섞지 않는다.
- 최근 canonical latest가 1238이므로 자연스러운 다음 prospective target은 1239이며 실제 실행 직전 최신값을 재확인한다.

## 4. 다음 연구 우선순위

`CHATGPT_DESIGN_SIGNAL_RESEARCH_AXIS_0_TO_6_NO_WORK_001`

- 기존 FAILED 축을 재포장하지 않는다.
- 0~6개를 실제로 출력할 수 있는 새 독립 연구가설을 먼저 찾는다.
- 신호가 없으면 억지로 만들지 않는다.
- 과도한 0개는 연구 실용성 문제로 보고 V2 개선 대상으로 다룬다.

## 5. 로컬 / Sources

Project Sources 최신 권장:
1. `1-P45_GPT_RECOVERY_HANDOFF_031.md`
2. `2-P45_PROJECT_CORE_GUIDE_TRIO_FIRST_ORBIT_005.md`
3. `3-P45_OFFICIAL_REPAIR_APPLY_RESULT_001.md`

이전 030/004는 Sources에서 최신 031/005로 교체하되 로컬 역사파일은 삭제하지 않는다.

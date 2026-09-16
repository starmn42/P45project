# 2-P45 프로젝트 핵심 지침 — TRIO-FIRST / ORBIT

## 새 대화방 복구용 장기 운영원칙

- 버전: `006`
- 기준일: `2026-08-27`
- 이전 `005`를 보존하고 아래 최신 운영상태를 계승한다.

## 0. 핵심 철학

P45의 핵심 연구단위는 숫자 3개다. 운을 통제한다고 주장하지 않으며, 통제 가능한 선택·배치·실행·기록·검증을 사전 고정한다.

V1은 결과 전에 잠근 뒤 그대로 실행한다. 문제가 발견되면 V1 결과와 실패판정을 보존하고 별도 V2로만 다룬다. 결과 후 규칙·기간·threshold·subgroup을 바꾸어 성공으로 재분류하지 않는다.

## 1. 세 가지 연구축

### ① 순수 고정 궤도

- 숫자 3개 × 3세트.
- KTS45 330 TRIO 고정 창고와 결과 무관 고정순서를 사용한다.
- 직전연동 궤도의 대조군으로 계속 prospective 병행한다.
- 역사적·prospective 성과가 기준을 통과하기 전 예측력을 주장하지 않는다.

### ② 직전회차 연동 V1

- 숫자 3개 × 3세트, 같은 KTS45 창고 사용.
- 직전 MAIN6+BONUS 7개를 오름차순 위치화하고 고정된 7회 패턴으로 anchor 3개를 선택한다.
- 서로 다른 미사용 TRIO에 정상배치할 수 없으면 강제배분하지 않고 V1 규칙대로 즉시 reset한다.
- reset 후 기존 TRIO 재사용 가능, 성공 TRIO 제거 금지.
- 실전 우선 운용 후보지만 통계적으로 우수하다는 뜻은 아니다.

고정 anchor-position 순환:

1. 1·2·4
2. 2·3·5
3. 3·4·6
4. 4·5·7
5. 5·6·1
6. 6·7·2
7. 7·1·3

### ③ 신호 연구 궤도

- 플랫폼은 유지한다.
- 현재 검증된 독립 신호는 없다.
- 근거에 따라 `0~6개`, 최대 6개만 출력하고 강제충원하지 않는다.
- 0개면 패스한다.
- 숨은 점수·임의가중치·결과 후 묶기를 금지한다.
- 억지 신규 아이디어 및 단순 실패축 결합 탐색은 현재 중단한다.

## 2. 역사 backtest와 prospective의 분리

- TRIO ORBIT V1 역사판정: fixed exact3 `5`, linked exact3 `7`, fair-null one-sided p `0.319384`, FINAL `FAILED_NOT_SUPPORTED`.
- Divergence attribution: linked-only `7`, fixed-only `5`, paired one-sided p `0.386906131`, FINAL `DIVERGENCE_NOT_SUPPORTED`.
- 관측상 linked가 더 많았다는 이유만으로 역사 실패판정을 변경하지 않는다.
- Prospective는 다음 미관측 회차의 출격을 결과 전에 sealed하고 새 데이터만 별도로 누적한다.
- 역사와 prospective 표본을 섞어 성공판정하지 않는다.
- Target 1239가 첫 sealed prospective 회차이며 기록 SHA는 `1-P45_GPT_RECOVERY_HANDOFF_032.md`와 실제 sealed 파일에서 확인한다.

## 3. Prospective 운영 절차

1. Canonical latest와 SHA를 확인한다.
2. 이미 결과가 있는 회차를 prospective로 소급 생성하지 않는다.
3. 기존 trace의 pointer/reset/used 상태를 이어받고 KTS schedule은 재생성하지 않는다.
4. Fixed와 linked 각 3TRIO, anchors, reset, common/fixed-only/linked-only를 결과 전에 저장한다.
5. Sealed record SHA를 확정하고 실제 log에는 결과 필드를 `PENDING`으로 둔다.
6. 결과 발표 후 sealed 파일은 수정하지 않는다. 별도 outcome record 또는 append-only log outcome 필드만 갱신한다.
7. 다음 회차 선택은 직전 sealed state와 canonical 결과를 이용해 동일 규칙으로 이어간다.

Prospective schema:
`v27_storage/experiments/trio_orbit_divergence_attribution_v1_001/P45_TRIO_ORBIT_PROSPECTIVE_LOG_SCHEMA_001.md`

Actual log/state:
`v27_storage/prospective/trio_orbit_v1_001/`

## 4. 신규 DRAW 연구 사전필터

Work 전에 다음을 모두 확인한다.

1. 기존 실패축과 실질적으로 다른가.
2. 현재 역사자료로 표본이 충분한가.
3. 공정 무작위 비교를 사전에 명확히 정할 수 있는가.
4. 결과 후 조건·기간·threshold를 바꾸지 않고 검증 가능한가.
5. 성공 시 숫자 3개 또는 0~6개 신호로 연결 가능한가.
6. 실패 연구를 이름만 바꾸어 구제하는 것은 아닌가.

중요한 문제가 하나라도 있으면 Work를 사용하지 않는다.

## 5. 실패축 결합 운영원칙

- 기존 실패판정 자체는 절대 변경하지 않는다.
- 논리적으로 독립적인 새 상호작용 가설은 별도 protocol을 결과 전에 잠근 경우만 검토할 수 있다.
- 결과 좋은 부분만 선택하는 결합, 숨은 점수, 임의가중치, 다수 실패축 무작정 조합 탐색은 금지한다.
- 최근 단순 결합실험들이 모두 실패했으므로 해당 탐색은 현재 `PAUSE`다.

## 6. Work 지시문과 저장 책임

- Work 지시문은 사용자가 실제로 다른 작업창에 복사해야 할 때만 코드블록으로 제공한다.
- 단순 설명에서는 불필요한 대형 지시문을 자동 생성하지 않는다.
- 로컬 산출물 저장이 필요한 작업은 Work/Codex가 실제 경로와 SHA를 확인하고 저장한다.
- ChatGPT Project Sources 교체·업로드는 해당 UI 권한이 있는 사용자가 수행한다. 로컬 생성 성공을 실제 업로드 성공으로 표현하지 않는다.
- 결과가 나온 prospective 행의 outcome 갱신은 canonical 반영 이후 담당 Work가 sealed SHA 대조 후 수행한다.

## 7. 현재 운영상태

- OFFICIAL ENGINE: `FROZEN`
- NO-PICK: `UNRESOLVED`
- DRAW_DISCOVERY_PAUSE: `ACTIVE`
- EXP-017: `NOT_CREATED`
- Verified independent draw signal: `NONE`
- 추첨기/추첨볼 외부자료 연구: 현재 계획에서 제외, 자동 재제안 금지

## 8. 공식 보호

- Official gate/threshold/signature/code/DB 변경 금지.
- NUMBER/TRIO/PAIR/CORE 공식 구조 변경 금지.
- Fixed/linked V1 규칙 및 KTS schedule 변경 금지.
- 기존 실패 연구와 TRIO ORBIT 역사판정 변경 금지.
- 미래누수, 결과 후 출격 변경, 성공 TRIO 제거 금지.

현재 Project Sources 권장본은 `032`, `006`, `3-P45_OFFICIAL_REPAIR_APPLY_RESULT_001.md`다. 이전 031/005와 모든 역사파일은 로컬에 보존한다.

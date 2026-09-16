# P45 EXPERIMENT LAB 거버넌스

- 단계: `EXPERIMENT_LAB_STAGE_1_GOVERNANCE_AND_REGISTRY_DESIGN`
- 성격: 운영체계·연구등록 장부 설계
- 공식 엔진: `FROZEN`
- 계산 알고리즘·실험 실행·공식 승격: 없음

## 1. 목적과 경계

EXPERIMENT LAB은 새로운 가설을 등록하고 실패까지 보존하는 독립 연구영역이다. 공식 P45의 `UNIT → NUMBER → TRIO → PAIR → CORE` 규칙, DB, prediction, walkforward 및 aggregation을 수정하지 않는다.

```text
OFFICIAL P45 (FROZEN, READ ONLY)
        |
        | 승인된 데이터 snapshot만 읽기
        v
EXPERIMENT LAB (별도 registry·storage·result)
        |
        | 자동 승격 경로 없음
        v
PROMOTION_CANDIDATE (공식 아님)
        |
        | 형님 별도 승인 + 새 공식 amendment/version
        v
OFFICIAL REVIEW (이번 단계 범위 밖)
```

## 2. 독립 연구영역

| LAB | RESEARCH_DOMAIN | 목적 | 공식 DRAW 엔진 연결 |
|---|---|---|---|
| NUMBER RELATION LAB | DRAW | 동시출현·조건부·시차 관계를 비인과적으로 검증 | 자동 연결 금지 |
| TRANSITION LAB | DRAW | 숫자 이동·흔적·격회·끝수 전이 검증 | 자동 연결 금지 |
| STRUCTURE LAB | DRAW | 가변 전멸·회복·교차구조 검증 | 자동 연결 금지 |
| SIMILAR ROUND LAB | DRAW | 유사/쌍둥이 회차 및 이후 전이 검증 | 자동 연결 금지 |
| SPACING LAB | DRAW | 간격·분산·등차·고정 간격 검증 | 자동 연결 금지 |
| CROWD LAB | CROWD | 사람들이 고르는 번호·형태의 편향 검증 | DRAW gate 사용 금지 |
| PRIZE-SHARE LAB | PRIZE_SHARE | 당첨 시 공동당첨·상금분할 위험 검증 | DRAW gate 사용 금지 |
| CROSS TEST LAB | DRAW_CROWD_CROSS_TEST | DRAW 효과와 CROWD 효과를 분리한 교차검증 | 결과·지표 별도 저장 |

각 LAB의 결과는 단순 점수, 가중치, 평균 또는 다수결로 합산하지 않는다.

## 3. 연구 ID

형식: `EXP-{DOMAIN}-{YYYYMMDD}-{NNN}-V{MAJOR}`

예: `EXP-DRAW-20260816-001-V1`.

- ID는 발급 후 재사용·수정하지 않는다.
- 결과를 본 뒤 기간·임계값·가설·성공기준을 바꾸려면 기존 실험을 종료하고 새 ID를 발급한다.
- 이전 실험은 `supersedes_experiment_id`로만 연결하고 삭제하지 않는다.
- DOMAIN 코드는 `DRAW`, `CROWD`, `PRIZE`, `CROSS`를 사용한다.

## 4. 사전등록과 잠금

`READY_FOR_TEST` 전에 다음을 canonical JSON으로 고정하고 SHA-256을 기록한다.

- 연구 목적·가설·반대가설
- 데이터 범위와 입력자료
- 계산 방법과 모든 자유 파라미터
- PRIMARY/SUPPORT 지표
- 성공·실패·중단 기준
- 최소 표본과 전체/최근 구간
- 미래 차단·walkforward·random/null 방식
- 다중검정·과최적화 통제

잠금 후 변경은 금지한다. 오탈자처럼 연구 의미가 바뀌지 않는 수정도 새 revision hash와 사유를 남기며, 의미 변경은 반드시 새 EXPERIMENT ID다.

## 5. 결과 보존

- 성공·실패·무효·중단을 모두 Registry에 남긴다.
- 결과 파일 삭제 대신 immutable archive와 hash를 사용한다.
- 실행한 모든 가설 수를 공개해 최고 결과만 골라 남기는 것을 금지한다.
- `3/3 PRIMARY`와 `exact 2/3 SUPPORT`는 해당 연구에서 사용될 때도 분리한다.
- 관계는 과거 동시출현·조건부 연관이라고 표현하며 인과관계로 주장하지 않는다.

## 6. 공식 격리

1. 공식 DB는 read-only URI 또는 hash가 고정된 snapshot으로만 읽는다.
2. EXPERIMENT 저장소는 공식 CORE/AUDIT/PAIR DB와 물리적으로 분리한다.
3. 공식 경로를 쓰는 API를 제공하지 않는다.
4. `PROMOTION_CANDIDATE`는 `official_effect=NONE`이다.
5. 공식 반영에는 형님 별도 승인, 새 amendment/version, 독립 검증 및 보호 manifest 갱신이 필요하다.

## 7. 권장 물리 구조(설계만)

```text
00_P45_STATE/experiment_lab/       # 거버넌스와 사람이 읽는 Registry
experiment_lab/registry/           # 향후 기계 판독 registry
experiment_lab/protocols/          # 사전등록 protocol
experiment_lab/snapshots/          # 공식 자료의 read-only snapshot manifest
experiment_lab/storage/            # 별도 실험 DB
experiment_lab/predictions/        # outcome 전 잠금
experiment_lab/backtests/
experiment_lab/walkforward/
experiment_lab/null_audits/
experiment_lab/reports/
experiment_lab/archive/            # 실패·폐기 포함
```

이번 단계에서는 `00_P45_STATE/experiment_lab` 문서만 만들며 연구 실행용 폴더·DB·코드는 만들지 않는다.

## 8. 금지사항

- 공식 코드·DB·gate·threshold·signature·ranking 변경
- 공식 walkforward 재실행 또는 1238회 추천 생성
- 실험 결과 자동 승격
- 여러 연구 결과의 임의 합산
- 좋은 결과만 보존
- outcome 확인 후 protocol 변경
- CROWD/PRIZE_SHARE를 추첨 확률 상승 근거로 사용


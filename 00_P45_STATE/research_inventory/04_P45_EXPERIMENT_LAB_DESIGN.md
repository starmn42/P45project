# P45 EXPERIMENT 연구소 설계안

이 문서는 설계안일 뿐이며 폴더·DB·계산기·실험을 만들거나 실행하지 않는다.

## 경계

```text
OFFICIAL ENGINE (FROZEN, READ ONLY)
              |
              | 승인된 데이터 스냅샷만 읽기
              v
EXPERIMENT LAB (별도 코드·DB·결과)
              |
              | 자동 승격 없음
              v
승격 후보 보고서 -> 사람의 별도 공식 승인 -> 새 공식 버전
```

EXPERIMENT는 공식 엔진의 DB, prediction, walkforward, aggregation 결과를 덮어쓸 권한이 없어야 한다.

## 권장 논리 구조

실제 생성은 다음 단계의 별도 승인 후에만 한다.

```text
experiment_lab/
  registry/          # 가설 ID, 소유자, 상태, 승인 기록
  protocols/         # 사전등록된 입력·식·기간·중단조건
  adapters/          # 공식 자료 read-only 스냅샷 어댑터
  experiments/       # 가설별 독립 코드
  storage/           # 공식 DB와 분리된 SQLite
  predictions/       # 결과 전 잠금 payload/hash
  backtests/         # 단순 과거적합과 분리
  walkforward/       # 회차별 1..R-1 원칙
  null_audits/       # random/placebo/permutation
  reports/           # 전체 성공·실패 공개
  archive/           # 폐기·중단 실험도 보존
```

## 수명주기

`IDEA → PROTOCOL_DRAFT → APPROVED_EXPERIMENT → BACKTEST → WALKFORWARD → NULL_AUDIT → REVIEW → KEEP / RETIRE / PROMOTION_CANDIDATE`

- `PROMOTION_CANDIDATE`는 공식 승격이 아니다.
- 공식 승격에는 새 공식 문서, 버전, 스키마 영향 분석, 보호 manifest, 별도 승인, 운영 전 검증이 필요하다.
- 실패한 실험을 삭제하지 않는다. 숨은 선택편향을 막기 위해 registry에 남긴다.

## 실험 레코드 최소 필드

- experiment_id, hypothesis_version, status
- 연구질문과 비인과 표현
- 입력 데이터 스냅샷 hash, source_end_round
- feature/algorithm canonical payload와 code hash
- 사전 고정 표본·기간·threshold
- PRIMARY와 SUPPORT 성과의 분리
- null probability 및 반대가설
- prediction hash before outcome
- walkforward run/checkpoint
- 시험한 전체 가설 수와 다중시험 교정
- 중단·실패·폐기 사유
- official_engine_write_attempt=0 증명

## 데이터 격리

1. 공식 DB는 SQLite `mode=ro` 또는 복제 스냅샷으로만 읽는다.
2. EXPERIMENT DB 파일은 공식 CORE/AUDIT/PAIR DB와 물리적으로 분리한다.
3. official 경로로 INSERT/UPDATE/DELETE하는 연결을 코드에서 제공하지 않는다.
4. 실험 결과의 UI 노출이 필요해도 `EXPERIMENTAL` 표기를 강제하고 공식 추천 영역과 분리한다.
5. 같은 데이터로 가설을 만들고 검증하지 않도록 개발/검증/최종 외부 구간을 구분한다.

## 성과 왜곡 방지

- 결과를 본 뒤 기간·임계값·feature를 바꾸면 새 hypothesis version으로 시작한다.
- 3/3 PRIMARY와 exact 2/3 SUPPORT를 합산하지 않는다.
- 관계망은 동시출현·조건부 연관으로만 표현하고 인과관계라고 쓰지 않는다.
- 작은 표본은 확정적 우위로 승격하지 않는다.
- 많은 가설 중 최고 하나만 보고하지 않고 전체 registry와 실패율을 공개한다.

## 후보 연구군

| 군 | 후보 | 시작 전 필수 쟁점 |
|---|---|---|
| 관계 | 숫자 동시출현·시차·3개·조건부 관계망 | 독립성 귀무가설, 다중검정, 누출 차단 |
| 전이 | 이동·회차 흔적·격회·끝자리 전이 | 정확한 상태 정의와 시간 방향 |
| 전멸 확장 | 가변 전멸·회복속도·이동×전멸 | 구간 탐색의 사후선택 방지 |
| 유사회차 | 쌍둥이·구조형 전이 | 유사도 식 사전 고정 |
| 간격 | 간격·등차·+13/+14·분산 | 패턴 대량탐색 교정 |
| 행동 | 대중선택·OMR | 추첨확률과 당첨금 분산 연구의 완전 분리 |

## 승격 차단장치

EXPERIMENT 결과를 OFFICIAL로 복사하는 자동 API를 만들지 않는다. 승격은 `PROMOTION_CANDIDATE` 보고서 생성까지만 자동화할 수 있고, 공식 파일·코드·DB 변경은 별도 명시적 승인 없이는 실패하도록 설계한다.

## DRAW / CROWD / PRIZE_SHARE 분리

모든 Registry 레코드는 `RESEARCH_DOMAIN`을 `DRAW`, `CROWD`, `PRIZE_SHARE`, `DRAW_CROWD_CROSS_TEST` 중 하나로 고정한다.

- DRAW는 추첨 결과의 구조만 연구한다.
- CROWD는 구매자의 번호 선택행동만 연구한다.
- PRIZE_SHARE는 당첨 시 공동당첨·상금분할의 상대 위험만 연구한다.
- CROSS는 DRAW와 CROWD 결과를 별도 지표·별도 성공기준으로 저장한다.

영역 간 단순 점수합산과 CROWD/PRIZE_SHARE 결과의 공식 DRAW gate 연결을 금지한다. LOW/HIGH WINNER의 구조적 특징도 DRAW 예측효과와 선택행동 효과를 각각 독립 검증한다.

# EXP-001 숫자 동시출현 관계망 사전등록

## 식별

- short_id: `EXP-001`
- registry_experiment_id: `EXP-DRAW-20260816-002-V1`
- research_domain: `DRAW`
- lab: `NUMBER RELATION LAB`
- status: `DESIGNED`
- official_effect: `NONE`
- official_engine_isolation: `REQUIRED`

## 연구 목적

1~45의 모든 unordered pair 990개에서 같은 회차 동시출현률이 공정한 무작위 추첨 기준과 다른지, 그 방향이 시간구간과 미래차단 walkforward에서 재현되는지 검증한다.

이는 통계적 연관성 연구다. 숫자가 서로 영향을 준다는 인과 주장을 하지 않는다.

## 연구 질문

1. 990개 중 무작위 기대와 다른 pair가 존재하는가?
2. 전체에서 보인 방향이 FIRST_HALF와 SECOND_HALF에서 재현되는가?
3. RECENT_100과 RECENT_50에서도 같은 방향 또는 최소한 유의한 반대가 없는가?
4. R에서 1..R-1만 쓴 walkforward에서도 유지되는가?
5. 990개 다중검정과 family/global null을 통제한 뒤에도 남는가?

## 가설과 반대가설

- H1: 하나 이상의 MAIN pair가 사전 정의한 다중검정·기간재현·walkforward·null 기준을 모두 충족한다.
- H0: 관측된 극단값은 공정한 무작위 추첨과 990개 동시검색으로 설명 가능하며, 시간·walkforward에서 재현되지 않는다.
- 방향은 양(과다 동시출현)과 음(과소 동시출현)을 모두 허용하고 두-sided로 검정한다.

## 분석대상

- 숫자: 1~45
- pair: `a < b`인 990개
- 한 회차에서 pair 발생 여부: 두 숫자가 scope에 모두 포함되면 1, 아니면 0
- A-B와 B-A는 동일 canonical pair
- 데이터 시작·종료 회차는 실행 승인 시 snapshot manifest에 고정한다.
- 누락·중복·범위오류 회차는 저장 전에 fail-closed하며 임의 보간하지 않는다.

## Scope

- `MAIN`: 본번호 6개. `EXP001_PRIMARY_SCOPE`
- `INTEGRATED`: 본번호 6개+보너스 1개. `EXP001_SUPPORT_SCOPE`
- 두 scope의 count, p-value, 보정, 판정을 합산하지 않는다.

P45 공식 연구의 3/3 PRIMARY 체계는 변경하지 않는다. 여기서 MAIN을 primary로 정한 것은 EXP-001의 공정한 6/45 동시출현 질문에 한정된다.

## 기간

- OVERALL: snapshot의 전체 적격 회차
- FIRST_HALF: N개 적격 회차를 시간순 정렬한 앞 `floor(N/2)`개
- SECOND_HALF: 나머지 `N-floor(N/2)`개
- RECENT_100/50/20: source_end_round 이하 적격 회차의 마지막 100/50/20개
- RECENT_20은 `TEST_ONLY`; 성공·실패·edge 생성·승격후보 판정에 사용하지 않는다.

## 최소 표본

- 정적 backtest: OVERALL 적격 회차 500 이상, 각 half 250 이상
- walkforward 학습 시작: R 이전 적격 회차 500 이상
- pair walkforward 확정평가: 해당 pair의 사전선택 exposure 200 이상
- 기준 미달은 FAILED가 아니라 `INCONCLUSIVE/INSUFFICIENT_SAMPLE`

## 금지 범위

- A→다음 회차 B, 2회 간격 B, 3개 네트워크
- UNIT/전멸/끝수 조건부 관계망
- degree·centrality·community를 이용한 추천
- TOP pair만 공개하거나 추천번호 생성
- outcome 확인 후 기간·지표·threshold 변경

변경 필요 시 EXP-001을 원래 기준으로 닫고 새 EXPERIMENT ID를 발급한다.


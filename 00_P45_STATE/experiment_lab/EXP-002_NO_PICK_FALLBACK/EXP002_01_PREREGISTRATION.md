# EXP-002 사전등록

- canonical ID: `EXP-DRAW-20260816-038-V1`
- human alias: `EXP-002`
- name: `NO-PICK COVERAGE & QUALIFIED RESEARCH FALLBACK`
- domain: `DRAW`
- official effect: `NONE`
- official engine: `FROZEN`

## 목적

공식 P45가 결과 전에 `RESEARCH_NO_PICK`으로 확정된 회차에서 공식 gate를 완화하지 않고, 이미 존재하는 NUMBER·UNIT·역할·구조·반대가설·Pareto 자료의 상대적 순서로 별도 실험 3+3을 만들 수 있는지 검증한다.

## 가설

사전 고정된 eligibility와 기존 결정론적 순서로 선택한 서로 겹치지 않는 TRIO A/B는 무작위 비중복 두 TRIO보다 MAIN 최소 한 TRIO 3/3 성과가 높고 워크포워드에서 재현된다.

## 반대가설

coverage 증가는 가능하더라도 MAIN 3/3 성과는 무작위와 같거나 낮으며, 관찰 차이는 표본변동·다중탐색·후보 재사용으로 설명된다.

## 입력과 경계

- 각 평가회차 `R`은 `1~R-1`만 사용한다.
- `DATA_UNAVAILABLE`, `HISTORICAL_SCHEMA_UNAVAILABLE`, `FIRST_ELIGIBLE_WARMUP`, `SYSTEM_ERROR`는 fallback 대상이 아니다.
- 공식 결과가 가능한 회차도 대상이 아니다.
- `RESEARCH_NO_PICK`만 실험 eligibility 평가 대상으로 한다.
- 1238 당첨결과는 설계·feature·ranking에 사용하지 않는다.

## 연구 출력

- EXPERIMENTAL FALLBACK만 생성 가능하다.
- `TRIO A`와 `TRIO B`는 각각 3개이고 서로 중복 숫자가 없어야 한다.
- 적격 후보가 부족하거나 비중복 TRIO가 없으면 EXPERIMENT도 `NO PICK`이다.
- 공식 추천, CORE, 최종 6개로 표시하지 않는다.


# EXP-001 LOCKED PROTOCOL 봉인 실행 결과

- experiment_id: `EXP-DRAW-20260816-002-V1`
- short_id: `EXP-001`
- run_id: `6cb93fa4-2d29-4deb-8229-c7febcac0255`
- execution: `SINGLE SEALED RUN`
- data range: `1~1237`
- data snapshot SHA-256: `b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0`
- protocol SHA-256: `2d4e723b87bc2f44a7a0d763ee4779ded40b007f3cbf4b093b9e771c9248dd9d`
- execution code SHA-256: `5a5155877832b2a367b492ae2be455781393edc109fe15f5955d9c03cb7fd866`
- result DB SHA-256: `bc20ae1e80c05297485a3f0fb9d98946eda94c2b54d1fc3865be992b0a52c6fd`
- result DB: `v27_storage/experiments/exp001/exp001_research.sqlite3`
- completed_at: `2026-08-16 07:32:12 UTC`

## 봉인 판정

- retrospective_result: `NO_STATIC_MAIN_SIGNAL`
- walkforward_result: `NOT_REPRODUCED`
- final_judgment: `FAILED`
- explanation_code: `D`
- promotion_candidate: `false`
- official_recommendation_allowed: `false`
- official engine effect: `NONE`

사전 고정한 기준을 사후 완화하지 않았다. 이 결과는 계산 오류가 아니라, 정적 MAIN 신호와 워크포워드 재현을 확보하지 못한 음성 연구 결과다.

## 회고 검증

- unordered number pairs: `990`
- scopes: `MAIN` primary, `INTEGRATED` secondary
- locked periods per scope: `OVERALL`, `FIRST_HALF`, `SECOND_HALF`, `RECENT_100`, `RECENT_50`, `RECENT_20 TEST_ONLY`
- stored pair-period results: `11,880`
- OVERALL Holm pass: `MAIN 0`, `INTEGRATED 0`
- OVERALL maxT pass: `MAIN 0`, `INTEGRATED 0`
- all-period Holm pass count: `1` (`MAIN RECENT_100` only)
- all-period maxT pass count: `0`

### 전체기간 관찰상 최강 관계 — 연구 진단 전용

- MAIN strongest positive: `11-21`, risk difference `+0.0123343377`, observed count `34`
- MAIN strongest negative: `8-12`, risk difference `-0.0094926631`, observed count `7`
- INTEGRATED strongest positive: `3-20`, risk difference `+0.0119325837`, observed count `41`
- INTEGRATED strongest negative: `23-41`, risk difference `-0.0115112320`, observed count `12`

위 관계는 Holm·maxT 공식 관문을 통과하지 못했으므로 추천이나 공식 예측 근거가 아니다.

## Null 및 다중검정 통제

- IID fair-draw maxT: `100,000`회, MAIN/INTEGRATED 분리
- fixed-marginal switch null: `10,000`회, MAIN/INTEGRATED 분리
- MAIN fixed-marginal max statistic: p95 `4.0168183832`, p99 `4.4823320150`
- INTEGRATED fixed-marginal max statistic: p95 `4.0965554386`, p99 `4.4912024375`
- null/checkpoint rows: `403`
- Holm FWER와 maxT 결과를 별도로 보존했다.

## 워크포워드

- evaluation range: `501~1237`
- evaluation rounds: `737`
- source boundary: every `R` used only `1~R-1`
- COMPLETE_NO_EDGE: `737`
- failed rounds: `0`
- future leakage: `0`
- prediction/network hash missing: `0`
- exposure rows: `0`
- pairs reaching exposure 200: `0`
- significant/reproduced pairs: `0`
- result: `NOT_REPRODUCED`

## 결과 해석

코드 `D`는 정적 MAIN 관문을 충족한 관계가 없고, 워크포워드에서도 재현 가능한 관계가 형성되지 않았음을 뜻한다. 최근 구간의 일부 관찰치는 `TEST_ONLY` 또는 보조 진단으로만 남기며 공식 신호로 승격하지 않는다. 독립 재현도 확인되지 않았다.

## 무결성 및 보호

- DB integrity_check: `ok`
- foreign_key_check violations: `0`
- data hash verified: `true`
- protocol hash verified: `true`
- protected canonical manifest: `7c1458328a17a0824622c00ce1f54996e22ed4c2e9d04180be4ad9029ba8febb`
- official engine: `FROZEN`
- official NUMBER/TRIO/PAIR/CORE changes: `0`
- official recommendation generated: `false`

실패 결과와 원인은 삭제하지 않고 EXP-001의 영구 연구 이력으로 보존한다.

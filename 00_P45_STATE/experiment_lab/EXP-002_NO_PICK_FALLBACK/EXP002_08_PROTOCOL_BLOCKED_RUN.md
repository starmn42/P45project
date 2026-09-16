# EXP-002 봉인 RUN 중단 기록

- experiment ID: `EXP-DRAW-20260816-038-V1`
- protocol: `EXP002-PROTOCOL-1.0`
- canonical protocol hash: `832e7df52854a61ae5b769ebdf529e48b6df0ca622606a583b5fa9c9055b7c46`
- lock hash: `0f8277ef43440764ec7e52dc80331af6b96ffc775bf24caaa06ba1a858e239fd`
- data snapshot: `1~1235`
- data snapshot SHA-256: `a5a33282fa9e6a5265b170086358bf901d3cfdcf6ec7ebc3df6f975ad7b95800`
- run ID: `95a29030-3ec3-435b-9696-e869c69c456f`
- final run status: `INVALID / PROTOCOL_BLOCKED`

## 중단 원인

사전등록된 fallback source pool은 `NUMBER_HOLD`를 허용한다. 그러나 공식 TRIO 파레토 계산기의 `NUMBER_RANK`에는 `NUMBER_PASS`, `NUMBER_WEAKEN`, `NUMBER_TEST`만 있고 `NUMBER_HOLD`가 정의되어 있지 않다. 평가회차 964의 prediction 생성 중 `KeyError: NUMBER_HOLD`가 발생했다.

`NUMBER_HOLD`에 임의 순위를 부여하거나 HOLD를 TEST/PASS로 바꾸면 새 연구 규칙을 만드는 것이므로 이번 봉인 protocol에서 금지된다. 따라서 계산을 강제로 계속하지 않았다.

## 보존된 부분 evidence

- committed prediction locks: 595 (`369~963`)
- committed outcome rows: 290 (`369~963` 중 fallback pick 회차)
- duplicate prediction rows: 0
- final judgment rows: 0
- database integrity: `ok`
- foreign-key violations: `0`

부분 결과는 성과 판정, 승격, 공식 추천 또는 후속 규칙 선택에 사용할 수 없다. `RETROSPECTIVE_COMPLETE`, `WALKFORWARD_COMPLETE`, random/null 비교 및 최종 experiment 판정은 모두 미완료다.

## 필요한 다음 결정

별도 승인 하에 다음 중 하나를 사전등록 protocol revision으로 명확히 해야 한다.

1. `NUMBER_HOLD`를 source pool에서 제외한다.
2. 공식 근거가 있는 `NUMBER_HOLD`의 TRIO ranking semantics를 별도 amendment로 정의한다.

이번 기록은 어느 선택도 승인하거나 추천 결과로 승격하지 않는다. 공식 P45 엔진은 `FROZEN`이며 변경되지 않았다.

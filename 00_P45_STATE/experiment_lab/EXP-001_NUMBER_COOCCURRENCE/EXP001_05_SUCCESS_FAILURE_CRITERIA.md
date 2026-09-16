# EXP-001 성공·실패 기준

## BACKTEST 단계의 의미

정적 과거검증 완료는 `BACKTESTED`일 뿐 `SUPPORTED`가 아니다. 아래 STATIC 기준은 walkforward 진입 후보를 정하는 데만 사용한다.

## STATIC MAIN 관계 통과 기준

하나의 pair가 다음을 모두 충족해야 한다.

1. OVERALL MAIN Holm-adjusted two-sided exact p < 0.05
2. 95% Clopper-Pearson interval이 MAIN baseline 1/66을 포함하지 않음
3. FIRST_HALF와 SECOND_HALF risk_difference 방향 동일
4. 두 half 각각 MAIN Holm-adjusted p < 0.05
5. RECENT_100 방향 동일
6. RECENT_50에 Holm-adjusted p < 0.05의 유의한 반대방향 없음
7. IID maxT global p < 0.05
8. MAIN 전체 적격 500, 각 half 250 이상

INTEGRATED는 SUPPORT로 별도 보고하며 MAIN 실패를 구제하지 않는다. RECENT_20은 TEST_ONLY다.

## 최종 SUPPORTED 기준

최소 한 pair가 STATIC MAIN 기준과 다음 WALKFORWARD 기준을 모두 충족해야 한다.

1. 사전선택 exposure 200 이상
2. 선택 당시 고정된 방향의 MAIN one-sided exact test가 Holm-adjusted p < 0.05
3. 실제 MAIN rate가 해당 방향으로 baseline 1/66보다 우위
4. round-order permutation temporal support p < 0.05
5. 독립 재현 실행의 결과·hash 일치
6. future leakage, protocol violation, official isolation violation 0

성공의 의미는 시간적으로 재현되는 통계적 동시출현 연관성의 존재다. 번호 예측 가능성이나 공식 추천 유효성을 뜻하지 않는다.

## INCONCLUSIVE

- 전체/half 최소 표본 부족
- walkforward selection exposure 200 미달
- fixed-marginal null 수렴 실패(해당 support 결과만 INCOMPLETE)
- 검정은 완료됐으나 효과 방향·재현 증거가 불충분

## FAILED

- 충분한 표본과 정상 검정을 완료했지만 통과 pair 0
- STATIC 관계가 walkforward에서 재현되지 않음
- 반대가설 또는 null이 결과를 충분히 설명
- 독립 재현 실패

## 무효 run

미래누출, outcome 선조회, protocol 변경, source/official DB write, hash 불일치는 연구결과 FAILED와 구분해 `PROTOCOL_VIOLATION` 또는 `SYSTEM_ERROR`로 종료한다. 무효 run도 삭제하지 않는다.

## 다음 상태

- 현재 사전등록 문서 완성: `DESIGNED`
- 실제 실행 전 별도 승인·data snapshot·protocol hash lock 후: `READY_FOR_TEST`
- 이번 작업에서 BACKTESTED/SUPPORTED/PROMOTION_CANDIDATE로 전환 금지


# P45 EXPERIMENT 승격 정책

## 핵심 원칙

`PROMOTION_CANDIDATE`는 공식 승격이 아니다. 이는 별도 공식 검토를 요청할 수 있는 상태일 뿐이며 `official_effect=NONE`을 유지한다.

## 후보화 최소 조건

1. protocol이 outcome 전에 hash-lock됨
2. 최소 표본 충족
3. backtest와 walkforward 완료
4. random/null 비교 완료
5. 반대가설 검증 완료
6. 다중검정·과최적화 통제 공개
7. 재현 성공
8. 실패·중단 포함 전체 실험 목록 공개
9. 공식 엔진 격리 위반 0
10. PRIMARY/SUPPORT 지표 분리

하나라도 미충족이면 PROMOTION_CANDIDATE로 이동할 수 없다.

## 공식 채택에 필요한 별도 절차

- 형님의 명시적 공식 검토 승인
- 공식 Amendment 또는 신규 version 작성
- 기존 공식 규칙과 충돌 감사
- schema/DB/웹/운영 영향 분석
- 독립 재현 및 FAIL-FAST 검증
- 보호 manifest와 상태시스템 갱신
- LIVE_OFFICIAL 별도 승인

이 절차를 EXPERIMENT LAB이 자동 수행하거나 우회할 수 없다.

## 영역별 제한

- DRAW: 검증돼도 자동으로 NUMBER/TRIO/PAIR/CORE gate에 들어가지 않는다.
- CROWD: 추첨확률 근거로 승격할 수 없다.
- PRIZE_SHARE: 당첨 시 상금분할 위험의 보조 정보일 뿐 공식 당첨 확률을 바꾸지 않는다.
- DRAW_CROWD_CROSS_TEST: DRAW 효과와 CROWD 효과가 각각 독립 기준을 통과해야 하며 합산 점수를 금지한다.

## 사후 선택 방지

여러 실험 중 최고 성과 하나만 승격 후보로 제출할 때도 전체 시험 수, 실패율, 선택절차 및 다중시험 교정을 함께 제출해야 한다.


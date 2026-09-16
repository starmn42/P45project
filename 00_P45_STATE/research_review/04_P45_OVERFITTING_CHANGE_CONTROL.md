# P45 과적합·연구 변경 통제

이 문서는 기존 공식 원칙을 운영 절차로 모은다. threshold나 gate를 추가하지 않는다.

1. 신규 규칙은 동결 운영 엔진과 분리된 EXPERIMENT에서 시작한다.
2. 규칙 개발 자료와 최종 평가 자료는 가능한 한 분리한다.
3. validation 결과를 본 뒤 규칙을 수정하면 기존 validation을 새 규칙의 공식 증거로 재사용하지 않는다.
4. 수정 규칙은 새 연구 버전·새 rule/code hash·새 run으로 취급한다.
5. 검증과 명시적 승인이 끝나기 전에는 FROZEN 운영 엔진에 합치지 않는다.
6. 같은 자료에서 많은 규칙을 반복 탐색하면 selection bias가 커진다는 사실을 기록한다.
7. 연구자 자유도를 줄이기 위해 gate, threshold, ranking, tie-break, signature, context와 분석 순서를 결과 확인 전에 고정한다.
8. 3/3 PRIMARY와 exact 2/3 SUPPORT, Integrated와 Main을 각각 분리해 보고한다.
9. 실패·HOLD·불리한 결과도 삭제하거나 평균화하지 않는다.
10. 성과가 좋아 보이는 변경보다 재현성, 누수 방지, 사전 고정을 우선한다.

변경 요청에는 최소한 변경 이유, 공식 규칙 대비 차이, 데이터 사용 범위, 사전 고정 hash, 독립 검증 계획과 과거 결과 재사용 금지 여부가 있어야 한다. 연구 의미를 바꾸는 변경은 `RESEARCH_RULE_CHANGE_APPROVAL_REQUIRED`이다.


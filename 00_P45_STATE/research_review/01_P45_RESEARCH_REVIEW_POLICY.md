# P45 연구 검토 정책

상태: 공식 운영 거버넌스 요약  
적용 대상: 외부 AI 의견과 신규 연구 제안의 검토  
주의: 이 문서는 연구 규칙을 추가하거나 변경하지 않는다.

## 판정

| 판정 | 의미 |
|---|---|
| ACCEPT | 기존 목적·공식 규칙과 일치하고 근거와 재현성이 충분하다. |
| ACCEPT_WITH_MODIFICATION | 취지는 유효하지만 기존 공식 규칙·누수 방지·불변성에 맞게 범위를 제한해야 한다. |
| REJECT | 핵심 원칙과 충돌하거나 성과를 본 뒤 관문을 완화한다. |
| ALREADY_EXISTS | 공식 문서와 코드에 이미 동일 기능 또는 원칙이 존재한다. |
| NEEDS_EVIDENCE | 근거·표본·결정식 또는 재현 절차가 부족하다. |

## 잠긴 핵심 기준

- 흐름은 `UNIT → NUMBER → TRIO → PAIR → CORE`이다.
- TRIO `3/3`은 PRIMARY, exact `2/3`은 SUPPORT이며 합산하지 않는다.
- Integrated와 Main, DIAGNOSTIC과 OFFICIAL을 분리한다.
- `valid_for_core = 0`이면 CORE와 최종 6개를 만들지 않는다.
- 결과 확인 후 threshold·gate·eligibility를 완화하지 않는다.
- 회차 R의 예측은 1~R-1 자료만 사용한다.
- 점수·가중치·확률·다수결을 임의로 만들지 않는다.
- 동결된 운영 엔진은 명시적 승인 전 변경하지 않는다.

## 연구 변경 심사

threshold, gate, eligibility, ranking, tie-break, signature, context, CORE eligibility, TRIO/PAIR 평가기준 또는 historical classification 변경이 필요하면 구현하지 않고 `RESEARCH_RULE_CHANGE_APPROVAL_REQUIRED`로 올린다.

요약 문서에 세부 규칙이 없다는 이유만으로 새 규칙을 만들지 않는다. 공식 Amendment/PATCH와 실제 코드까지 확인한다. 성과 개선보다 신뢰성·재현성·누수 방지를 우선한다.


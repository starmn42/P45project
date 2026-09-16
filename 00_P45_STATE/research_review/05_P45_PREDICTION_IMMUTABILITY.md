# P45 Prediction 불변성·누수 방지

## 공식 운영 원칙

- 회차 R의 prediction은 1~R-1 자료만 사용한다.
- prediction은 결과 발표 전에 canonical payload와 hash로 고정하고 write-once로 저장한다.
- outcome은 실제 발표 후 별도 레코드에 저장한다.
- evaluation은 prediction을 수정하지 않고 별도 append한다.
- 과거 prediction의 번호, 순위, signature, context 또는 hash를 outcome 확인 후 덮어쓰지 않는다.
- prediction timestamp, target_round, as_of/source_end_round, outcome timestamp와 provenance를 분리 보존한다.

## 현재 보호 수준

| 영역 | 확인 결과 |
|---|---|
| PAIR v1.2 | PRELOCK → gate/context → FINALIZATION 뒤 outcome 접근, R-1 강제, atomic round, unique 제약과 hash 검증: `ALREADY_PROTECTED` |
| CORE | 잠금 결과 불변 트리거와 감사의 역수정 차단: `ALREADY_PROTECTED` |
| 회차 업데이트 | 실제 결과 append 후 이전 prediction을 별도 평가하고 다음 회차 snapshot 생성: `ALREADY_PROTECTED` |
| 과거 TRIO walkforward | selection 계산에 R 결과를 사용한 증거는 없으나 코드가 prediction hash 생성 전에 R outcome 객체를 메모리에 읽는 경로가 존재: `ANTI_LEAKAGE_GAP` |

과거 TRIO 결과를 변경하거나 재실행하지 않는다. 엄격한 인터페이스 수준 보완은 outcome loader를 prediction 저장 뒤에만 호출하도록 분리하는 작업이며, 동결 엔진 코드 변경 승인이 필요하다. 현재 문서 판정은 `PARTIAL`이다.

## 검증 규칙

- `as_of_round = target_round - 1`을 강제한다.
- prediction hash 저장 시각은 outcome 접근 시각보다 앞서야 한다.
- resume은 같은 rule/code/schema/source hash에서만 허용한다.
- COMPLETE prediction 및 exposure 중복은 0이어야 한다.
- 결과 발표 후 변경 요청은 새 evaluation 또는 새 연구 버전으로만 남긴다.


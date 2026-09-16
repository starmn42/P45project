# P45 EXPERIMENT 상태전이

## 상태 의미

|상태|의미|결과 존재|
|---|---|---|
|IDEA|아직 등록 전 아이디어|아니오|
|REGISTERED|ID와 연구영역이 등록됨|아니오|
|DESIGNED|가설·반대가설·방법 초안이 완성됨|아니오|
|READY_FOR_TEST|protocol hash가 outcome 전에 잠김|아니오|
|TESTING|승인된 protocol로 실행 중|부분 결과는 공식 사용 금지|
|BACKTESTED|사전 고정 backtest 완료|예|
|WALKFORWARD_TESTED|외부 순차검증 완료|예|
|SUPPORTED|가설이 사전 성공 기준을 충족|예|
|INCONCLUSIVE|표본·검정이 결론에 부족|예|
|FAILED|실패 기준 충족 또는 재현 실패|예|
|RETIRED|연구 종료·폐기·대체|보존|
|PROMOTION_CANDIDATE|별도 공식 검토 후보|예; 공식 아님|

## 허용 전이

```text
IDEA -> REGISTERED -> DESIGNED -> READY_FOR_TEST -> TESTING
TESTING -> BACKTESTED | INCONCLUSIVE | FAILED
BACKTESTED -> WALKFORWARD_TESTED | INCONCLUSIVE | FAILED
WALKFORWARD_TESTED -> SUPPORTED | INCONCLUSIVE | FAILED
SUPPORTED -> PROMOTION_CANDIDATE | RETIRED
INCONCLUSIVE -> RETIRED
FAILED -> RETIRED
모든 비종료 상태 -> RETIRED (사유 필수)
PROMOTION_CANDIDATE -> RETIRED (공식 미채택 포함)
```

## 금지 전이

- IDEA/REGISTERED/DESIGNED에서 곧바로 TESTING 또는 PROMOTION_CANDIDATE
- BACKTESTED만으로 공식 승격
- FAILED/INCONCLUSIVE를 같은 ID로 조건 수정 후 재시험
- PROMOTION_CANDIDATE에서 자동 OFFICIAL

## 규칙 변경

READY_FOR_TEST 이후 기간, 임계값, 가설, 성공기준, 계산방법의 연구 의미를 바꾸면 현재 ID는 `RETIRED` 또는 해당 결과 상태로 닫고 새 ID를 발급한다. 새 ID는 `supersedes_experiment_id`로 연결한다.

## 상태전이 감사

모든 전이는 이전 상태, 새 상태, 사유, 승인자, 시각, protocol hash, record hash를 append-only event로 남긴다. 결과가 좋지 않아도 전이 기록과 결과를 삭제하지 않는다.


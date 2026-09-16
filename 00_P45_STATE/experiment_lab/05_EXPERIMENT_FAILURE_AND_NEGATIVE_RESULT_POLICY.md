# P45 실패·음성 결과 정책

## 보존 원칙

실패, 무효, 모순, 표본 부족, 재현 실패를 삭제하지 않는다. 모든 결과는 Registry와 archive에 보존하며 좋은 결과만 남기는 survivorship bias를 금지한다.

## 실패 분류

- `HYPOTHESIS_NOT_SUPPORTED`: 사전 성공 기준 미충족
- `COUNTER_HYPOTHESIS_SUPPORTED`: 반대가설 지지
- `INSUFFICIENT_SAMPLE`: 최소 표본 미달
- `NULL_NOT_BEATEN`: random/null 기준 우위 없음
- `MULTIPLE_TESTING_RISK`: 다중시험 통제 실패
- `OVERFITTING_DETECTED`: backtest와 walkforward 괴리
- `FUTURE_LEAKAGE`: 미래자료 접근
- `PROTOCOL_VIOLATION`: 잠긴 규칙 위반
- `NOT_REPRODUCED`: 동일 조건 재현 실패
- `DATA_INVALID`: 입력자료 무결성 실패
- `OFFICIAL_ISOLATION_VIOLATION`: 공식 엔진/DB 쓰기 시도
- `SYSTEM_ERROR`: 연구결과와 분리된 기술 오류

## 결과 수정 금지

결과를 본 뒤 기간·threshold·가설·성공기준을 바꾸지 않는다. 변경 필요 시:

1. 기존 실험을 원래 기준으로 완료 또는 종료한다.
2. 변경 사유를 failure/retirement record에 남긴다.
3. 새 EXPERIMENT ID와 새 protocol hash를 발급한다.
4. 기존 ID를 supersedes 링크로 연결한다.

## 음성 결과의 가치

FAILED와 INCONCLUSIVE는 연구 낭비가 아니라 중복 실험과 사후선택을 막는 증거다. 후속 연구는 이전 실패를 인용하고 무엇이 달라졌는지 사전 설명해야 한다.

## 공개 최소정보

- 원래 가설·반대가설
- 잠긴 protocol hash
- 사용 데이터 범위
- 실제 표본 수
- 모든 PRIMARY/SUPPORT 결과
- random/null 결과
- 실패 원인과 재현 상태
- 후속 실험 ID


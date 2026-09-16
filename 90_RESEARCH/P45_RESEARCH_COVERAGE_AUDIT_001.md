# P45 연구목록 Coverage Audit 001

- research-related files found: `551`
- formal Registry rows: `53`
- master entries: `94` (`공식 내부 12 + 정식 EXP 53 + EXP 외 27 + 미실행 후보 2`)
- unmapped research files: `0` at research-family level
- master entries without local evidence: `1` (`REHEARSAL/리허설 번호`; 사용자 결정만 보존, 로컬 독립 결정문 근거미확인)

## 역방향 대조 방식

- `00_P45_STATE`, `v27_storage/experiments`, `v27_storage/audits`, `analysis`, `backtests`, `experimental`, `candidate-results`, `approvals`, `docs`, `90_RESEARCH`에서 MD/JSON/CSV 중 result/protocol/audit/calculation/registry/state/trace/backtest/report/lock 관련 파일을 전수 수집했다.
- 파일별 path/size/SHA/evidence class는 `P45_RESEARCH_EVIDENCE_INVENTORY_001.csv`에 저장했다.
- Registry 전 행은 `P45_FORMAL_EXP_REGISTRY_SNAPSHOT_001.csv`에 저장했다.
- rollback, reproduction, raw calculation, protocol/lock은 새로운 연구 개수로 중복 계산하지 않고 해당 family의 증거로 매핑했다.
- UNIT_3/5/9/10은 설계 원문과 실제 current-1239 rerun/audit 증거가 모두 Master에 반영됐다.

## 주의

Registry 문서의 과거 서술에는 physical/version rows `68`이라는 메모가 있으나 실제 `|EXP-DRAW-...|` 표 행은 `53`이다. 본 감사는 실제 행 수를 사용하며 차이를 숨기지 않는다.

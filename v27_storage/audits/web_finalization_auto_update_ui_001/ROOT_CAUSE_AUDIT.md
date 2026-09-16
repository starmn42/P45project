# P45 WEB 자동 업데이트 ROOT CAUSE AUDIT

- 확정일: 2026-09-06 KST
- 판정: `TRIGGER_ABSENT_AND_LIFECYCLE_CHAIN_ABSENT`
- 기존 `P45 시작.cmd`는 웹 서버만 실행했다.
- 기존 `/api/status`는 저장된 상태를 읽기만 했고, 공식 결과 확인을 시작하는 startup hook 또는 주기 실행기가 없었다.
- 기존 웹에는 preview/seal 수동 경로만 있었으며 `결과 감지 → canonical 갱신 → settlement → 다음 회차 preview/seal` 연결 실행기가 없었다.
- 저장 상태를 화면에 투영하는 기능 자체는 정상이며, stale projection이 근본 원인은 아니었다.

## 수정

- 웹 서버 시작 시 즉시 확인하고 이후 300초마다 확인하는 단일 coordinator를 추가했다.
- 공식 updater가 새 결과를 반영한 경우에만 settlement와 다음 회차 preview/seal을 순서대로 수행한다.
- 이미 최신이면 `DRAW_ALREADY_CURRENT`로 종료하며 prospective 파일을 쓰지 않는다.
- Official Engine 규칙, gate, threshold, signature, NUMBER/TRIO/PAIR/CORE semantics는 변경하지 않았다.

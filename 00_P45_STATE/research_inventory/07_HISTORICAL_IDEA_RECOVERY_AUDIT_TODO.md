# HISTORICAL IDEA RECOVERY AUDIT — TODO

- 상태: `CLOSED_2026-08-16`
- 성격: 과거 연구 아이디어 누락 복구 감사
- 공식 엔진 영향: `NONE`
- 실행 승인: 완료

## 완료 연결

- 감사 보고: `07_HISTORICAL_IDEA_RECOVERY_AUDIT.md`
- 복구 목록: `08_RECOVERED_HISTORICAL_IDEAS.md`
- 대조표: `09_HISTORICAL_IDEA_CROSSCHECK_MATRIX.md`
- 조사 결과: 후보 36건, `RECOVERED_MISSING_IDEA` 1건, `PARTIALLY_CAPTURED` 6건, `DEPRECATED_HISTORICAL` 6건
- Inventory/Registry 자동 변경: 없음
- 공식 엔진 영향: 없음
- 최종 Inventory: 87건
- 최종 Experiment Registry: 44건
- 신규 Experiment 등록: 0건

## 목적

과거 ChatGPT 대화 아이디어가 모두 저장됐다고 가정하지 않고, 현재 프로젝트 파일에 남은 연구 흔적을 기존 86개 Research Inventory와 44개 Experiment Registry에 대조한다.

## 향후 조사 범위

- P45 v2.x 구버전·시험·보류·폐기 문서
- `P45_IDEA_INBOX.md`
- `P45_DECISION_LOG.md`
- CURRENT_STATE/HANDOFF/history/snapshot
- research_review, analysis, approvals, legacy ledger·experimental 자료
- 코드·schema·테스트의 연구명·상태명·미사용 필드
- 과거 첨부·작업 문서 중 프로젝트에 보존된 자료

## 대조 기준

1. 동일 canonical 연구가 86개 Inventory에 있는가.
2. MISSING/PARTIAL/HOLD라면 Experiment Registry에 있는가.
3. 이름만 유사하고 목적·계산법이 다른 연구를 잘못 합치지 않았는가.
4. 공식 구현 흔적 없이 OFFICIAL_ACTIVE로 추정하지 않았는가.
5. CROWD/PRIZE_SHARE와 DRAW 목적을 혼합하지 않았는가.

## 누락 발견 시 처리

- 즉시 공식 엔진에 넣지 않는다.
- `RECOVERED_IDEA_CANDIDATE`로 근거 경로와 함께 기록한다.
- 중복·대체·폐기 여부를 별도 검토한다.
- 새 실험 후보라면 별도 승인 후 Experiment ID를 발급한다.
- 공식 규칙 변경은 amendment·검토·명시적 승인 없이는 불가하다.

## 완료 조건

- 조사한 파일 목록과 hash manifest
- 발견 후보 전체 목록
- Inventory/Registry 중복 대조표
- 누락·중복·충돌·UNKNOWN 분류
- 공식 엔진 변경 0 증명

이 문서는 원래 TODO 기록을 보존하면서 완료 문서로 연결한다. 복구 항목은 아직 기존 Inventory/Registry에 합치지 않았다.

# P45 AUTO RESEARCH LOOP V1 — 운영 및 기술 명세서

## 1. 개요 및 목적
P45 AUTO RESEARCH LOOP V1은 공식 추첨 결과가 발표되고 운영 라이프사이클(공식 정산 및 웹 동기화)이 완료된 후,
사람의 수동 지시 없이도 기존 활성 연구를 자동으로 정산·복기하고, 후속 연구 가설을 통계적 원칙에 따라 안전하게 탐색·사전잠금하는 자동화 서브시스템이다.

## 2. 핵심 운영 원칙
1. **Official Engine = FROZEN:**
   - 공식 추천 엔진, 게이트, 임계치, 시그니처, 공식 DB 및 웹 추천번호는 절대 자동 수정되지 않는다.
   - 연구 성과가 아무리 우수하더라도 `PROMOTION_CANDIDATE` 상태에서 멈추며, 반드시 사용자 명시 승인(`USER_APPROVAL_REQUIRED`)을 거쳐야 한다.
2. **공식 라이프사이클 격리 (Strict Failure Isolation):**
   - 연구 자동화 서브시스템에서 예외나 장애가 발생하더라도 공식 결과 감지, 정산 및 웹 반영은 정상 완료된다.
   - 연구 자동화 실패는 격리된 로그(`v27_storage/research_automation/logs/`)로 보존되고 다음 사이클에서 안전하게 재시도된다.
3. **사후 데이터 오염 방지 (Data Snooping Prevention):**
   - $R$ 회차 정산 시점에서 생성된 신규 가설은:
     - `birth_round = R`
     - `discovery_range = 1..R` (`EXPLORATORY_ONLY`)
     - `confirmatory_start_round = R + 1`
   - $R$ 이전 데이터는 탐색용으로만 분류되며, 최종 검증 판정에 사후 재사용할 수 없다.
4. **프로토콜 사전 잠금 (Pre-registration & Protocol Lock):**
   - Follow-up Gate(12대 검증 항목)를 통과한 후보 가설은 결과 계산 전에 프로토콜 전문의 SHA-256 해시를 생성하여 `PROTOCOL_LOCK.json`으로 영구 잠금된다.
5. **연구 폭주 방지 (Runaway Prevention):**
   - 1회 추첨 정산 사이클당 신규 생성되는 `IDEA_CANDIDATE`는 최대 3개로 엄격히 제한된다.

## 3. 서브시스템 디렉토리 구조
```
src/p45_v27/research_automation/
├── __init__.py                     # 패키지 익스포트
├── constants.py                    # 상태 머신 열거형 및 상수 정의
├── candidate_queue.py              # 후보 큐 관리자
├── research_state_machine.py       # 14대 상태 전이 및 승격 방화벽
├── followup_gate.py                # 12대 후속 연구 필수 통과 게이트
├── duplicate_checker.py            # Registry/Master 중복 검사기
├── hypothesis_candidate_builder.py # Type A/B/C 가설 자동 생성기
├── protocol_generator.py           # 기계 판독형 프로토콜 생성 및 SHA 잠금
├── active_research_discovery.py    # 활성 연구(TRIO ORBIT, EDGE ARITHMETIC 등) 자동 탐색
├── settlement_dispatcher.py        # 연구별 정산 및 겹침 감지 디스패처
├── retrospective_builder.py        # 회차별 복기 패킷(JSON/MD) 생성기
├── signal_diagnostics.py           # 6/45 정확 귀무가설 캘리브레이션 및 진단
├── idempotency_guard.py            # 동일 회차 중복 실행 차단기 (중복 쓰기 0건 보장)
├── audit_logger.py                 # 단방향 추가 전용 감사 로거
├── evidence_writer.py              # 증거 및 산출물 안전 기록기
├── retry_recovery.py               # 프로세스 비정상 종료 복구 관리자
├── hook.py                         # 공식 수명주기 연동 격리 훅
└── README.md                       # 본 기술 문서
```

## 4. 저장소 데이터 구조 (`v27_storage/research_automation/`)
- `candidate_queue/`: 생성된 후보 가설 레코드 (JSON)
- `retrospectives/round_{R}/`: 회차별 `RESEARCH_RETROSPECTIVE_PACKET.json` 및 `.md`
- `protocols/{CANDIDATE_ID}/`: 사전 등록 프로토콜 및 `PROTOCOL_LOCK.json`
- `state/`: 회차 정산 완료 상태 및 복구 체크포인트 (`processed_rounds.json`, `recovery.json`)
- `logs/`: 장애 격리 에러 로그
- `research_automation_audit.jsonl`: 전체 이벤트 감사 로그

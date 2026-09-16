# P45 상태 전이 매트릭스

확인된 공식 문서와 저장 코드만 기록한다. 확인되지 않은 자동 전이는 `REVIEW_REQUIRED`이다.

## PAIR → CORE

| PAIR 상태 | 공식 의미 | 허용되는 CORE 경로 |
|---|---|---|
| PAIR_SYSTEM_HOLD | 시스템·필수자료 문제 | CORE_SYSTEM_HOLD |
| PAIR_RESEARCH_HOLD | 연구 관문 미충족 | CORE_RESEARCH_HOLD |
| PAIR_READY | PG01~PG14 전부 PASS | 추가 잠금·보고·해시 조건 충족 시 CORE_SET_READY 가능 |
| PAIR_TEST_READY | 공식 TEST_READY 연구경로 | CORE_TEST_SET_READY 가능 |

AUDIT_NOT_RUN/PENDING/INCOMPLETE는 그 자체로 CORE HOLD를 만들지 않는다. AUDIT는 이미 잠긴 CORE 결과를 변경할 수 없다.

## CORE

| 시작/조건 | 전이 | 확인 상태 |
|---|---|---|
| 새 run | RUNNING 또는 PARTIAL | 코드 확인 |
| 공식 세트 준비 | CORE_SET_READY | 공식 문서 확인 |
| 시험 세트 준비 | CORE_TEST_SET_READY | 공식 문서 확인 |
| 연구/시스템 관문 보류 | CORE_RESEARCH_HOLD / CORE_SYSTEM_HOLD | 공식 문서 확인 |
| 잠금 수행 | COMPLETE/LOCKED 및 불변 결과 저장 | 코드·DB 트리거 확인 |
| 잠금 후 번호 변경 | 금지 | 코드·DB 트리거 확인 |

## AUDIT

| 상태 | 의미/전이 | 확인 상태 |
|---|---|---|
| AUDIT_NOT_RUN | 미실행 | 공식 enum 확인 |
| AUDIT_PENDING | run 생성/대기 | 저장 코드 확인 |
| AUDIT_RUNNING | 실행 중 | enum 존재, 자동 전이 구현 `REVIEW_REQUIRED` |
| AUDIT_PASS | 공식 관문 통과 | 기준 문서 존재, 저장 전이 `REVIEW_REQUIRED` |
| AUDIT_BORDERLINE | 경계 | 조정 p값 .05~.10 기준 문서 존재, 저장 전이 `REVIEW_REQUIRED` |
| AUDIT_FAIL | 실패 | 조정 p값 >.10 등 기준 문서 존재, 저장 전이 `REVIEW_REQUIRED` |
| AUDIT_INCOMPLETE | 미완료 | enum 존재, 저장 전이 `REVIEW_REQUIRED` |
| AUDIT_INVALIDATED | 규칙/해시 변경 등 무효화 | 원칙 존재, 저장 전이 `REVIEW_REQUIRED` |

현재 `audit_store.py`는 run·chunk·cache 생성/완료 골격은 있으나 audit_run의 모든 최종 상태 전이 API가 완성됐다고 확인할 수 없다. 따라서 AUDIT 전이 구현은 `TRANSITION_REVIEW_REQUIRED`이다.

## CERTIFICATION

| 단계 | 공식 조건 | 구현 확인 |
|---|---|---|
| EXPLORATORY | CORE만 완료 | enum/초기 저장 확인 |
| TESTED | 1,000회 개발 감사 | 공식 문서 확인, 자동 승격 `REVIEW_REQUIRED` |
| VALIDATED | 10,000회 및 안정성·placebo | 공식 문서 확인, 자동 승격 `REVIEW_REQUIRED` |
| CERTIFIED | 50,000회·전체 관문·보수적 조정 기준 | 공식 문서 확인, 자동 승격 `REVIEW_REQUIRED` |

규칙 변경은 과거 CORE 잠금을 바꾸지 않으며 해당 certification의 유효성을 다시 검토하게 한다. 전체 승격/무효화 저장 워크플로는 `TRANSITION_REVIEW_REQUIRED`이다.


# P45 HISTORICAL IDEA RECOVERY AUDIT

- 감사일: 2026-08-16 (KST)
- 상태: `HISTORICAL_IDEA_RECOVERY_CLOSED`
- 엔진: `FROZEN`
- 조사 목적: 현재 86개 Research Inventory와 44개 Experiment Registry 밖에 남은 과거 연구 아이디어를 복구
- 공식 엔진·코드·DB·예측 변경: 없음
- 보호 canonical hash 기준: `7c1458328a17a0824622c00ce1f54996e22ed4c2e9d04180be4ad9029ba8febb`

## 조사 범위와 방법

프로젝트의 텍스트성 파일 696개(`md`, `txt`, `json`, `csv`, `py`)를 파일 목록과 키워드로 검색했다. 원자료 JSON, 상태 이력 복사본, 자동 생성 보고서는 동일 내용 중복 여부를 확인한 뒤 원본 문서를 우선했다. 23개 후보 문서의 156개 일치 문맥을 직접 대조했고, 핵심 근거는 다음과 같다.

- `docs/P45_v2.3_Work_UTF8_BOM_CRLF.md`의 시험·보류·폐기 목록
- `P45_v2.5_Work_UTF8_BOM_CRLF.md`
- `P45_v2.7_Work_UTF8_BOM_CRLF.md`와 `P45_v2.7.1_Work_UTF8_BOM_CRLF.md`의 감사 연구
- `00_P45_STATE/P45_IDEA_INBOX.md`, `P45_DECISION_LOG.md`, CURRENT_STATE/HANDOFF
- `research_inventory`, `experiment_lab`, `research_review`
- 코드·테스트·스키마의 연구 상태명과 미완료 메모

단순 키워드가 아니라 당시 목적과 현재 항목의 목적을 비교했다. 이름이 비슷해도 연구 질문이 다르면 합치지 않았다. 과거 문서의 동일 복사본은 한 아이디어로 계산했다.

## 결과 요약

|분류|수|의미|
|---|---:|---|
|ALREADY_CAPTURED|19|현재 Inventory 또는 Registry에 목적이 보존됨|
|PARTIALLY_CAPTURED|6|상위 개념은 있으나 원래 세부 연구 질문이 빠짐|
|RECOVERED_MISSING_IDEA|1|현재 두 목록에 독립 항목이 없음|
|DUPLICATE|1|표현만 다르거나 세부 조건 메모가 기존 연구와 동일|
|AMBIGUOUS|3|연구 아이디어보다 운영·구현 보완인지 불명확|
|DEPRECATED_HISTORICAL|6|과거 명시 폐기됐으나 86개 장부에서 개별 기록이 빠짐|
|합계|36|고유 후보 문맥|

## 핵심 판정

- 현재 86개 Research Inventory가 완전한가: `NO`
- 현재 44개 Experiment Registry가 완전한가: `NO`
- 이유: `선정 안정성 감사`가 독립 연구로 누락됐고, 6개 명시 폐기 아이디어의 역사 기록이 빠져 있다. 부분 포착 6건도 원래 세부 목적을 완전히 보존하지 못한다.
- 복구 항목의 현재 상태: `ADD_CANDIDATE`
- 자동 Registry 등록: 없음
- 공식 승격: 없음

## 가장 중요한 복구·부분복구 TOP 10

1. 선정 안정성 감사 — 독립 `RECOVERED_MISSING_IDEA`
2. 최근20 급변 관찰 — `최근20 TEST_ONLY`에 급변 가설이 명시되지 않은 부분 포착
3. 탐색가족 사전등록 — 과최적화 방지에 포함되지만 별도 장부 목적이 축약됨
4. 강세 지속 대 강세 붕괴 — 최근10 지속 연구에 반대가설 축이 축약됨
5. 결손 회복 대 결손 확대 — 회복 연구에 반대 방향 검증이 축약됨
6. 과밀 지속 대 정상화 — 구조 붕괴 연구에 원래 전이 가설이 명시되지 않음
7. 규칙 변경 시 감사 인증 무효화 — 규칙 장부에 포함되나 독립 재인증 질문이 축약됨
8. 전멸구간 경계번호 우선 — 역사적으로 명시 폐기됐으나 개별 장부 누락
9. 교차조건 개수가 많은 번호 우선 — 역사적으로 명시 폐기됐으나 개별 장부 누락
10. 타 AI 번호 역삭제 — 역사적으로 명시 폐기됐으나 개별 장부 누락

## 형님이 과거 제안했지만 현재 목록에서 빠져 있던 연구

- `선정 안정성 감사`: 공식 v2.7 문서 37장의 12개 고정 시나리오 연구. 현재 86개 목록의 과최적화 방지와 관련되지만, 선택쌍 재현·순위 백분위·재선정 수를 독립 판정하는 연구가 별도 항목으로 없다.
- 아래 6개는 과거 제안 흔적은 있으나 문서에서 명시적으로 폐기됐다. 연구 복원 후보가 아니라 `DEPRECATED_HISTORICAL` 보존 대상이다.
  - 전멸구간 경계번호 우선
  - 교차조건 개수가 많은 번호 우선
  - 5단위·끝수 강제 압축
  - 격회 재출현 직접 가산
  - 타 AI 번호 역삭제
  - 근거 없는 확률·점수·가중치

## 한계

- 삭제된 대화나 프로젝트 밖 자료는 확인할 수 없으므로 “과거 모든 아이디어가 복구됐다”고 증명할 수 없다.
- 바이너리 DB는 아이디어 본문 저장소가 아니므로 schema·metadata 수준만 확인했다.
- `research_review`의 세 항목은 연구 가설인지 구현 안전 조치인지 불명확해 `AMBIGUOUS`로 남겼다.

## 감사 완료 전 권장 단계 — 처리 완료

이 단계는 최종 반영 승인으로 완료됐다. 선정 안정성 감사는 Inventory 87로 분리했고, 부분 포착 6건은 기존 의미를 보강했으며 Experiment Registry는 44건을 유지했다.

## 최종 반영 결과

- `선정 안정성 감사`: Inventory 87로 독립 추가, 상태 `PARTIAL`
- PARTIALLY_CAPTURED 6건: 기존 5개 항목의 원래 목적에 보강
- 신규 Experiment: 0건
- Experiment Registry: 44건 유지
- DEPRECATED_HISTORICAL 6건: 폐기 이력만 유지
- AMBIGUOUS 3건: 추측 없이 유지
- 역사 아이디어 복구: `CLOSED`

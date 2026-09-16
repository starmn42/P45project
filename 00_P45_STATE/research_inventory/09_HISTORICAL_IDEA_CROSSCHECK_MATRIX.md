# P45 과거 아이디어 대조표

|ID|과거 아이디어|주 근거|현재 대응|분류|후속 상태|
|---|---|---|---|---|---|
|H01|격회 재출현|v2.3 23장|Inventory/EXP 12|ALREADY_CAPTURED|유지|
|H02|최근10회 강세 지속성|v2.3 23장|Inventory 79/EXP 20|ALREADY_CAPTURED|유지|
|H03|구조적 결손 회복속도|v2.3 23장|Inventory/EXP 15|ALREADY_CAPTURED|유지|
|H04|가변 전멸구간|v2.3 23장|Inventory/EXP 17|ALREADY_CAPTURED|유지|
|H05|비전멸 전용 엔진|v2.3 23장|Inventory/EXP 21|ALREADY_CAPTURED|유지|
|H06|최근20 급변 관찰|v2.3 23장|Inventory 27|PARTIALLY_CAPTURED|HR-002 검토|
|H07|구조형 쌍둥이 회차 전이|v2.3 23장|Inventory/EXP 24|ALREADY_CAPTURED|유지|
|H08|가변 전멸구간 세부 조건|v2.3 23장|Inventory/EXP 17|DUPLICATE|기존 항목 근거 보강 가능|
|H09|결손 회복 전환점|v2.3 23장|Inventory/EXP 16|ALREADY_CAPTURED|유지|
|H10|다중 전멸구간 상호작용|v2.3 23장|Inventory/EXP 18|ALREADY_CAPTURED|유지|
|H11|구간 간 복귀 우선순위 전이|v2.3 23장|Inventory/EXP 22|ALREADY_CAPTURED|유지|
|H12|전멸구간 경계번호 우선|v2.3 폐기 목록|정확한 개별 행 없음|DEPRECATED_HISTORICAL|HD-001 폐기 보존|
|H13|교차조건 개수가 많은 번호 우선|v2.3 폐기 목록|정확한 개별 행 없음|DEPRECATED_HISTORICAL|HD-002 폐기 보존|
|H14|단순 핫번호·콜드번호|v2.3 폐기 목록|Inventory 82|ALREADY_CAPTURED|폐기 유지|
|H15|5단위·끝수 강제 압축|v2.3 폐기 목록|정확한 개별 행 없음|DEPRECATED_HISTORICAL|HD-003 폐기 보존|
|H16|격회 재출현 직접 가산|v2.3 폐기 목록|정확한 개별 행 없음|DEPRECATED_HISTORICAL|HD-004 폐기 보존|
|H17|홀짝·고저·총합·연속수·이월수 강제|v2.3 폐기 목록|Inventory 83|ALREADY_CAPTURED|폐기 유지|
|H18|장기 미출현 자동 반등|v2.3 폐기 목록|Inventory 84|ALREADY_CAPTURED|폐기 유지|
|H19|과거 동일 조합 영구 제외|v2.3 폐기 목록|Inventory 85|ALREADY_CAPTURED|폐기 유지|
|H20|OMR·손가락 동선|v2.3 폐기 목록|Inventory 77~78, CROWD EXP|ALREADY_CAPTURED|DRAW 폐기/CROWD 분리 유지|
|H21|타 AI 번호 역삭제|v2.3 폐기 목록|정확한 개별 행 없음|DEPRECATED_HISTORICAL|HD-005 폐기 보존|
|H22|근거 없는 확률·점수·가중치|v2.3 폐기 목록|일반 금지 원칙만 존재|DEPRECATED_HISTORICAL|HD-006 폐기 보존|
|H23|난수·의사난수 추천|v2.3 폐기 목록|Inventory 86|ALREADY_CAPTURED|폐기 유지|
|H24|탐색가족 사전등록|v2.7.1 34장|Inventory 70|PARTIALLY_CAPTURED|HR-003 검토|
|H25|중첩 워크포워드|v2.7.1 35장|Inventory walkforward 연구|ALREADY_CAPTURED|유지|
|H26|전체 엔진 귀무감사|v2.7.1 36장|Inventory 68/EXP 35|ALREADY_CAPTURED|유지|
|H27|선정 안정성 감사|v2.7.1 37장|Inventory 87로 최종 반영|RECOVERED_MISSING_IDEA|공식 연구 PARTIAL로 통합; Experiment 추가 없음|
|H28|위약·음성 대조|v2.7.1 38장|Inventory 69/EXP 36|ALREADY_CAPTURED|유지|
|H29|봉인 전진장부|v2.7.1 39장|예측 잠금·공식 장부|ALREADY_CAPTURED|유지|
|H30|탐색가족 변경 시 감사 무효화|v2.7.1 34장|규칙 장부/Inventory 70|PARTIALLY_CAPTURED|HR-007 검토|
|H31|강세 지속 대 강세 붕괴|v2.3 11장|최근10·구조붕괴|PARTIALLY_CAPTURED|HR-004 검토|
|H32|결손 회복 대 결손 확대|v2.3 11장|결손 회복 연구|PARTIALLY_CAPTURED|HR-005 검토|
|H33|과밀 지속 대 정상화|v2.3 11장 문맥|구조붕괴 연구|PARTIALLY_CAPTURED|HR-006 검토|
|H34|AUDIT terminal transition workflow|research_review|운영 상태 전환|AMBIGUOUS|연구/구현 경계 검토|
|H35|legacy TRIO outcome ordering|research_review|저장 무결성|AMBIGUOUS|연구/결함 경계 검토|
|H36|PAIR streaming/batching|research_review|성능 구현|AMBIGUOUS|연구 아님 가능성 큼|

## 합계 검산

`19 + 6 + 1 + 1 + 3 + 6 = 36`

이 대조표는 과거 아이디어의 존재와 현재 보존 여부만 판정한다. 연구 성과, 구현 완료, 공식 승격을 뜻하지 않는다.

최종 반영 후에도 최초 감사 분류는 역사적 발견 기록으로 유지한다. 처리 상태는 Inventory 87 추가, 기존 의미 보강 6건, 신규 Experiment 0건이며 감사는 `CLOSED`다.

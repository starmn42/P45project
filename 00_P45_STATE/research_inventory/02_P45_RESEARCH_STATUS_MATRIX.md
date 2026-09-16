# P45 연구 상태 매트릭스

문서만 있는 항목은 구현으로 인정하지 않았다. 표의 '공식 영향'은 현재 FROZEN 규칙에서의 영향이다.

|ID|연구명|최초/주요 목적|현재 상태|근거 문서|근거 문서 경로|관련 코드|관련 DB|실제 계산|공식 픽 영향|과거 검증|walkforward|무작위 비교|반대 가설|현재 문제점|빠진 부분|향후 연구 가치|권장 조치|우선순위|
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|1|3-unit 연구|3-unit 연구의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|2|5-unit 연구|5-unit 연구의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|3|9-unit 연구|9-unit 연구의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|4|10-unit 연구|10-unit 연구의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|5|끝수 END_DIGIT 연구|끝수 END_DIGIT 연구의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|6|숫자 이동 구조|숫자 이동 구조의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|7|숫자 역할 구조|숫자 역할 구조의 재현 가능한 구조·성과 확인|PARTIAL|현행 구현 근거 없음|—|—|—|일부|아니오|일부|아니오|아니오|아니오|전용 연구·실행 완결성 부족|독립 계산·검증·피드백 연결|중간|EXPERIMENT에서 누락 범위 검증|P2|
|8|회차 간 흔적 구조|회차 간 흔적 구조의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|9|숫자 관계망 구조|숫자 관계망 구조의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|10|구조 이탈·구조 붕괴 신호|구조 이탈·붕괴와 과밀 지속↔정상화 전이를 반대 방향까지 분리 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침; v2.3 반대가설|P45_v2.7.1_Work_UTF8_BOM_CRLF.md; docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|연결|공식 의미 고정|과밀 지속↔정상화 원뜻을 보존하되 새 gate로 사용하지 않음|중간|동결 유지|유지|
|11|전멸구간|전멸구간의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|12|연속 전멸률|연속 전멸률의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|13|전멸 후 다음 회차 재등장률|전멸 후 다음 회차 재등장률의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|14|복귀 깊이 0/1/2|복귀 깊이 0/1/2의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|15|결손 회복속도|결손 회복속도와 반대가설인 결손 확대를 분리 검증|MISSING|v2.3 시험·보류·반대가설 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|예정|코드·DB·검증 흔적 없음|회복·확대 양방향 정의·계산기·장부·백테스트|높음|기존 EXPERIMENT에서 원뜻 보강|P1|
|16|결손 회복 전환점|결손 회복 전환점의 재현 가능한 구조·성과 확인|HOLD|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|보류 조건 미완성|사전등록식·반대가설·검증|중간|HOLD 유지|P2|
|17|가변 전멸구간|가변 전멸구간의 재현 가능한 구조·성과 확인|MISSING|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|18|다중 전멸구간 상호작용|다중 전멸구간 상호작용의 재현 가능한 구조·성과 확인|HOLD|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|보류 조건 미완성|사전등록식·반대가설·검증|중간|HOLD 유지|P2|
|19|이동구간×가변 전멸구간 교차효과|이동구간×가변 전멸구간 교차효과의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|20|한 회차 건너뛰기·격회 재출현|한 회차 건너뛰기·격회 재출현의 재현 가능한 구조·성과 확인|MISSING|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|21|같은 끝자리 회차 연구|같은 끝자리 회차 연구의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|22|끝수 전이 연구|끝수 전이 연구의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|23|전체 데이터 vs 최근 데이터|전체 데이터 vs 최근 데이터의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|24|전체·전반부·후반부|전체·전반부·후반부의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|25|최근100|최근100의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|26|최근50|최근50의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|27|최근20 TEST_ONLY|최근20의 단기 급변을 관찰하되 단독 PASS·FAIL이나 공식 확정에 사용하지 않음|TEST_ACTIVE|v2.7.1 공식 지침; v2.3 시험 연구|P45_v2.7.1_Work_UTF8_BOM_CRLF.md; docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|일부|직접 영향 없음|아니오|아니오|아니오|아니오|최근20 단독 확정 금지|급변 정의·독립 성과는 미완성|중간|TEST_ONLY 유지·원뜻 보강|P2|
|28|쌍둥이 유사 회차|쌍둥이 유사 회차의 재현 가능한 구조·성과 확인|MISSING|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|중간|EXPERIMENT 후보|P2|
|29|구조형 쌍둥이 회차 전이|구조형 쌍둥이 회차 전이의 재현 가능한 구조·성과 확인|HOLD|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|아니오|아니오|아니오|아니오|아니오|아니오|보류 조건 미완성|사전등록식·반대가설·검증|중간|HOLD 유지|P2|
|30|유사 회차 이후 다음 회차 전이|유사 회차 이후 다음 회차 전이의 재현 가능한 구조·성과 확인|HOLD|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|아니오|아니오|아니오|아니오|아니오|아니오|보류 조건 미완성|사전등록식·반대가설·검증|중간|HOLD 유지|P2|
|31|반대 가설 동시 검증|반대 가설 동시 검증의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|예|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|32|UNIT 충돌 연구|UNIT 충돌 연구의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|연결|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|33|다중 UNIT 일치 연구|다중 UNIT 일치 연구의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|예|예|일부|아니오|아니오|연결|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|34|특정 UNIT만 일시적으로 강한 경우|특정 UNIT만 일시적으로 강한 경우의 재현 가능한 구조·성과 확인|PARTIAL|v2.7.1 공식 지침|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/units; unit_states.py; unit_relations.py|unit_definition; unit_round_metric; unit_number_metric; unit_relation|일부|아니오|일부|아니오|아니오|아니오|전용 연구·실행 완결성 부족|독립 계산·검증·피드백 연결|중간|EXPERIMENT에서 누락 범위 검증|P2|
|35|NUMBER 역할|NUMBER 역할의 재현 가능한 구조·성과 확인|PARTIAL|v2.7.2 NUMBER 지침|P45_v2.7.2_Number_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/number_engine.py; number_store.py|number_ledger|일부|아니오|일부|아니오|아니오|아니오|전용 연구·실행 완결성 부족|독립 계산·검증·피드백 연결|중간|EXPERIMENT에서 누락 범위 검증|P2|
|36|복귀 역할|복귀 역할의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.2 NUMBER 지침|P45_v2.7.2_Number_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/number_engine.py; number_store.py|number_ledger|예|예|일부|아니오|아니오|연결|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|37|비복귀 역할|비복귀 역할의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.2 NUMBER 지침|P45_v2.7.2_Number_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/number_engine.py; number_store.py|number_ledger|예|예|일부|아니오|아니오|연결|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|38|다중 역할|다중 역할의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.2 NUMBER 지침|P45_v2.7.2_Number_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/number_engine.py; number_store.py|number_ledger|예|예|일부|아니오|아니오|연결|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|39|역할 중복|역할 중복의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.2 NUMBER 지침|P45_v2.7.2_Number_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/number_engine.py; number_store.py|number_ledger|예|예|일부|아니오|아니오|연결|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|40|역할 충돌|역할 충돌의 재현 가능한 구조·성과 확인|PARTIAL|v2.7.2 NUMBER 지침|P45_v2.7.2_Number_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/number_engine.py; number_store.py|number_ledger|일부|아니오|일부|아니오|아니오|아니오|전용 연구·실행 완결성 부족|독립 계산·검증·피드백 연결|중간|EXPERIMENT에서 누락 범위 검증|P2|
|41|숫자 동시출현 관계|숫자 동시출현 관계의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|42|A 출현 후 다음 회차 B 관계|A 출현 후 다음 회차 B 관계의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|43|2회 간격 관계|2회 간격 관계의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|44|3개 숫자 관계망|3개 숫자 관계망의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|45|조건부 관계망|조건부 관계망의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|46|최근100 관계망|최근100 관계망의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|47|최근50 관계망|최근50 관계망의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|48|전체 관계망|전체 관계망의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|높음|EXPERIMENT 후보|P1|
|49|TRIO 3/3|TRIO 3/3의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.3 TRIO 지침|P45_v2.7.3_TRIO_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/trio_engine.py; trio_store.py|trio_ledger; trio_*|예|예|예|예|예|연결|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|50|TRIO exact 2/3 SUPPORT|TRIO exact 2/3 SUPPORT의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.3 TRIO 지침|P45_v2.7.3_TRIO_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/trio_engine.py; trio_store.py|trio_ledger; trio_*|예|예|예|예|예|연결|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|51|TRIO 역할 분산|TRIO 역할 분산의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.3 TRIO 지침|P45_v2.7.3_TRIO_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/trio_engine.py; trio_store.py|trio_ledger; trio_*|예|예|예|예|예|연결|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|52|TRIO 근거 중복|TRIO 근거 중복의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.3 TRIO 지침|P45_v2.7.3_TRIO_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/trio_engine.py; trio_store.py|trio_ledger; trio_*|예|예|예|예|예|연결|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|53|TRIO 구조 위험|TRIO 구조 위험의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.3 TRIO 지침|P45_v2.7.3_TRIO_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/trio_engine.py; trio_store.py|trio_ledger; trio_*|예|예|예|예|예|연결|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|54|TRIO 반대가설|TRIO 반대가설의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.3 TRIO 지침|P45_v2.7.3_TRIO_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/trio_engine.py; trio_store.py|trio_ledger; trio_*|예|예|예|예|예|예|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|55|비중복 PAIR|비중복 PAIR의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.4 PAIR 지침|P45_v2.7.4_PAIR_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/pairs|pair_*|예|예|예|예|예|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|56|PAIR 역할 분산|PAIR 역할 분산의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.4 PAIR 지침|P45_v2.7.4_PAIR_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/pairs|pair_*|예|예|예|예|예|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|57|PAIR 공동 실패위험|PAIR 공동 실패위험의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.4 PAIR 지침|P45_v2.7.4_PAIR_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/pairs|pair_*|예|예|예|예|예|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|58|PAIR 구조 위험|PAIR 구조 위험의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.4 PAIR 지침|P45_v2.7.4_PAIR_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/pairs|pair_*|예|예|예|예|예|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|59|PAIR 최근성|PAIR 최근성의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.4 PAIR 지침|P45_v2.7.4_PAIR_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/pairs|pair_*|예|예|예|예|예|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|60|PAIR 반대가설|PAIR 반대가설의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|v2.7.4 PAIR 지침|P45_v2.7.4_PAIR_Gate_Amendment_UTF8_BOM_CRLF.md|src/p45_v27/pairs|pair_*|예|예|예|예|예|예|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|61|규칙별 성과 장부|규칙별 성과 장부의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|공식 장부·감사 규칙|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/*walkforward*; audit_store.py|*_walkforward_*; audit_*|예|예|예|예|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|62|실패 원인 복기|실패 원인 복기의 재현 가능한 구조·성과 확인|PARTIAL|공식 장부·감사 규칙|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/*walkforward*; audit_store.py|*_walkforward_*; audit_*|일부|아니오|일부|아니오|아니오|아니오|전용 연구·실행 완결성 부족|독립 계산·검증·피드백 연결|중간|EXPERIMENT에서 누락 범위 검증|P2|
|63|후보 탈락 원인 장부|후보 탈락 원인 장부의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|공식 장부·감사 규칙|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/*walkforward*; audit_store.py|*_walkforward_*; audit_*|예|예|예|예|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|64|결과 전 prediction 잠금|결과 전 prediction 잠금의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|공식 장부·감사 규칙|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/*walkforward*; audit_store.py|*_walkforward_*; audit_*|예|예|예|예|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|65|미래 데이터 차단|미래 데이터 차단의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|공식 장부·감사 규칙|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/*walkforward*; audit_store.py|*_walkforward_*; audit_*|예|예|예|예|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|66|walkforward|walkforward의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|공식 장부·감사 규칙|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/*walkforward*; audit_store.py|*_walkforward_*; audit_*|예|예|예|예|아니오|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|67|무작위 기준 비교|무작위 기준 비교의 재현 가능한 구조·성과 확인|OFFICIAL_ACTIVE|공식 장부·감사 규칙|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/*walkforward*; audit_store.py|*_walkforward_*; audit_*|예|예|예|예|예|아니오|공식 의미 고정|없음(정의 범위)|중간|동결 유지|유지|
|68|전체 엔진 귀무감사|전체 엔진 귀무감사의 재현 가능한 구조·성과 확인|PARTIAL|공식 장부·감사 규칙|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/*walkforward*; audit_store.py|*_walkforward_*; audit_*|일부|아니오|일부|아니오|설계|아니오|전용 연구·실행 완결성 부족|독립 계산·검증·피드백 연결|중간|EXPERIMENT에서 누락 범위 검증|P2|
|69|placebo·permutation 연구|placebo·permutation 연구의 재현 가능한 구조·성과 확인|PARTIAL|공식 장부·감사 규칙|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/*walkforward*; audit_store.py|*_walkforward_*; audit_*|일부|아니오|일부|아니오|설계|아니오|전용 연구·실행 완결성 부족|독립 계산·검증·피드백 연결|중간|EXPERIMENT에서 누락 범위 검증|P2|
|70|과최적화 방지 연구|탐색가족을 결과 전에 사전등록하고 폐기 규칙까지 보존하며, 탐색가족 변경 시 기존 감사 인증을 무효화하고 재인증|PARTIAL|공식 장부·감사 규칙 34장|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|src/p45_v27/*walkforward*; audit_store.py|*_walkforward_*; audit_*|일부|아니오|일부|아니오|설계|연결|탐색가족 장부·변경 무효화의 실제 완결 실행 증거 부족|SEARCH_FAMILY manifest/hash와 변경→무효화→재인증 장부 완결성|중간|기존 연구 의미 보강; 별도 중복 연구 생성 금지|P2|
|71|숫자 간격 구조|숫자 간격 구조의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|중간|EXPERIMENT 후보|P2|
|72|등차수열형 구조|등차수열형 구조의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|중간|EXPERIMENT 후보|P2|
|73|+13·+14 특정 간격 패턴|+13·+14 특정 간격 패턴의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|중간|EXPERIMENT 후보|P2|
|74|간격 분산 연구|간격 분산 연구의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|중간|EXPERIMENT 후보|P2|
|75|대중 번호 선택 행동|대중 번호 선택 행동의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|중간|EXPERIMENT 후보|P2|
|76|많이 고르는 번호·패턴|많이 고르는 번호·패턴의 재현 가능한 구조·성과 확인|MISSING|현행 구현 근거 없음|—|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|중간|EXPERIMENT 후보|P2|
|77|OMR 시각 패턴|OMR 시각 패턴의 재현 가능한 구조·성과 확인|DEPRECATED|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|공식 금지 또는 확률 근거 없음|정의·계산기·장부·백테스트|낮음/당첨금 분산 연구로만 제한|폐기 유지|P4|
|78|OMR 물리 좌표|OMR 물리 좌표의 재현 가능한 구조·성과 확인|DEPRECATED|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|공식 금지 또는 확률 근거 없음|정의·계산기·장부·백테스트|낮음/당첨금 분산 연구로만 제한|폐기 유지|P4|
|79|최근10 강도 지속|최근10 강세 지속과 반대가설인 강세 붕괴를 분리 검증|MISSING|v2.3 시험·반대가설 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|예정|코드·DB·검증 흔적 없음|지속·붕괴 양방향 정의·계산기·장부·백테스트|중간|기존 EXPERIMENT에서 원뜻 보강|P2|
|80|비전멸 전용 엔진|비전멸 전용 엔진의 재현 가능한 구조·성과 확인|MISSING|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|코드·DB·검증 흔적 없음|정의·계산기·장부·백테스트|중간|EXPERIMENT 후보|P2|
|81|구간별 복귀우선 전이|구간별 복귀우선 전이의 재현 가능한 구조·성과 확인|HOLD|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|보류 조건 미완성|사전등록식·반대가설·검증|중간|HOLD 유지|P2|
|82|핫·콜드 강제선정|핫·콜드 강제선정의 재현 가능한 구조·성과 확인|DEPRECATED|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|공식 금지 또는 확률 근거 없음|정의·계산기·장부·백테스트|낮음/당첨금 분산 연구로만 제한|폐기 유지|P4|
|83|홀짝·고저·합·연번·이월 강제|홀짝·고저·합·연번·이월 강제의 재현 가능한 구조·성과 확인|DEPRECATED|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|공식 금지 또는 확률 근거 없음|정의·계산기·장부·백테스트|낮음/당첨금 분산 연구로만 제한|폐기 유지|P4|
|84|장기미출 자동반등|장기미출 자동반등의 재현 가능한 구조·성과 확인|DEPRECATED|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|공식 금지 또는 확률 근거 없음|정의·계산기·장부·백테스트|낮음/당첨금 분산 연구로만 제한|폐기 유지|P4|
|85|과거조합 영구배제|과거조합 영구배제의 재현 가능한 구조·성과 확인|DEPRECATED|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|공식 금지 또는 확률 근거 없음|정의·계산기·장부·백테스트|낮음/당첨금 분산 연구로만 제한|폐기 유지|P4|
|86|무작위·의사무작위 추천|무작위·의사무작위 추천의 재현 가능한 구조·성과 확인|DEPRECATED|v2.3 시험·보류·폐기 목록|docs/P45_v2.3_Work_UTF8_BOM_CRLF.md|—|—|아니오|아니오|아니오|아니오|아니오|아니오|공식 금지 또는 확률 근거 없음|정의·계산기·장부·백테스트|낮음/당첨금 분산 연구로만 제한|폐기 유지|P4|
|87|선정 안정성 감사|12개 고정 시나리오에서 선택쌍·순위 백분위·번호 재선정 수와 UNIT/TRIO/PAIR 상태 변화를 감사|PARTIAL|v2.7.1 공식 지침 37장|P45_v2.7.1_Work_UTF8_BOM_CRLF.md|audit 연구 골격|audit_*|일부|핵심 선택 변경 없음|설계|아니오|시나리오 감사|연결|공식 연구 정의는 존재하나 실제 전체 안정성 감사 완료 장부 미확인|12개 시나리오 실행·STABLE/BORDERLINE/UNSTABLE 완료 근거|높음|공식 연구로 보존; 새 Experiment 중복 등록 금지|P2|

## 합계

OFFICIAL_ACTIVE 39 / PARTIAL 9 / TEST_ACTIVE 1 / HOLD 5 / DEPRECATED 7 / MISSING 26 / UNKNOWN 0 / 총 87.

## 연구영역 해석 보완

- 75~76은 `CROWD` 또는 `PRIZE_SHARE` 연구 후보이며 DRAW 예측효과로 분류하지 않는다.
- 77~78의 DEPRECATED는 OMR이 추첨 확률을 높인다는 공식 예측 연구에 대한 판정이다.
- OMR의 대중 선택 편향을 조사하려면 별도 `CROWD` EXPERIMENT ID로 등록해야 하며, 기존 DEPRECATED 판정을 뒤집지 않는다.
- 판매량 보정 WINNER_DENSITY와 LOW/NORMAL/HIGH WINNER는 `PRIZE_SHARE` 소속 신규 Registry 후보로만 관리한다.
- 87 `선정 안정성 감사`는 v2.7.1에 이미 존재하는 공식 감사 연구이므로 새 Experiment를 만들지 않는다.

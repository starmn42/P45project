# P45 Gate·Threshold 요약

상태: 기존 공식 규칙 추출본  
새 규칙: 0건

## UNIT 상태

근거: `P45_v2.7.1_Work_UTF8_BOM_CRLF.md` 부록 A, `src/p45_v27/unit_states.py`.

- 회차 R은 1~R-1만 사용한다.
- 이론 기준은 통합 `7/45`, 본번호 `6/45`, 보너스 `1/45`이다.
- Wilson 95% 구간을 사용한다.
- 정확 점유벡터 표본: 충분 20 이상, 경계 10~19.
- 로컬 그룹 문맥 표본: 충분 30 이상, 경계 20~29.
- 최근100: 공식 15 이상, 경계 8~14. 최근50: 공식 8 이상, 경계 5~7. 최근20은 TEST_ONLY다.
- 공식 20단계 독립 관문으로 UNIT_PASS·WEAKEN·TEST·HOLD·FAIL을 판정한다.
- 다섯 단위는 독립이며 점수·가중치로 합산하지 않는다.

판정: `ALREADY_EXISTS`.

## UNIT 관계·충돌·Pareto

근거: 같은 부록 A.13, `src/p45_v27/unit_relations.py`.

- 고정 저장 순서는 UNIT_3, UNIT_5, UNIT_9, UNIT_10, END_DIGIT이며 우선순위가 아니다.
- 누락은 INCOMPLETE, 지지와 강한 반대가 함께 있으면 CONFLICT, 전부 PASS/WEAKEN이면 CONSENSUS, 일부 지지는 PARTIAL, 지지 없음은 NO_SUPPORT다.
- 원자료·관련근거·독립 문맥근거·중복근거를 분리 보존한다.
- Pareto는 다섯 상태를 성분별로 비교한다. 하나도 나쁘지 않고 최소 하나가 더 좋을 때만 지배한다.

판정: `ALREADY_EXISTS`.

## NUMBER

근거: `P45_v2.7.2_Number_Gate_Amendment_UTF8_BOM_CRLF.md`, `src/p45_v27/number_engine.py`.

- 우선순위: SYSTEM/DATA 오류 → FAIL → HOLD → PASS → WEAKEN → TEST → RETIRED.
- NUMBER_PASS는 공식 PG 18개를 모두 통과해야 한다.
- 핵심 수치에는 primary 전체 표본 30 이상, 통합 전체 `7/45 + 0.015` 이상, 최근100 표본 15 이상·비율 `7/45` 이상, 최근50 표본 8 이상·비율 `7/45 - 0.02` 이상, 본번호 전체 `6/45` 이상이 포함된다.
- UNIT 관계 INCOMPLETE/NO_SUPPORT, Pareto, 보너스 과의존, 반대위험, 구조 붕괴, 결정론, gate order를 별도 관문으로 확인한다.
- 후보군은 최대 12개이며 공식 14-key 사전식 순서를 사용한다. 숨은 tie key는 없다.

판정: `ALREADY_EXISTS`.

## PAIR

근거: `P45_v2.7.4_PAIR_Gate_Amendment_UTF8_BOM_CRLF.md`, 공식 Timing/Sequence/Signature PATCH, `src/p45_v27/pairs/decision.py`.

- 상태 우선순위: SYSTEM_HOLD → RESEARCH_HOLD → READY → TEST_READY.
- READY는 PG01~PG14 전부 PASS일 때만 가능하다.
- TEST_READY는 공식 정의 범위만 허용하며 PG07/PG08 예외는 READY 승격이 아니다.
- RESEARCH_HOLD에는 유효 TRIO 부족, 겹침, exposure 50 미만, HIGH/SEVERE 위험, 보너스 과의존, 확정 열세, 최근 붕괴 등이 포함된다.
- structural Pareto는 공식 7차원이며 성과율과 p-value를 섞지 않는다.
- ranking은 공식 15-key와 마지막 canonical pair key를 사용한다.
- 50/200 exposure 기준, 3/3 PRIMARY와 exact 2/3 SUPPORT 분리는 유지한다.

판정: `ALREADY_EXISTS`.


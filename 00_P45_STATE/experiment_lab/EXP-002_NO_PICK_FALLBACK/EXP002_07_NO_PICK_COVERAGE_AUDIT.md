# EXP-002 NO-PICK Coverage Audit

- source range: `43~1235`
- first eligible PAIR round: `369`
- warmup: `43~368` (`326` rounds, NO-PICK 통계 제외)
- valid rounds: `867`
- output available: `0`
- RESEARCH_NO_PICK: `867`
- output coverage rate: `0.0000%`
- no-pick rate: `100.0000%`
- future leakage: `0`
- system error rounds: `0`

## 중단 단계

- NUMBER_STAGE_STOP: `104`
- TRIO_STAGE_STOP: `492`
- PAIR_STAGE_STOP: `13`
- CORE_STAGE_STOP: `258`

## 세부 빈도

- NUMBER_PASS = 0: `806/867`
- NUMBER_PASS < 3: `847/867`
- valid TRIO = 0: `595/867`
- valid TRIO = 1: `1/867`
- eligible PAIR = 0: `609/867`

## 연속·최근

- max consecutive NO-PICK: `867`
- average consecutive NO-PICK: `867.0`
- recent50 NO-PICK: `100.0000%`
- recent100 NO-PICK: `100.0000%`
- recent200 NO-PICK: `100.0000%`

## 1238 판정

`NORMAL`. 현재 공식 규칙과 비교하면 1238 NO-PICK은 드문 예외가 아니다. 유효 역사 회차의 공식 출력 가용성이 0%였으므로 구조적·반복적 현상이다. 이 판정은 gate 완화나 fallback 성과를 의미하지 않는다.

- audit_id: `5b3905bd-d717-4db2-b641-22e24bae7ee5`
- records hash: `ba77b407b8f7991ff1da511976b50994e297d83576d485cd7e417e965eee0b21`
- audit hash: `26718433a8ceeba2545ac01e8757841290b61504c5736c539f25ceaf046cb0a2`
- machine report: `v27_storage/experiments/exp002/audit/no_pick_coverage_audit.json`
- per-round CSV: `v27_storage/experiments/exp002/audit/no_pick_coverage_rounds.csv`

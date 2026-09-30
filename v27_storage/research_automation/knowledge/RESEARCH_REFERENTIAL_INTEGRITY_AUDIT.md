# Research Referential Integrity Audit Report V1.0

- **기준일:** 2026-09-30
- **Final Verdict:** **`PASS_REFERENTIAL_INTEGRITY`**
- **총 원천 연구 항목(Total Source Items):** **115건**
- **정식 레지스트리 참조 검증:** 총 69건 중 **69건 정상 해결**, 무효 0건, 모호 0건
- **ALIAS 감사 결과:** 총 6건 중 **유효(VALID) 6건**, 무효(INVALID) 0건, 모호(AMBIGUOUS) 0건
- **MERGED 감사 결과:** 총 2건 중 **유효(VALID) 2건**, 무효(INVALID) 0건, 모호(AMBIGUOUS) 0건

---

## Alias Audit Details

| # | Source Item ID | Target Registry ID | Target Exists | Semantic Match | Lineage Evidence | Verdict |
|---|---|---|---|---|---|---|
| 1 | `SRC-NONEXP-20` | `EXP-DRAW-20260824-010-V1` | `True` | `True` | Supporting deterministic validation lineage for formal repair EXP-DRAW-20260824-010-V1 (OFFICIAL PAIR LIFECYCLE REPAIR APPLY AUDIT 001) | **`VALID_ALIAS`** |
| 2 | `SRC-NONEXP-23` | `EXP-CROWD-20260816-001-V1` | `True` | `True` | Crowd topology 001 supporting audit lineage of formal experiment | **`VALID_ALIAS`** |
| 3 | `SRC-NONEXP-24` | `EXP-CROWD-20260816-002-V1` | `True` | `True` | Crowd topology 002 independent calibration lineage of formal experiment | **`VALID_ALIAS`** |
| 4 | `SRC-NONEXP-25` | `EXP-CROWD-20260816-003-V1` | `True` | `True` | Crowd topology 003 methodology supporting lineage of formal experiment | **`VALID_ALIAS`** |
| 5 | `SRC-NONEXP-26` | `EXP-CROWD-20260816-004-V1` | `True` | `True` | Crowd retail 001 calibration lineage of formal experiment | **`VALID_ALIAS`** |
| 6 | `SRC-NONEXP-27` | `EXP-PRIZE-20260816-001-V1` | `True` | `True` | Prize-share 001/002 historical validation and prospective lineage | **`VALID_ALIAS`** |

---

## Merged Audit Details

| # | Source Item ID | Target Registry ID | Target Exists | Same Lineage | Evidence | Verdict |
|---|---|---|---|---|---|---|
| 1 | `SRC-NONEXP-21` | `EXP-DRAW-20260824-010-V1` | `True` | `True` | DECISION-20260824-095 official repair change-control facet | **`VALID_MERGE`** |
| 2 | `SRC-NONEXP-22` | `EXP-DRAW-20260824-010-V1` | `True` | `True` | DECISION-20260824-095 official repair change-control facet | **`VALID_MERGE`** |

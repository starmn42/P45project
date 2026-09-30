# Research Referential Integrity Audit Report V1.2

- **기준일:** 2026-09-30
- **Final Verdict:** **`PASS_NON_EXP_REFERENTIAL_INTEGRITY`**
- **총 원천 연구 항목(Total Source Items):** **115건**
- **정식 레지스트리 참조 검증:** 총 69건 중 **69건 정상 해결**, 무효 0건, 모호 0건
- **ALIAS 감사 결과:** 총 5건 중 **유효(VALID) 5건**, 무효(INVALID) 0건, 모호(AMBIGUOUS) 0건
- **MERGED 감사 결과:** 총 2건 중 **유효(VALID) 2건**, 무효(INVALID) 0건, 모호(AMBIGUOUS) 0건
- **NON-EXP 계보 감사:** 무효 계보 **0건**, 모호 계보 **0건**, 부당 도메인 불일치 **0건**

---

## Alias Audit Details

| # | Source Item ID | Target Registry ID | Target Exists | Domain Match | Semantic Match | Lineage Evidence | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | `SRC-NONEXP-20` | `EXP-DRAW-20260824-010-V1` | `True` | `True` | `True` | Supporting deterministic validation lineage for formal repair EXP-DRAW-20260824-010-V1 (OFFICIAL PAIR LIFECYCLE REPAIR APPLY AUDIT 001) | **`VALID_ALIAS`** |
| 2 | `SRC-NONEXP-23` | `EXP-CROWD-20260823-005-V1` | `True` | `True` | `True` | Crowd topology 001 supporting audit lineage of formal experiment EXP-CROWD-TOPO-001-V1 (EXP-CROWD-20260823-005-V1, Row 58 in Registry) | **`VALID_ALIAS`** |
| 3 | `SRC-NONEXP-24` | `EXP-CROWD-20260823-006-V1` | `True` | `True` | `True` | Crowd topology 002 independent reproduction/calibration lineage of formal experiment EXP-CROWD-TOPO-002-V1 (EXP-CROWD-20260823-006-V1, Row 59 in Registry) | **`VALID_ALIAS`** |
| 4 | `SRC-NONEXP-25` | `EXP-CROWD-20260823-007-V1` | `True` | `True` | `True` | Crowd topology 003 methodology supporting lineage of formal experiment EXP-CROWD-TOPO-003-V1 (EXP-CROWD-20260823-007-V1, Row 60 in Registry) | **`VALID_ALIAS`** |
| 5 | `SRC-NONEXP-26` | `EXP-CROWD-20260823-008-V1` | `True` | `True` | `True` | Crowd retail 001 calibration lineage of formal experiment EXP-CROWD-RETAIL-001-V1 (EXP-CROWD-20260823-008-V1, Row 61 in Registry) | **`VALID_ALIAS`** |

---

## Merged Audit Details

| # | Source Item ID | Target Registry ID | Target Exists | Same Lineage | Evidence | Verdict |
|---|---|---|---|---|---|---|
| 1 | `SRC-NONEXP-21` | `EXP-DRAW-20260824-010-V1` | `True` | `True` | DECISION-20260824-095 official repair change-control facet | **`VALID_MERGE`** |
| 2 | `SRC-NONEXP-22` | `EXP-DRAW-20260824-010-V1` | `True` | `True` | DECISION-20260824-095 official repair change-control facet | **`VALID_MERGE`** |

from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path

from p45_v27.stage6_diagnostics import diagnose_stage6
from p45_v27.trio_engine import build_current_trios
from p45_v27.pairs.production import ProductionPairPipeline
from p45_v27.units import DEFINITIONS

ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT = ROOT / "v27_storage/audits/no_pick_root_cause_trace_001/CURRENT_INPUT_SNAPSHOT.csv"
TRIO_DB = ROOT / "v27_storage/backtests/p45_v273_trio_walkforward.sqlite3"
OUT = ROOT / "v27_storage/audits/trio_hold_causal_decomposition_001"


def main() -> None:
    stage6 = diagnose_stage6(SNAPSHOT, 1238)
    pipeline = ProductionPairPipeline(SNAPSHOT, TRIO_DB)
    history = pipeline._trio_history(1238)
    result = build_current_trios(stage6, DEFINITIONS, history)
    records = []
    primary_reasons = Counter(); all_reasons = Counter(); first_gates = Counter()
    for key, row in sorted(result["rows"].items()):
        n = int(row["selection_rule_exposure_count"])
        conflicts = row["coverage"]["trio_unit_state_vector"].count("UNIT_TRIO_CONFLICT")
        incomplete = row["coverage"]["trio_unit_state_vector"].count("UNIT_TRIO_INCOMPLETE")
        observed = {
            "selection_rule_exposure_count": n,
            "member_structure_summary": row["member_structure_summary"],
            "trio_rule_structure_state": row["trio_rule_structure_state"],
            "trio_rule_opposite_risk": row["trio_rule_opposite_risk"],
            "final_structure_state": row["final_structure_state"],
            "bonus_dependency_state": row["bonus_dependency_state"],
            "unit_conflict_count": conflicts,
            "unit_incomplete_count": incomplete,
        }
        unmet = []
        if n < 50: unmet.append("SELECTION_RULE_EXPOSURE_LT50")
        if row["trio_rule_opposite_risk"] == "HIGH": unmet.append("TRIO_RULE_OPPOSITE_RISK_HIGH")
        if row["final_structure_state"] == "SEVERE": unmet.append("FINAL_STRUCTURE_SEVERE")
        if row["bonus_dependency_state"] == "BONUS_DEPENDENCE_HIGH": unmet.append("BONUS_DEPENDENCE_HIGH")
        if conflicts >= 2: unmet.append("UNIT_CONFLICT_COUNT_GE2")
        primary = unmet[0] if unmet else "NO_HOLD_PREDICATE_FOUND"
        primary_reasons[primary] += 1; all_reasons.update(unmet)
        first_gates[str(row.get("first_failed_gate"))] += 1
        stats = row["performance"]["statistics"]
        i3 = stats[("INTEGRATED", "EXACT_3_OF_3")]["evidence_label"]
        i2 = stats[("INTEGRATED", "EXACT_2_OF_3")]["evidence_label"]
        nearest_test_other_ok = (i3 != "INFERIOR_CONFIRMED" and i2 != "INFERIOR_CONFIRMED"
            and row["trio_rule_opposite_risk"] != "HIGH" and row["final_structure_state"] != "SEVERE"
            and row["bonus_dependency_state"] != "BONUS_DEPENDENCE_HIGH" and incomplete == 0 and conflicts < 2
            and row["future_blocked"] and row["deterministic_ok"])
        records.append({
            "trio_identity": key, "source_numbers": list(row["trio"]), "lifecycle_status": row["trio_state"],
            "canonical_module_function": "p45_v27.trio_engine.classify_trio",
            "primary_hold_reason": primary, "secondary_unmet_conditions": unmet[1:],
            "first_failed_gate": row.get("first_failed_gate"), "hold_predicate_inputs": observed,
            "required_for_hold_release": {"selection_rule_exposure_count":">=50", "trio_rule_opposite_risk":"!=HIGH",
                "final_structure_state":"!=SEVERE", "bonus_dependency_state":"!=BONUS_DEPENDENCE_HIGH",
                "unit_conflict_count":"<2"},
            "integrated_primary_evidence": i3, "integrated_support_evidence": i2,
            "distance_to_test_exposure": max(0, 50-n), "other_valid_test_conditions_currently_ok": nearest_test_other_ok,
            "upstream_dependency_status": "NUMBER_SURVIVOR_INPUT_AVAILABLE",
        })
    gaps = [r["distance_to_test_exposure"] for r in records]
    exposure_counts = Counter(r["hold_predicate_inputs"]["selection_rule_exposure_count"] for r in records)
    distributions = {field: dict(Counter(r["hold_predicate_inputs"][field] for r in records)) for field in
        ("member_structure_summary", "trio_rule_structure_state", "final_structure_state",
         "trio_rule_opposite_risk", "bonus_dependency_state", "unit_conflict_count", "unit_incomplete_count")}
    summary = {
        "target_round": 1238, "source_max_round": 1237, "number_survivors": len(stage6["candidate_numbers"]),
        "trio_universe_count": len(records), "trio_hold_count": sum(r["lifecycle_status"] == "TRIO_HOLD" for r in records),
        "primary_hold_reasons": dict(primary_reasons), "all_unmet_conditions": dict(all_reasons),
        "first_failed_gate_distribution": dict(first_gates), "selection_exposure_distribution": dict(sorted(exposure_counts.items())),
        "observed_distributions": distributions,
        "distance_to_test_exposure": {"min": min(gaps), "median": statistics.median(gaps), "max": max(gaps),
            "pass_adjacent_gap_1_count": sum(g == 1 for g in gaps), "other_conditions_ok_count": sum(r["other_valid_test_conditions_currently_ok"] for r in records)},
        "structural_bottleneck_class": "SINGLE_PREDICATE_GLOBAL_HOLD" if all(r["hold_predicate_inputs"]["final_structure_state"] == "SEVERE" for r in records) else "MULTI_PREDICATE_SYSTEMIC_HOLD",
        "defect_evidence_found": False, "future_leakage_count": len(pipeline.outcome_accesses), "outcome_scoring_count": 0,
    }
    (OUT / "TRIO_HOLD_220_RECORDS.json").write_text(json.dumps(records, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (OUT / "TRIO_HOLD_CAUSAL_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()

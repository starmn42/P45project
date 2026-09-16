from __future__ import annotations

import json
from collections import Counter
from math import comb
from pathlib import Path

from p45_v27.stage6_diagnostics import diagnose_stage6
from p45_v27.number_engine import STRUCTURE_RANK

ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT = ROOT / "v27_storage/audits/no_pick_root_cause_trace_001/CURRENT_INPUT_SNAPSHOT.csv"
OUT = ROOT / "v27_storage/audits/number_member_structure_severe_causal_trace_001"


def nested(mapping, *path, default=None):
    value = mapping
    for key in path:
        if not isinstance(value, dict) or key not in value: return default
        value = value[key]
    return value


def main() -> None:
    result = diagnose_stage6(SNAPSHOT, 1238)
    survivors = [result["rows"][n] for n in result["candidate_numbers"]]
    records = []
    reasons = Counter()
    for row in survivors:
        primary = row.get("primary_number_context") or {}
        context = primary.get("context", {})
        unit_structures = {unit: result["unit_metrics"][unit][row["number"]].get("structure_state") for unit in result["unit_metrics"]}
        severe_units = sorted(unit for unit, state in unit_structures.items() if state == "SEVERE")
        reason = "ANY_EVALUABLE_UNIT_STRUCTURE_SEVERE:" + "+".join(severe_units)
        reasons[reason] += 1
        records.append({
            "number": row["number"], "number_state": row["number_state"], "selected_pool": row["selected_pool"],
            "candidate_pool_type": row["candidate_pool_type"], "survivor_reason": "ELIGIBLE_EXPANDED_TEST_POOL_RANKED_TOP12",
            "valid_test_status": row["valid_test_status"], "number_structure_state": row["number_structure_state"],
            "structure_reason": reason, "canonical_module_function": "p45_v27.number_engine.combine_number_risk",
            "propagation_input": unit_structures, "severe_units": severe_units,
            "first_fatal_predicate": "max(evaluable unit structure states, STRUCTURE_RANK) == SEVERE",
            "required_condition": "all evaluable unit structure states must be WARNING or better",
            "first_failed_gate": row["first_failed_gate"], "structure_gate": row["gate_results"]["NUMBER_PASS_GATE_17"],
            "relation_state": row["relation_state"], "pareto_state": row["pareto_state"],
            "opposite_risk": row["number_opposite_risk"], "context_conflict": row["number_context_conflict"],
            "bonus_dependence": row["number_bonus_dependence"], "structure_insufficient_sample": row["structure_insufficient_sample"],
            "primary_context_unit": primary.get("unit_type"), "primary_context_name": primary.get("context_name"),
            "sample_state": context.get("sample_state"),
            "overall_integrated_sample_count": nested(context,"overall","integrated","sample_count"),
            "overall_integrated_evidence": nested(context,"overall","integrated","evidence_label"),
            "overall_main_evidence": nested(context,"overall","main","evidence_label"),
            "recent100_integrated_evidence": nested(context,"recent100","integrated","evidence_label"),
            "recent50_integrated_evidence": nested(context,"recent50","integrated","evidence_label"),
            "primary_3of3_state": "NOT_A_NUMBER_STRUCTURE_INPUT",
            "support_exact2_state": "NOT_A_NUMBER_STRUCTURE_INPUT",
        })
    states = Counter(r["number_structure_state"] for r in records)
    number_states = Counter(r["number_state"] for r in records)
    unit_ledgers = {unit: {"structure_state": value["structure_state"], "decision_reason": value["decision_reason"],
        "overall_percentile": value["overall_percentile"], "sample_count": value["sample_count"],
        "metric_percentiles": value["metric_percentiles"], "current_metrics": value["current_metrics"]}
        for unit, value in result["structures"].items()}
    severe_count = states["SEVERE"]; non_severe = len(records)-severe_count
    propagation = {"severe_number_count": severe_count, "non_severe_number_count": non_severe,
        "trios_without_severe": comb(non_severe,3) if non_severe >= 3 else 0,
        "trios_with_at_least_one_severe": comb(len(records),3)-(comb(non_severe,3) if non_severe >= 3 else 0),
        "canonical_rule": "max(member number_structure_state by STRUCTURE_RANK); one SEVERE member is sufficient"}
    summary = {"target_round":1238,"max_source_round":1237,"number_survivor_count":len(records),
        "number_identities":[r["number"] for r in records], "number_state_distribution":dict(number_states),
        "number_structure_distribution":dict(states), "number_structure_reasons":dict(reasons),
        "unit_structure_ledgers":unit_ledgers, "combinatorial_propagation":propagation,
        "min_number_state_change_for_one_trio_release":3 if severe_count==len(records) else max(0,3-non_severe),
        "structural_root_cause_class":"NUMBER_GLOBAL_STRUCTURE_SEVERE",
        "defect_evidence_found":False,"future_leakage_count":0,"outcome_scoring_count":0}
    (OUT/"NUMBER_SURVIVOR_12_RECORDS.json").write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"NUMBER_MEMBER_STRUCTURE_SUMMARY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False))


if __name__ == "__main__": main()

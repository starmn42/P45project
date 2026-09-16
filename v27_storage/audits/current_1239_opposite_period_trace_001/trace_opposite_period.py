from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import p45_v27.number_engine as number_engine
from p45_v27.number_engine import decide_number
from p45_v27.stage6_diagnostics import diagnose_stage6
from p45_v27.units import DEFINITIONS

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "v27_storage/audits/current_1239_opposite_period_trace_001"
STAGING = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
EXPECTED_SHA = "1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def period(ctx: dict, name: str) -> dict:
    raw = ctx[name]["integrated"]
    return {"evidence_state": raw["evidence_label"], "sample_count": raw["sample_count"], "rate": raw["rate"]}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    state = json.loads((ROOT / "00_P45_STATE/P45_CURRENT_STATE.json").read_text(encoding="utf-8-sig"))
    if state["state_version"] != "1.0.88" or state["last_decision_id"] != "DECISION-20260824-095" or sha(STAGING) != EXPECTED_SHA:
        raise RuntimeError("STOP_STATE_DRIFT_OR_STAGING_MISMATCH")
    stage6 = diagnose_stage6(STAGING, 1239)
    rows = stage6["rows"]

    affected = []
    for n, row in rows.items():
        if row["number_state"] != "NUMBER_HOLD":
            continue
        primary = row["primary_number_context"]
        ctx = primary["context"]
        if not number_engine._opposite_directions(ctx):
            continue
        overall_label = ctx["overall"]["integrated"]["evidence_label"]
        if overall_label in ("POSITIVE_CONFIRMED", "NEGATIVE_CONFIRMED"):
            continue
        affected.append(n)
    if affected != [2,3,4,6,7,8,10,15,16,17,19,21,22,23,28,29,30,31,32,33,35,36,39,40,42,43,44,45]:
        raise RuntimeError("OPPOSITE_PERIOD_TARGET_SET_MISMATCH")

    shadow_rows = {}
    with patch.object(number_engine, "_opposite_directions", return_value=False):
        for n in range(1, 46):
            row = rows[n]
            metrics = {unit: stage6["unit_metrics"][unit][n] for unit in DEFINITIONS}
            roles = {key: row[key] for key in ("return_roles", "primary_return_role", "role_signature")}
            roles["has_return_role"] = any(item["role_type"].startswith("RETURN_") for item in roles["return_roles"])
            shadow_rows[n] = decide_number(n, metrics, stage6["relations"][n], stage6["pareto"][str(n)], roles)

    full = []
    patterns = Counter()
    for n in affected:
        row = rows[n]
        ctx = row["primary_number_context"]["context"]
        periods = {name: period(ctx, name) for name in ("overall", "recent100", "recent50", "recent20")}
        opposite = "recent100"
        pattern = f"overall:{periods['overall']['evidence_state']}__recent100:{periods['recent100']['evidence_state']}"
        patterns[pattern] += 1
        exact = "OPPOSITE_RISK_HIGH + OPPOSITE_PERIOD_DIRECTIONS" if row["number_opposite_risk"] == "HIGH" else "OPPOSITE_PERIOD_DIRECTIONS"
        full.append({
            "number": n, "primary_unit": row["primary_number_context"]["unit_type"],
            "overall_direction": periods["overall"]["evidence_state"], "periods": periods,
            "period_opposite_to_overall": opposite, "risk": row["number_opposite_risk"],
            "conflict": row["number_context_conflict"], "lifecycle": row["number_state"],
            "first_failed_gate": row["first_failed_gate"], "exact_hold_predicate": exact,
            "shadow_lifecycle_without_opposite_predicate": shadow_rows[n]["number_state"],
            "shadow_eligible": shadow_rows[n]["number_state"] in ("NUMBER_PASS", "NUMBER_WEAKEN") or shadow_rows[n]["valid_test_status"],
        })

    shadow_counts = Counter(row["number_state"] for row in shadow_rows.values())
    shadow_eligible = [n for n, row in shadow_rows.items() if row["number_state"] in ("NUMBER_PASS", "NUMBER_WEAKEN") or row["valid_test_status"]]
    result = {
        "final_verdict": "CURRENT_1239_OPPOSITE_PERIOD_CAUSAL_TRACE_COMPLETE",
        "canonical": {
            "module_function": "p45_v27.number_engine._opposite_directions called by decide_number",
            "predicate": "(rank(overall.integrated.evidence_label)>=4 and rank(recent100.integrated.evidence_label)<=2) or (rank(overall)<=2 and rank(recent100)>=4)",
            "rank_source": "EVIDENCE_RANK; POSITIVE_CONFIRMED=5, POSITIVE_TENTATIVE=4, NEUTRAL=3, NEGATIVE_TENTATIVE=2, NEGATIVE_CONFIRMED=1, INSUFFICIENT=0",
            "source_fields": ["primary_context.overall.integrated.evidence_label", "primary_context.recent100.integrated.evidence_label"],
            "sign_tie_zero": "No numeric sign, tie, or zero-rate comparison. Direction is ordinal evidence-rank polarity only; ranks 3/3 are neither side; equality cannot satisfy both inequalities.",
            "hold_connection": "hold when _opposite_directions(ctx) and overall integrated label not in (POSITIVE_CONFIRMED, NEGATIVE_CONFIRMED)",
            "high_risk_combination": "number_opposite_risk==HIGH is an earlier independent OR term in hold; number 2 satisfies both",
            "predicate_order": "fail evaluated first; then hold OR terms, with HIGH risk before opposite-directions in source order; first_limited_gate reports NUMBER_HOLD_RULE, not an individual OR term",
        },
        "opposite_period_hold_count": len(affected), "high_risk_plus_opposite_count": sum(row["risk"] == "HIGH" for row in full),
        "positive_tentative_count": sum(row["overall_direction"] == "POSITIVE_TENTATIVE" for row in full),
        "patterns": [{"opposite_pattern": key, "count": count, "period_a": "overall", "period_b": "recent100", "canonical_hold_effect": "OPPOSITE_PERIOD_DIRECTIONS OR-term makes HOLD"} for key, count in patterns.most_common()],
        "unique_opposite_pattern_count": len(patterns), "per_number": full,
        "shadow": {"assumption": "_opposite_directions returns false only; all inputs and other predicates unchanged", "number_counts": dict(shadow_counts), "eligible_count": len(shadow_eligible), "eligible_identities": shadow_eligible, "minimum_6_met": len(shadow_eligible) >= 6, "official_selection_generated": False, "official_output_generated": False},
        "opposite_period_predicate_is_necessary_for_current_number_extinction": len(shadow_eligible) >= 6,
        "root_cause_class": "CURRENT_NUMBER_EXTINCTION_CAUSED_BY_PERIOD_STABILITY_FILTER" if len(shadow_eligible) >= 6 else "OPPOSITE_PERIOD_FILTER_NOT_SUFFICIENT",
        "current_partial_survivor_pool": [13,18,20,24,27],
        "partial_survivor_reporting": {"id": "PARTIAL_SURVIVOR_REPORTING", "status": "REPORTING_POLICY_IDEA_REGISTERED", "official_contract_changed": False},
        "defect_evidence_found": False, "future_leakage": 0, "outcome_scoring": 0,
    }
    (OUT / "OPPOSITE_PERIOD_CAUSAL_TRACE.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("final_verdict", "opposite_period_hold_count", "patterns", "shadow", "root_cause_class")}, ensure_ascii=False))


if __name__ == "__main__":
    main()

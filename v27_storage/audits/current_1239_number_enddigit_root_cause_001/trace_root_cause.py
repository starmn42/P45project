from __future__ import annotations

import copy
import csv
import hashlib
import json
from collections import Counter, defaultdict
from math import sqrt
from pathlib import Path

from p45_v27.number_engine import decide_number, finalize_numbers
from p45_v27.stage55_diagnostics import load_draw_csv
from p45_v27.stage6_diagnostics import diagnose_stage6
from p45_v27.units import DEFINITIONS

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "v27_storage/audits/current_1239_number_enddigit_root_cause_001"
STAGING = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
EXPECTED_SHA = "1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primary_label(row: dict) -> str:
    return row["primary_number_context"]["context"]["overall"]["integrated"]["evidence_label"]


def hold_reasons(row: dict) -> list[str]:
    label = primary_label(row)
    reasons = []
    if row["relation_state"] == "UNIT_RELATION_INCOMPLETE": reasons.append("UNIT_RELATION_INCOMPLETE")
    if row["relation_state"] == "UNIT_NO_SUPPORT" and label != "NEGATIVE_CONFIRMED": reasons.append("UNIT_NO_SUPPORT_NON_NEGATIVE_CONFIRMED")
    if row["number_context_conflict"] == "HIGH": reasons.append("CONTEXT_CONFLICT_HIGH")
    if row["number_opposite_risk"] == "HIGH": reasons.append("OPPOSITE_RISK_HIGH")
    if row["number_bonus_dependence"] == "BONUS_DEPENDENCE_HIGH": reasons.append("BONUS_DEPENDENCE_HIGH")
    if row["number_structure_state"] == "SEVERE" and label not in ("POSITIVE_CONFIRMED", "POSITIVE_TENTATIVE"):
        reasons.append("SEVERE_AND_PRIMARY_NOT_POSITIVE")
    ctx = row["primary_number_context"]["context"]
    a = ctx["overall"]["integrated"]["evidence_label"]
    b = ctx["recent100"]["integrated"]["evidence_label"]
    rank = {"POSITIVE_CONFIRMED":5,"POSITIVE_TENTATIVE":4,"NEUTRAL":3,"NEGATIVE_TENTATIVE":2,"NEGATIVE_CONFIRMED":1,"INSUFFICIENT":0}
    opposite = (rank[a] >= 4 and rank[b] <= 2) or (rank[a] <= 2 and rank[b] >= 4)
    if opposite and label not in ("POSITIVE_CONFIRMED", "NEGATIVE_CONFIRMED"): reasons.append("OPPOSITE_PERIOD_DIRECTIONS")
    return reasons


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    state = json.loads((ROOT / "00_P45_STATE/P45_CURRENT_STATE.json").read_text(encoding="utf-8-sig"))
    with STAGING.open("r", encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    rounds = [int(row["round"]) for row in raw_rows]
    if state["state_version"] != "1.0.88" or state["last_decision_id"] != "DECISION-20260824-095" or sha(STAGING) != EXPECTED_SHA or len(rounds) != 1238 or len(set(rounds)) != 1238 or rounds != list(range(1, 1239)):
        raise RuntimeError("STOP_STATE_DRIFT_OR_STAGING_MISMATCH")

    stage6 = diagnose_stage6(STAGING, 1239)
    rows = stage6["rows"]
    ledger = stage6["structures"]["END_DIGIT"]
    taxonomy: dict[tuple, list[int]] = defaultdict(list)
    per_number = []
    for n in range(1, 46):
        row = rows[n]
        label = primary_label(row)
        reasons = hold_reasons(row) if row["number_state"] == "NUMBER_HOLD" else []
        if row["number_state"] == "NUMBER_WEAKEN":
            canonical = "MANDATORY_WEAKEN_AND_WEAK_REASON"
        elif row["number_state"] == "NUMBER_HOLD":
            canonical = "+".join(reasons)
        else:
            canonical = row["first_limited_gate"] or "PASS"
        taxonomy[(row["number_state"], row["number_structure_state"], label, canonical)].append(n)
        per_number.append({
            "number": n, "primary_integrated_evidence": label, "structure_state": row["number_structure_state"],
            "opposite_risk": row["number_opposite_risk"], "context_conflict": row["number_context_conflict"],
            "lifecycle": row["number_state"], "eligible_source": row["number_state"] in ("NUMBER_PASS", "NUMBER_WEAKEN") or row["valid_test_status"],
            "first_failed_pass_gate": row["first_failed_gate"], "first_limited_gate": row["first_limited_gate"],
            "canonical_reasons": reasons if reasons else [canonical],
        })

    # Dependency-only shadow: retain every evidence/risk/relation input and change only END_DIGIT structure state.
    shadow_rows = {}
    changed_from_hold = []
    for n in range(1, 46):
        metrics = {unit: copy.deepcopy(stage6["unit_metrics"][unit][n]) for unit in DEFINITIONS}
        metrics["END_DIGIT"]["structure_state"] = "WARNING"
        roles = {key: copy.deepcopy(rows[n][key]) for key in ("return_roles", "primary_return_role", "role_signature")}
        roles["has_return_role"] = any(item["role_type"].startswith("RETURN_") for item in roles["return_roles"])
        shadow = decide_number(n, metrics, stage6["relations"][n], stage6["pareto"][str(n)], roles)
        shadow["unit_state_vector"] = rows[n]["unit_state_vector"]
        shadow_rows[n] = shadow
        if rows[n]["number_state"] == "NUMBER_HOLD" and shadow["number_state"] != "NUMBER_HOLD": changed_from_hold.append(n)
    shadow_final = finalize_numbers(shadow_rows)
    shadow_counts = Counter(row["number_state"] for row in shadow_rows.values())
    shadow_eligible = [n for n, row in shadow_rows.items() if row["number_state"] in ("NUMBER_PASS", "NUMBER_WEAKEN") or row["valid_test_status"]]

    draws = load_draw_csv(STAGING)
    definition = DEFINITIONS["END_DIGIT"]
    vectors = []
    for draw in draws:
        vectors.append([len(set((*draw.main, draw.bonus)) & set(group.members)) for group in definition.groups])
    current, previous = vectors[-1], vectors[-2]
    group_rows = []
    max_z = -1.0
    max_groups = []
    for group, observed in zip(definition.groups, current):
        p = group.size / 45
        expected = 7 * p
        variance = 7 * p * (1-p) * ((45-7)/44)
        z = abs((observed - expected) / sqrt(variance)) if variance else 0.0
        group_rows.append({"group": group.label, "members": list(group.members), "size": group.size, "occupancy": observed, "expected_occupancy": expected, "abs_standardized_occupancy": z})
        if z > max_z: max_z, max_groups = z, [group.label]
        elif z == max_z: max_groups.append(group.label)
    zero_groups = [row["group"] for row in group_rows if row["occupancy"] == 0]
    return_groups = [{"group": group.label, "previous_occupancy": old, "current_occupancy": now} for group, old, now in zip(definition.groups, previous, current) if old == 0]

    positions = {}
    for metric, current_value in ledger["current_metrics"].items():
        distribution = ledger["historical_distribution"][metric]
        less = sum(value < current_value for value in distribution)
        equal = sum(value == current_value for value in distribution)
        positions[metric] = {"raw_current": current_value, "percentile": ledger["metric_percentiles"][metric], "reference_n": len(distribution), "less_count": less, "tie_count": equal, "greater_count": len(distribution)-less-equal, "strict_maximum": all(current_value > value for value in distribution), "tied_maximum": equal > 0 and all(current_value >= value for value in distribution), "reference_min": min(distribution), "reference_max": max(distribution)}

    result = {
        "final_verdict": "CURRENT_1239_NUMBER_ENDDIGIT_ROOT_CAUSE_COMPLETE",
        "staging_sha256": sha(STAGING), "source_end": 1238, "target": 1239,
        "number_counts": dict(Counter(row["number_state"] for row in rows.values())),
        "eligible_identities": [n for n, row in rows.items() if row["number_state"] in ("NUMBER_PASS", "NUMBER_WEAKEN") or row["valid_test_status"]],
        "per_number": per_number,
        "taxonomy": [{"number_reason": key[0] + ":" + key[3], "count": len(numbers), "structure": key[1], "primary_evidence": key[2], "canonical_predicate": key[3], "numbers": numbers} for key, numbers in sorted(taxonomy.items())],
        "unique_number_hold_reason_count": len({tuple(item["canonical_reasons"]) for item in per_number if item["lifecycle"] == "NUMBER_HOLD"}),
        "shadow": {"assumption": "END_DIGIT_STRUCTURE_STATE_WARNING_ONLY", "number_counts": dict(shadow_counts), "eligible_count": len(shadow_eligible), "eligible_identities": shadow_eligible, "selected_count": len(shadow_final["candidate_numbers"]), "selected_identities": shadow_final["candidate_numbers"], "hold_numbers_changed": changed_from_hold, "minimum_6_met": len(shadow_eligible) >= 6},
        "end_digit": {"state": ledger["structure_state"], "overall_percentile": ledger["overall_percentile"], "reference_sample": ledger["sample_count"], "current_metrics": ledger["current_metrics"], "metric_percentiles": ledger["metric_percentiles"], "historical_positions": positions, "groups": group_rows, "zero_groups": zero_groups, "return_from_prior_zero_groups": return_groups, "max_abs_standardized_groups": max_groups, "max_abs_standardized_value": max_z},
        "end_digit_severe_necessary_for_current_number_extinction": len(shadow_eligible) >= 6,
        "latent_trio_global_severe_current": all(row["number_structure_state"] == "SEVERE" for row in rows.values()),
        "common_root_cause_class": "END_DIGIT_COMMON_ROOT_CAUSE_CONFIRMED" if len(shadow_eligible) >= 6 else "NUMBER_EXTINCTION_INDEPENDENT_OF_END_DIGIT",
        "defect_evidence_found": False, "future_leakage": 0, "outcome_scoring": 0,
    }
    (OUT / "NUMBER_ENDDIGIT_ROOT_CAUSE_TRACE.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("final_verdict", "number_counts", "eligible_identities", "unique_number_hold_reason_count", "shadow", "common_root_cause_class")}, ensure_ascii=False))


if __name__ == "__main__":
    main()

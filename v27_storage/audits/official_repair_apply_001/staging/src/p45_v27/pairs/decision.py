"""Official P45 v2.7.4 PAIR stage-3 deterministic decision primitives."""

from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Any, Iterable, Mapping, Sequence

GATE_IDS = tuple(f"PG{i:02d}" for i in range(1, 15))
RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
STRUCTURE_ORDER = {"NORMAL": 0, "CAUTION": 1, "WARNING": 2, "SEVERE": 3}
UNIT_ORDER = ("UNIT_3", "UNIT_5", "UNIT_9", "UNIT_10", "END_DIGIT")


@dataclass(frozen=True)
class GateResult:
    gate_id: str
    status: str
    reason: str | None = None


def pair_unit_coverage(member_cells: Sequence[Sequence[Mapping[str, Any]]]) -> tuple[dict[str, Any], ...]:
    """Preserve the official 2×3×5 cells and derive only specified counts/vectors."""
    if len(member_cells) != 2 or any(len(member) != 3 for member in member_cells):
        raise ValueError("PAIR_ENGINE_SPEC_CONFLICT:COVERAGE_SHAPE")
    if any(len(number_cells) != 5 for member in member_cells for number_cells in member):
        raise ValueError("PAIR_ENGINE_SPEC_CONFLICT:COVERAGE_SHAPE")
    result = []
    for unit_index, unit in enumerate(UNIT_ORDER):
        cells = [member_cells[m][n][unit_index] for m in range(2) for n in range(3)]
        result.append({
            "unit_type": unit,
            "raw_cells": tuple(dict(cell) for cell in cells),
            "complete_cell_count": sum(cell.get("calculation_status") == "COMPLETE" for cell in cells),
            "support_cell_count": sum(bool(cell.get("support")) for cell in cells),
            "conflict_cell_count": sum(bool(cell.get("conflict")) for cell in cells),
            "distinct_role_count": len({cell.get("role") for cell in cells if cell.get("role") is not None}),
            "shared_evidence_id_count": sum(1 for evidence in set().union(*(set(cell.get("evidence_ids", ())) for cell in cells)) if sum(evidence in cell.get("evidence_ids", ()) for cell in cells) > 1),
        })
    return tuple(result)


def _gate(gate_id: str, value: bool | None, reason: str) -> GateResult:
    return GateResult(gate_id, "INCOMPLETE" if value is None else "PASS" if value else "FAIL", None if value else reason)


def evaluate_gates(data: Mapping[str, Any]) -> tuple[GateResult, ...]:
    """Evaluate exactly PG01..PG14; missing required input is INCOMPLETE."""
    states = data.get("member_states")
    numbers = data.get("member_numbers")
    unit_statuses = data.get("unit_statuses")
    executed = data.get("executed_gate_ids")
    predicates: list[tuple[bool | None, str]] = [
        (None if states is None else tuple(states) == ("TRIO_PASS", "TRIO_PASS"), "PAIR_MEMBER_NOT_BOTH_PASS"),
        (None if numbers is None else not(set(numbers[0]) & set(numbers[1])) and len(set(numbers[0]) | set(numbers[1])) == 6, "PAIR_OVERLAP"),
        (None if unit_statuses is None else len(unit_statuses) == 5 and all(x == "COMPLETE" for x in unit_statuses), "MANDATORY_UNIT_INCOMPLETE"),
        (None if data.get("coverage_complete_cells") is None else data["coverage_complete_cells"] == 30, "PAIR_COVERAGE_INCOMPLETE"),
        (None if data.get("walkforward_prelock_ok") is None else bool(data["walkforward_prelock_ok"]), "LEAKAGE_OR_PRELOCK_FAIL"),
        (None if data.get("selection_exposure") is None else data["selection_exposure"] >= 200, "PAIR_SAMPLE_UNDER_200"),
        (None if data.get("integrated_primary_rate") is None or data.get("integrated_primary_baseline") is None or data.get("integrated_primary_evidence") is None else data["integrated_primary_rate"] > data["integrated_primary_baseline"] and data["integrated_primary_evidence"] != "INFERIOR_CONFIRMED", "PAIR_PRIMARY_BASELINE_FAIL"),
        (None if data.get("main_primary_rate") is None or data.get("main_primary_baseline") is None or data.get("main_primary_evidence") is None else data["main_primary_rate"] >= data["main_primary_baseline"] and data["main_primary_evidence"] != "INFERIOR_CONFIRMED", "PAIR_MAIN_BASELINE_FAIL"),
        (None if data.get("recent_state") is None else data["recent_state"] != "SEVERE", "PAIR_RECENT_COLLAPSE"),
        (None if data.get("final_risk") is None else data["final_risk"] != "HIGH", "PAIR_OPPOSITE_HIGH"),
        (None if data.get("final_structure") is None else data["final_structure"] != "SEVERE", "PAIR_STRUCTURE_SEVERE"),
        (None if data.get("determinism_ok") is None else bool(data["determinism_ok"]), "PAIR_DETERMINISM_FAIL"),
        (None if executed is None else tuple(executed) == GATE_IDS, "PAIR_GATE_SEQUENCE_FAIL"),
        (None if data.get("ledger_complete") is None else bool(data["ledger_complete"]), "PAIR_LEDGER_INCOMPLETE"),
    ]
    return tuple(_gate(gid, value, reason) for gid, (value, reason) in zip(GATE_IDS, predicates))


def pair_risk(member_a: str, member_b: str, *, primary: str, support: str,
              integrated_primary: str, main_primary: str, bonus: str,
              recent: str, conflict_columns: int) -> tuple[str, str, str]:
    member = max((member_a, member_b), key=RISK_ORDER.__getitem__)
    high = (primary == "INFERIOR_CONFIRMED" or
            (integrated_primary.startswith("SUPERIOR_") and support == "INFERIOR_CONFIRMED") or
            bonus == "HIGH" or recent == "SEVERE" or conflict_columns >= 2 or
            (main_primary == "INFERIOR_CONFIRMED" and integrated_primary == "SUPERIOR_CONFIRMED"))
    medium = (member == "MEDIUM" or
              (integrated_primary.startswith("SUPERIOR_") and support == "INFERIOR_TENTATIVE") or
              bonus == "MEDIUM" or recent == "WARNING" or conflict_columns == 1)
    rule = "HIGH" if high else "MEDIUM" if medium else "LOW"
    final = max((member, rule), key=RISK_ORDER.__getitem__)
    return member, rule, final


def recent_support_state(baseline: float, overall_wilson_low: float,
                         recent100: tuple[float, float] | None,
                         recent50: tuple[float, float] | None) -> str:
    limit = max(baseline, overall_wilson_low)
    flags = [window is not None and window[0] < baseline and window[1] < limit for window in (recent100, recent50)]
    return "SEVERE" if all(flags) else "WARNING" if any(flags) else "STABLE"


def bonus_dependence(integrated_evidence: str, main_evidence: str,
                     integrated_positive: bool, main_rate: float, main_baseline: float) -> str:
    if integrated_evidence == "SUPERIOR_CONFIRMED" and main_evidence == "INFERIOR_CONFIRMED":
        return "HIGH"
    if integrated_positive and main_rate < main_baseline and main_evidence != "INFERIOR_CONFIRMED":
        return "MEDIUM"
    return "NONE"


def structure_state(overall: Mapping[str, float], recent100: Mapping[str, float],
                    recent50: Mapping[str, float], history: Sequence[Sequence[float]]) -> tuple[tuple[float, ...], tuple[float, ...], str]:
    metrics = (
        max(0.0, overall["primary"] - recent100["primary"]),
        max(0.0, overall["primary"] - recent50["primary"]),
        max(0.0, overall["support"] - recent100["support"]),
        max(0.0, overall["support"] - recent50["support"]),
        max(0.0, recent50["failure"] - overall["failure"]),
        max(0.0, recent50["conflict"] - overall["conflict"]),
    )
    if len(history) < 50:
        return metrics, (), "INSUFFICIENT_SAMPLE"
    percentiles = tuple(100.0 * sum(row[i] <= metrics[i] for row in history) / len(history) for i in range(6))
    p = max(percentiles)
    state = "NORMAL" if p < 90 else "CAUTION" if p < 95 else "WARNING" if p < 99 else "SEVERE"
    return metrics, percentiles, state


def final_structure(member_a: str, member_b: str, rule: str) -> str:
    actual = [x for x in (member_a, member_b, rule) if x != "INSUFFICIENT_SAMPLE"]
    return max(actual, key=STRUCTURE_ORDER.__getitem__) if actual else "INSUFFICIENT_SAMPLE"


def decide_state(gates: Sequence[GateResult], data: Mapping[str, Any]) -> str:
    by_id = {g.gate_id: g for g in gates}
    if set(by_id) != set(GATE_IDS) or any(g.status == "INCOMPLETE" for g in gates) or any(data.get(x) is False for x in ("signature_ok", "atomic_storage_ok")):
        return "PAIR_SYSTEM_HOLD"
    research = (data.get("valid_trio_count", 2) < 2 or not data.get("disjoint", True) or
                data["selection_exposure"] < 50 or data["final_risk"] == "HIGH" or
                data["final_structure"] == "SEVERE" or data["bonus_dependence"] == "HIGH" or
                data["primary_evidence"] == "INFERIOR_CONFIRMED" or data["support_evidence"] == "INFERIOR_CONFIRMED" or
                data["recent_state"] == "SEVERE" or data["conflict_columns"] >= 2)
    if research:
        return "PAIR_RESEARCH_HOLD"
    failed = {g.gate_id for g in gates if g.status == "FAIL"}
    if not failed:
        return "PAIR_READY"
    members = tuple(data["member_states"])
    member_allowed = all(x in {"TRIO_PASS", "TRIO_WEAKEN", "TRIO_TEST"} for x in members)
    path_a = (any(x != "TRIO_PASS" for x in members) or data.get("pool_type") == "EXPANDED_TEST_POOL" or 50 <= data["selection_exposure"] <= 199)
    path_b = (members == ("TRIO_PASS", "TRIO_PASS") and data["selection_exposure"] >= 200 and
              bool(failed) and failed <= {"PG07", "PG08"} and
              data["integrated_primary_evidence"] != "INFERIOR_CONFIRMED" and data["main_primary_evidence"] != "INFERIOR_CONFIRMED")
    safe = (data.get("members_valid", True) and member_allowed and data["selection_exposure"] >= 50 and
            data["primary_evidence"] != "INFERIOR_CONFIRMED" and data["support_evidence"] != "INFERIOR_CONFIRMED" and
            data["final_risk"] != "HIGH" and data["final_structure"] != "SEVERE" and
            data["bonus_dependence"] != "HIGH" and data["recent_state"] != "SEVERE" and
            data["conflict_columns"] < 2 and all(data.get(x, True) for x in ("walkforward_ok", "determinism_ok", "signature_ok", "prediction_hash_ok", "atomic_storage_ok")))
    return "PAIR_TEST_READY" if safe and (path_a or path_b) else "PAIR_RESEARCH_HOLD"


@dataclass(frozen=True)
class ParetoVector:
    conflict_columns: int
    incomplete_cells: int
    role_diversity: tuple[int, ...]
    evidence_overlap: tuple[int, ...]
    member_risk: str
    rule_risk: str
    final_structure: str


def pareto_dominates(a: ParetoVector, b: ParetoVector) -> bool:
    av = (-a.conflict_columns, -a.incomplete_cells, *a.role_diversity, *(-x for x in a.evidence_overlap),
          -RISK_ORDER[a.member_risk], -RISK_ORDER[a.rule_risk], -STRUCTURE_ORDER.get(a.final_structure, 4))
    bv = (-b.conflict_columns, -b.incomplete_cells, *b.role_diversity, *(-x for x in b.evidence_overlap),
          -RISK_ORDER[b.member_risk], -RISK_ORDER[b.rule_risk], -STRUCTURE_ORDER.get(b.final_structure, 4))
    return all(x >= y for x, y in zip(av, bv)) and any(x > y for x, y in zip(av, bv))


def assign_sets(a_numbers: tuple[int, int, int], b_numbers: tuple[int, int, int],
                a_rank: tuple[Any, ...], b_rank: tuple[Any, ...]) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    if a_rank > b_rank or (a_rank == b_rank and a_numbers < b_numbers):
        return a_numbers, b_numbers
    return b_numbers, a_numbers


def ranking_key(x: Mapping[str, Any]) -> tuple[Any, ...]:
    """Ascending Python key implementing the public 15 keys plus stable storage key."""
    cat = lambda value, order: -order.get(value, -1)
    benefit = lambda value: inf if value is None else -value
    adverse = lambda value: inf if value is None else value
    return (
        -bool(x["both_pass"]), cat(x["pareto"], {"NONDOMINATED": 2, "DOMINATED": 1, "NOT_COMPARABLE": 0}),
        benefit(x["integrated_primary_rate"]), benefit(x["integrated_primary_rate"] - x["integrated_baseline"] if x["integrated_primary_rate"] is not None else None),
        benefit(x["main_primary_rate"]), benefit(x["support_rate"]),
        cat(x["recent"], {"STABLE": 3, "WARNING": 2, "SEVERE": 1, "INSUFFICIENT": 0}),
        tuple(benefit(v) for v in x["weaker_member_vector"]),
        (-bool(x["final_risk"] != "HIGH"), x["conflict_columns"]),
        RISK_ORDER.get(x["final_risk"], 3),
        {"NORMAL": 0, "CAUTION": 1, "WARNING": 2, "SEVERE": 3, "INSUFFICIENT": 4}.get(x["structure"], 5),
        (tuple(-v for v in x["role_diversity"]), tuple(x["evidence_overlap"])),
        adverse(x["simultaneous_failure_rate"]), tuple(x["set1"]), tuple(x["set2"]), x["canonical_pair_key"],
    )

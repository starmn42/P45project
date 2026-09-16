"""P45 v2.7 stage-5 unit relationship engine.

The fixed unit order is an identity/storage convention only.  This module
contains no weights, totals, averages, or promotion of UNIT_TEST.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .integrity import sha256_json

UNIT_ORDER = ("UNIT_3", "UNIT_5", "UNIT_9", "UNIT_10", "END_DIGIT")
STATE_ORDER = {"UNIT_FAIL": 0, "UNIT_HOLD": 1, "UNIT_TEST": 2,
               "UNIT_WEAKEN": 3, "UNIT_PASS": 4}
VALID_STATES = frozenset(STATE_ORDER)


@dataclass(frozen=True)
class UnitEvidence:
    state: str
    raw_values: Mapping[str, Any]
    evidence_keys: tuple[str, ...] = ()
    independent_context: Mapping[str, Any] | None = None
    strong_opposition: bool = False

    def __post_init__(self) -> None:
        if self.state not in VALID_STATES:
            raise ValueError(f"invalid unit state: {self.state}")


def build_relation(entity_type: str, entity_key: str,
                   evidence: Mapping[str, UnitEvidence]) -> dict[str, Any]:
    """Build one lossless relationship record without aggregating scores."""
    unknown = set(evidence) - set(UNIT_ORDER)
    if unknown:
        raise ValueError(f"unknown units: {sorted(unknown)}")
    vector = [evidence[u].state if u in evidence else None for u in UNIT_ORDER]
    missing = [u for u in UNIT_ORDER if u not in evidence]
    support = [u for u in UNIT_ORDER if u in evidence and evidence[u].state == "UNIT_PASS"]
    weaken = [u for u in UNIT_ORDER if u in evidence and evidence[u].state == "UNIT_WEAKEN"]
    tests = [u for u in UNIT_ORDER if u in evidence and evidence[u].state == "UNIT_TEST"]
    holds = [u for u in UNIT_ORDER if u in evidence and evidence[u].state == "UNIT_HOLD"]
    fails = [u for u in UNIT_ORDER if u in evidence and evidence[u].state == "UNIT_FAIL"]
    strong = [u for u in UNIT_ORDER if u in evidence and evidence[u].strong_opposition]

    if missing:
        relation_state = "UNIT_RELATION_INCOMPLETE"
    elif (support or weaken) and (fails or strong):
        relation_state = "UNIT_CONFLICT"
    elif all(state in ("UNIT_PASS", "UNIT_WEAKEN") for state in vector):
        relation_state = "UNIT_CONSENSUS_SUPPORT"
    elif support or weaken:
        relation_state = "UNIT_PARTIAL_SUPPORT"
    else:
        relation_state = "UNIT_NO_SUPPORT"

    key_units: dict[str, list[str]] = {}
    for unit in UNIT_ORDER:
        if unit in evidence:
            for key in evidence[unit].evidence_keys:
                key_units.setdefault(key, []).append(unit)
    duplicate_evidence = {key: units for key, units in key_units.items() if len(units) > 1}
    related_support = {
        unit: {"evidence_keys": list(evidence[unit].evidence_keys),
               "duplicated_keys": [k for k in evidence[unit].evidence_keys if k in duplicate_evidence]}
        for unit in UNIT_ORDER if unit in evidence and evidence[unit].evidence_keys
    }
    independent = {
        unit: dict(evidence[unit].independent_context or {})
        for unit in UNIT_ORDER if unit in evidence and evidence[unit].independent_context
    }
    raw_unit_support = {
        unit: {"state": evidence[unit].state, "values": dict(evidence[unit].raw_values),
               "strong_opposition": evidence[unit].strong_opposition}
        for unit in UNIT_ORDER if unit in evidence
    }
    conflict_raw = {
        "supporting_units": support + weaken,
        "opposing_units": list(dict.fromkeys(fails + strong)),
        "raw_values": {u: raw_unit_support[u] for u in UNIT_ORDER if u in evidence},
    }
    payload = {
        "entity_type": entity_type, "entity_key": str(entity_key), "unit_state_vector": vector,
        "missing_units": missing, "support_units": support, "weaken_units": weaken,
        "test_units": tests, "hold_units": holds, "fail_units": fails,
        "relation_state": relation_state,
        "evidence": {"RAW_UNIT_SUPPORT": raw_unit_support,
                     "RELATED_UNIT_SUPPORT": related_support,
                     "INDEPENDENT_CONTEXT_SUPPORT": independent,
                     "UNIT_CONFLICT": conflict_raw},
        "duplicate_evidence": duplicate_evidence,
    }
    return {**payload, "relation_hash": sha256_json(payload)}


def pareto_compare(left: Mapping[str, Any], right: Mapping[str, Any]) -> str:
    """Compare complete vectors component by component; never sum components."""
    lv, rv = left["unit_state_vector"], right["unit_state_vector"]
    if len(lv) != 5 or len(rv) != 5 or any(s not in STATE_ORDER for s in (*lv, *rv)):
        return "UNIT_PARETO_NOT_COMPARABLE"
    left_not_worse = all(STATE_ORDER[a] >= STATE_ORDER[b] for a, b in zip(lv, rv))
    left_better = any(STATE_ORDER[a] > STATE_ORDER[b] for a, b in zip(lv, rv))
    right_not_worse = all(STATE_ORDER[b] >= STATE_ORDER[a] for a, b in zip(lv, rv))
    right_better = any(STATE_ORDER[b] > STATE_ORDER[a] for a, b in zip(lv, rv))
    if left_not_worse and left_better:
        return "UNIT_PARETO_DOMINATE"
    if right_not_worse and right_better:
        return "UNIT_PARETO_DOMINATED"
    return "UNIT_PARETO_NONDOMINATED"


def pareto_classify(relations: Mapping[str, Mapping[str, Any]]) -> dict[str, str]:
    result = {}
    for key, relation in relations.items():
        comparisons = [pareto_compare(other, relation) for other_key, other in relations.items() if other_key != key]
        if any(value == "UNIT_PARETO_DOMINATE" for value in comparisons):
            result[key] = "UNIT_PARETO_DOMINATED"
        elif any(value == "UNIT_PARETO_NOT_COMPARABLE" for value in comparisons):
            result[key] = "UNIT_PARETO_NOT_COMPARABLE"
        else:
            result[key] = "UNIT_PARETO_NONDOMINATED"
    return result


def build_number_relations(unit_number_metrics: Mapping[str, Mapping[int, Mapping[str, Any]]]) -> dict[int, dict[str, Any]]:
    """Use only number-level UNIT states, as required by v2.7.1 appendix A.13."""
    relations = {}
    for number in range(1, 46):
        evidence = {}
        for unit in UNIT_ORDER:
            metric = unit_number_metrics.get(unit, {}).get(number)
            if metric is not None:
                evidence[unit] = UnitEvidence(
                    metric["unit_state"],
                    {"decision_hash": metric["decision_hash"], "reason_codes": metric["reason_codes"],
                     "opposite_risk": metric["opposite_risk"], "structure_state": metric["structure_state"]},
                    independent_context={"primary_context": metric["primary_context"]},
                    strong_opposition=metric["opposite_risk"] == "HIGH",
                )
        relations[number] = build_relation("NUMBER", str(number), evidence)
    return relations

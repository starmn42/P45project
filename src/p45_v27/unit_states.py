"""P45 v2.7.1 stage-5.5 number-by-unit state adjudication."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Any, Iterable, Mapping, Sequence

from .integrity import sha256_json
from .units.models import Draw, UnitDefinition

Z95 = 1.959963984540054
P0 = {"integrated": 7 / 45, "main": 6 / 45, "bonus": 1 / 45}
POSITIVE = {"POSITIVE_CONFIRMED", "POSITIVE_TENTATIVE"}
NEGATIVE = {"NEGATIVE_CONFIRMED", "NEGATIVE_TENTATIVE"}


def wilson95(hit_count: int, sample_count: int) -> tuple[float | None, float | None]:
    if sample_count < 0 or hit_count < 0 or hit_count > sample_count:
        raise ValueError("invalid Wilson inputs")
    if sample_count == 0:
        return None, None
    p = hit_count / sample_count
    z2 = Z95 * Z95
    denominator = 1 + z2 / sample_count
    center = (p + z2 / (2 * sample_count)) / denominator
    margin = Z95 * sqrt((p * (1 - p) / sample_count) + z2 / (4 * sample_count**2)) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def evidence_label(hit_count: int, sample_count: int, baseline: float, sufficient: bool) -> dict[str, Any]:
    low, high = wilson95(hit_count, sample_count)
    rate = hit_count / sample_count if sample_count else None
    if not sufficient or sample_count == 0:
        label = "INSUFFICIENT"
    elif low is not None and low > baseline:
        label = "POSITIVE_CONFIRMED"
    elif high is not None and high < baseline:
        label = "NEGATIVE_CONFIRMED"
    elif rate is not None and rate > baseline:
        label = "POSITIVE_TENTATIVE"
    elif rate is not None and rate < baseline:
        label = "NEGATIVE_TENTATIVE"
    else:
        label = "NEUTRAL"
    return {"sample_count": sample_count, "hit_count": hit_count, "rate": rate,
            "wilson_low_95": low, "wilson_high_95": high, "evidence_label": label}


def _context_sample_state(kind: str, count: int) -> str:
    threshold, borderline = (20, 10) if kind == "EXACT_VECTOR_CONTEXT" else (30, 20)
    return "SUFFICIENT" if count >= threshold else "BORDERLINE" if count >= borderline else "INSUFFICIENT"


def _period_level(period: str, count: int) -> str:
    if period == "recent100":
        return "OFFICIAL" if count >= 15 else "BORDERLINE" if count >= 8 else "REFERENCE_ONLY"
    if period == "recent50":
        return "OFFICIAL" if count >= 8 else "BORDERLINE" if count >= 5 else "REFERENCE_ONLY"
    return "TEST_ONLY"


def _outcome_summary(samples: Sequence[dict], sufficient: bool) -> dict[str, Any]:
    result = {}
    for channel in ("integrated", "main", "bonus"):
        result[channel] = evidence_label(sum(s[channel] for s in samples), len(samples), P0[channel], sufficient)
    return result


def _direction(label: str) -> str:
    return "POSITIVE" if label in POSITIVE else "NEGATIVE" if label in NEGATIVE else "NEUTRAL"


def choose_context(exact: Mapping[str, Any], local: Mapping[str, Any]) -> tuple[str, str]:
    if exact["sample_state"] == "SUFFICIENT": return "EXACT_VECTOR_CONTEXT", "LOCAL_GROUP_CONTEXT"
    if local["sample_state"] == "SUFFICIENT": return "LOCAL_GROUP_CONTEXT", "EXACT_VECTOR_CONTEXT"
    if exact["sample_state"] == "BORDERLINE": return "EXACT_VECTOR_CONTEXT_BORDERLINE", "LOCAL_GROUP_CONTEXT"
    if local["sample_state"] == "BORDERLINE": return "LOCAL_GROUP_CONTEXT_BORDERLINE", "EXACT_VECTOR_CONTEXT"
    return "NO_EVALUABLE_CONTEXT", "NONE"


def context_relation(primary: Mapping[str, Any] | None, secondary: Mapping[str, Any] | None) -> str:
    if not primary or not secondary or secondary["sample_state"] == "INSUFFICIENT": return "CONTEXT_INCONCLUSIVE"
    a, b = primary["overall"]["integrated"]["evidence_label"], secondary["overall"]["integrated"]["evidence_label"]
    da, db = _direction(a), _direction(b)
    if da == db and da != "NEUTRAL": return "CONTEXT_ALIGNED"
    if {da, db} == {"POSITIVE", "NEUTRAL"}: return "CONTEXT_PARTIAL"
    if {a, b} == {"POSITIVE_CONFIRMED", "NEGATIVE_CONFIRMED"}: return "CONTEXT_CONFLICT_HIGH"
    if "POSITIVE" in (da, db) and "NEGATIVE" in (da, db): return "CONTEXT_CONFLICT_MEDIUM"
    return "CONTEXT_INCONCLUSIVE"


def _bonus_dependence(primary: Mapping[str, Any]) -> str:
    integrated = primary["overall"]["integrated"]
    main = primary["overall"]["main"]
    if integrated["evidence_label"] in POSITIVE and main["evidence_label"] == "NEGATIVE_CONFIRMED":
        return "BONUS_DEPENDENCE_HIGH"
    if integrated["evidence_label"] in POSITIVE and main["rate"] is not None and main["rate"] < P0["main"] \
            and main["wilson_low_95"] <= P0["main"] <= main["wilson_high_95"]:
        return "BONUS_DEPENDENCE_MEDIUM"
    return "BONUS_DEPENDENCE_NONE"


def _opposite_risk(primary: Mapping[str, Any], secondary: Mapping[str, Any] | None,
                   relation: str, bonus: str) -> str:
    recent100 = primary["recent100"]["integrated"]["evidence_label"]
    recent50 = primary["recent50"]["integrated"]["evidence_label"]
    if relation == "CONTEXT_CONFLICT_HIGH" or bonus == "BONUS_DEPENDENCE_HIGH" \
            or (secondary and secondary["sample_state"] == "SUFFICIENT" and
                secondary["overall"]["integrated"]["evidence_label"] == "NEGATIVE_CONFIRMED") \
            or (primary["overall"]["integrated"]["evidence_label"] in POSITIVE and recent100 == "NEGATIVE_CONFIRMED"):
        return "HIGH"
    if relation == "CONTEXT_CONFLICT_MEDIUM" or bonus == "BONUS_DEPENDENCE_MEDIUM" \
            or recent100 == "NEGATIVE_TENTATIVE" or recent50 == "NEGATIVE_TENTATIVE" \
            or (_direction(primary["overall"]["integrated"]["evidence_label"]) != _direction(recent100)
                and recent100 != "INSUFFICIENT"):
        return "MEDIUM"
    return "LOW"


def decide_unit_state(*, primary_name: str, primary: Mapping[str, Any] | None,
                      secondary: Mapping[str, Any] | None, relation: str,
                      bonus_dependence: str, opposite_risk: str, structure_state: str,
                      deterministic_ok: bool = True, storage_ok: bool = True) -> tuple[str, str | None, list[str]]:
    reasons: list[str] = []
    if not deterministic_ok or not storage_ok:
        return "UNIT_SYSTEM_ERROR", "SYSTEM_INTEGRITY", ["DETERMINISM_OR_STORAGE_FAILED"]
    if primary_name == "NO_EVALUABLE_CONTEXT" or primary is None:
        return "UNIT_HOLD", "PRIMARY_CONTEXT", ["NO_EVALUABLE_CONTEXT"]
    integrated = primary["overall"]["integrated"]
    main = primary["overall"]["main"]
    r100, r50 = primary["recent100"], primary["recent50"]
    stable_negative = integrated["evidence_label"] == "NEGATIVE_CONFIRMED"
    if stable_negative or (main["evidence_label"] == "NEGATIVE_CONFIRMED" and integrated["evidence_label"] != "POSITIVE_CONFIRMED") \
            or (opposite_risk == "HIGH" and (stable_negative or (secondary and secondary["overall"]["integrated"]["evidence_label"] == "NEGATIVE_CONFIRMED"))) \
            or (structure_state == "SEVERE" and stable_negative):
        return "UNIT_FAIL", "CONFIRMED_NEGATIVE", ["NEGATIVE_CONFIRMED"]
    if relation == "CONTEXT_CONFLICT_HIGH" or opposite_risk == "HIGH" or bonus_dependence == "BONUS_DEPENDENCE_HIGH" \
            or (structure_state == "SEVERE" and integrated["evidence_label"] not in POSITIVE):
        return "UNIT_HOLD", "RISK_OR_CONTEXT", [relation, opposite_risk, bonus_dependence, structure_state]
    pass_ok = (primary["sample_state"] == "SUFFICIENT" and integrated["evidence_label"] == "POSITIVE_CONFIRMED"
               and main["evidence_label"] != "NEGATIVE_CONFIRMED" and main["rate"] is not None and main["rate"] >= P0["main"]
               and r100["sample_level"] == "OFFICIAL" and r100["integrated"]["rate"] is not None
               and r100["integrated"]["rate"] >= P0["integrated"] and r100["integrated"]["evidence_label"] != "NEGATIVE_CONFIRMED"
               and (r50["sample_level"] != "OFFICIAL" or r50["integrated"]["evidence_label"] != "NEGATIVE_CONFIRMED")
               and r50["sample_level"] == "OFFICIAL" and bonus_dependence == "BONUS_DEPENDENCE_NONE"
               and relation != "CONTEXT_CONFLICT_HIGH" and opposite_risk == "LOW"
               and structure_state in ("NORMAL", "CAUTION"))
    if pass_ok:
        return "UNIT_PASS", None, ["ALL_PASS_GATES"]
    positive = integrated["evidence_label"] in POSITIVE
    borderline_positive = primary["sample_state"] == "BORDERLINE" and _direction(integrated["evidence_label"]) == "POSITIVE"
    if positive or borderline_positive or opposite_risk == "MEDIUM" or structure_state in ("WARNING",) \
            or (structure_state == "SEVERE" and positive and opposite_risk == "LOW") or bonus_dependence == "BONUS_DEPENDENCE_MEDIUM":
        return "UNIT_WEAKEN", "PASS_GATE_WEAK", ["POSITIVE_DIRECTION_NOT_FULL_PASS"]
    return "UNIT_TEST", "EVIDENCE_NOT_CONFIRMED", [integrated["evidence_label"]]


def evaluate_number_unit(definition: UnitDefinition, draws: Iterable[Draw], analysis_round: int,
                         number: int, structure_state: str = "INSUFFICIENT_SAMPLE") -> dict[str, Any]:
    history = sorted((d for d in draws if d.round < analysis_round), key=lambda d: d.round)
    if not history or history[-1].round != analysis_round - 1: raise ValueError("history boundary missing")
    group = next((g for g in definition.groups if number in g.members), None)
    if group is None: raise ValueError("number not in exactly one group")
    vectors, occupancies, streaks = [], [], []
    streak = 0
    for draw in history:
        vector = tuple(len(set((*draw.main, draw.bonus)) & set(g.members)) for g in definition.groups)
        occupancy = vector[group.order - 1]
        streak = streak + 1 if occupancy == 0 else 0
        vectors.append(vector); occupancies.append(occupancy); streaks.append(streak)
    current_vector = vectors[-1]
    current_local = (occupancies[-1], occupancies[-1] == 0, streaks[-1])
    exact_samples, local_samples = [], []
    for index in range(len(history) - 1):
        nxt = history[index + 1]
        outcome = {"source_round": nxt.round, "integrated": int(number in (*nxt.main, nxt.bonus)),
                   "main": int(number in nxt.main), "bonus": int(number == nxt.bonus)}
        if vectors[index] == current_vector: exact_samples.append(outcome)
        if (occupancies[index], occupancies[index] == 0, streaks[index]) == current_local: local_samples.append(outcome)

    contexts = {}
    for name, samples in (("EXACT_VECTOR_CONTEXT", exact_samples), ("LOCAL_GROUP_CONTEXT", local_samples)):
        state = _context_sample_state(name, len(samples)); sufficient = state != "INSUFFICIENT"
        context = {"sample_state": state, "overall": _outcome_summary(samples, sufficient)}
        for period, width in (("recent100",100),("recent50",50),("recent20",20)):
            window = [s for s in samples if s["source_round"] >= max(1, analysis_round-width)]
            level = _period_level(period, len(window))
            context[period] = {**_outcome_summary(window, level in ("OFFICIAL","TEST_ONLY")), "sample_level": level,
                               "round_start": max(1, analysis_round-width), "round_end": analysis_round-1}
        contexts[name] = context
    primary_name, secondary_name = choose_context(contexts["EXACT_VECTOR_CONTEXT"], contexts["LOCAL_GROUP_CONTEXT"])
    base_primary = primary_name.replace("_BORDERLINE", "")
    primary = contexts.get(base_primary) if primary_name != "NO_EVALUABLE_CONTEXT" else None
    secondary = contexts.get(secondary_name) if secondary_name != "NONE" else None
    relation = context_relation(primary, secondary)
    bonus = _bonus_dependence(primary) if primary else "BONUS_DEPENDENCE_NONE"
    risk = _opposite_risk(primary, secondary, relation, bonus) if primary else "LOW"
    state, first_gate, reasons = decide_unit_state(primary_name=primary_name, primary=primary, secondary=secondary,
        relation=relation, bonus_dependence=bonus, opposite_risk=risk, structure_state=structure_state)
    payload = {"unit_type": definition.unit_type, "number": number, "analysis_round": analysis_round,
               "primary_context": primary_name, "secondary_context": secondary_name, "context_relation": relation,
               "contexts": contexts, "bonus_dependence": bonus, "opposite_risk": risk,
               "structure_state": structure_state, "unit_state": state, "first_limiting_gate": first_gate,
               "reason_codes": reasons}
    return {**payload, "decision_hash": sha256_json(payload)}


def evaluate_all_units(definitions: Mapping[str, UnitDefinition], draws: Iterable[Draw], analysis_round: int,
                       structure_states: Mapping[str, str] | None = None) -> dict[str, dict[int, dict[str, Any]]]:
    materialized = tuple(draws)
    states = structure_states or {}
    return {unit: {n: evaluate_number_unit(definition, materialized, analysis_round, n,
                                            states.get(unit, "INSUFFICIENT_SAMPLE")) for n in range(1,46)}
            for unit, definition in definitions.items()}

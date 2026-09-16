"""Independent unit calculation without cross-unit scoring or candidate selection."""

from __future__ import annotations

from collections import Counter
from math import sqrt
from statistics import mean
from typing import Iterable, Sequence

from ..integrity import sha256_json
from .models import Draw, UnitAnalysis, UnitDefinition


PERIODS = ("overall", "first_half", "second_half", "recent100", "recent50", "recent20")


def _deviations(observed: int, group_size: int, draw_size: int) -> tuple[float, float, float]:
    proportion = group_size / 45
    expected = draw_size * proportion
    # Hypergeometric variance: sampling without replacement from numbers 1..45.
    variance = draw_size * proportion * (1 - proportion) * ((45 - draw_size) / 44)
    raw = observed - expected
    return expected, raw, raw / sqrt(variance) if variance else 0.0


def _sample_state(count: int) -> str:
    return "SUFFICIENT" if count >= 30 else "BORDERLINE" if count >= 20 else "INSUFFICIENT"


def _summary(rows: Sequence[dict]) -> dict:
    count = len(rows)
    return {
        "sample_count": count,
        "sample_state": _sample_state(count),
        "main_count": sum(r["main"] for r in rows),
        "bonus_count": sum(r["bonus"] for r in rows),
        "integrated_count": sum(r["integrated"] for r in rows),
        "main_mean": mean([r["main"] for r in rows]) if rows else None,
        "integrated_mean": mean([r["integrated"] for r in rows]) if rows else None,
    }


def _period_slices(rows: Sequence[dict], analysis_round: int) -> dict[str, Sequence[dict]]:
    midpoint = len(rows) // 2
    return {
        "overall": rows,
        "first_half": rows[:midpoint],
        "second_half": rows[midpoint:],
        "recent100": [r for r in rows if r["source_round"] >= max(1, analysis_round - 100)],
        "recent50": [r for r in rows if r["source_round"] >= max(1, analysis_round - 50)],
        "recent20": [r for r in rows if r["source_round"] >= max(1, analysis_round - 20)],
    }


def _performance(transitions: Sequence[dict]) -> dict:
    count = len(transitions)
    return {
        "sample_count": count,
        "sample_state": _sample_state(count),
        "main_hit_count": sum(t["next_main"] > 0 for t in transitions),
        "bonus_hit_count": sum(t["next_bonus"] > 0 for t in transitions),
        "integrated_hit_count": sum(t["next_integrated"] > 0 for t in transitions),
        "main_total": sum(t["next_main"] for t in transitions),
        "bonus_total": sum(t["next_bonus"] for t in transitions),
        "integrated_total": sum(t["next_integrated"] for t in transitions),
        "main_hit_rate": sum(t["next_main"] > 0 for t in transitions) / count if count else None,
        "bonus_hit_rate": sum(t["next_bonus"] > 0 for t in transitions) / count if count else None,
        "integrated_hit_rate": sum(t["next_integrated"] > 0 for t in transitions) / count if count else None,
        "return_depth_counts": dict(Counter(t["return_depth"] for t in transitions if t["return_depth"])),
    }


def calculate_unit(definition: UnitDefinition, draws: Iterable[Draw], analysis_round: int) -> UnitAnalysis:
    # This is the hard future-data boundary. Rows from analysis_round onward never enter a statistic.
    history = sorted((d for d in draws if d.round < analysis_round), key=lambda d: d.round)
    if not history or history[-1].round != analysis_round - 1:
        raise ValueError("history must end at analysis_round - 1")
    if len({d.round for d in history}) != len(history):
        raise ValueError("duplicate source round")

    group_rows: dict[str, list[dict]] = {g.label: [] for g in definition.groups}
    round_metrics: list[dict] = []
    streaks = {g.label: 0 for g in definition.groups}
    draw_vectors: list[tuple[int, ...]] = []
    for draw in history:
        vector = tuple(len(set((*draw.main, draw.bonus)) & set(g.members)) for g in definition.groups)
        draw_vectors.append(vector)
        for group, integrated in zip(definition.groups, vector):
            main = len(set(draw.main) & set(group.members))
            bonus = int(draw.bonus in group.members)
            expected_main, raw_main, standardized_main = _deviations(main, group.size, 6)
            expected_integrated, raw_integrated, standardized_integrated = _deviations(integrated, group.size, 7)
            annihilated = integrated == 0
            streaks[group.label] = streaks[group.label] + 1 if annihilated else 0
            row = {
                "source_round": draw.round, "group_order": group.order, "group_label": group.label,
                "group_size": group.size, "main": main, "bonus": bonus, "integrated": integrated,
                "main_occupancy_rate": main / group.size,
                "integrated_occupancy_rate": integrated / group.size,
                "expected_main_count": expected_main,
                "expected_integrated_count": expected_integrated,
                "raw_main_deviation": raw_main,
                "raw_integrated_deviation": raw_integrated,
                "standardized_main_deviation": standardized_main,
                "standardized_integrated_deviation": standardized_integrated,
                "is_annihilated": annihilated,
                "consecutive_annihilation_length": streaks[group.label],
                "next_return_count": None, "return_depth": None,
                "structural_exception_3_plus": False, "occupancy_vector": vector,
            }
            group_rows[group.label].append(row)
            round_metrics.append(row)

    for rows in group_rows.values():
        for index, row in enumerate(rows[:-1]):
            if row["is_annihilated"]:
                returned = rows[index + 1]["integrated"]
                row["next_return_count"] = returned
                row["return_depth"] = str(returned) if returned < 3 else "3_PLUS"
                row["structural_exception_3_plus"] = returned >= 3

    period_metrics = {
        label: {name: _summary(parts) for name, parts in _period_slices(rows, analysis_round).items()}
        for label, rows in group_rows.items()
    }
    current_vector = draw_vectors[-1]
    exact_transitions, all_transitions = [], []
    local_transitions: dict[str, list[dict]] = {g.label: [] for g in definition.groups}
    for index in range(len(history) - 1):
        for group_index, group in enumerate(definition.groups):
            current, nxt = group_rows[group.label][index], group_rows[group.label][index + 1]
            transition = {
                "source_round": current["source_round"], "group_label": group.label,
                "next_main": nxt["main"], "next_bonus": nxt["bonus"], "next_integrated": nxt["integrated"],
                "return_depth": current["return_depth"],
            }
            all_transitions.append(transition)
            if current["integrated"] == group_rows[group.label][-1]["integrated"]:
                local_transitions[group.label].append(transition)
            if draw_vectors[index] == current_vector:
                exact_transitions.append(transition)

    number_metrics = {}
    for number in range(1, 46):
        group = next(g for g in definition.groups if number in g.members)
        rows = group_rows[group.label]
        current_occ = rows[-1]["integrated"]
        samples = []
        for index in range(len(history) - 1):
            if rows[index]["integrated"] == current_occ:
                nxt = history[index + 1]
                samples.append({"source_round": nxt.round, "main": int(number in nxt.main), "bonus": int(number == nxt.bonus),
                                "integrated": int(number in (*nxt.main, nxt.bonus))})
        period = {name: _summary(parts) for name, parts in _period_slices(samples, analysis_round).items()}
        number_metrics[number] = {
            "group_label": group.label, "sample_count": len(samples), "sample_state": _sample_state(len(samples)),
            "overall": period["overall"], "first_half": period["first_half"], "second_half": period["second_half"],
            "recent100": period["recent100"], "recent50": period["recent50"], "recent20": period["recent20"],
            "exact_vector": _performance([t for t in exact_transitions if t["group_label"] == group.label]),
            "local_state": _performance(local_transitions[group.label]),
            "opposite_hypothesis_inputs": {"miss_count": sum(not s["integrated"] for s in samples)},
            "structure_collapse_inputs": {"sample_count": len(samples), "hit_rate": (sum(s["integrated"] for s in samples) / len(samples)) if samples else None},
            "unit_state": "UNIT_TEST",
        }

    definition_payload = {
        "unit_type": definition.unit_type, "correction_method": definition.correction_method,
        "groups": [{"order": g.order, "label": g.label, "size": g.size, "members": g.members} for g in definition.groups],
    }
    data_payload = [{"round": d.round, "main": d.main, "bonus": d.bonus} for d in history]
    execution_payload = {"definition": definition_payload, "analysis_round": analysis_round,
                         "data_hash": sha256_json(data_payload), "round_metrics": round_metrics,
                         "number_metrics": number_metrics}
    return UnitAnalysis(
        unit_type=definition.unit_type, analysis_round=analysis_round, definition=definition_payload,
        round_metrics=tuple(round_metrics), period_metrics=period_metrics,
        exact_vector_sample=_performance(exact_transitions),
        group_local_state_samples={k: _performance(v) for k, v in local_transitions.items()},
        performance=_performance(all_transitions), number_metrics=number_metrics,
        sample_state=_sample_state(len(history)),
        opposite_hypothesis_inputs={"current_vector": current_vector, "historical_vector_frequency": draw_vectors.count(current_vector)},
        structure_collapse_inputs={"structural_exception_count": sum(r["structural_exception_3_plus"] for r in round_metrics),
                                   "current_annihilation_streaks": {k: v[-1]["consecutive_annihilation_length"] for k, v in group_rows.items()}},
        unit_state="UNIT_TEST", calculation_status="COMPLETE", data_hash=sha256_json(data_payload),
        execution_hash=sha256_json(execution_payload),
    )

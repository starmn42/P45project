"""P45 v2.7.1 stage-5.6 structure-collapse percentile ledger."""

from __future__ import annotations

from math import sqrt
from statistics import mean
from typing import Any, Iterable

from .integrity import sha256_json
from .units.models import Draw, UnitDefinition


class StructureCalculationError(RuntimeError):
    pass


def _percentile(distribution: list[float], current: float) -> float:
    if not distribution:
        raise StructureCalculationError("historical distribution is missing")
    return 100.0 * sum(value <= current for value in distribution) / len(distribution)


def _state(percentile: float) -> str:
    if percentile < 90: return "NORMAL"
    if percentile < 95: return "CAUTION"
    if percentile < 99: return "WARNING"
    return "SEVERE"


def calculate_structure_ledger(definition: UnitDefinition, draws: Iterable[Draw], analysis_round: int) -> dict[str, Any]:
    history = sorted((d for d in draws if d.round < analysis_round), key=lambda d: d.round)
    if not history or history[-1].round != analysis_round - 1:
        raise StructureCalculationError("required R-1 input is missing")
    if len({d.round for d in history}) != len(history):
        raise StructureCalculationError("duplicate round input")
    if any(history[i].round >= history[i+1].round for i in range(len(history)-1)):
        raise StructureCalculationError("round order error")
    streaks = [0] * len(definition.groups)
    rows: list[dict[str, float]] = []
    previous_vector: tuple[int, ...] | None = None
    zero_history: list[float] = []
    for draw in history:
        vector = tuple(len(set((*draw.main, draw.bonus)) & set(g.members)) for g in definition.groups)
        standardized = []
        for index, (group, observed) in enumerate(zip(definition.groups, vector)):
            streaks[index] = streaks[index] + 1 if observed == 0 else 0
            p = group.size / 45
            expected = 7 * p
            variance = 7 * p * (1-p) * ((45-7)/44)
            standardized.append(abs((observed-expected)/sqrt(variance)) if variance else 0.0)
        zero_count = float(sum(value == 0 for value in vector))
        realized_return = float(max((value for value, old in zip(vector, previous_vector or vector) if old == 0), default=0))
        preceding = zero_history[:-50] if len(zero_history) > 50 else zero_history
        recent = zero_history[-50:]
        shift = abs(mean(recent)-mean(preceding)) if recent and preceding else 0.0
        rows.append({"zero_group_count": zero_count, "max_abs_standardized_occupancy": max(standardized),
                     "max_annihilation_streak": float(max(streaks)), "realized_return_depth": realized_return,
                     "recent50_zero_group_shift": shift})
        zero_history.append(zero_count)
        previous_vector = vector
    sample_count = len(rows)-1
    current = rows[-1]
    distributions = {name: [row[name] for row in rows[:-1]] for name in current}
    data_hash = sha256_json([{"round":d.round,"main":d.main,"bonus":d.bonus} for d in history])
    if sample_count < 50:
        percentiles = {name: None for name in current}
        overall = None
        state = "INSUFFICIENT_SAMPLE"
        reason = "REFERENCE_SAMPLE_LT_50"
    else:
        percentiles = {name: _percentile(distributions[name], value) for name, value in current.items()}
        overall = max(percentiles.values())
        state = _state(overall)
        reason = "MAX_METRIC_PERCENTILE_WITHOUT_WEIGHTING"
    payload = {"unit_type":definition.unit_type,"analysis_round":analysis_round,
               "reference_start_round":history[0].round,"reference_end_round":history[-1].round,
               "sample_count":sample_count,"metric_names":list(current),"current_metrics":current,
               "historical_distribution":distributions,"metric_percentiles":percentiles,
               "overall_percentile":overall,"structure_state":state,"decision_reason":reason,"data_hash":data_hash}
    return {**payload,"calculation_hash":sha256_json(payload)}

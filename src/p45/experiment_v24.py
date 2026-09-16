from __future__ import annotations

import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import mean

from .candidates import RANDOM_INTEGRATED, RANDOM_MAIN
from .data import ENGINE_VERSION, load_and_validate_csv, sha256_file
from .structure import build_draw_structure


EXPERIMENT_VERSION = "P45 v2.4-EXPERIMENTAL-1236"
STAGES = {"NORMAL": 0, "CAUTION": 1, "WARNING": 2, "SEVERE": 3}


class ExperimentalRuleError(ValueError):
    pass


def _stage_max(*stages: str) -> str:
    return max(stages, key=lambda value: STAGES[value])


def fixed_collapse_stage(overall: float, recent_100: float, recent_50: float) -> dict[str, object]:
    drop_100 = max(0.0, overall - recent_100)
    drop_50 = max(0.0, overall - recent_50)
    if drop_100 >= 0.15 or drop_50 >= 0.20:
        stage = "SEVERE"
    elif drop_100 >= 0.10 or drop_50 >= 0.125:
        stage = "WARNING"
    elif drop_100 >= 0.05 or drop_50 >= 0.075:
        stage = "CAUTION"
    else:
        stage = "NORMAL"
    return {"stage": stage, "recent_100_drop": drop_100, "recent_50_drop": drop_50}


def opposite_risk(record: dict[str, object]) -> str:
    periods = record["primary_performance"]
    overall = periods["overall"]
    recent_100 = periods["recent_100"]
    recent_50 = periods["recent_50"]
    if overall["sample_count"] < 20 or recent_100["sample_count"] < 8 or recent_50["sample_count"] < 5:
        return "HOLD_SAMPLE_INSUFFICIENT"
    overall_rate = overall["integrated_rate"]
    rate_100 = recent_100["integrated_rate"]
    rate_50 = recent_50["integrated_rate"]
    if overall_rate <= RANDOM_INTEGRATED or (rate_100 < RANDOM_INTEGRATED and rate_50 < RANDOM_INTEGRATED):
        return "HIGH"
    wilson = overall["integrated_wilson_95"]
    if (
        overall_rate >= RANDOM_INTEGRATED
        and rate_100 >= RANDOM_INTEGRATED
        and rate_50 >= RANDOM_INTEGRATED
        and wilson
        and wilson[0] >= RANDOM_INTEGRATED
    ):
        return "LOW"
    return "MEDIUM"


def _mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def _depth_distribution(events: list[dict[str, object]]) -> list[float]:
    if not events:
        return [0.0, 0.0, 0.0, 0.0]
    counts = Counter(
        str(event["integrated_depth"]) if int(event["integrated_depth"]) <= 2 else "3_PLUS"
        for event in events
    )
    return [counts[key] / len(events) for key in ("0", "1", "2", "3_PLUS")]


def _window_metrics(
    structures: list[object],
    events: list[dict[str, object]],
    start_index: int,
    end_index: int,
) -> dict[str, object]:
    window = structures[start_index:end_index]
    rounds = {item.round for item in window}
    window_events = [event for event in events if event["target_round"] in rounds]
    return {
        "annihilated_9_mean": _mean([len(item.annihilated_9) for item in window]),
        "continued_annihilation_rate": (
            sum(int(event["integrated_depth"]) == 0 for event in window_events) / len(window_events)
            if window_events else 0.0
        ),
        "depth_distribution": _depth_distribution(window_events),
        "absent_5_mean": _mean([len(item.absent_5) for item in window]),
        "absent_endings_mean": _mean([len(item.absent_endings) for item in window]),
        "concentration_mean": _mean([sum(count * count for count in item.occupancy_9) for item in window]),
    }


def _metric_changes(left: dict[str, object], right: dict[str, object]) -> dict[str, float]:
    return {
        "annihilated_9": abs(right["annihilated_9_mean"] - left["annihilated_9_mean"]),
        "continued_annihilation": abs(right["continued_annihilation_rate"] - left["continued_annihilation_rate"]),
        "return_depth_distribution": 0.5 * sum(
            abs(a - b) for a, b in zip(left["depth_distribution"], right["depth_distribution"])
        ),
        "absent_5": abs(right["absent_5_mean"] - left["absent_5_mean"]),
        "absent_endings": abs(right["absent_endings_mean"] - left["absent_endings_mean"]),
        "concentration": abs(right["concentration_mean"] - left["concentration_mean"]),
    }


def percentile_collapse(draws: list[object], events: list[dict[str, object]]) -> dict[str, object]:
    structures = [build_draw_structure(draw) for draw in draws]
    if len(structures) < 101:
        return {"stage": "NORMAL", "sample_count": 0, "official": False, "metrics": {}}
    changes = []
    for end in range(100, len(structures) + 1):
        left = _window_metrics(structures, events, end - 100, end - 50)
        right = _window_metrics(structures, events, end - 50, end)
        changes.append(_metric_changes(left, right))
    current = changes[-1]
    history = changes[:-1]
    metric_results = {}
    stages = []
    for name, value in current.items():
        percentile = 100 * sum(previous <= value for previous in (item[name] for item in history)) / len(history)
        if percentile >= 99:
            stage = "SEVERE"
        elif percentile >= 95:
            stage = "WARNING"
        elif percentile >= 90:
            stage = "CAUTION"
        else:
            stage = "NORMAL"
        stages.append(stage)
        metric_results[name] = {"current_change": value, "percentile": percentile, "stage": stage}
    official = len(history) >= 100
    return {
        "stage": _stage_max(*stages) if official else "NORMAL",
        "sample_count": len(history),
        "official": official,
        "window": "previous 50 draws versus latest 50 draws",
        "metrics": metric_results,
    }


def _classify(record: dict[str, object], percentile_stage: str) -> dict[str, object]:
    result = json.loads(json.dumps(record))
    periods = result["primary_performance"]
    overall = periods["overall"]
    recent_100 = periods["recent_100"]
    recent_50 = periods["recent_50"]
    risk = opposite_risk(result)
    enough_reference = (
        overall["sample_count"] >= 20
        and recent_100["sample_count"] >= 8
        and recent_50["sample_count"] >= 5
    )
    fixed = fixed_collapse_stage(
        overall["integrated_rate"], recent_100["integrated_rate"], recent_50["integrated_rate"]
    )
    final_collapse = _stage_max(fixed["stage"], percentile_stage)
    criteria = result["gate"]["criteria"]
    criteria["opposite_hypothesis_risk"] = risk
    criteria["structure_collapse_not_severe"] = final_collapse != "SEVERE"
    official_pass = all((
        criteria["overall_sample_at_least_30"],
        criteria["overall_integrated_at_least_random_plus_1_5pp"],
        criteria["recent_100_sample_at_least_15"],
        criteria["recent_100_integrated_at_least_random"],
        criteria["recent_50_sample_at_least_8"],
        criteria["recent_50_not_below_random_by_more_than_2pp"],
        criteria["main_rate_at_least_random"],
        criteria["bonus_dependency"] == "NO",
        risk in ("LOW", "MEDIUM"),
        final_collapse != "SEVERE",
    ))

    if overall["integrated_rate"] <= RANDOM_INTEGRATED or risk == "HIGH":
        status = "FAIL"
    elif not enough_reference or risk == "HOLD_SAMPLE_INSUFFICIENT" or final_collapse == "SEVERE":
        status = "HOLD"
    elif result["role"] == "RETURN":
        status = "PASS" if official_pass else "WEAKEN"
    elif (
        overall["main_rate"] < RANDOM_MAIN
        or recent_100["integrated_rate"] < RANDOM_INTEGRATED
        or recent_50["integrated_rate"] < RANDOM_INTEGRATED - 0.02
    ):
        status = "WEAKEN"
    else:
        status = "TEST"

    result["gate"]["provisional_numeric_status"] = status
    result["rule_state"] = "EXPERIMENTAL_OFFICIAL_REVIEW" if result["role"] == "RETURN" else "TEST"
    result["status"] = status
    result["hold_reasons"] = []
    if status == "HOLD":
        if not enough_reference or risk == "HOLD_SAMPLE_INSUFFICIENT":
            result["hold_reasons"].append("SAMPLE_INSUFFICIENT")
        if final_collapse == "SEVERE":
            result["hold_reasons"].append("STRUCTURE_SEVERE")
    result["independent_evidence_groups"]["risk"] = risk in ("LOW", "MEDIUM")
    result["structure_collapse"] = {
        "fixed": fixed,
        "percentile_stage": percentile_stage,
        "final_stage": final_collapse,
    }
    result["experimental_rule_version"] = EXPERIMENT_VERSION
    return result


def create_experimental_candidates(
    candidate_dir: Path,
    structure_dir: Path,
    backtest_dir: Path,
    output_root: Path,
) -> Path:
    candidate_meta = json.loads((candidate_dir / "metadata.json").read_text(encoding="utf-8"))
    structure_meta = json.loads((structure_dir / "metadata.json").read_text(encoding="utf-8"))
    backtest_meta = json.loads((backtest_dir / "metadata.json").read_text(encoding="utf-8"))
    if {candidate_meta.get("target_round"), structure_meta.get("target_round"), backtest_meta.get("target_round")} != {1236}:
        raise ExperimentalRuleError("이번 예외 승인은 1236회에만 적용할 수 있습니다.")
    gates_path = candidate_dir / "candidate-gates.json"
    input_path = structure_dir / "analysis-input.csv"
    events_path = backtest_dir / "return-events.jsonl"
    if candidate_meta.get("candidate_gates_sha256") != sha256_file(gates_path):
        raise ExperimentalRuleError("기존 후보 자료가 변경되었습니다.")
    if structure_meta.get("effective_data_sha256") != sha256_file(input_path):
        raise ExperimentalRuleError("실험 입력 데이터가 변경되었습니다.")
    records = json.loads(gates_path.read_text(encoding="utf-8"))
    draws = load_and_validate_csv(input_path)
    events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line]
    percentile = percentile_collapse(draws, events)

    def calculate() -> list[dict[str, object]]:
        return [_classify(record, percentile["stage"]) for record in records]

    reruns = [calculate() for _ in range(10)]
    serialized = [json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for value in reruns]
    if len(set(serialized)) != 1:
        raise ExperimentalRuleError("실험 후보 판정의 10회 결과가 일치하지 않습니다.")
    experimental = reruns[0]

    final_dir = output_root / "candidates-1236"
    staging = output_root / ".candidates-1236.staging"
    if final_dir.exists() or staging.exists():
        raise FileExistsError("1236회 실험 후보 결과가 이미 존재합니다.")
    staging.mkdir(parents=True)
    try:
        output_gates = staging / "candidate-gates.json"
        output_gates.write_text(
            json.dumps(experimental, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        official = [record["number"] for record in experimental if record["status"] == "PASS"]
        valid_tests = [
            record["number"] for record in experimental
            if record["role"] == "NON_RETURN_TEST" and record["status"] == "TEST"
        ]
        report = {
            "target_round": 1236,
            "experiment_version": EXPERIMENT_VERSION,
            "label": "실험 재계산 결과·당시 공식 추천 아님",
            "data_cutoff_round": 1235,
            "original_locked_result": "HOLD",
            "official_pass_candidates": official,
            "valid_test_candidates": valid_tests,
            "official_candidate_result": "OFFICIAL" if len(official) >= 6 else "HOLD",
            "percentile_structure_collapse": percentile,
            "status_counts": dict(Counter(record["status"] for record in experimental)),
            "approved_scope": "1236_ONLY",
            "forced_fill_performed": False,
        }
        report_path = staging / "candidate-report.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        metadata = {
            "engine_version": EXPERIMENT_VERSION,
            "analysis_type": "CANDIDATE_GATE_EVALUATION",
            "analysis_status": "COMPLETE",
            "target_round": 1236,
            "source_candidates": str(candidate_dir.resolve()),
            "source_structure": str(structure_dir.resolve()),
            "source_backtest": str(backtest_dir.resolve()),
            "source_effective_data_sha256": structure_meta["effective_data_sha256"],
            "candidate_gates_sha256": sha256_file(output_gates),
            "candidate_report_sha256": sha256_file(report_path),
            "determinism_10_runs": "PASS",
            "determinism_result_sha256": hashlib.sha256(serialized[0].encode()).hexdigest(),
            "historical_official_recommendation": False,
            "approved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        (staging / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        staging.rename(final_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return final_dir

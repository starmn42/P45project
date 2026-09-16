from __future__ import annotations

import hashlib
import json
import math
import shutil
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from .data import Draw, ENGINE_VERSION, load_and_validate_csv, sha256_file
from .structure import NINE_GROUPS, StructureAnalysisError, build_draw_structure


class BacktestError(ValueError):
    pass


@dataclass(frozen=True)
class ReturnEvent:
    target_round: int
    generation_cutoff_round: int
    group_index: int
    group: str
    previous_occupancy_vector: tuple[int, int, int, int, int]
    integrated_depth: int
    main_depth: int
    bonus_returned: bool
    integrated_depth_class: str


def _group_label(index: int) -> str:
    start, end = NINE_GROUPS[index]
    return f"{start}~{end}"


def _depth_class(depth: int) -> str:
    return str(depth) if depth <= 2 else "3_PLUS"


def generate_return_events(draws: list[Draw]) -> list[ReturnEvent]:
    events: list[ReturnEvent] = []
    for previous, outcome in zip(draws, draws[1:]):
        previous_structure = build_draw_structure(previous)
        for index, count in enumerate(previous_structure.occupancy_9):
            if count != 0:
                continue
            start, end = NINE_GROUPS[index]
            main_depth = sum(start <= number <= end for number in outcome.main)
            bonus_returned = start <= outcome.bonus <= end
            integrated_depth = main_depth + int(bonus_returned)
            events.append(ReturnEvent(
                target_round=outcome.round,
                generation_cutoff_round=previous.round,
                group_index=index,
                group=_group_label(index),
                previous_occupancy_vector=previous_structure.occupancy_9,
                integrated_depth=integrated_depth,
                main_depth=main_depth,
                bonus_returned=bonus_returned,
                integrated_depth_class=_depth_class(integrated_depth),
            ))
    return events


def wilson_interval(successes: int, trials: int, z: float = 1.959963984540054) -> tuple[float, float] | None:
    if trials == 0:
        return None
    probability = successes / trials
    denominator = 1 + z * z / trials
    center = (probability + z * z / (2 * trials)) / denominator
    margin = z * math.sqrt(probability * (1 - probability) / trials + z * z / (4 * trials * trials)) / denominator
    return center - margin, center + margin


def _random_depth_probabilities(draw_count: int) -> dict[str, float]:
    denominator = math.comb(45, draw_count)
    exact = {
        depth: math.comb(9, depth) * math.comb(36, draw_count - depth) / denominator
        for depth in range(0, min(9, draw_count) + 1)
    }
    return {
        "0": exact.get(0, 0.0),
        "1": exact.get(1, 0.0),
        "2": exact.get(2, 0.0),
        "3_PLUS": sum(value for depth, value in exact.items() if depth >= 3),
        "return_any": 1 - exact.get(0, 0.0),
    }


def summarize_events(events: list[ReturnEvent]) -> dict[str, object]:
    sample = len(events)
    integrated_return = sum(event.integrated_depth > 0 for event in events)
    main_return = sum(event.main_depth > 0 for event in events)
    integrated_depths = Counter(event.integrated_depth_class for event in events)
    main_depths = Counter(_depth_class(event.main_depth) for event in events)
    integrated_ci = wilson_interval(integrated_return, sample)
    main_ci = wilson_interval(main_return, sample)
    integrated_random = _random_depth_probabilities(7)
    main_random = _random_depth_probabilities(6)
    return {
        "sample_count": sample,
        "integrated": {
            "depth_counts": {key: integrated_depths[key] for key in ("0", "1", "2", "3_PLUS")},
            "return_count": integrated_return,
            "return_rate": integrated_return / sample if sample else None,
            "wilson_95": list(integrated_ci) if integrated_ci else None,
            "random_structural_reference": integrated_random,
            "return_rate_minus_random": integrated_return / sample - integrated_random["return_any"] if sample else None,
        },
        "main": {
            "depth_counts": {key: main_depths[key] for key in ("0", "1", "2", "3_PLUS")},
            "return_count": main_return,
            "return_rate": main_return / sample if sample else None,
            "wilson_95": list(main_ci) if main_ci else None,
            "random_structural_reference": main_random,
            "return_rate_minus_random": main_return / sample - main_random["return_any"] if sample else None,
        },
        "bonus_return_count": sum(event.bonus_returned for event in events),
        "opposite_hypothesis": {
            "return": integrated_return,
            "continued_annihilation": sample - integrated_return,
            "risk_rating": "NOT_RATED_MISSING_THRESHOLD",
        },
    }


def _period_event_sets(events: list[ReturnEvent], draws: list[Draw]) -> dict[str, list[ReturnEvent]]:
    outcome_rounds = [draw.round for draw in draws[1:]]
    midpoint = len(outcome_rounds) // 2
    first_rounds = set(outcome_rounds[:midpoint])
    second_rounds = set(outcome_rounds[midpoint:])
    recent_100 = set(outcome_rounds[-100:])
    recent_50 = set(outcome_rounds[-50:])
    recent_20 = set(outcome_rounds[-20:])
    return {
        "overall": events,
        "first_half": [event for event in events if event.target_round in first_rounds],
        "second_half": [event for event in events if event.target_round in second_rounds],
        "recent_100": [event for event in events if event.target_round in recent_100],
        "recent_50": [event for event in events if event.target_round in recent_50],
        "recent_20": [event for event in events if event.target_round in recent_20],
    }


def _validate_structure_bundle(structure_dir: Path) -> tuple[dict[str, object], dict[str, object], Path]:
    metadata_path = structure_dir / "metadata.json"
    report_path = structure_dir / "structure-report.json"
    input_path = structure_dir / "analysis-input.csv"
    if not all(path.is_file() for path in (metadata_path, report_path, input_path)):
        raise BacktestError("페이즈 4 구조 분석 묶음의 필수 파일이 없습니다.")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BacktestError(f"구조 분석 묶음을 읽을 수 없습니다: {exc}") from exc
    if metadata.get("analysis_type") != "BASIC_STRUCTURE" or metadata.get("analysis_status") != "COMPLETE":
        raise BacktestError("완료된 페이즈 4 구조 분석만 시험할 수 있습니다.")
    if metadata.get("effective_data_sha256") != sha256_file(input_path):
        raise BacktestError("구조 분석 입력 데이터가 변경되었습니다.")
    if metadata.get("structure_report_sha256") != sha256_file(report_path):
        raise BacktestError("구조 분석 보고서가 변경되었습니다.")
    return metadata, report, input_path


def _exact_vector_summary(events: list[ReturnEvent], vector: tuple[int, ...]) -> dict[str, object]:
    matching = [event for event in events if event.previous_occupancy_vector == vector]
    occurrence_count = len({event.target_round for event in matching})
    if occurrence_count >= 20:
        evidence_status = "OFFICIAL_EVIDENCE"
    elif occurrence_count >= 10:
        evidence_status = "WEAK_EVIDENCE"
    else:
        evidence_status = "REFERENCE_OR_HOLD"
    by_group = {
        _group_label(index): summarize_events([event for event in matching if event.group_index == index])
        for index, count in enumerate(vector) if count == 0
    }
    return {
        "vector": list(vector),
        "occurrence_count": occurrence_count,
        "event_count": len(matching),
        "evidence_status": evidence_status,
        "by_annihilated_group": by_group,
    }


def run_backtest(structure_dir: Path, output_root: Path) -> Path:
    source_metadata, structure_report, input_path = _validate_structure_bundle(structure_dir)
    try:
        draws = load_and_validate_csv(input_path)
    except Exception as exc:
        raise BacktestError(f"구조 분석 입력 데이터를 다시 읽을 수 없습니다: {exc}") from exc
    events = generate_return_events(draws)
    target_round = int(source_metadata["target_round"])
    result_id = f"backtest-{target_round}"
    final_dir = output_root / result_id
    staging = output_root / f".{result_id}.staging"
    if final_dir.exists():
        raise FileExistsError(f"이미 생성된 과거 회차 시험이 있습니다: {final_dir}")
    if staging.exists():
        raise FileExistsError(f"미완료 과거 회차 시험이 있습니다: {staging}")
    staging.mkdir(parents=True)
    try:
        ledger_path = staging / "return-events.jsonl"
        with ledger_path.open("w", encoding="utf-8", newline="") as stream:
            for event in events:
                stream.write(json.dumps(asdict(event), ensure_ascii=False, sort_keys=True) + "\n")
        periods = _period_event_sets(events, draws)
        current_vector = tuple(structure_report["previous_draw_structure"]["occupancy_9"])
        rounds_without_annihilation = sum(
            not build_draw_structure(draw).annihilated_9 for draw in draws[:-1]
        )
        rounds_with_multiple = sum(
            len(build_draw_structure(draw).annihilated_9) >= 2 for draw in draws[:-1]
        )
        report = {
            "record_type": "BACKTEST",
            "target_round": target_round,
            "tested_outcome_rounds": {"start": 2, "end": draws[-1].round},
            "event_definition": "one event per annihilated 9-number group in the previous draw",
            "leakage_audit": {
                "status": "PASS",
                "generation_rule": "target R condition uses draw R-1 only",
                "evaluation_rule": "target R result is read only after condition creation",
                "event_count": len(events),
                "cutoff_mismatch_count": sum(
                    event.generation_cutoff_round != event.target_round - 1 for event in events
                ),
            },
            "periods": {name: summarize_events(items) for name, items in periods.items()},
            "recent_20_usage": "OBSERVATION_ONLY",
            "current_exact_occupancy_vector": _exact_vector_summary(events, current_vector),
            "structural_counts": {
                "prior_rounds_tested": len(draws) - 1,
                "rounds_without_annihilated_9_group": rounds_without_annihilation,
                "rounds_with_multiple_annihilated_9_groups": rounds_with_multiple,
            },
            "official_gate": {
                "status": "HOLD",
                "reason": "candidate generation and candidate exposure do not exist before Phase 6",
            },
            "structure_collapse": {
                "fixed_threshold_stage": "HOLD",
                "percentile_stage": "HOLD",
                "final_stage": "HOLD",
                "reasons": [
                    "candidate hit-rate decline is unavailable before Phase 6",
                    "the guide does not predefine aggregation formulas for structural percentile change metrics",
                ],
                "arbitrary_threshold_created": False,
            },
            "candidate_selection_performed": False,
        }
        report_path = staging / "backtest-report.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        metadata = {
            "engine_version": ENGINE_VERSION,
            "analysis_type": "SEQUENTIAL_RETURN_BACKTEST",
            "analysis_status": "COMPLETE",
            "record_type": "BACKTEST",
            "target_round": target_round,
            "source_structure": str(structure_dir.resolve()),
            "source_effective_data_sha256": source_metadata["effective_data_sha256"],
            "event_ledger_sha256": sha256_file(ledger_path),
            "backtest_report_sha256": sha256_file(report_path),
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        (staging / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        staging.rename(final_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return final_dir

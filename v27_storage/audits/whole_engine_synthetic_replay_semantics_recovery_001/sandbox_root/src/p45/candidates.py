from __future__ import annotations

import json
import hashlib
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from .backtest import wilson_interval
from .data import Draw, ENGINE_VERSION, load_and_validate_csv, sha256_file
from .structure import FIVE_GROUPS, NINE_GROUPS, build_draw_structure


RANDOM_INTEGRATED = 7 / 45
RANDOM_MAIN = 6 / 45


class CandidateGateError(ValueError):
    pass


@dataclass(frozen=True)
class Exposure:
    target_round: int
    integrated_hit: bool
    main_hit: bool
    bonus_hit: bool


def _group_index(number: int) -> int:
    return (number - 1) // 9


def _five_group(number: int) -> str:
    index = (number - 1) // 5
    start, end = FIVE_GROUPS[index]
    return f"{start}~{end}"


def _exposures(
    draws: list[Draw],
    previous_vectors: list[tuple[int, ...]],
    number: int,
    condition: Callable[[tuple[int, ...]], bool],
) -> list[Exposure]:
    result: list[Exposure] = []
    for vector, outcome in zip(previous_vectors, draws[1:]):
        if condition(vector):
            main_hit = number in outcome.main
            bonus_hit = number == outcome.bonus
            result.append(Exposure(outcome.round, main_hit or bonus_hit, main_hit, bonus_hit))
    return result


def _period_exposures(exposures: list[Exposure], draws: list[Draw]) -> dict[str, list[Exposure]]:
    outcome_rounds = [draw.round for draw in draws[1:]]
    midpoint = len(outcome_rounds) // 2
    sets = {
        "first_half": set(outcome_rounds[:midpoint]),
        "second_half": set(outcome_rounds[midpoint:]),
        "recent_100": set(outcome_rounds[-100:]),
        "recent_50": set(outcome_rounds[-50:]),
        "recent_20": set(outcome_rounds[-20:]),
    }
    return {
        "overall": exposures,
        **{name: [item for item in exposures if item.target_round in rounds] for name, rounds in sets.items()},
    }


def _stats(exposures: list[Exposure]) -> dict[str, object]:
    sample = len(exposures)
    integrated = sum(item.integrated_hit for item in exposures)
    main = sum(item.main_hit for item in exposures)
    bonus = sum(item.bonus_hit for item in exposures)
    integrated_ci = wilson_interval(integrated, sample)
    main_ci = wilson_interval(main, sample)
    return {
        "sample_count": sample,
        "integrated_hits": integrated,
        "integrated_rate": integrated / sample if sample else None,
        "integrated_wilson_95": list(integrated_ci) if integrated_ci else None,
        "main_hits": main,
        "main_rate": main / sample if sample else None,
        "main_wilson_95": list(main_ci) if main_ci else None,
        "bonus_hits": bonus,
        "bonus_rate": bonus / sample if sample else None,
    }


def _gate_result(periods: dict[str, dict[str, object]]) -> tuple[dict[str, object], str]:
    overall = periods["overall"]
    recent_100 = periods["recent_100"]
    recent_50 = periods["recent_50"]
    overall_rate = overall["integrated_rate"]
    main_rate = overall["main_rate"]
    bonus_dependent = bool(
        overall_rate is not None
        and overall_rate >= RANDOM_INTEGRATED + 0.015
        and (main_rate is None or main_rate < RANDOM_MAIN)
    )
    gates = {
        "sequential_validation": "PASS",
        "overall_sample_at_least_30": overall["sample_count"] >= 30,
        "overall_integrated_at_least_random_plus_1_5pp": (
            overall_rate is not None and overall_rate >= RANDOM_INTEGRATED + 0.015
        ),
        "recent_100_sample_at_least_15": recent_100["sample_count"] >= 15,
        "recent_100_integrated_at_least_random": (
            recent_100["integrated_rate"] is not None
            and recent_100["integrated_rate"] >= RANDOM_INTEGRATED
        ),
        "recent_50_sample_at_least_8": recent_50["sample_count"] >= 8,
        "recent_50_not_below_random_by_more_than_2pp": (
            recent_50["integrated_rate"] is not None
            and recent_50["integrated_rate"] >= RANDOM_INTEGRATED - 0.02
        ),
        "main_rate_at_least_random": main_rate is not None and main_rate >= RANDOM_MAIN,
        "bonus_dependency": "YES" if bonus_dependent else "NO",
        "opposite_hypothesis_risk": "UNRESOLVED_MISSING_THRESHOLD",
        "structure_collapse_not_severe": "UNRESOLVED_PHASE_5_HOLD",
        "deterministic_generation_rule": "PASS",
    }
    if overall_rate is not None and overall_rate <= RANDOM_INTEGRATED:
        provisional = "FAIL"
    elif overall["sample_count"] < 20:
        provisional = "HOLD"
    elif overall["sample_count"] < 30:
        provisional = "WEAKEN"
    elif not gates["overall_integrated_at_least_random_plus_1_5pp"]:
        provisional = "TEST"
    elif bonus_dependent or not gates["main_rate_at_least_random"]:
        provisional = "WEAKEN"
    elif not gates["recent_100_integrated_at_least_random"]:
        provisional = "WEAKEN"
    elif not gates["recent_50_not_below_random_by_more_than_2pp"]:
        provisional = "WEAKEN"
    else:
        provisional = "NUMERIC_PASS_PENDING_UNRESOLVED_GATES"
    # 반대 위험과 구조 붕괴 관문이 수치로 고정되지 않았으므로 공식 PASS 금지.
    final = "FAIL" if provisional == "FAIL" else "HOLD"
    return {"criteria": gates, "provisional_numeric_status": provisional}, final


def _candidate_record(
    draws: list[Draw],
    previous_vectors: list[tuple[int, ...]],
    number: int,
    role: str,
    current_vector: tuple[int, ...],
    current_absent_5: set[str],
    current_absent_endings: set[int],
) -> dict[str, object]:
    group_index = _group_index(number)
    if role == "RETURN":
        condition_name = "previous candidate group occupancy equals zero"
        condition = lambda vector: vector[group_index] == 0
        rule_state = "OFFICIAL_GATE_REVIEW"
    else:
        current_count = current_vector[group_index]
        condition_name = f"previous candidate group occupancy equals current count {current_count}"
        condition = lambda vector: vector[group_index] == current_count
        rule_state = "TEST"
    primary = _exposures(draws, previous_vectors, number, condition)
    exact = _exposures(draws, previous_vectors, number, lambda vector: vector == current_vector)
    primary_periods = {
        name: _stats(items) for name, items in _period_exposures(primary, draws).items()
    }
    exact_stats = _stats(exact)
    gate, status = _gate_result(primary_periods)
    five_support = _five_group(number) in current_absent_5
    ending_support = number % 10 in current_absent_endings
    return {
        "number": number,
        "role": role,
        "group_9": f"{NINE_GROUPS[group_index][0]}~{NINE_GROUPS[group_index][1]}",
        "rule_state": rule_state,
        "primary_condition": condition_name,
        "primary_performance": primary_periods,
        "exact_occupancy_vector_performance": exact_stats,
        "independent_evidence_groups": {
            "structure": primary_periods["overall"]["sample_count"] >= 30,
            "performance": gate["provisional_numeric_status"] == "NUMERIC_PASS_PENDING_UNRESOLVED_GATES",
            "risk": "UNRESOLVED",
            "composition": "NOT_APPLICABLE_BEFORE_FINAL_SELECTION",
        },
        "auxiliary_annihilation_support": {
            "five_group_or_ending": five_support or ending_support,
            "five_group": _five_group(number) if five_support else None,
            "ending": number % 10 if ending_support else None,
            "counts_as_independent_evidence": False,
        },
        "gate": gate,
        "status": status,
        "hold_reasons": [
            "OPPOSITE_RISK_THRESHOLD_MISSING",
            "STRUCTURE_COLLAPSE_GATE_UNRESOLVED",
        ] if status == "HOLD" else [],
    }


def _validate_inputs(structure_dir: Path, backtest_dir: Path) -> tuple[dict[str, object], dict[str, object], Path]:
    structure_meta_path = structure_dir / "metadata.json"
    structure_report_path = structure_dir / "structure-report.json"
    input_path = structure_dir / "analysis-input.csv"
    backtest_meta_path = backtest_dir / "metadata.json"
    backtest_report_path = backtest_dir / "backtest-report.json"
    for path in (structure_meta_path, structure_report_path, input_path, backtest_meta_path, backtest_report_path):
        if not path.is_file():
            raise CandidateGateError(f"필수 입력 파일이 없습니다: {path}")
    structure_meta = json.loads(structure_meta_path.read_text(encoding="utf-8"))
    structure_report = json.loads(structure_report_path.read_text(encoding="utf-8"))
    backtest_meta = json.loads(backtest_meta_path.read_text(encoding="utf-8"))
    if structure_meta.get("analysis_type") != "BASIC_STRUCTURE":
        raise CandidateGateError("페이즈 4 구조 분석 입력이 아닙니다.")
    if backtest_meta.get("analysis_type") != "SEQUENTIAL_RETURN_BACKTEST":
        raise CandidateGateError("페이즈 5 순차검증 입력이 아닙니다.")
    if structure_meta.get("target_round") != backtest_meta.get("target_round"):
        raise CandidateGateError("구조 분석과 순차검증의 대상 회차가 다릅니다.")
    if structure_meta.get("effective_data_sha256") != sha256_file(input_path):
        raise CandidateGateError("페이즈 4 분석 입력이 변경되었습니다.")
    if structure_meta.get("structure_report_sha256") != sha256_file(structure_report_path):
        raise CandidateGateError("페이즈 4 보고서가 변경되었습니다.")
    if backtest_meta.get("backtest_report_sha256") != sha256_file(backtest_report_path):
        raise CandidateGateError("페이즈 5 보고서가 변경되었습니다.")
    if backtest_meta.get("source_effective_data_sha256") != structure_meta.get("effective_data_sha256"):
        raise CandidateGateError("페이즈 4와 5의 데이터 해시가 다릅니다.")
    return structure_meta, structure_report, input_path


def evaluate_candidates(structure_dir: Path, backtest_dir: Path, output_root: Path) -> Path:
    source_meta, structure_report, input_path = _validate_inputs(structure_dir, backtest_dir)
    draws = load_and_validate_csv(input_path)
    current = structure_report["previous_draw_structure"]
    current_vector = tuple(current["occupancy_9"])
    annihilated_indices = {index for index, count in enumerate(current_vector) if count == 0}
    absent_5 = set(current["absent_5"])
    absent_endings = set(current["absent_endings"])
    previous_vectors = [build_draw_structure(draw).occupancy_9 for draw in draws[:-1]]

    def calculate_records() -> list[dict[str, object]]:
        return [
            _candidate_record(
                draws,
                previous_vectors,
                number,
                "RETURN" if _group_index(number) in annihilated_indices else "NON_RETURN_TEST",
                current_vector,
                absent_5,
                absent_endings,
            )
            for number in range(1, 46)
        ]

    records = calculate_records()
    target_round = int(source_meta["target_round"])
    result_id = f"candidates-{target_round}"
    final_dir = output_root / result_id
    staging = output_root / f".{result_id}.staging"
    if final_dir.exists():
        raise FileExistsError(f"이미 생성된 후보 판정이 있습니다: {final_dir}")
    if staging.exists():
        raise FileExistsError(f"미완료 후보 판정이 있습니다: {staging}")
    staging.mkdir(parents=True)
    try:
        candidate_path = staging / "candidate-gates.json"
        candidate_path.write_text(
            json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        status_counts: dict[str, int] = {}
        for record in records:
            status_counts[record["status"]] = status_counts.get(record["status"], 0) + 1
        report = {
            "target_round": target_round,
            "current_occupancy_vector": list(current_vector),
            "annihilated_9_groups": current["annihilated_9"],
            "return_candidate_numbers": [r["number"] for r in records if r["role"] == "RETURN"],
            "non_return_test_numbers": [r["number"] for r in records if r["role"] == "NON_RETURN_TEST"],
            "status_counts": status_counts,
            "official_pass_candidates": [r["number"] for r in records if r["status"] == "PASS"],
            "valid_test_candidates": [
                r["number"] for r in records
                if r["role"] == "NON_RETURN_TEST" and r["status"] not in ("HOLD", "FAIL")
            ],
            "official_candidate_result": "HOLD",
            "official_candidate_reason": "unresolved opposite-risk and structure-collapse gates",
            "ranking_performed": False,
            "final_six_selected": False,
            "arbitrary_threshold_created": False,
        }
        report_path = staging / "candidate-report.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        # 결정론 검사: 후보 45개 판정을 실제로 10회 독립 재계산한다.
        deterministic_hashes = []
        for _ in range(10):
            rerun = calculate_records()
            canonical = json.dumps(rerun, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            deterministic_hashes.append(hashlib.sha256(canonical.encode()).hexdigest())
        deterministic = len(set(deterministic_hashes)) == 1
        metadata = {
            "engine_version": ENGINE_VERSION,
            "analysis_type": "CANDIDATE_GATE_EVALUATION",
            "analysis_status": "COMPLETE",
            "target_round": target_round,
            "source_structure": str(structure_dir.resolve()),
            "source_backtest": str(backtest_dir.resolve()),
            "source_effective_data_sha256": source_meta["effective_data_sha256"],
            "candidate_gates_sha256": sha256_file(candidate_path),
            "candidate_report_sha256": sha256_file(report_path),
            "determinism_10_runs": "PASS" if deterministic else "FAIL",
            "determinism_result_sha256": deterministic_hashes[0],
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

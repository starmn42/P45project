from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from fractions import Fraction
from pathlib import Path

from .data import ENGINE_VERSION, sha256_file


class SelectionError(ValueError):
    pass


def _fraction(hits: int, samples: int) -> Fraction:
    return Fraction(hits, samples) if samples else Fraction(-1, 1)


def _evidence_count(record: dict[str, object]) -> int:
    evidence = record["independent_evidence_groups"]
    return sum(value is True for value in evidence.values())


def _sample_tier(sample: int) -> int:
    if sample >= 30:
        return 2
    if sample >= 20:
        return 1
    return 0


def _base_rank_key(record: dict[str, object]) -> tuple[object, ...]:
    periods = record["primary_performance"]
    overall = periods["overall"]
    wilson = overall["integrated_wilson_95"]
    wilson_above_random = bool(wilson and wilson[0] >= 7 / 45)
    criteria = record["gate"]["criteria"]
    simultaneous = all((
        criteria["overall_integrated_at_least_random_plus_1_5pp"],
        criteria["recent_100_integrated_at_least_random"],
        criteria["recent_50_not_below_random_by_more_than_2pp"],
    ))
    evidence = record["independent_evidence_groups"]
    sample = int(overall["sample_count"])
    main_fraction = _fraction(int(overall["main_hits"]), sample)
    risk_pass = evidence.get("risk") is True
    composition_pass = evidence.get("composition") is True
    collapse_safe = criteria.get("structure_collapse_not_severe") is True
    return (
        0 if record["status"] == "PASS" else 1,
        0 if wilson_above_random else 1,
        -_evidence_count(record),
        0 if simultaneous else 1,
        0 if evidence.get("structure") is True else 1,
        0 if evidence.get("performance") is True else 1,
        0 if risk_pass else 1,
        0 if composition_pass else 1,
        -main_fraction,
        -_sample_tier(sample),
        -sample,
        0 if collapse_safe else 1,
    )


def _role_overlap(record: dict[str, object], selected: list[dict[str, object]]) -> int:
    return sum(
        int(item["role"] == record["role"]) + int(item["group_9"] == record["group_9"])
        for item in selected
    )


def rank_pool(records: list[dict[str, object]]) -> list[dict[str, object]]:
    remaining = list(records)
    selected: list[dict[str, object]] = []
    while remaining:
        best_base = min(_base_rank_key(record) for record in remaining)
        tied = [record for record in remaining if _base_rank_key(record) == best_base]
        chosen = min(tied, key=lambda record: (_role_overlap(record, selected), record["number"]))
        selected.append(chosen)
        remaining.remove(chosen)
    return selected


def _reason_code(record: dict[str, object]) -> str:
    if record["status"] == "FAIL":
        risk = record.get("gate", {}).get("criteria", {}).get("opposite_hypothesis_risk")
        if risk == "HIGH":
            return "OPPOSITE_HIGH"
        return "OVERALL_FAIL"
    if record["role"] == "NON_RETURN_TEST":
        return "NON_RETURN_TEST_ONLY"
    if record["exact_occupancy_vector_performance"]["sample_count"] < 10:
        return "SAMPLE_INSUFFICIENT"
    if record["status"] == "HOLD":
        return "SAMPLE_INSUFFICIENT"
    if record["status"] in ("WEAKEN", "TEST"):
        return "RECENT_CONFLICT"
    return "RANK_CUTOFF"


def select_final_six(records: list[dict[str, object]]) -> dict[str, object]:
    official_pool = rank_pool([record for record in records if record["status"] == "PASS"])
    test_pool = rank_pool([
        record for record in records
        if record["role"] == "NON_RETURN_TEST"
        and record["rule_state"] == "TEST"
        and record["status"] == "TEST"
    ])

    official_selected = official_pool[:6] if len(official_pool) >= 6 else []
    if official_selected:
        selection_mode = "OFFICIAL"
        selected = official_selected
        official_status = "OFFICIAL"
        mixed_status = "NOT_NEEDED"
    else:
        official_status = "HOLD"
        combined = official_pool + test_pool
        selected = rank_pool(combined)[:6] if len(combined) >= 6 else []
        if selected:
            selection_mode = "MIXED_TEST"
            mixed_status = "MIXED_TEST"
        else:
            selection_mode = "NONE"
            mixed_status = "HOLD"

    selected_numbers = {record["number"] for record in selected}
    alternate = []
    middle = []
    initial = []
    valid_numbers = {record["number"] for record in official_pool + test_pool}
    for record in records:
        item = {"number": record["number"], "reason_code": _reason_code(record)}
        if record["number"] in selected_numbers:
            continue
        if record["number"] in valid_numbers:
            item["reason_code"] = "RANK_CUTOFF"
            alternate.append(item)
        elif record["status"] == "FAIL":
            initial.append(item)
        else:
            middle.append(item)

    return {
        "official_status": official_status,
        "official_hold_reason": None if official_selected else "official PASS candidates fewer than 6",
        "mixed_test_status": mixed_status,
        "mixed_test_hold_reason": None if selected else "official plus valid TEST candidates fewer than 6",
        "selection_mode": selection_mode,
        "official_pool_order": [record["number"] for record in official_pool],
        "valid_test_pool_order": [record["number"] for record in test_pool],
        "selected_numbers": [record["number"] for record in selected],
        "selected_count": len(selected),
        "all_six_unique": len(selected_numbers) == 6 if selected else False,
        "stages": {
            "final_selected": [record["number"] for record in selected],
            "alternate_eliminated": sorted(alternate, key=lambda item: item["number"]),
            "middle_eliminated": sorted(middle, key=lambda item: item["number"]),
            "initial_eliminated": sorted(initial, key=lambda item: item["number"]),
        },
        "forced_fill_performed": False,
    }


def _validate_candidate_bundle(candidate_dir: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    metadata_path = candidate_dir / "metadata.json"
    gates_path = candidate_dir / "candidate-gates.json"
    report_path = candidate_dir / "candidate-report.json"
    if not all(path.is_file() for path in (metadata_path, gates_path, report_path)):
        raise SelectionError("페이즈 6 후보 판정 묶음의 필수 파일이 없습니다.")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        records = json.loads(gates_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SelectionError(f"후보 판정 묶음을 읽을 수 없습니다: {exc}") from exc
    if metadata.get("analysis_type") != "CANDIDATE_GATE_EVALUATION":
        raise SelectionError("페이즈 6 후보 판정 결과가 아닙니다.")
    if metadata.get("analysis_status") != "COMPLETE":
        raise SelectionError("완료되지 않은 후보 판정 결과입니다.")
    if metadata.get("determinism_10_runs") != "PASS":
        raise SelectionError("후보 판정의 10회 결정론 검사가 통과되지 않았습니다.")
    if metadata.get("candidate_gates_sha256") != sha256_file(gates_path):
        raise SelectionError("후보 관문 자료가 판정 후 변경되었습니다.")
    if metadata.get("candidate_report_sha256") != sha256_file(report_path):
        raise SelectionError("후보 보고서가 판정 후 변경되었습니다.")
    if not isinstance(records, list) or len(records) != 45:
        raise SelectionError("후보 판정은 1~45번 전체를 포함해야 합니다.")
    if sorted(record.get("number") for record in records) != list(range(1, 46)):
        raise SelectionError("후보 번호가 누락되거나 중복되었습니다.")
    return metadata, records


def create_selection(candidate_dir: Path, output_root: Path) -> Path:
    source_metadata, records = _validate_candidate_bundle(candidate_dir)
    target_round = int(source_metadata["target_round"])

    # 실제 선택 절차를 10회 재실행해 결과 전체가 같은지 검사한다.
    results = [select_final_six(records) for _ in range(10)]
    serialized = [json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for result in results]
    if len(set(serialized)) != 1:
        raise SelectionError("동일 입력 10회 선택 결과가 일치하지 않습니다.")
    selection = results[0]

    result_id = f"selection-{target_round}"
    final_dir = output_root / result_id
    staging = output_root / f".{result_id}.staging"
    if final_dir.exists():
        raise FileExistsError(f"이미 생성된 최종 선택 결과가 있습니다: {final_dir}")
    if staging.exists():
        raise FileExistsError(f"미완료 최종 선택 결과가 있습니다: {staging}")
    staging.mkdir(parents=True)
    try:
        report = {
            "target_round": target_round,
            **selection,
            "sets_created": False,
            "next_phase": "PHASE_8_SET_PLACEMENT" if selection["selected_count"] == 6 else None,
        }
        report_path = staging / "selection-report.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        metadata = {
            "engine_version": ENGINE_VERSION,
            "analysis_type": "FINAL_SIX_SELECTION",
            "analysis_status": "COMPLETE",
            "target_round": target_round,
            "source_candidates": str(candidate_dir.resolve()),
            "source_candidate_gates_sha256": source_metadata["candidate_gates_sha256"],
            "selection_report_sha256": sha256_file(report_path),
            "determinism_10_runs": "PASS",
            "determinism_result_sha256": hashlib.sha256(serialized[0].encode()).hexdigest(),
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

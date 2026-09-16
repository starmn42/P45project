from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from .data import ENGINE_VERSION, sha256_file


class PlacementError(ValueError):
    pass


def _evidence_signature(record: dict[str, object]) -> tuple[str, ...]:
    evidence = record["independent_evidence_groups"]
    return tuple(sorted(name for name, value in evidence.items() if value is True))


def _distribution_key(
    candidate: dict[str, object],
    target_set: list[dict[str, object]],
    set_index: int,
) -> tuple[int, int, int, int, int]:
    # 지침의 우선순위를 가중치 없이 사전식으로 적용한다.
    same_role = sum(item["role"] == candidate["role"] for item in target_set)
    same_group = sum(item["group_9"] == candidate["group_9"] for item in target_set)
    signature = _evidence_signature(candidate)
    same_evidence = sum(_evidence_signature(item) == signature for item in target_set)
    return same_role, same_group, same_evidence, len(target_set), set_index


def place_two_sets(
    selected_numbers: list[int],
    records_by_number: dict[int, dict[str, object]],
) -> dict[str, object]:
    if len(selected_numbers) != 6 or len(set(selected_numbers)) != 6:
        return {
            "placement_status": "HOLD",
            "hold_reason": "final selection does not contain six unique candidates",
            "set_1": [],
            "set_2": [],
            "candidate_replacement_performed": False,
        }
    if any(number not in records_by_number for number in selected_numbers):
        raise PlacementError("선택 번호의 후보 근거를 찾을 수 없습니다.")

    ordered = [records_by_number[number] for number in selected_numbers]
    return_candidates = [record for record in ordered if record["role"] == "RETURN"]
    set_1: list[dict[str, object]] = []
    set_2: list[dict[str, object]] = []

    # 복귀 1순위는 세트1, 복귀 2순위는 세트2에 고정한다.
    if return_candidates:
        set_1.append(return_candidates[0])
    if len(return_candidates) >= 2:
        set_2.append(return_candidates[1])

    placed = {record["number"] for record in set_1 + set_2}
    for candidate in ordered:
        if candidate["number"] in placed:
            continue
        available: list[tuple[int, list[dict[str, object]]]] = []
        if len(set_1) < 3:
            available.append((1, set_1))
        if len(set_2) < 3:
            available.append((2, set_2))
        if not available:
            raise PlacementError("세트 정원이 찼는데 미배치 후보가 남았습니다.")
        _, destination = min(
            available,
            key=lambda pair: _distribution_key(candidate, pair[1], pair[0]),
        )
        destination.append(candidate)
        placed.add(candidate["number"])

    numbers_1 = [record["number"] for record in set_1]
    numbers_2 = [record["number"] for record in set_2]
    combined = numbers_1 + numbers_2
    if len(numbers_1) != 3 or len(numbers_2) != 3:
        raise PlacementError("각 세트가 정확히 3개로 구성되지 않았습니다.")
    if set(combined) != set(selected_numbers) or len(set(combined)) != 6:
        raise PlacementError("배치 과정에서 후보가 교체·누락·중복되었습니다.")
    return {
        "placement_status": "COMPLETE",
        "hold_reason": None,
        "set_1": numbers_1,
        "set_2": numbers_2,
        "candidate_replacement_performed": False,
    }


def _validate_inputs(
    selection_dir: Path,
    candidate_dir: Path,
) -> tuple[dict[str, object], dict[str, object], list[dict[str, object]]]:
    selection_meta_path = selection_dir / "metadata.json"
    selection_report_path = selection_dir / "selection-report.json"
    candidate_meta_path = candidate_dir / "metadata.json"
    candidate_gates_path = candidate_dir / "candidate-gates.json"
    for path in (selection_meta_path, selection_report_path, candidate_meta_path, candidate_gates_path):
        if not path.is_file():
            raise PlacementError(f"필수 입력 파일이 없습니다: {path}")
    try:
        selection_meta = json.loads(selection_meta_path.read_text(encoding="utf-8"))
        selection_report = json.loads(selection_report_path.read_text(encoding="utf-8"))
        candidate_meta = json.loads(candidate_meta_path.read_text(encoding="utf-8"))
        records = json.loads(candidate_gates_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PlacementError(f"배치 입력을 읽을 수 없습니다: {exc}") from exc
    if selection_meta.get("analysis_type") != "FINAL_SIX_SELECTION":
        raise PlacementError("페이즈 7 선택 결과가 아닙니다.")
    if selection_meta.get("analysis_status") != "COMPLETE":
        raise PlacementError("완료되지 않은 선택 결과입니다.")
    if selection_meta.get("selection_report_sha256") != sha256_file(selection_report_path):
        raise PlacementError("선택 보고서가 생성 후 변경되었습니다.")
    if candidate_meta.get("analysis_type") != "CANDIDATE_GATE_EVALUATION":
        raise PlacementError("페이즈 6 후보 근거가 아닙니다.")
    if candidate_meta.get("candidate_gates_sha256") != sha256_file(candidate_gates_path):
        raise PlacementError("후보 근거가 판정 후 변경되었습니다.")
    if selection_meta.get("target_round") != candidate_meta.get("target_round"):
        raise PlacementError("선택 결과와 후보 근거의 대상 회차가 다릅니다.")
    if selection_meta.get("source_candidate_gates_sha256") != candidate_meta.get("candidate_gates_sha256"):
        raise PlacementError("선택에 사용한 후보 근거와 현재 후보 근거가 다릅니다.")
    return selection_meta, selection_report, records


def create_set_placement(selection_dir: Path, candidate_dir: Path, output_root: Path) -> Path:
    selection_meta, selection_report, records = _validate_inputs(selection_dir, candidate_dir)
    records_by_number = {record["number"]: record for record in records}
    selected_numbers = selection_report["selected_numbers"]

    results = [place_two_sets(selected_numbers, records_by_number) for _ in range(10)]
    serialized = [json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for result in results]
    if len(set(serialized)) != 1:
        raise PlacementError("동일 입력 10회 세트 배치 결과가 일치하지 않습니다.")
    placement = results[0]

    target_round = int(selection_meta["target_round"])
    result_id = f"sets-{target_round}"
    final_dir = output_root / result_id
    staging = output_root / f".{result_id}.staging"
    if final_dir.exists():
        raise FileExistsError(f"이미 생성된 세트 배치 결과가 있습니다: {final_dir}")
    if staging.exists():
        raise FileExistsError(f"미완료 세트 배치 결과가 있습니다: {staging}")
    staging.mkdir(parents=True)
    try:
        report = {
            "target_round": target_round,
            "selection_mode": selection_report["selection_mode"],
            "selected_numbers_before_placement": selected_numbers,
            **placement,
        }
        report_path = staging / "set-report.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        metadata = {
            "engine_version": ENGINE_VERSION,
            "analysis_type": "TWO_SET_PLACEMENT",
            "analysis_status": "COMPLETE",
            "target_round": target_round,
            "source_selection": str(selection_dir.resolve()),
            "source_candidates": str(candidate_dir.resolve()),
            "source_selection_report_sha256": selection_meta["selection_report_sha256"],
            "set_report_sha256": sha256_file(report_path),
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

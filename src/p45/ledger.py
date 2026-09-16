from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from .data import ENGINE_VERSION, sha256_file


RULE_VERSIONS = {
    "performance_gate": "CONSERVATIVE-B-1.2",
    "exact_structure": "EXACT-OCCUPANCY-VECTOR-1.1",
    "return_selection": "RETURN-CANDIDATE-GATE-1.2",
    "non_return_selection": "NON-RETURN-CANDIDATE-GATE-1.0",
    "non_return_operation": "NON-RETURN-TEST-PROMOTION-1.2",
    "structure_collapse": "HYBRID-FIXED-PERCENTILE-1.2",
    "determinism": "DETERMINISTIC-SELECTION-1.2",
    "ledger": "IMMUTABLE-LEDGER-1.2",
}


class LedgerError(ValueError):
    pass


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LedgerError(f"JSON 파일을 읽을 수 없습니다: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LedgerError(f"JSON 객체가 아닙니다: {path}")
    return value


def _artifact_meta(directory: Path, expected_type: str) -> dict[str, object]:
    metadata_path = directory / "metadata.json"
    if not metadata_path.is_file():
        raise LedgerError(f"단계 메타데이터가 없습니다: {directory}")
    metadata = _read_json(metadata_path)
    if metadata.get("analysis_type") != expected_type:
        raise LedgerError(f"예상 단계가 아닙니다: {directory} / {metadata.get('analysis_type')}")
    if metadata.get("analysis_status") != "COMPLETE":
        raise LedgerError(f"완료되지 않은 단계입니다: {directory}")
    return metadata


def _manifest_entries(root: Path) -> list[dict[str, object]]:
    entries = []
    for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda item: item.as_posix()):
        entries.append({
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    return entries


def verify_locked_record(record_dir: Path) -> dict[str, object]:
    manifest_path = record_dir / "manifest.json"
    metadata_path = record_dir / "metadata.json"
    if not manifest_path.is_file() or not metadata_path.is_file():
        raise LedgerError("잠금 기록의 manifest 또는 metadata가 없습니다.")
    metadata = _read_json(metadata_path)
    if metadata.get("manifest_sha256") != sha256_file(manifest_path):
        raise LedgerError("잠금 기록 manifest가 변경되었습니다.")
    manifest = _read_json(manifest_path)
    for entry in manifest.get("files", []):
        path = record_dir / entry["path"]
        if not path.is_file():
            raise LedgerError(f"잠금 기록 파일이 누락되었습니다: {entry['path']}")
        if path.stat().st_size != entry["size"] or sha256_file(path) != entry["sha256"]:
            raise LedgerError(f"잠금 기록 파일이 변경되었습니다: {entry['path']}")
    return metadata


def lock_analysis(
    *,
    dataset_dir: Path,
    structure_dir: Path,
    backtest_dir: Path,
    candidate_dir: Path,
    selection_dir: Path,
    sets_dir: Path,
    ledger_root: Path,
    engine_version: str = ENGINE_VERSION,
    rule_versions: dict[str, str] | None = None,
    record_label: str | None = None,
    original_record_reference: dict[str, object] | None = None,
) -> Path:
    active_rule_versions = rule_versions or RULE_VERSIONS
    dataset_meta = _read_json(dataset_dir / "metadata.json")
    if dataset_meta.get("confirmation_status") != "CONFIRMED" or dataset_meta.get("analysis_allowed") is not True:
        raise LedgerError("페이즈 3 확정 데이터가 아닙니다.")
    structure_meta = _artifact_meta(structure_dir, "BASIC_STRUCTURE")
    backtest_meta = _artifact_meta(backtest_dir, "SEQUENTIAL_RETURN_BACKTEST")
    candidate_meta = _artifact_meta(candidate_dir, "CANDIDATE_GATE_EVALUATION")
    selection_meta = _artifact_meta(selection_dir, "FINAL_SIX_SELECTION")
    sets_meta = _artifact_meta(sets_dir, "TWO_SET_PLACEMENT")
    target_rounds = {
        structure_meta["target_round"], backtest_meta["target_round"], candidate_meta["target_round"],
        selection_meta["target_round"], sets_meta["target_round"],
    }
    if len(target_rounds) != 1:
        raise LedgerError(f"단계별 분석 대상 회차가 충돌합니다: {sorted(target_rounds)}")
    target_round = int(next(iter(target_rounds)))
    if dataset_meta.get("end_round") != target_round - 1:
        raise LedgerError("확정 데이터 종료 회차와 분석 대상 회차가 맞지 않습니다.")

    # 마지막 단계의 해시 연결을 다시 확인한다.
    set_report_path = sets_dir / "set-report.json"
    if sets_meta.get("set_report_sha256") != sha256_file(set_report_path):
        raise LedgerError("세트 보고서가 배치 후 변경되었습니다.")

    selection_report = _read_json(selection_dir / "selection-report.json")
    set_report = _read_json(set_report_path)
    structure_report = _read_json(structure_dir / "structure-report.json")
    candidate_report = _read_json(candidate_dir / "candidate-report.json")
    previous_record = ledger_root / "records" / f"round-{target_round - 1}"
    first_execution = not previous_record.is_dir()

    final_dir = ledger_root / "records" / f"round-{target_round}"
    staging = ledger_root / "records" / f".round-{target_round}.staging"
    if final_dir.exists():
        raise FileExistsError(f"이미 잠긴 회차 기록이 있습니다: {final_dir}")
    if staging.exists():
        raise FileExistsError(f"미완료 잠금 기록이 있습니다: {staging}")
    staging.mkdir(parents=True)
    try:
        snapshot = staging / "snapshot"
        sources = {
            "phase3-data": dataset_dir,
            "phase4-structure": structure_dir,
            "phase5-backtest": backtest_dir,
            "phase6-candidates": candidate_dir,
            "phase7-selection": selection_dir,
            "phase8-sets": sets_dir,
        }
        for name, source in sources.items():
            shutil.copytree(source, snapshot / name)

        locked_report = {
            "title": "P45 분석 잠금 기록",
            "target_round": target_round,
            "engine_version": engine_version,
            "rule_versions": active_rule_versions,
            "record_label": record_label,
            "original_record_reference": original_record_reference,
            "data": {
                "range": [dataset_meta["start_round"], dataset_meta["end_round"]],
                "valid_draw_count": dataset_meta["valid_draw_count"],
                "source": dataset_meta["data_source"],
                "normalized_sha256": dataset_meta["normalized_sha256"],
                "confirmation_status": dataset_meta["confirmation_status"],
            },
            "previous_review": (
                "최초 실행 회차로 이전 추천 대조 데이터 없음."
                if first_execution else f"{target_round - 1}회 잠금 기록 존재"
            ),
            "first_execution": first_execution,
            "structure": structure_report["previous_draw_structure"],
            "candidate_result": {
                "official_pass_candidates": candidate_report["official_pass_candidates"],
                "valid_test_candidates": candidate_report["valid_test_candidates"],
                "official_status": candidate_report["official_candidate_result"],
            },
            "selection": selection_report,
            "sets": set_report,
            "record_class": (
                "LIVE_OFFICIAL" if selection_report["selection_mode"] == "OFFICIAL" else "LIVE_TEST"
            ),
            "locked": True,
            "warning": "정해진 연구 규칙에 따른 결과이며 당첨을 보장하지 않습니다.",
        }
        locked_report_path = staging / "locked-report.json"
        locked_report_path.write_text(
            json.dumps(locked_report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        manifest = {
            "target_round": target_round,
            "files": _manifest_entries(staging),
        }
        manifest_path = staging / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        metadata = {
            "engine_version": engine_version,
            "record_type": "IMMUTABLE_ANALYSIS_LOCK",
            "target_round": target_round,
            "lock_status": "LOCKED",
            "manifest_sha256": sha256_file(manifest_path),
            "locked_report_sha256": sha256_file(locked_report_path),
            "locked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        (staging / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        staging.rename(final_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    verify_locked_record(final_dir)
    return final_dir


def _validate_result(main: list[int], bonus: int) -> tuple[list[int], int]:
    normalized = sorted(main)
    if len(normalized) != 6 or len(set(normalized)) != 6:
        raise LedgerError("실제 본번호는 서로 다른 6개여야 합니다.")
    if any(not 1 <= number <= 45 for number in (*normalized, bonus)):
        raise LedgerError("실제 번호는 모두 1~45 범위여야 합니다.")
    if bonus in normalized:
        raise LedgerError("실제 보너스번호가 본번호와 중복됩니다.")
    return normalized, bonus


def _stage_lookup(selection: dict[str, object]) -> dict[int, dict[str, object]]:
    stages = selection["stages"]
    lookup = {number: {"stage": "final_selected", "reason_code": None} for number in stages["final_selected"]}
    for stage_name in ("alternate_eliminated", "middle_eliminated", "initial_eliminated"):
        for item in stages[stage_name]:
            lookup[item["number"]] = {"stage": stage_name, "reason_code": item["reason_code"]}
    return lookup


def review_result(
    ledger_root: Path,
    target_round: int,
    main: list[int],
    bonus: int,
) -> Path:
    main, bonus = _validate_result(main, bonus)
    record_dir = ledger_root / "records" / f"round-{target_round}"
    record_metadata = verify_locked_record(record_dir)
    locked_report_path = record_dir / "locked-report.json"
    if record_metadata.get("locked_report_sha256") != sha256_file(locked_report_path):
        raise LedgerError("잠금 보고서가 변경되었습니다.")
    locked = _read_json(locked_report_path)
    selection = locked["selection"]
    sets = locked["sets"]
    selected = selection["selected_numbers"]
    main_hits = sorted(set(selected) & set(main))
    bonus_hit = bonus in selected
    integrated_hits = sorted(set(selected) & set((*main, bonus)))
    stage_lookup = _stage_lookup(selection)
    actual_trace = [
        {"number": number, **stage_lookup.get(number, {"stage": "not_generated", "reason_code": None})}
        for number in (*main, bonus)
    ]
    set_results = {}
    for name, numbers in (("set_1", sets["set_1"]), ("set_2", sets["set_2"])):
        set_results[name] = {
            "numbers": numbers,
            "main_hits": sorted(set(numbers) & set(main)),
            "bonus_hit": bonus in numbers,
            "integrated_hit_count": len(set(numbers) & set((*main, bonus))),
        }
    exposure = len(selected)
    review = {
        "target_round": target_round,
        "locked_record_manifest_sha256": record_metadata["manifest_sha256"],
        "actual_main": main,
        "actual_bonus": bonus,
        "selected_numbers": selected,
        "main_hits": main_hits,
        "main_hit_count": len(main_hits),
        "bonus_hit": bonus_hit,
        "integrated_hits": integrated_hits,
        "integrated_hit_count": len(integrated_hits),
        "candidate_exposure": exposure,
        "integrated_rate": len(integrated_hits) / exposure if exposure else None,
        "main_rate": len(main_hits) / exposure if exposure else None,
        "random_expected_integrated_hits": exposure * 7 / 45,
        "random_expected_main_hits": exposure * 6 / 45,
        "set_results": set_results,
        "actual_number_stage_trace": actual_trace,
        "record_class": locked["record_class"],
        "original_record_modified": False,
    }
    result_key = hashlib.sha256(
        json.dumps({"main": main, "bonus": bonus}, sort_keys=True).encode()
    ).hexdigest()[:16]
    final_dir = ledger_root / "reviews" / f"round-{target_round}" / f"review-{result_key}"
    if final_dir.exists():
        raise FileExistsError(f"동일 실제 결과의 복기 기록이 이미 있습니다: {final_dir}")
    final_dir.mkdir(parents=True)
    try:
        review_path = final_dir / "review.json"
        review_path.write_text(
            json.dumps(review, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        metadata = {
            "record_type": "RESULT_REVIEW",
            "target_round": target_round,
            "review_sha256": sha256_file(review_path),
            "source_locked_manifest_sha256": record_metadata["manifest_sha256"],
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        (final_dir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except Exception:
        shutil.rmtree(final_dir, ignore_errors=True)
        raise
    # 복기 저장 뒤에도 원본 잠금 기록이 그대로인지 재확인한다.
    verify_locked_record(record_dir)
    return final_dir

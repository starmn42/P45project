from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .data import Draw, ENGINE_VERSION, REQUIRED_COLUMNS, load_and_validate_csv, sha256_file


NINE_GROUPS = ((1, 9), (10, 18), (19, 27), (28, 36), (37, 45))
FIVE_GROUPS = tuple((start, min(start + 4, 45)) for start in range(1, 46, 5))


class StructureAnalysisError(ValueError):
    pass


@dataclass(frozen=True)
class DrawStructure:
    round: int
    main: tuple[int, ...]
    bonus: int
    seven: tuple[int, ...]
    occupancy_9: tuple[int, int, int, int, int]
    annihilated_9: tuple[str, ...]
    absent_5: tuple[str, ...]
    absent_endings: tuple[int, ...]


def _label(group: tuple[int, int]) -> str:
    return f"{group[0]}~{group[1]}"


def _occupancy(numbers: tuple[int, ...], groups: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    return tuple(sum(start <= number <= end for number in numbers) for start, end in groups)


def build_draw_structure(draw: Draw) -> DrawStructure:
    seven = tuple(sorted((*draw.main, draw.bonus)))
    occupancy_9 = _occupancy(seven, NINE_GROUPS)
    occupancy_5 = _occupancy(seven, FIVE_GROUPS)
    endings = {number % 10 for number in seven}
    return DrawStructure(
        round=draw.round,
        main=tuple(sorted(draw.main)),
        bonus=draw.bonus,
        seven=seven,
        occupancy_9=occupancy_9,
        annihilated_9=tuple(_label(group) for group, count in zip(NINE_GROUPS, occupancy_9) if count == 0),
        absent_5=tuple(_label(group) for group, count in zip(FIVE_GROUPS, occupancy_5) if count == 0),
        absent_endings=tuple(ending for ending in range(10) if ending not in endings),
    )


def _number_counts(draws: list[Draw]) -> dict[str, dict[str, int]]:
    main: Counter[int] = Counter()
    bonus: Counter[int] = Counter()
    integrated: Counter[int] = Counter()
    for draw in draws:
        main.update(draw.main)
        bonus.update([draw.bonus])
        integrated.update((*draw.main, draw.bonus))
    return {
        "main": {str(number): main[number] for number in range(1, 46)},
        "bonus": {str(number): bonus[number] for number in range(1, 46)},
        "integrated": {str(number): integrated[number] for number in range(1, 46)},
    }


def summarize_period(draws: list[Draw]) -> dict[str, object]:
    structures = [build_draw_structure(draw) for draw in draws]
    vector_counts = Counter(",".join(map(str, item.occupancy_9)) for item in structures)
    annihilation_counts = {
        _label(group): sum(item.occupancy_9[index] == 0 for item in structures)
        for index, group in enumerate(NINE_GROUPS)
    }
    return {
        "start_round": draws[0].round if draws else None,
        "end_round": draws[-1].round if draws else None,
        "draw_count": len(draws),
        "candidate_exposure": {
            "main": len(draws) * 6,
            "bonus": len(draws),
            "integrated": len(draws) * 7,
        },
        "number_occurrences": _number_counts(draws),
        "occupancy_vector_counts": dict(sorted(vector_counts.items())),
        "annihilation_9_counts": annihilation_counts,
    }


def split_periods(draws: list[Draw]) -> dict[str, list[Draw]]:
    midpoint = len(draws) // 2
    return {
        "overall": draws,
        "first_half": draws[:midpoint],
        "second_half": draws[midpoint:],
        "recent_100": draws[-100:],
        "recent_50": draws[-50:],
        "recent_20": draws[-20:],
    }


def _validate_confirmed_dataset(dataset_dir: Path) -> tuple[dict[str, object], Path]:
    metadata_path = dataset_dir / "metadata.json"
    normalized_path = dataset_dir / "normalized.csv"
    if not metadata_path.is_file() or not normalized_path.is_file():
        raise StructureAnalysisError("확정 데이터 묶음의 필수 파일이 없습니다.")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StructureAnalysisError(f"확정 데이터 메타데이터를 읽을 수 없습니다: {exc}") from exc
    if metadata.get("confirmation_status") != "CONFIRMED" or metadata.get("analysis_allowed") is not True:
        raise StructureAnalysisError("페이즈 3에서 확정된 데이터만 분석할 수 있습니다.")
    actual_hash = sha256_file(normalized_path)
    if metadata.get("normalized_sha256") != actual_hash:
        raise StructureAnalysisError("확정 후 정규화 데이터가 변경되어 분석을 중단합니다.")
    return metadata, normalized_path


def _write_effective_csv(draws: list[Draw], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(REQUIRED_COLUMNS)
        for draw in draws:
            writer.writerow([
                draw.round,
                draw.draw_date.isoformat() if draw.draw_date else "",
                *sorted(draw.main),
                draw.bonus,
            ])


def analyze_structure(
    dataset_dir: Path,
    output_root: Path,
    *,
    target_round: int | None = None,
) -> Path:
    metadata, normalized_path = _validate_confirmed_dataset(dataset_dir)
    draws = load_and_validate_csv(normalized_path)
    if target_round is None:
        target_round = draws[-1].round + 1
    if target_round < 2 or target_round > draws[-1].round + 1:
        raise StructureAnalysisError(
            f"분석 대상 회차는 2~{draws[-1].round + 1} 범위여야 합니다: {target_round}"
        )
    effective = [draw for draw in draws if draw.round < target_round]
    if not effective or effective[-1].round != target_round - 1:
        raise StructureAnalysisError("분석 대상 직전 회차 데이터가 없습니다.")

    result_id = f"structure-{target_round}"
    final_dir = output_root / result_id
    staging = output_root / f".{result_id}.staging"
    if final_dir.exists():
        raise FileExistsError(f"이미 생성된 구조 분석이 있습니다: {final_dir}")
    if staging.exists():
        raise FileExistsError(f"미완료 구조 분석이 있습니다: {staging}")
    staging.mkdir(parents=True)
    try:
        effective_path = staging / "analysis-input.csv"
        _write_effective_csv(effective, effective_path)
        structures = [build_draw_structure(draw) for draw in effective]
        with (staging / "draw-structures.jsonl").open("w", encoding="utf-8", newline="") as stream:
            for item in structures:
                stream.write(json.dumps({
                    "round": item.round,
                    "main": list(item.main),
                    "bonus": item.bonus,
                    "seven": list(item.seven),
                    "occupancy_9": list(item.occupancy_9),
                    "annihilated_9": list(item.annihilated_9),
                    "absent_5": list(item.absent_5),
                    "absent_endings": list(item.absent_endings),
                }, ensure_ascii=False, sort_keys=True) + "\n")

        current = structures[-1]
        report = {
            "target_round": target_round,
            "data_range": {"start": effective[0].round, "end": effective[-1].round, "count": len(effective)},
            "previous_draw_structure": {
                "round": current.round,
                "main": list(current.main),
                "bonus": current.bonus,
                "seven": list(current.seven),
                "occupancy_9": list(current.occupancy_9),
                "annihilated_9": list(current.annihilated_9),
                "absent_5": list(current.absent_5),
                "absent_endings": list(current.absent_endings),
            },
            "periods": {
                name: summarize_period(period_draws)
                for name, period_draws in split_periods(effective).items()
            },
            "recent_20_usage": "OBSERVATION_ONLY",
            "candidate_selection_performed": False,
        }
        report_path = staging / "structure-report.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        output_metadata = {
            "engine_version": ENGINE_VERSION,
            "analysis_type": "BASIC_STRUCTURE",
            "analysis_status": "COMPLETE",
            "target_round": target_round,
            "future_data_blocked_after_round": target_round - 1,
            "source_dataset": str(dataset_dir.resolve()),
            "source_normalized_sha256": metadata["normalized_sha256"],
            "effective_data_sha256": sha256_file(effective_path),
            "structure_report_sha256": sha256_file(report_path),
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        (staging / "metadata.json").write_text(
            json.dumps(output_metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        staging.rename(final_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return final_dir

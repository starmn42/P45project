from __future__ import annotations

import csv
import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


ENGINE_VERSION = "P45 Research Engine v2.3 Integrated Compact"
REQUIRED_COLUMNS = ("round", "date", "n1", "n2", "n3", "n4", "n5", "n6", "bonus")


@dataclass(frozen=True)
class Draw:
    round: int
    draw_date: date | None
    main: tuple[int, int, int, int, int, int]
    bonus: int


class DataValidationError(ValueError):
    def __init__(self, errors: Iterable[str]):
        self.errors = tuple(errors)
        super().__init__("\n".join(self.errors))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_int(value: str, label: str, row_number: int, errors: list[str]) -> int | None:
    try:
        return int(value.strip())
    except (AttributeError, ValueError):
        errors.append(f"행 {row_number}: {label}이(가) 정수가 아닙니다: {value!r}")
        return None


def load_and_validate_csv(path: Path) -> list[Draw]:
    errors: list[str] = []
    draws: list[Draw] = []

    try:
        stream = path.open("r", encoding="utf-8-sig", newline="")
    except (OSError, UnicodeError) as exc:
        raise DataValidationError([f"원본 파일을 읽을 수 없습니다: {exc}"]) from exc

    with stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise DataValidationError(["CSV 헤더가 없습니다."])
        actual = tuple(name.strip() for name in reader.fieldnames)
        if actual != REQUIRED_COLUMNS:
            raise DataValidationError([
                "CSV 열 순서가 올바르지 않습니다.",
                f"필요: {','.join(REQUIRED_COLUMNS)}",
                f"입력: {','.join(actual)}",
            ])

        seen_rounds: set[int] = set()
        for row_number, row in enumerate(reader, start=2):
            round_no = _parse_int(row["round"], "round", row_number, errors)
            main_values = [_parse_int(row[f"n{i}"], f"n{i}", row_number, errors) for i in range(1, 7)]
            bonus = _parse_int(row["bonus"], "bonus", row_number, errors)
            raw_date = row["date"].strip()
            draw_date: date | None = None
            if raw_date:
                try:
                    draw_date = date.fromisoformat(raw_date)
                except ValueError:
                    errors.append(f"행 {row_number}: date는 YYYY-MM-DD 형식이어야 합니다: {raw_date!r}")

            if round_no is None or bonus is None or any(value is None for value in main_values):
                continue
            main = tuple(main_values)
            if round_no < 1:
                errors.append(f"행 {row_number}: 회차는 1 이상이어야 합니다.")
            if round_no in seen_rounds:
                errors.append(f"행 {row_number}: {round_no}회가 중복되었습니다.")
            seen_rounds.add(round_no)
            invalid = [number for number in (*main, bonus) if not 1 <= number <= 45]
            if invalid:
                errors.append(f"행 {row_number}: 1~45 범위를 벗어난 번호: {invalid}")
            if len(set(main)) != 6:
                errors.append(f"행 {row_number}: 본번호 내부에 중복이 있습니다: {list(main)}")
            if bonus in main:
                errors.append(f"행 {row_number}: 보너스번호 {bonus}가 본번호와 중복됩니다.")
            draws.append(Draw(round_no, draw_date, main, bonus))

    if not draws and not errors:
        errors.append("데이터 행이 없습니다.")

    rounds = [draw.round for draw in draws]
    if rounds != sorted(rounds):
        errors.append("회차가 오름차순으로 정렬되어 있지 않습니다.")
    if rounds:
        expected = list(range(1, rounds[-1] + 1))
        missing = sorted(set(expected) - set(rounds))
        if missing:
            errors.append(f"누락 회차가 있습니다: {missing}")

    dated = [draw for draw in draws if draw.draw_date is not None]
    for previous, current in zip(dated, dated[1:]):
        if current.draw_date <= previous.draw_date:
            errors.append(
                f"날짜 순서 오류: {previous.round}회 {previous.draw_date} / "
                f"{current.round}회 {current.draw_date}"
            )

    if errors:
        raise DataValidationError(errors)
    return draws


def write_normalized(draws: Iterable[Draw], destination: Path) -> None:
    with destination.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(REQUIRED_COLUMNS)
        for draw in draws:
            writer.writerow([
                draw.round,
                draw.draw_date.isoformat() if draw.draw_date else "",
                *sorted(draw.main),
                draw.bonus,
            ])


def prepare_dataset(input_path: Path, output_root: Path, source: str) -> Path:
    draws = load_and_validate_csv(input_path)
    dataset_id = f"rounds-1-{draws[-1].round}"
    final_dir = output_root / dataset_id
    if final_dir.exists():
        raise FileExistsError(f"이미 확정된 분석 묶음이 있습니다: {final_dir}")

    staging = output_root / f".{dataset_id}.staging"
    if staging.exists():
        raise FileExistsError(f"미완료 임시 묶음이 있습니다: {staging}")
    staging.mkdir(parents=True)
    try:
        raw_path = staging / "raw.csv"
        normalized_path = staging / "normalized.csv"
        shutil.copyfile(input_path, raw_path)
        write_normalized(draws, normalized_path)
        metadata = {
            "engine_version": ENGINE_VERSION,
            "data_source": source,
            "confirmation_status": "CONFIRMED",
            "start_round": draws[0].round,
            "end_round": draws[-1].round,
            "valid_draw_count": len(draws),
            "raw_sha256": sha256_file(raw_path),
            "normalized_sha256": sha256_file(normalized_path),
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        (staging / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        staging.rename(final_dir)
    except Exception:
        for child in staging.iterdir():
            child.unlink()
        staging.rmdir()
        raise
    return final_dir

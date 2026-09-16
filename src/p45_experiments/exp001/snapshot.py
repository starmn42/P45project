from __future__ import annotations

import csv
import hashlib
import io
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[3]
BASE_CSV = ROOT / "analysis/structure-1236/analysis-input.csv"
LIVE_DB = ROOT / "v27_storage/live/p45_new_draw_update_v1.sqlite3"
SNAPSHOT_DIR = ROOT / "v27_storage/experiments/exp001/data"


@dataclass(frozen=True)
class DrawRow:
    round: int
    date: str
    main: tuple[int, ...]
    bonus: int

    def csv_row(self) -> list[object]:
        return [self.round, self.date, *self.main, self.bonus]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _validate(row: DrawRow) -> None:
    if len(row.main) != 6 or len(set(row.main)) != 6:
        raise ValueError(f"DRAW_MAIN_INVALID:{row.round}")
    if any(number < 1 or number > 45 for number in (*row.main, row.bonus)):
        raise ValueError(f"DRAW_NUMBER_RANGE:{row.round}")
    if row.bonus in row.main:
        raise ValueError(f"DRAW_BONUS_DUPLICATE:{row.round}")


def load_source_rows(end_round: int = 1237) -> list[DrawRow]:
    rows: dict[int, DrawRow] = {}
    with BASE_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        for raw in csv.DictReader(handle):
            draw = DrawRow(int(raw["round"]), raw["date"], tuple(int(raw[f"n{i}"]) for i in range(1, 7)), int(raw["bonus"]))
            if draw.round <= end_round:
                _validate(draw)
                if draw.round in rows:
                    raise ValueError(f"DRAW_DUPLICATE:{draw.round}")
                rows[draw.round] = draw
    connection = sqlite3.connect(f"file:{LIVE_DB.resolve().as_posix()}?mode=ro", uri=True)
    try:
        for round_no, date, main_json, bonus in connection.execute(
            "SELECT draw_round,draw_date,main_json,bonus FROM draw_result WHERE draw_round<=? ORDER BY draw_round",
            (end_round,),
        ):
            draw = DrawRow(int(round_no), str(date), tuple(int(x) for x in json.loads(main_json)), int(bonus))
            _validate(draw)
            if draw.round in rows:
                raise ValueError(f"DRAW_DUPLICATE:{draw.round}")
            rows[draw.round] = draw
    finally:
        connection.close()
    ordered = [rows[key] for key in sorted(rows)]
    expected = list(range(1, end_round + 1))
    actual = [row.round for row in ordered]
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        raise ValueError(f"DRAW_RANGE_NOT_CONTIGUOUS:{missing[:10]}")
    return ordered


def canonical_csv_bytes(rows: Iterable[DrawRow]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["round", "date", "n1", "n2", "n3", "n4", "n5", "n6", "bonus"])
    for row in rows:
        writer.writerow(row.csv_row())
    return output.getvalue().encode("utf-8")


def create_locked_snapshot(end_round: int = 1237) -> dict[str, object]:
    rows = load_source_rows(end_round)
    payload = canonical_csv_bytes(rows)
    digest = hashlib.sha256(payload).hexdigest()
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot = SNAPSHOT_DIR / f"exp001_draws_1_{end_round}.csv"
    manifest_path = SNAPSHOT_DIR / "exp001_data_snapshot_manifest.json"
    snapshot.write_bytes(payload)
    manifest = {
        "experiment_id": "EXP-DRAW-20260816-002-V1",
        "snapshot_version": "EXP001-DATA-SNAPSHOT-1.0",
        "start_round": 1,
        "end_round": end_round,
        "row_count": len(rows),
        "main_width": 6,
        "integrated_width": 7,
        "duplicate_rounds": 0,
        "missing_rounds": 0,
        "sorted": True,
        "snapshot_path": snapshot.relative_to(ROOT).as_posix(),
        "snapshot_sha256": digest,
        "source_files": [
            {"path": BASE_CSV.relative_to(ROOT).as_posix(), "sha256": file_sha256(BASE_CSV), "mode": "READ_ONLY"},
            {"path": LIVE_DB.relative_to(ROOT).as_posix(), "sha256": file_sha256(LIVE_DB), "mode": "READ_ONLY"},
        ],
        "future_data_policy": "END_ROUND_LOCKED_NO_EXTENSION_AFTER_RESULTS",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return manifest


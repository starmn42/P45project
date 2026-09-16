from __future__ import annotations

import csv
import hashlib
import json
import os
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = Path(__file__).resolve().parent
LIVE_CSV = ROOT / "v27_storage/live/p45_live_draws.csv"
LIVE_DB = ROOT / "v27_storage/live/p45_new_draw_update_v1.sqlite3"
BACKUP = ROOT / "v27_storage/backups/draw_source_truth_normalization_1239_001"
OFFICIAL_CSV = ROOT / "downloads/official-1-1237/official.csv"
RAW_DIR = ROOT / "downloads/official-1-1237/raw"
STAGING_1238 = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
RAW_1239 = AUDIT / "ROUND_1239_OFFICIAL_RAW.json"
SOURCE_URL = "https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do?srchDir=center&srchLtEpsd={round}"
EXPECTED_STAGING_SHA = "1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"
EXPECTED_1238_PAYLOAD_SHA = "99d44e493a357785f976e37d99b1e0d2ae179b161cc1aa4a5665f9606ec0c119"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def canonical(row: dict[str, str]) -> tuple[int, str, tuple[int, ...], int]:
    return (
        int(row["round"]),
        row["date"],
        tuple(int(row[f"n{i}"]) for i in range(1, 7)),
        int(row["bonus"]),
    )


def validate(rows: list[dict[str, str]], end: int) -> None:
    values = [canonical(row) for row in rows]
    rounds = [value[0] for value in values]
    if rounds != list(range(1, end + 1)):
        raise RuntimeError("STOP_CANONICAL_1_1239_INTEGRITY_FAILED:ROUND_SEQUENCE")
    for draw_round, _, main, bonus in values:
        if len(main) != 6 or len(set(main)) != 6:
            raise RuntimeError(f"STOP_CANONICAL_1_1239_INTEGRITY_FAILED:MAIN:{draw_round}")
        if any(number < 1 or number > 45 for number in (*main, bonus)) or bonus in main:
            raise RuntimeError(f"STOP_CANONICAL_1_1239_INTEGRITY_FAILED:RANGE:{draw_round}")


def raw_provenance() -> dict[int, tuple[str, str]]:
    result: dict[int, tuple[str, str]] = {}
    for path in sorted(RAW_DIR.glob("api-*.json")):
        payload = path.read_bytes()
        payload_sha = hashlib.sha256(payload).hexdigest()
        for row in json.loads(payload.decode("utf-8"))["data"]["list"]:
            result[int(row["ltEpsd"])] = (str(path.relative_to(ROOT)), payload_sha)
    return result


def main() -> None:
    if sha(STAGING_1238) != EXPECTED_STAGING_SHA:
        raise RuntimeError("STOP_1238_PROVENANCE_MISMATCH:STAGING_SHA")
    official = read_rows(OFFICIAL_CSV)
    staging = read_rows(STAGING_1238)
    live_before = read_rows(BACKUP / "p45_live_draws.before.csv")
    if [canonical(x) for x in official] != [canonical(x) for x in live_before]:
        raise RuntimeError("STOP_CANONICAL_1_1239_INTEGRITY_FAILED:BASELINE_OFFICIAL_LIVE")
    if [canonical(x) for x in staging[:1237]] != [canonical(x) for x in live_before]:
        raise RuntimeError("STOP_CANONICAL_1_1239_INTEGRITY_FAILED:BASELINE_STAGING")
    expected_1238 = (1238, "2026-08-22", (2, 13, 18, 32, 38, 42), 22)
    if canonical(staging[-1]) != expected_1238:
        raise RuntimeError("STOP_1238_PROVENANCE_MISMATCH:ROW")

    payload_1239 = RAW_1239.read_bytes()
    payload_1239_sha = hashlib.sha256(payload_1239).hexdigest()
    rows_1239 = json.loads(payload_1239.decode("utf-8"))["data"]["list"]
    raw_row = next((row for row in rows_1239 if int(row.get("ltEpsd", -1)) == 1239), None)
    if raw_row is None:
        raise RuntimeError("STOP_1239_AUTHORITATIVE_ACQUISITION_FAILED")
    ymd = str(raw_row["ltRflYmd"])
    row_1239 = {
        "round": "1239",
        "date": f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}",
        **{f"n{i}": str(int(raw_row[f"tm{i}WnNo"])) for i in range(1, 7)},
        "bonus": str(int(raw_row["bnsWnNo"])),
    }
    candidate = [*staging, row_1239]
    validate(candidate, 1239)

    candidate_path = AUDIT / "CANONICAL_DRAW_1_1239.csv"
    with candidate_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["round", "date", "n1", "n2", "n3", "n4", "n5", "n6", "bonus"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(candidate)

    provenance = raw_provenance()
    if set(provenance) != set(range(1, 1238)):
        raise RuntimeError("STOP_CANONICAL_1_1239_INTEGRITY_FAILED:RAW_PROVENANCE_1_1237")
    fetched_at = datetime.now().astimezone().isoformat(timespec="seconds")
    db = sqlite3.connect(LIVE_DB)
    try:
        db.execute("BEGIN IMMEDIATE")
        for row in candidate[:1235]:
            draw_round, draw_date, main_numbers, bonus = canonical(row)
            _, payload_sha = provenance[draw_round]
            db.execute(
                "INSERT INTO draw_result(draw_round,draw_date,main_json,bonus,source_url,source_payload_sha256,fetched_at) VALUES(?,?,?,?,?,?,?)",
                (draw_round, draw_date, json.dumps(main_numbers, separators=(",", ":")), bonus, SOURCE_URL.format(round=draw_round), payload_sha, fetched_at),
            )
        draw_round, draw_date, main_numbers, bonus = canonical(row_1239)
        db.execute(
            "INSERT INTO draw_result(draw_round,draw_date,main_json,bonus,source_url,source_payload_sha256,fetched_at) VALUES(?,?,?,?,?,?,?)",
            (draw_round, draw_date, json.dumps(main_numbers, separators=(",", ":")), bonus, SOURCE_URL.format(round=1239), payload_1239_sha, fetched_at),
        )
        db.execute("INSERT OR REPLACE INTO provenance(key,value) VALUES(?,?)", ("canonical_draw_store", str(LIVE_CSV)))
        db.execute("INSERT OR REPLACE INTO provenance(key,value) VALUES(?,?)", ("canonical_draw_range", "1..1239"))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    with tempfile.NamedTemporaryFile("wb", delete=False, dir=LIVE_CSV.parent, prefix="canonical-", suffix=".csv") as handle:
        handle.write(candidate_path.read_bytes())
        temporary = Path(handle.name)
    os.replace(temporary, LIVE_CSV)

    db = sqlite3.connect(f"file:{LIVE_DB.resolve()}?mode=ro", uri=True)
    db_rows = db.execute("SELECT draw_round,draw_date,main_json,bonus FROM draw_result ORDER BY draw_round").fetchall()
    db.close()
    db_values = [(int(r), d, tuple(json.loads(m)), int(b)) for r, d, m, b in db_rows]
    csv_values = [canonical(row) for row in read_rows(LIVE_CSV)]
    if db_values != csv_values:
        raise RuntimeError("STOP_CANONICAL_1_1239_INTEGRITY_FAILED:CSV_SQLITE_MISMATCH")

    canonical_row_1239_sha = hashlib.sha256(json.dumps({
        "round": 1239,
        "date": row_1239["date"],
        "main": list(canonical(row_1239)[2]),
        "bonus": canonical(row_1239)[3],
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    report = {
        "status": "DRAW_SOURCE_OF_TRUTH_NORMALIZED",
        "rows": len(csv_values),
        "min_round": csv_values[0][0],
        "max_round": csv_values[-1][0],
        "missing_rounds": 0,
        "duplicate_rounds": 0,
        "csv_sqlite_equal": True,
        "baseline_1_1237_exact": True,
        "round_1238": {"value": expected_1238, "approved_source_payload_sha256": EXPECTED_1238_PAYLOAD_SHA, "provenance": "PASS"},
        "round_1239": {"value": canonical(row_1239), "source_payload_sha256": payload_1239_sha, "canonical_row_sha256": canonical_row_1239_sha, "provenance": "PASS"},
        "canonical_csv": str(candidate_path),
        "canonical_csv_sha256": sha(candidate_path),
        "live_csv_sha256": sha(LIVE_CSV),
        "live_db_sha256": sha(LIVE_DB),
    }
    (AUDIT / "DRAW_SOURCE_TRUTH_NORMALIZATION_RESULT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

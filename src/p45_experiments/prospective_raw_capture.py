"""Append-only official raw capture for the locked prize-share prospective study."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sqlite3
import subprocess
import tempfile
import urllib.request
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "v27_storage" / "experiments" / "prize_share_prospective_001_v1"
LEDGER = STORE / "PRIZE_SHARE_PROSPECTIVE_001_LEDGER.jsonl"
CORRECTIONS = STORE / "PRIZE_SHARE_PROSPECTIVE_001_CORRECTIONS.jsonl"
RUN_LOG = STORE / "collector_runs.jsonl"
LOCK = STORE / ".collector.lock"
LIVE_DB = ROOT / "v27_storage" / "live" / "p45_new_draw_update_v1.sqlite3"
FIXTURE = ROOT / "downloads" / "official-1-1237" / "raw" / "api-0001.json"
URL = "https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do?srchDir=center&srchLtEpsd={round}"
START_ROUND = 1238
VERSION = "P45-PROSPECTIVE-RAW-CAPTURE-1.0"
SOURCE_SCHEMA = "DHLOTTERY-LT645-RAW-1.0"


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: bytes | Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def append_jsonl(path: Path, values: Iterable[dict[str, Any]]) -> None:
    payload = "".join(canonical(item) + "\n" for item in values).encode("utf-8")
    if not payload:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def source_row(payload: bytes, expected_round: int, retrieved_at: str) -> dict[str, Any]:
    doc = json.loads(payload.decode("utf-8"))
    item = next((x for x in doc.get("data", {}).get("list", []) if int(x.get("ltEpsd", -1)) == expected_round), None)
    if item is None:
        raise LookupError("SOURCE_UNAVAILABLE")
    main = [int(item[f"tm{i}WnNo"]) for i in range(1, 7)]
    bonus = int(item["bnsWnNo"])
    k1 = int(item["rnk1WnNope"])
    k2 = int(item["rnk2WnNope"])
    sales = int(item["wholEpsdSumNtslAmt"])
    if len(set(main)) != 6 or any(not 1 <= n <= 45 for n in main):
        raise ValueError("SOURCE_MAIN_INVALID")
    if not 1 <= bonus <= 45 or bonus in main:
        raise ValueError("SOURCE_BONUS_INVALID")
    if k1 < 0 or k2 < 0 or sales <= 0:
        raise ValueError("SOURCE_COUNT_OR_SALES_INVALID")
    selected = {
        "round": expected_round,
        "main_numbers": main,
        "bonus": bonus,
        "first_prize_games": k1,
        "second_prize_games": k2,
        "total_sales_amount_krw": sales,
        "source_endpoint": URL.format(round=expected_round),
        "source_schema_version": SOURCE_SCHEMA,
        "source_payload_sha256": digest(payload),
    }
    return {
        "record_id": f"OBS-{expected_round}-{digest(selected)[:16]}",
        "record_type": "OBSERVATION",
        "corrects_record_id": None,
        **selected,
        "retrieved_at": retrieved_at,
        "source_record_sha256": digest(selected),
        "collector_version": VERSION,
    }


def fetch(round_number: int, timeout: float = 20.0) -> bytes:
    request = urllib.request.Request(URL.format(round=round_number), headers={"User-Agent": VERSION})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def other_python_process() -> bool:
    if os.name != "nt":
        return False
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        for row in csv.reader(result.stdout.splitlines()):
            if len(row) >= 2 and row[1].isdigit() and int(row[1]) != os.getpid():
                return True
    except (OSError, subprocess.SubprocessError):
        return True
    return False


def live_update_running() -> bool:
    if other_python_process():
        return True
    lock_candidates = tuple((ROOT / "v27_storage" / "live").glob("*.lock"))
    return any(path.exists() for path in lock_candidates)


@contextmanager
def exclusive_lock():
    STORE.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError("COLLECTOR_ALREADY_RUNNING") from exc
    try:
        os.write(fd, f"{os.getpid()}|{now()}".encode("ascii"))
        os.close(fd)
        yield
    finally:
        LOCK.unlink(missing_ok=True)


def static_guard() -> dict[str, Any]:
    source = Path(__file__).read_text(encoding="utf-8").lower()
    forbidden = (
        "sc" + "ipy", "stats" + "models", "prize_share_" + "exp001", "prize_share_" + "exp002",
        "fit_" + "beta", "permutation" + "_p", "p_" + "value", "birthday" + "_count",
        "x" + "2_r", "z" + "2_r",
    )
    hits = [token for token in forbidden if token in source]
    if hits:
        raise RuntimeError("SIGNAL_BLIND_STATIC_GUARD_FAILED:" + ",".join(hits))
    return {"status": "PASS", "signal_calculation_code_paths": 0, "forbidden_hits": 0}


def dry_run_1237() -> dict[str, Any]:
    static_guard()
    payload = FIXTURE.read_bytes()
    row = source_row(payload, 1237, "DRY_RUN_FIXTURE")
    expected = {
        "main_numbers": [10, 20, 23, 34, 37, 40], "bonus": 36,
        "first_prize_games": 23, "second_prize_games": 75,
        "total_sales_amount_krw": 118363161000,
    }
    mismatches = {key: {"expected": value, "actual": row[key]} for key, value in expected.items() if row[key] != value}
    serialized = canonical(row)
    result = {
        "status": "PASS" if not mismatches else "FAIL", "fixture_round": 1237,
        "fixture_file": FIXTURE.relative_to(ROOT).as_posix(), "fixture_file_sha256": digest(payload),
        "serialized_row_sha256": digest(serialized.encode("utf-8")), "mismatches": mismatches,
        "prospective_ledger_write": 0, "signal_calculation_code_paths": 0,
    }
    target = STORE / "dry_run_1237_evidence.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if mismatches:
        raise RuntimeError("DRY_RUN_1237_MISMATCH")
    return result


def capture() -> dict[str, Any]:
    static_guard()
    if live_update_running():
        result = {"status": "DEFERRED_DUE_TO_P45_UPDATE", "written": 0, "timestamp": now()}
        append_jsonl(RUN_LOG, [result])
        return result
    with exclusive_lock():
        existing = read_jsonl(LEDGER)
        by_round = {int(row["round"]): row for row in existing if row.get("record_type") == "OBSERVATION"}
        if by_round:
            verify_round = max(by_round)
            verify_time = now()
            try:
                verify_payload = fetch(verify_round)
                verified = source_row(verify_payload, verify_round, verify_time)
            except (LookupError, OSError, TimeoutError):
                result = {"status": "SOURCE_UNAVAILABLE", "written": 0, "timestamp": verify_time}
                append_jsonl(RUN_LOG, [result])
                return result
            old = by_round[verify_round]
            if old["source_record_sha256"] != verified["source_record_sha256"]:
                conflict = {
                    "status": "DATA_INTEGRITY_CONFLICT", "round": verify_round,
                    "original_record_id": old["record_id"], "original_hash": old["source_record_sha256"],
                    "corrected_official_hash": verified["source_record_sha256"], "retrieved_at": verify_time,
                    "reason": "OFFICIAL_RAW_VALUE_CHANGED", "signal_analysis_allowed": False,
                }
                append_jsonl(CORRECTIONS, [conflict])
                append_jsonl(RUN_LOG, [conflict])
                return {**conflict, "written": 0}
        next_round = START_ROUND if not by_round else max(by_round) + 1
        new_rows: list[dict[str, Any]] = []
        while True:
            retrieved_at = now()
            try:
                payload = fetch(next_round)
                row = source_row(payload, next_round, retrieved_at)
            except (LookupError, OSError, TimeoutError):
                break
            if next_round in by_round:
                old = by_round[next_round]
                if old["source_record_sha256"] == row["source_record_sha256"]:
                    next_round += 1
                    continue
                conflict = {
                    "status": "DATA_INTEGRITY_CONFLICT", "round": next_round,
                    "original_record_id": old["record_id"], "original_hash": old["source_record_sha256"],
                    "corrected_official_hash": row["source_record_sha256"], "retrieved_at": retrieved_at,
                    "reason": "OFFICIAL_RAW_VALUE_CHANGED", "signal_analysis_allowed": False,
                }
                append_jsonl(CORRECTIONS, [conflict])
                append_jsonl(RUN_LOG, [conflict])
                return {**conflict, "written": 0}
            new_rows.append(row)
            next_round += 1
        if new_rows:
            batch_base = [{key: value for key, value in row.items() if key != "append_batch_sha256"} for row in new_rows]
            batch_hash = digest(batch_base)
            for row in new_rows:
                row["append_batch_sha256"] = batch_hash
            append_jsonl(LEDGER, new_rows)
        result = {
            "status": "CAPTURED" if new_rows else "SOURCE_UNAVAILABLE_OR_ALREADY_CURRENT",
            "written": len(new_rows), "ledger_rows": len(existing) + len(new_rows),
            "latest_captured_round": max([int(x["round"]) for x in [*existing, *new_rows]], default=None),
            "timestamp": now(), "signal_calculation_code_paths": 0,
        }
        append_jsonl(RUN_LOG, [result])
        return result


def status() -> dict[str, Any]:
    rows = read_jsonl(LEDGER)
    corrections = read_jsonl(CORRECTIONS)
    return {
        "status": "READY", "ledger_path": str(LEDGER), "ledger_rows": len(rows),
        "latest_captured_round": max((int(x["round"]) for x in rows), default=None),
        "correction_records": len(corrections), "static_guard": static_guard(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("dry-run-1237", "capture", "status"))
    args = parser.parse_args(argv)
    operation = {"dry-run-1237": dry_run_1237, "capture": capture, "status": status}[args.command]
    print(json.dumps(operation(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

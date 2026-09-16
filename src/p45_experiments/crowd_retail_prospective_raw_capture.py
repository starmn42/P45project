"""Signal-blind, append-only official raw capture for CROWD RETAIL PROSPECTIVE-001."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.parse
import urllib.request
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "v27_storage/experiments/crowd_retail_prospective_001_v1"
LEDGER = STORE / "CROWD_RETAIL_PROSPECTIVE_001_RAW_LEDGER.jsonl"
CORRECTIONS = STORE / "CROWD_RETAIL_PROSPECTIVE_001_CORRECTIONS.jsonl"
RUNS = STORE / "collector_runs.jsonl"
RAW = STORE / "official_raw"
LOCK = STORE / ".collector.lock"
PRIZE_LOCK = ROOT / "v27_storage/experiments/prize_share_prospective_001_v1/.collector.lock"
LIVE_LOCKS = ROOT / "v27_storage/live"
ENDPOINT = "https://www.dhlottery.co.kr/wnprchsplcsrch/selectLtWnShp.do"
PAGE = "https://www.dhlottery.co.kr/wnprchsplcsrch/home"
START_ROUND = 1239
VERSION = "P45-CROWD-RETAIL-PROSPECTIVE-RAW-1.0"
SCHEMA = "DHLOTTERY-WINNER-STORE-ROW-1.0"
ALLOWED_MODES = {"자동", "수동", "반자동"}


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: bytes | Any) -> str:
    raw = value if isinstance(value, bytes) else canonical(value).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def append_lines(path: Path, records: Iterable[dict[str, Any]]) -> None:
    data = "".join(canonical(record) + "\n" for record in records).encode("utf-8")
    if not data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())


def read_lines(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def fetch(round_number: int, timeout: float = 30.0) -> bytes:
    query = urllib.parse.urlencode({"srchWnShpRnk": "1", "srchLtEpsd": round_number, "srchShpLctn": ""})
    request = urllib.request.Request(ENDPOINT + "?" + query,
        headers={"User-Agent": VERSION, "Referer": PAGE})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def parse(payload: bytes, round_number: int, retrieved_at: str) -> dict[str, Any]:
    document = json.loads(payload.decode("utf-8"))
    data = document.get("data", {})
    rows = data.get("list")
    if not isinstance(rows, list):
        raise ValueError("SOURCE_LIST_MISSING")
    total = int(data.get("total", -1))
    if total == 0 and not rows:
        raise LookupError("ROUND_NOT_PUBLISHED")
    if total != len(rows):
        raise ValueError("OFFICIAL_TOTAL_ROW_MISMATCH")
    normalized = []
    seen_row_numbers = set()
    for item in rows:
        row_number = int(item["rnum"])
        if row_number in seen_row_numbers:
            raise ValueError("DUPLICATE_OFFICIAL_ROW_NUMBER")
        seen_row_numbers.add(row_number)
        mode = str(item.get("atmtPsvYnTxt") or "").strip()
        if mode not in ALLOWED_MODES:
            raise ValueError("MODE_SEMANTICS_UNKNOWN")
        store_id = str(item.get("ltShpId") or "").strip()
        name = str(item.get("shpNm") or "").strip()
        address = " ".join(str(item.get("shpAddr") or "").split())
        if not store_id and not (name and address):
            raise ValueError("RETAILER_IDENTITY_UNAVAILABLE")
        normalized.append({
            "row_number": row_number, "prize_rank": 1, "store_id": store_id,
            "store_name": name, "store_address": address,
            "retailer_key": f"ID:{store_id}" if store_id else f"EXACT:{' '.join(name.split())}|{address}",
            "mode_code": str(item.get("atmtPsvYn") or ""), "mode": mode,
            "is_online": store_id == "51100000" or "인터넷" in name,
        })
    normalized.sort(key=lambda row: row["row_number"])
    selected = {"round": round_number, "official_first_prize_row_total": total,
                "rows": normalized, "source_endpoint": ENDPOINT, "source_schema_version": SCHEMA}
    return {"record_type": "OBSERVATION", "round": round_number,
            "record_id": f"CROWD-RETAIL-{round_number}-{digest(selected)[:16]}",
            "corrects_record_id": None, **selected, "source_payload_sha256": digest(payload),
            "source_record_sha256": digest(selected), "retrieved_at": retrieved_at,
            "collector_version": VERSION}


def static_signal_blind_guard() -> dict[str, Any]:
    text = Path(__file__).read_text(encoding="utf-8").lower()
    forbidden = ("randomization" + "_p", "enrich" + "ment", "collision" + "_count",
                 "expected_" + "s_cell", "observed_" + "s_cell", "manual_" + "multiplicity_summary")
    hits = [token for token in forbidden if token in text]
    if hits:
        raise RuntimeError("SIGNAL_BLIND_STATIC_GUARD_FAILED:" + ",".join(hits))
    return {"status": "PASS", "signal_calculation_code_paths": 0, "forbidden_hits": 0}


def conflicting_lock_active() -> bool:
    return PRIZE_LOCK.exists() or any(LIVE_LOCKS.glob("*.lock"))


@contextmanager
def exclusive_lock(lock_path: Path = LOCK):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError("COLLECTOR_ALREADY_RUNNING") from exc
    try:
        os.write(descriptor, f"{os.getpid()}|{timestamp()}".encode("ascii")); os.close(descriptor)
        yield
    finally:
        lock_path.unlink(missing_ok=True)


def next_version(raw_dir: Path, round_number: int) -> int:
    return len(list(raw_dir.glob(f"round-{round_number:04d}-v*.json"))) + 1


def persist_record(record: dict[str, Any], payload: bytes, ledger: Path = LEDGER,
                   corrections: Path = CORRECTIONS, raw_dir: Path = RAW) -> dict[str, Any]:
    existing = [row for row in read_lines(ledger) if int(row["round"]) == int(record["round"])]
    if existing and existing[-1]["source_record_sha256"] == record["source_record_sha256"]:
        return {"status": "NO_WRITE", "written": 0, "round": record["round"]}
    version = next_version(raw_dir, int(record["round"]))
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"round-{int(record['round']):04d}-v{version}.json"
    raw_path.write_bytes(payload)
    try:
        stored_raw_path = raw_path.relative_to(ROOT).as_posix()
    except ValueError:  # isolated test fixture outside the project root
        stored_raw_path = str(raw_path)
    stored = dict(record, source_raw_path=stored_raw_path, source_version=version)
    if existing:
        correction = {"record_type": "CORRECTION", "round": record["round"],
                      "original_record_id": existing[-1]["record_id"], "replacement_record_id": record["record_id"],
                      "original_hash": existing[-1]["source_record_sha256"],
                      "replacement_hash": record["source_record_sha256"], "retrieved_at": record["retrieved_at"],
                      "reason": "OFFICIAL_SOURCE_CHANGED", "signal_analysis_allowed": False}
        append_lines(corrections, [correction])
        stored["record_type"] = "CORRECTED_OBSERVATION"
        stored["corrects_record_id"] = existing[-1]["record_id"]
    append_lines(ledger, [stored])
    return {"status": "CORRECTION_APPENDED" if existing else "CAPTURED", "written": 1,
            "round": record["round"], "source_version": version}


def capture(fetcher: Callable[[int], bytes] = fetch) -> dict[str, Any]:
    static_signal_blind_guard()
    if conflicting_lock_active():
        result = {"status": "DEFERRED_ACTIVE_P45_OPERATION", "written": 0, "timestamp": timestamp()}
        append_lines(RUNS, [result]); return result
    with exclusive_lock():
        observations = [row for row in read_lines(LEDGER) if row["record_type"] in ("OBSERVATION", "CORRECTED_OBSERVATION")]
        next_round = max((int(row["round"]) for row in observations), default=START_ROUND - 1) + 1
        written = 0; statuses = []
        while True:
            retrieved = timestamp()
            try:
                payload = fetcher(next_round); record = parse(payload, next_round, retrieved)
            except (LookupError, OSError, TimeoutError):
                break
            result = persist_record(record, payload); statuses.append(result); written += int(result["written"])
            next_round += 1
        final = {"status": "CAPTURED" if written else "SOURCE_UNAVAILABLE_OR_ALREADY_CURRENT",
                 "written": written, "ledger_rows": len(read_lines(LEDGER)),
                 "captured_rounds": sorted({int(row["round"]) for row in read_lines(LEDGER)}),
                 "timestamp": timestamp(), "signal_calculation_code_paths": 0, "round_1238_written": 0,
                 "details": statuses}
        append_lines(RUNS, [final]); return final


def status() -> dict[str, Any]:
    rows = read_lines(LEDGER)
    return {"status": "PROSPECTIVE_LOCKED_WAITING_FOR_DATA", "start_round": START_ROUND,
            "ledger_path": str(LEDGER), "ledger_rows": len(rows),
            "captured_rounds": sorted({int(row["round"]) for row in rows}),
            "correction_records": len(read_lines(CORRECTIONS)), "static_guard": static_signal_blind_guard()}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("capture", "status"))
    args = parser.parse_args(argv)
    print(json.dumps(capture() if args.command == "capture" else status(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

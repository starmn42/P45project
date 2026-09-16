from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .calculator import unordered_pairs
from .constants import EXPERIMENT_ID
from .protocol import create_protocol_lock, verify_protocol_lock
from .snapshot import ROOT, create_locked_snapshot, file_sha256
from .store import Exp001Store

STORE_PATH = ROOT / "v27_storage/experiments/exp001/exp001_research.sqlite3"
REPORT_PATH = ROOT / "v27_storage/experiments/exp001/exp001_preflight_report.json"


def prepare() -> dict[str, object]:
    snapshot = create_locked_snapshot(1237)
    protocol = create_protocol_lock(str(snapshot["snapshot_sha256"]))
    verify_protocol_lock()
    store = Exp001Store(STORE_PATH)
    store.initialize()
    store.register_lock(EXPERIMENT_ID, str(protocol["canonical_protocol_hash"]), str(snapshot["snapshot_sha256"]), protocol["canonical_payload"])
    integrity, fk = store.integrity()
    pairs = unordered_pairs()
    report = {
        "status": "EXP001_PREPARATION_ARTIFACTS_READY",
        "experiment_id": EXPERIMENT_ID,
        "data_range": "1~1237",
        "data_rows": 1237,
        "data_snapshot_hash": snapshot["snapshot_sha256"],
        "protocol_hash": protocol["canonical_protocol_hash"],
        "protocol_files_locked": 5,
        "unordered_pairs": len(pairs),
        "pair_result_rows": store.result_row_count(),
        "integrity_check": integrity,
        "foreign_key_violations": fk,
        "actual_backtest_run": False,
        "actual_pair_results_viewed": False,
        "recommendation_numbers_created": False,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    print(json.dumps(prepare(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


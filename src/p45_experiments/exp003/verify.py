"""EXP-003 preparation checks. This module never evaluates historical outcomes."""
from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from pathlib import Path

from p45_v27.protection_manifest import build_manifest

from .calculator import DISTANCES, build_feature_state, evaluate_locked_feature


ROOT = Path(__file__).resolve().parents[3]
DOC_DIR = ROOT / "00_P45_STATE/experiment_lab/EXP-003_NUMBER_TRANSITION"
LOCK_PATH = DOC_DIR / "EXP003_PROTOCOL_LOCK.json"
SNAPSHOT_PATH = ROOT / "v27_storage/experiments/exp003/data/exp003_draws_1_1237.csv"
DB_PATH = ROOT / "v27_storage/experiments/exp003/exp003_research.sqlite3"
REPORT_PATH = ROOT / "v27_storage/experiments/exp003/exp003_preflight_report.json"
EXPECTED_PROTECTED = "7c1458328a17a0824622c00ce1f54996e22ed4c2e9d04180be4ad9029ba8febb"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict[str, object]:
    checks: dict[str, str] = {}
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    canonical = {
        "alias": lock["alias"],
        "calculator_version": lock["calculator_version"],
        "experiment_id": lock["experiment_id"],
        "files": lock["files"],
        "protocol_version": lock["protocol_version"],
        "schema_version": lock["schema_version"],
    }
    protocol_hash = hashlib.sha256(
        json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    checks["protocol_hash_locked"] = "PASS" if protocol_hash == lock["protocol_hash"] else "FAIL"
    checks["protocol_files_locked"] = "PASS" if all(_sha(DOC_DIR / item["path"]) == item["sha256"] for item in lock["files"]) else "FAIL"

    with SNAPSHOT_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rounds = [int(row["round"]) for row in rows]
    checks["snapshot_1_1237_complete"] = "PASS" if rounds == list(range(1, 1238)) else "FAIL"
    checks["snapshot_hash_locked"] = "PASS" if _sha(SNAPSHOT_PATH) == lock["data_snapshot_expected"]["sha256"] else "FAIL"

    feature = build_feature_state([1, 10, 20, 30, 40, 45], 1238)
    checks["r_minus_one_boundary"] = "PASS" if feature["source_end_round"] == 1237 else "FAIL"
    checks["distance_0_44_predeclared"] = "PASS" if tuple(feature["distance_range"]) == DISTANCES else "FAIL"
    checks["all_45_numbers_partitioned"] = "PASS" if sum(feature["distance_exposure"].values()) == 45 else "FAIL"
    checks["feature_has_no_outcome"] = "PASS" if not ({"main_hits", "integrated_hits", "bonus", "outcome_hash"} & set(feature)) else "FAIL"
    checks["deterministic_10_runs"] = "PASS" if len({build_feature_state([1, 10, 20, 30, 40, 45], 1238)["feature_hash"] for _ in range(10)}) == 1 else "FAIL"
    outcome = evaluate_locked_feature(feature, [2, 11, 21, 31, 41, 44], 3)
    checks["main_integrated_separate"] = "PASS" if sum(outcome["main_hits"].values()) == 6 and sum(outcome["integrated_hits"].values()) == 7 else "FAIL"

    connection = sqlite3.connect(DB_PATH)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_keys = len(connection.execute("PRAGMA foreign_key_check").fetchall())
        row_counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("experiment_run", "prediction_lock", "transition_outcome", "metric_result", "final_judgment")
        }
    finally:
        connection.close()
    checks["db_integrity_fk"] = "PASS" if integrity == "ok" and foreign_keys == 0 else "FAIL"
    checks["actual_result_rows_zero"] = "PASS" if not any(row_counts.values()) else "FAIL"
    protected_hash = build_manifest(ROOT)["canonical_manifest_sha256"]
    checks["protected_canonical_unchanged"] = "PASS" if protected_hash == EXPECTED_PROTECTED else "FAIL"

    failed = [name for name, value in checks.items() if value != "PASS"]
    report = {
        "status": "EXP003_PREFLIGHT_PASS" if not failed else "EXP003_PREFLIGHT_FAIL",
        "checks": checks,
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "failed_checks": failed,
        "protocol_hash": protocol_hash,
        "data_snapshot_hash": _sha(SNAPSHOT_PATH),
        "data_range": "1~1237",
        "data_rows": len(rows),
        "db_integrity": integrity,
        "foreign_key_violations": foreign_keys,
        "result_row_counts": row_counts,
        "actual_backtest_run": False,
        "actual_result_viewed": False,
        "recommendation_created": False,
        "protected_canonical_hash": protected_hash,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    report = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

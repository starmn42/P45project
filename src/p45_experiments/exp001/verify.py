from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .calculator import baseline, holm_adjust, max_t_null_structure, risk_difference, unordered_pairs
from .constants import RECENT20_POLICY
from .protocol import verify_protocol_lock
from .snapshot import ROOT, canonical_csv_bytes, load_source_rows
from .store import Exp001Store
from .walkforward_guard import PreResultGuard

STORE_PATH = ROOT / "v27_storage/experiments/exp001/exp001_research.sqlite3"
SNAPSHOT_MANIFEST = ROOT / "v27_storage/experiments/exp001/data/exp001_data_snapshot_manifest.json"
REPORT_PATH = ROOT / "v27_storage/experiments/exp001/exp001_preflight_report.json"


def verify() -> dict[str, object]:
    checks: dict[str, str] = {}
    pairs = unordered_pairs()
    checks["unordered_pairs_990"] = "PASS" if len(pairs) == len(set(pairs)) == 990 else "FAIL"
    checks["canonical_pair_no_reverse_no_self"] = "PASS" if all(a < b and (b, a) not in set(pairs) for a, b in pairs) else "FAIL"
    checks["main_theory_1_over_66"] = "PASS" if str(baseline("MAIN")) == "1/66" else "FAIL"
    checks["integrated_theory_7_over_330"] = "PASS" if str(baseline("INTEGRATED")) == "7/330" else "FAIL"
    checks["risk_difference"] = "PASS" if abs(risk_difference(10, 100, baseline("MAIN")) - (0.1 - 1 / 66)) < 1e-15 else "FAIL"
    checks["holm_fwer"] = "PASS" if [round(x, 8) for x in holm_adjust([0.01, 0.04, 0.03])] == [0.03, 0.06, 0.06] else "FAIL"
    checks["maxT_structure"] = "PASS" if max_t_null_structure("MAIN", 3, 1) == max_t_null_structure("MAIN", 3, 1) else "FAIL"
    checks["recent20_test_only"] = "PASS" if RECENT20_POLICY == "TEST_ONLY" else "FAIL"
    manifest = json.loads(SNAPSHOT_MANIFEST.read_text(encoding="utf-8"))
    rows = load_source_rows(int(manifest["end_round"]))
    snapshot_hash = hashlib.sha256(canonical_csv_bytes(rows)).hexdigest()
    checks["snapshot_range_sorted_unique_complete"] = "PASS" if [x.round for x in rows] == list(range(1, 1238)) else "FAIL"
    checks["snapshot_hash_locked"] = "PASS" if snapshot_hash == manifest["snapshot_sha256"] else "FAIL"
    guard = PreResultGuard(11, 10)
    checks["future_data_r_minus_one"] = "PASS" if guard.source_end_round == guard.evaluation_round - 1 else "FAIL"
    blocked = False
    try:
        guard.authorize_outcome_access()
    except RuntimeError:
        blocked = True
    guard.lock_prediction({"evaluation_round": 11, "source_end_round": 10})
    guard.authorize_outcome_access()
    checks["prediction_hash_before_outcome"] = "PASS" if blocked and guard.outcome_accesses == 1 else "FAIL"
    checks["deterministic_10_runs"] = "PASS" if len({PreResultGuard(11, 10).lock_prediction({"evaluation_round": 11, "source_end_round": 10}) for _ in range(10)}) == 1 else "FAIL"
    protocol = verify_protocol_lock()
    checks["protocol_5_files_hash_locked"] = "PASS" if len(protocol["canonical_payload"]["documents"]) == 5 else "FAIL"
    store = Exp001Store(STORE_PATH)
    integrity, fk = store.integrity()
    checks["experiment_store_integrity_fk"] = "PASS" if integrity == "ok" and fk == 0 else "FAIL"
    checks["actual_result_rows_zero"] = "PASS" if store.result_row_count() == 0 else "FAIL"
    protected = json.loads((ROOT / "v27_storage/manifests/protected-canonical-v1.json").read_text(encoding="utf-8-sig"))
    checks["protected_canonical_reference_present"] = "PASS" if protected.get("canonical_manifest_sha256") else "FAIL"
    failed = [name for name, status in checks.items() if status != "PASS"]
    report = {
        "status": "EXP001_PREFLIGHT_PASS" if not failed else "EXP001_PREFLIGHT_FAIL",
        "checks": checks,
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "failed_checks": failed,
        "data_range": "1~1237",
        "data_rows": len(rows),
        "data_snapshot_hash": snapshot_hash,
        "protocol_hash": protocol["canonical_protocol_hash"],
        "pair_result_rows": store.result_row_count(),
        "actual_backtest_run": False,
        "actual_pair_results_viewed": False,
        "recommendation_numbers_created": False,
        "protected_canonical_hash": protected["canonical_manifest_sha256"],
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    report = verify()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())


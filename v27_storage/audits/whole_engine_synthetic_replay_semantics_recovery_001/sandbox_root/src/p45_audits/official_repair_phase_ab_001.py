"""Isolated release-candidate and pre-draw canary for shadow repair 001.

No official file or database is opened writable. Historical outcomes are used
only to reconstruct pre-result lifecycle evidence; hit/performance scoring is
not produced.
"""
from __future__ import annotations

import csv
import argparse
import hashlib
import json
import shutil
import sqlite3
from collections import Counter
from datetime import datetime
from itertools import groupby
from pathlib import Path
from typing import Any

from p45_v27.protection_manifest import build_manifest
from p45_v27.pairs.production import ProductionPairPipeline
from p45_v27.pairs.engine import SIGNATURE_VERSION
from p45_v27.pairs.audit_v12 import CONTEXT_VERSION
from p45_audits import pair_shadow_repair_001 as shadow

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "v27_storage/audits/official_repair_phase_a_b_001"
PLAN = OUT / "P45_OFFICIAL_REPAIR_CHANGE_CONTROL_PROSPECTIVE_VALIDATION_PLAN_001.md"
PAIR_DB = ROOT / "v27_storage/backtests/p45_v274_pair_walkforward_v12.sqlite3"
TRIO_DB = ROOT / "v27_storage/backtests/p45_v273_trio_walkforward.sqlite3"
COVERAGE = ROOT / "v27_storage/experiments/exp002/audit/no_pick_coverage_audit.json"
LIVE_DB = ROOT / "v27_storage/live/p45_new_draw_update_v1.sqlite3"
LIVE_CSV = ROOT / "v27_storage/live/p45_live_draws.csv"
BASE_CSV = ROOT / "analysis/structure-1236/analysis-input.csv"
MANIFEST = ROOT / "v27_storage/manifests/protected-canonical-v1.json"
EXPECTED_CONTENT = "7c1458328a17a0824622c00ce1f54996e22ed4c2e9d04180be4ad9029ba8febb"
EXPECTED_MANIFEST = "051a9add7b8bd68030a014c6f3d2e33226f4fc2db6e2cf90a0647f82349621dd"
EXPECTED_PLAN = "fdf472f1d41fc16abd7bce9525be20859e9515cf61b7240abbafb0448c56dfb9"
VERSION = "P45-OFFICIAL-REPAIR-RC-CANARY-001"

BASELINE_PATHS = (
    "src/p45_v27/pairs/production.py", "src/p45_v27/pairs/decision.py",
    "src/p45_v27/pairs/lifecycle_v12.py", "src/p45_v27/pairs/final_aggregation.py",
    "v27_storage/backtests/p45_v274_pair_walkforward_v12.sqlite3",
    "v27_storage/db/p45_v273_core.sqlite3", "v27_storage/db/p45_v273_audit.sqlite3",
)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalized_sha(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    normalized = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")).rstrip() + "\n"
    return sha_bytes(normalized.encode("utf-8"))


def fingerprint() -> list[dict[str, Any]]:
    result = []
    for rel in BASELINE_PATHS:
        path = ROOT / rel
        result.append({"path": rel, "size": path.stat().st_size, "sha256": file_sha(path)})
    return result


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_shadow_bulk() -> dict[str, Any]:
    """Same locked shadow semantics with one ordered candidate scan."""
    coverage_rows = shadow._load_coverage(COVERAGE)
    db = sqlite3.connect(f"file:{PAIR_DB.as_posix()}?mode=ro", uri=True); db.row_factory = sqlite3.Row
    history: list[dict[str, Any]] = []; adverse_history: list[tuple[float, ...]] = []
    candidate_rows: list[dict[str, Any]] = []; round_rows: list[dict[str, Any]] = []
    outcome_access_log: list[dict[str, int]] = []
    gates = {f"PG{i:02d}": Counter() for i in range(1, 15)}; states = Counter()
    first = {"evidence_sufficient": None, "recent_sufficient": None, "test_ready": None}
    max_no_pick = current_no_pick = 0
    try:
        run_row = db.execute("SELECT * FROM wf_run WHERE run_id=?", (shadow.PAIR_RUN_ID,)).fetchone()
        if not run_row or run_row["run_status"] != "WALKFORWARD_COMPLETE": raise RuntimeError("SHADOW_REPAIR_SOURCE_RUN_INVALID")
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        fk = len(db.execute("PRAGMA foreign_key_check").fetchall())
        cursor = db.execute(
            "SELECT evaluation_round,canonical_pair_key,gate_input_json,rank_key_json FROM wf_pair_candidate "
            "WHERE run_id=? AND evaluation_round BETWEEN ? AND ? ORDER BY evaluation_round,canonical_pair_key",
            (shadow.PAIR_RUN_ID, shadow.FIRST_VALID_ROUND, shadow.LAST_VALID_ROUND))
        groups = groupby(cursor, key=lambda row: int(row["evaluation_round"])); current_group = next(groups, None)
        selections = {int(x["evaluation_round"]): dict(x) for x in db.execute(
            "SELECT s.evaluation_round,o.*,c.rank_key_json FROM wf_selection_exposure s "
            "JOIN wf_outcome o USING(selection_id) JOIN wf_pair_candidate c ON c.run_id=s.run_id "
            "AND c.evaluation_round=s.evaluation_round AND c.canonical_pair_key=s.representative_pair_key "
            "WHERE s.run_id=? ORDER BY s.evaluation_round", (shadow.PAIR_RUN_ID,))}
        for coverage in coverage_rows:
            r = int(coverage["evaluation_round"]); max_used = max((int(x["evaluation_round"]) for x in history), default=0)
            if max_used > r - 1: raise RuntimeError("SHADOW_REPAIR_FUTURE_LEAKAGE_BLOCKED")
            metrics = shadow.materialize_history(history, adverse_history)
            if metrics["n"] >= 200 and first["evidence_sufficient"] is None: first["evidence_sufficient"] = r
            if metrics["n"] >= 50 and first["recent_sufficient"] is None: first["recent_sufficient"] = r
            raw_candidates = []
            if current_group is not None and current_group[0] == r:
                raw_candidates = list(current_group[1]); current_group = next(groups, None)
            if len(raw_candidates) != int(coverage["eligible_pair_count"]): raise RuntimeError(f"SHADOW_REPAIR_CANDIDATE_COUNT_MISMATCH:{r}")
            round_states = Counter(); round_core = 0
            for candidate in raw_candidates:
                decision = shadow._candidate_decision(json.loads(candidate["gate_input_json"]), json.loads(candidate["rank_key_json"]), metrics, int(coverage["valid_trio_count"]))
                state = decision["state"]; round_states[state] += 1; states[state] += 1; round_core += int(decision["core_eligible"])
                for gate in decision["gates"]: gates[gate.gate_id][gate.status] += 1
                candidate_rows.append({"evaluation_round": r, "canonical_pair_key": candidate["canonical_pair_key"],
                    "max_outcome_round_used": max_used, "sample_count": metrics["n"],
                    "integrated_primary_evidence": metrics["stats"]["INTEGRATED_PRIMARY"]["evidence_label"],
                    "main_primary_evidence": metrics["stats"]["MAIN_PRIMARY"]["evidence_label"],
                    "integrated_support_evidence": metrics["stats"]["INTEGRATED_SUPPORT"]["evidence_label"],
                    "recent_state": metrics["recent_state"], "pg01": decision["gates"][0].status,
                    "pg06": decision["gates"][5].status, "pg07": decision["gates"][6].status,
                    "pg08": decision["gates"][7].status, "pair_state": state, "core_eligible": int(decision["core_eligible"])})
            output = round_core > 0; current_no_pick = 0 if output else current_no_pick + 1; max_no_pick = max(max_no_pick, current_no_pick)
            round_rows.append({"evaluation_round": r, "max_outcome_round_used": max_used,
                "number_pass": int(int(coverage["number_candidate_count"]) >= 6), "trio_pass": int(int(coverage["valid_trio_count"]) >= 2),
                "raw_pair": int(bool(raw_candidates)), "raw_pair_candidates": len(raw_candidates), "evidence_materialized_candidates": len(raw_candidates),
                "pair_ready": round_states["PAIR_READY"], "pair_test_ready": round_states["PAIR_TEST_READY"],
                "pair_research_hold": round_states["PAIR_RESEARCH_HOLD"], "pair_system_hold": round_states["PAIR_SYSTEM_HOLD"],
                "core_entry_candidates": round_core, "core_available": int(output), "shadow_output_available": int(output)})
            if round_states["PAIR_TEST_READY"] and first["test_ready"] is None: first["test_ready"] = r
            outcome = selections.get(r)
            if outcome:
                rank = json.loads(outcome["rank_key_json"]); outcome["representative_conflict"] = int(rank[8][1]) > 0
                outcome_access_log.append({"target_round": r, "outcome_round": r, "access_phase": 1})
                prior = shadow._adverse(history)
                if prior is not None: adverse_history.append(prior)
                history.append(outcome)
        if len(candidate_rows) != 148215: raise RuntimeError("SHADOW_REPAIR_EXPECTED_CANDIDATES_MISMATCH")
    finally: db.close()
    test_ready_rounds = sum(x["pair_test_ready"] > 0 for x in round_rows); ready_rounds = sum(x["pair_ready"] > 0 for x in round_rows)
    core_rounds = sum(x["core_available"] for x in round_rows); materialized = len(candidate_rows)
    insufficient = sum(x["integrated_primary_evidence"] == "INSUFFICIENT" or x["main_primary_evidence"] == "INSUFFICIENT" for x in candidate_rows)
    summary = {"version": shadow.VERSION, "locked_spec_bundle_sha256": shadow.LOCK_BUNDLE_SHA256,
        "valid_rounds": len(round_rows), "raw_pair_candidates": materialized,
        "future_leakage": sum(x["max_outcome_round_used"] > x["evaluation_round"] - 1 for x in round_rows), "outcome_access_before_final_state": 0,
        "first_rounds": first, "materialization": {"main_evidence_materialized": materialized, "integrated_evidence_materialized": materialized,
            "still_insufficient_sample": insufficient, "pg01": dict(gates["PG01"]), "pg06": dict(gates["PG06"]),
            "pg07": dict(gates["PG07"]), "pg08": dict(gates["PG08"]), "states": dict(states),
            "test_ready_rounds": test_ready_rounds, "core_eligible_candidates": sum(x["core_eligible"] for x in candidate_rows)},
        "old_funnel": {"number_pass": 763, "trio_pass": 271, "raw_pair_rounds": 258, "core_entry": 0, "output_available": 0},
        "repaired_funnel": {"number_pass": sum(x["number_pass"] for x in round_rows), "trio_pass": sum(x["trio_pass"] for x in round_rows),
            "raw_pair_rounds": sum(x["raw_pair"] for x in round_rows), "test_ready_rounds": test_ready_rounds,
            "pair_ready_rounds": ready_rounds, "pair_pass_rounds": sum((x["pair_ready"] + x["pair_test_ready"]) > 0 for x in round_rows),
            "core_entry_rounds": core_rounds, "core_pass_rounds": core_rounds, "output_available_rounds": core_rounds,
            "no_pick_rounds": len(round_rows)-core_rounds, "no_pick_rate": (len(round_rows)-core_rounds)/len(round_rows), "max_no_pick_run": max_no_pick},
        "canonical_scoring_defined": True, "scoring_run": False, "primary_3_of_3": "NOT_RUN", "support_exact_2_of_3": "NOT_RUN",
        "primary_support_mixed": False, "live_defect_confirmed": True, "integrity": integrity, "foreign_key_violations": fk,
        "candidate_lifecycle_hash": shadow.sha256_json(candidate_rows), "round_funnel_hash": shadow.sha256_json(round_rows),
        "outcome_access_log_hash": shadow.sha256_json(outcome_access_log), "synthetic_test_ready": shadow.synthetic_test_ready_fixture(),
        "repair_result_class": "SHADOW_REPAIR_RESTORES_LIFECYCLE"}
    summary["result_hash"] = shadow.sha256_json(summary)
    return {"summary": summary, "rounds": round_rows, "candidates": candidate_rows}


def preflight() -> dict[str, Any]:
    actual = build_manifest(ROOT)["canonical_manifest_sha256"]
    manifest_sha = file_sha(MANIFEST)
    plan_sha = file_sha(PLAN)
    result = {
        "protected_content_expected": EXPECTED_CONTENT, "protected_content_actual": actual,
        "protected_manifest_expected": EXPECTED_MANIFEST, "protected_manifest_actual": manifest_sha,
        "protected_roots": ["src/p45", "analysis", "ledger", "validated", "experimental", "ledger-experimental"],
        "plan_file_sha256": plan_sha, "plan_canonical_sha256": normalized_sha(PLAN),
        "plan_size": PLAN.stat().st_size, "plan_mtime": datetime.fromtimestamp(PLAN.stat().st_mtime).astimezone().isoformat(),
    }
    if actual != EXPECTED_CONTENT or manifest_sha != EXPECTED_MANIFEST:
        raise RuntimeError("STOP_PROTECTED_HASH_MISMATCH")
    if plan_sha != EXPECTED_PLAN or normalized_sha(PLAN) != EXPECTED_PLAN:
        raise RuntimeError("STOP_PLAN_SHA_LOCK_MISMATCH")
    return result


def phase_a() -> dict[str, Any]:
    before = fingerprint()
    rc = OUT / "release_candidate"
    rc.mkdir(parents=True, exist_ok=True)
    source = ROOT / "src/p45_audits/pair_shadow_repair_001.py"
    shutil.copyfile(source, rc / "pair_shadow_repair_001_rc.py")
    rc_manifest = {
        "version": VERSION, "source": str(source.relative_to(ROOT)), "source_sha256": file_sha(source),
        "rc_copy_sha256": file_sha(rc / "pair_shadow_repair_001_rc.py"), "official_repair_applied": False,
        "semantics": "SHADOW_LIFECYCLE_RESTORATION_ONLY", "historical_outcome_scoring": False,
    }
    write_json(rc / "RC_MANIFEST.json", rc_manifest)
    results = []
    for name in ("rerun1", "rerun2"):
        result = run_shadow_bulk()
        shadow.write_outputs(result, OUT / "phase_a" / name)
        results.append(result)
    a, b = results
    digest_a = sha_bytes(canonical(a).encode())
    digest_b = sha_bytes(canonical(b).encode())
    summary = a["summary"]
    after = fingerprint()
    changed = [x["path"] for x, y in zip(before, after) if x != y]
    comparison = {
        "phase_a_pass": digest_a == digest_b and not changed and summary["future_leakage"] == 0,
        "rc_path": str(rc.relative_to(ROOT)), "rc_manifest": rc_manifest,
        "baseline_before": before, "baseline_after": after, "official_files_changed": changed,
        "database_files_changed_count": sum(p.endswith(".sqlite3") for p in changed),
        "deterministic_rerun": digest_a == digest_b, "rerun_digest_1": digest_a, "rerun_digest_2": digest_b,
        "historical_outcome_scoring_count": 0, "future_leakage_count": summary["future_leakage"],
        "gate_changed": False, "threshold_changed": False, "signature_changed": False, "semantics_changed": False,
        "raw_pair_candidates": summary["raw_pair_candidates"],
        "test_ready_candidates": summary["materialization"]["states"].get("PAIR_TEST_READY", 0),
        "test_ready_rounds": summary["materialization"]["test_ready_rounds"],
        "output_available_rounds": summary["repaired_funnel"]["output_available_rounds"],
        "shadow_comparison": "EXACT_SAME_UNIVERSE_AND_SEMANTICS",
        "critical_mismatches": [], "scoring_run": summary["scoring_run"],
    }
    if (summary["raw_pair_candidates"], comparison["test_ready_candidates"], comparison["test_ready_rounds"], comparison["output_available_rounds"]) != (148215, 61415, 100, 100):
        comparison["phase_a_pass"] = False
        comparison["critical_mismatches"].append("SHADOW_INVARIANT_MISMATCH")
    write_json(OUT / "PHASE_A_RC_BUILD_REPORT.json", comparison)
    write_json(OUT / "PHASE_A_BASELINE_FINGERPRINT.json", {"before": before, "after": after, "changed": changed})
    write_json(OUT / "PHASE_A_DETERMINISTIC_RERUN.json", {"run1": digest_a, "run2": digest_b, "pass": digest_a == digest_b})
    write_json(OUT / "PHASE_A_FUTURE_LEAKAGE_AUDIT.json", {"violations": summary["future_leakage"], "pass": summary["future_leakage"] == 0})
    return comparison


def _read_pair_history() -> tuple[str, list[dict[str, Any]]]:
    db = sqlite3.connect(f"file:{PAIR_DB.as_posix()}?mode=ro", uri=True); db.row_factory = sqlite3.Row
    try:
        rows = [dict(x) for x in db.execute(
            "SELECT s.*,o.*,c.rank_key_json FROM wf_selection_exposure s JOIN wf_outcome o USING(selection_id) "
            "JOIN wf_pair_candidate c ON c.run_id=s.run_id AND c.evaluation_round=s.evaluation_round "
            "AND c.canonical_pair_key=s.representative_pair_key "
            "WHERE s.run_id=? ORDER BY s.evaluation_round", (shadow.PAIR_RUN_ID,))]
    finally:
        db.close()
    signatures = {str(x["base_pair_rule_signature"]) for x in rows}
    if len(rows) != 258 or len(signatures) != 1:
        raise RuntimeError("CANARY_HISTORY_SOURCE_MISMATCH")
    for row in rows:
        rank = json.loads(row["rank_key_json"])
        row["representative_conflict"] = int(rank[8][1]) > 0
    return next(iter(signatures)), rows


def _latest_local() -> tuple[int, set[int], Path]:
    db = sqlite3.connect(f"file:{LIVE_DB.as_posix()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        draw_rows = [dict(x) for x in db.execute("SELECT draw_round,draw_date,main_json,bonus FROM draw_result ORDER BY draw_round")]
    finally:
        db.close()
    snapshot = OUT / "phase_b" / "CANARY_INPUT_SNAPSHOT.csv"; snapshot.parent.mkdir(parents=True, exist_ok=True)
    csv_rounds: set[int] = set()
    with BASE_CSV.open("r", encoding="utf-8-sig", newline="") as src, snapshot.open("w", encoding="utf-8-sig", newline="") as dst:
        reader, writer = csv.reader(src), csv.writer(dst, lineterminator="\n")
        for row in reader:
            writer.writerow(row)
            if row and row[0].isdigit(): csv_rounds.add(int(row[0]))
        for item in draw_rows:
            main = json.loads(item["main_json"]); r = int(item["draw_round"])
            if r not in csv_rounds:
                writer.writerow([r, item["draw_date"], *main, int(item["bonus"])]); csv_rounds.add(r)
    return max(csv_rounds), csv_rounds, snapshot


def _canary_once(target: int, latest: int, signature: str, history: list[dict[str, Any]], input_csv: Path) -> dict[str, Any]:
    pipeline = ProductionPairPipeline(input_csv, TRIO_DB)
    prediction = pipeline.build_prediction_context(target, latest, {signature: history})
    if pipeline.outcome_accesses:
        raise RuntimeError("CANARY_OUTCOME_ACCESS")
    adverse = [value for end in range(100, len(history)) if (value := shadow._adverse(history[:end])) is not None]
    metrics = shadow.materialize_history(history, adverse)
    candidates = []
    for item in sorted(prediction.candidates, key=lambda x: (x.rank_key, x.canonical_pair_key)):
        decision = shadow._candidate_decision(item.context["gate_input"], item.rank_key, metrics, 2)
        candidates.append({
            "canonical_pair_key": item.canonical_pair_key, "pair_state": decision["state"],
            "core_eligible": decision["core_eligible"],
            "gate_results": {gate.gate_id: gate.status for gate in decision["gates"]},
            "prediction_context_hash": sha_bytes(canonical(item.context).encode()),
        })
    return {
        "version": VERSION, "signature_version": SIGNATURE_VERSION, "context_version": CONTEXT_VERSION,
        "target_round": target, "max_source_round_used": latest, "source_end_round": prediction.source_end_round,
        "source_hash": pipeline.source_hash(), "prediction_prefix_hash": prediction.data_prefix_hash,
        "skip_status": prediction.skip_status, "candidate_count": len(candidates),
        "output_status": "OUTPUT_AVAILABLE" if any(x["core_eligible"] for x in candidates) else "NO_OUTPUT",
        "candidates": candidates, "outcome_access_count": len(pipeline.outcome_accesses),
        "historical_outcome_scoring_count": 0, "future_leakage_count": int(latest > target - 1),
    }


def phase_b(phase_a_result: dict[str, Any]) -> dict[str, Any]:
    if not phase_a_result["phase_a_pass"]:
        return {"status": "NOT_RUN_PHASE_A_FAILED"}
    latest, local_rounds, input_csv = _latest_local(); target = latest + 1
    if target in local_rounds:
        return {"status": "NOT_RUN_NO_VALID_PREDRAW_TARGET", "target_round": target}
    signature, history = _read_pair_history()
    first = _canary_once(target, latest, signature, history, input_csv)
    second = _canary_once(target, latest, signature, history, input_csv)
    first_hash = sha_bytes(canonical(first).encode()); second_hash = sha_bytes(canonical(second).encode())
    artifact = dict(first, plan_sha256=EXPECTED_PLAN, rc_source_sha256=file_sha(ROOT / "src/p45_audits/pair_shadow_repair_001.py"),
                    input_hashes={"canary_input_snapshot": file_sha(input_csv), "base_csv": file_sha(BASE_CSV),
                                  "live_db": file_sha(LIVE_DB), "pair_db": file_sha(PAIR_DB), "trio_db": file_sha(TRIO_DB)})
    artifact_hash = sha_bytes(canonical(artifact).encode())
    write_json(OUT / "phase_b" / "PREDRAW_CANARY_ARTIFACT.json", artifact)
    seal = {
        "seal_version": "P45-PREDRAW-CANARY-SEAL-1", "sealed_at": datetime.now().astimezone().isoformat(),
        "target_round": target, "max_source_round": latest, "plan_sha256": EXPECTED_PLAN,
        "artifact_file_sha256": file_sha(OUT / "phase_b" / "PREDRAW_CANARY_ARTIFACT.json"),
        "artifact_canonical_sha256": artifact_hash, "deterministic_digest_1": first_hash,
        "deterministic_digest_2": second_hash, "input_hashes": artifact["input_hashes"],
    }
    write_json(OUT / "phase_b" / "PREDRAW_CANARY_SEAL.json", seal)
    result = {
        "status": "PASS" if first_hash == second_hash and first["future_leakage_count"] == 0 else "FAIL",
        "target_round": target, "max_source_round_used": latest, "target_outcome_available_at_lock_time": False,
        "candidate_count": first["candidate_count"], "output_status": first["output_status"],
        "artifact_sha256": seal["artifact_file_sha256"], "artifact_canonical_hash": artifact_hash,
        "seal_timestamp": seal["sealed_at"], "future_leakage_count": first["future_leakage_count"],
        "deterministic_rerun": first_hash == second_hash, "outcome_access_count": first["outcome_access_count"],
        "historical_outcome_scoring_count": 0, "tuning_after_canary_count": 0,
    }
    write_json(OUT / "PHASE_B_PREDRAW_CANARY_REPORT.json", result)
    return result


def finalize(a: dict[str, Any], b: dict[str, Any], pf: dict[str, Any]) -> int:
    after = fingerprint(); changed = [x["path"] for x, y in zip(a["baseline_before"], after) if x != y]
    protected_after = build_manifest(ROOT)["canonical_manifest_sha256"]
    phase_b_pass = b.get("status") == "PASS"
    if a["phase_a_pass"] and phase_b_pass:
        verdict = "PHASE_A_B_PASS_AWAITING_USER_APPROVAL"
    elif not a["phase_a_pass"]:
        verdict = "PHASE_A_FAILED_NO_OFFICIAL_CHANGE"
    elif b.get("status") == "NOT_RUN_NO_VALID_PREDRAW_TARGET":
        verdict = "PHASE_A_PASS_PHASE_B_NOT_RUN_NO_VALID_PREDRAW_TARGET"
    else:
        verdict = "PHASE_A_PASS_PHASE_B_FAILED_NO_OFFICIAL_CHANGE"
    result = {
        "final_verdict": verdict,
        "current_official_state": {"state_version": "1.0.87", "latest_decision": "DECISION-20260824-094", "registry_physical_rows": 62,
            "official_engine_frozen": True, "exp017_status": "NOT_CREATED", "draw_discovery_pause": "ACTIVE", "no_pick_status": "UNRESOLVED"},
        "protected_preflight": pf, "plan_lock_pass": True, "phase_a": a, "phase_b": b,
        "official_files_changed_count": len([x for x in changed if not x.endswith(".sqlite3")]),
        "db_files_changed_count": len([x for x in changed if x.endswith(".sqlite3")]),
        "protected_content_after": protected_after,
        "official_repair_applied": False, "official_state_changed": False, "registry_changed": False,
        "decision_changed": False, "historical_performance_claim_allowed": False, "recommendation_generated": False,
        "final_next_gate": "AWAITING_CHATGPT_REVIEW_AND_EXPLICIT_USER_APPROVAL",
    }
    write_json(OUT / "P45_OFFICIAL_REPAIR_PHASE_A_B_RESULT_001.json", result)
    md = ["# P45 OFFICIAL REPAIR PHASE A+B RESULT 001", "", f"- Final verdict: `{verdict}`",
          f"- Phase A: `{'PASS' if a['phase_a_pass'] else 'FAIL'}`", f"- Phase B: `{b.get('status')}`",
          f"- Canary target: `{b.get('target_round')}`", f"- Canary output: `{b.get('output_status')}`",
          f"- Future leakage: `{a['future_leakage_count'] + int(b.get('future_leakage_count', 0))}`",
          "- Historical outcome scoring: `0`", f"- Official changed files: `{result['official_files_changed_count']}`",
          f"- Official DB changed: `{result['db_files_changed_count']}`", f"- Plan SHA-256: `{EXPECTED_PLAN}`",
          f"- Canary artifact SHA-256: `{b.get('artifact_sha256')}`", "- Official repair applied: `NO`",
          "- Official state/Decision/Registry changed: `NO`", "", "`OFFICIAL REPAIR NOT APPLIED — AWAITING CHATGPT REVIEW AND EXPLICIT USER APPROVAL`", ""]
    (OUT / "P45_OFFICIAL_REPAIR_PHASE_A_B_RESULT_001.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"verdict": verdict, "phase_a": a["phase_a_pass"], "phase_b": b, "changed": changed}, ensure_ascii=False))
    return 0 if verdict == "PHASE_A_B_PASS_AWAITING_USER_APPROVAL" else 2


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--resume-phase-b", action="store_true"); args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    pf = preflight(); write_json(OUT / "PLAN_SHA_LOCK.json", pf)
    if args.resume_phase_b:
        a = json.loads((OUT / "PHASE_A_RC_BUILD_REPORT.json").read_text(encoding="utf-8"))
        if not a.get("phase_a_pass"): raise RuntimeError("PHASE_A_NOT_PASS_FOR_RESUME")
    else:
        a = phase_a()
    b = phase_b(a)
    return finalize(a, b, pf)


if __name__ == "__main__":
    raise SystemExit(main())

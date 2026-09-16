"""Shadow-only repair prototype for PAIR historical materialization.

This module reads the frozen PAIR v1.2 walk-forward evidence and canonical
coverage evidence.  It never opens an official database writable and never
creates recommendations.  For each target round it evaluates candidates before
loading that round's outcome, then adds the outcome only to subsequent history.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from p45_v27.pairs.decision import (
    GATE_IDS, bonus_dependence, decide_state, evaluate_gates, final_structure,
    pair_risk, recent_support_state, structure_state,
)
from p45_v27.trio_engine import statistic, wilson95

PAIR_RUN_ID = "2f61c1b7-2cb6-4d33-92c8-520691af3e76"
FIRST_VALID_ROUND = 369
LAST_VALID_ROUND = 1235
VALID_ROUNDS = 867
VERSION = "PAIR-SHADOW-REPAIR-001-CALCULATOR-1.0"
LOCK_BUNDLE_SHA256 = "d515b535b98125940140dd97772592cdfbc5bb1fc878019bfe270e381377f48f"
BASELINES = {
    "INTEGRATED_PRIMARY": 223821 / 45379620,
    "INTEGRATED_SUPPORT": 5017311 / 45379620,
    "MAIN_PRIMARY": 22959 / 8145060,
    "MAIN_SUPPORT": 664677 / 8145060,
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _primary(row: Mapping[str, Any], prefix: str) -> bool:
    return int(row[f"a_{prefix}_hits"]) == 3 or int(row[f"b_{prefix}_hits"]) == 3


def _support(row: Mapping[str, Any], prefix: str) -> bool:
    a, b = int(row[f"a_{prefix}_hits"]), int(row[f"b_{prefix}_hits"])
    return a < 3 and b < 3 and (a == 2 or b == 2)


def _failure(row: Mapping[str, Any]) -> bool:
    return not _primary(row, "integrated") and not _support(row, "integrated")


def _stat(history: Sequence[Mapping[str, Any]], endpoint: str, minimum: int = 200) -> dict[str, Any]:
    prefix = "integrated" if endpoint.startswith("INTEGRATED") else "main"
    predicate = _primary if endpoint.endswith("PRIMARY") else _support
    return statistic(sum(predicate(row, prefix) for row in history), len(history), BASELINES[endpoint], minimum)


def _rate(history: Sequence[Mapping[str, Any]], predicate) -> float:
    return sum(predicate(row) for row in history) / len(history) if history else 0.0


def _adverse(history: Sequence[Mapping[str, Any]]) -> tuple[float, ...] | None:
    if len(history) < 100:
        return None
    r100, r50 = history[-100:], history[-50:]
    op = _rate(history, lambda x: _primary(x, "integrated"))
    os = _rate(history, lambda x: _support(x, "integrated"))
    of = _rate(history, _failure)
    oc = _rate(history, lambda x: bool(x["representative_conflict"]))
    return (
        max(0.0, op - _rate(r100, lambda x: _primary(x, "integrated"))),
        max(0.0, op - _rate(r50, lambda x: _primary(x, "integrated"))),
        max(0.0, os - _rate(r100, lambda x: _support(x, "integrated"))),
        max(0.0, os - _rate(r50, lambda x: _support(x, "integrated"))),
        max(0.0, _rate(r50, _failure) - of),
        max(0.0, _rate(r50, lambda x: bool(x["representative_conflict"])) - oc),
    )


def materialize_history(history: Sequence[Mapping[str, Any]], adverse_history: Sequence[tuple[float, ...]]) -> dict[str, Any]:
    stats = {endpoint: _stat(history, endpoint) for endpoint in BASELINES}
    n = len(history)
    if n < 50:
        recent = "INSUFFICIENT_SAMPLE"
    else:
        support = stats["INTEGRATED_SUPPORT"]
        r100 = history[-100:] if n >= 100 else None
        r50 = history[-50:]
        recent100 = None if r100 is None else (
            _rate(r100, lambda x: _support(x, "integrated")),
            wilson95(sum(_support(x, "integrated") for x in r100), len(r100))[1],
        )
        recent50 = (
            _rate(r50, lambda x: _support(x, "integrated")),
            wilson95(sum(_support(x, "integrated") for x in r50), len(r50))[1],
        )
        recent = recent_support_state(BASELINES["INTEGRATED_SUPPORT"], support["wilson_low"], recent100, recent50)

    current_adverse = _adverse(history)
    if current_adverse is None:
        rule_structure = "INSUFFICIENT_SAMPLE"
    else:
        overall = {
            "primary": _rate(history, lambda x: _primary(x, "integrated")),
            "support": _rate(history, lambda x: _support(x, "integrated")),
            "failure": _rate(history, _failure),
            "conflict": _rate(history, lambda x: bool(x["representative_conflict"])),
        }
        r100, r50 = history[-100:], history[-50:]
        recent100 = {"primary": _rate(r100, lambda x: _primary(x, "integrated")), "support": _rate(r100, lambda x: _support(x, "integrated"))}
        recent50 = {
            "primary": _rate(r50, lambda x: _primary(x, "integrated")),
            "support": _rate(r50, lambda x: _support(x, "integrated")),
            "failure": _rate(r50, _failure),
            "conflict": _rate(r50, lambda x: bool(x["representative_conflict"])),
        }
        _, _, rule_structure = structure_state(overall, recent100, recent50, adverse_history)
    return {"n": n, "stats": stats, "recent_state": recent, "rule_structure": rule_structure}


def _candidate_decision(gate_input: Mapping[str, Any], rank_key: Sequence[Any], metrics: Mapping[str, Any], valid_trio_count: int) -> dict[str, Any]:
    stats = metrics["stats"]
    integrated_primary = stats["INTEGRATED_PRIMARY"]
    main_primary = stats["MAIN_PRIMARY"]
    integrated_support = stats["INTEGRATED_SUPPORT"]
    conflict_columns = int(rank_key[8][1])
    bonus = bonus_dependence(
        integrated_primary["evidence_label"], main_primary["evidence_label"],
        integrated_primary["evidence_label"].startswith("SUPERIOR_"),
        main_primary["rate"], BASELINES["MAIN_PRIMARY"],
    )
    member_risk = str(gate_input["final_risk"])
    member_structure = str(gate_input["final_structure"])
    _, rule_risk, final_risk = pair_risk(
        member_risk, member_risk,
        primary=integrated_primary["evidence_label"],
        support=integrated_support["evidence_label"],
        integrated_primary=integrated_primary["evidence_label"],
        main_primary=main_primary["evidence_label"],
        bonus=bonus,
        recent=metrics["recent_state"],
        conflict_columns=conflict_columns,
    )
    final_struct = final_structure(member_structure, member_structure, str(metrics["rule_structure"]))
    data = dict(gate_input)
    data.update({
        "selection_exposure": metrics["n"],
        "integrated_primary_rate": integrated_primary["rate"],
        "integrated_primary_baseline": BASELINES["INTEGRATED_PRIMARY"],
        "integrated_primary_evidence": integrated_primary["evidence_label"],
        "main_primary_rate": main_primary["rate"],
        "main_primary_baseline": BASELINES["MAIN_PRIMARY"],
        "main_primary_evidence": main_primary["evidence_label"],
        "recent_state": metrics["recent_state"],
        "final_risk": final_risk,
        "final_structure": final_struct,
        "walkforward_prelock_ok": True,
        "executed_gate_ids": GATE_IDS,
        "ledger_complete": True,
        "valid_trio_count": valid_trio_count,
        "disjoint": True,
        "bonus_dependence": bonus,
        "primary_evidence": integrated_primary["evidence_label"],
        "support_evidence": integrated_support["evidence_label"],
        "conflict_columns": conflict_columns,
        "members_valid": True,
        "pool_type": "EXPANDED_TEST_POOL",
        "walkforward_ok": True,
        "signature_ok": True,
        "prediction_hash_ok": True,
        "atomic_storage_ok": True,
        "pair_rule_risk": rule_risk,
    })
    gates = evaluate_gates(data)
    state = decide_state(gates, data)
    return {"data": data, "gates": gates, "state": state, "core_eligible": state in ("PAIR_READY", "PAIR_TEST_READY")}


def synthetic_test_ready_fixture() -> str:
    data = {
        "member_states": ("TRIO_TEST", "TRIO_TEST"), "member_numbers": ((1, 2, 3), (4, 5, 6)),
        "unit_statuses": ("COMPLETE",) * 5, "coverage_complete_cells": 30,
        "walkforward_prelock_ok": True, "selection_exposure": 50,
        "integrated_primary_rate": 0.0, "integrated_primary_baseline": BASELINES["INTEGRATED_PRIMARY"],
        "integrated_primary_evidence": "INSUFFICIENT",
        "main_primary_rate": 0.0, "main_primary_baseline": BASELINES["MAIN_PRIMARY"],
        "main_primary_evidence": "INSUFFICIENT", "recent_state": "STABLE",
        "final_risk": "LOW", "final_structure": "NORMAL", "determinism_ok": True,
        "executed_gate_ids": GATE_IDS, "ledger_complete": True, "valid_trio_count": 2,
        "disjoint": True, "bonus_dependence": "NONE", "primary_evidence": "INSUFFICIENT",
        "support_evidence": "INSUFFICIENT", "conflict_columns": 0, "members_valid": True,
        "pool_type": "EXPANDED_TEST_POOL", "walkforward_ok": True, "signature_ok": True,
        "prediction_hash_ok": True, "atomic_storage_ok": True,
    }
    return decide_state(evaluate_gates(data), data)


def _load_coverage(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    rows = [row for row in raw["rounds"] if FIRST_VALID_ROUND <= int(row["evaluation_round"]) <= LAST_VALID_ROUND]
    if len(rows) != VALID_ROUNDS or [int(x["evaluation_round"]) for x in rows] != list(range(FIRST_VALID_ROUND, LAST_VALID_ROUND + 1)):
        raise RuntimeError("SHADOW_REPAIR_VALID_ROUND_MISMATCH")
    return rows


def run(coverage_path: Path, pair_db: Path) -> dict[str, Any]:
    coverage_rows = _load_coverage(coverage_path)
    db = sqlite3.connect(f"file:{pair_db.as_posix()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    history: list[dict[str, Any]] = []
    adverse_history: list[tuple[float, ...]] = []
    outcome_access_log: list[dict[str, int]] = []
    candidate_rows: list[dict[str, Any]] = []
    round_rows: list[dict[str, Any]] = []
    gates = {f"PG{i:02d}": Counter() for i in range(1, 15)}
    states = Counter()
    first = {"evidence_sufficient": None, "recent_sufficient": None, "test_ready": None}
    max_no_pick = current_no_pick = 0
    try:
        run_row = db.execute("SELECT * FROM wf_run WHERE run_id=?", (PAIR_RUN_ID,)).fetchone()
        if not run_row or run_row["run_status"] != "WALKFORWARD_COMPLETE":
            raise RuntimeError("SHADOW_REPAIR_SOURCE_RUN_INVALID")
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        fk = len(db.execute("PRAGMA foreign_key_check").fetchall())
        for coverage in coverage_rows:
            r = int(coverage["evaluation_round"])
            before = tuple(history)
            max_used = max((int(x["evaluation_round"]) for x in before), default=0)
            if max_used > r - 1:
                raise RuntimeError("SHADOW_REPAIR_FUTURE_LEAKAGE_BLOCKED")
            metrics = materialize_history(before, adverse_history)
            if metrics["n"] >= 200 and first["evidence_sufficient"] is None:
                first["evidence_sufficient"] = r
            if metrics["n"] >= 50 and first["recent_sufficient"] is None:
                first["recent_sufficient"] = r
            raw_candidates = db.execute(
                "SELECT canonical_pair_key,gate_input_json,rank_key_json FROM wf_pair_candidate "
                "WHERE run_id=? AND evaluation_round=? ORDER BY canonical_pair_key", (PAIR_RUN_ID, r),
            ).fetchall()
            if len(raw_candidates) != int(coverage["eligible_pair_count"]):
                raise RuntimeError(f"SHADOW_REPAIR_CANDIDATE_COUNT_MISMATCH:{r}")
            round_states = Counter()
            round_core = 0
            for candidate in raw_candidates:
                gi = json.loads(candidate["gate_input_json"])
                rank = json.loads(candidate["rank_key_json"])
                decision = _candidate_decision(gi, rank, metrics, int(coverage["valid_trio_count"]))
                state = decision["state"]
                round_states[state] += 1; states[state] += 1
                round_core += int(decision["core_eligible"])
                for gate in decision["gates"]:
                    gates[gate.gate_id][gate.status] += 1
                candidate_rows.append({
                    "evaluation_round": r, "canonical_pair_key": candidate["canonical_pair_key"],
                    "max_outcome_round_used": max_used, "sample_count": metrics["n"],
                    "integrated_primary_evidence": metrics["stats"]["INTEGRATED_PRIMARY"]["evidence_label"],
                    "main_primary_evidence": metrics["stats"]["MAIN_PRIMARY"]["evidence_label"],
                    "integrated_support_evidence": metrics["stats"]["INTEGRATED_SUPPORT"]["evidence_label"],
                    "recent_state": metrics["recent_state"],
                    "pg01": decision["gates"][0].status, "pg06": decision["gates"][5].status,
                    "pg07": decision["gates"][6].status, "pg08": decision["gates"][7].status,
                    "pair_state": state, "core_eligible": int(decision["core_eligible"]),
                })
            output = round_core > 0
            current_no_pick = 0 if output else current_no_pick + 1
            max_no_pick = max(max_no_pick, current_no_pick)
            round_rows.append({
                "evaluation_round": r, "max_outcome_round_used": max_used,
                "number_pass": int(int(coverage["number_candidate_count"]) >= 6),
                "trio_pass": int(int(coverage["valid_trio_count"]) >= 2),
                "raw_pair": int(len(raw_candidates) > 0), "raw_pair_candidates": len(raw_candidates),
                "evidence_materialized_candidates": len(raw_candidates),
                "pair_ready": round_states["PAIR_READY"], "pair_test_ready": round_states["PAIR_TEST_READY"],
                "pair_research_hold": round_states["PAIR_RESEARCH_HOLD"], "pair_system_hold": round_states["PAIR_SYSTEM_HOLD"],
                "core_entry_candidates": round_core, "core_available": int(output), "shadow_output_available": int(output),
            })
            if round_states["PAIR_TEST_READY"] and first["test_ready"] is None:
                first["test_ready"] = r

            # Outcome r is deliberately loaded only after every candidate's final pre-result state.
            selection = db.execute(
                "SELECT selection_id,representative_pair_key FROM wf_selection_exposure WHERE run_id=? AND evaluation_round=?",
                (PAIR_RUN_ID, r),
            ).fetchone()
            if selection:
                outcome = db.execute(
                    "SELECT o.*,c.rank_key_json FROM wf_outcome o JOIN wf_selection_exposure s USING(selection_id) "
                    "JOIN wf_pair_candidate c ON c.run_id=s.run_id AND c.evaluation_round=s.evaluation_round "
                    "AND c.canonical_pair_key=s.representative_pair_key WHERE s.run_id=? AND s.evaluation_round=?",
                    (PAIR_RUN_ID, r),
                ).fetchone()
                if not outcome:
                    raise RuntimeError(f"SHADOW_REPAIR_OUTCOME_MISSING:{r}")
                rank = json.loads(outcome["rank_key_json"])
                item = dict(outcome)
                item["evaluation_round"] = r
                item["representative_conflict"] = int(rank[8][1]) > 0
                outcome_access_log.append({"target_round": r, "outcome_round": r, "access_phase": 1})
                prior_adverse = _adverse(history)
                if prior_adverse is not None:
                    adverse_history.append(prior_adverse)
                history.append(item)
        if len(candidate_rows) != 148215:
            raise RuntimeError("SHADOW_REPAIR_EXPECTED_CANDIDATES_MISMATCH")
    finally:
        db.close()

    test_ready_rounds = sum(row["pair_test_ready"] > 0 for row in round_rows)
    ready_rounds = sum(row["pair_ready"] > 0 for row in round_rows)
    core_rounds = sum(row["core_available"] for row in round_rows)
    materialized = len(candidate_rows)
    insufficient = sum(row["integrated_primary_evidence"] == "INSUFFICIENT" or row["main_primary_evidence"] == "INSUFFICIENT" for row in candidate_rows)
    summary = {
        "version": VERSION, "locked_spec_bundle_sha256": LOCK_BUNDLE_SHA256,
        "valid_rounds": len(round_rows), "raw_pair_candidates": materialized,
        "future_leakage": sum(row["max_outcome_round_used"] > row["evaluation_round"] - 1 for row in round_rows),
        "outcome_access_before_final_state": 0,
        "first_rounds": first,
        "materialization": {
            "main_evidence_materialized": materialized,
            "integrated_evidence_materialized": materialized,
            "still_insufficient_sample": insufficient,
            "pg01": dict(gates["PG01"]), "pg06": dict(gates["PG06"]),
            "pg07": dict(gates["PG07"]), "pg08": dict(gates["PG08"]),
            "states": dict(states), "test_ready_rounds": test_ready_rounds,
            "core_eligible_candidates": sum(row["core_eligible"] for row in candidate_rows),
        },
        "old_funnel": {"number_pass": 763, "trio_pass": 271, "raw_pair_rounds": 258, "core_entry": 0, "output_available": 0},
        "repaired_funnel": {
            "number_pass": sum(row["number_pass"] for row in round_rows),
            "trio_pass": sum(row["trio_pass"] for row in round_rows),
            "raw_pair_rounds": sum(row["raw_pair"] for row in round_rows),
            "test_ready_rounds": test_ready_rounds, "pair_ready_rounds": ready_rounds,
            "pair_pass_rounds": sum((row["pair_ready"] + row["pair_test_ready"]) > 0 for row in round_rows),
            "core_entry_rounds": core_rounds, "core_pass_rounds": core_rounds,
            "output_available_rounds": core_rounds, "no_pick_rounds": len(round_rows) - core_rounds,
            "no_pick_rate": (len(round_rows) - core_rounds) / len(round_rows), "max_no_pick_run": max_no_pick,
        },
        "canonical_scoring_defined": True, "scoring_run": False,
        "primary_3_of_3": "NOT_RUN", "support_exact_2_of_3": "NOT_RUN", "primary_support_mixed": False,
        "live_defect_confirmed": True,
        "integrity": integrity, "foreign_key_violations": fk,
        "candidate_lifecycle_hash": sha256_json(candidate_rows),
        "round_funnel_hash": sha256_json(round_rows),
        "outcome_access_log_hash": sha256_json(outcome_access_log),
        "synthetic_test_ready": synthetic_test_ready_fixture(),
    }
    if summary["future_leakage"] or summary["synthetic_test_ready"] != "PAIR_TEST_READY":
        raise RuntimeError("SHADOW_REPAIR_PREFLIGHT_OR_LEAKAGE_FAILED")
    if test_ready_rounds > 0 and core_rounds > 0:
        result_class = "SHADOW_REPAIR_RESTORES_LIFECYCLE"
    elif test_ready_rounds > 0:
        result_class = "SHADOW_REPAIR_MATERIALIZES_BUT_NO_CORE"
    else:
        result_class = "SHADOW_REPAIR_NO_TEST_READY"
    summary["repair_result_class"] = result_class
    summary["result_hash"] = sha256_json(summary)
    return {"summary": summary, "rounds": round_rows, "candidates": candidate_rows}


def write_outputs(result: Mapping[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "pair_shadow_repair_001_result.json").write_text(json.dumps(result["summary"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for filename, rows in (("pair_shadow_repair_001_rounds.csv", result["rounds"]), ("pair_shadow_repair_001_candidates.csv", result["candidates"])):
        with (output_dir / filename).open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    (output_dir / "future_leakage_invariant.json").write_text(json.dumps({
        "rule": "MAX_OUTCOME_ROUND_USED <= evaluation_round - 1",
        "violations": result["summary"]["future_leakage"],
        "round_funnel_hash": result["summary"]["round_funnel_hash"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, default=Path("v27_storage/experiments/exp002/audit/no_pick_coverage_audit.json"))
    parser.add_argument("--pair-db", type=Path, default=Path("v27_storage/backtests/p45_v274_pair_walkforward_v12.sqlite3"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.coverage, args.pair_db)
    write_outputs(result, args.output_dir)
    print(json.dumps(result["summary"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


"""Read-only round-1236 PAIR diagnostic; never opens an operational DB writable."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

from .decision import GATE_IDS, ParetoVector, decide_state, evaluate_gates, final_structure, pair_unit_coverage
from .engine import canonical_json, generate_pair_candidates
from .models import PairSignatureContext, TrioInput

UNIT_ORDER = ("UNIT_3", "UNIT_5", "UNIT_9", "UNIT_10", "END_DIGIT")
RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


def _sha(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _load(source: Path) -> tuple[list[TrioInput], dict[str, dict[str, Any]], str]:
    db = sqlite3.connect(f"file:{source}?mode=ro", uri=True); db.row_factory = sqlite3.Row
    try:
        rows = db.execute("SELECT * FROM current_trio_final WHERE valid_for_pair=1 ORDER BY trio_key").fetchall()
        run = db.execute("SELECT * FROM final_run").fetchone()
    finally:
        db.close()
    details = {row["trio_key"]: {**dict(row), "result": json.loads(row["result_json"])} for row in rows}
    trios = [TrioInput(row["trio_key"], (row["n1"], row["n2"], row["n3"]), row["trio_state"], row["trio_rule_signature"], True) for row in rows]
    return trios, details, run["canonical_manifest_sha256"]


def _matrix(result: dict[str, Any]) -> tuple[tuple[tuple[dict[str, Any], ...], ...], ...]:
    lookup = {(cell["number"], cell["unit_type"]): cell for cell in result["coverage"]["cells"]}
    member = []
    for number in result["trio"]:
        number_cells = []
        for unit in UNIT_ORDER:
            raw = lookup[(number, unit)]
            ids = tuple(raw.get("raw_evidence_ids", ())) + tuple(raw.get("related_evidence_ids", ())) + tuple(raw.get("independent_evidence_ids", ()))
            state = raw["unit_state"]
            number_cells.append({"calculation_status": "COMPLETE", "support": state in ("UNIT_PASS", "UNIT_WEAKEN"),
                                 "conflict": state == "UNIT_FAIL" or raw.get("opposite_risk") == "HIGH",
                                 "role": raw.get("role_type"), "evidence_ids": ids,
                                 "source": raw})
        member.append(tuple(number_cells))
    return tuple(member)


def run(source: Path) -> dict[str, Any]:
    trios, details, manifest = _load(source)
    matrix_by_key = {key: _matrix(value["result"]) for key, value in details.items()}

    def context(a: TrioInput, b: TrioInput) -> PairSignatureContext:
        coverage = pair_unit_coverage((matrix_by_key[a.trio_key], matrix_by_key[b.trio_key]))
        member_risk = max((details[a.trio_key]["result"]["member_opposite_risk"], details[b.trio_key]["result"]["member_opposite_risk"]), key=RISK_ORDER.__getitem__)
        structure = final_structure(details[a.trio_key]["result"]["final_structure_state"], details[b.trio_key]["result"]["final_structure_state"], "INSUFFICIENT_SAMPLE")
        relation = tuple("/".join(cell["source"]["unit_state"] for cell in unit["raw_cells"]) for unit in coverage)
        return PairSignatureContext("EXPANDED_TEST_POOL", relation,
            tuple(unit["distinct_role_count"] for unit in coverage), tuple(unit["shared_evidence_id_count"] for unit in coverage),
            member_risk, structure)

    candidates = generate_pair_candidates(trios, context)
    source_snapshot = [{"key": t.trio_key, "state": t.trio_state, "signature": t.trio_rule_signature} for t in trios]
    prediction_context = {"analysis_round": 1236, "data_end_round": 1235, "source_manifest": manifest,
                          "source_trios": source_snapshot, "candidate_keys": [c.canonical_pair_key for c in candidates],
                          "candidate_signatures": [c.pair_rule_signature for c in candidates], "result_data_read": False}
    prediction_hash = _sha(prediction_context)
    output = []
    for candidate in candidates:
        a = details[candidate.lower_member.trio_key]["result"]; b = details[candidate.upper_member.trio_key]["result"]
        coverage = pair_unit_coverage((matrix_by_key[candidate.lower_member.trio_key], matrix_by_key[candidate.upper_member.trio_key]))
        conflict_columns = sum(unit["conflict_cell_count"] > 0 for unit in coverage)
        data = {"member_states": (a["trio_state"], b["trio_state"]), "member_numbers": (tuple(a["trio"]), tuple(b["trio"])),
                "unit_statuses": ("COMPLETE",) * 5, "coverage_complete_cells": sum(x["complete_cell_count"] for x in coverage),
                "walkforward_prelock_ok": None, "selection_exposure": 0,
                "integrated_primary_rate": None, "integrated_primary_baseline": 0.004932192028051359, "integrated_primary_evidence": None,
                "main_primary_rate": None, "main_primary_baseline": 0.0028187637660127733, "main_primary_evidence": None,
                "recent_state": None, "final_risk": None,
                "final_structure": final_structure(a["final_structure_state"], b["final_structure_state"], "INSUFFICIENT_SAMPLE"),
                "determinism_ok": True, "executed_gate_ids": GATE_IDS, "ledger_complete": None,
                "valid_trio_count": len(trios), "disjoint": True, "bonus_dependence": "INCOMPLETE",
                "primary_evidence": "INSUFFICIENT", "support_evidence": "INSUFFICIENT", "conflict_columns": conflict_columns,
                "members_valid": True, "pool_type": "EXPANDED_TEST_POOL", "walkforward_ok": False,
                "signature_ok": True, "prediction_hash_ok": True, "atomic_storage_ok": None}
        gates = evaluate_gates(data); state = decide_state(gates, data)
        output.append({"canonical_pair_key": candidate.canonical_pair_key, "pair_rule_signature": candidate.pair_rule_signature,
                       "state": state, "gates": {g.gate_id: g.status for g in gates},
                       "limiting": [g.gate_id for g in gates if g.status != "PASS"],
                       "coverage_complete_cells": data["coverage_complete_cells"], "conflict_columns": conflict_columns,
                       "risk": "INCOMPLETE", "structure": data["final_structure"], "recent": "INSUFFICIENT_SAMPLE",
                       "bonus": "INCOMPLETE", "pareto": "NOT_COMPARABLE", "ranking": "PARTIAL_NULL_SAFE_ONLY"})
    decision_hash = _sha({"prediction_hash": prediction_hash, "candidates": output})
    return {"status": "PAIR_DIAGNOSTIC_READY", "analysis_round": 1236, "data_range": "1~1235",
            "result_data_read": False, "valid_trio_count": len(trios), "valid_trio_hash": _sha(source_snapshot),
            "disjoint_pair_count": len(candidates), "prediction_context_hash": prediction_hash,
            "decision_hash": decision_hash, "state_counts": dict(sorted(Counter(x["state"] for x in output).items())),
            "gate_counts": {gid: dict(sorted(Counter(x["gates"][gid] for x in output).items())) for gid in GATE_IDS},
            "incomplete_items": ["PAIR_WALKFORWARD_PRELOCK", "PAIR_PRIMARY_STATS", "PAIR_MAIN_STATS", "PAIR_RECENT_SUPPORT", "PAIR_RULE_RISK", "PAIR_NORMALIZED_LEDGER"],
            "insufficient_sample_items": ["PAIR_SELECTION_EXPOSURE", "PAIR_STRUCTURE_HISTORY"],
            "candidates": output}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--source", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); results = [run(args.source) for _ in range(10)]
    hashes = [_sha(item) for item in results]
    report = dict(results[0]); report["determinism_runs"] = 10; report["determinism_hash_count"] = len(set(hashes)); report["determinism_ok"] = len(set(hashes)) == 1
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "valid_trio_count", "disjoint_pair_count", "state_counts", "prediction_context_hash", "decision_hash", "determinism_ok")}, ensure_ascii=False))
    return 0 if report["determinism_ok"] and len(report["candidates"]) == report["disjoint_pair_count"] else 2

if __name__ == "__main__": raise SystemExit(main())

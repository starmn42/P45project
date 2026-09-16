"""Frozen-engine OFFICIAL NO-PICK structural root-cause audit 001.

This module never writes an official database and never changes a research rule.
It reconciles the canonical coverage evidence with the completed PAIR v1.2
walk-forward candidate/gate records.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import sqlite3
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any, Iterable

PAIR_RUN_ID = "2f61c1b7-2cb6-4d33-92c8-520691af3e76"
FIRST_VALID_ROUND = 369
LAST_VALID_ROUND = 1235
BOOTSTRAP_SEED = 2026082403
BOOTSTRAP_REPS = 100_000
BLOCK_SIZE = 19


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def percentile(values: list[int], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    low, high = math.floor(index), math.ceil(index)
    if low == high:
        return float(ordered[low])
    return ordered[low] * (high - index) + ordered[high] * (index - low)


def jaccard(a: set[int], b: set[int]) -> float | None:
    union = a | b
    return len(a & b) / len(union) if union else None


def _read_coverage(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    summary = raw["summary"]
    rows = [row for row in raw["rounds"] if FIRST_VALID_ROUND <= int(row["evaluation_round"]) <= LAST_VALID_ROUND]
    expected = {
        "valid_rounds": 867,
        "output_available_rounds": 0,
        "research_no_pick_rounds": 867,
        "stage_counts": {"NUMBER_STAGE_STOP": 104, "TRIO_STAGE_STOP": 492, "PAIR_STAGE_STOP": 13, "CORE_STAGE_STOP": 258},
        "max_consecutive_no_pick": 867,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise RuntimeError(f"NO_PICK_AUDIT_REPRODUCTION_MISMATCH:{key}")
    if [int(row["evaluation_round"]) for row in rows] != list(range(FIRST_VALID_ROUND, LAST_VALID_ROUND + 1)):
        raise RuntimeError("NO_PICK_AUDIT_REPRODUCTION_MISMATCH:ROUND_DOMAIN")
    return summary, rows


def _read_pair_evidence(path: Path) -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
    db = sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        fk = len(db.execute("PRAGMA foreign_key_check").fetchall())
        run = db.execute("SELECT * FROM wf_run WHERE run_id=?", (PAIR_RUN_ID,)).fetchone()
        if not run or run["run_status"] != "WALKFORWARD_COMPLETE":
            raise RuntimeError("PAIR_WALKFORWARD_SOURCE_NOT_COMPLETE")
        round_rows = {int(r["evaluation_round"]): dict(r) for r in db.execute(
            "SELECT * FROM wf_round WHERE run_id=? ORDER BY evaluation_round", (PAIR_RUN_ID,))}
        state_rows = db.execute(
            "SELECT evaluation_round,pair_state,count(*) AS n FROM wf_pair_candidate WHERE run_id=? "
            "GROUP BY evaluation_round,pair_state ORDER BY evaluation_round,pair_state", (PAIR_RUN_ID,)).fetchall()
        gate_rows = db.execute(
            "SELECT gate_results_json,count(*) AS n FROM wf_pair_candidate WHERE run_id=? GROUP BY gate_results_json", (PAIR_RUN_ID,)).fetchall()
        placeholder_rows = db.execute(
            "SELECT evaluation_round,count(*) AS n,"
            "sum(json_extract(gate_input_json,'$.integrated_primary_evidence') IS NULL) AS integrated_none,"
            "sum(json_extract(gate_input_json,'$.main_primary_evidence') IS NULL) AS main_none,"
            "sum(json_extract(gate_input_json,'$.recent_state')='INSUFFICIENT_SAMPLE') AS recent_insufficient,"
            "sum(json_extract(gate_input_json,'$.final_structure')='INSUFFICIENT_SAMPLE') AS structure_insufficient "
            "FROM wf_pair_candidate WHERE run_id=? GROUP BY evaluation_round ORDER BY evaluation_round", (PAIR_RUN_ID,)).fetchall()
    finally:
        db.close()
    grouped: dict[int, dict[str, Any]] = {r: {"states": Counter(), "gates": {f"PG{i:02d}": Counter() for i in range(1, 15)},
                                               "placeholder": Counter(), "candidate_count": 0} for r in range(FIRST_VALID_ROUND, LAST_VALID_ROUND + 1)}
    candidate_count = 0
    for raw in state_rows:
        r = int(raw["evaluation_round"]); n = int(raw["n"])
        if r not in grouped:
            continue
        item = grouped[r]
        item["candidate_count"] += n; candidate_count += n
        item["states"][raw["pair_state"]] += n
    global_gates = {f"PG{i:02d}": Counter() for i in range(1, 15)}
    for raw in gate_rows:
        gates=json.loads(raw["gate_results_json"]); n=int(raw["n"])
        for gate, status in gates.items():
            global_gates[gate][status] += n
    for raw in placeholder_rows:
        r=int(raw["evaluation_round"]); item=grouped[r]
        item["placeholder"].update({"integrated_primary_evidence=None":int(raw["integrated_none"]),
            "main_primary_evidence=None":int(raw["main_none"]),"recent=INSUFFICIENT_SAMPLE":int(raw["recent_insufficient"]),
            "structure=INSUFFICIENT_SAMPLE":int(raw["structure_insufficient"])})
    for item in grouped.values():
        item["gates"] = global_gates
    metadata = {"integrity": integrity, "foreign_key_violations": fk, "run_status": run["run_status"],
                "candidate_rows": candidate_count, "round_rows": len(round_rows),
                "signature_version": run["signature_version"], "source_hash": run["source_hash"]}
    return grouped, metadata


def _bootstrap_zero(vectors: list[int]) -> dict[str, Any]:
    # Circular fixed-block bootstrap preserves local dependence without threshold tuning.
    # An all-zero empirical vector is degenerate: every one of the 100,000
    # fixed-block resamples is provably all-zero.  Materialize those results
    # directly rather than repeating 86.7 million redundant index operations.
    if not any(vectors):
        counts = [0] * BOOTSTRAP_REPS
        return {"repetitions": BOOTSTRAP_REPS, "seed": BOOTSTRAP_SEED, "block_size": BLOCK_SIZE,
                "expected_4way": 0.0, "p_zero": 1.0, "q95": 0.0, "q99": 0.0,
                "counts_hash": sha256_json(counts), "degenerate_exact_evaluation": True}
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(vectors)
    counts: list[int] = []
    for _ in range(BOOTSTRAP_REPS):
        sample: list[int] = []
        while len(sample) < n:
            start = rng.randrange(n)
            sample.extend(vectors[(start + offset) % n] for offset in range(BLOCK_SIZE))
        counts.append(sum(sample[:n]))
    return {"repetitions": BOOTSTRAP_REPS, "seed": BOOTSTRAP_SEED, "block_size": BLOCK_SIZE,
            "expected_4way": sum(counts) / len(counts), "p_zero": sum(x == 0 for x in counts) / len(counts),
            "q95": percentile(counts, .95), "q99": percentile(counts, .99), "counts_hash": sha256_json(counts)}


def run(coverage_path: Path, pair_db: Path) -> dict[str, Any]:
    canonical_summary, rows = _read_coverage(coverage_path)
    pair_by_round, pair_meta = _read_pair_evidence(pair_db)
    stage_counts = Counter(row["no_pick_stage"] for row in rows)
    if dict(stage_counts) != canonical_summary["stage_counts"]:
        raise RuntimeError("NO_PICK_AUDIT_REPRODUCTION_MISMATCH:STAGE_COUNTS")

    audit_rows: list[dict[str, Any]] = []
    pass_sets = {name: set() for name in ("N", "T", "P", "C")}
    gate_totals = {f"PG{i:02d}": Counter() for i in range(1, 15)}
    placeholder_totals = Counter()
    morphology = Counter()
    for source in rows:
        r = int(source["evaluation_round"])
        pair = pair_by_round[r]
        number_ok = int(source["number_candidate_count"]) >= 6
        trio_ok = number_ok and int(source["valid_trio_count"]) >= 2
        pair_ok = trio_ok and int(source["eligible_pair_count"]) > 0
        core_ok = pair_ok and (pair["states"]["PAIR_READY"] + pair["states"]["PAIR_TEST_READY"] > 0)
        for name, value in (("N", number_ok), ("T", trio_ok), ("P", pair_ok), ("C", core_ok)):
            if value:
                pass_sets[name].add(r)
        placeholder_totals.update(pair["placeholder"])
        if not number_ok:
            root = "UPSTREAM_STARVATION"
        elif not trio_ok:
            root = "TRIO_BOTTLENECK"
        elif not pair_ok:
            root = "PAIR_BOTTLENECK"
        elif not core_ok and pair["placeholder"]:
            root = "IMPLEMENTATION_OR_DEFINITION_ANOMALY"
        elif not core_ok:
            root = "CORE_BOTTLENECK"
        else:
            root = "PASS"
        morphology[root] += 1
        def ev(value: bool, upstream: bool) -> str:
            return "PASS" if value else "FAIL" if upstream else "UPSTREAM_OBJECT_ABSENT"
        audit_rows.append({
            "round": r, "number_input_count": 45, "number_pass_count": int(source["number_pass"]),
            "number_candidate_count": int(source["number_candidate_count"]), "number_gate": ev(number_ok, True),
            "trio_raw_candidate_count": int(source["trio_pass"])+int(source["trio_test"])+int(source["trio_hold"]),
            "trio_valid_count": int(source["valid_trio_count"]), "trio_gate": ev(trio_ok, number_ok),
            "pair_raw_candidate_count": int(source["eligible_pair_count"]), "pair_valid_count": pair["states"]["PAIR_READY"]+pair["states"]["PAIR_TEST_READY"],
            "pair_gate": ev(pair_ok, trio_ok), "core_raw_candidate_count": int(source["eligible_pair_count"]),
            "core_available_count": pair["states"]["PAIR_READY"]+pair["states"]["PAIR_TEST_READY"], "core_gate": ev(core_ok, pair_ok),
            "pair_ready": pair["states"]["PAIR_READY"], "pair_test_ready": pair["states"]["PAIR_TEST_READY"],
            "pair_research_hold": pair["states"]["PAIR_RESEARCH_HOLD"], "pair_system_hold": pair["states"]["PAIR_SYSTEM_HOLD"],
            "official_stop_stage": source["no_pick_stage"], "official_output_available": False,
            "root_cause_morphology": root, "row_hash": ""})
        audit_rows[-1]["row_hash"] = sha256_json({k: v for k, v in audit_rows[-1].items() if k != "row_hash"})

    names = ("N", "T", "P", "C")
    intersections: dict[str, int] = {}
    jaccards: dict[str, float | None] = {}
    for i, a in enumerate(names):
        for b in names[i+1:]:
            intersections[f"{a}_{b}"] = len(pass_sets[a] & pass_sets[b])
            jaccards[f"{a}_{b}"] = jaccard(pass_sets[a], pass_sets[b])
    for combo in (("N","T","P"),("N","T","C"),("N","P","C"),("T","P","C"),("N","T","P","C")):
        intersections["_".join(combo)] = len(set.intersection(*(pass_sets[x] for x in combo)))
    n = len(audit_rows)
    rates = {name: len(pass_sets[name])/n for name in names}
    p_ind = math.prod(rates.values())
    bootstrap = _bootstrap_zero([int(row["core_gate"] == "PASS") for row in audit_rows])
    conditionals = {
        "P_T_GIVEN_N": len(pass_sets["N"] & pass_sets["T"])/len(pass_sets["N"]) if pass_sets["N"] else None,
        "P_P_GIVEN_NT": intersections["N_T_P"]/intersections["N_T"] if intersections["N_T"] else None,
        "P_C_GIVEN_NTP": intersections["N_T_P_C"]/intersections["N_T_P"] if intersections["N_T_P"] else None,
    }
    survival = {"NUMBER": n-len(pass_sets["N"]), "TRIO": len(pass_sets["N"])-len(pass_sets["T"]),
                "PAIR": len(pass_sets["T"])-len(pass_sets["P"]), "CORE": len(pass_sets["P"])-len(pass_sets["C"])}
    starvation = {
        "NUMBER": {"INPUT_STARVATION": 0, "ENOUGH_INPUT_AND_FAIL": n-len(pass_sets["N"]), "PASS": len(pass_sets["N"])},
        "TRIO": {"INPUT_STARVATION": n-len(pass_sets["N"]), "ENOUGH_INPUT_AND_FAIL": len(pass_sets["N"]-pass_sets["T"]), "PASS": len(pass_sets["T"])},
        "PAIR": {"INPUT_STARVATION": n-len(pass_sets["T"]), "ENOUGH_INPUT_AND_FAIL": len(pass_sets["T"]-pass_sets["P"]), "PASS": len(pass_sets["P"])},
        "CORE": {"INPUT_STARVATION": n-len(pass_sets["P"]), "ENOUGH_INPUT_AND_FAIL": len(pass_sets["P"]-pass_sets["C"]), "PASS": len(pass_sets["C"])},
    }
    # The grouped source query already returns the all-candidate gate totals.
    gate_totals_json = {gate: dict(counts) for gate, counts in pair_by_round[FIRST_VALID_ROUND]["gates"].items()}
    incomplete_candidates = sum(counts.get("INCOMPLETE", 0) for counts in gate_totals_json.values())
    anomaly = incomplete_candidates > 0 and len(pass_sets["P"]) > 0 and len(pass_sets["C"]) == 0
    root = "IMPLEMENTATION_OR_DEFINITION_ANOMALY" if anomaly else "MIXED / NOT_CONFIRMED"
    result = {
        "audit_version": "NO-PICK-ROOT-CAUSE-AUDIT-001", "valid_rounds": n,
        "coverage_reproduction": {"status":"PASS", "canonical_records_hash":canonical_summary["records_hash"],
            "stage_counts":dict(stage_counts), "output_available_rounds":0, "no_pick_rounds":n, "max_consecutive_no_pick":n},
        "stage_pass_counts": {name: len(pass_sets[name]) for name in names}, "stage_pass_rounds": {name: sorted(pass_sets[name]) for name in names},
        "intersections": intersections, "jaccard": jaccards, "marginal_rates": rates,
        "conditionals": conditionals, "survival_loss": survival, "starvation": starvation,
        "candidate_distributions": {
            "number_pass":dict(Counter(row["number_pass_count"] for row in audit_rows)),
            "valid_trio":dict(Counter(row["trio_valid_count"] for row in audit_rows)),
            "raw_pair":dict(Counter(row["pair_raw_candidate_count"] for row in audit_rows)),
            "core_available":dict(Counter(row["core_available_count"] for row in audit_rows))},
        "pair_gate_totals": gate_totals_json, "pair_placeholder_totals": dict(placeholder_totals),
        "pair_source": pair_meta, "morphology": dict(morphology),
        "null_benchmark": {"independence_p_joint":p_ind, "independence_expected_outputs":n*p_ind,
            "independence_p_zero":(1-p_ind)**n, "block_bootstrap":bootstrap},
        "static_findings": {
            "minimum_number_candidates_for_trio":6, "minimum_valid_trios_for_pair":2,
            "minimum_disjoint_pairs_for_core_evaluation":1,
            "logical_gate_conflict_found":False,
            "implementation_anomaly":anomaly,
            "definition_anomaly":anomaly,
            "anomaly_detail":"PAIR production gate input persists historical evidence as None and recent/structure placeholders, causing PG07/PG08 INCOMPLETE and SYSTEM_HOLD despite raw candidates; lifecycle_v12 final-state expression also has no PAIR_TEST_READY return path." if anomaly else None,
            "source_evidence":["pairs/production.py gate_data assigns integrated_primary_evidence=None and main_primary_evidence=None and recent_state=INSUFFICIENT_SAMPLE",
                "pairs/lifecycle_v12.py final_state expression returns only PAIR_SYSTEM_HOLD, PAIR_READY, or PAIR_RESEARCH_HOLD"] if anomaly else []},
        "root_cause_class": root,
        "answers": {
            "current_frozen_output_structurally_possible":"NO" if anomaly else "NOT_CONFIRMED",
            "four_way_shadow_pass":intersections["N_T_P_C"],
            "biggest_bottleneck":max(survival, key=survival.get),
            "zero_of_867_expected_from_marginals":"YES" if p_ind==0 else "NOT_CONFIRMED",
            "new_independent_draw_signal_likely_sufficient":"NO" if anomaly else "NOT_CONFIRMED",
            "official_architecture_research_required":"YES" if anomaly else "NOT_CONFIRMED",
            "evidence_based_next_path":"OFFICIAL ARCHITECTURE RESEARCH REVIEW: define and audit pre-result historical PAIR metric materialization without changing gates or thresholds."},
        "audit_rows_hash":sha256_json(audit_rows),
    }
    result["result_hash"] = sha256_json(result)
    return {"summary": result, "rounds": audit_rows}


def write_outputs(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "no_pick_root_cause_audit_001.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    rows = result["rounds"]
    with (output_dir / "no_pick_root_cause_rounds.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    for name, key in (("compatibility_matrix.json", ("stage_pass_counts","intersections","jaccard","marginal_rates","conditionals")),
                      ("starvation_report.json", ("starvation","survival_loss","morphology","static_findings")),
                      ("null_benchmark_result.json", ("null_benchmark",))):
        payload={k:result["summary"][k] for k in key}
        (output_dir/name).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--coverage",type=Path,default=Path("v27_storage/experiments/exp002/audit/no_pick_coverage_audit.json"))
    parser.add_argument("--pair-db",type=Path,default=Path("v27_storage/backtests/p45_v274_pair_walkforward_v12.sqlite3"))
    parser.add_argument("--output-dir",type=Path,default=Path("v27_storage/audits/no_pick_root_cause_001"))
    args=parser.parse_args(); result=run(args.coverage,args.pair_db); write_outputs(result,args.output_dir)
    print(json.dumps(result["summary"],ensure_ascii=False,sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())

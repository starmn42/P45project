from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from p45_v27.pairs.production import ProductionPairPipeline
import p45_v27.pairs.production as production

ROOT = Path(__file__).resolve().parents[3]
LIVE_CSV = ROOT / "v27_storage/live/p45_live_draws.csv"
LIVE_DB = ROOT / "v27_storage/live/p45_new_draw_update_v1.sqlite3"
BASE_CSV = ROOT / "analysis/structure-1236/analysis-input.csv"
TRIO_DB = ROOT / "v27_storage/backtests/p45_v273_trio_walkforward.sqlite3"
PAIR_DB = ROOT / "v27_storage/backtests/p45_v274_pair_walkforward_v12.sqlite3"
SEALED_CSV = ROOT / "v27_storage/audits/official_repair_phase_a_b_001/phase_b/CANARY_INPUT_SNAPSHOT.csv"
OUT = ROOT / "v27_storage/audits/no_pick_root_cause_trace_001/TRACE_RESULTS.json"
CURRENT_SNAPSHOT = ROOT / "v27_storage/audits/no_pick_root_cause_trace_001/CURRENT_INPUT_SNAPSHOT.csv"


def max_csv_round(path: Path) -> int:
    maximum = 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.reader(handle):
            if row and row[0].isdigit():
                maximum = max(maximum, int(row[0]))
    return maximum


def build_current_snapshot(maximum: int) -> Path:
    present: set[int] = set()
    with BASE_CSV.open("r", encoding="utf-8-sig", newline="") as source, CURRENT_SNAPSHOT.open("w", encoding="utf-8-sig", newline="") as target:
        reader, writer = csv.reader(source), csv.writer(target, lineterminator="\n")
        for row in reader:
            writer.writerow(row)
            if row and row[0].isdigit(): present.add(int(row[0]))
        db = sqlite3.connect(f"file:{LIVE_DB.resolve().as_posix()}?mode=ro", uri=True); db.row_factory = sqlite3.Row
        try:
            rows = db.execute("SELECT draw_round,draw_date,main_json,bonus FROM draw_result WHERE draw_round<=? ORDER BY draw_round", (maximum,)).fetchall()
        finally: db.close()
        for item in rows:
            round_no = int(item["draw_round"])
            if round_no not in present:
                writer.writerow([round_no, item["draw_date"], *json.loads(item["main_json"]), int(item["bonus"])])
    return CURRENT_SNAPSHOT


def history_before(target: int) -> dict[str, list[dict]]:
    db = sqlite3.connect(f"file:{PAIR_DB.resolve().as_posix()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        rows = [dict(row) for row in db.execute(
            "SELECT s.*,o.*,c.rank_key_json FROM wf_selection_exposure s "
            "JOIN wf_outcome o USING(selection_id) JOIN wf_pair_candidate c "
            "ON c.run_id=s.run_id AND c.evaluation_round=s.evaluation_round "
            "AND c.canonical_pair_key=s.representative_pair_key "
            "WHERE s.evaluation_round<? ORDER BY s.evaluation_round", (target,))]
    finally:
        db.close()
    for row in rows:
        rank = json.loads(row["rank_key_json"])
        row["representative_conflict"] = int(rank[8][1]) > 0
    result: dict[str, list[dict]] = {}
    for row in rows:
        result.setdefault(str(row["base_pair_rule_signature"]), []).append(row)
    if target > 1238:
        live = sqlite3.connect(f"file:{LIVE_DB.resolve().as_posix()}?mode=ro", uri=True)
        live.row_factory = sqlite3.Row
        try:
            evaluated = [dict(row) for row in live.execute(
                "SELECT * FROM prediction_evaluation WHERE evaluation_round<? AND scope='PAIR_DIAGNOSTIC' "
                "ORDER BY evaluation_round", (target,))]
        finally:
            live.close()
        if evaluated and result:
            signature = next(iter(result))
            seen = {int(x["evaluation_round"]) for x in result[signature]}
            for item in evaluated:
                if int(item["evaluation_round"]) not in seen:
                    item["representative_conflict"] = False
                    result[signature].append(item)
                    seen.add(int(item["evaluation_round"]))
    return result


def trace(target: int, source: int, data_path: Path, label: str) -> dict:
    captured: dict[str, object] = {}
    real_stage6 = production.diagnose_stage6
    real_trios = production.build_current_trios
    real_pairs = production.generate_pair_candidates

    def stage6_wrapper(*args, **kwargs):
        value = real_stage6(*args, **kwargs); captured["number"] = value; return value

    def trio_wrapper(*args, **kwargs):
        value = real_trios(*args, **kwargs); captured["trio"] = value; return value

    def pair_wrapper(*args, **kwargs):
        value = real_pairs(*args, **kwargs); captured["raw_pairs"] = value; return value

    pipeline = ProductionPairPipeline(data_path, TRIO_DB)
    with patch.object(production, "diagnose_stage6", stage6_wrapper), patch.object(production, "build_current_trios", trio_wrapper), patch.object(production, "generate_pair_candidates", pair_wrapper):
        prediction = pipeline.build_prediction_context(target, source, history_before(target))

    number = captured["number"]
    number_rows = number["rows"]
    number_survivors = list(number["candidate_numbers"])
    number_reasons = Counter(str(row.get("number_state", "UNKNOWN")) for n, row in number_rows.items() if n not in number_survivors)

    trio = captured.get("trio")
    if trio is None:
        trio_input = trio_output = 0; trio_reasons = Counter(); trio_primary = trio_support = 0
    else:
        trio_rows = list(trio["rows"].values())
        trio_input = len(trio_rows)
        valid_trios = [row for row in trio_rows if row["valid_for_pair"]]
        trio_output = len(valid_trios)
        trio_reasons = Counter(str(row.get("pair_eligibility_reason") or row.get("trio_state") or "UNKNOWN") for row in trio_rows if not row["valid_for_pair"])
        trio_primary = sum(row.get("integrated_3of3_count", 0) > 0 or row.get("main_3of3_count", 0) > 0 for row in valid_trios)
        trio_support = sum(row.get("integrated_2of3_count", 0) > 0 or row.get("main_2of3_count", 0) > 0 for row in valid_trios)

    raw_pairs = list(captured.get("raw_pairs", ()))
    pair_states = Counter(item.context["pair_state"] for item in prediction.candidates)
    gate_reasons = Counter()
    primary_survivors = support_survivors = 0
    for item in prediction.candidates:
        gates = item.context["gate_records"]
        first = next((g for g in gates if g["status"] != "PASS"), None)
        if first:
            gate_reasons[f"{first['gate_id']}:{first.get('failure_code')}"] += 1
        gi = item.context["gate_input"]
        primary_survivors += int(str(gi.get("integrated_primary_evidence", "")).startswith("SUPERIOR_") or str(gi.get("main_primary_evidence", "")).startswith("SUPERIOR_"))
        support_survivors += int(str(gi.get("support_evidence", "")).startswith("SUPERIOR_"))
    valid_pairs = [item for item in prediction.candidates if item.context["pair_state"] in ("PAIR_READY", "PAIR_TEST_READY")]
    outputs = [] if not valid_pairs else [list(valid_pairs[0].member_a), list(valid_pairs[0].member_b)]

    stages = [
        {"stage":"NUMBER", "input":45, "output":len(number_survivors), "rejected":45-len(number_survivors), "minimum_required":6, "rejection_reasons":dict(number_reasons)},
        {"stage":"TRIO", "input":trio_input, "output":trio_output, "rejected":trio_input-trio_output, "minimum_required":2, "rejection_reasons":dict(trio_reasons), "primary_3of3_survivors":trio_primary, "support_exact2_survivors":trio_support},
        {"stage":"PAIR_LIFECYCLE", "input":len(raw_pairs), "output":len(valid_pairs), "rejected":len(raw_pairs)-len(valid_pairs), "minimum_required":1, "state_counts":dict(pair_states), "rejection_reasons":dict(gate_reasons), "primary_evidence_survivors":primary_survivors, "support_evidence_survivors":support_survivors},
        {"stage":"FINAL_3X2", "input":len(valid_pairs), "output":int(bool(outputs)), "rejected":max(0,len(valid_pairs)-int(bool(outputs))), "minimum_required":1}
    ]
    fatal = next((s["stage"] for s in stages if s["output"] < s["minimum_required"]), None)
    return {"label":label, "target_round":target, "max_source_round":source, "source_file":str(data_path.relative_to(ROOT)),
        "skip_status":prediction.skip_status, "stages":stages, "final_three_set_candidate_count":trio_output,
        "two_set_constructible":bool(outputs), "official_output":bool(outputs), "outputs":outputs,
        "first_fatal_bottleneck":fatal, "future_leakage_count":len(pipeline.outcome_accesses), "outcome_scoring_count":0}


def main() -> None:
    db = sqlite3.connect(f"file:{LIVE_DB.resolve().as_posix()}?mode=ro", uri=True)
    try: db_max = int(db.execute("SELECT max(draw_round) FROM draw_result").fetchone()[0] or 0)
    finally: db.close()
    maximum = db_max
    current = trace(maximum + 1, maximum, build_current_snapshot(maximum), "CURRENT_TARGET")
    sealed = trace(1238, 1237, SEALED_CSV, "SEALED_1238_REFERENCE") if maximum + 1 >= 1239 else None
    payload = {"max_source_round":maximum, "target_round":maximum+1, "current":current, "sealed_1238":sealed,
        "historical_trace":"NOT_REQUIRED_SAME_FATAL_BOTTLENECK" if sealed and sealed["first_fatal_bottleneck"]==current["first_fatal_bottleneck"] else "HISTORICAL_TRACE_SKIPPED_COST_NOT_JUSTIFIED"}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()

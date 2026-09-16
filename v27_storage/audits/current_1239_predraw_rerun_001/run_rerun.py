from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import p45_v27.pairs.production as production
from p45_v27.draw_update import Draw, _history_map, _previous_predictions, validate_draw
from p45_v27.pairs.production import ProductionPairPipeline

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001"
BASELINE = ROOT / "v27_storage/audits/no_pick_root_cause_trace_001/CURRENT_INPUT_SNAPSHOT.csv"
STAGING = OUT / "STAGING_CONTIGUOUS_DRAW_1_1238.csv"
PRIOR_JSON = ROOT / "v27_storage/audits/current_1239_official_predraw_001/PREDRAW_1239_RESULT.json"
PRIZE_LEDGER = ROOT / "v27_storage/experiments/prize_share_prospective_001_v1/PRIZE_SHARE_PROSPECTIVE_001_LEDGER.jsonl"
TRIO_DB = ROOT / "v27_storage/backtests/p45_v273_trio_walkforward.sqlite3"
EXPECTED_BASELINE_SHA = "ad69ec8d28b4e5cdb40d468ad758c5f23acaeb6225f525c5201c8027952701e6"
EXPECTED_SOURCE_SHA = "99d44e493a357785f976e37d99b1e0d2ae179b161cc1aa4a5665f9606ec0c119"


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_row(row: dict[str, str]) -> list[object]:
    return [int(row["round"]), row["date"], *[int(row[f"n{i}"]) for i in range(1, 7)], int(row["bonus"])]


def content_sha(rows: list[list[object]]) -> str:
    raw = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def find_values(value: object, key: str) -> list[object]:
    found_values: list[object] = []
    if isinstance(value, dict):
        if key in value:
            found_values.append(value[key])
        for child in value.values():
            found_values.extend(find_values(child, key))
    elif isinstance(value, list):
        for child in value:
            found_values.extend(find_values(child, key))
    return found_values


def validate_rows(path: Path) -> tuple[list[list[object]], dict[str, object]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [canonical_row(row) for row in csv.DictReader(handle)]
    rounds = [int(row[0]) for row in rows]
    counts = Counter(rounds)
    structural = 0
    for row in rows:
        main, bonus = list(map(int, row[2:8])), int(row[8])
        structural += int(len(main) != 6 or len(set(main)) != 6 or any(not 1 <= n <= 45 for n in main + [bonus]) or bonus in main)
    info = {
        "rows": len(rows), "unique_rounds": len(set(rounds)), "min_round": min(rounds), "max_round": max(rounds),
        "missing_rounds": sorted(set(range(1, max(rounds) + 1)) - set(rounds)),
        "duplicate_rounds": sorted(r for r, n in counts.items() if n > 1), "structural_errors": structural,
    }
    return rows, info


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    state = json.loads((ROOT / "00_P45_STATE/P45_CURRENT_STATE.json").read_text(encoding="utf-8-sig"))
    registry = max(int(value) for value in find_values(state, "registry_physical_rows"))
    if state["state_version"] != "1.0.88" or state["last_decision_id"] != "DECISION-20260824-095" or registry != 63:
        raise RuntimeError("STOP_STATE_DRIFT_OR_BASELINE_MISMATCH")
    if file_sha(BASELINE) != EXPECTED_BASELINE_SHA:
        raise RuntimeError("STOP_STATE_DRIFT_OR_BASELINE_MISMATCH")
    base_rows, base_info = validate_rows(BASELINE)
    if base_info != {"rows": 1237, "unique_rounds": 1237, "min_round": 1, "max_round": 1237, "missing_rounds": [], "duplicate_rounds": [], "structural_errors": 0}:
        raise RuntimeError("STOP_STATE_DRIFT_OR_BASELINE_MISMATCH")

    prior = json.loads(PRIOR_JSON.read_text(encoding="utf-8"))["draw_1238"]
    ledger = json.loads(PRIZE_LEDGER.read_text(encoding="utf-8").splitlines()[0])
    expected = (1238, "2026-08-22", [2, 13, 18, 32, 38, 42], 22, EXPECTED_SOURCE_SHA)
    prior_tuple = (prior["round"], prior["date"], prior["main"], prior["bonus"], prior["source_payload_sha256"])
    ledger_tuple = (ledger["round"], ledger["main_numbers"], ledger["bonus"], ledger["source_payload_sha256"])
    if prior_tuple != expected or ledger_tuple != (expected[0], expected[2], expected[3], expected[4]):
        raise RuntimeError("ROUND_1238_SOURCE_CONFLICT_STOP")
    draw = Draw(1238, "2026-08-22", tuple(expected[2]), 22, prior["source_url"], EXPECTED_SOURCE_SHA)
    validate_draw(draw, 1237)

    # Preserve baseline bytes exactly and append one canonical row.
    base_bytes = BASELINE.read_bytes()
    if not base_bytes.endswith(b"\n"):
        base_bytes += b"\n"
    STAGING.write_bytes(base_bytes + b"1238,2026-08-22,2,13,18,32,38,42,22\n")
    stage_rows, stage_info = validate_rows(STAGING)
    first_equal = stage_rows[:1237] == base_rows
    authoritative_equal = stage_rows[1237] == [1238, "2026-08-22", 2, 13, 18, 32, 38, 42, 22]
    if stage_info != {"rows": 1238, "unique_rounds": 1238, "min_round": 1, "max_round": 1238, "missing_rounds": [], "duplicate_rounds": [], "structural_errors": 0} or not first_equal or not authoritative_equal:
        raise RuntimeError("STAGING_CONTIGUITY_VALIDATION_FAILED")

    captures: dict[str, object] = {}
    real_stage6, real_trios, real_pairs = production.diagnose_stage6, production.build_current_trios, production.generate_pair_candidates
    def stage6(*args, **kwargs):
        value = real_stage6(*args, **kwargs); captures["number"] = value; return value
    def trios(*args, **kwargs):
        value = real_trios(*args, **kwargs); captures["trio"] = value; return value
    def pairs(*args, **kwargs):
        value = real_pairs(*args, **kwargs); captures["pairs"] = value; return value

    evaluations = _previous_predictions(draw)
    history = _history_map(draw, evaluations)
    pipeline = ProductionPairPipeline(STAGING, TRIO_DB)
    with patch.object(production, "diagnose_stage6", stage6), patch.object(production, "build_current_trios", trios), patch.object(production, "generate_pair_candidates", pairs):
        prediction = pipeline.build_prediction_context(1239, 1238, history)

    number = captures["number"]
    rows = number["rows"]
    lifecycle = Counter(row["number_state"] for row in rows.values())
    eligible_ids = [n for n, row in rows.items() if row["number_state"] in ("NUMBER_PASS", "NUMBER_TEST", "NUMBER_WEAKEN")]
    selected_ids = list(number["candidate_numbers"])
    structure_all = Counter(row["number_structure_state"] for row in rows.values())
    primary_evidence = Counter(row["primary_number_context"]["context"]["overall"]["integrated"]["evidence_label"] for row in rows.values())
    trio = captures.get("trio")
    trio_rows = [] if trio is None else list(trio["rows"].values())
    trio_states = Counter(row["trio_state"] for row in trio_rows)
    member_structures = Counter(row["member_structure_summary"] for row in trio_rows)
    final_structures = Counter(row["final_structure_state"] for row in trio_rows)
    valid_trios = [row for row in trio_rows if row["valid_for_pair"]]
    primary = sum(row["performance"]["statistics"][("INTEGRATED", "EXACT_3_OF_3")]["evidence_label"] in ("SUPERIOR_CONFIRMED", "SUPERIOR_TENTATIVE") for row in valid_trios)
    support = sum(row["performance"]["statistics"][("INTEGRATED", "EXACT_2_OF_3")]["evidence_label"] in ("SUPERIOR_CONFIRMED", "SUPERIOR_TENTATIVE") for row in valid_trios)
    pair_states = Counter(item.context["pair_state"] for item in prediction.candidates)
    valid_pairs = [item for item in sorted(prediction.candidates, key=lambda x: (x.rank_key, x.canonical_pair_key)) if item.context["pair_state"] in ("PAIR_READY", "PAIR_TEST_READY")]
    sets = [] if not valid_pairs else [list(valid_pairs[0].member_a), list(valid_pairs[0].member_b)]
    fatal = "NUMBER_EXTINCTION" if len(selected_ids) < 6 else "TRIO_EXTINCTION_BY_OFFICIAL_LIFECYCLE_HOLD" if len(valid_trios) < 2 else "PAIR_EXTINCTION" if not valid_pairs else None
    structures = {name: {"state": ledger_["structure_state"], "percentile": ledger_["overall_percentile"], "metric_percentiles": ledger_["metric_percentiles"]} for name, ledger_ in number["structures"].items()}

    result = {
        "final_verdict": "CURRENT_1239_RERUN_OFFICIAL_OUTPUT_AVAILABLE" if sets else "CURRENT_1239_RERUN_NO_OUTPUT_TRACED",
        "preflight": {"state": state["state_version"], "decision": state["last_decision_id"], "registry_physical_rows": registry, "engine": "FROZEN", "no_pick": "UNRESOLVED", "pause": "ACTIVE", "exp_017": "NOT_CREATED"},
        "authoritative_1238": {"status": "PASS", "round": 1238, "date": draw.date, "main": list(draw.main), "bonus": draw.bonus, "source_payload_sha256": draw.source_sha256, "provenance_match": True, "conflicts": 0},
        "staging": {"path": str(STAGING.relative_to(ROOT)), "sha256": file_sha(STAGING), **stage_info, "baseline_sha256": file_sha(BASELINE), "first_1237_exact_equality": first_equal, "first_1237_canonical_content_sha256": content_sha(stage_rows[:1237]), "baseline_canonical_content_sha256": content_sha(base_rows), "row_1238_authoritative_equality": authoritative_equal, "row_1238_canonical_hash": content_sha([stage_rows[1237]])},
        "invalid_staging_disposition": "INVALID_FOR_TARGET_1239_CAUSAL_USE - MISSING_1236_1237",
        "max_source_round": 1238, "target_round": 1239, "future_leakage_count": len(pipeline.outcome_accesses), "outcome_scoring_count": 0,
        "number": {"input": 45, "lifecycle_distribution": dict(lifecycle), "eligible_count_before_minimum_gate": len(eligible_ids), "eligible_identities_before_minimum_gate": eligible_ids, "selected_count": len(selected_ids), "selected_identities": selected_ids, "structure_distribution": dict(structure_all), "primary_evidence_distribution": dict(primary_evidence), "support_state": "NOT_APPLICABLE_AT_NUMBER_LEVEL"},
        "structures": structures,
        "trio": {"entered": trio is not None, "universe": len(trio_rows), "status_counts": dict(trio_states), "eligible": len(valid_trios), "member_structure_summary": dict(member_structures), "final_structure_state": dict(final_structures)},
        "pair": {"universe": len(prediction.candidates), "status_counts": dict(pair_states), "eligible": len(valid_pairs)},
        "primary_3of3_survivors": primary, "support_exact_2of3_survivors": support, "final_three_number_candidate_set_count": len(valid_trios),
        "two_set_constructible": bool(sets), "official_output": bool(sets), "sets": sets, "forced_pick": False, "first_fatal_bottleneck": fatal,
        "historical_lifecycle_update_count": len(evaluations), "official_source_changes": 0, "official_db_changes": 0,
    }
    (OUT / "PREDRAW_1239_RERUN_RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

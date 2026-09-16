from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import p45_v27.pairs.production as production
from p45_v27.draw_update import BASE_DATA, Draw, _history_map, _materialize_csv, _previous_predictions, fetch_official, validate_draw
from p45_v27.pairs.production import ProductionPairPipeline

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "v27_storage/audits/current_1239_official_predraw_001"
SNAPSHOT = OUT / "STAGING_IMMUTABLE_DRAW_THROUGH_1238.csv"
TRIO_DB = ROOT / "v27_storage/backtests/p45_v273_trio_walkforward.sqlite3"
PRIZE_LEDGER = ROOT / "v27_storage/experiments/prize_share_prospective_001_v1/PRIZE_SHARE_PROSPECTIVE_001_LEDGER.jsonl"


def main() -> None:
    draw = fetch_official(1238); validate_draw(draw, 1237)
    raw = json.loads(PRIZE_LEDGER.read_text(encoding="utf-8").splitlines()[0])
    if (raw["round"], raw["main_numbers"], raw["bonus"], raw["source_payload_sha256"]) != (draw.round, list(draw.main), draw.bonus, draw.source_sha256):
        raise RuntimeError("DRAW_1238_CANONICAL_CONFLICT")
    _materialize_csv([draw], SNAPSHOT)
    captures = {}
    real_stage6, real_trios, real_pairs = production.diagnose_stage6, production.build_current_trios, production.generate_pair_candidates
    def stage6(*a, **k): value=real_stage6(*a, **k); captures["number"]=value; return value
    def trios(*a, **k): value=real_trios(*a, **k); captures["trio"]=value; return value
    def pairs(*a, **k): value=real_pairs(*a, **k); captures["pairs"]=value; return value
    evaluations = _previous_predictions(draw)
    history = _history_map(draw, evaluations)
    pipeline = ProductionPairPipeline(SNAPSHOT, TRIO_DB)
    with patch.object(production,"diagnose_stage6",stage6), patch.object(production,"build_current_trios",trios), patch.object(production,"generate_pair_candidates",pairs):
        prediction = pipeline.build_prediction_context(1239,1238,history)
    number = captures["number"]
    number_states = Counter(row["number_state"] for row in number["rows"].values())
    selected = [number["rows"][n] for n in number["candidate_numbers"]]
    selected_states = Counter(row["number_state"] for row in selected)
    selected_structures = Counter(row["number_structure_state"] for row in selected)
    unit5 = number["structures"]["UNIT_5"]; end = number["structures"]["END_DIGIT"]
    trio = captures.get("trio")
    trio_rows = [] if trio is None else list(trio["rows"].values())
    trio_states = Counter(row["trio_state"] for row in trio_rows)
    member_structures = Counter(row["member_structure_summary"] for row in trio_rows)
    final_structures = Counter(row["final_structure_state"] for row in trio_rows)
    valid_trios = [row for row in trio_rows if row["valid_for_pair"]]
    primary_trios = sum(row["performance"]["statistics"][("INTEGRATED","EXACT_3_OF_3")]["evidence_label"] in ("SUPERIOR_CONFIRMED","SUPERIOR_TENTATIVE") for row in valid_trios)
    support_trios = sum(row["performance"]["statistics"][("INTEGRATED","EXACT_2_OF_3")]["evidence_label"] in ("SUPERIOR_CONFIRMED","SUPERIOR_TENTATIVE") for row in valid_trios)
    pair_states = Counter(item.context["pair_state"] for item in prediction.candidates)
    valid_pairs = [item for item in sorted(prediction.candidates,key=lambda x:(x.rank_key,x.canonical_pair_key)) if item.context["pair_state"] in ("PAIR_READY","PAIR_TEST_READY")]
    sets = [] if not valid_pairs else [list(valid_pairs[0].member_a),list(valid_pairs[0].member_b)]
    fatal = "NUMBER_EXTINCTION" if len(number["candidate_numbers"])<6 else "TRIO_EXTINCTION_BY_OFFICIAL_LIFECYCLE_HOLD" if len(valid_trios)<2 else "PAIR_EXTINCTION" if not valid_pairs else None
    result = {
      "final_verdict":"CURRENT_1239_OFFICIAL_OUTPUT_AVAILABLE" if sets else "CURRENT_1239_NO_OUTPUT_TRACED",
      "draw_1238":{"canonical_confirmed":True,"round":draw.round,"date":draw.date,"main":list(draw.main),"bonus":draw.bonus,"source_url":draw.source_url,"source_payload_sha256":draw.source_sha256,"duplicate_conflict":False},
      "draw_input_mode":"STAGING_PREDRAW","previous_max_source_round":1237,"max_source_round":1238,"target_round":1239,
      "snapshot_path":str(SNAPSHOT.relative_to(ROOT)),"snapshot_sha256":__import__("hashlib").sha256(SNAPSHOT.read_bytes()).hexdigest(),
      "number":{"input":45,"output":len(number["candidate_numbers"]),"all_state_counts":dict(number_states),"selected_state_counts":dict(selected_states),"selected_structure_distribution":dict(selected_structures),"identities":number["candidate_numbers"]},
      "unit_5":{"state":unit5["structure_state"],"percentile":unit5["overall_percentile"],"metric_percentiles":unit5["metric_percentiles"]},
      "end_digit":{"state":end["structure_state"],"percentile":end["overall_percentile"],"metric_percentiles":end["metric_percentiles"]},
      "trio":{"universe":len(trio_rows),"status_counts":dict(trio_states),"eligible":len(valid_trios),"member_structure_distribution":dict(member_structures),"final_structure_distribution":dict(final_structures)},
      "pair":{"universe":len(prediction.candidates),"state_counts":dict(pair_states),"eligible":len(valid_pairs)},
      "primary_3of3_survivors":primary_trios,"support_exact2_survivors":support_trios,"final_three_number_candidate_sets":len(valid_trios),
      "two_set_constructible":bool(sets),"official_output":bool(sets),"sets":sets,"forced_pick":False,
      "first_fatal_bottleneck":fatal,"same_as_1238_severe_bottleneck":unit5["structure_state"]=="SEVERE" and end["structure_state"]=="SEVERE" and len(valid_trios)==0,
      "future_leakage_count":len(pipeline.outcome_accesses),"outcome_scoring_count":0,"historical_lifecycle_update_count":len(evaluations),
    }
    (OUT/"PREDRAW_1239_RESULT.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))

if __name__ == "__main__": main()

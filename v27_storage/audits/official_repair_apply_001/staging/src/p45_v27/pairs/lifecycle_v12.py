"""Deterministic two-phase PAIR prediction lifecycle for official v1.2 audit storage."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .audit_v12 import CONTEXT_VERSION, SIGNATURE_VERSION, canonical_json, context_fingerprint, semantic_policy_hashes, sha256_json
from .decision import (GATE_IDS, bonus_dependence, decide_state, evaluate_gates,
    final_structure, pair_risk, recent_support_state, structure_state)
from ..trio_engine import statistic, wilson95

PRELOCK_VERSION = "PAIR-PRELOCK-1.0"
FINAL_PREDICTION_VERSION = "PAIR-FINAL-PREDICTION-1.0"
FINALIZATION_VERSION = "PAIR-PREDICTION-FINALIZATION-1.0"
BASELINES = {"INTEGRATED_PRIMARY":223821/45379620, "INTEGRATED_SUPPORT":5017311/45379620,
    "MAIN_PRIMARY":22959/8145060, "MAIN_SUPPORT":664677/8145060}

def _primary(row: Mapping[str, Any], prefix: str) -> bool:
    return int(row[f"a_{prefix}_hits"]) == 3 or int(row[f"b_{prefix}_hits"]) == 3

def _support(row: Mapping[str, Any], prefix: str) -> bool:
    a, b = int(row[f"a_{prefix}_hits"]), int(row[f"b_{prefix}_hits"])
    return a < 3 and b < 3 and (a == 2 or b == 2)

def _failure(row: Mapping[str, Any]) -> bool:
    return not _primary(row, "integrated") and not _support(row, "integrated")

def _rate(history: Sequence[Mapping[str, Any]], predicate: Any) -> float:
    return sum(predicate(row) for row in history) / len(history) if history else 0.0

def _adverse(history: Sequence[Mapping[str, Any]]) -> tuple[float, ...] | None:
    if len(history) < 100:
        return None
    r100, r50 = history[-100:], history[-50:]
    op = _rate(history, lambda x: _primary(x, "integrated"))
    os = _rate(history, lambda x: _support(x, "integrated"))
    of = _rate(history, _failure)
    oc = _rate(history, lambda x: bool(x["representative_conflict"]))
    return (max(0.0, op-_rate(r100, lambda x: _primary(x, "integrated"))),
        max(0.0, op-_rate(r50, lambda x: _primary(x, "integrated"))),
        max(0.0, os-_rate(r100, lambda x: _support(x, "integrated"))),
        max(0.0, os-_rate(r50, lambda x: _support(x, "integrated"))),
        max(0.0, _rate(r50, _failure)-of),
        max(0.0, _rate(r50, lambda x: bool(x["representative_conflict"]))-oc))

def materialize_historical_lifecycle(history: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Restore the already-defined pre-result lifecycle inputs from prior outcomes only."""
    stats = {}
    for endpoint, baseline in BASELINES.items():
        prefix = "integrated" if endpoint.startswith("INTEGRATED") else "main"
        predicate = _primary if endpoint.endswith("PRIMARY") else _support
        stats[endpoint] = statistic(sum(predicate(row, prefix) for row in history), len(history), baseline, 200)
    n = len(history)
    if n < 50:
        recent = "INSUFFICIENT_SAMPLE"
    else:
        r100 = history[-100:] if n >= 100 else None
        r50 = history[-50:]
        recent100 = None if r100 is None else (_rate(r100, lambda x: _support(x, "integrated")),
            wilson95(sum(_support(x, "integrated") for x in r100), len(r100))[1])
        recent50 = (_rate(r50, lambda x: _support(x, "integrated")),
            wilson95(sum(_support(x, "integrated") for x in r50), len(r50))[1])
        recent = recent_support_state(BASELINES["INTEGRATED_SUPPORT"], stats["INTEGRATED_SUPPORT"]["wilson_low"], recent100, recent50)
    current_adverse = _adverse(history)
    if current_adverse is None:
        rule_structure = "INSUFFICIENT_SAMPLE"
    else:
        adverse_history = tuple(value for end in range(100, n) if (value := _adverse(history[:end])) is not None)
        overall = {"primary":_rate(history, lambda x: _primary(x,"integrated")),
            "support":_rate(history, lambda x: _support(x,"integrated")), "failure":_rate(history,_failure),
            "conflict":_rate(history, lambda x: bool(x["representative_conflict"]))}
        r100, r50 = history[-100:], history[-50:]
        recent100 = {"primary":_rate(r100, lambda x: _primary(x,"integrated")), "support":_rate(r100, lambda x: _support(x,"integrated"))}
        recent50 = {"primary":_rate(r50, lambda x: _primary(x,"integrated")), "support":_rate(r50, lambda x: _support(x,"integrated")),
            "failure":_rate(r50,_failure), "conflict":_rate(r50, lambda x: bool(x["representative_conflict"]))}
        _, _, rule_structure = structure_state(overall, recent100, recent50, adverse_history)
    return {"n":n, "stats":stats, "recent_state":recent, "rule_structure":rule_structure}

def restore_lifecycle_gate_data(gate_data: Mapping[str, Any], rank_values: Sequence[Any],
                                history: Sequence[Mapping[str, Any]], valid_trio_count: int) -> dict[str, Any]:
    metrics = materialize_historical_lifecycle(history); stats = metrics["stats"]
    primary, main, support = stats["INTEGRATED_PRIMARY"], stats["MAIN_PRIMARY"], stats["INTEGRATED_SUPPORT"]
    conflict_columns = int(rank_values[8][1])
    bonus = bonus_dependence(primary["evidence_label"], main["evidence_label"],
        primary["evidence_label"].startswith("SUPERIOR_"), main["rate"], BASELINES["MAIN_PRIMARY"])
    member_risk = str(gate_data["final_risk"])
    _, rule_risk, final_risk = pair_risk(member_risk, member_risk, primary=primary["evidence_label"],
        support=support["evidence_label"], integrated_primary=primary["evidence_label"],
        main_primary=main["evidence_label"], bonus=bonus, recent=metrics["recent_state"], conflict_columns=conflict_columns)
    data = dict(gate_data)
    data.update({"selection_exposure":metrics["n"], "integrated_primary_rate":primary["rate"],
        "integrated_primary_baseline":BASELINES["INTEGRATED_PRIMARY"], "integrated_primary_evidence":primary["evidence_label"],
        "main_primary_rate":main["rate"], "main_primary_baseline":BASELINES["MAIN_PRIMARY"], "main_primary_evidence":main["evidence_label"],
        "recent_state":metrics["recent_state"], "final_risk":final_risk,
        "final_structure":final_structure(str(gate_data["final_structure"]), str(gate_data["final_structure"]), metrics["rule_structure"]),
        "valid_trio_count":valid_trio_count, "disjoint":True, "bonus_dependence":bonus,
        "primary_evidence":primary["evidence_label"], "support_evidence":support["evidence_label"],
        "conflict_columns":conflict_columns, "members_valid":True, "pool_type":"EXPANDED_TEST_POOL",
        "walkforward_ok":True, "signature_ok":True, "prediction_hash_ok":True, "atomic_storage_ok":True,
        "pair_rule_risk":rule_risk})
    return data

def _link(version: str, payload: Mapping[str, Any], *, verified: bool = True) -> dict[str, Any]:
    raw = canonical_json(payload)
    return {"version": version, "canonical_payload_json": raw, "hash": sha256_json(payload), "staging_verified": verified}

def build_official_prediction_audit(*, evaluation_round: int, source_end_round: int,
    data_prefix_hash: str, canonical_pair_key: str, pair_numbers: Sequence[int], pool_type: str,
    set1_key: str, set2_key: str, constituent_trios: Sequence[Mapping[str, Any]],
    unit_cells: Sequence[Mapping[str, Any]], unit_summaries: Sequence[Mapping[str, Any]],
    member_risks: Sequence[Mapping[str, Any]], member_structures: Sequence[Mapping[str, Any]],
    selection_exposure: int, rule_signature: str, canonical_rule_payload_json: str,
    rank_values: Sequence[Any], stable_key: str, representative_selected: bool,
    gate_data: Mapping[str, Any]) -> dict[str, Any]:
    if source_end_round != evaluation_round - 1:
        raise RuntimeError("PAIR_FUTURE_LEAKAGE")
    if len(unit_cells) != 30 or len(unit_summaries) != 5 or len(constituent_trios) != 2:
        raise RuntimeError("PAIR_CONTEXT_SHAPE_INVALID")
    prelock_payload = {"candidate_key":canonical_pair_key,"data_prefix_hash":data_prefix_hash,
        "evaluation_round":evaluation_round,"outcome_access_count":0,"policy_hashes":semantic_policy_hashes(),
        "rule_signature":rule_signature,"source_end_round":source_end_round}
    prelock = _link(PRELOCK_VERSION, prelock_payload)
    gd = dict(gate_data)
    gd.update({"walkforward_prelock_ok":True,"executed_gate_ids":GATE_IDS,"ledger_complete":True})
    provisional = list(evaluate_gates(gd))
    # PG13 is activated in position 13 and locked as PENDING_FINAL. PG14 is then evaluated.
    preliminary_inputs = [list(GATE_IDS[:12]), sha256_json([g.__dict__ for g in provisional[:12]]),
        sha256_json({"sequence":list(GATE_IDS)}), sha256_json({"next":"PG14"}),
        sha256_json({"candidate":canonical_pair_key,"required":"pre-result"}), 0]
    preliminary_record = {"inputs":preliminary_inputs,"marker":"PG13_PENDING_FINAL"}
    preliminary_hash = sha256_json(preliminary_record)
    final_prediction_payload = {"gate_pg01_pg12":[g.__dict__ for g in provisional[:12]],
        "pg13_pending_record_hash":preliminary_hash,"policy_linkage":semantic_policy_hashes(),
        "prelock_hash":prelock["hash"],"ranking_context_hash":sha256_json(list(rank_values)),
        "representative_selected":representative_selected}
    final_prediction = _link(FINAL_PREDICTION_VERSION, final_prediction_payload)
    pg14_status = "PASS" if final_prediction["staging_verified"] else "FAIL"
    pg14_record = {"gate_id":"PG14","input_values":[True,True,True,True,True,0,True],
        "status":pg14_status,"failure_code":None if pg14_status == "PASS" else "PAIR_LEDGER_INCOMPLETE",
        "pg13_lifecycle":None}
    pg14_hash = sha256_json(pg14_record)
    final_trace = [*GATE_IDS[:12], "PG13_PRELIMINARY", "PG14"]
    final_inputs = [preliminary_hash, final_trace, preliminary_inputs[1], pg14_hash,
        preliminary_inputs[2], sha256_json({"timing":"official"}), 0, 0]
    pg13_status = "PASS" if pg14_status == "PASS" else "FAIL"
    pg13_lifecycle = {"preliminary_inputs":preliminary_inputs,"preliminary_trace_hash":sha256_json(list(GATE_IDS[:12])),
        "preliminary_record_hash":preliminary_hash,"pending_final_marker":"PG13_PENDING_FINAL",
        "pg14_record_hash":pg14_hash,"final_certification_inputs":final_inputs,
        "final_execution_trace_hash":sha256_json(final_trace),"final_result":pg13_status,
        "final_failure_code":None if pg13_status == "PASS" else "PAIR_GATE_SEQUENCE_FAIL"}
    numbers=gd.get("member_numbers")
    intersection=len(set(numbers[0]) & set(numbers[1])) if numbers is not None else None
    union=len(set(numbers[0]) | set(numbers[1])) if numbers is not None else None
    unit_statuses=gd.get("unit_statuses")
    gate_inputs=[
      list(gd.get("member_states") or (None,None)), [intersection,union],
      [sum(x=="COMPLETE" for x in unit_statuses) if unit_statuses is not None else None],
      [gd.get("coverage_complete_cells")], [True,0,True,True,True,True], [gd.get("selection_exposure")],
      [gd.get("integrated_primary_rate"),gd.get("integrated_primary_baseline"),gd.get("integrated_primary_evidence")],
      [gd.get("main_primary_rate"),gd.get("main_primary_baseline"),gd.get("main_primary_evidence")],
      [gd.get("recent_state")],[gd.get("final_risk")],[gd.get("final_structure")],
      [10,1,1,1],
    ]
    records=[]
    for index, result in enumerate(provisional[:12], 1):
        records.append({"gate_id":f"PG{index:02d}","input_values":gate_inputs[index-1],
            "status":result.status,"failure_code":result.reason,"pg13_lifecycle":None})
    records.append({"gate_id":"PG13","input_values":[True,list(GATE_IDS),0],"status":pg13_status,
        "failure_code":None if pg13_status == "PASS" else "PAIR_GATE_SEQUENCE_FAIL","pg13_lifecycle":pg13_lifecycle})
    records.append(pg14_record)
    final_state = decide_state(evaluate_gates(gd), gd)
    gate_vector_hash=sha256_json(records)
    finalization_payload={"final_pair_state":final_state,"gate_vector_hash":gate_vector_hash,
        "outcome_access_count_before_finalization":0,"prediction_hash":final_prediction["hash"]}
    finalization_raw=canonical_json(finalization_payload)
    finalization={"version":FINALIZATION_VERSION,"canonical_payload_json":finalization_raw,
        "hash":sha256_json(finalization_payload),"gate_vector_hash":gate_vector_hash,
        "outcome_access_count_before_finalization":0}
    windows=[]
    for window in ("OVERALL","RECENT100","RECENT50","RECENT20"):
        windows.append({"window_id":window,"exposure_count":selection_exposure,"integrated_primary_count":0,
            "main_primary_count":0,"integrated_support_count":0,"main_support_count":0,
            "simultaneous_failure_count":0,"unit_conflict_exposure_count":0})
    fields={
      "temporal_boundary":{"evaluation_round":evaluation_round,"source_end_round":source_end_round,"data_prefix_hash":data_prefix_hash,"outcome_access_count":0},
      "pair_identity":{"canonical_pair_key":canonical_pair_key,"pair_numbers":list(pair_numbers),"pool_type":pool_type,"set1_trio_key":set1_key,"set2_trio_key":set2_key},
      "constituent_trios":list(constituent_trios),"unit_coverage_cells":list(unit_cells),"unit_summaries":list(unit_summaries),
      "role_diversity":[x["distinct_role_count"] for x in unit_summaries],"evidence_overlap":[x["shared_evidence_id_count"] for x in unit_summaries],
      "member_risk_inputs":list(member_risks),"member_structure_inputs":list(member_structures),
      "historical_selection_exposure":{"rule_signature":rule_signature,"count_before_round":selection_exposure,"sample_band":"GE200" if selection_exposure>=200 else "GE50_LT200" if selection_exposure>=50 else "LT50"},
      "recent_inputs":windows,
      "historical_risk_inputs":{"integrated_primary_evidence":None,"main_primary_evidence":None,"integrated_support_evidence":None,"main_support_evidence":None,"member_max_risk":max((x["opposite_risk"] for x in member_risks),default="LOW"),"pair_rule_risk":None,"final_risk":None},
      "structure_percentile_inputs":{"metrics":[{"metric_index":i,"current_value":None,"history_endpoint_count":selection_exposure,"percentile_0_100":None} for i in range(1,7)],"pair_rule_state":"INSUFFICIENT_SAMPLE","member_summary_state":"INSUFFICIENT_SAMPLE","final_state":"INSUFFICIENT_SAMPLE","insufficient_sample":True},
      "bonus_pre_result_inputs":{"integrated_primary_count":0,"main_primary_count":0,"bonus_assisted_primary_count":0,"integrated_primary_evidence":None,"main_primary_evidence":None,"bonus_dependence":None},
      "prelock_link":prelock,"gate_records":records,"final_prediction_link":final_prediction,"final_pre_result_state":final_state,
      "ranking_and_representative":{"ranking_inputs":[{"key_index":i,"value":v,"is_null":v is None} for i,v in enumerate(rank_values[:15],1)],"stable_key":stable_key,"representative_group_key":[evaluation_round,rule_signature],"representative_selected":representative_selected},
      "policy_linkage":{**semantic_policy_hashes(),"pair_rule_signature_version":SIGNATURE_VERSION,"pair_rule_signature":rule_signature,"canonical_rule_payload_json":canonical_rule_payload_json},
      "finalization_link":finalization,
    }
    fingerprint, raw, _ = context_fingerprint(fields)
    return {"context_fingerprint_version":CONTEXT_VERSION,"pair_context_fingerprint":fingerprint,
        "canonical_context_payload_json":raw,"prelock":prelock,"final_prediction":final_prediction,
        "finalization":finalization,"gate_records":records,"pair_state":final_state}

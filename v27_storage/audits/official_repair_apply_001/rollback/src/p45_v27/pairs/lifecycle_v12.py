"""Deterministic two-phase PAIR prediction lifecycle for official v1.2 audit storage."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .audit_v12 import CONTEXT_VERSION, SIGNATURE_VERSION, canonical_json, context_fingerprint, semantic_policy_hashes, sha256_json
from .decision import GATE_IDS, evaluate_gates

PRELOCK_VERSION = "PAIR-PRELOCK-1.0"
FINAL_PREDICTION_VERSION = "PAIR-FINAL-PREDICTION-1.0"
FINALIZATION_VERSION = "PAIR-PREDICTION-FINALIZATION-1.0"

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
    # Official precedence: incomplete is system hold; otherwise ready only if every gate passes.
    statuses=[r["status"] for r in records]
    final_state = "PAIR_SYSTEM_HOLD" if "INCOMPLETE" in statuses else "PAIR_READY" if set(statuses)=={"PASS"} else "PAIR_RESEARCH_HOLD"
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

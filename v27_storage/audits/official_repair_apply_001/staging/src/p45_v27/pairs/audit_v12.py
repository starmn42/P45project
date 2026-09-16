"""Official PAIR rule-signature 1.2 and context-fingerprint 1.0 audit primitives."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

SIGNATURE_VERSION = "PAIR-RULE-SIGNATURE-1.2"
CONTEXT_VERSION = "PAIR-CONTEXT-FINGERPRINT-1.0"
OFFICIAL_PATCH_SHA256 = "0c91315ef0cc7d1638a61f321faf3e62079f9545a1386bd3271710b27e113316"
RANKING_POLICY_HASH = "b8965fbbf91b7cdb4423fdf9c35da70a9687def464df7fc5fddab1f045ab0d38"
GATE_STATE_POLICY_HASH = "3dce8b886556f952af5c8f401fd2db02cec0527e10647cdbde6747bd543359c5"

CONTEXT_FIELD_IDS = (
    "temporal_boundary", "pair_identity", "constituent_trios", "unit_coverage_cells",
    "unit_summaries", "role_diversity", "evidence_overlap", "member_risk_inputs",
    "member_structure_inputs", "historical_selection_exposure", "recent_inputs",
    "historical_risk_inputs", "structure_percentile_inputs", "bonus_pre_result_inputs",
    "prelock_link", "gate_records", "final_prediction_link", "final_pre_result_state",
    "ranking_and_representative", "policy_linkage", "finalization_link",
)

ELIGIBILITY_DESCRIPTOR = {"authority":"P45-v2.7.4-PAIR","eligible_member_states":["TRIO_PASS","TRIO_WEAKEN","VALID_TRIO_TEST"],"minimum_valid_trios":2,"policy_id":"PAIR-ELIGIBILITY-1.0","test_pool_state_cap":"PAIR_TEST_READY","valid_for_pair_required":True}
CANDIDATE_DESCRIPTOR = {"authority":"P45-v2.7.4-PAIR","candidate_object":"UNORDERED_DISJOINT_TRIO_PAIR","canonical_pair_key":"LEXICOGRAPHIC_SORT_OF_TWO_CANONICAL_TRIO_KEYS","disjointness":"NUMBER_INTERSECTION_SIZE_EQUALS_ZERO","duplicate_policy":"ONE_CANDIDATE_PER_CANONICAL_PAIR_KEY","policy_id":"PAIR-CANDIDATE-GENERATION-1.0"}
REPRESENTATIVE_DESCRIPTOR = {"authority":"P45-v2.7.4-PAIR","grouping_key":["walkforward_run_id","evaluation_round","pair_rule_signature"],"max_selection_per_group":1,"policy_id":"PAIR-REPRESENTATIVE-SELECTION-1.0","selection_order":"RANKING_POLICY_THEN_CANONICAL_PAIR_KEY"}
BOOTSTRAP_DESCRIPTOR = {"authority":"P45-v2.7.4-PAIR-WALKFORWARD-BOOTSTRAP-PATCH","historical_update_lag":1,"outcome_available_after_finalization":True,"pair_metric_role":"GATE_STATE_RANKING_INPUT_ONLY","policy_id":"PAIR-BOOTSTRAP-1.1-TIMING","pre_result_boundary":"SOURCE_END_ROUND_EQUALS_EVALUATION_ROUND_MINUS_1","signature_dependency":"NO_PAIR_HISTORICAL_METRIC","zero_and_new_signature":"DETERMINISTIC_ZERO_EXPOSURE_BOOTSTRAP"}
BASELINE_DESCRIPTOR = {"authority":"P45-v2.7.4-PAIR-GATE-AMENDMENT","policy_id":"PAIR-EXACT-BASELINES-1.0","primary":"INTEGRATED_AND_MAIN_EXACT_3_OF_3_SEPARATE","support":"INTEGRATED_AND_MAIN_EXACT_2_OF_3_SEPARATE"}
SAMPLE_BAND_DESCRIPTOR = {"authority":"P45-v2.7.4-PAIR-GATE-AMENDMENT","policy_id":"PAIR-SAMPLE-BAND-1.0","bands":[0,50,200],"recent_windows":[100,50,20],"recent20":"TEST_ONLY"}
MEMBER_ORDER_DESCRIPTOR = {"authority":"P45-v2.7.4-PAIR-GATE-AMENDMENT","policy_id":"PAIR-MEMBER-ORDER-1.0","order":"CANONICAL_TRIO_KEY_ASC","set_assignment":"OFFICIAL_DETERMINISTIC_PRE_RESULT"}

def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)

def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def semantic_policy_hashes() -> dict[str, str]:
    return {
        "eligibility_policy_hash": sha256_json(ELIGIBILITY_DESCRIPTOR),
        "candidate_generation_policy_hash": sha256_json(CANDIDATE_DESCRIPTOR),
        "ranking_policy_hash": RANKING_POLICY_HASH,
        "representative_selection_policy_hash": sha256_json(REPRESENTATIVE_DESCRIPTOR),
        "gate_state_policy_hash": GATE_STATE_POLICY_HASH,
        "bootstrap_policy_hash": sha256_json(BOOTSTRAP_DESCRIPTOR),
        "baseline_policy_hash": sha256_json(BASELINE_DESCRIPTOR),
        "sample_band_policy_hash": sha256_json(SAMPLE_BAND_DESCRIPTOR),
        "member_order_policy_hash": sha256_json(MEMBER_ORDER_DESCRIPTOR),
    }

def canonical_rule_payload(pair_pool_type: str, *, policy_hashes: Mapping[str, str] | None = None) -> dict[str, Any]:
    if pair_pool_type not in {"CORE_PASS_POOL", "EXPANDED_TEST_POOL"}:
        raise ValueError("PAIR_RULE_POOL_TYPE_INVALID")
    hashes = dict(policy_hashes or semantic_policy_hashes())
    required = set(semantic_policy_hashes())
    if set(hashes) != required or any(len(v) != 64 for v in hashes.values()):
        raise ValueError("PAIR_RULE_POLICY_HASH_SET_INVALID")
    return {**hashes, "pair_pool_type": pair_pool_type,
            "selection_rule_authority": "P45-v2.7.4-PAIR", "signature_version": SIGNATURE_VERSION}

def rule_signature(pair_pool_type: str, *, policy_hashes: Mapping[str, str] | None = None) -> tuple[str, str, dict[str, Any]]:
    payload = canonical_rule_payload(pair_pool_type, policy_hashes=policy_hashes)
    raw = canonical_json(payload)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest(), raw, payload

def _reject_forbidden(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        if not value:
            raise ValueError(f"PAIR_CONTEXT_EMPTY_OBJECT:{path}")
        for key, item in value.items():
            lowered = str(key).lower()
            if lowered in {"outcome", "future", "result_after_round", "commit_result"}:
                raise ValueError(f"PAIR_CONTEXT_FUTURE_OR_OUTCOME_FIELD:{path}.{key}")
            _reject_forbidden(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_forbidden(item, f"{path}[{index}]")

def canonical_context_payload(fields: Mapping[str, Any]) -> dict[str, Any]:
    if tuple(fields.keys()) != CONTEXT_FIELD_IDS:
        missing = [x for x in CONTEXT_FIELD_IDS if x not in fields]
        extra = [x for x in fields if x not in CONTEXT_FIELD_IDS]
        raise ValueError(f"PAIR_CONTEXT_FIXED_FIELDS_INVALID:missing={missing}:extra={extra}")
    records = [{"field_id": field_id, "value": deepcopy(fields[field_id])} for field_id in CONTEXT_FIELD_IDS]
    payload = {"fields": records, "version": CONTEXT_VERSION}
    _reject_forbidden(payload)
    return payload

def context_fingerprint(fields: Mapping[str, Any]) -> tuple[str, str, dict[str, Any]]:
    payload = canonical_context_payload(fields)
    raw = canonical_json(payload)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest(), raw, payload

def verify_official_patch(project_root: Path) -> None:
    path = project_root / "P45_v2.7.4_PAIR_Signature_v1.2_PATCH_UTF8_BOM_CRLF.md"
    if hashlib.sha256(path.read_bytes()).hexdigest() != OFFICIAL_PATCH_SHA256:
        raise RuntimeError("PAIR_SIGNATURE_V12_OFFICIAL_PATCH_HASH_MISMATCH")


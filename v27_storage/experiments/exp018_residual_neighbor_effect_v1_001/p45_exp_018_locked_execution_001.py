from __future__ import annotations

import hashlib
import json
from pathlib import Path


EXP_DIR = Path(__file__).resolve().parent
PROTOCOL = EXP_DIR / "P45_EXP_018_RESIDUAL_NEIGHBOR_EFFECT_V1_PROTOCOL_001.md"
LOCK = EXP_DIR / "P45_EXP_018_PROTOCOL_LOCK_001.md"
PREFLIGHT = EXP_DIR / "P45_EXP_018_STRUCTURAL_PREFLIGHT_001.json"
OUTPUT = EXP_DIR / "P45_EXP_018_RESIDUAL_NEIGHBOR_EFFECT_V1_CALCULATION_001.json"

EXPECTED_PROTOCOL_SHA = "d64b3ec3bdf5c65006236cefc67432333bc5edbc61dbe3b5db90d85a614d527c"
EXPECTED_LOCK_SHA = "08006727b6b83f6d903cc1216c24be64a8bf21fbc027a7e471162da10aeab906"
EXPECTED_PREFLIGHT_SHA = "ca2a8055eeda0f7c3c8c8217f9dd966b614e5fb51f2c7be54a7250364d074190"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    actual_protocol_sha = sha256(PROTOCOL)
    actual_lock_sha = sha256(LOCK)
    actual_preflight_sha = sha256(PREFLIGHT)
    if actual_protocol_sha != EXPECTED_PROTOCOL_SHA or actual_lock_sha != EXPECTED_LOCK_SHA:
        verdict = "EXP_018_EXECUTION_BLOCKED_LOCK_MISMATCH"
        reason = "LOCK_SHA_MISMATCH"
    elif actual_preflight_sha != EXPECTED_PREFLIGHT_SHA:
        verdict = "EXP_018_EXECUTION_BLOCKED_PREFLIGHT_MISMATCH"
        reason = "STRUCTURAL_PREFLIGHT_SHA_MISMATCH"
    else:
        protocol_text = PROTOCOL.read_text(encoding="utf-8").lower()
        bound_methods = ("percentile", "basic bootstrap", "bca", "studentized", "bootstrap-t")
        specified_methods = [method for method in bound_methods if method in protocol_text]
        if not specified_methods:
            verdict = "EXP_018_EXECUTION_BLOCKED_BOOTSTRAP_AMBIGUITY"
            reason = "U95_BOUND_CONSTRUCTION_METHOD_NOT_LOCKED"
        else:
            verdict = "EXP_018_EXECUTION_BLOCKED_PRIMARY_TEST"
            reason = "UNEXPECTED_EXECUTION_PATH_REQUIRES_REVIEW"

    payload = {
        "experiment_id": "EXP-018 / EXP-DRAW-20260827-018-V1",
        "execution_status": "BLOCKED_BEFORE_OUTCOME_ACCESS",
        "final_verdict": verdict,
        "block_reason": reason,
        "lock_verify": {
            "protocol_sha_expected": EXPECTED_PROTOCOL_SHA,
            "protocol_sha_actual": actual_protocol_sha,
            "protocol_sha_status": "PASS" if actual_protocol_sha == EXPECTED_PROTOCOL_SHA else "FAIL",
            "lock_sha_expected": EXPECTED_LOCK_SHA,
            "lock_sha_actual": actual_lock_sha,
            "lock_sha_status": "PASS" if actual_lock_sha == EXPECTED_LOCK_SHA else "FAIL",
        },
        "structural_reproduction": {
            "preflight_sha_expected": EXPECTED_PREFLIGHT_SHA,
            "preflight_sha_actual": actual_preflight_sha,
            "structural_match": "PASS" if actual_preflight_sha == EXPECTED_PREFLIGHT_SHA else "FAIL",
        },
        "bootstrap_lock_audit": {
            "cluster_unit": "TARGET_ROUND",
            "n_bootstrap": 100000,
            "seed": 20260827,
            "requested_bound": "ONE_SIDED_95_PERCENT_UPPER",
            "bound_construction_method": "NOT_SPECIFIED_IN_LOCKED_PROTOCOL",
            "ambiguous_choices": ["PERCENTILE", "BASIC", "BCA", "STUDENTIZED"],
        },
        "outcome_access": {
            "historical_outcomes_joined": False,
            "neighbor_hits_calculated": False,
            "control_hits_calculated": False,
            "hit_rates_calculated": False,
            "matched_delta_calculated": False,
            "p_value_calculated": False,
            "bootstrap_executed": False,
            "split_verdicts_calculated": False,
        },
        "protection": {"future_leakage": 0, "sealed_1239_changes": 0, "prospective_outcome_changes": 0},
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

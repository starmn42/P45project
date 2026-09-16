import json
import math

import numpy as np
from p45_audits import crowd_topology_exp002_calibration_audit_001 as A


def test_lock_and_protected_hashes():
    assert A.file_sha256(A.LOCK_NOTE) == A.LOCK_NOTE_SHA256
    assert A.protected_hashes() == A.EXPECTED_PROTECTED_HASHES


def test_data_boundary_and_denominator():
    data = A.load_data()
    assert data["round"].astype(int).tolist() == list(range(1, 1238))
    assert np.all(data["sold_lines"] > 1)
    assert np.all(data["k1"] >= 0) and np.all(data["k2"] >= 0) and np.all(data["k3"] >= 0)


def test_combinatorial_constants_and_required_terms():
    assert A.M == 8_145_060
    assert A.D1_DEGREE == 234
    assert 6 / 234 == 1 / 39
    data = {"k1": np.array([2.0]), "k2": np.array([3.0]), "k3": np.array([5.0]), "sold_lines": np.array([1000.0])}
    parts = A.calculate_components(data)
    expected_raw = 3 * 2 - 6 * 2 * 1 - (5 / 39) * 2 * 8
    expected = A.M * A.M * expected_raw / (1000 * 999)
    assert np.isclose(parts["residual"][0], expected)


def test_fixed_block_bootstrap_is_deterministic():
    values = np.linspace(-2.0, 3.0, 437)
    first = A.fixed_block_wild(values)
    second = A.fixed_block_wild(values)
    assert first == second
    assert first["p_cal"] == (1 + first["exceedances"]) / 200001


def test_saved_result_guardrails():
    result = json.loads(A.RAW_RESULT.read_text(encoding="utf-8"))
    assert result["status"] in ("NO_CALIBRATION_TENSION_DETECTED", "CALIBRATION_IDENTITY_TENSION")
    assert result["round_1238_plus_used"] is False
    assert result["k1_only_calibration_identifiable"] is False
    assert result["required_calibration_terms"] == ["K1(K1-1)", "K1*K23"]
    assert result["new_experiment_created"] is False
    assert result["exp002_original_status_changed"] is False
    assert result["prospective_signal_peeking"] == 0
    assert result["promotion_candidate"] is False


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"{len(tests)}/{len(tests)} PASS")


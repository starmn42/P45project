import csv
import json
import math

import numpy as np
from p45_experiments import crowd_topology_exp002_v1 as C


def test_shell_and_column_identity():
    assert C.D1_DEGREE == 234
    assert C.COLUMN_COUNT == 39
    assert C.COLUMN_SIZE == 6
    assert C.K3_SHELL_SIZE == 228
    assert C.COLUMN_SIZE / C.D1_DEGREE == C.P0 == 1 / 39


def test_protocol_and_reused_snapshot_are_locked():
    assert C.sha_file(C.PROTOCOL) == C.PROTOCOL_SHA256
    assert C.sha_file(C.SNAPSHOT) == C.SNAPSHOT_SHA256
    lock = json.loads(C.LOCK.read_text(encoding="utf-8"))
    assert lock["lock_status"] == "LOCKED_BEFORE_OUTCOME_ANALYSIS"
    assert lock["outcome_analyzed_at_lock"] is False


def test_snapshot_is_exactly_historical_and_complete():
    with C.SNAPSHOT.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [int(row["round"]) for row in rows] == list(range(1, 1238))
    assert all(int(row["k2"]) >= 0 and int(row["k3"]) >= 0 for row in rows)
    assert all(int(row["k2"]) + int(row["k3"]) > 0 for row in rows)


def test_pearson_contribution_formula():
    x = np.asarray([4.0])
    n = np.asarray([100.0])
    expected = (4 - 100 / 39) ** 2 / (100 / 39 * 38 / 39)
    assert np.isclose(C.pearson_contributions(x, n)[0], expected, rtol=0.0, atol=1e-15)


def test_fixed_ranges_and_block_geometry():
    rounds, k2, k3 = C.load_locked_data()
    assert rounds[:800].tolist() == list(range(1, 801))
    assert rounds[800:].tolist() == list(range(801, 1238))
    assert len(rounds[800:818]) == 18
    assert len(rounds[800:1018]) == 218
    assert len(rounds[1018:]) == 219
    assert len(rounds[800:]) == 23 * 19


def test_mc_is_seed_deterministic_on_small_probe():
    n = np.asarray([29, 1283, 2050], dtype=np.int64)
    first = C.monte_carlo(n, 0.1)
    second = C.monte_carlo(n, 0.1)
    assert first == second


def test_saved_result_obeys_locked_guardrails():
    result = json.loads(C.RESULT.read_text(encoding="utf-8"))
    assert result["round_1238_plus_used"] is False
    assert result["mc_repetitions"] in (0, 200_000)
    assert result["mc_seed"] == 2026082303
    assert result["promotion_candidate"] is False
    assert result["independent_reproduction"] == "NOT_YET"
    assert result["novelty_status"] == "NOVELTY_NOT_CONFIRMED"
    assert result["official_effect"] == "NONE"
    assert result["deterministic_rerun"] == "PASS"


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"{len(tests)}/{len(tests)} PASS")

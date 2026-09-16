import csv, hashlib, json, math
from pathlib import Path

import numpy as np
from p45_experiments import crowd_topology_exp001_v1 as C


def test_johnson_distance1_shell_identity():
    assert C.M == 8_145_060
    assert C.D1 == 234
    assert math.comb(6, 1) == 6
    assert 6 * 38 == 228
    assert 6 + 228 == C.D1


def test_local_excess_formula_locked():
    n = np.array([1_000_000.0])
    k1 = np.array([2.0])
    k23 = np.array([30.0])
    actual = C.M*C.M*k1*k23/(n*(n-1)*C.D1)-1
    expected = (C.M**2*2*30)/(1_000_000*999_999*234)-1
    assert actual[0] == expected


def test_snapshot_is_exactly_1_to_1237_and_future_blocked():
    with C.SNAPSHOT.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    rounds = [int(row["round"]) for row in rows]
    assert rounds == list(range(1, 1238))
    assert not any(r >= 1238 for r in rounds)


def test_snapshot_hash_and_protocol_hash_locked():
    manifest = json.loads(C.MANIFEST.read_text(encoding="utf-8"))
    assert C.sha_file(C.PROTOCOL) == C.PROTOCOL_SHA256
    assert C.sha_file(C.SNAPSHOT) == manifest["snapshot_sha256"]
    assert manifest["canonical_main_mismatch"] == 0
    assert manifest["shell_identity"] == {"k2": 6, "k3": 228, "total": 234, "status": "PASS"}


def test_saved_result_respects_sequential_gate_and_no_promotion():
    result = json.loads(C.RESULT.read_text(encoding="utf-8"))
    assert result["train_gate"] == "PASS"
    assert result["primary_bootstraps"] == 100_000
    assert result["uniform_mc"] == 100_000
    assert result["round_1238_plus_used"] is False
    assert result["promotion_candidate"] is False
    assert result["official_effect"] == "NONE"
    assert result["deterministic_rerun"] == "PASS"


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"{len(tests)}/{len(tests)} PASS")

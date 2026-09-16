import ast
import json

import numpy as np
from p45_reproductions import crowd_topology_exp002_v1_reproduction as R


def test_independent_module_does_not_import_original_calculator():
    tree = ast.parse(R.Path(R.__file__).read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert not any("crowd_topology_exp002_v1" in name and "reproduction" not in name for name in imported)


def test_source_boundary_and_identity():
    rounds, k2, k3 = R.read_source()
    assert rounds.tolist() == list(range(1, 1238))
    assert np.all(k2 >= 0) and np.all(k3 >= 0) and np.all(k2 + k3 > 0)
    assert R.D1_DEGREE == 234 and R.COLUMN_COUNT == 39 and R.COLUMN_SIZE == 6
    assert R.COLUMN_SIZE / R.D1_DEGREE == 1 / 39


def test_deterministic_targets_match_after_independent_calculation():
    _, k2, k3 = R.read_source()
    values = R.deterministic_quantities(k2, k3)
    values.pop("holdout_n")
    assert R.compare_after_calculation(values)["status"] == "PASS"


def test_fresh_mc_uses_new_seed_and_multinomial_path():
    assert R.FRESH_SEED == 2026082304
    assert R.FRESH_SEED != 2026082303
    source = R.Path(R.__file__).read_text(encoding="utf-8")
    assert ".multinomial(" in source
    assert "full_counts[:, 0]" in source


def test_small_multinomial_probe_is_deterministic():
    n = np.asarray([29, 1283, 2050], dtype=np.int64)
    first = R.multinomial_null(n, 0.1, repetitions=500)
    second = R.multinomial_null(n, 0.1, repetitions=500)
    assert first == second


def test_saved_result_guardrails():
    result = json.loads(R.RAW_RESULT.read_text(encoding="utf-8"))
    assert result["status"] == "INDEPENDENT_REPRODUCTION_PASS"
    assert result["round_1238_plus_used"] is False
    assert result["original_files_changed"] is False
    assert result["strong_null_limitation_recorded"] is True
    assert result["independent_empirical_replication"] is False
    assert result["promotion_candidate"] is False
    assert result["prospective_signal_peeking"] == 0


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"{len(tests)}/{len(tests)} PASS")


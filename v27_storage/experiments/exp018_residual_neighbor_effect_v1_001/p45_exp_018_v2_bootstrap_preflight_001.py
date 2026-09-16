from __future__ import annotations

import json
import math
import random
from pathlib import Path


OUTPUT = Path(__file__).resolve().parent / "P45_EXP_018_V2_BOOTSTRAP_IMPLEMENTATION_PREFLIGHT_001.json"
B = 100_000
SEED = 20260827
U95_INDEX = 94_999


def bootstrap_dummy(clusters: list[tuple[int, float, float]]) -> tuple[float, list[int]]:
    ordered = sorted(clusters, key=lambda item: item[0])
    if ordered != clusters:
        raise RuntimeError("DUMMY_CLUSTER_ORDER_NOT_ASCENDING")
    rng = random.Random(SEED)
    deltas: list[float] = []
    first_indices: list[int] = []
    n_split = len(ordered)
    for replicate in range(B):
        indices = [rng.randrange(n_split) for _ in range(n_split)]
        if replicate == 0:
            first_indices = indices
        numerator = sum(ordered[index][1] for index in indices)
        denominator = sum(ordered[index][2] for index in indices)
        if denominator <= 0:
            raise RuntimeError("EXP_018_EXECUTION_BLOCKED_BOOTSTRAP_INVALID_REPLICATE")
        delta = numerator / denominator
        if not math.isfinite(delta):
            raise RuntimeError("EXP_018_EXECUTION_BLOCKED_BOOTSTRAP_INVALID_REPLICATE")
        deltas.append(delta)
    deltas.sort()
    return deltas[U95_INDEX], first_indices


def main() -> int:
    # Synthetic contributions only; no P45 historical outcomes are loaded.
    development_dummy = [(2, -0.2, 2.0), (3, 0.4, 3.0), (4, 0.1, 1.5)]
    holdout_dummy = [(868, 0.3, 2.5), (869, -0.1, 1.0)]
    dev_u95_a, dev_first_a = bootstrap_dummy(development_dummy)
    dev_u95_b, dev_first_b = bootstrap_dummy(development_dummy)
    hold_u95_a, hold_first_a = bootstrap_dummy(holdout_dummy)
    hold_u95_b, hold_first_b = bootstrap_dummy(holdout_dummy)
    if dev_u95_a != dev_u95_b or hold_u95_a != hold_u95_b:
        raise RuntimeError("BOOTSTRAP_REPRODUCIBILITY_FAILURE")
    if dev_first_a != dev_first_b or hold_first_a != hold_first_b:
        raise RuntimeError("RNG_REPRODUCIBILITY_FAILURE")

    payload = {
        "experiment_family": "EXP-018",
        "version": "V2",
        "mode": "DUMMY_DATA_BOOTSTRAP_IMPLEMENTATION_PREFLIGHT",
        "historical_outcomes_loaded": False,
        "method": "TARGET_ROUND_CLUSTER_PERCENTILE_BOOTSTRAP",
        "sampling_unit": "TARGET_ROUND_WITH_VALID_MATCHED_STRATA",
        "population_order": "ASCENDING_TARGET",
        "replacement": True,
        "replicates": B,
        "seed": SEED,
        "rng": "Python random.Random",
        "split_rng_initialization": "INDEPENDENT random.Random(20260827) FOR EACH SPLIT",
        "draw_method": "rng.randrange(N_SPLIT)",
        "u95_method": "SORT_ASCENDING_AND_SELECT_FIXED_ORDER_STATISTIC",
        "u95_one_based_order_statistic": 95_000,
        "u95_python_zero_based_index": U95_INDEX,
        "interpolation": "NONE",
        "invalid_replicate_policy": "BLOCK_WITHOUT_DROP_OR_REDRAW",
        "dummy_development_u95": dev_u95_a,
        "dummy_holdout_u95": hold_u95_a,
        "development_reproducible": True,
        "holdout_reproducible": True,
        "implementation_ambiguity_remaining": False,
        "status": "PASS",
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

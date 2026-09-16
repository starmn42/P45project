"""Independent reproduction of EXP-CROWD-TOPO-002-V1.

This module deliberately does not import the original experiment calculator.
The original result is opened only after deterministic quantities have been
computed from the immutable CSV.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "v27_storage/experiments/crowd_topology_exp001_v1/exp_crowd_topo_001_v1_draws_1_1237.csv"
ORIGINAL_PROTOCOL = ROOT / "00_P45_STATE/experiment_lab/EXP-CROWD-TOPO-002/EXP_CROWD_TOPO_002_V1_LOCKED_PROTOCOL.md"
ORIGINAL_REPORT = ROOT / "00_P45_STATE/experiment_lab/EXP-CROWD-TOPO-002/EXP_CROWD_TOPO_002_V1_FINAL_RESULT.md"
ORIGINAL_CALCULATOR = ROOT / "src/p45_experiments/crowd_topology_exp002_v1.py"
ORIGINAL_RESULT = ROOT / "v27_storage/experiments/crowd_topology_exp002_v1/EXP_CROWD_TOPO_002_V1_RESULT.json"
OUTPUT_DIR = ROOT / "v27_storage/experiments/crowd_topology_exp002_v1/independent_reproduction_001"
RAW_RESULT = OUTPUT_DIR / "INDEPENDENT_REPRODUCTION_RAW_RESULT.json"
MC_SUMMARY = OUTPUT_DIR / "FRESH_MULTINOMIAL_MC_SUMMARY.json"

SNAPSHOT_SHA256 = "1a03abc4babec2cd64eda8c426429747352e412bc1f63e5513f7794aa980ef32"
ORIGINAL_HASHES = {
    "protocol": "7d32357ff787a50e7ef67ecbcf8e38780b2886b0bf6d4ffedb1871cf35edd8c3",
    "report": "fa249ddd3872773a4e5491c6849532be3d17b05724f8a777c7edaba1da594065",
    "calculator": "6b7a39481ccb0e799b56aed32634c7d4128c698e18a1411ec9df99e41a77da03",
    "result": "993a3ef157a149e4d2dfb846e3aaf7a105e5f1c316d4e68dd564e83ca62dbe58",
    "snapshot": SNAPSHOT_SHA256,
}
P0 = 1.0 / 39.0
D1_DEGREE = 234
COLUMN_COUNT = 39
COLUMN_SIZE = 6
REPETITIONS = 300_000
FRESH_SEED = 2026082304
TOLERANCE = 1e-10
REPRODUCER_VERSION = "EXP-CROWD-TOPO-002-INDEPENDENT-REPRODUCER-1.0"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def protected_hashes() -> dict[str, str]:
    return {
        "protocol": file_sha256(ORIGINAL_PROTOCOL),
        "report": file_sha256(ORIGINAL_REPORT),
        "calculator": file_sha256(ORIGINAL_CALCULATOR),
        "result": file_sha256(ORIGINAL_RESULT),
        "snapshot": file_sha256(SNAPSHOT),
    }


def read_source() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if protected_hashes() != ORIGINAL_HASHES:
        raise RuntimeError("ORIGINAL_FILE_HASH_MISMATCH")
    rounds: list[int] = []
    k2: list[int] = []
    k3: list[int] = []
    with SNAPSHOT.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                round_no = int(row["round"])
                value2 = int(row["k2"])
                value3 = int(row["k3"])
            except (KeyError, TypeError, ValueError) as exc:
                raise RuntimeError("EXP_CROWD_TOPO_002_REPRO_BLOCKED_DATA") from exc
            if value2 < 0 or value3 < 0 or value2 + value3 <= 0:
                raise RuntimeError(f"EXP_CROWD_TOPO_002_REPRO_BLOCKED_DATA:{round_no}")
            rounds.append(round_no)
            k2.append(value2)
            k3.append(value3)
    if rounds != list(range(1, 1238)):
        raise RuntimeError("EXP_CROWD_TOPO_002_REPRO_BLOCKED_DATA:ROUND_RANGE")
    if math.comb(6, 1) * math.comb(39, 1) != D1_DEGREE:
        raise RuntimeError("EXP_CROWD_TOPO_002_REPRO_BLOCKED_DATA:D1")
    if COLUMN_SIZE != 6 or COLUMN_COUNT != 39 or COLUMN_SIZE / D1_DEGREE != P0:
        raise RuntimeError("EXP_CROWD_TOPO_002_REPRO_BLOCKED_DATA:COLUMN_IDENTITY")
    return np.asarray(rounds), np.asarray(k2, dtype=np.float64), np.asarray(k3, dtype=np.float64)


def deterministic_quantities(k2: np.ndarray, k3: np.ndarray) -> dict[str, Any]:
    n = k2 + k3
    expectation = n / COLUMN_COUNT
    variance = n * (1.0 / COLUMN_COUNT) * (38.0 / COLUMN_COUNT)
    contributions = ((k2 - expectation) ** 2) / variance
    train = contributions[:800]
    holdout = contributions[800:]
    first_half, second_half = holdout[:218], holdout[218:]
    block_effects = np.asarray([chunk.mean() - 1.0 for chunk in np.split(holdout, 23)])

    def remove_largest(count: int) -> float:
        ordered = np.sort(holdout)
        return float(ordered[:-count].mean() - 1.0)

    return {
        "train_d": float(train.mean() - 1.0),
        "holdout_d": float(holdout.mean() - 1.0),
        "holdout_q": float(holdout.sum()),
        "holdout_half1_d": float(first_half.mean() - 1.0),
        "holdout_half2_d": float(second_half.mean() - 1.0),
        "positive_19round_blocks": int((block_effects > 0).sum()),
        "top1_removed_d": remove_largest(1),
        "top5_removed_d": remove_largest(5),
        "top10_removed_d": remove_largest(10),
        "top10_q_share": float(np.sort(holdout)[-10:].sum() / holdout.sum()),
        "holdout_n": (k2[800:] + k3[800:]).astype(np.int64),
    }


def compare_after_calculation(reproduced: dict[str, Any]) -> dict[str, Any]:
    original = json.loads(ORIGINAL_RESULT.read_text(encoding="utf-8"))
    fields = (
        "train_d", "holdout_d", "holdout_q", "holdout_half1_d",
        "holdout_half2_d", "top1_removed_d", "top5_removed_d", "top10_removed_d",
    )
    deltas = {field: abs(float(reproduced[field]) - float(original[field])) for field in fields}
    block_match = reproduced["positive_19round_blocks"] == original["positive_19round_blocks"]
    if any(delta > TOLERANCE for delta in deltas.values()) or not block_match:
        raise RuntimeError("REPRODUCTION_MISMATCH_DETERMINISTIC")
    return {
        "original": {field: original[field] for field in fields} | {
            "positive_19round_blocks": original["positive_19round_blocks"]
        },
        "deltas": deltas,
        "block_count_match": block_match,
        "status": "PASS",
    }


def multinomial_null(n_values: np.ndarray, observed_d: float, repetitions: int = REPETITIONS) -> dict[str, Any]:
    rng = np.random.default_rng(FRESH_SEED)
    probabilities = np.full(COLUMN_COUNT, 1.0 / COLUMN_COUNT, dtype=np.float64)
    sum_r = np.zeros(repetitions, dtype=np.float64)
    batch_size = 100_000
    for n_value in n_values:
        expected = float(n_value) / COLUMN_COUNT
        variance = float(n_value) * (1.0 / COLUMN_COUNT) * (38.0 / COLUMN_COUNT)
        for start in range(0, repetitions, batch_size):
            stop = min(start + batch_size, repetitions)
            full_counts = rng.multinomial(int(n_value), probabilities, size=stop - start)
            fixed_column = full_counts[:, 0]
            sum_r[start:stop] += ((fixed_column - expected) ** 2) / variance
    null_d = sum_r / len(n_values) - 1.0
    exceedances = int((null_d >= observed_d).sum())
    p_value = (1.0 + exceedances) / (repetitions + 1.0)
    standard_error = math.sqrt(p_value * (1.0 - p_value) / repetitions)
    quantiles = np.quantile(null_d, [0.95, 0.99, 0.999], method="linear")
    return {
        "method": "39-category multinomial; fixed column index 0",
        "seed": FRESH_SEED,
        "repetitions": repetitions,
        "exceedances": exceedances,
        "p_value": p_value,
        "standard_error": standard_error,
        "null_d_mean": float(null_d.mean()),
        "null_d_q95": float(quantiles[0]),
        "null_d_q99": float(quantiles[1]),
        "null_d_q999": float(quantiles[2]),
        "observed_gt_null_q999": bool(observed_d > quantiles[2]),
    }


def run() -> dict[str, Any]:
    before = protected_hashes()
    rounds, k2, k3 = read_source()
    deterministic = deterministic_quantities(k2, k3)
    n_values = deterministic.pop("holdout_n")
    comparison = compare_after_calculation(deterministic)
    mc = multinomial_null(n_values, deterministic["holdout_d"])
    after = protected_hashes()
    if before != after or after != ORIGINAL_HASHES:
        raise RuntimeError("ORIGINAL_FILES_CHANGED")
    status = (
        "INDEPENDENT_REPRODUCTION_PASS"
        if comparison["status"] == "PASS" and deterministic["holdout_d"] > 0 and mc["p_value"] <= 0.05
        else "REPRODUCTION_MISMATCH_MONTE_CARLO"
    )
    result = {
        "reproducer_version": REPRODUCER_VERSION,
        "status": status,
        "data_sha256": SNAPSHOT_SHA256,
        "data_range": "1~1237",
        "round_1238_plus_used": False,
        "source_rows": int(len(rounds)),
        "deterministic": deterministic,
        "comparison": comparison,
        "fresh_mc": mc,
        "original_hashes_before": before,
        "original_hashes_after": after,
        "original_files_changed": False,
        "strong_null_limitation_recorded": True,
        "independent_empirical_replication": False,
        "novelty_status": "NOVELTY_NOT_CONFIRMED",
        "promotion_candidate": False,
        "prospective_protocol_changed": False,
        "prospective_signal_peeking": 0,
        "draw_engine_changed": 0,
    }
    result["reproducer_sha256"] = file_sha256(Path(__file__))
    result["result_hash"] = hashlib.sha256(canonical_json(result).encode("utf-8")).hexdigest()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MC_SUMMARY.write_text(json.dumps(mc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("preflight", "run"))
    args = parser.parse_args(argv)
    if args.command == "preflight":
        rounds, k2, k3 = read_source()
        output = {"status": "PASS", "rows": len(rounds), "range": [int(rounds[0]), int(rounds[-1])], "k23_min": int(np.min(k2 + k3))}
    else:
        output = run()
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


"""Exact combinatorial calibration audit for EXP-CROWD-TOPO-002 V1."""
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
LOCK_NOTE = ROOT / "00_P45_STATE/experiment_lab/EXP-CROWD-TOPO-002/calibration_audit_001/EXP_CROWD_TOPO_002_CALIBRATION_AUDIT_001_LOCKED_NOTE.md"
OUTPUT_DIR = ROOT / "v27_storage/experiments/crowd_topology_exp002_v1/calibration_audit_001"
RAW_RESULT = OUTPUT_DIR / "CALIBRATION_AUDIT_RAW_RESULT.json"
BOOTSTRAP_SUMMARY = OUTPUT_DIR / "CALIBRATION_BOOTSTRAP_SUMMARY.json"

SNAPSHOT_SHA256 = "1a03abc4babec2cd64eda8c426429747352e412bc1f63e5513f7794aa980ef32"
LOCK_NOTE_SHA256 = "b13666657e524a555a6387f180e2aa4fff1a1860366ac72bd120ab3cc0ba91ff"
M = math.comb(45, 6)
D1_DEGREE = 234
BOOTSTRAPS = 200_000
BOOTSTRAP_SEED = 2026082305
AUDIT_VERSION = "EXP-CROWD-TOPO-002-CALIBRATION-AUDIT-001-CALCULATOR-1.0"

PROTECTED_FILES = {
    "exp002_protocol": ROOT / "00_P45_STATE/experiment_lab/EXP-CROWD-TOPO-002/EXP_CROWD_TOPO_002_V1_LOCKED_PROTOCOL.md",
    "exp002_report": ROOT / "00_P45_STATE/experiment_lab/EXP-CROWD-TOPO-002/EXP_CROWD_TOPO_002_V1_FINAL_RESULT.md",
    "exp002_calculator": ROOT / "src/p45_experiments/crowd_topology_exp002_v1.py",
    "exp002_result": ROOT / "v27_storage/experiments/crowd_topology_exp002_v1/EXP_CROWD_TOPO_002_V1_RESULT.json",
    "reproduction_calculator": ROOT / "src/p45_reproductions/crowd_topology_exp002_v1_reproduction.py",
    "reproduction_result": ROOT / "v27_storage/experiments/crowd_topology_exp002_v1/independent_reproduction_001/INDEPENDENT_REPRODUCTION_RAW_RESULT.json",
    "snapshot": SNAPSHOT,
}
EXPECTED_PROTECTED_HASHES = {
    "exp002_protocol": "7d32357ff787a50e7ef67ecbcf8e38780b2886b0bf6d4ffedb1871cf35edd8c3",
    "exp002_report": "fa249ddd3872773a4e5491c6849532be3d17b05724f8a777c7edaba1da594065",
    "exp002_calculator": "6b7a39481ccb0e799b56aed32634c7d4128c698e18a1411ec9df99e41a77da03",
    "exp002_result": "993a3ef157a149e4d2dfb846e3aaf7a105e5f1c316d4e68dd564e83ca62dbe58",
    "reproduction_calculator": "534aa5f306b09bce4081c270a81deeae608310668a0458bae69dedb786abec3a",
    "reproduction_result": "4249f14c62d4fc75f887c1039b6ae6946c955b42f0c665323b63c2ff4150a392",
    "snapshot": SNAPSHOT_SHA256,
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def protected_hashes() -> dict[str, str]:
    return {name: file_sha256(path) for name, path in PROTECTED_FILES.items()}


def load_data() -> dict[str, np.ndarray]:
    if file_sha256(LOCK_NOTE) != LOCK_NOTE_SHA256:
        raise RuntimeError("CALIBRATION_AUDIT_LOCK_HASH_MISMATCH")
    if protected_hashes() != EXPECTED_PROTECTED_HASHES:
        raise RuntimeError("PROTECTED_INPUT_HASH_MISMATCH")
    values: dict[str, list[int]] = {key: [] for key in ("round", "k1", "k2", "k3", "sold_lines")}
    with SNAPSHOT.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                parsed = {key: int(row[key]) for key in values}
            except (KeyError, TypeError, ValueError) as exc:
                raise RuntimeError("CALIBRATION_AUDIT_DATA_BLOCKED") from exc
            if min(parsed["k1"], parsed["k2"], parsed["k3"]) < 0 or parsed["sold_lines"] <= 1:
                raise RuntimeError(f"CALIBRATION_AUDIT_DATA_BLOCKED:{parsed['round']}")
            for key in values:
                values[key].append(parsed[key])
    if values["round"] != list(range(1, 1238)):
        raise RuntimeError("CALIBRATION_AUDIT_DATA_BLOCKED:ROUND_RANGE")
    return {key: np.asarray(items, dtype=np.float64) for key, items in values.items()}


def calculate_components(data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    k1, k2, k3, sold = data["k1"], data["k2"], data["k3"], data["sold_lines"]
    k23 = k2 + k3
    scale = (M * M) / (sold * (sold - 1.0))
    selected = scale * k2 * (k2 - 1.0)
    center_duplicate = scale * 6.0 * k1 * (k1 - 1.0)
    d1_pair = scale * (5.0 / 39.0) * k1 * k23
    residual = selected - center_duplicate - d1_pair
    return {
        "selected": selected,
        "center_duplicate": center_duplicate,
        "d1_pair": d1_pair,
        "predicted": center_duplicate + d1_pair,
        "residual": residual,
    }


def student_t(values: np.ndarray) -> float:
    standard_deviation = float(np.std(values, ddof=1))
    if standard_deviation == 0:
        raise RuntimeError("CALIBRATION_AUDIT_ZERO_SD")
    return float(math.sqrt(len(values)) * np.mean(values) / standard_deviation)


def fixed_block_wild(values: np.ndarray) -> dict[str, Any]:
    if len(values) != 437 or len(values) != 23 * 19:
        raise RuntimeError("CALIBRATION_AUDIT_BLOCK_GEOMETRY")
    observed = student_t(values)
    centered = values - values.mean()
    blocks = centered.reshape(23, 19)
    block_sums = blocks.sum(axis=1)
    fixed_sum_squares = float(np.square(centered).sum())
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    exceedances = 0
    batch_size = 10_000
    for start in range(0, BOOTSTRAPS, batch_size):
        batch = min(batch_size, BOOTSTRAPS - start)
        signs = rng.integers(0, 2, size=(batch, 23), dtype=np.int8) * 2 - 1
        means = (signs @ block_sums) / len(values)
        variances = (fixed_sum_squares - len(values) * np.square(means)) / (len(values) - 1)
        t_star = math.sqrt(len(values)) * means / np.sqrt(variances)
        exceedances += int(np.count_nonzero(np.abs(t_star) >= abs(observed)))
    p_value = (1.0 + exceedances) / (BOOTSTRAPS + 1.0)
    return {"t_cal": observed, "exceedances": exceedances, "p_cal": p_value}


def calculate() -> dict[str, Any]:
    before = protected_hashes()
    data = load_data()
    parts = calculate_components(data)
    train_residual = parts["residual"][:800]
    holdout_residual = parts["residual"][800:]
    bootstrap = fixed_block_wild(holdout_residual)
    half1, half2 = holdout_residual[:218], holdout_residual[218:]
    block_means = holdout_residual.reshape(23, 19).mean(axis=1)
    order = np.argsort(np.abs(holdout_residual))[::-1]
    top_indices = order[:10]
    holdout_rounds = data["round"][800:].astype(np.int64)
    top_rounds = [
        {"round": int(holdout_rounds[index]), "cal_resid": float(holdout_residual[index]), "abs_cal_resid": float(abs(holdout_residual[index]))}
        for index in top_indices
    ]
    top_share = float(np.abs(holdout_residual[top_indices]).sum() / np.abs(holdout_residual).sum())
    selected_mean = float(parts["selected"][800:].mean())
    center_mean = float(parts["center_duplicate"][800:].mean())
    d1_mean = float(parts["d1_pair"][800:].mean())
    predicted_mean = float(parts["predicted"][800:].mean())
    holdout_mean = float(holdout_residual.mean())
    status = "NO_CALIBRATION_TENSION_DETECTED" if bootstrap["p_cal"] > 0.01 else "CALIBRATION_IDENTITY_TENSION"
    after = protected_hashes()
    if before != after or after != EXPECTED_PROTECTED_HASHES:
        raise RuntimeError("PROTECTED_INPUT_CHANGED")
    result = {
        "audit_version": AUDIT_VERSION,
        "status": status,
        "audit_protocol_sha256": LOCK_NOTE_SHA256,
        "data_sha256": SNAPSHOT_SHA256,
        "data_range": "1~1237",
        "data_rows": 1237,
        "round_1238_plus_used": False,
        "m": M,
        "d1_degree": D1_DEGREE,
        "exact_identity_locked": True,
        "k1_only_calibration_identifiable": False,
        "required_calibration_terms": ["K1(K1-1)", "K1*K23"],
        "train_mean_cal_resid": float(train_residual.mean()),
        "holdout_mean_cal_resid": holdout_mean,
        "holdout_t_cal": bootstrap["t_cal"],
        "primary_two_sided_p_cal": bootstrap["p_cal"],
        "bootstraps": BOOTSTRAPS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_exceedances": bootstrap["exceedances"],
        "selected_column_component_mean": selected_mean,
        "center_dup_component_mean": center_mean,
        "d1_pair_component_mean": d1_mean,
        "predicted_component_mean": predicted_mean,
        "observed_minus_predicted": holdout_mean,
        "holdout_half1_mean": float(half1.mean()),
        "holdout_half2_mean": float(half2.mean()),
        "positive_19round_blocks": int(np.count_nonzero(block_means > 0)),
        "top10_abs_rounds": top_rounds,
        "top10_abs_share": top_share,
        "exp002_original_status_changed": False,
        "exp002_program_interpretation": (
            "STRONG INDEPENDENT-UNIFORM NULL REJECTED; TOPOLOGY-SPECIFIC MECHANISM NOT IDENTIFIED"
            if status == "NO_CALIBRATION_TENSION_DETECTED"
            else "INTERPRETATION_BLOCKED_BY_CALIBRATION_TENSION"
        ),
        "new_experiment_created": False,
        "novelty_status": "NOVELTY_NOT_CONFIRMED",
        "promotion_candidate": False,
        "prospective_protocol_changed": False,
        "prospective_signal_peeking": 0,
        "draw_engine_changed": 0,
        "protected_hashes_before": before,
        "protected_hashes_after": after,
    }
    result["calculator_sha256"] = file_sha256(Path(__file__))
    result["result_hash"] = hashlib.sha256(canonical_json(result).encode("utf-8")).hexdigest()
    return result


def run() -> dict[str, Any]:
    result = calculate()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    BOOTSTRAP_SUMMARY.write_text(json.dumps({key: result[key] for key in (
        "holdout_mean_cal_resid", "holdout_t_cal", "primary_two_sided_p_cal",
        "bootstraps", "bootstrap_seed", "bootstrap_exceedances"
    )}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("preflight", "run"))
    args = parser.parse_args(argv)
    if args.command == "preflight":
        data = load_data()
        output = {"status": "PASS", "rows": len(data["round"]), "range": [int(data["round"][0]), int(data["round"][-1])], "n_min": int(data["sold_lines"].min())}
    else:
        output = run()
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


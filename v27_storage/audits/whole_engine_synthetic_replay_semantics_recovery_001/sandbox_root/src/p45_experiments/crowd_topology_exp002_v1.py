"""Locked EXP-CROWD-TOPO-002-V1 random-bonus column probe.

This calculator is isolated from the official DRAW engine and reuses the
immutable EXP-CROWD-TOPO-001 snapshot for rounds 1..1237 only.
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
EXP = ROOT / "v27_storage/experiments/crowd_topology_exp002_v1"
SOURCE_EXP = ROOT / "v27_storage/experiments/crowd_topology_exp001_v1"
SNAPSHOT = SOURCE_EXP / "exp_crowd_topo_001_v1_draws_1_1237.csv"
SOURCE_MANIFEST = SOURCE_EXP / "SNAPSHOT_MANIFEST.json"
SOURCE_PREFLIGHT = ROOT / "00_P45_STATE/experiment_lab/EXP-CROWD-TOPO-001/EXP_CROWD_TOPO_001_V1_SOURCE_SCHEMA_PREFLIGHT.md"
PROTOCOL = ROOT / "00_P45_STATE/experiment_lab/EXP-CROWD-TOPO-002/EXP_CROWD_TOPO_002_V1_LOCKED_PROTOCOL.md"
LOCK = EXP / "PROTOCOL_LOCK.json"
RESULT = EXP / "EXP_CROWD_TOPO_002_V1_RESULT.json"
MC_SUMMARY = EXP / "MC_SUMMARY.json"
RERUN_EVIDENCE = EXP / "DETERMINISTIC_RERUN_EVIDENCE.json"

PROTOCOL_SHA256 = "7d32357ff787a50e7ef67ecbcf8e38780b2886b0bf6d4ffedb1871cf35edd8c3"
SNAPSHOT_SHA256 = "1a03abc4babec2cd64eda8c426429747352e412bc1f63e5513f7794aa980ef32"
CALCULATOR_VERSION = "EXP-CROWD-TOPO-002-CALCULATOR-1.0"
D1_DEGREE = 234
COLUMN_COUNT = 39
COLUMN_SIZE = 6
K3_SHELL_SIZE = 228
P0 = 1.0 / COLUMN_COUNT
MC_REPETITIONS = 200_000
MC_SEED = 2026082303


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def preflight() -> dict[str, Any]:
    assertions = {
        "d1_degree_234": math.comb(6, 1) * math.comb(39, 1) == D1_DEGREE,
        "selected_column_size_6": COLUMN_SIZE == 6,
        "remaining_shell_size_228": 38 * COLUMN_SIZE == K3_SHELL_SIZE,
        "shell_partition": COLUMN_SIZE + K3_SHELL_SIZE == D1_DEGREE,
        "null_probability": COLUMN_SIZE / D1_DEGREE == P0,
        "protocol_hash": sha_file(PROTOCOL) == PROTOCOL_SHA256,
        "snapshot_hash": sha_file(SNAPSHOT) == SNAPSHOT_SHA256,
        "source_preflight_pass": "Status: `PASS`" in SOURCE_PREFLIGHT.read_text(encoding="utf-8-sig"),
    }
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    assertions["protocol_prelocked"] = (
        lock["lock_status"] == "LOCKED_BEFORE_OUTCOME_ANALYSIS"
        and lock["outcome_analyzed_at_lock"] is False
        and lock["protocol_sha256"] == PROTOCOL_SHA256
    )
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    assertions["source_manifest"] = (
        manifest["data_range"] == "1~1237"
        and manifest["rows"] == 1237
        and manifest["missing_rounds"] == 0
        and manifest["duplicate_rounds"] == 0
        and manifest["round_1238_plus_rows"] == 0
        and manifest["canonical_main_mismatch"] == 0
        and manifest["snapshot_sha256"] == SNAPSHOT_SHA256
        and manifest["shell_identity"] == {"k2": 6, "k3": 228, "total": 234, "status": "PASS"}
    )
    if not all(assertions.values()):
        failed = [key for key, value in assertions.items() if not value]
        raise RuntimeError("PREFLIGHT_FAILED:" + ",".join(failed))
    return {"status": "PASS", "assertions": assertions}


def load_locked_data() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    preflight()
    rounds: list[int] = []
    k2: list[int] = []
    k3: list[int] = []
    with SNAPSHOT.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            round_no = int(row["round"])
            x2, x3 = int(row["k2"]), int(row["k3"])
            if x2 < 0 or x3 < 0:
                raise RuntimeError(f"DATA_BLOCKED_NEGATIVE_K2_K3:{round_no}")
            if x2 + x3 <= 0:
                raise RuntimeError(f"DATA_BLOCKED_ZERO_K23:{round_no}")
            rounds.append(round_no)
            k2.append(x2)
            k3.append(x3)
    if rounds != list(range(1, 1238)):
        raise RuntimeError("DATA_BLOCKED_ROUND_RANGE")
    return np.asarray(rounds, dtype=np.int64), np.asarray(k2, dtype=np.int64), np.asarray(k3, dtype=np.int64)


def pearson_contributions(x: np.ndarray, n: np.ndarray) -> np.ndarray:
    mu = n * P0
    variance = n * P0 * (1.0 - P0)
    if np.any(variance <= 0):
        raise RuntimeError("DATA_BLOCKED_ZERO_VARIANCE")
    return np.square(x - mu) / variance


def monte_carlo(n: np.ndarray, observed_d: float) -> tuple[int, float, float]:
    rng = np.random.default_rng(MC_SEED)
    mu = n.astype(np.float64) * P0
    variance = n.astype(np.float64) * P0 * (1.0 - P0)
    exceedances = 0
    batch_size = 2_000
    for start in range(0, MC_REPETITIONS, batch_size):
        batch = min(batch_size, MC_REPETITIONS - start)
        simulated = rng.binomial(n, P0, size=(batch, len(n)))
        d_star = (np.square(simulated - mu) / variance).mean(axis=1) - 1.0
        exceedances += int(np.count_nonzero(d_star >= observed_d))
    p_value = (1.0 + exceedances) / (MC_REPETITIONS + 1.0)
    standard_error = math.sqrt(p_value * (1.0 - p_value) / MC_REPETITIONS)
    return exceedances, p_value, standard_error


def _removed_d(r_values: np.ndarray, count: int) -> float:
    keep = np.argsort(r_values)[: len(r_values) - count]
    return float(np.mean(r_values[keep]) - 1.0)


def calculate() -> dict[str, Any]:
    rounds, k2, k3 = load_locked_data()
    k23 = k2 + k3
    r_values = pearson_contributions(k2.astype(np.float64), k23.astype(np.float64))
    train_r, holdout_r = r_values[:800], r_values[800:]
    train_d = float(np.mean(train_r) - 1.0)
    base: dict[str, Any] = {
        "logical_id": "EXP-CROWD-TOPO-002-V1",
        "registry_id": "EXP-CROWD-20260823-006-V1",
        "calculator_version": CALCULATOR_VERSION,
        "protocol_sha256": PROTOCOL_SHA256,
        "snapshot_sha256": SNAPSHOT_SHA256,
        "data_range": "1~1237",
        "data_rows": int(len(rounds)),
        "round_1238_plus_used": False,
        "d1_degree": D1_DEGREE,
        "column_count": COLUMN_COUNT,
        "column_size": COLUMN_SIZE,
        "k3_shell_size": K3_SHELL_SIZE,
        "null_p": "1/39",
        "train_d": train_d,
        "train_gate": "PASS" if train_d > 0 else "FAIL",
        "holdout_d": None,
        "holdout_q": None,
        "primary_mc_p": None,
        "mc_repetitions": 0,
        "mc_seed": MC_SEED,
        "mc_exceedances": None,
        "mc_standard_error": None,
        "max_abs_z": None,
        "top10_q_share": None,
        "holdout_half1_d": None,
        "holdout_half2_d": None,
        "half_consistency": None,
        "positive_19round_blocks": None,
        "top1_removed_d": None,
        "top5_removed_d": None,
        "top10_removed_d": None,
        "independent_reproduction": "NOT_YET",
        "novelty_status": "NOVELTY_NOT_CONFIRMED",
        "promotion_candidate": False,
        "official_effect": "NONE",
        "prospective_protocol_changed": False,
        "prospective_signal_peeking": 0,
        "draw_engine_changed": 0,
    }
    if train_d <= 0:
        base["final_judgment"] = "FAILED_EARLY_TRAIN_DIRECTION"
        return base

    holdout_d = float(np.mean(holdout_r) - 1.0)
    exceedances, p_value, standard_error = monte_carlo(k23[800:], holdout_d)
    half1 = holdout_r[:218]
    half2 = holdout_r[218:]
    d1 = float(np.mean(half1) - 1.0)
    d2 = float(np.mean(half2) - 1.0)
    if d1 > 0 and d2 > 0:
        consistency = "BOTH_POSITIVE"
    elif d1 <= 0 and d2 <= 0:
        consistency = "BOTH_NONPOSITIVE"
    else:
        consistency = "MIXED"
    blocks = holdout_r.reshape(23, 19).mean(axis=1) - 1.0
    z = (k2[800:] - k23[800:] * P0) / np.sqrt(k23[800:] * P0 * (1.0 - P0))
    sorted_r = np.sort(holdout_r)[::-1]
    q = float(np.sum(holdout_r))
    base.update({
        "holdout_d": holdout_d,
        "holdout_q": q,
        "primary_mc_p": p_value,
        "mc_repetitions": MC_REPETITIONS,
        "mc_exceedances": exceedances,
        "mc_standard_error": standard_error,
        "max_abs_z": float(np.max(np.abs(z))),
        "top10_q_share": float(np.sum(sorted_r[:10]) / q),
        "holdout_half1_d": d1,
        "holdout_half2_d": d2,
        "half_consistency": consistency,
        "positive_19round_blocks": int(np.count_nonzero(blocks > 0)),
        "top1_removed_d": _removed_d(holdout_r, 1),
        "top5_removed_d": _removed_d(holdout_r, 5),
        "top10_removed_d": _removed_d(holdout_r, 10),
        "final_judgment": "SUPPORTED_WITHIN_EXPERIMENT" if holdout_d > 0 and p_value <= 0.05 else "FAILED",
    })
    return base


def run() -> dict[str, Any]:
    first = calculate()
    second = calculate()
    if canonical_json(first) != canonical_json(second):
        raise RuntimeError("REPRODUCTION_MISMATCH")
    first["deterministic_rerun"] = "PASS"
    first["calculator_sha256"] = sha_file(Path(__file__))
    first["result_hash"] = hashlib.sha256(canonical_json(first).encode("utf-8")).hexdigest()
    EXP.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(first, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MC_SUMMARY.write_text(json.dumps({key: first[key] for key in (
        "holdout_d", "holdout_q", "primary_mc_p", "mc_repetitions", "mc_seed",
        "mc_exceedances", "mc_standard_error", "max_abs_z", "top10_q_share"
    )}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    RERUN_EVIDENCE.write_text(json.dumps({
        "status": "PASS", "same_input": True, "same_code": True, "same_seed": True,
        "canonical_first_sha256": hashlib.sha256(canonical_json(first | {"deterministic_rerun": "PASS", "calculator_sha256": first["calculator_sha256"], "result_hash": first["result_hash"]}).encode("utf-8")).hexdigest(),
        "compared_fields": ["train_d", "holdout_d", "mc_exceedances", "primary_mc_p", "holdout_half1_d", "holdout_half2_d", "positive_19round_blocks", "top1_removed_d", "top5_removed_d", "top10_removed_d"]
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return first


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("preflight", "run"))
    args = parser.parse_args(argv)
    output = preflight() if args.command == "preflight" else run()
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


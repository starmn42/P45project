"""Execute the single locked EXP-003 retrospective/walk-forward validation."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
import uuid
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from p45_v27.protection_manifest import build_manifest

from .calculator import BANDS, DISTANCES, VERSION, build_feature_state, evaluate_locked_feature


ROOT = Path(__file__).resolve().parents[3]
DOC_DIR = ROOT / "00_P45_STATE/experiment_lab/EXP-003_NUMBER_TRANSITION"
LOCK_PATH = DOC_DIR / "EXP003_PROTOCOL_LOCK.json"
SNAPSHOT_PATH = ROOT / "v27_storage/experiments/exp003/data/exp003_draws_1_1237.csv"
DB_PATH = ROOT / "v27_storage/experiments/exp003/exp003_research.sqlite3"
REPORT_PATH = ROOT / "v27_storage/experiments/exp003/exp003_locked_run_result.json"
EXPECTED_PROTOCOL = "feb78db79d1dbebbfe6f41b097651aa27acdc8b7b7d7d4260e1e6645e6035329"
EXPECTED_DATA = "b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0"
EXPECTED_PROTECTED = "7c1458328a17a0824622c00ce1f54996e22ed4c2e9d04180be4ad9029ba8febb"
SEED = 202608160310
REPETITIONS = 100_000
KST = timezone(timedelta(hours=9))
WINDOW_ORDER = ("OVERALL", "FIRST_HALF", "SECOND_HALF", "RECENT100", "RECENT50", "RECENT20_TEST_ONLY")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _load_lock_and_verify() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    canonical = {
        "alias": lock["alias"],
        "calculator_version": lock["calculator_version"],
        "experiment_id": lock["experiment_id"],
        "files": lock["files"],
        "protocol_version": lock["protocol_version"],
        "schema_version": lock["schema_version"],
    }
    calculated = _canonical_hash(canonical)
    if calculated != EXPECTED_PROTOCOL or lock["protocol_hash"] != EXPECTED_PROTOCOL:
        raise RuntimeError("LOCK_MISMATCH_ABORT:PROTOCOL_HASH")
    if any(_sha(DOC_DIR / item["path"]) != item["sha256"] for item in lock["files"]):
        raise RuntimeError("LOCK_MISMATCH_ABORT:PROTOCOL_FILE")
    if _sha(SNAPSHOT_PATH) != EXPECTED_DATA:
        raise RuntimeError("LOCK_MISMATCH_ABORT:DATA_HASH")
    if build_manifest(ROOT)["canonical_manifest_sha256"] != EXPECTED_PROTECTED:
        raise RuntimeError("LOCK_MISMATCH_ABORT:PROTECTED_CANONICAL")
    connection = sqlite3.connect(DB_PATH)
    try:
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("LOCK_MISMATCH_ABORT:DB_INTEGRITY")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("LOCK_MISMATCH_ABORT:DB_FK")
        tables = ("experiment_run", "prediction_lock", "transition_outcome", "metric_result", "final_judgment")
        if any(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in tables):
            raise RuntimeError("LOCK_MISMATCH_ABORT:RESULT_ROWS_NOT_ZERO")
    finally:
        connection.close()
    return lock


def _load_rows() -> list[dict[str, object]]:
    with SNAPSHOT_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        raw = list(csv.DictReader(handle))
    rows = []
    for row in raw:
        rows.append({
            "round": int(row["round"]),
            "main": tuple(int(row[f"n{i}"]) for i in range(1, 7)),
            "bonus": int(row["bonus"]),
        })
    if [row["round"] for row in rows] != list(range(1, 1238)):
        raise RuntimeError("LOCK_MISMATCH_ABORT:DATA_RANGE")
    return rows


def _window_indices(total: int) -> dict[str, list[int]]:
    half = total // 2
    return {
        "OVERALL": list(range(total)),
        "FIRST_HALF": list(range(half)),
        "SECOND_HALF": list(range(half, total)),
        "RECENT100": list(range(total - 100, total)),
        "RECENT50": list(range(total - 50, total)),
        "RECENT20_TEST_ONLY": list(range(total - 20, total)),
    }


def _hypergeom_pmf(exposure: int, draws: int) -> np.ndarray:
    result = np.zeros(min(exposure, draws) + 1, dtype=float)
    denominator = math.comb(45, draws)
    for hits in range(len(result)):
        if draws - hits <= 45 - exposure:
            result[hits] = math.comb(exposure, hits) * math.comb(45 - exposure, draws - hits) / denominator
    return result


def _exact_tails(exposures: Iterable[int], draws: int, observed: int) -> tuple[float, float, float]:
    distribution = np.array([1.0])
    for exposure in exposures:
        distribution = np.convolve(distribution, _hypergeom_pmf(int(exposure), draws))
    lower = float(distribution[: observed + 1].sum())
    upper = float(distribution[observed:].sum())
    return lower, upper, min(1.0, 2.0 * min(lower, upper))


def _wilson(hits: int, exposure: int) -> tuple[float | None, float | None]:
    if exposure == 0:
        return None, None
    z = 1.959963984540054
    rate = hits / exposure
    denominator = 1 + z * z / exposure
    center = (rate + z * z / (2 * exposure)) / denominator
    margin = z * math.sqrt(rate * (1 - rate) / exposure + z * z / (4 * exposure * exposure)) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def _holm(raw: dict[int, float]) -> dict[int, float]:
    ordered = sorted(raw, key=lambda distance: (raw[distance], distance))
    adjusted: dict[int, float] = {}
    running = 0.0
    count = len(ordered)
    for index, distance in enumerate(ordered):
        running = max(running, min(1.0, raw[distance] * (count - index)))
        adjusted[distance] = running
    return adjusted


def _variance(exposures: Iterable[int], draws: int) -> float:
    total = 0.0
    for exposure in exposures:
        fraction = exposure / 45
        total += draws * fraction * (1 - fraction) * ((45 - draws) / 44)
    return total


def _calculate_metrics(features: list[dict[str, object]], outcomes: list[dict[str, object]]) -> tuple[dict, dict, dict]:
    windows = _window_indices(len(features))
    all_metrics: dict[str, dict[str, dict[int, dict[str, object]]]] = {"MAIN": {}, "INTEGRATED": {}}
    observed_z: dict[str, dict[str, np.ndarray]] = {"MAIN": {}, "INTEGRATED": {}}
    variance_map: dict[str, dict[str, np.ndarray]] = {"MAIN": {}, "INTEGRATED": {}}
    for scope, draws, hit_key in (("MAIN", 6, "main_hits"), ("INTEGRATED", 7, "integrated_hits")):
        baseline = draws / 45
        for window, indices in windows.items():
            raw_values: dict[int, float] = {}
            metrics: dict[int, dict[str, object]] = {}
            z_values = np.zeros(45, dtype=float)
            variances = np.zeros(45, dtype=float)
            for distance in DISTANCES:
                exposure_vector = [features[index]["distance_exposure"][distance] for index in indices]
                exposure = int(sum(exposure_vector))
                observed = int(sum(outcomes[index][hit_key][distance] for index in indices))
                expected = exposure * baseline
                lower_p, upper_p, raw_p = _exact_tails(exposure_vector, draws, observed)
                low, high = _wilson(observed, exposure)
                variance = _variance(exposure_vector, draws)
                z_value = (observed - expected) / math.sqrt(variance) if variance > 0 else 0.0
                raw_values[distance] = raw_p
                z_values[distance] = z_value
                variances[distance] = variance
                metrics[distance] = {
                    "scope": scope,
                    "window": window,
                    "distance": distance,
                    "rounds": len(indices),
                    "exposure": exposure,
                    "observation": observed,
                    "expected_rate": baseline,
                    "observed_rate": observed / exposure if exposure else None,
                    "risk_difference": observed / exposure - baseline if exposure else None,
                    "wilson_low": low,
                    "wilson_high": high,
                    "raw_p_lower": lower_p,
                    "raw_p_upper": upper_p,
                    "raw_p_two_sided": raw_p,
                    "standardized_deviation": z_value,
                    "status": "CALCULATED" if exposure else "NO_EXPOSURE",
                }
            adjusted = _holm(raw_values)
            for distance in DISTANCES:
                metrics[distance]["holm_p"] = adjusted[distance]
            all_metrics[scope][window] = metrics
            observed_z[scope][window] = z_values
            variance_map[scope][window] = variances
    return all_metrics, observed_z, variance_map


def _max_t(
    features: list[dict[str, object]],
    observed_z: dict[str, dict[str, np.ndarray]],
    variance_map: dict[str, dict[str, np.ndarray]],
) -> dict[str, dict[str, np.ndarray]]:
    windows = _window_indices(len(features))
    membership = {window: np.zeros(len(features), dtype=bool) for window in WINDOW_ORDER}
    for window, indices in windows.items():
        membership[window][indices] = True
    rng = np.random.default_rng(SEED)
    exceed: dict[str, dict[str, np.ndarray]] = {
        scope: {window: np.zeros(45, dtype=np.int64) for window in WINDOW_ORDER}
        for scope in ("MAIN", "INTEGRATED")
    }
    chunk_size = 5_000
    for scope, draws in (("MAIN", 6), ("INTEGRATED", 7)):
        expectations = {
            window: np.array([
                sum(features[index]["distance_exposure"][distance] for index in windows[window]) * draws / 45
                for distance in DISTANCES
            ])
            for window in WINDOW_ORDER
        }
        for start in range(0, REPETITIONS, chunk_size):
            size = min(chunk_size, REPETITIONS - start)
            totals = {window: np.zeros((size, 45), dtype=np.int16) for window in WINDOW_ORDER}
            for index, feature in enumerate(features):
                sampled = rng.multivariate_hypergeometric(
                    [feature["distance_exposure"][distance] for distance in DISTANCES], draws, size=size
                ).astype(np.int16, copy=False)
                for window in WINDOW_ORDER:
                    if membership[window][index]:
                        totals[window] += sampled
            for window in WINDOW_ORDER:
                variance = variance_map[scope][window]
                safe = np.where(variance > 0, np.sqrt(variance), np.inf)
                simulated_z = (totals[window] - expectations[window]) / safe
                max_abs = np.max(np.abs(simulated_z), axis=1)
                exceed[scope][window] += np.array([
                    np.count_nonzero(max_abs >= abs(observed_z[scope][window][distance]) - 1e-15)
                    for distance in DISTANCES
                ])
    return {
        scope: {
            window: (exceed[scope][window] + 1) / (REPETITIONS + 1)
            for window in WINDOW_ORDER
        }
        for scope in ("MAIN", "INTEGRATED")
    }


def _direction(metric: dict[str, object]) -> int:
    value = metric["risk_difference"]
    return 0 if value is None or value == 0 else (1 if value > 0 else -1)


def _summarize(all_metrics: dict, max_t: dict) -> dict[str, object]:
    for scope in ("MAIN", "INTEGRATED"):
        for window in WINDOW_ORDER:
            for distance in DISTANCES:
                all_metrics[scope][window][distance]["maxT_p"] = float(max_t[scope][window][distance])
    overall = all_metrics["MAIN"]["OVERALL"]
    strongest_positive = max(DISTANCES, key=lambda d: (overall[d]["risk_difference"] if overall[d]["risk_difference"] is not None else -math.inf, -d))
    strongest_negative = min(DISTANCES, key=lambda d: (overall[d]["risk_difference"] if overall[d]["risk_difference"] is not None else math.inf, d))
    holm_pass = [d for d in DISTANCES if overall[d]["holm_p"] < 0.05]
    maxt_pass = [d for d in DISTANCES if overall[d]["maxT_p"] < 0.05]
    supported = []
    for distance in DISTANCES:
        metric = overall[distance]
        direction = _direction(metric)
        if not direction or metric["holm_p"] >= 0.05 or metric["maxT_p"] >= 0.05:
            continue
        baseline = metric["expected_rate"]
        wilson_outside = metric["wilson_low"] > baseline if direction > 0 else metric["wilson_high"] < baseline
        halves_same = all(_direction(all_metrics["MAIN"][window][distance]) == direction for window in ("FIRST_HALF", "SECOND_HALF"))
        recent100_same = _direction(all_metrics["MAIN"]["RECENT100"][distance]) == direction
        recent50 = all_metrics["MAIN"]["RECENT50"][distance]
        recent50_confirmed_opposite = recent50["wilson_high"] < baseline if direction > 0 else recent50["wilson_low"] > baseline
        if wilson_outside and halves_same and recent100_same and not recent50_confirmed_opposite:
            supported.append(distance)
    final = "SUPPORTED" if supported else "FAILED"
    explanation = "A" if supported else ("C" if any(abs(overall[d]["risk_difference"] or 0) > 0 for d in DISTANCES) else "D")
    return {
        "final_judgment": final,
        "explanation_code": explanation,
        "holm_pass_distances": holm_pass,
        "maxT_pass_distances": maxt_pass,
        "supported_distances": supported,
        "distance_0": overall[0],
        "strongest_positive_distance": strongest_positive,
        "strongest_positive_result": overall[strongest_positive],
        "strongest_negative_distance": strongest_negative,
        "strongest_negative_result": overall[strongest_negative],
    }


def run() -> dict[str, object]:
    lock = _load_lock_and_verify()
    rows = _load_rows()
    run_id = str(uuid.uuid4())
    started_at = datetime.now(KST).isoformat()
    features: list[dict[str, object]] = []
    outcomes: list[dict[str, object]] = []
    for index in range(1, len(rows)):
        current = rows[index]
        feature = build_feature_state(rows[index - 1]["main"], int(current["round"]))
        if feature["source_end_round"] != int(current["round"]) - 1:
            raise RuntimeError("FUTURE_LEAKAGE")
        features.append(feature)
        outcomes.append(evaluate_locked_feature(feature, current["main"], int(current["bonus"])))
    all_metrics, observed_z, variance_map = _calculate_metrics(features, outcomes)
    max_t = _max_t(features, observed_z, variance_map)
    summary = _summarize(all_metrics, max_t)
    report: dict[str, object] = {
        "experiment_id": lock["experiment_id"],
        "run_id": run_id,
        "run_status": "BACKTESTED_WALKFORWARD_COMPLETE",
        "protocol_hash": EXPECTED_PROTOCOL,
        "data_snapshot_hash": EXPECTED_DATA,
        "calculator_version": VERSION,
        "seed": SEED,
        "repetitions": REPETITIONS,
        "evaluation_range": "2~1237",
        "walkforward_rounds": len(features),
        "transitions_tested": len(features),
        "distances_tested": 45,
        "future_leakage": 0,
        "hash_mismatch": 0,
        "failed_rounds": 0,
        "skipped_rounds": 0,
        "walkforward_signal_exposure_main": sum(sum(f["distance_exposure"].values()) for f in features),
        "metrics": all_metrics,
        **summary,
        "official_engine_changed": False,
        "official_db_changed": False,
        "recommendation_created": False,
        "completed_at": datetime.now(KST).isoformat(),
    }
    report["result_hash"] = _canonical_hash(report)
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "INSERT INTO experiment_run VALUES(?,?,?,?,?,?)",
            (run_id, EXPECTED_PROTOCOL, EXPECTED_DATA, report["run_status"], started_at, report["completed_at"]),
        )
        for feature, outcome in zip(features, outcomes, strict=True):
            connection.execute(
                "INSERT INTO prediction_lock VALUES(?,?,?,?,?,1)",
                (run_id, feature["evaluation_round"], feature["source_end_round"], json.dumps(feature, ensure_ascii=False, sort_keys=True, separators=(",", ":")), feature["feature_hash"]),
            )
            connection.execute(
                "INSERT INTO transition_outcome VALUES(?,?,?,?,?,?)",
                (run_id, outcome["evaluation_round"], json.dumps(outcome["main_hits"], sort_keys=True), json.dumps(outcome["integrated_hits"], sort_keys=True), json.dumps(outcome["band_transition"], sort_keys=True), outcome["outcome_hash"]),
            )
        for scope in ("MAIN", "INTEGRATED"):
            for window in WINDOW_ORDER:
                for distance in DISTANCES:
                    metric = all_metrics[scope][window][distance]
                    connection.execute(
                        "INSERT INTO metric_result VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (run_id, scope, distance, window, metric["exposure"], metric["observation"], metric["observed_rate"] or 0.0, metric["risk_difference"] or 0.0, metric["wilson_low"], metric["wilson_high"], metric["raw_p_two_sided"], metric["holm_p"], metric["maxT_p"], metric["status"]),
                    )
        compact = {key: value for key, value in report.items() if key != "metrics"}
        connection.execute(
            "INSERT INTO final_judgment VALUES(?,?,?,?)",
            (run_id, report["final_judgment"], json.dumps(compact, ensure_ascii=False, sort_keys=True, separators=(",", ":")), report["result_hash"]),
        )
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("DB_FK_FAILURE")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    report = run()
    compact = {key: value for key, value in report.items() if key != "metrics"}
    print(json.dumps(compact, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
PROTOCOL = EXP_DIR / "P45_EXP_017_CONSENSUS_NUMBER_EFFECT_V1_PROTOCOL_001.md"
LOCK = EXP_DIR / "P45_EXP_017_PROTOCOL_LOCK_001.md"
TRACE = ROOT / "v27_storage/experiments/trio_orbit_v1_001/P45_TRIO_ORBIT_V1_ROUND_TRACE_001.csv"
CANONICAL = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
OUTPUT = EXP_DIR / "P45_EXP_017_CONSENSUS_NUMBER_EFFECT_V1_CALCULATION_001.json"

EXPECTED_PROTOCOL_SHA = "da86d5192cf25a7d45b3c8eb8d68a55d06f720613cd2335dc41f06fdf0cd83a3"
EXPECTED_LOCK_SHA = "839ae4c0e96a19823d8b900447cb8082fd696dc67bbac4e75d28c504e381272c"
EXPECTED_STRUCTURE = {
    "targets": 1237,
    "active_rounds": 1104,
    "total_exposures": 2267,
    "k_distribution": {"0": 133, "1": 342, "2": 448, "3": 249, "4": 48, "5": 12, "6": 5},
    "max_k": 6,
    "development": {"targets": 866, "active_rounds": 769, "total_exposures": 1592},
    "walkforward": {"targets": 371, "active_rounds": 335, "total_exposures": 675},
}
NULL_RATE = 6 / 45
ALPHA = 0.05
N_PERMUTATIONS = 100_000
RANDOM_SEED = 20260827


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_trio(value: str) -> set[int]:
    values = {int(item) for item in value.split()}
    if len(values) != 3 or not all(1 <= item <= 45 for item in values):
        raise RuntimeError("INVALID_LOCKED_TRIO")
    return values


def load_candidates() -> list[tuple[int, tuple[int, ...]]]:
    records: list[tuple[int, tuple[int, ...]]] = []
    with TRACE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            fixed = set().union(*(parse_trio(row[f"fixed_{label}"]) for label in "ABC"))
            linked = set().union(*(parse_trio(row[f"linked_{label}"]) for label in "ABC"))
            records.append((int(row["target_round"]), tuple(sorted(fixed & linked))))
    return records


def structural_summary(records: list[tuple[int, tuple[int, ...]]]) -> dict:
    def part(items: list[tuple[int, tuple[int, ...]]]) -> dict:
        ks = [len(candidate) for _, candidate in items]
        return {
            "targets": len(items),
            "active_rounds": sum(k > 0 for k in ks),
            "total_exposures": sum(ks),
        }

    ks = [len(candidate) for _, candidate in records]
    development = [item for item in records if 2 <= item[0] <= 867]
    walkforward = [item for item in records if 868 <= item[0] <= 1238]
    return {
        "targets": len(records),
        "active_rounds": sum(k > 0 for k in ks),
        "total_exposures": sum(ks),
        "k_distribution": {str(k): Counter(ks).get(k, 0) for k in range(7)},
        "max_k": max(ks),
        "development": part(development),
        "walkforward": part(walkforward),
    }


def load_main6(start: int, end: int) -> dict[int, tuple[int, ...]]:
    draws: dict[int, tuple[int, ...]] = {}
    with CANONICAL.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            target = int(row["round"])
            if start <= target <= end:
                main6 = tuple(sorted(int(row[f"n{i}"]) for i in range(1, 7)))
                if len(set(main6)) != 6 or not all(1 <= value <= 45 for value in main6):
                    raise RuntimeError("INVALID_CANONICAL_MAIN6")
                draws[target] = main6
    if set(draws) != set(range(start, end + 1)):
        raise RuntimeError("CANONICAL_RANGE_MISMATCH")
    return draws


def exact_upper_tail(ks: list[int], observed: int) -> float:
    distribution = [1.0]
    denominator = math.comb(45, 6)
    for k in ks:
        upper = min(k, 6)
        pmf = [math.comb(k, h) * math.comb(45 - k, 6 - h) / denominator for h in range(upper + 1)]
        updated = [0.0] * (len(distribution) + upper)
        for total, probability in enumerate(distribution):
            for h, mass in enumerate(pmf):
                updated[total + h] += probability * mass
        distribution = updated
    return float(math.fsum(distribution[observed:]))


def evaluate(records: list[tuple[int, tuple[int, ...]]], start: int, end: int) -> tuple[dict, list[tuple[int, ...]], list[tuple[int, ...]]]:
    selected = [item for item in records if start <= item[0] <= end]
    draws_by_target = load_main6(start, end)
    candidates = [candidate for _, candidate in selected]
    draws = [draws_by_target[target] for target, _ in selected]
    hits = sum(len(set(candidate) & set(draw)) for candidate, draw in zip(candidates, draws))
    exposures = sum(map(len, candidates))
    rate = hits / exposures
    p_primary = exact_upper_tail([len(candidate) for candidate in candidates], hits)
    result = {
        "range": f"{start}..{end}",
        "targets": len(selected),
        "active_rounds": sum(bool(candidate) for candidate in candidates),
        "exposures": exposures,
        "hits": hits,
        "inclusion_rate": rate,
        "null_rate": NULL_RATE,
        "absolute_lift": rate - NULL_RATE,
        "absolute_lift_percentage_points": (rate - NULL_RATE) * 100,
        "exact_p_primary_one_sided_upper": p_primary,
        "rate_condition": rate > NULL_RATE,
        "p_condition": p_primary <= ALPHA,
    }
    return result, candidates, draws


def target_shuffle(candidates: list[tuple[int, ...]], draws: list[tuple[int, ...]], observed: int) -> dict:
    candidate_mask = np.zeros((len(candidates), 45), dtype=np.uint8)
    draw_mask = np.zeros((len(draws), 45), dtype=np.uint8)
    for row, values in enumerate(candidates):
        if values:
            candidate_mask[row, np.asarray(values) - 1] = 1
    for row, values in enumerate(draws):
        draw_mask[row, np.asarray(values) - 1] = 1
    hit_matrix = candidate_mask @ draw_mask.T
    row_index = np.arange(len(candidates))
    rng = np.random.default_rng(RANDOM_SEED)
    greater_or_equal = 0
    for _ in range(N_PERMUTATIONS):
        permuted_total = int(hit_matrix[row_index, rng.permutation(len(draws))].sum())
        greater_or_equal += permuted_total >= observed
    return {
        "executed": True,
        "permutations": N_PERMUTATIONS,
        "seed": RANDOM_SEED,
        "greater_or_equal": greater_or_equal,
        "p_secondary_add_one": (greater_or_equal + 1) / (N_PERMUTATIONS + 1),
        "status": "ROBUSTNESS_CONTEXT_ONLY",
    }


def main() -> int:
    actual_protocol_sha = sha256(PROTOCOL)
    actual_lock_sha = sha256(LOCK)
    if actual_protocol_sha != EXPECTED_PROTOCOL_SHA or actual_lock_sha != EXPECTED_LOCK_SHA:
        raise RuntimeError("EXP_017_EXECUTION_BLOCKED_LOCK_MISMATCH")

    records = load_candidates()
    structure = structural_summary(records)
    if structure != EXPECTED_STRUCTURE:
        raise RuntimeError("EXP_017_EXECUTION_BLOCKED_STRUCTURAL_MISMATCH")

    development, development_candidates, development_draws = evaluate(records, 2, 867)
    development_pass = development["rate_condition"] and development["p_condition"]
    development["verdict"] = "DEVELOPMENT_SCREEN_POSITIVE" if development_pass else "FAILED_NOT_SUPPORTED"

    robustness = target_shuffle(development_candidates, development_draws, development["hits"])
    walkforward = {"executed": False, "reason": "DEVELOPMENT_FAILED_PROTOCOL_GATE"}
    if development_pass:
        walkforward_result, _, _ = evaluate(records, 868, 1238)
        walkforward_pass = walkforward_result["rate_condition"] and walkforward_result["p_condition"]
        walkforward_result["executed"] = True
        walkforward_result["verdict"] = "HISTORICAL_WALKFORWARD_POSITIVE" if walkforward_pass else "FAILED_NOT_REPRODUCED"
        walkforward = walkforward_result
        final_verdict = "HISTORICAL_SCREEN_AND_WALKFORWARD_POSITIVE_PROSPECTIVE_REQUIRED" if walkforward_pass else "FAILED_NOT_REPRODUCED"
    else:
        final_verdict = "FAILED_NOT_SUPPORTED"

    output = {
        "experiment_id": "EXP-017 / EXP-DRAW-20260827-017-V1",
        "execution_mode": "LOCKED_HISTORICAL_BACKTEST_CONDITIONAL_WALKFORWARD",
        "lock_verify": {
            "protocol_sha_expected": EXPECTED_PROTOCOL_SHA,
            "protocol_sha_actual": actual_protocol_sha,
            "protocol_sha_status": "PASS",
            "lock_sha_expected": EXPECTED_LOCK_SHA,
            "lock_sha_actual": actual_lock_sha,
            "lock_sha_status": "PASS",
        },
        "structural_reproduction": {**structure, "structural_match": "PASS"},
        "development": development,
        "walkforward": walkforward,
        "secondary_robustness": robustness,
        "final_verdict": final_verdict,
        "prospective": {"required": bool(development_pass and walkforward.get("verdict") == "HISTORICAL_WALKFORWARD_POSITIVE"), "start_target": 1239, "outcome_read_or_written": False},
        "protection": {"future_leakage": 0, "sealed_1239_changed": False, "prospective_outcome_changes": 0},
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

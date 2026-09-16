from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
PROTOCOL = EXP_DIR / "P45_EXP_018_RESIDUAL_NEIGHBOR_EFFECT_V2_PROTOCOL_001.md"
LOCK = EXP_DIR / "P45_EXP_018_V2_PROTOCOL_LOCK_001.md"
SOURCE = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
OUTPUT = EXP_DIR / "P45_EXP_018_RESIDUAL_NEIGHBOR_EFFECT_V2_CALCULATION_001.json"

EXPECTED_PROTOCOL_SHA = "a75bbe585f01be80ced3dd1252aad2f3b5de2e1b0d93e5db3d3ade73408c3127"
EXPECTED_LOCK_SHA = "da2c637e994fbd0c39b49a97471f342a1dbc332e91fa2817b8b9fbf37b7a8909"
EXPECTED_SOURCE_SHA = "1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"
EXPECTED_STRUCTURE = {
    "historical_targets": 1237,
    "development_targets": 866,
    "holdout_targets": 371,
    "matched_target_rounds": 1236,
    "matched_strata": 6854,
    "matched_neighbor_exposures": 9183,
    "matched_control_exposures": 15823,
    "unmatched_neighbor_exposures": 2964,
    "match_rate": 0.7559891331192887,
    "age_undefined_exclusions": 315,
    "max_neighbor_candidates": 12,
    "candidate_distribution": {"4": 4, "5": 3, "6": 18, "7": 54, "8": 150, "9": 242, "10": 344, "11": 252, "12": 170},
}
B = 100_000
SEED = 20260827
U95_INDEX = 94_999
ALPHA = 0.05
DELTA_PRACTICAL = 0.0100


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_main6() -> dict[int, tuple[int, ...]]:
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA:
        raise RuntimeError("EXP_018_V2_EXECUTION_BLOCKED_SOURCE_MISMATCH")
    draws: dict[int, tuple[int, ...]] = {}
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            target = int(row["round"])
            values = tuple(sorted(int(row[f"n{i}"]) for i in range(1, 7)))
            if len(set(values)) != 6 or not all(1 <= value <= 45 for value in values):
                raise RuntimeError("EXP_018_V2_EXECUTION_BLOCKED_SOURCE_MISMATCH")
            draws[target] = values
    if set(draws) != set(range(1, 1239)):
        raise RuntimeError("EXP_018_V2_EXECUTION_BLOCKED_SOURCE_MISMATCH")
    return draws


def build_structure(draws: dict[int, tuple[int, ...]]) -> tuple[list[dict], dict]:
    last_seen: dict[int, int] = {}
    all_numbers = set(range(1, 46))
    targets: list[dict] = []
    undefined_total = 0
    neighbor_counts: list[int] = []
    total_neighbor_candidates = 0
    unmatched_neighbor_total = 0

    for target in range(2, 1239):
        previous_round = target - 1
        previous = set(draws[previous_round])
        for value in previous:
            last_seen[value] = previous_round

        raw_neighbors = {candidate for value in previous for candidate in (value - 1, value + 1) if 1 <= candidate <= 45}
        neighbors = raw_neighbors - previous
        controls = (all_numbers - previous) - neighbors
        neighbor_counts.append(len(neighbors))
        total_neighbor_candidates += len(neighbors)

        neighbor_by_age: dict[int, list[int]] = defaultdict(list)
        control_by_age: dict[int, list[int]] = defaultdict(list)
        undefined_neighbors = 0
        undefined_controls = 0
        for value in sorted(neighbors):
            if value not in last_seen:
                undefined_neighbors += 1
            else:
                neighbor_by_age[previous_round - last_seen[value]].append(value)
        for value in sorted(controls):
            if value not in last_seen:
                undefined_controls += 1
            else:
                control_by_age[previous_round - last_seen[value]].append(value)
        undefined_total += undefined_neighbors + undefined_controls

        valid_ages = sorted(set(neighbor_by_age) & set(control_by_age))
        no_control_neighbors = sum(len(neighbor_by_age[age]) for age in set(neighbor_by_age) - set(control_by_age))
        unmatched_neighbor_total += undefined_neighbors + no_control_neighbors
        strata = [
            {"target": target, "age": age, "neighbors": tuple(neighbor_by_age[age]), "controls": tuple(control_by_age[age])}
            for age in valid_ages
        ]
        targets.append({"target": target, "neighbor_candidates": len(neighbors), "strata": strata})

    all_strata = [stratum for item in targets for stratum in item["strata"]]
    matched_neighbor = sum(len(stratum["neighbors"]) for stratum in all_strata)
    matched_control = sum(len(stratum["controls"]) for stratum in all_strata)
    summary = {
        "historical_targets": len(targets),
        "development_targets": sum(item["target"] <= 867 for item in targets),
        "holdout_targets": sum(item["target"] >= 868 for item in targets),
        "matched_target_rounds": sum(bool(item["strata"]) for item in targets),
        "matched_strata": len(all_strata),
        "matched_neighbor_exposures": matched_neighbor,
        "matched_control_exposures": matched_control,
        "unmatched_neighbor_exposures": unmatched_neighbor_total,
        "match_rate": matched_neighbor / total_neighbor_candidates,
        "age_undefined_exclusions": undefined_total,
        "max_neighbor_candidates": max(neighbor_counts),
        "candidate_distribution": {str(k): v for k, v in sorted(Counter(neighbor_counts).items())},
    }
    return targets, summary


def exact_upper_tail(strata: list[dict], observed: int) -> float:
    distribution = [1.0]
    for stratum in strata:
        n1 = stratum["n1"]
        n0 = stratum["n0"]
        total_hits = stratum["a"] + stratum["c"]
        lower = max(0, total_hits - n0)
        upper = min(n1, total_hits)
        denominator = math.comb(n1 + n0, total_hits)
        pmf = [0.0] * (upper + 1)
        for neighbor_hits in range(lower, upper + 1):
            pmf[neighbor_hits] = math.comb(n1, neighbor_hits) * math.comb(n0, total_hits - neighbor_hits) / denominator
        updated = [0.0] * (len(distribution) + upper)
        for current, probability in enumerate(distribution):
            for neighbor_hits in range(lower, upper + 1):
                updated[current + neighbor_hits] += probability * pmf[neighbor_hits]
        distribution = updated
    return float(math.fsum(distribution[observed:]))


def percentile_cluster_bootstrap(clusters: list[tuple[int, float, float]]) -> float:
    ordered = sorted(clusters, key=lambda item: item[0])
    if ordered != clusters:
        raise RuntimeError("EXP_018_V2_EXECUTION_BLOCKED_STRUCTURAL_MISMATCH")
    numerators = [item[1] for item in ordered]
    denominators = [item[2] for item in ordered]
    n_split = len(ordered)
    rng = random.Random(SEED)
    deltas: list[float] = []
    for _ in range(B):
        numerator = 0.0
        denominator = 0.0
        for _ in range(n_split):
            index = rng.randrange(n_split)
            numerator += numerators[index]
            denominator += denominators[index]
        if denominator <= 0:
            raise RuntimeError("EXP_018_V2_EXECUTION_BLOCKED_BOOTSTRAP_INVALID_REPLICATE")
        delta = numerator / denominator
        if not math.isfinite(delta):
            raise RuntimeError("EXP_018_V2_EXECUTION_BLOCKED_BOOTSTRAP_INVALID_REPLICATE")
        deltas.append(delta)
    deltas.sort()
    return deltas[U95_INDEX]


def evaluate_split(targets: list[dict], draws: dict[int, tuple[int, ...]], start: int, end: int) -> dict:
    selected = [item for item in targets if start <= item["target"] <= end]
    evaluated_strata: list[dict] = []
    clusters: list[tuple[int, float, float]] = []
    for item in selected:
        target_outcome = set(draws[item["target"]])
        cluster_numerator = 0.0
        cluster_weight = 0.0
        for stratum in item["strata"]:
            n1 = len(stratum["neighbors"])
            n0 = len(stratum["controls"])
            a = len(set(stratum["neighbors"]) & target_outcome)
            c = len(set(stratum["controls"]) & target_outcome)
            weight = n1 * n0 / (n1 + n0)
            contribution = weight * (a / n1 - c / n0)
            evaluated_strata.append({"target": item["target"], "age": stratum["age"], "n1": n1, "n0": n0, "a": a, "c": c, "weight": weight, "contribution": contribution})
            cluster_numerator += contribution
            cluster_weight += weight
        if item["strata"]:
            clusters.append((item["target"], cluster_numerator, cluster_weight))

    neighbor_exposures = sum(stratum["n1"] for stratum in evaluated_strata)
    control_exposures = sum(stratum["n0"] for stratum in evaluated_strata)
    neighbor_hits = sum(stratum["a"] for stratum in evaluated_strata)
    control_hits = sum(stratum["c"] for stratum in evaluated_strata)
    total_weight = math.fsum(stratum["weight"] for stratum in evaluated_strata)
    delta_match = math.fsum(stratum["contribution"] for stratum in evaluated_strata) / total_weight
    p_primary = exact_upper_tail(evaluated_strata, neighbor_hits)
    u95_delta = percentile_cluster_bootstrap(clusters)
    if p_primary <= ALPHA and delta_match >= DELTA_PRACTICAL:
        verdict = "POSITIVE_PRACTICALLY_RELEVANT"
    elif u95_delta < DELTA_PRACTICAL:
        verdict = "NO_PRACTICALLY_USEFUL_EFFECT"
    else:
        verdict = "INCONCLUSIVE"
    return {
        "range": f"{start}..{end}",
        "targets": len(selected),
        "matched_target_rounds": len(clusters),
        "matched_strata": len(evaluated_strata),
        "neighbor_exposures": neighbor_exposures,
        "control_exposures": control_exposures,
        "neighbor_hits": neighbor_hits,
        "control_hits": control_hits,
        "neighbor_pooled_hit_rate": neighbor_hits / neighbor_exposures,
        "control_pooled_hit_rate": control_hits / control_exposures,
        "delta_match": delta_match,
        "delta_match_percentage_points": delta_match * 100,
        "exact_p_primary_one_sided_upper": p_primary,
        "bootstrap_method": "TARGET_ROUND_CLUSTER_PERCENTILE_BOOTSTRAP",
        "bootstrap_n": B,
        "bootstrap_seed": SEED,
        "bootstrap_rng": "Python random.Random independently initialized for split",
        "u95_delta": u95_delta,
        "u95_delta_percentage_points": u95_delta * 100,
        "split_verdict": verdict,
    }


def final_decision(development: str, holdout: str) -> tuple[str, bool, str]:
    no_effect = "NO_PRACTICALLY_USEFUL_EFFECT"
    positive = "POSITIVE_PRACTICALLY_RELEVANT"
    if development == no_effect and holdout == no_effect:
        return "AXIS_CLOSED_NO_PRACTICALLY_USEFUL_RESIDUAL_NEIGHBOR_EFFECT", False, "T-1 MAIN6 -> numerical label ±1 adjacency -> T MAIN6 predictive axis"
    if development == positive and holdout == positive:
        return "HISTORICAL_RESIDUAL_NEIGHBOR_EFFECT_POSITIVE", True, "NO_AXIS_CLOSURE"
    if (development == positive) != (holdout == positive):
        return "FAILED_NOT_REPRODUCED", False, "NO_AXIS_CLOSURE"
    return "INCONCLUSIVE", False, "NO_AXIS_CLOSURE / NO_SIGNAL_CLAIM"


def main() -> int:
    protocol_sha = sha256(PROTOCOL)
    lock_sha = sha256(LOCK)
    if protocol_sha != EXPECTED_PROTOCOL_SHA or lock_sha != EXPECTED_LOCK_SHA:
        raise RuntimeError("EXP_018_V2_EXECUTION_BLOCKED_LOCK_MISMATCH")
    draws = load_main6()
    targets, structure = build_structure(draws)
    if structure != EXPECTED_STRUCTURE:
        raise RuntimeError("EXP_018_V2_EXECUTION_BLOCKED_STRUCTURAL_MISMATCH")

    development = evaluate_split(targets, draws, 2, 867)
    holdout = evaluate_split(targets, draws, 868, 1238)
    verdict, prospective_required, closure_scope = final_decision(development["split_verdict"], holdout["split_verdict"])
    payload = {
        "experiment_family": "EXP-018",
        "version": "V2",
        "full_id": "EXP-DRAW-20260827-018-V2",
        "protocol_sha256": protocol_sha,
        "lock_sha256": lock_sha,
        "structural_reproduction": {**structure, "status": "PASS"},
        "development": development,
        "holdout": holdout,
        "delta_practical": DELTA_PRACTICAL,
        "alpha": ALPHA,
        "final_verdict": verdict,
        "closure_scope": closure_scope,
        "signalization_allowed_now": False,
        "prospective_required": prospective_required,
        "reproducibility": "PENDING_SECOND_IDENTICAL_RUN",
        "protection": {"v1_files_changed": False, "future_leakage": 0, "sealed_1239_changes": 0, "prospective_outcome_changes": 0},
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

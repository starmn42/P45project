"""Independent reproduction and retailer-propensity audit for CROWD RETAIL EXP-001.

This module deliberately does not import the original experiment calculator.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "v27_storage/experiments/crowd_retail_exp001_v1/exp_crowd_retail_001_v1_winner_rows_262_1237.csv"
OUT = ROOT / "v27_storage/experiments/crowd_retail_exp001_v1/independent_reproduction_calibration_audit_001"
EXPECTED_SOURCE_SHA = "854ca7256219eadf574ac32ad256b84e9a5bfa42ceece09f0a09dd1eed79cd50"
ORIGINAL_REPS, ORIGINAL_SEED = 300_000, 2026082308
CAL_REPS, CAL_SEED = 300_000, 2026082309


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def retailer(row: dict[str, str]) -> str:
    store_id = row["store_id"].strip()
    if store_id:
        return f"ID:{store_id}"
    name = " ".join(row["store_name"].split())
    address = " ".join(row["store_address"].split())
    return f"EXACT:{name}|{address}"


def load_rows() -> list[dict[str, object]]:
    if file_sha(SOURCE) != EXPECTED_SOURCE_SHA:
        raise RuntimeError("RETAIL001_CALIBRATION_BLOCKED_BASELINE:SOURCE_SHA")
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        raw = list(csv.DictReader(stream))
    if any(not (262 <= int(row["round"]) <= 1237) for row in raw):
        raise RuntimeError("ROUND_RANGE_VIOLATION")
    result = []
    for row in raw:
        result.append({
            "round": int(row["round"]), "retailer": retailer(row),
            "mode": row["mode"], "online": bool(int(row["is_online"])),
        })
    return result


def probability_at_least_two(n: int, m: int, cell_size: int) -> float:
    denominator = math.comb(n, m)
    zero = math.comb(n - cell_size, m) if m <= n - cell_size else 0
    one = cell_size * math.comb(n - cell_size, m - 1) if 0 <= m - 1 <= n - cell_size else 0
    return 1.0 - (zero + one) / denominator


def cell_round_distribution(cell_sizes: list[int], manual_total: int,
                            cell_odds: list[float] | None = None) -> np.ndarray:
    """Exact conditional distribution of cells containing >=2 selected slots."""
    odds = cell_odds or [1.0] * len(cell_sizes)
    table: dict[tuple[int, int], float] = {(0, 0): 1.0}
    for size, weight in zip(cell_sizes, odds):
        nxt: dict[tuple[int, int], float] = defaultdict(float)
        for (chosen, collisions), mass in table.items():
            for q in range(min(size, manual_total - chosen) + 1):
                nxt[(chosen + q, collisions + int(q >= 2))] += mass * math.comb(size, q) * weight**q
        scale = max(nxt.values(), default=1.0)
        table = {key: value / scale for key, value in nxt.items()}
    width = max((collisions for chosen, collisions in table if chosen == manual_total), default=0)
    result = np.zeros(width + 1)
    for (chosen, collisions), mass in table.items():
        if chosen == manual_total:
            result[collisions] += mass
    total = result.sum()
    if not total > 0:
        raise RuntimeError("CONDITIONAL_DISTRIBUTION_EMPTY")
    return result / total


def aggregate(distributions: Iterable[np.ndarray]) -> np.ndarray:
    result = np.array([1.0])
    for distribution in distributions:
        result = np.convolve(result, distribution)
    result /= result.sum()
    return result


def draw_summary(pmf: np.ndarray, observed: int, reps: int, seed: int) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    simulations = rng.choice(np.arange(len(pmf)), size=reps, p=pmf)
    exceedances = int(np.count_nonzero(simulations >= observed))
    p_value = (exceedances + 1) / (reps + 1)
    return {
        "randomizations": reps, "seed": seed, "exceedances": exceedances,
        "p": p_value, "mc_standard_error": math.sqrt(p_value * (1 - p_value) / reps),
        "null_mean": float(simulations.mean()),
        "q95": float(np.quantile(simulations, .95, method="higher")),
        "q99": float(np.quantile(simulations, .99, method="higher")),
        "q999": float(np.quantile(simulations, .999, method="higher")),
    }


def original_reproduction(rows: list[dict[str, object]]) -> dict[str, object]:
    eligible = [row for row in rows if row["mode"] in ("자동", "수동") and not row["online"]]
    by_round: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in eligible:
        by_round[int(row["round"])].append(row)
    observed = 0
    expected = 0.0
    pairs = 0
    expected_pairs = 0.0
    duplicate = 0
    max_cell = (0, 0, "")
    distributions = []
    for round_no in range(262, 1238):
        round_rows = by_round[round_no]
        n = len(round_rows)
        m = sum(row["mode"] == "수동" for row in round_rows)
        groups: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in round_rows:
            groups[str(row["retailer"])].append(row)
        sizes = [len(group) for group in groups.values()]
        if n:
            distributions.append(cell_round_distribution(sizes, m))
        for key, group in groups.items():
            size = len(group)
            manual = sum(row["mode"] == "수동" for row in group)
            observed += int(manual >= 2)
            expected += probability_at_least_two(n, m, size)
            pairs += math.comb(manual, 2)
            if n >= 2:
                expected_pairs += math.comb(size, 2) * math.comb(m, 2) / math.comb(n, 2)
            duplicate += int(size >= 2)
            max_cell = max(max_cell, (manual, -round_no, key))
    random = draw_summary(aggregate(distributions), observed, ORIGINAL_REPS, ORIGINAL_SEED)
    counts = {mode: sum(row["mode"] == mode for row in rows) for mode in ("자동", "수동", "반자동")}
    result = {
        "raw_rows": len(rows), "auto_rows": counts["자동"], "manual_rows": counts["수동"],
        "semiauto_excluded": counts["반자동"], "online_excluded": sum(bool(row["online"]) for row in rows),
        "duplicate_capable_cells": duplicate, "observed_s_cell": observed, "expected_s_cell": expected,
        "s_pair": pairs, "expected_pair": expected_pairs, "max_manual_multiplicity": max_cell[0],
        "max_manual_round": -max_cell[1], "max_manual_retailer": max_cell[2], "randomization": random,
    }
    expected_fixed = {"observed_s_cell": 132, "expected_s_cell": 56.97188240042372,
                      "s_pair": 469, "expected_pair": 168.8878974918936,
                      "duplicate_capable_cells": 150, "max_manual_multiplicity": 10}
    for key, expected_value in expected_fixed.items():
        actual = result[key]
        if isinstance(expected_value, float):
            if abs(float(actual) - expected_value) > 1e-10:
                raise RuntimeError(f"REPRODUCTION_MISMATCH_DETERMINISTIC:{key}")
        elif actual != expected_value:
            raise RuntimeError(f"REPRODUCTION_MISMATCH_DETERMINISTIC:{key}")
    if observed <= expected or float(random["p"]) > .01:
        raise RuntimeError("REPRODUCTION_MISMATCH_RANDOMIZATION")
    return result


def beta_binomial_log_likelihood(log_params: np.ndarray, counts: list[tuple[int, int]]) -> float:
    alpha, beta = np.exp(log_params)
    base = math.lgamma(alpha) + math.lgamma(beta) - math.lgamma(alpha + beta)
    return sum(math.lgamma(a + alpha) + math.lgamma(u + beta) - math.lgamma(a + u + alpha + beta) - base
               for a, u in counts)


def fit_empirical_bayes(counts: list[tuple[int, int]]) -> dict[str, object]:
    """Deterministic 2-D Nelder-Mead maximization in log(alpha), log(beta)."""
    total_a, total_u = map(sum, zip(*counts))
    mean = total_a / (total_a + total_u)
    start = np.log([max(mean * 10, 1e-4), max((1 - mean) * 10, 1e-4)])
    simplex = [start, start + np.array([.25, 0.0]), start + np.array([0.0, .25])]
    score = lambda x: -beta_binomial_log_likelihood(np.clip(x, -12, 12), counts)
    values = [score(point) for point in simplex]
    iterations = 0
    for iterations in range(1, 2001):
        order = np.argsort(values)
        simplex = [simplex[i] for i in order]
        values = [values[i] for i in order]
        if max(np.linalg.norm(simplex[i] - simplex[0]) for i in (1, 2)) < 1e-10:
            break
        centroid = (simplex[0] + simplex[1]) / 2
        reflected = np.clip(centroid + (centroid - simplex[2]), -12, 12)
        reflected_value = score(reflected)
        if reflected_value < values[0]:
            expanded = np.clip(centroid + 2 * (reflected - centroid), -12, 12)
            expanded_value = score(expanded)
            simplex[2], values[2] = (expanded, expanded_value) if expanded_value < reflected_value else (reflected, reflected_value)
        elif reflected_value < values[1]:
            simplex[2], values[2] = reflected, reflected_value
        else:
            contracted = np.clip(centroid + .5 * (simplex[2] - centroid), -12, 12)
            contracted_value = score(contracted)
            if contracted_value < values[2]:
                simplex[2], values[2] = contracted, contracted_value
            else:
                simplex[1] = simplex[0] + .5 * (simplex[1] - simplex[0])
                simplex[2] = simplex[0] + .5 * (simplex[2] - simplex[0])
                values[1], values[2] = score(simplex[1]), score(simplex[2])
    optimum = simplex[int(np.argmin(values))]
    alpha, beta = np.exp(optimum)
    h = 1e-4
    f0 = score(optimum)
    hessian = np.zeros((2, 2))
    for i in range(2):
        ei = np.zeros(2); ei[i] = h
        hessian[i, i] = (score(optimum + ei) - 2 * f0 + score(optimum - ei)) / h**2
    e0, e1 = np.array([h, 0.]), np.array([0., h])
    hessian[0, 1] = hessian[1, 0] = (score(optimum+e0+e1)-score(optimum+e0-e1)-score(optimum-e0+e1)+score(optimum-e0-e1))/(4*h*h)
    eig = np.linalg.eigvalsh(hessian)
    return {"alpha": float(alpha), "beta": float(beta), "prior_mean": float(alpha/(alpha+beta)),
            "prior_concentration": float(alpha+beta), "iterations": iterations,
            "converged": iterations < 2000, "near_boundary": bool(np.any(np.abs(optimum) > 11.5)),
            "negative_log_likelihood_hessian_eigenvalues": [float(x) for x in eig],
            "hessian_positive_definite": bool(np.all(eig > 0))}


def exact_subset_probabilities(weights: list[float], m: int) -> dict[tuple[int, ...], float]:
    import itertools
    masses = {combo: math.prod(weights[i] for i in combo) for combo in itertools.combinations(range(len(weights)), m)}
    denominator = sum(masses.values())
    return {combo: mass / denominator for combo, mass in masses.items()}


def exact_subset_sample(weights: list[float], m: int, rng: np.random.Generator) -> tuple[int, ...]:
    n = len(weights)
    suffix = np.zeros((n + 1, m + 1)); suffix[:, 0] = 1.0
    for i in range(n - 1, -1, -1):
        for j in range(1, m + 1):
            suffix[i, j] = suffix[i + 1, j] + weights[i] * suffix[i + 1, j - 1]
    chosen = []
    remaining = m
    for i in range(n):
        if remaining == 0:
            break
        probability = weights[i] * suffix[i + 1, remaining - 1] / suffix[i, remaining]
        if rng.random() < probability:
            chosen.append(i); remaining -= 1
    if remaining:
        raise RuntimeError("SAMPLER_FAILED_TO_FILL")
    return tuple(chosen)


def validate_sampler() -> dict[str, object]:
    weights, m, reps, seed = [.35, .8, 1.7, 3.2, 5.1], 2, 200_000, 2026082310
    exact = exact_subset_probabilities(weights, m)
    rng = np.random.default_rng(seed)
    counts: dict[tuple[int, ...], int] = defaultdict(int)
    for _ in range(reps):
        counts[exact_subset_sample(weights, m, rng)] += 1
    errors = {str(key): abs(counts[key] / reps - probability) for key, probability in exact.items()}
    max_error = max(errors.values())
    passed = max_error < .005 and set(counts) == set(exact)
    if not passed:
        raise RuntimeError("CALIBRATION_BLOCKED_SAMPLER_VALIDATION")
    return {"status": "PASS", "weights": weights, "m": m, "repetitions": reps,
            "seed": seed, "max_absolute_error": max_error, "tolerance": .005,
            "exact_probabilities": {str(k): v for k, v in exact.items()},
            "empirical_probabilities": {str(k): counts[k]/reps for k in exact}}


def calibration(rows: list[dict[str, object]]) -> dict[str, object]:
    eligible = [row for row in rows if row["mode"] in ("자동", "수동") and not row["online"]]
    train_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for row in eligible:
        if int(row["round"]) <= 749:
            train_counts[str(row["retailer"])][int(row["mode"] == "자동")] += 1
    # Stored tuple order is manual, auto.
    fit_counts = [(values[0], values[1]) for values in train_counts.values()]
    eb = fit_empirical_bayes(fit_counts)
    if not eb["converged"] or eb["near_boundary"] or not eb["hessian_positive_definite"]:
        raise RuntimeError("CALIBRATION_BLOCKED_EB_FIT")
    alpha, beta = float(eb["alpha"]), float(eb["beta"])
    history: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for key, values in train_counts.items():
        history[key] = values.copy()
    by_round: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in eligible:
        if 750 <= int(row["round"]) <= 1237:
            by_round[int(row["round"])].append(row)
    distributions, round_metrics, cell_metrics = [], [], []
    propensity_hasher = hashlib.sha256()
    seen_rows = unseen_rows = all_seen_duplicate = duplicate_cells = observed_total = 0
    eval_retailers = set()
    posterior_values = []
    for round_no in range(750, 1238):
        rr = by_round[round_no]
        groups: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in rr:
            groups[str(row["retailer"])].append(row); eval_retailers.add(str(row["retailer"]))
        n, manual_total = len(rr), sum(row["mode"] == "수동" for row in rr)
        sizes, odds = [], []
        round_observed = 0
        round_all_seen = True
        for key in sorted(groups):
            a, u = history[key]
            p = (a + alpha) / (a + u + alpha + beta)
            posterior_values.append(p)
            propensity_hasher.update((canonical({"r": round_no, "retailer": key, "a": a, "u": u, "p": p}) + "\n").encode())
            group = groups[key]
            sizes.append(len(group)); odds.append(p / (1-p))
            manual = sum(row["mode"] == "수동" for row in group)
            hit = int(manual >= 2)
            round_observed += hit
            cell_metrics.append({"round": round_no, "retailer": key, "manual": manual, "observed": hit})
            if len(group) >= 2:
                duplicate_cells += 1
                if a + u > 0: all_seen_duplicate += 1
                else: round_all_seen = False
            for _ in group:
                if a + u > 0: seen_rows += 1
                else: unseen_rows += 1
        pmf = cell_round_distribution(sizes, manual_total, odds) if n else np.array([1.0])
        distributions.append(pmf)
        expectation = float(np.dot(np.arange(len(pmf)), pmf))
        observed_total += round_observed
        round_metrics.append({"round": round_no, "observed": round_observed, "expected": expectation,
                              "excess": round_observed-expectation, "n": n, "m": manual_total,
                              "all_duplicate_retailers_previously_seen": round_all_seen})
        for row in rr:  # update only after prediction/null construction for round r
            history[str(row["retailer"])][int(row["mode"] == "자동")] += 1
    total_pmf = aggregate(distributions)
    expected = float(np.dot(np.arange(len(total_pmf)), total_pmf))
    random = draw_summary(total_pmf, observed_total, CAL_REPS, CAL_SEED)
    gate = duplicate_cells >= 20 and expected >= 5
    if not gate:
        final = "INCONCLUSIVE_PROPENSITY_CALIBRATION_EXPOSURE"
    elif observed_total > expected and float(random["p"]) <= .01:
        final = "RETAILER_PROPENSITY_ROBUST_EXPLORATORY_CONCENTRATION"
    else:
        final = "NOT_ROBUST_TO_RETAILER_PROPENSITY_NULL"
    ranked = sorted(cell_metrics, key=lambda x: (-x["manual"], x["round"], x["retailer"]))
    def removed(count: int) -> float:
        # Diagnostic removal uses the corresponding round/cell expected collision contribution.
        removed_observed = sum(x["observed"] for x in ranked[:count])
        removed_expected = 0.0
        for cell in ranked[:count]:
            rm = next(x for x in round_metrics if x["round"] == cell["round"])
            rr = by_round[cell["round"]]
            group_size = sum(str(x["retailer"]) == cell["retailer"] for x in rr)
            a_u = None
            # Reconstruct the exact pre-round p from the hashed prequential sequence by replay below.
            replay = defaultdict(lambda: [0, 0], {k: v.copy() for k, v in train_counts.items()})
            for r in range(750, cell["round"] + 1):
                if r == cell["round"]:
                    a, u = replay[cell["retailer"]]; p = (a+alpha)/(a+u+alpha+beta); a_u = p
                    break
                for row in by_round[r]: replay[str(row["retailer"])][int(row["mode"] == "자동")] += 1
            group_odds = []
            group_sizes = []
            replay_groups = defaultdict(list)
            for row in rr: replay_groups[str(row["retailer"])].append(row)
            for key in sorted(replay_groups):
                a, u = replay[key]; p=(a+alpha)/(a+u+alpha+beta)
                group_sizes.append(len(replay_groups[key])); group_odds.append(p/(1-p))
            pmf_all = cell_round_distribution(group_sizes, int(rm["m"]), group_odds)
            # Marginal cell probability via marking this single cell in a two-category collision DP.
            idx = sorted(replay_groups).index(cell["retailer"])
            joint: dict[tuple[int,int],float]={(0,0):1.0}
            for j,(size,w) in enumerate(zip(group_sizes,group_odds)):
                nxt=defaultdict(float)
                for (chosen,hit),mass in joint.items():
                    for q in range(min(size,int(rm["m"])-chosen)+1):
                        nxt[(chosen+q,hit or int(j==idx and q>=2))]+=mass*math.comb(size,q)*w**q
                scale=max(nxt.values());joint={k:v/scale for k,v in nxt.items()}
            yes=sum(v for (chosen,hit),v in joint.items() if chosen==int(rm["m"]) and hit)
            den=sum(v for (chosen,hit),v in joint.items() if chosen==int(rm["m"]))
            removed_expected += yes/den
        return (observed_total-removed_observed) - (expected-removed_expected)
    first = sum(x["excess"] for x in round_metrics if x["round"] <= 993)
    second = sum(x["excess"] for x in round_metrics if x["round"] >= 994)
    quantiles = np.quantile(np.asarray(posterior_values), [.05,.25,.5,.75,.95]).tolist()
    return {"eb_fit": eb, "train_unique_retailers": len(train_counts), "eval_unique_retailers": len(eval_retailers),
            "seen_rows": seen_rows, "unseen_rows": unseen_rows, "seen_row_share": seen_rows/(seen_rows+unseen_rows),
            "duplicate_capable_cells": duplicate_cells,
            "duplicate_capable_cells_all_retailers_seen": all_seen_duplicate,
            "posterior_propensity_quantiles": dict(zip(("q05","q25","median","q75","q95"), quantiles)),
            "prequential_propensity_sequence_hash": propensity_hasher.hexdigest(),
            "observed_s_cell": observed_total, "expected_s_cell": expected, "excess": observed_total-expected,
            "enrichment": observed_total/expected, "exposure_gate": "PASS" if gate else "FAIL",
            "randomization": random, "first_half_excess": first, "second_half_excess": second,
            "top1_removed_excess": removed(1), "top5_removed_excess": removed(5),
            "final_status": final, "round_1238_plus_used": False, "outcome_future_used": 0}


def calculate() -> dict[str, object]:
    rows = load_rows()
    sampler = validate_sampler()
    return {"source_sha256": file_sha(SOURCE), "range": "262~1237", "original": original_reproduction(rows),
            "sampler_validation": sampler, "calibration": calibration(rows)}


def run() -> dict[str, object]:
    first, second = calculate(), calculate()
    if canonical(first) != canonical(second):
        raise RuntimeError("REPRODUCTION_MISMATCH")
    result = dict(first)
    result["deterministic_rerun"] = "PASS"
    result["calculator_sha256"] = file_sha(Path(__file__))
    result["canonical_result_hash"] = hashlib.sha256(canonical(first).encode()).hexdigest()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "independent_reproduction_calibration_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "conditional_sampler_validation.json").write_text(
        json.dumps(result["sampler_validation"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "eb_fit_report.json").write_text(
        json.dumps(result["calibration"]["eb_fit"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "fresh_original_null_result.json").write_text(
        json.dumps(result["original"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "calibrated_monte_carlo_result.json").write_text(
        json.dumps(result["calibration"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "deterministic_rerun_evidence.json").write_text(
        json.dumps({"status": "PASS", "runs": 2,
                    "canonical_result_hash": result["canonical_result_hash"],
                    "prequential_propensity_sequence_hash": result["calibration"]["prequential_propensity_sequence_hash"]},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))

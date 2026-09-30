"""Signal diagnostics, exact null calibration, and statistical tests for AUTO RESEARCH LOOP V1."""
from __future__ import annotations

import math
from typing import Any, Sequence

def wilson_score_interval(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / (1 + z * z / n)
    return (max(0.0, center - half), min(1.0, center + half))

def _log_comb(n: int, k: int) -> float:
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)

def binomial_pmf(k: int, n: int, p0: float) -> float:
    """Exact binomial probability mass P(X = k) with overflow protection."""
    if n == 0 or k < 0 or k > n:
        return 0.0
    if p0 <= 0.0:
        return 1.0 if k == 0 else 0.0
    if p0 >= 1.0:
        return 1.0 if k == n else 0.0
    log_prob = _log_comb(n, k) + k * math.log(p0) + (n - k) * math.log(1.0 - p0)
    return math.exp(log_prob) if log_prob > -709.0 else 0.0

def binomial_exact_one_sided_upper(k: int, n: int, p0: float) -> float:
    """Exact one-sided upper-tail enrichment p-value P(X >= k)."""
    if n == 0:
        return 1.0
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    p_val = sum(binomial_pmf(i, n, p0) for i in range(k, n + 1))
    return min(1.0, max(0.0, p_val))

def binomial_exact_two_sided(k: int, n: int, p0: float) -> float:
    """Exact two-sided binomial p-value using minimum-likelihood criteria."""
    if n == 0:
        return 1.0
    if k < 0 or k > n:
        return 0.0
    pmfs = [binomial_pmf(i, n, p0) for i in range(n + 1)]
    observed_pmf = pmfs[k]
    eps = 1e-12
    p_val = sum(p for p in pmfs if p <= observed_pmf + eps)
    return min(1.0, max(0.0, p_val))

def mcnemar_exact_two_sided(b: int, c: int) -> float:
    """Exact two-sided McNemar test using binomial test on discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k_min = min(b, c)
    p_val = 2.0 * sum(binomial_pmf(i, n, 0.5) for i in range(k_min + 1))
    return min(1.0, max(0.0, p_val))

def holm_bonferroni_adjust(p_values: Sequence[float]) -> list[float]:
    """Applies step-down Holm-Bonferroni correction to a family of p-values."""
    m = len(p_values)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: p_values[i])
    adj = [0.0] * m
    cum_max = 0.0
    for rank, idx in enumerate(order):
        multiplier = m - rank
        raw_adj = multiplier * p_values[idx]
        cum_max = max(cum_max, raw_adj)
        adj[idx] = min(1.0, max(0.0, cum_max))
    return adj

def calculate_trio_null_probabilities(trios: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Calculates exact probability under a fair 6/45 lottery of at least one PRIMARY (3/3) and SUPPORT (exact 2/3)."""
    t_sets = [set(t) for t in trios]
    regions = [0] * 8
    for n in range(1, 46):
        idx = 0
        for i, t in enumerate(t_sets[:3]):
            if n in t:
                idx |= (1 << i)
        regions[idx] += 1

    total_hands = math.comb(45, 6)
    primary_hands = 0
    support_hands = 0

    def generate_partitions(curr_region: int, balls_left: int, current_assignment: list[int]) -> None:
        if curr_region == 7:
            if balls_left <= regions[7]:
                current_assignment.append(balls_left)
                process_assignment(current_assignment)
                current_assignment.pop()
            return
        max_balls = min(balls_left, regions[curr_region])
        for b in range(max_balls + 1):
            current_assignment.append(b)
            generate_partitions(curr_region + 1, balls_left - b, current_assignment)
            current_assignment.pop()

    def process_assignment(k: list[int]) -> None:
        nonlocal primary_hands, support_hands
        ways = 1
        for r in range(8):
            if k[r] > 0:
                ways *= math.comb(regions[r], k[r])

        h0 = k[1] + k[3] + k[5] + k[7] if len(t_sets) > 0 else 0
        h1 = k[2] + k[3] + k[6] + k[7] if len(t_sets) > 1 else 0
        h2 = k[4] + k[5] + k[6] + k[7] if len(t_sets) > 2 else 0

        hits = [h0, h1, h2][:len(t_sets)]
        if any(h == 3 for h in hits):
            primary_hands += ways
        if any(h == 2 for h in hits):
            support_hands += ways

    generate_partitions(0, 6, [])
    return {
        "unique_candidates": 45 - regions[0],
        "primary_hands": primary_hands,
        "support_hands": support_hands,
        "total_hands": total_hands,
        "p_primary": primary_hands / total_hands,
        "p_support": support_hands / total_hands,
    }

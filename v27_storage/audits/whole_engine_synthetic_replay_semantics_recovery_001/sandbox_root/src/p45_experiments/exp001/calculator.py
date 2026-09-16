from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence

from .constants import INTEGRATED_BASELINE, MAIN_BASELINE, MAXT_SEED, RECENT20_POLICY
from .snapshot import DrawRow


def unordered_pairs() -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(1, 46), 2))


def baseline(scope: str) -> Fraction:
    if scope == "MAIN":
        return MAIN_BASELINE
    if scope == "INTEGRATED":
        return INTEGRATED_BASELINE
    raise ValueError(f"UNKNOWN_SCOPE:{scope}")


def risk_difference(observation_count: int, exposure_count: int, expected_rate: Fraction | float) -> float:
    if exposure_count <= 0:
        raise ValueError("EXPOSURE_MUST_BE_POSITIVE")
    return observation_count / exposure_count - float(expected_rate)


def holm_adjust(raw_p_values: Sequence[float]) -> list[float]:
    count = len(raw_p_values)
    order = sorted(range(count), key=lambda index: (raw_p_values[index], index))
    adjusted = [0.0] * count
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, min(1.0, (count - rank) * raw_p_values[index]))
        adjusted[index] = running
    return adjusted


def exact_binomial_two_sided(successes: int, trials: int, p0: float) -> float:
    if not (0 <= successes <= trials) or not (0 < p0 < 1):
        raise ValueError("BINOMIAL_INPUT_INVALID")
    def log_pmf(k: int) -> float:
        return math.lgamma(trials + 1) - math.lgamma(k + 1) - math.lgamma(trials - k + 1) + k * math.log(p0) + (trials - k) * math.log1p(-p0)

    observed_log = log_pmf(successes)
    total = 0.0
    for k in range(trials + 1):
        probability_log = log_pmf(k)
        if probability_log <= observed_log + 1e-12:
            total += math.exp(probability_log)
    return min(1.0, total)


def _beta_continued_fraction(a: float, b: float, x: float) -> float:
    max_iterations, epsilon, floor = 300, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    d = 1.0 / max(abs(d), floor) * (1 if d >= 0 else -1)
    h = d
    for iteration in range(1, max_iterations + 1):
        m2 = 2 * iteration
        aa = iteration * (b - iteration) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = floor if abs(d) < floor else d
        c = 1.0 + aa / c
        c = floor if abs(c) < floor else c
        d = 1.0 / d
        h *= d * c
        aa = -(a + iteration) * (qab + iteration) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = floor if abs(d) < floor else d
        c = 1.0 + aa / c
        c = floor if abs(c) < floor else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < epsilon:
            return h
    raise ArithmeticError("BETA_CONTINUED_FRACTION_DID_NOT_CONVERGE")


def regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1) / (a + b + 2):
        return front * _beta_continued_fraction(a, b, x) / a
    return 1.0 - front * _beta_continued_fraction(b, a, 1 - x) / b


def _beta_quantile(probability: float, a: float, b: float) -> float:
    low, high = 0.0, 1.0
    for _ in range(100):
        middle = (low + high) / 2
        if regularized_beta(middle, a, b) < probability:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def clopper_pearson_95(successes: int, trials: int) -> tuple[float, float]:
    if not (0 <= successes <= trials) or trials <= 0:
        raise ValueError("CLOPPER_PEARSON_INPUT_INVALID")
    lower = 0.0 if successes == 0 else _beta_quantile(0.025, successes, trials - successes + 1)
    upper = 1.0 if successes == trials else _beta_quantile(0.975, successes + 1, trials - successes)
    return lower, upper


def phi_coefficient(n11: int, n10: int, n01: int, n00: int) -> float | None:
    denominator = (n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00)
    if denominator == 0:
        return None
    return (n11 * n00 - n10 * n01) / math.sqrt(denominator)


def period_rows(rows: Sequence[DrawRow], period: str, source_end_round: int) -> list[DrawRow]:
    eligible = [row for row in rows if row.round <= source_end_round]
    eligible.sort(key=lambda row: row.round)
    if period == "OVERALL":
        return eligible
    split = len(eligible) // 2
    if period == "FIRST_HALF":
        return eligible[:split]
    if period == "SECOND_HALF":
        return eligible[split:]
    recent = {"RECENT_100": 100, "RECENT_50": 50, "RECENT_20": 20}
    if period in recent:
        return eligible[-recent[period] :]
    raise ValueError(f"UNKNOWN_PERIOD:{period}")


@dataclass(frozen=True)
class PairMetric:
    pair_a: int
    pair_b: int
    scope: str
    period: str
    observation_count: int
    exposure_count: int
    expected_count: float
    observed_rate: float
    expected_rate: float
    risk_difference: float
    lift: float
    standardized_residual: float
    clopper_pearson_low: float
    clopper_pearson_high: float
    a_exposure_count: int
    b_exposure_count: int
    phi: float | None
    raw_p: float
    test_only: bool


def calculate_pair_metrics(rows: Sequence[DrawRow], scope: str, period: str, source_end_round: int) -> list[PairMetric]:
    selected = period_rows(rows, period, source_end_round)
    p0 = float(baseline(scope))
    counts = {pair: 0 for pair in unordered_pairs()}
    number_counts = {number: 0 for number in range(1, 46)}
    for row in selected:
        numbers = row.main if scope == "MAIN" else (*row.main, row.bonus)
        for number in numbers:
            number_counts[number] += 1
        for pair in itertools.combinations(sorted(numbers), 2):
            counts[pair] += 1
    result = []
    for (a, b), observed in counts.items():
        n = len(selected)
        expected = n * p0
        rate = observed / n
        residual = (observed - expected) / math.sqrt(n * p0 * (1 - p0))
        low, high = clopper_pearson_95(observed, n)
        a_only = number_counts[a] - observed
        b_only = number_counts[b] - observed
        neither = n - observed - a_only - b_only
        result.append(PairMetric(a, b, scope, period, observed, n, expected, rate, p0, risk_difference(observed, n, p0), rate / p0, residual, low, high, number_counts[a], number_counts[b], phi_coefficient(observed, a_only, b_only, neither), exact_binomial_two_sided(observed, n, p0), period == "RECENT_20" and RECENT20_POLICY == "TEST_ONLY"))
    return result


def prediction_hash(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def max_t_null_structure(scope: str, round_count: int, repetitions: int = 1, seed: int = MAXT_SEED) -> dict[str, object]:
    if repetitions < 1 or round_count < 1:
        raise ValueError("NULL_DIMENSION_INVALID")
    width = 6 if scope == "MAIN" else 7
    rng = random.Random(seed)
    maxima = []
    p0 = float(baseline(scope))
    denominator = math.sqrt(round_count * p0 * (1 - p0))
    for _ in range(repetitions):
        counts = {pair: 0 for pair in unordered_pairs()}
        for _round in range(round_count):
            for pair in itertools.combinations(sorted(rng.sample(range(1, 46), width)), 2):
                counts[pair] += 1
        maxima.append(max(abs((value - round_count * p0) / denominator) for value in counts.values()))
    return {"null": "IID_FAIR_DRAW_NULL_MAXT", "scope": scope, "round_count": round_count, "repetitions": repetitions, "seed": seed, "max_abs_standardized_residual": maxima}

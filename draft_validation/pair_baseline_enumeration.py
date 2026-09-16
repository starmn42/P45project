"""P45 v2.7.4 PAIR amendment DRAFT validation only; not research engine code."""
from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction


def c(n: int, k: int) -> int:
    return math.comb(n, k) if 0 <= k <= n else 0


def closed_counts(m: int) -> dict[str, int]:
    denominator = c(45, m)
    double_triple = c(39, m - 6)
    at_least_one_triple = 2 * c(42, m - 3) - double_triple
    double_exact2_no_triple = c(3, 2) ** 2 * c(39, m - 4)
    single_exact2_no_triple = 2 * c(3, 2) * sum(c(3, b) * c(39, m - 2 - b) for b in (0, 1))
    no_triple_exact2_support = double_exact2_no_triple + single_exact2_no_triple
    return {
        "sample_space": denominator,
        "at_least_one_triple": at_least_one_triple,
        "double_triple": double_triple,
        "double_exact2_no_triple": double_exact2_no_triple,
        "single_exact2_no_triple": single_exact2_no_triple,
        "no_triple_exact2_support": no_triple_exact2_support,
    }


def finite_enumeration_counts(m: int) -> dict[str, int]:
    counts = {key: 0 for key in closed_counts(m)}
    for a, b in itertools.product(range(4), repeat=2):
        ways = c(3, a) * c(3, b) * c(39, m - a - b)
        counts["sample_space"] += ways
        if a == 3 or b == 3:
            counts["at_least_one_triple"] += ways
        if a == b == 3:
            counts["double_triple"] += ways
        if a < 3 and b < 3 and a == b == 2:
            counts["double_exact2_no_triple"] += ways
        if a < 3 and b < 3 and ((a == 2) ^ (b == 2)):
            counts["single_exact2_no_triple"] += ways
        if a < 3 and b < 3 and (a == 2 or b == 2):
            counts["no_triple_exact2_support"] += ways
    return counts


def result(m: int) -> dict[str, object]:
    closed = closed_counts(m)
    enumerated = finite_enumeration_counts(m)
    assert closed == enumerated
    denominator = closed["sample_space"]
    return {
        "m": m,
        "closed_form_counts": closed,
        "enumeration_counts": enumerated,
        "exact_match": True,
        "probabilities": {
            key: {
                "fraction": str(Fraction(value, denominator)),
                "decimal": value / denominator,
            }
            for key, value in closed.items()
            if key != "sample_space"
        },
    }


if __name__ == "__main__":
    payload = {"validation_scope": "DRAFT_ONLY", "results": [result(7), result(6)]}
    print(json.dumps(payload, ensure_ascii=False, indent=2))

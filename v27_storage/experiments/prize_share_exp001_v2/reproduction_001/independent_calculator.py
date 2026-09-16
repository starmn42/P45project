from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE.parent / "exp_prize_001_v2_draws_1_1237.csv"
EXPECTED_DATA_SHA = "86b14968aca3ad10b854f9d5c53eba00a786627f73e353938e1e801dc888fa21"
SEED = 2026082102
N_PERM = 100_000
CENTER = 6 * 31 / 45


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_and_assert() -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    if digest(SNAPSHOT) != EXPECTED_DATA_SHA:
        raise RuntimeError("REPRODUCTION_BLOCKED_DATA:HASH")
    with SNAPSHOT.open(encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    rounds = [int(r["round"]) for r in records]
    if rounds != list(range(1, 1238)) or len(set(rounds)) != 1237:
        raise RuntimeError("REPRODUCTION_BLOCKED_DATA:RANGE")
    mismatch = 0
    ks, sold, xs = [], [], []
    for row in records:
        r = int(row["round"])
        main = [int(row[f"main_{i}"]) for i in range(1, 7)]
        if len(set(main)) != 6 or any(v < 1 or v > 45 for v in main):
            raise RuntimeError(f"REPRODUCTION_BLOCKED_DATA:MAIN:{r}")
        price = 2000 if r <= 87 else 1000
        sales = int(row["sales_amount_krw"])
        if sales <= 0 or sales % price:
            raise RuntimeError(f"REPRODUCTION_BLOCKED_DATA:SALES:{r}")
        n = sales // price
        b = sum(v <= 31 for v in main)
        if price != int(row["price_per_game_krw"]): mismatch += 1
        if n != int(row["sold_lines"]): mismatch += 1
        if b != int(row["birthday_count"]): mismatch += 1
        ks.append(int(row["first_prize_games"])); sold.append(n); xs.append(b - CENTER)
    if mismatch:
        raise RuntimeError(f"REPRODUCTION_BLOCKED_DATA:DERIVED_MISMATCH:{mismatch}")
    assertions = {"rows": 1237, "duplicates": 0, "missing": 0, "derived_mismatch": 0,
                  "round_1238_plus": 0, "price_boundary": "PASS", "future_leakage": 0}
    return np.asarray(ks, float), np.asarray(sold, float), np.asarray(xs, float), assertions


def irls(y: np.ndarray, exposure: np.ndarray, predictor: np.ndarray) -> tuple[float, float]:
    design = np.column_stack((np.ones(predictor.size), predictor))
    coef = np.array([math.log(y.sum() / exposure.sum()), 0.0])
    offset = np.log(exposure)
    for _ in range(80):
        eta = offset + design @ coef
        mu = np.exp(eta)
        adjusted = eta + (y - mu) / mu - offset
        normal = design.T @ (mu[:, None] * design)
        rhs = design.T @ (mu * adjusted)
        updated = np.linalg.solve(normal, rhs)
        if np.max(np.abs(updated - coef)) < 1e-13:
            coef = updated
            break
        coef = updated
    return float(coef[0]), float(coef[1])


def fresh_permutation(y: np.ndarray, exposure: np.ndarray, predictor: np.ndarray, observed: float) -> tuple[float, int]:
    generator = np.random.default_rng(SEED)
    exceed = 0
    batch = 400
    total_y = float(y.sum())
    for base in range(0, N_PERM, batch):
        size = min(batch, N_PERM - base)
        permuted = generator.permuted(np.broadcast_to(predictor, (size, predictor.size)), axis=1)
        beta = np.zeros(size)
        alpha = np.full(size, math.log(total_y / exposure.sum()))
        for _ in range(30):
            eta = alpha[:, None] + beta[:, None] * permuted + np.log(exposure)[None, :]
            mu = np.exp(eta)
            g0 = (y[None, :] - mu).sum(axis=1)
            g1 = ((y[None, :] - mu) * permuted).sum(axis=1)
            h00 = mu.sum(axis=1)
            h01 = (mu * permuted).sum(axis=1)
            h11 = (mu * permuted * permuted).sum(axis=1)
            determinant = h00 * h11 - h01 * h01
            step_a = (h11 * g0 - h01 * g1) / determinant
            step_b = (-h01 * g0 + h00 * g1) / determinant
            alpha += step_a; beta += step_b
            if max(float(np.max(np.abs(step_a))), float(np.max(np.abs(step_b)))) < 1e-11:
                break
        exceed += int(np.count_nonzero(beta >= observed - 1e-12))
    return (1 + exceed) / (N_PERM + 1), exceed


def log_likelihood(y: np.ndarray, expected: np.ndarray) -> float:
    constants = np.array([math.lgamma(float(v) + 1) for v in y])
    return float(np.sum(y * np.log(expected) - expected - constants))


def walkforward(y: np.ndarray, exposure: np.ndarray, predictor: np.ndarray) -> tuple[float, list[dict]]:
    details = []
    for first, last in ((801, 900), (901, 1000), (1001, 1100), (1101, 1237)):
        end_train = first - 1
        intercept, slope = irls(y[:end_train], exposure[:end_train], predictor[:end_train])
        null_intercept = math.log(float(y[:end_train].sum() / exposure[:end_train].sum()))
        selected = slice(first - 1, last)
        alt = exposure[selected] * np.exp(intercept + slope * predictor[selected])
        null = exposure[selected] * math.exp(null_intercept)
        delta = log_likelihood(y[selected], alt) - log_likelihood(y[selected], null)
        details.append({"range": f"{first}~{last}", "delta_ll": delta})
    return sum(item["delta_ll"] for item in details), details


def main() -> None:
    y, exposure, predictor, assertions = read_and_assert()
    _, train_beta = irls(y[:800], exposure[:800], predictor[:800])
    _, holdout_beta = irls(y[800:], exposure[800:], predictor[800:])
    permutation_p, exceed = fresh_permutation(y[800:], exposure[800:], predictor[800:], holdout_beta)
    wf_total, wf_blocks = walkforward(y, exposure, predictor)
    result = {
        "implementation": "INDEPENDENT_IRLS_2X2_NEWTON",
        "data_sha256": EXPECTED_DATA_SHA, "range": "1~1237", "assertions": assertions,
        "train_beta": train_beta, "holdout_beta": holdout_beta,
        "fresh_permutation_seed": SEED, "permutations": N_PERM,
        "fresh_permutation_exceed_count": exceed, "fresh_permutation_p": permutation_p,
        "wf_delta_ll_total": wf_total, "wf_blocks": wf_blocks,
    }
    target = HERE / "independent_raw_result.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "downloads" / "official-1-1237"
CANONICAL = ROOT / "v27_storage" / "experiments" / "exp003" / "data" / "exp003_draws_1_1237.csv"
STATE_DIR = ROOT / "00_P45_STATE" / "experiment_lab" / "EXP-PRIZE-002_SECOND_PRIZE"
OUT = ROOT / "v27_storage" / "experiments" / "prize_share_exp002_v1"
PROTOCOL = STATE_DIR / "EXP_PRIZE_002_V1_LOCKED_PROTOCOL.md"
PROTOCOL_SHA = "e27100d726264310d2402cb691f8ca8a53d0d2e5f9ece861cd033156573f5302"
BLOCKS = ((801, 900), (901, 1000), (1001, 1100), (1101, 1237))
PERMUTATIONS = 100_000
BLOCK_SEED = 2026082103
GLOBAL_SEED = 2026082104


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_raw() -> tuple[dict[int, dict], dict[str, str]]:
    rows: dict[int, dict] = {}
    file_hashes: dict[str, str] = {}
    for path in sorted((SOURCE / "raw").glob("api-*.json")):
        rel = path.relative_to(ROOT).as_posix()
        file_hashes[rel] = sha(path)
        doc = json.loads(path.read_text(encoding="utf-8"))
        for item in doc["data"]["list"]:
            r = int(item["ltEpsd"])
            if r > 1237:
                continue
            selected = {
                "round": r,
                "date": str(item["ltRflYmd"]),
                "main": [int(item[f"tm{i}WnNo"]) for i in range(1, 7)],
                "bonus": int(item["bnsWnNo"]),
                "second_prize_games": int(item["rnk2WnNope"]),
                "whole_sales_amount": int(item["wholEpsdSumNtslAmt"]),
                "source_file": rel,
                "source_file_sha256": file_hashes[rel],
            }
            if r in rows and rows[r] != selected:
                raise RuntimeError(f"DATA_BLOCKED:DUPLICATE_CONFLICT:{r}")
            rows[r] = selected
    expected = set(range(1, 1238))
    if set(rows) != expected:
        raise RuntimeError(f"DATA_BLOCKED:RANGE:missing={sorted(expected-set(rows))}:extra={sorted(set(rows)-expected)}")
    return rows, file_hashes


def load_canonical() -> dict[int, tuple[int, ...]]:
    with CANONICAL.open(encoding="utf-8-sig", newline="") as stream:
        return {
            int(row["round"]): tuple(sorted(int(row[f"n{i}"]) for i in range(1, 7)))
            for row in csv.DictReader(stream)
        }


def derive(rows: dict[int, dict]) -> list[dict]:
    canonical = load_canonical()
    if set(canonical) != set(range(1, 1238)):
        raise RuntimeError("DATA_BLOCKED:CANONICAL_RANGE")
    derived: list[dict] = []
    for r in range(1, 1238):
        item = rows[r]
        main = tuple(sorted(item["main"]))
        bonus = item["bonus"]
        if len(main) != 6 or len(set(main)) != 6 or not all(1 <= n <= 45 for n in main):
            raise RuntimeError(f"DATA_BLOCKED:MAIN:{r}")
        if not 1 <= bonus <= 45 or bonus in main:
            raise RuntimeError(f"DATA_BLOCKED:BONUS:{r}")
        if main != canonical[r]:
            raise RuntimeError(f"DATA_BLOCKED:CANONICAL_MAIN:{r}")
        k2 = item["second_prize_games"]
        sales = item["whole_sales_amount"]
        price = 2000 if r <= 87 else 1000
        if k2 < 0 or sales <= 0 or sales % price:
            raise RuntimeError(f"DATA_BLOCKED:OUTCOME_OR_SALES:{r}")
        tickets = [tuple(sorted((*main[:i], *main[i + 1 :], bonus))) for i in range(6)]
        if len(set(tickets)) != 6 or any(len(t) != 6 or len(set(t)) != 6 for t in tickets):
            raise RuntimeError(f"DATA_BLOCKED:SECOND_PRIZE_TICKETS:{r}")
        counts = [sum(n <= 31 for n in ticket) for ticket in tickets]
        direct = sum(counts) / 6.0
        m = sum(n <= 31 for n in main)
        b = int(bonus <= 31)
        closed = (5 * m + 6 * b) / 6.0
        if abs(direct - closed) > 1e-15:
            raise RuntimeError(f"DATA_BLOCKED:X2_ASSERTION:{r}")
        sold = sales // price
        derived.append({
            "round": r,
            "date": item["date"],
            **{f"main_{i}": value for i, value in enumerate(main, 1)},
            "bonus": bonus,
            "second_prize_games": k2,
            "sales_amount_krw": sales,
            "price_per_game_krw": price,
            "sold_lines": sold,
            "main_birthday_count": m,
            "bonus_birthday_indicator": b,
            "second_prize_tickets_json": canonical_json(tickets),
            "second_prize_birthday_counts_json": canonical_json(counts),
            "x2": format(closed, ".17g"),
            "z2": format(closed - 6 * 31 / 45, ".17g"),
            "share2_index": format(k2 * math.comb(45, 6) / (6 * sold), ".17g"),
            "source_file": item["source_file"],
            "source_file_sha256": item["source_file_sha256"],
        })
    return derived


def write_snapshot(rows: list[dict]) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "exp_prize_002_v1_draws_1_1237.csv"
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return target


def fit_beta(k: np.ndarray, exposure: np.ndarray, x: np.ndarray) -> tuple[float, float]:
    total_k = float(k.sum())
    target = float(np.dot(k, x))
    lo, hi = -20.0, 20.0
    for _ in range(100):
        beta = (lo + hi) / 2
        z = beta * x
        z -= z.max()
        weights = exposure * np.exp(z)
        score = target - total_k * float(np.dot(weights, x) / weights.sum())
        if score > 0:
            lo = beta
        else:
            hi = beta
    beta = (lo + hi) / 2
    alpha = math.log(total_k) - math.log(float(np.sum(exposure * np.exp(beta * x))))
    return alpha, beta


def batch_betas(k: np.ndarray, exposure: np.ndarray, xp: np.ndarray) -> np.ndarray:
    total_k = float(k.sum())
    targets = xp @ k
    beta = np.zeros(xp.shape[0])
    for _ in range(24):
        z = beta[:, None] * xp
        z -= z.max(axis=1, keepdims=True)
        weights = exposure[None, :] * np.exp(z)
        sw = weights.sum(axis=1)
        mean = (weights * xp).sum(axis=1) / sw
        var = (weights * (xp - mean[:, None]) ** 2).sum(axis=1) / sw
        score = targets - total_k * mean
        step = np.divide(score, total_k * var, out=np.zeros_like(score), where=var > 0)
        beta = np.clip(beta + step, -20, 20)
    return beta


def permutation_p(k: np.ndarray, exposure: np.ndarray, x: np.ndarray, observed: float, *, block: bool, seed: int) -> tuple[float, int]:
    rng = np.random.default_rng(seed)
    exceed = 0
    batch_size = 400
    relative_blocks = tuple((start - 801, end - 800) for start, end in BLOCKS)
    for start in range(0, PERMUTATIONS, batch_size):
        size = min(batch_size, PERMUTATIONS - start)
        if block:
            xp = np.empty((size, x.size), dtype=float)
            for left, right in relative_blocks:
                segment = x[left:right]
                xp[:, left:right] = rng.permuted(np.broadcast_to(segment, (size, segment.size)), axis=1)
        else:
            xp = rng.permuted(np.broadcast_to(x, (size, x.size)), axis=1)
        betas = batch_betas(k, exposure, xp)
        exceed += int(np.count_nonzero(betas >= observed - 1e-12))
    return (1 + exceed) / (PERMUTATIONS + 1), exceed


def poisson_ll(k: np.ndarray, mu: np.ndarray) -> float:
    return float(np.sum(k * np.log(mu) - mu - np.fromiter((math.lgamma(float(v) + 1) for v in k), float)))


def main() -> int:
    if sha(PROTOCOL) != PROTOCOL_SHA:
        raise RuntimeError("PROTOCOL_HASH_CONFLICT")
    raw, source_hashes = load_raw()
    rows = derive(raw)
    snapshot = write_snapshot(rows)
    dictionary = {
        "round": "ltEpsd", "main_1..main_6": "sorted tm1WnNo..tm6WnNo", "bonus": "bnsWnNo",
        "second_prize_games": "rnk2WnNope; official second-rank 당첨게임 수",
        "sales_amount_krw": "wholEpsdSumNtslAmt; official 총판매금액",
        "price_per_game_krw": "2000 rounds 1~87; 1000 rounds 88~1237",
        "sold_lines": "sales_amount_krw / price_per_game_krw",
        "second_prize_tickets_json": "six unique exact 5-main-plus-bonus ticket combinations",
        "x2": "mean count(number<=31) across those six tickets; equals (5*m+6*b)/6",
        "z2": "x2 - 6*31/45", "share2_index": "descriptive K2*C(45,6)/(6*N)",
    }
    (OUT / "data_dictionary.json").write_text(json.dumps(dictionary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {
        "status": "DATA_VALIDATION_PASS", "protocol_sha256": PROTOCOL_SHA,
        "source_schema_preflight": "SOURCE_SCHEMA_PREFLIGHT_PASS", "rows": len(rows), "range": "1~1237",
        "missing": 0, "duplicates": 0, "canonical_mismatch": 0, "k2_missing": 0,
        "x2_formula_mismatch": 0, "round_1238_plus_used": False, "future_leakage": 0,
        "snapshot": snapshot.relative_to(ROOT).as_posix(), "snapshot_sha256": sha(snapshot),
        "source_files": len(source_hashes), "source_file_hashes": source_hashes,
    }
    (OUT / "data_validation.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    k = np.array([int(row["second_prize_games"]) for row in rows], dtype=float)
    exposure = np.array([6 * int(row["sold_lines"]) for row in rows], dtype=float)
    x = np.array([float(row["z2"]) for row in rows], dtype=float)
    _, train_beta = fit_beta(k[:800], exposure[:800], x[:800])
    result: dict[str, object] = {
        "status": "FAILED_EARLY_TRAIN_DIRECTION" if train_beta <= 0 else None,
        "protocol_sha256": PROTOCOL_SHA, "data_range": "1~1237", "data_sha256": sha(snapshot),
        "round_1238_plus_used": False, "future_leakage": 0, "train_beta2": train_beta,
        "train_gate": "PASS" if train_beta > 0 else "FAIL", "holdout_beta2": None,
        "effect_per_plus1_x2": None, "primary_block_permutation_p": None,
        "secondary_global_permutation_p": None, "block_exceed": None, "global_exceed": None,
        "permutations_each": 0, "wf_delta_ll_total": None, "wf_blocks": [], "wf_gate": "NOT_RUN",
        "cross_outcome_corroboration": False, "independent_empirical_replication": False,
        "promotion_candidate": False, "draw_engine_changed": False,
    }
    if train_beta > 0:
        _, hold_beta = fit_beta(k[800:], exposure[800:], x[800:])
        p_block, block_exceed = permutation_p(k[800:], exposure[800:], x[800:], hold_beta, block=True, seed=BLOCK_SEED)
        p_global, global_exceed = permutation_p(k[800:], exposure[800:], x[800:], hold_beta, block=False, seed=GLOBAL_SEED)
        result.update(holdout_beta2=hold_beta, effect_per_plus1_x2=math.exp(hold_beta),
                      primary_block_permutation_p=p_block, secondary_global_permutation_p=p_global,
                      block_exceed=block_exceed, global_exceed=global_exceed, permutations_each=PERMUTATIONS)
        if hold_beta <= 0 or p_block > 0.05:
            result["status"] = "FAILED"
        else:
            total = 0.0
            wf = []
            for first, last in BLOCKS:
                train_end = first - 1
                alpha_alt, beta_alt = fit_beta(k[:train_end], exposure[:train_end], x[:train_end])
                alpha_null = math.log(float(k[:train_end].sum()) / float(exposure[:train_end].sum()))
                sl = slice(first - 1, last)
                alt_mu = exposure[sl] * np.exp(alpha_alt + beta_alt * x[sl])
                null_mu = exposure[sl] * math.exp(alpha_null)
                delta = poisson_ll(k[sl], alt_mu) - poisson_ll(k[sl], null_mu)
                wf.append({"range": f"{first}~{last}", "delta_ll": delta, "train_end_round": train_end})
                total += delta
            result.update(wf_delta_ll_total=total, wf_blocks=wf, wf_gate="PASS" if total > 0 else "FAIL")
            if total > 0:
                result.update(status="SUPPORTED_CROSS_OUTCOME", cross_outcome_corroboration=True)
            else:
                result["status"] = "INCONCLUSIVE"
    result["decision_hash"] = hashlib.sha256(canonical_json(result).encode("utf-8")).hexdigest()
    result_path = OUT / "exp_prize_002_v1_result.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "permutation_summary.json").write_text(json.dumps({
        "primary": {"type": "within-fixed-time-block", "seed": BLOCK_SEED, "n": PERMUTATIONS,
                    "exceed": result["block_exceed"], "p": result["primary_block_permutation_p"]},
        "secondary": {"type": "global-diagnostic-only", "seed": GLOBAL_SEED, "n": PERMUTATIONS,
                      "exceed": result["global_exceed"], "p": result["secondary_global_permutation_p"]},
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "wf_log.json").write_text(json.dumps({"blocks": result["wf_blocks"], "total": result["wf_delta_ll_total"], "gate": result["wf_gate"]}, indent=2) + "\n", encoding="utf-8")
    print(canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

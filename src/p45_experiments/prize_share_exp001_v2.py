from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "downloads" / "official-1-1237"
CANONICAL = ROOT / "v27_storage" / "experiments" / "exp003" / "data" / "exp003_draws_1_1237.csv"
OUT = ROOT / "v27_storage" / "experiments" / "prize_share_exp001_v2"
PROTOCOL_SHA = "479c83f5905d1bcd928e5b388420a41259c413836711202fd30704e7b4b9d5b7"
AUDIT_ROUNDS = (1, 10, 87, 88, 1201, 1237)
SEED = 2026082101
PERMUTATIONS = 100_000


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_official() -> tuple[dict[int, dict], list[dict]]:
    rows: dict[int, dict] = {}
    raw_evidence: list[dict] = []
    for path in sorted((SOURCE / "raw").glob("api-*.json")):
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
                "first_prize_games": int(item["rnk1WnNope"]),
                "whole_sales_amount": int(item["wholEpsdSumNtslAmt"]),
                "relevant_sales_amount": int(item["rlvtEpsdSumNtslAmt"]),
                "source_file": path.relative_to(ROOT).as_posix(),
                "source_file_sha256": sha(path),
            }
            if r in rows and rows[r] != selected:
                raise RuntimeError(f"DATA_BLOCKED_MISMATCH:DUPLICATE_CONFLICT:{r}")
            rows[r] = selected
    if set(rows) != set(range(1, 1238)):
        missing = sorted(set(range(1, 1238)) - set(rows))
        extra = sorted(set(rows) - set(range(1, 1238)))
        raise RuntimeError(f"DATA_BLOCKED_MISSING_REQUIRED_FIELD:missing={missing}:extra={extra}")
    for r in AUDIT_ROUNDS:
        raw_evidence.append(dict(rows[r]))
    return rows, raw_evidence


def load_canonical() -> dict[int, tuple[int, ...]]:
    with CANONICAL.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return {int(row["round"]): tuple(sorted(int(row[f"n{i}"]) for i in range(1, 7))) for row in reader}


def validate_and_derive(rows: dict[int, dict]) -> list[dict]:
    canonical = load_canonical()
    if set(canonical) != set(range(1, 1238)):
        raise RuntimeError("DATA_BLOCKED_MISMATCH:CANONICAL_RANGE")
    out = []
    for r in range(1, 1238):
        row = rows[r]
        main = tuple(sorted(row["main"]))
        if len(main) != 6 or len(set(main)) != 6 or min(main) < 1 or max(main) > 45:
            raise RuntimeError(f"DATA_BLOCKED_MISMATCH:MAIN:{r}")
        if main != canonical[r]:
            raise RuntimeError(f"DATA_BLOCKED_MISMATCH:CANONICAL_MAIN:{r}")
        k = row["first_prize_games"]
        sales = row["whole_sales_amount"]
        price = 2000 if r <= 87 else 1000
        if k < 0 or sales <= 0 or sales % price:
            raise RuntimeError(f"PROTOCOL_BLOCKED_SOURCE_SEMANTICS_V2:CONVERSION:{r}:{sales}:{price}")
        n = sales // price
        out.append({
            "round": r, "date": row["date"],
            **{f"main_{i}": value for i, value in enumerate(main, 1)},
            "first_prize_games": k,
            "sales_amount_krw": sales,
            "price_per_game_krw": price,
            "sold_lines": n,
            "birthday_count": sum(value <= 31 for value in main),
            "relevant_sales_amount_audit_only": row["relevant_sales_amount"],
        })
    return out


def preflight() -> dict:
    rows, audit = load_official()
    derived = validate_and_derive(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    snapshot = OUT / "exp_prize_001_v2_draws_1_1237.csv"
    fields = list(derived[0])
    with snapshot.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(derived)
    audit_rows = []
    for item in audit:
        d = derived[item["round"] - 1]
        audit_rows.append({
            "round": item["round"], "main": sorted(item["main"]),
            "first_prize_games": item["first_prize_games"],
            "whole_sales_amount": item["whole_sales_amount"],
            "relevant_sales_amount": item["relevant_sales_amount"],
            "price_per_game": d["price_per_game_krw"], "sold_lines": d["sold_lines"],
            "integer_conversion": True, "source_file": item["source_file"],
            "source_file_sha256": item["source_file_sha256"],
        })
    payload = {
        "status": "SEMANTIC_AUDIT_PASS", "protocol_sha256": PROTOCOL_SHA,
        "source_page": "https://www.dhlottery.co.kr/lt645/result",
        "source_api": "https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do",
        "total_sales_field": "wholEpsdSumNtslAmt",
        "forbidden_denominator_field": "rlvtEpsdSumNtslAmt",
        "price_rule": {"1~87": 2000, "88~1237": 1000},
        "rounds": "1~1237", "rows": 1237, "round_1238_plus_used": False,
        "missing": 0, "duplicates": 0, "canonical_main_mismatch": 0,
        "audit_rounds": audit_rows, "snapshot": snapshot.relative_to(ROOT).as_posix(),
        "snapshot_sha256": sha(snapshot), "retrieved_at": json.loads((SOURCE / "metadata.json").read_text(encoding="utf-8"))["collected_at"],
    }
    (OUT / "semantic_audit.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "data_dictionary.json").write_text(json.dumps({
        "round": "official draw round", "main_1..main_6": "sorted main winning numbers; bonus excluded",
        "first_prize_games": "rnk1WnNope", "sales_amount_krw": "wholEpsdSumNtslAmt",
        "price_per_game_krw": "2000 for rounds 1~87; 1000 for rounds 88~1237",
        "sold_lines": "sales_amount_krw / price_per_game_krw",
        "birthday_count": "count(main number <=31)",
        "relevant_sales_amount_audit_only": "rlvtEpsdSumNtslAmt; forbidden from inference"
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(canonical_json(payload))
    return payload


def fit_beta(k: np.ndarray, n: np.ndarray, x: np.ndarray) -> tuple[float, float]:
    total_k = float(k.sum())
    target = float(np.dot(k, x))
    lo, hi = -20.0, 20.0
    for _ in range(100):
        beta = (lo + hi) / 2
        z = beta * x
        z -= z.max()
        w = n * np.exp(z)
        score = target - total_k * float(np.dot(w, x) / w.sum())
        if score > 0: lo = beta
        else: hi = beta
    beta = (lo + hi) / 2
    alpha = math.log(total_k) - math.log(float(np.sum(n * np.exp(beta * x))))
    return alpha, beta


def permutation_p(k: np.ndarray, n: np.ndarray, x: np.ndarray, observed: float) -> float:
    rng = np.random.default_rng(SEED)
    count = 0
    batch_size = 500
    total_k = float(k.sum())
    for start in range(0, PERMUTATIONS, batch_size):
        size = min(batch_size, PERMUTATIONS - start)
        xp = rng.permuted(np.broadcast_to(x, (size, x.size)), axis=1)
        beta = np.zeros(size)
        targets = xp @ k
        for _ in range(20):
            z = beta[:, None] * xp
            z -= z.max(axis=1, keepdims=True)
            w = n[None, :] * np.exp(z)
            sw = w.sum(axis=1)
            mean = (w * xp).sum(axis=1) / sw
            var = (w * (xp - mean[:, None]) ** 2).sum(axis=1) / sw
            score = targets - total_k * mean
            step = np.divide(score, total_k * var, out=np.zeros_like(score), where=var > 0)
            beta = np.clip(beta + step, -20, 20)
        count += int(np.count_nonzero(beta >= observed - 1e-12))
    return (1 + count) / (PERMUTATIONS + 1)


def poisson_ll(k: np.ndarray, mu: np.ndarray) -> float:
    return float(np.sum(k * np.log(mu) - mu - np.fromiter((math.lgamma(float(v) + 1) for v in k), float)))


def analyze() -> dict:
    audit = json.loads((OUT / "semantic_audit.json").read_text(encoding="utf-8"))
    if audit["status"] != "SEMANTIC_AUDIT_PASS" or audit["round_1238_plus_used"]:
        raise RuntimeError("SEMANTIC_PREFLIGHT_NOT_PASS")
    snapshot = ROOT / audit["snapshot"]
    if sha(snapshot) != audit["snapshot_sha256"]:
        raise RuntimeError("SNAPSHOT_HASH_MISMATCH")
    with snapshot.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    k = np.array([int(r["first_prize_games"]) for r in rows], dtype=float)
    n = np.array([int(r["sold_lines"]) for r in rows], dtype=float)
    x = np.array([int(r["birthday_count"]) - 6 * 31 / 45 for r in rows], dtype=float)
    _, beta_train = fit_beta(k[:800], n[:800], x[:800])
    result = {
        "status": None, "protocol_sha256": PROTOCOL_SHA, "data_range": "1~1237",
        "data_sha256": audit["snapshot_sha256"], "round_1238_plus_used": False,
        "train_beta": beta_train, "train_gate": "PASS" if beta_train > 0 else "FAIL",
        "holdout_beta": None, "holdout_effect_per_birthday_number": None,
        "holdout_permutation_p": None, "permutations": 0,
        "wf_delta_ll_total": None, "wf_blocks": [], "promotion_candidate": False,
        "official_engine_changed": False,
    }
    if beta_train <= 0:
        result.update(status="FAILED_EARLY_TRAIN_DIRECTION", final_judgment="FAILED_EARLY_TRAIN_DIRECTION")
    else:
        _, beta_hold = fit_beta(k[800:], n[800:], x[800:])
        p = permutation_p(k[800:], n[800:], x[800:], beta_hold)
        result.update(holdout_beta=beta_hold, holdout_effect_per_birthday_number=math.exp(beta_hold), holdout_permutation_p=p, permutations=PERMUTATIONS)
        if beta_hold <= 0 or p > .05:
            result.update(status="FAILED", final_judgment="FAILED")
        else:
            total = 0.0
            for start, end in ((801,900),(901,1000),(1001,1100),(1101,1237)):
                train_end = start - 1
                alpha_alt, beta_alt = fit_beta(k[:train_end], n[:train_end], x[:train_end])
                alpha_null = math.log(float(k[:train_end].sum()) / float(n[:train_end].sum()))
                sl = slice(start-1, end)
                mu_alt = n[sl] * np.exp(alpha_alt + beta_alt*x[sl])
                mu_null = n[sl] * math.exp(alpha_null)
                delta = poisson_ll(k[sl], mu_alt) - poisson_ll(k[sl], mu_null)
                result["wf_blocks"].append({"range": f"{start}~{end}", "delta_ll": delta})
                total += delta
            result["wf_delta_ll_total"] = total
            if total > 0: result.update(status="SUPPORTED_WITHIN_EXPERIMENT", final_judgment="SUPPORTED_WITHIN_EXPERIMENT")
            else: result.update(status="INCONCLUSIVE", final_judgment="INCONCLUSIVE")
    result["decision_hash"] = hashlib.sha256(canonical_json(result).encode()).hexdigest()
    target = OUT / "exp_prize_001_v2_result.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    first_hash = sha(target)
    repeat = json.loads(target.read_text(encoding="utf-8"))
    reproducible = repeat == result and sha(target) == first_hash
    log = {"reproducible": reproducible, "result_sha256": first_hash, "protocol_sha256": PROTOCOL_SHA, "data_sha256": audit["snapshot_sha256"], "future_leakage": 0}
    (OUT / "reproducibility_log.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    print(canonical_json(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("preflight", "analyze")); args = parser.parse_args()
    if args.command == "preflight": preflight()
    else: analyze()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

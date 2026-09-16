from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter
from pathlib import Path

EXP_ID = "EXP-DRAW-20260827-019-V1"
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "P45_EXP_019_SALES_ADJUSTED_BIRTHDAY_CROWD_EFFECT_V1_PROTOCOL_001.md"
LOCK = HERE / "P45_EXP_019_PROTOCOL_LOCK_001.md"
DATASET = HERE / "P45_EXP_019_OFFICIAL_CROWD_METADATA_001.csv"
RAW = HERE / "P45_EXP_019_OFFICIAL_RAW_BATCHES_001.jsonl"
MANIFEST = HERE / "P45_EXP_019_OFFICIAL_SOURCE_MANIFEST_001.json"
STATE = HERE / "P45_EXP_019_EXPERIMENT_STATE_001.json"
CANONICAL = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
CALC = HERE / "P45_EXP_019_SALES_ADJUSTED_BIRTHDAY_CROWD_EFFECT_V1_CALCULATION_001.json"
RESULT = HERE / "P45_EXP_019_SALES_ADJUSTED_BIRTHDAY_CROWD_EFFECT_V1_RESULT_001.md"

EXPECTED = {
    PROTOCOL: "220d59aa8c50e11c74f6146061784b8f5e0413c5a7013758a47891404e2f4d5c",
    LOCK: "fb28b4daed366e4a9448a33c68155bb742a63fecda41a2f6ce37eec30ef32b6a",
    DATASET: "03cec8aea026d987a6ea8550154e4110ac8b100df9c868f18ce19258cb65a9a4",
    RAW: "e825073224aa7a869d0902be237ea5dc60652acae10632d6314517465a691742",
    MANIFEST: "b19c14c9f843a9db5fecf377ca391663f206322a2f99ef0ec77e7103e4bc383a",
}
PERMUTATIONS = 100_000
SEED = 20260827
UNIVERSE = 8_145_060


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_integrity() -> dict:
    actual = {str(path): sha(path) for path in EXPECTED}
    if any(actual[str(path)] != expected for path, expected in EXPECTED.items()):
        raise RuntimeError("EXP_019_EXECUTION_BLOCKED_INTEGRITY_MISMATCH")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("experiment_id") != EXP_ID or state.get("status") != "READY_FOR_TEST" or state.get("outcome_peek") != 0 or state.get("result_calculation") is not False:
        raise RuntimeError("EXP_019_EXECUTION_BLOCKED_INTEGRITY_MISMATCH")
    return actual


def load_and_verify_structure() -> list[dict]:
    with DATASET.open("r", encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    draws = [int(row["draw"]) for row in raw_rows]
    if len(raw_rows) != 1151 or set(draws) != set(range(88, 1239)) or len(draws) != len(set(draws)):
        raise RuntimeError("EXP_019_EXECUTION_BLOCKED_STRUCTURAL_MISMATCH")

    canonical = {}
    with CANONICAL.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            draw = int(row["round"])
            if 88 <= draw <= 1238:
                canonical[draw] = tuple(sorted(int(row[f"n{i}"]) for i in range(1, 7)))

    rows = []
    for source in sorted(raw_rows, key=lambda x: int(x["draw"])):
        draw = int(source["draw"])
        main = tuple(int(source[f"main{i}"]) for i in range(1, 7))
        sales = int(source["total_sales_krw"])
        games = int(source["games_sold"])
        b = int(source["birthday_range_count"])
        if tuple(sorted(main)) != canonical.get(draw) or sales % 1000 or games != sales // 1000 or int(source["price_per_game"]) != 1000:
            raise RuntimeError("EXP_019_EXECUTION_BLOCKED_STRUCTURAL_MISMATCH")
        if b != sum(1 <= number <= 31 for number in main):
            raise RuntimeError("EXP_019_EXECUTION_BLOCKED_STRUCTURAL_MISMATCH")
        expected_lambda = games / UNIVERSE
        if not math.isclose(float(source["lambda_uniform"]), expected_lambda, rel_tol=0.0, abs_tol=5e-14):
            raise RuntimeError("EXP_019_EXECUTION_BLOCKED_STRUCTURAL_MISMATCH")
        rows.append({"draw": draw, "w": int(source["winner_count_1st"]), "games": games, "lam": expected_lambda, "b": b})

    if Counter(row["b"] for row in rows) != Counter({0: 1, 1: 12, 2: 58, 3: 240, 4: 405, 5: 335, 6: 100}):
        raise RuntimeError("EXP_019_EXECUTION_BLOCKED_STRUCTURAL_MISMATCH")
    if sum(row["draw"] <= 867 for row in rows) != 780 or sum(row["draw"] >= 868 for row in rows) != 371:
        raise RuntimeError("EXP_019_EXECUTION_BLOCKED_STRUCTURAL_MISMATCH")
    return rows


def estimate_beta(rows: list[dict]) -> float:
    total_w = math.fsum(row["w"] for row in rows)
    if total_w <= 0:
        raise RuntimeError("EXP_019_EXECUTION_BLOCKED_EFFECT_ESTIMATOR")

    def score(beta: float) -> float:
        a = math.fsum(row["lam"] * math.exp(beta * row["b"]) for row in rows)
        scale = total_w / a
        value = math.fsum(row["b"] * (row["w"] - row["lam"] * scale * math.exp(beta * row["b"])) for row in rows)
        if not math.isfinite(a) or not math.isfinite(scale) or not math.isfinite(value):
            raise RuntimeError("EXP_019_EXECUTION_BLOCKED_EFFECT_ESTIMATOR")
        return value

    low, high = -20.0, 20.0
    if score(low) < 0 or score(high) > 0:
        raise RuntimeError("EXP_019_EXECUTION_BLOCKED_EFFECT_ESTIMATOR")
    for _ in range(1000):
        if high - low <= 1e-12:
            return (low + high) / 2.0
        mid = (low + high) / 2.0
        if score(mid) > 0:
            low = mid
        else:
            high = mid
    raise RuntimeError("EXP_019_EXECUTION_BLOCKED_EFFECT_ESTIMATOR")


def evaluate(rows: list[dict]) -> dict:
    beta = estimate_beta(rows)
    total_w = sum(row["w"] for row in rows)
    total_games = sum(row["games"] for row in rows)
    total_lam = math.fsum(row["lam"] for row in rows)
    c = total_w / total_lam
    residuals = [row["w"] - c * row["lam"] for row in rows]
    ordered_b = [row["b"] for row in rows]
    u_obs = math.fsum(b * residual for b, residual in zip(ordered_b, residuals))
    rng = random.Random(SEED)
    exceedances = 0
    for _ in range(PERMUTATIONS):
        shuffled = ordered_b.copy()
        rng.shuffle(shuffled)
        u_perm = math.fsum(b * residual for b, residual in zip(shuffled, residuals))
        if u_perm >= u_obs:
            exceedances += 1
    p_perm = (1 + exceedances) / (PERMUTATIONS + 1)
    return {
        "targets": len(rows), "winner_games_total": total_w, "games_sold_total": total_games,
        "lambda_total": total_lam, "b_distribution": {str(k): v for k, v in sorted(Counter(ordered_b).items())},
        "beta_hat": beta, "exp_beta_hat": math.exp(beta), "U_obs": u_obs,
        "permutations": PERMUTATIONS, "seed": SEED, "exceedance_count": exceedances, "p_perm": p_perm,
        "success": beta > 0 and p_perm <= 0.05,
    }


def formal_run(rows: list[dict]) -> dict:
    development = evaluate([row for row in rows if row["draw"] <= 867])
    development["verdict"] = "DEVELOPMENT_SCREEN_POSITIVE" if development["success"] else "FAILED_NOT_SUPPORTED"
    if not development["success"]:
        return {"development": development, "holdout_executed": False, "holdout": None, "final_verdict": "FAILED_NOT_SUPPORTED"}
    holdout = evaluate([row for row in rows if row["draw"] >= 868])
    holdout["verdict"] = "HOLDOUT_POSITIVE" if holdout["success"] else "HOLDOUT_FAILED"
    final = "HISTORICAL_SCREEN_AND_WALKFORWARD_POSITIVE" if holdout["success"] else "FAILED_NOT_REPRODUCED"
    return {"development": development, "holdout_executed": True, "holdout": holdout, "final_verdict": final}


def main() -> None:
    integrity = verify_integrity()
    rows = load_and_verify_structure()
    first = formal_run(rows)
    second = formal_run(rows)
    if first != second:
        raise RuntimeError("EXP_019_EXECUTION_BLOCKED_REPRODUCIBILITY_FAILURE")

    proof_payload = json.dumps(first, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    proof = hashlib.sha256(proof_payload).hexdigest()
    protection = {
        "protocol_changed": "NO", "lock_changed": "NO", "dataset_changed": "NO",
        "official_changes": 0, "DB_changes": 0, "Fixed_changes": 0, "Linked_changes": 0,
        "KTS_changes": 0, "sealed_1239_changes": 0, "prospective_changes": 0,
        "existing_experiment_verdict_changes": 0, "FUTURE_LEAKAGE": 0,
    }
    calculation = {
        "experiment_id": EXP_ID,
        "protocol_sha256": EXPECTED[PROTOCOL], "lock_sha256": EXPECTED[LOCK],
        "dataset_sha256": EXPECTED[DATASET], "raw_sha256": EXPECTED[RAW], "manifest_sha256": EXPECTED[MANIFEST],
        "historical_range": [88, 1238], "development_range": [88, 867], "holdout_range": [868, 1238],
        "predictor_definition": "B_t=count(MAIN6 intersection {1..31})",
        "model_definition": "log(E[W_t])=log(LAMBDA_t)+alpha+beta*B_t; LAMBDA_t=games_sold/8145060",
        **first,
        "reproducibility": {
            "full_calculation_runs": 2, "beta": "PASS", "U_statistic": "PASS", "permutation_exceedance": "PASS",
            "p_value": "PASS", "development_verdict": "PASS",
            "holdout_verdict": "PASS" if first["holdout_executed"] else "NOT_RUN", "final_verdict": "PASS",
            "deterministic_execution_proof_sha256": proof,
        },
        "protection_checks": protection,
    }
    CALC.write_text(json.dumps(calculation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    d = first["development"]
    h = first["holdout"]
    lines = [
        "# EXP-019 locked execution result", "", f"FINAL_VERDICT = {first['final_verdict']}", "",
        "## Development", "", f"- targets: `{d['targets']}`", f"- winner games total: `{d['winner_games_total']}`",
        f"- games sold total: `{d['games_sold_total']}`", f"- lambda total: `{d['lambda_total']!r}`",
        f"- B distribution: `{d['b_distribution']}`", f"- beta_hat: `{d['beta_hat']!r}`", f"- exp(beta_hat): `{d['exp_beta_hat']!r}`",
        f"- U_obs: `{d['U_obs']!r}`", f"- exceedance count: `{d['exceedance_count']}`", f"- p_perm: `{d['p_perm']!r}`",
        f"- verdict: `{d['verdict']}`", "", "## Holdout", "",
    ]
    if h is None:
        lines += ["- executed: `NO`", "- reason: `DEVELOPMENT_FAILED_PROTOCOL_GATE`", "- formal relationship metrics: `NOT CALCULATED`"]
    else:
        lines += [f"- executed: `YES`", f"- targets: `{h['targets']}`", f"- winner games total: `{h['winner_games_total']}`",
                  f"- games sold total: `{h['games_sold_total']}`", f"- lambda total: `{h['lambda_total']!r}`",
                  f"- B distribution: `{h['b_distribution']}`", f"- beta_hat: `{h['beta_hat']!r}`", f"- exp(beta_hat): `{h['exp_beta_hat']!r}`",
                  f"- U_obs: `{h['U_obs']!r}`", f"- exceedance count: `{h['exceedance_count']}`", f"- p_perm: `{h['p_perm']!r}`",
                  f"- verdict: `{h['verdict']}`"]
    lines += ["", "## Reproducibility and protection", "", f"- deterministic proof SHA-256: `{proof}`",
              "- full calculation repeated identically: `PASS`", "- draw-prediction claim: `NO`", "- recommendation signal created: `NO`",
              "- Official/DB/Fixed/Linked/KTS/sealed/prospective changes: `0`", "- FUTURE_LEAKAGE: `0`"]
    RESULT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(calculation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from unittest.mock import patch

import p45_v27.number_engine as number_engine
from p45_v27.number_engine import decide_number
from p45_v27.stage55_diagnostics import load_draw_csv
from p45_v27.stage6_diagnostics import diagnose_stage6
from p45_v27.units import DEFINITIONS

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "v27_storage/audits/opposite_period_filter_validation_001"
STAGING = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
PROTOCOL = OUT / "P45_OPPOSITE_PERIOD_STABILITY_FILTER_VALIDATION_PROTOCOL_LOCKED_001.md"
EXPECTED_STAGING_SHA = "1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"
EXPECTED_PROTOCOL_SHA = "03bb3ba7c472955b0f7825dc9ed348a865f7b3d42dfc19611bdd5a705a09ff4b"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eligible(row: dict) -> bool:
    return row["number_state"] in ("NUMBER_PASS", "NUMBER_WEAKEN") or row["valid_test_status"]


def one_target(target: int) -> dict:
    stage6 = diagnose_stage6(STAGING, target)
    if tuple(stage6["source_rounds"]) != (1, target - 1):
        raise RuntimeError(f"FUTURE_OR_SOURCE_BOUNDARY:{target}:{stage6['source_rounds']}")
    rows = stage6["rows"]
    official = [n for n, row in rows.items() if eligible(row)]
    shadow_rows = {}
    with patch.object(number_engine, "_opposite_directions", return_value=False):
        for n in range(1, 46):
            row = rows[n]
            metrics = {unit: stage6["unit_metrics"][unit][n] for unit in DEFINITIONS}
            roles = {key: row[key] for key in ("return_roles", "primary_return_role", "role_signature")}
            roles["has_return_role"] = any(item["role_type"].startswith("RETURN_") for item in roles["return_roles"])
            shadow_rows[n] = decide_number(n, metrics, stage6["relations"][n], stage6["pareto"][str(n)], roles)
    fixed = [n for n, row in shadow_rows.items() if eligible(row)]
    blocked = []
    for n in range(1, 46):
        row, variant = rows[n], shadow_rows[n]
        primary = row.get("primary_number_context")
        if not primary or row["number_state"] != "NUMBER_HOLD" or not eligible(variant):
            continue
        ctx = primary["context"]
        if ctx["overall"]["integrated"]["evidence_label"] != "POSITIVE_TENTATIVE" or ctx["recent100"]["integrated"]["evidence_label"] != "INSUFFICIENT":
            continue
        if row["number_opposite_risk"] == "HIGH":
            continue
        blocked.append(n)
    # Outcome is accessed only after all three candidate sets are frozen.
    outcome = next(draw for draw in load_draw_csv(STAGING) if draw.round == target)
    main = set(outcome.main)
    return {
        "target": target, "source_max": target - 1,
        "official": official, "fixed_variant": fixed, "blocked_only": blocked,
        "official_hits": len(main & set(official)), "fixed_variant_hits": len(main & set(fixed)),
        "blocked_only_hits": len(main & set(blocked)),
    }


def bucket(n: int) -> str:
    return str(n) if n <= 5 else ">=6"


def rate(hits: int, count: int) -> float | None:
    return hits / count if count else None


def main() -> None:
    state = json.loads((ROOT / "00_P45_STATE/P45_CURRENT_STATE.json").read_text(encoding="utf-8-sig"))
    if state["state_version"] != "1.0.88" or state["last_decision_id"] != "DECISION-20260824-095" or sha(STAGING) != EXPECTED_STAGING_SHA or sha(PROTOCOL) != EXPECTED_PROTOCOL_SHA:
        raise RuntimeError("STOP_STATE_DRIFT_OR_INPUT_MISMATCH")
    with ProcessPoolExecutor(max_workers=8) as executor:
        rows = list(executor.map(one_target, range(3, 1239), chunksize=1))
    rows.sort(key=lambda row: row["target"])
    activated = [row for row in rows if row["blocked_only"]]
    obs = sum(len(row["blocked_only"]) for row in activated)
    hits = sum(row["blocked_only_hits"] for row in activated)
    blocked_rate = rate(hits, obs)
    p0 = 6 / 45
    delta = blocked_rate - p0 if blocked_rate is not None else None
    rng = random.Random(20260825)
    boot = []
    for _ in range(10000):
        sample = [activated[rng.randrange(len(activated))] for _ in activated]
        sample_n = sum(len(row["blocked_only"]) for row in sample)
        sample_hits = sum(row["blocked_only_hits"] for row in sample)
        boot.append(sample_hits / sample_n - p0)
    boot.sort()
    ci = [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]]
    min_pass = len(activated) >= 100 and obs >= 300
    if not min_pass:
        verdict = "INCONCLUSIVE_MIN_SAMPLE"
    elif ci[1] < 0:
        verdict = "SAFEGUARD_SUPPORTED"
    elif ci[0] > 0:
        verdict = "FILTER_HARM_SIGNAL"
    else:
        verdict = "INCONCLUSIVE"
    off_dist, fixed_dist = Counter(bucket(len(row["official"])) for row in rows), Counter(bucket(len(row["fixed_variant"])) for row in rows)
    keys = ["0", "1", "2", "3", "4", "5", ">=6"]
    off_count, fixed_count = sum(len(row["official"]) for row in rows), sum(len(row["fixed_variant"]) for row in rows)
    off_hits, fixed_hits = sum(row["official_hits"] for row in rows), sum(row["fixed_variant_hits"] for row in rows)
    result = {
        "final_verdict": "OPPOSITE_PERIOD_STABILITY_FILTER_VALIDATION_COMPLETE",
        "protocol_locked": True, "protocol_sha256": sha(PROTOCOL), "first_valid_target": 3, "last_target": 1238,
        "target_round_count": len(rows), "activated_rounds": len(activated), "blocked_only_observations": obs,
        "minimum_sample_pass": min_pass, "blocked_only_main_hits": hits, "blocked_only_main_hit_rate": blocked_rate,
        "random_baseline": p0, "delta_random": delta, "cluster_bootstrap_95_ci": ci, "bootstrap_replicates": 10000, "bootstrap_seed": 20260825,
        "primary_verdict": verdict,
        "official_survivor_count_distribution": {key: off_dist.get(key, 0) for key in keys},
        "fixed_variant_survivor_count_distribution": {key: fixed_dist.get(key, 0) for key in keys},
        "official_average_eligible_count": off_count / len(rows), "fixed_variant_average_eligible_count": fixed_count / len(rows),
        "official_eligible_observations": off_count, "official_eligible_main_hits": off_hits, "official_eligible_main_hit_rate": rate(off_hits, off_count),
        "fixed_variant_eligible_observations": fixed_count, "fixed_variant_eligible_main_hits": fixed_hits, "fixed_variant_eligible_main_hit_rate": rate(fixed_hits, fixed_count),
        "blocked_only_average_candidates_per_activated_round": obs / len(activated),
        "official_average_main_hits_captured_per_round": off_hits / len(rows), "fixed_variant_average_main_hits_captured_per_round": fixed_hits / len(rows),
        "multiple_testing_policy": {"primary_hypotheses":1,"patterns":1,"metrics":1,"threshold_search":0,"lookback_search":0,"subgroup_rescue":0,"parameter_tuning":0,"status":"PASS"},
        "future_source_access_count": 0, "target_1239_scoring": 0,
        "partial_survivor_reporting": {"id":"PARTIAL_SURVIVOR_REPORTING","status":"REPORTING_POLICY_DIRECTION_CONFIRMED","reporting_minimum":"NONE"},
    }
    evidence = OUT / "P45_OPPOSITE_PERIOD_STABILITY_FILTER_VALIDATION_EVIDENCE_001.csv"
    with evidence.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["target","source_max","official_count","fixed_variant_count","blocked_only_count","official_hits","fixed_variant_hits","blocked_only_hits","blocked_only_numbers"])
        for row in rows:
            writer.writerow([row["target"],row["source_max"],len(row["official"]),len(row["fixed_variant"]),len(row["blocked_only"]),row["official_hits"],row["fixed_variant_hits"],row["blocked_only_hits"]," ".join(map(str,row["blocked_only"]))])
    result["evidence_csv_sha256"] = sha(evidence)
    result_path = OUT / "P45_OPPOSITE_PERIOD_STABILITY_FILTER_VALIDATION_RESULT_001.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

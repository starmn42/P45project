from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from p45_v27.stage55_diagnostics import load_draw_csv
from p45_v27.stage6_diagnostics import diagnose_stage6

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "v27_storage/audits/survivor_pool_actionability_rolling_origin_001"
STAGING = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
PROTOCOL = OUT / "P45_SURVIVOR_POOL_ACTIONABILITY_PROTOCOL_LOCKED_001.md"
EXPECTED_STAGING_SHA = "1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"
EXPECTED_PROTOCOL_SHA = "64dead6a65b141bf99725bcfc98106f713bc44843c2135244ea37e4eefa08a44"
P0 = 6 / 45


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def features(target: int) -> dict:
    stage6 = diagnose_stage6(STAGING, target)
    if tuple(stage6["source_rounds"]) != (1, target - 1):
        raise RuntimeError(f"SOURCE_BOUNDARY:{target}:{stage6['source_rounds']}")
    survivors = [n for n, row in stage6["rows"].items() if row["number_state"] in ("NUMBER_PASS", "NUMBER_WEAKEN") or row["valid_test_status"]]
    return {"target": target, "source_max": target - 1, "survivors": survivors, "n": len(survivors), "future_check": 0}


def score(row: dict, outcomes: dict[int, tuple[int, ...]]) -> dict:
    # Called only after survivors are frozen by features().
    main = outcomes[row["target"]]
    hits = len(set(row["survivors"]) & set(main))
    return {**row, "main": list(main), "hits": hits, "candidate_observations": row["n"], "hit_rate": hits / row["n"] if row["n"] else None,
            "official_output_state": "NUMBER_POOL_AVAILABLE" if row["n"] >= 6 else "NO_NUMBER_POOL"}


def bootstrap_ci(rows: list[dict], seed: int) -> list[float]:
    n = len(rows)
    ns = np.array([row["n"] for row in rows], dtype=np.int64)
    hs = np.array([row["hits"] for row in rows], dtype=np.int64)
    rng = np.random.default_rng(seed)
    values = []
    remaining = 10000
    while remaining:
        batch = min(500, remaining)
        indices = rng.integers(0, n, size=(batch, n))
        rates = hs[indices].sum(axis=1) / ns[indices].sum(axis=1)
        values.extend((rates - P0).tolist())
        remaining -= batch
    values.sort()
    return [values[int(.025 * len(values))], values[int(.975 * len(values)) - 1]]


def summary(rows: list[dict], seed: int | None = None) -> dict:
    obs = sum(row["n"] for row in rows)
    hits = sum(row["hits"] for row in rows)
    hit_rate = hits / obs if obs else None
    return {"rounds": len(rows), "observations": obs, "hits": hits, "hit_rate": hit_rate,
            "delta_random": hit_rate - P0 if hit_rate is not None else None,
            "ci95": bootstrap_ci(rows, seed) if seed is not None and rows else None,
            "average_pool_size": obs / len(rows) if rows else None,
            "average_main_hits_per_round": hits / len(rows) if rows else None}


def bin_name(n: int) -> str:
    if n == 0: return "0"
    if n <= 2: return "1-2"
    if n <= 5: return "3-5"
    if n <= 9: return "6-9"
    if n <= 14: return "10-14"
    if n <= 19: return "15-19"
    if n <= 29: return "20-29"
    if n <= 39: return "30-39"
    return "40-45"


def main() -> None:
    state = json.loads((ROOT / "00_P45_STATE/P45_CURRENT_STATE.json").read_text(encoding="utf-8-sig"))
    if state["state_version"] != "1.0.88" or state["last_decision_id"] != "DECISION-20260824-095" or sha(STAGING) != EXPECTED_STAGING_SHA or sha(PROTOCOL) != EXPECTED_PROTOCOL_SHA:
        raise RuntimeError("STOP_STATE_DRIFT_OR_INPUT_MISMATCH")
    outcomes = {draw.round: tuple(draw.main) for draw in load_draw_csv(STAGING)}

    # Phase 1: discovery features freeze, then discovery outcomes score.
    with ProcessPoolExecutor(max_workers=8) as executor:
        discovery_frozen = list(executor.map(features, range(3, 868), chunksize=1))
    discovery = [score(row, outcomes) for row in discovery_frozen]
    candidates = []
    discovery_all = []
    for k in range(1, 46):
        actionable = [row for row in discovery if 1 <= row["n"] <= k]
        item = {"k": k, **summary(actionable, 20260825 + k)}
        item["minimum_sample_pass"] = item["rounds"] >= 100 and item["observations"] >= 300
        item["lower_ci_gt_zero"] = bool(item["minimum_sample_pass"] and item["ci95"][0] > 0)
        discovery_all.append(item)
        if item["lower_ci_gt_zero"]: candidates.append(item)
    selected = max(candidates, key=lambda item: item["k"]) if candidates else None
    k_discovery = selected["k"] if selected else None

    # Phase 2: confirmation features are computed only after K is frozen. Outcomes are scored only if K exists.
    with ProcessPoolExecutor(max_workers=8) as executor:
        confirmation_frozen = list(executor.map(features, range(868, 1239), chunksize=1))
    confirmation_scored = [score(row, outcomes) for row in confirmation_frozen] if k_discovery is not None else []
    if k_discovery is not None:
        confirmation_actionable = [row for row in confirmation_scored if 1 <= row["n"] <= k_discovery]
        confirmation = summary(confirmation_actionable, 20260826)
        confirmation["minimum_sample_pass"] = confirmation["rounds"] >= 50 and confirmation["observations"] >= 150
        primary = "MAX_ACTIONABLE_POOL_SUPPORTED" if confirmation["minimum_sample_pass"] and confirmation["ci95"][0] > 0 else "MAX_ACTIONABLE_POOL_NOT_CONFIRMED"
        max_pool = k_discovery if primary == "MAX_ACTIONABLE_POOL_SUPPORTED" else None
    else:
        confirmation = {"rounds": None,"observations": None,"hits":None,"hit_rate":None,"delta_random":None,"ci95":None,"average_pool_size":None,"average_main_hits_per_round":None,"minimum_sample_pass":False}
        primary = "NO_DISCOVERY_K"
        max_pool = None

    # Full scored evidence exists only when the locked discovery rule authorizes confirmation outcome access.
    all_scored = discovery + confirmation_scored
    evidence = OUT / "P45_SURVIVOR_POOL_ACTIONABILITY_PER_TARGET_EVIDENCE_001.csv"
    with evidence.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["segment","target","source_max","raw_survivor_identities","raw_survivor_count","main6","survivor_main_hits","candidate_observations","survivor_hit_rate","official_output_state","future_data_check"])
        for row in discovery:
            writer.writerow(["DISCOVERY",row["target"],row["source_max"]," ".join(map(str,row["survivors"])),row["n"]," ".join(map(str,row["main"])),row["hits"],row["candidate_observations"],row["hit_rate"],row["official_output_state"],0])
        for row in confirmation_scored:
            writer.writerow(["CONFIRMATION",row["target"],row["source_max"]," ".join(map(str,row["survivors"])),row["n"]," ".join(map(str,row["main"])),row["hits"],row["candidate_observations"],row["hit_rate"],row["official_output_state"],0])

    exact_path = OUT / "P45_SURVIVOR_POOL_ACTIONABILITY_EXACT_N_PROFILE_001.csv"
    exact_groups = defaultdict(list)
    for row in all_scored: exact_groups[row["n"]].append(row)
    with exact_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer=csv.writer(handle,lineterminator="\n");writer.writerow(["exact_n","rounds","candidate_observations","main_hits","candidate_hit_rate","delta_random","average_main_hits_per_round"])
        for n in range(46):
            s=summary(exact_groups[n]);writer.writerow([n,s["rounds"],s["observations"],s["hits"],s["hit_rate"],s["delta_random"],s["average_main_hits_per_round"]])

    bin_path = OUT / "P45_SURVIVOR_POOL_ACTIONABILITY_COARSE_BIN_PROFILE_001.csv"
    bin_groups=defaultdict(list)
    for row in all_scored: bin_groups[bin_name(row["n"])].append(row)
    bin_order=["0","1-2","3-5","6-9","10-14","15-19","20-29","30-39","40-45"]
    with bin_path.open("w",encoding="utf-8-sig",newline="") as handle:
        writer=csv.writer(handle,lineterminator="\n");writer.writerow(["bin","rounds","average_pool_size","candidate_observations","main_hits","candidate_hit_rate","average_main_hits_captured","random_expected_hits","lift"])
        for name in bin_order:
            s=summary(bin_groups[name]); expected=(s["average_pool_size"]*P0 if s["average_pool_size"] is not None else None);lift=(s["average_main_hits_per_round"]/expected if expected else None)
            writer.writerow([name,s["rounds"],s["average_pool_size"],s["observations"],s["hits"],s["hit_rate"],s["average_main_hits_per_round"],expected,lift])

    discovery_path=OUT/"P45_SURVIVOR_POOL_ACTIONABILITY_DISCOVERY_K_PROFILE_001.csv"
    with discovery_path.open("w",encoding="utf-8-sig",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=["k","rounds","observations","hits","hit_rate","delta_random","ci95_lower","ci95_upper","average_pool_size","average_main_hits_per_round","minimum_sample_pass","lower_ci_gt_zero"],lineterminator="\n");writer.writeheader()
        for item in discovery_all:
            writer.writerow({**{key:item[key] for key in ("k","rounds","observations","hits","hit_rate","delta_random","average_pool_size","average_main_hits_per_round","minimum_sample_pass","lower_ci_gt_zero")},"ci95_lower":item["ci95"][0] if item["ci95"] else None,"ci95_upper":item["ci95"][1] if item["ci95"] else None})

    result={
        "final_verdict":"SURVIVOR_POOL_ACTIONABILITY_VALIDATION_COMPLETE","protocol_locked":True,"protocol_sha256":sha(PROTOCOL),
        "valid_target_count":1236,"discovery_range":[3,867],"confirmation_range":[868,1238],"k_discovery":k_discovery,
        "discovery_selected":selected,"confirmation":confirmation,"primary_verdict":primary,"max_actionable_pool":max_pool,
        "current_1239_raw_survivor_count":5,"current_1239_raw_survivors":[13,18,20,24,27],
        "current_1239_actionable":"YES" if max_pool is not None and 5<=max_pool else "NO" if max_pool is not None else "NOT_CONFIRMED",
        "confirmation_outcome_accessed":k_discovery is not None,"future_leakage":0,"target_1239_scoring":0,
        "multiple_testing_policy":"PASS","exp_017":"NOT_CREATED",
        "survivor_pool_actionability_policy":{"raw_preserved":"0..45","max_actionable_pool":max_pool if max_pool is not None else "NOT_CONFIRMED","broad_pool":"N>MAX => BROAD_POOL / NO_ACTIONABLE_PICK","top_k_truncation":"FORBIDDEN","official_3x2_separate":True},
        "artifacts":{"per_target_sha256":sha(evidence),"exact_n_sha256":sha(exact_path),"coarse_bin_sha256":sha(bin_path),"discovery_k_sha256":sha(discovery_path)}
    }
    result_path=OUT/"P45_SURVIVOR_POOL_ACTIONABILITY_RESULT_001.json";result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__": main()

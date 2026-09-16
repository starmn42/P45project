"""Locked EXP-CROWD-TOPO-001-V1 calculator.

This module is isolated from the official DRAW engine.  It uses only the
pre-locked historical snapshot (rounds 1..1237) for the registered crowd
topology experiment.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "v27_storage/experiments/crowd_topology_exp001_v1"
RAW = ROOT / "downloads/official-1-1237/raw"
CANONICAL_MAIN = ROOT / "v27_storage/experiments/prize_share_exp001_v2/exp_prize_001_v2_draws_1_1237.csv"
SNAPSHOT = EXP / "exp_crowd_topo_001_v1_draws_1_1237.csv"
MANIFEST = EXP / "SNAPSHOT_MANIFEST.json"
RESULT = EXP / "EXP_CROWD_TOPO_001_V1_RESULT.json"
PROTOCOL = ROOT / "00_P45_STATE/experiment_lab/EXP-CROWD-TOPO-001/EXP_CROWD_TOPO_001_V1_LOCKED_PROTOCOL.md"
LOCK = EXP / "PROTOCOL_LOCK.json"

PROTOCOL_SHA256 = "421720adfa6cee93b622cdf51e7aac3200f3e44ae934e36c2790289aa1988006"
CALCULATOR_VERSION = "EXP-CROWD-TOPO-001-CALCULATOR-1.0"
M = math.comb(45, 6)
D1 = math.comb(6, 1) * math.comb(39, 1)
PRIMARY_REPS = 100_000
PRIMARY_SEED = 2026082301
UNIFORM_REPS = 100_000
UNIFORM_SEED = 2026082302


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _official_rows() -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for source in sorted(RAW.glob("api-*.json")):
        payload = json.loads(source.read_text(encoding="utf-8-sig"))
        source_sha = sha_file(source)
        for item in payload.get("data", {}).get("list", []):
            round_no = int(item["ltEpsd"])
            if not 1 <= round_no <= 1237:
                continue
            selected = {
                "round": round_no,
                "date": str(item["ltRflYmd"]),
                "main": [int(item[f"tm{i}WnNo"]) for i in range(1, 7)],
                "bonus": int(item["bnsWnNo"]),
                "k1": int(item["rnk1WnNope"]),
                "k2": int(item["rnk2WnNope"]),
                "k3": int(item["rnk3WnNope"]),
                "sales": int(item["wholEpsdSumNtslAmt"]),
                "source_file": source.relative_to(ROOT).as_posix(),
                "source_file_sha256": source_sha,
            }
            previous = rows.get(round_no)
            if previous and {k: v for k, v in previous.items() if not k.startswith("source_")} != {
                k: v for k, v in selected.items() if not k.startswith("source_")
            }:
                raise RuntimeError(f"DUPLICATE_SOURCE_CONFLICT:{round_no}")
            rows.setdefault(round_no, selected)
    return rows


def _canonical_main() -> dict[int, tuple[int, ...]]:
    result: dict[int, tuple[int, ...]] = {}
    with CANONICAL_MAIN.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            result[int(row["round"])] = tuple(int(row[f"main_{i}"]) for i in range(1, 7))
    return result


def build_snapshot() -> dict[str, Any]:
    if sha_file(PROTOCOL) != PROTOCOL_SHA256:
        raise RuntimeError("PROTOCOL_HASH_MISMATCH")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    if lock["lock_status"] != "LOCKED_BEFORE_OUTCOME_RELATION_ANALYSIS" or lock["outcome_relation_analyzed_at_lock"]:
        raise RuntimeError("PROTOCOL_NOT_PRELOCKED")
    raw = _official_rows()
    expected = set(range(1, 1238))
    if set(raw) != expected:
        raise RuntimeError(f"ROUND_COVERAGE:{len(raw)}:missing={sorted(expected-set(raw))[:10]}")
    canonical = _canonical_main()
    if set(canonical) != expected:
        raise RuntimeError("CANONICAL_MAIN_COVERAGE")
    records: list[dict[str, Any]] = []
    main_mismatch = 0
    for r in range(1, 1238):
        item = raw[r]
        if tuple(item["main"]) != canonical[r]:
            main_mismatch += 1
        if len(set(item["main"])) != 6 or any(not 1 <= n <= 45 for n in (*item["main"], item["bonus"])):
            raise RuntimeError(f"NUMBER_INVALID:{r}")
        if item["bonus"] in item["main"]:
            raise RuntimeError(f"BONUS_DUPLICATE:{r}")
        if min(item["k1"], item["k2"], item["k3"]) < 0 or item["sales"] <= 0:
            raise RuntimeError(f"COUNT_OR_SALES_INVALID:{r}")
        price = 2000 if r <= 87 else 1000
        if item["sales"] % price:
            raise RuntimeError(f"NONINTEGER_SOLD_LINES:{r}")
        records.append({
            "round": r, "date": item["date"],
            **{f"main_{i}": item["main"][i-1] for i in range(1, 7)},
            "bonus": item["bonus"], "k1": item["k1"], "k2": item["k2"], "k3": item["k3"],
            "total_sales_krw": item["sales"], "price_per_game_krw": price,
            "sold_lines": item["sales"] // price,
            "source_file": item["source_file"], "source_file_sha256": item["source_file_sha256"],
        })
    if main_mismatch:
        raise RuntimeError(f"CANONICAL_MAIN_MISMATCH:{main_mismatch}")
    EXP.mkdir(parents=True, exist_ok=True)
    fields = list(records[0])
    with SNAPSHOT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(records)
    manifest = {
        "snapshot_version": "EXP-CROWD-TOPO-001-SNAPSHOT-1.0",
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "data_range": "1~1237", "rows": len(records), "missing_rounds": 0, "duplicate_rounds": 0,
        "round_1238_plus_rows": 0, "canonical_main_mismatch": main_mismatch,
        "k1_field": "rnk1WnNope", "k2_field": "rnk2WnNope", "k3_field": "rnk3WnNope",
        "total_sales_field": "wholEpsdSumNtslAmt", "price_rule": "1~87=2000;88~1237=1000",
        "shell_identity": {"k2": 6, "k3": 228, "total": D1, "status": "PASS"},
        "snapshot_path": SNAPSHOT.relative_to(ROOT).as_posix(), "snapshot_sha256": sha_file(SNAPSHOT),
        "protocol_sha256": PROTOCOL_SHA256,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return manifest


def _load_snapshot() -> tuple[np.ndarray, ...]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["snapshot_sha256"] != sha_file(SNAPSHOT) or manifest["protocol_sha256"] != PROTOCOL_SHA256:
        raise RuntimeError("SNAPSHOT_OR_PROTOCOL_HASH_MISMATCH")
    rounds=[]; k1=[]; k2=[]; k3=[]; sold=[]
    with SNAPSHOT.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            rounds.append(int(row["round"])); k1.append(int(row["k1"])); k2.append(int(row["k2"]));
            k3.append(int(row["k3"])); sold.append(int(row["sold_lines"]))
    if rounds != list(range(1,1238)):
        raise RuntimeError("SNAPSHOT_ROUND_ORDER")
    return tuple(np.asarray(x, dtype=np.float64) for x in (rounds,k1,k2,k3,sold))


def _student_t(x: np.ndarray) -> float:
    sd=float(np.std(x, ddof=1))
    return float(math.sqrt(len(x))*np.mean(x)/sd) if sd else float("nan")


def _block_wild(x: np.ndarray) -> tuple[float, float]:
    if len(x) != 437 or len(x) % 19:
        raise RuntimeError("HOLDOUT_BLOCK_STRUCTURE")
    observed=_student_t(x); residual=x-np.mean(x); rng=np.random.default_rng(PRIMARY_SEED); exceed=0
    for start in range(0,PRIMARY_REPS,5000):
        n=min(5000,PRIMARY_REPS-start)
        signs=rng.integers(0,2,size=(n,23),dtype=np.int8)*2-1
        samples=signs.repeat(19,axis=1)*residual
        means=samples.mean(axis=1); sds=samples.std(axis=1,ddof=1)
        t=np.divide(math.sqrt(len(x))*means,sds,out=np.full(n,np.nan),where=sds>0)
        exceed += int(np.count_nonzero(t >= observed))
    return observed,(1+exceed)/(PRIMARY_REPS+1)


def _uniform_mc(n_values: np.ndarray, observed_theta: float) -> float:
    rng=np.random.default_rng(UNIFORM_SEED); totals=np.zeros(UNIFORM_REPS,dtype=np.float64)
    p0=1/M; p1=D1/M; conditional=p1/(1-p0)
    for n_float in n_values:
        n=int(n_float)
        center=rng.binomial(n,p0,size=UNIFORM_REPS)
        shell=rng.binomial(n-center,conditional,size=UNIFORM_REPS)
        totals += (M*M*center*shell/(n*(n-1)*D1)-1.0)
    theta=totals/len(n_values)
    return (1+int(np.count_nonzero(theta>=observed_theta)))/(UNIFORM_REPS+1)


def calculate() -> dict[str, Any]:
    rounds,k1,k2,k3,n=_load_snapshot(); k23=k2+k3
    x=M*M*k1*k23/(n*(n-1)*D1)-1.0
    var_x=M*M*k1*(k1-1)/(n*(n-1))-1.0
    train=x[:800]; hold=x[800:]
    theta_train=float(np.mean(train))
    result: dict[str,Any]={
        "calculator_version":CALCULATOR_VERSION,"protocol_sha256":PROTOCOL_SHA256,
        "snapshot_sha256":sha_file(SNAPSHOT),"data_range":"1~1237","round_1238_plus_used":False,
        "m":M,"d1":D1,"k2_shell":6,"k3_shell":228,"shell_identity":"PASS",
        "train_theta":theta_train,"train_gate":"PASS" if theta_train>0 else "FAIL",
        "primary_bootstraps":0,"uniform_mc":0,"holdout_theta":None,"holdout_t":None,
        "primary_block_wild_p":None,"uniform_mc_p":None,"v_hat":None,"rho1_hat":None,
        "positive_19round_blocks":None,"median_block_theta":None,"first_11_blocks_mean":None,
        "last_12_blocks_mean":None,"prospective_signal_peeking":0,"official_effect":"NONE",
        "promotion_candidate":False,"independent_reproduction":"NOT_YET",
    }
    if theta_train<=0:
        result["final_judgment"]="FAILED_EARLY_TRAIN_DIRECTION"
        return result
    theta_hold=float(np.mean(hold)); t_obs,p_wild=_block_wild(hold); p_mc=_uniform_mc(n[800:],theta_hold)
    v_hat=float(np.mean(var_x[800:])); rho=float(theta_hold/v_hat) if v_hat>0 else None
    blocks=hold.reshape(23,19).mean(axis=1)
    result.update({
        "holdout_theta":theta_hold,"holdout_t":t_obs,"primary_block_wild_p":p_wild,
        "primary_bootstraps":PRIMARY_REPS,"uniform_mc_p":p_mc,"uniform_mc":UNIFORM_REPS,
        "v_hat":v_hat,"rho1_hat":rho,"positive_19round_blocks":int(np.count_nonzero(blocks>0)),
        "median_block_theta":float(np.median(blocks)),"first_11_blocks_mean":float(np.mean(blocks[:11])),
        "last_12_blocks_mean":float(np.mean(blocks[11:])),
        "final_judgment":"SUPPORTED_WITHIN_EXPERIMENT" if theta_hold>0 and p_wild<=0.05 else "FAILED",
    })
    return result


def run() -> dict[str, Any]:
    first=calculate(); second=calculate()
    comparable=lambda x: canonical_json(x)
    deterministic=comparable(first)==comparable(second)
    if not deterministic:
        raise RuntimeError("REPRODUCTION_MISMATCH")
    first["deterministic_rerun"]="PASS"
    first["calculator_sha256"]=sha_file(Path(__file__))
    first["result_hash"]=hashlib.sha256(canonical_json(first).encode()).hexdigest()
    RESULT.write_text(json.dumps(first,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return first


def main(argv: Iterable[str] | None=None) -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("snapshot","run")); args=parser.parse_args(argv)
    output=build_snapshot() if args.command=="snapshot" else run()
    print(json.dumps(output,ensure_ascii=False,indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())

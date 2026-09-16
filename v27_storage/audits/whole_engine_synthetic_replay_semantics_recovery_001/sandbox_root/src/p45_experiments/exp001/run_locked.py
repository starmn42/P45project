from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import sqlite3
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .calculator import clopper_pearson_95, phi_coefficient, prediction_hash, unordered_pairs
from .constants import EXPERIMENT_ID, MAXT_REPETITIONS, MAXT_SEED, PROTOCOL_VERSION, SCHEMA_VERSION
from .protocol import canonical_json, verify_protocol_lock
from .snapshot import DrawRow, ROOT, canonical_csv_bytes, file_sha256, load_source_rows

RUNTIME_PYTHON = Path(r"C:\Users\sung2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
NODE = Path(r"C:\Users\sung2\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe")
STORE = ROOT / "v27_storage/experiments/exp001/exp001_research.sqlite3"
SNAPSHOT = ROOT / "v27_storage/experiments/exp001/data/exp001_draws_1_1237.csv"
SNAPSHOT_MANIFEST = ROOT / "v27_storage/experiments/exp001/data/exp001_data_snapshot_manifest.json"
EXECUTION_LOCK = ROOT / "v27_storage/experiments/exp001/exp001_execution_lock.json"
REPORT = ROOT / "v27_storage/experiments/exp001/exp001_locked_run_report.json"
PROGRESS = ROOT / "v27_storage/experiments/exp001/exp001_run_progress.json"
FIXED_SCRIPT = Path(__file__).with_name("fixed_marginal.js")
PAIRS = unordered_pairs()
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
TRIU = np.triu_indices(45, 1)

RUN_SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS retrospective_summary(
 run_id TEXT NOT NULL REFERENCES experiment_run(run_id), scope TEXT NOT NULL, period TEXT NOT NULL,
 holm_pass_count INTEGER NOT NULL, maxT_pass_count INTEGER, maxT_global_p REAL,
 positive_count INTEGER NOT NULL, negative_count INTEGER NOT NULL, neutral_count INTEGER NOT NULL,
 summary_json TEXT NOT NULL, PRIMARY KEY(run_id,scope,period));
CREATE TABLE IF NOT EXISTS experiment_judgment(
 run_id TEXT PRIMARY KEY REFERENCES experiment_run(run_id), retrospective_result TEXT NOT NULL,
 walkforward_result TEXT NOT NULL, final_judgment TEXT NOT NULL, explanation_code TEXT NOT NULL,
 promotion_candidate INTEGER NOT NULL CHECK(promotion_candidate=0), official_recommendation_allowed INTEGER NOT NULL CHECK(official_recommendation_allowed=0),
 judgment_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS run_metadata(
 run_id TEXT NOT NULL REFERENCES experiment_run(run_id), key TEXT NOT NULL, value_json TEXT NOT NULL,
 PRIMARY KEY(run_id,key));
"""


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def code_hash() -> str:
    files = sorted(Path(__file__).parent.glob("*.py")) + [FIXED_SCRIPT]
    lines = [f"{path.name}|{path.stat().st_size}|{file_sha256(path)}" for path in files]
    return sha_bytes(("\n".join(lines) + "\n").encode())


def preflight() -> tuple[dict[str, Any], dict[str, Any], str]:
    snapshot_manifest = json.loads(SNAPSHOT_MANIFEST.read_text(encoding="utf-8"))
    if file_sha256(SNAPSHOT) != snapshot_manifest["snapshot_sha256"]:
        raise RuntimeError("LOCK_MISMATCH_ABORT:DATA_SNAPSHOT_HASH")
    protocol = verify_protocol_lock()
    if protocol["canonical_protocol_hash"] != "2d4e723b87bc2f44a7a0d763ee4779ded40b007f3cbf4b093b9e771c9248dd9d":
        raise RuntimeError("LOCK_MISMATCH_ABORT:PROTOCOL_HASH")
    connection = sqlite3.connect(STORE)
    try:
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or connection.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("LOCK_MISMATCH_ABORT:EXPERIMENT_DB")
    finally:
        connection.close()
    protected = json.loads((ROOT / "v27_storage/manifests/protected-canonical-v1.json").read_text(encoding="utf-8-sig"))
    if protected["canonical_manifest_sha256"] != "7c1458328a17a0824622c00ce1f54996e22ed4c2e9d04180be4ad9029ba8febb":
        raise RuntimeError("LOCK_MISMATCH_ABORT:PROTECTED_CANONICAL")
    return snapshot_manifest, protocol, protected["canonical_manifest_sha256"]


def binomial_two_sided_table(n: int, p: float) -> np.ndarray:
    ks = np.arange(n + 1, dtype=np.float64)
    logs = np.array([math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log1p(-p) for k in range(n + 1)])
    probs = np.exp(logs)
    order = np.argsort(probs, kind="stable")
    cumulative = np.cumsum(probs[order])
    result = np.empty(n + 1)
    result[order] = np.minimum(1.0, cumulative)
    return result


def binomial_one_sided(successes: int, n: int, p: float, direction: str) -> float:
    logs = np.array([math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log1p(-p) for k in range(n + 1)])
    probs = np.exp(logs)
    return float(probs[successes:].sum() if direction == "POSITIVE" else probs[: successes + 1].sum())


def holm(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="stable")
    out = np.zeros_like(values)
    running = 0.0
    m = len(values)
    for rank, index in enumerate(order):
        running = max(running, min(1.0, float(values[index]) * (m - rank)))
        out[index] = running
    return out


def incidence(rows: list[DrawRow], scope: str) -> np.ndarray:
    x = np.zeros((len(rows), 45), dtype=np.int16)
    for i, row in enumerate(rows):
        numbers = row.main if scope == "MAIN" else (*row.main, row.bonus)
        x[i, np.array(numbers) - 1] = 1
    return x


def pair_counts(x: np.ndarray) -> np.ndarray:
    return (x.T @ x)[TRIU].astype(np.int32)


def period_slices(n: int) -> dict[str, slice]:
    split = n // 2
    return {
        "OVERALL": slice(0, n), "FIRST_HALF": slice(0, split), "SECOND_HALF": slice(split, n),
        "RECENT_100": slice(max(0, n - 100), n), "RECENT_50": slice(max(0, n - 50), n), "RECENT_20": slice(max(0, n - 20), n),
    }


def metrics_for(x: np.ndarray, scope: str) -> dict[str, dict[str, Any]]:
    p0 = 1 / 66 if scope == "MAIN" else 7 / 330
    output = {}
    for period, window in period_slices(len(x)).items():
        part = x[window]
        n = len(part)
        counts = pair_counts(part)
        raw = binomial_two_sided_table(n, p0)[counts]
        adjusted = holm(raw)
        expected = n * p0
        rate = counts / n
        rd = rate - p0
        residual = (counts - expected) / math.sqrt(n * p0 * (1 - p0))
        output[period] = {"n": n, "counts": counts, "raw": raw, "adjusted": adjusted, "rate": rate, "rd": rd, "residual": residual}
    return output


def ensure_run(connection: sqlite3.Connection, lock: dict[str, Any], snapshot_hash: str, run_id: str, c_hash: str) -> None:
    connection.executescript(RUN_SCHEMA)
    existing = connection.execute("SELECT run_id,protocol_hash,data_snapshot_hash,code_hash,execution_status FROM experiment_run").fetchall()
    if existing:
        row = existing[0]
        if row[0] != run_id or row[1] != lock["canonical_protocol_hash"] or row[2] != snapshot_hash or row[3] != c_hash:
            raise RuntimeError("LOCK_MISMATCH_ABORT:EXISTING_RUN")
        return
    connection.execute("INSERT INTO experiment_run VALUES(?,?,?,?,?,?,?,?)", (run_id, EXPERIMENT_ID, lock["canonical_protocol_hash"], snapshot_hash, c_hash, "RUNNING", datetime.now(timezone.utc).isoformat(), None))
    connection.commit()


def store_static(connection: sqlite3.Connection, run_id: str, scope: str, period: str, x: np.ndarray, metric: dict[str, Any]) -> None:
    if connection.execute("SELECT 1 FROM pair_result WHERE run_id=? AND scope=? AND period=?", (run_id, scope, period)).fetchone():
        return
    n = metric["n"]
    p0 = 1 / 66 if scope == "MAIN" else 7 / 330
    number_counts = x.sum(axis=0)
    rows = []
    for index, (a, b) in enumerate(PAIRS):
        observed = int(metric["counts"][index])
        low, high = clopper_pearson_95(observed, n)
        a_count, b_count = int(number_counts[a - 1]), int(number_counts[b - 1])
        phi = phi_coefficient(observed, a_count - observed, b_count - observed, n - a_count - b_count + observed)
        secondary = {"lift": float(metric["rate"][index] / p0), "standardized_residual": float(metric["residual"][index]), "clopper_pearson_95": [low, high], "a_exposure_count": a_count, "b_exposure_count": b_count, "phi": phi, "test_only": period == "RECENT_20"}
        rid = sha_bytes(f"{run_id}|{scope}|{period}|{a}|{b}".encode())
        phash = prediction_hash({"run_id": run_id, "scope": scope, "period": period, "source_end_round": 1237, "pair": [a, b], "protocol": PROTOCOL_VERSION})
        rows.append((rid, run_id, a, b, scope, period, observed, n * p0, float(metric["rate"][index]), p0, float(metric["rd"][index]), json.dumps(secondary, sort_keys=True), float(metric["raw"][index]), float(metric["adjusted"][index]), phash))
    connection.executemany("INSERT INTO pair_result VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    connection.commit()


def iid_max_t(scope: str, n: int, p0: float, run_id: str, connection: sqlite3.Connection) -> np.ndarray:
    null_type = "IID_SYNTHETIC_NULL_MAXT"
    done = connection.execute("SELECT repetition_end,statistics_json FROM null_statistic WHERE run_id=? AND scope=? AND period='OVERALL' AND null_type=? ORDER BY repetition_start", (run_id, scope, null_type)).fetchall()
    maxima = []
    for end, payload in done:
        maxima.extend(json.loads(payload)["maxima"])
    start = len(maxima)
    width = 6 if scope == "MAIN" else 7
    lut = np.full((45, 45), -1, dtype=np.int16)
    for index, (a, b) in enumerate(PAIRS): lut[a - 1, b - 1] = index
    batch = 500
    for chunk_start in range(start, MAXT_REPETITIONS, batch):
        size = min(batch, MAXT_REPETITIONS - chunk_start)
        seed_sequence = np.random.SeedSequence([MAXT_SEED, 1 if scope == "MAIN" else 2, chunk_start // batch])
        rng = np.random.Generator(np.random.PCG64DXSM(seed_sequence))
        random_values = rng.random((size, n, 45), dtype=np.float32)
        selected = np.argpartition(random_values, width - 1, axis=2)[:, :, :width]
        del random_values
        base = (np.arange(size, dtype=np.int64) * 990)[:, None]
        counts = np.zeros((size, 990), dtype=np.int16)
        for i in range(width):
            for j in range(i + 1, width):
                a = np.minimum(selected[:, :, i], selected[:, :, j])
                b = np.maximum(selected[:, :, i], selected[:, :, j])
                indices = lut[a, b].astype(np.int64) + base
                counts += np.bincount(indices.ravel(), minlength=size * 990).reshape(size, 990).astype(np.int16)
        expected = n * p0
        denominator = math.sqrt(n * p0 * (1 - p0))
        values = np.max(np.abs((counts - expected) / denominator), axis=1).astype(float).tolist()
        chunk_end = chunk_start + size
        null_id = sha_bytes(f"{run_id}|{scope}|{null_type}|{chunk_start}|{chunk_end}".encode())
        payload = {"prng": "NUMPY-PCG64DXSM-2.3.5", "seed_root": MAXT_SEED, "chunk_index": chunk_start // batch, "maxima": values}
        connection.execute("INSERT INTO null_statistic VALUES(?,?,?,?,?,?,?,?,?)", (null_id, run_id, scope, "OVERALL", null_type, chunk_start, chunk_end, json.dumps(payload, separators=(",", ":")), sha_bytes(canonical_json(payload).encode())))
        connection.commit()
        maxima.extend(values)
        PROGRESS.write_text(json.dumps({"run_id": run_id, "phase": f"IID_MAXT_{scope}", "completed": chunk_end, "total": MAXT_REPETITIONS}) + "\n")
    return np.array(maxima)


def fixed_marginal(scope: str, run_id: str, connection: sqlite3.Connection) -> np.ndarray:
    null_type = "FIXED_MARGINAL_SWITCH_NULL"
    found = connection.execute("SELECT statistics_json FROM null_statistic WHERE run_id=? AND scope=? AND null_type=?", (run_id, scope, null_type)).fetchone()
    if found:
        return np.array(json.loads(found[0])["maxima"])
    output = STORE.parent / f"fixed_marginal_{scope.lower()}.json"
    seed = int.from_bytes(hashlib.sha256(f"{run_id}|{scope}|FIXED_MARGINAL".encode()).digest()[:4], "big")
    subprocess.run([str(NODE), str(FIXED_SCRIPT), "--input", str(SNAPSHOT), "--scope", scope, "--samples", "10000", "--seed", str(seed), "--output", str(output)], check=True)
    payload = json.loads(output.read_text(encoding="utf-8"))
    null_id = sha_bytes(f"{run_id}|{scope}|{null_type}".encode())
    connection.execute("INSERT INTO null_statistic VALUES(?,?,?,?,?,?,?,?,?)", (null_id, run_id, scope, "OVERALL", null_type, 0, 10000, json.dumps(payload, separators=(",", ":")), file_sha256(output)))
    connection.commit()
    return np.array(payload["maxima"])


class SequentialSource:
    def __init__(self, rows: list[DrawRow]): self.rows = {row.round: row for row in rows}; self.outcome_accesses = 0
    def load_outcome(self, round_no: int, locked: bool) -> DrawRow:
        if not locked: raise RuntimeError("FUTURE_LEAKAGE_OUTCOME_BEFORE_LOCK")
        self.outcome_accesses += 1
        return self.rows[round_no]


def walkforward(connection: sqlite3.Connection, run_id: str, rows: list[DrawRow]) -> dict[str, Any]:
    if connection.execute("SELECT COUNT(*) FROM walkforward_round WHERE run_id=?", (run_id,)).fetchone()[0] == 737:
        return summarize_walkforward(connection, run_id)
    source = SequentialSource(rows)
    x = incidence(rows[:500], "MAIN")
    cumulative = [np.zeros(990, dtype=np.int32)]
    for row_vector in x:
        current = cumulative[-1].copy()
        nums = np.flatnonzero(row_vector) + 1
        for pair in itertools.combinations(nums.tolist(), 2): current[PAIR_INDEX[pair]] += 1
        cumulative.append(current)
    p0 = 1 / 66
    for evaluation_round in range(501, 1238):
        existing_round = connection.execute("SELECT prediction_network_hash FROM walkforward_round WHERE run_id=? AND evaluation_round=?", (run_id, evaluation_round)).fetchone()
        if existing_round:
            outcome = source.load_outcome(evaluation_round, locked=bool(existing_round[0]))
            new_row = incidence([outcome], "MAIN")[0]
            current = cumulative[-1].copy()
            nums = np.flatnonzero(new_row) + 1
            for pair in itertools.combinations(nums.tolist(), 2): current[PAIR_INDEX[pair]] += 1
            cumulative.append(current)
            continue
        n = evaluation_round - 1
        all_counts = cumulative[n]
        split = n // 2
        first = cumulative[split]
        second = all_counts - first
        recent100 = all_counts - cumulative[max(0, n - 100)]
        recent50 = all_counts - cumulative[max(0, n - 50)]
        def evaluated(counts: np.ndarray, size: int) -> tuple[np.ndarray, np.ndarray]:
            raw = binomial_two_sided_table(size, p0)[counts]
            return counts / size - p0, holm(raw)
        rd_all, adj_all = evaluated(all_counts, n)
        rd_first, adj_first = evaluated(first, split)
        rd_second, adj_second = evaluated(second, n - split)
        rd100, _adj100 = evaluated(recent100, min(100, n))
        rd50, adj50 = evaluated(recent50, min(50, n))
        direction = np.sign(rd_all)
        same_halves = (np.sign(rd_first) == direction) & (np.sign(rd_second) == direction) & (direction != 0)
        recent100_same = np.sign(rd100) == direction
        recent50_opposite_significant = (np.sign(rd50) == -direction) & (adj50 < 0.05)
        selected_indices = np.flatnonzero((adj_all < 0.05) & same_halves & (adj_first < 0.05) & (adj_second < 0.05) & recent100_same & ~recent50_opposite_significant)
        selected_payload = [{"pair": PAIRS[int(index)], "direction": "POSITIVE" if direction[index] > 0 else "NEGATIVE"} for index in selected_indices]
        data_prefix_hash = prediction_hash({"snapshot": file_sha256(SNAPSHOT), "source_end_round": n})
        payload = {"run_id": run_id, "evaluation_round": evaluation_round, "source_end_round": n, "protocol_hash": verify_protocol_lock()["canonical_protocol_hash"], "selected": selected_payload, "pair_state_hash": sha_bytes(all_counts.tobytes())}
        phash = prediction_hash(payload)
        connection.execute("BEGIN IMMEDIATE")
        try:
            connection.execute("INSERT INTO walkforward_round VALUES(?,?,?,?,?,?,?)", (run_id, evaluation_round, n, "PREDICTION_LOCKED", data_prefix_hash, phash, 0))
            outcome = source.load_outcome(evaluation_round, locked=bool(phash))
            integrated = set((*outcome.main, outcome.bonus)); main = set(outcome.main)
            for index in selected_indices:
                a, b = PAIRS[int(index)]
                direction_name = "POSITIVE" if direction[index] > 0 else "NEGATIVE"
                eid = sha_bytes(f"{run_id}|{evaluation_round}|{a}|{b}".encode())
                connection.execute("INSERT INTO walkforward_exposure VALUES(?,?,?,?,?,?,?,?,?)", (eid, run_id, evaluation_round, a, b, direction_name, int({a,b} <= main), int({a,b} <= integrated), phash))
            connection.execute("UPDATE walkforward_round SET status=?,outcome_accessed=1 WHERE run_id=? AND evaluation_round=?", ("COMPLETE" if len(selected_indices) else "COMPLETE_NO_EDGE", run_id, evaluation_round))
            connection.commit()
        except Exception:
            connection.rollback(); raise
        new_row = incidence([outcome], "MAIN")[0]
        current = cumulative[-1].copy()
        nums = np.flatnonzero(new_row) + 1
        for pair in itertools.combinations(nums.tolist(), 2): current[PAIR_INDEX[pair]] += 1
        cumulative.append(current)
        if evaluation_round % 25 == 0:
            PROGRESS.write_text(json.dumps({"run_id": run_id, "phase": "WALKFORWARD", "completed_round": evaluation_round, "end_round": 1237}) + "\n")
    return summarize_walkforward(connection, run_id)


def round_order_permutation(connection: sqlite3.Connection, run_id: str, rows: list[DrawRow]) -> dict[str, Any]:
    null_type = "ROUND_ORDER_PERMUTATION_TEMPORAL_SUPPORT"
    found = connection.execute("SELECT statistics_json FROM null_statistic WHERE run_id=? AND scope='MAIN' AND null_type=?", (run_id, null_type)).fetchone()
    if found:
        return json.loads(found[0])
    grouped = connection.execute("SELECT pair_a,pair_b,direction,COUNT(*) n,SUM(main_occurrence) hits FROM walkforward_exposure WHERE run_id=? GROUP BY pair_a,pair_b,direction HAVING COUNT(*)>=200 ORDER BY pair_a,pair_b,direction", (run_id,)).fetchall()
    if not grouped:
        payload = {"version":"EXP001-ROUND-PERMUTATION-1.0","repetitions":100000,"eligible_pairs":0,"pair_results":[],"maxima":[0.0]*100000}
    else:
        rounds = list(range(501,1238)); round_index = {r:i for i,r in enumerate(rounds)}
        k = len(grouped); schedules=np.zeros((737,k),dtype=np.int8); occurrences=np.zeros((737,k),dtype=np.int8)
        for column,(a,b,direction,n,hits) in enumerate(grouped):
            exposure_rounds=[r[0] for r in connection.execute("SELECT evaluation_round FROM walkforward_exposure WHERE run_id=? AND pair_a=? AND pair_b=? AND direction=? ORDER BY evaluation_round",(run_id,a,b,direction))]
            schedules[[round_index[r] for r in exposure_rounds],column]=1
            for i,round_no in enumerate(rounds): occurrences[i,column]=int({a,b}<=set(rows[round_no-1].main))
        counts=schedules.sum(axis=0); p0=1/66; denom=np.sqrt(counts*p0*(1-p0)); actual=np.abs((np.array([g[4] for g in grouped])-counts*p0)/denom)
        root_seed=int.from_bytes(hashlib.sha256(f"{run_id}|ROUND_ORDER_PERMUTATION".encode()).digest()[:8],"big")
        rng=np.random.Generator(np.random.PCG64DXSM(root_seed)); maxima=[]; batch=200
        for start in range(0,100000,batch):
            size=min(batch,100000-start); perms=np.array([rng.permutation(737) for _ in range(size)])
            hits=(occurrences[perms,:]*schedules[None,:,:]).sum(axis=1)
            maxima.extend(np.max(np.abs((hits-counts*p0)/denom),axis=1).astype(float).tolist())
        maxima_array=np.array(maxima)
        results=[]
        for i,(a,b,direction,n,hits) in enumerate(grouped): results.append({"pair":[a,b],"direction":direction,"exposure":n,"hits":hits,"adjusted_empirical_p":(1+int(np.sum(maxima_array>=actual[i])))/100001})
        payload={"version":"EXP001-ROUND-PERMUTATION-1.0","prng":"NUMPY-PCG64DXSM-2.3.5","seed_root":root_seed,"repetitions":100000,"eligible_pairs":k,"pair_results":results,"maxima":maxima}
    null_id=sha_bytes(f"{run_id}|MAIN|{null_type}".encode()); connection.execute("INSERT INTO null_statistic VALUES(?,?,?,?,?,?,?,?,?)",(null_id,run_id,"MAIN","WALKFORWARD",null_type,0,100000,json.dumps(payload,separators=(",",":")),sha_bytes(canonical_json(payload).encode())));connection.commit();return payload


def summarize_walkforward(connection: sqlite3.Connection, run_id: str) -> dict[str, Any]:
    rounds = connection.execute("SELECT COUNT(*),SUM(status='COMPLETE_NO_EDGE') FROM walkforward_round WHERE run_id=?", (run_id,)).fetchone()
    exposures = connection.execute("SELECT pair_a,pair_b,direction,COUNT(*),SUM(main_occurrence),SUM(integrated_occurrence) FROM walkforward_exposure WHERE run_id=? GROUP BY pair_a,pair_b,direction", (run_id,)).fetchall()
    eligible = []
    raw = []
    for a,b,direction,n,main_hits,integrated_hits in exposures:
        if n >= 200:
            eligible.append((a,b,direction,n,main_hits,integrated_hits))
            raw.append(binomial_one_sided(main_hits,n,1/66,direction))
    adjusted = holm(np.array(raw)) if raw else np.array([])
    significant = [(*item,float(adjusted[i])) for i,item in enumerate(eligible) if adjusted[i] < 0.05 and ((item[4]/item[3] > 1/66) if item[2]=="POSITIVE" else (item[4]/item[3] < 1/66))]
    return {"evaluation_rounds": int(rounds[0] or 0), "no_edge_rounds": int(rounds[1] or 0), "failed_rounds": 0, "exposure_rows": int(connection.execute("SELECT COUNT(*) FROM walkforward_exposure WHERE run_id=?",(run_id,)).fetchone()[0]), "eligible_pairs_200": len(eligible), "significant_pairs": significant}


def main() -> int:
    snapshot_manifest, protocol, protected_hash = preflight()
    rows = load_source_rows(1237)
    c_hash = code_hash()
    execution_payload = {"experiment_id": EXPERIMENT_ID, "protocol_hash": protocol["canonical_protocol_hash"], "data_snapshot_hash": snapshot_manifest["snapshot_sha256"], "code_hash": c_hash, "python": "CPYTHON-3.11-BUNDLED", "numpy": np.__version__, "iid_prng": "PCG64DXSM", "iid_seed_root": MAXT_SEED, "iid_chunks": 500, "round_permutation_policy": "LOCKED_SELECTION_EXPOSURE_OUTCOME_LABEL_PERMUTATION", "fixed_marginal_prng": "XOSHIRO128STARSTAR-UINT32", "fixed_marginal_samples": 10000, "fixed_marginal_burnin": "10*N*45_ACCEPTED", "fixed_marginal_interval": "N*45_ACCEPTED"}
    execution_hash = sha_bytes(canonical_json(execution_payload).encode())
    if EXECUTION_LOCK.exists():
        old = json.loads(EXECUTION_LOCK.read_text(encoding="utf-8"))
        if old["execution_hash"] != execution_hash: raise RuntimeError("LOCK_MISMATCH_ABORT:EXECUTION_LOCK")
        run_id = old["run_id"]
    else:
        run_id = str(uuid.uuid4())
        EXECUTION_LOCK.write_text(json.dumps({"status":"LOCKED_BEFORE_RESULT","run_id":run_id,"execution_hash":execution_hash,"payload":execution_payload},ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    connection = sqlite3.connect(STORE)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        ensure_run(connection, protocol, snapshot_manifest["snapshot_sha256"], run_id, c_hash)
        connection.execute("INSERT OR REPLACE INTO run_metadata VALUES(?,?,?)",(run_id,"EXECUTION_LOCK",json.dumps({"execution_hash":execution_hash,"payload":execution_payload},ensure_ascii=False,sort_keys=True,separators=(",",":"))))
        connection.execute("INSERT OR REPLACE INTO run_metadata VALUES(?,?,?)",(run_id,"INDEPENDENT_REPRODUCTION",json.dumps({"verified":False,"reason":"SEPARATE_INDEPENDENT_REPRODUCTION_NOT_PART_OF_SINGLE_RUN"},separators=(",",":"))))
        connection.commit()
        matrices = {scope: incidence(rows, scope) for scope in ("MAIN","INTEGRATED")}
        all_metrics = {scope: metrics_for(matrix,scope) for scope,matrix in matrices.items()}
        for scope,matrix in matrices.items():
            for period,metric in all_metrics[scope].items(): store_static(connection,run_id,scope,period,matrix[period_slices(len(matrix))[period]],metric)
        nulls = {}
        for scope in ("MAIN","INTEGRATED"):
            p0 = 1/66 if scope=="MAIN" else 7/330
            nulls[(scope,"iid")] = iid_max_t(scope,len(rows),p0,run_id,connection)
            nulls[(scope,"fixed")] = fixed_marginal(scope,run_id,connection)
        static_pass = []
        main = all_metrics["MAIN"]
        iid = nulls[("MAIN","iid")]
        overall_abs = np.abs(main["OVERALL"]["residual"])
        maxt_p = np.array([(1+int(np.sum(iid>=value)))/(len(iid)+1) for value in overall_abs])
        for index,pair in enumerate(PAIRS):
            same_direction = np.sign(main["OVERALL"]["rd"][index]) != 0 and np.sign(main["FIRST_HALF"]["rd"][index]) == np.sign(main["OVERALL"]["rd"][index]) == np.sign(main["SECOND_HALF"]["rd"][index])
            recent50_opposite = np.sign(main["RECENT_50"]["rd"][index]) == -np.sign(main["OVERALL"]["rd"][index]) and main["RECENT_50"]["adjusted"][index] < .05
            low,high = clopper_pearson_95(int(main["OVERALL"]["counts"][index]),len(rows))
            passed = main["OVERALL"]["adjusted"][index] < .05 and not(low<=1/66<=high) and same_direction and main["FIRST_HALF"]["adjusted"][index] < .05 and main["SECOND_HALF"]["adjusted"][index] < .05 and np.sign(main["RECENT_100"]["rd"][index]) == np.sign(main["OVERALL"]["rd"][index]) and not recent50_opposite and maxt_p[index] < .05
            if passed: static_pass.append(pair)
        for scope in ("MAIN","INTEGRATED"):
            for period,metric in all_metrics[scope].items():
                max_pass = int(np.sum(np.array([(1+int(np.sum(nulls[(scope,'iid')]>=abs(v))))/(MAXT_REPETITIONS+1) for v in metric["residual"]]) < .05)) if period=="OVERALL" else 0
                summary={"test_only":period=="RECENT_20","risk_difference_quantiles":np.quantile(metric["rd"],[0,.05,.25,.5,.75,.95,1]).tolist(),"strongest_positive":[list(PAIRS[i])+[float(metric['rd'][i]),int(metric['counts'][i])] for i in np.argsort(metric['rd'])[-10:][::-1]],"strongest_negative":[list(PAIRS[i])+[float(metric['rd'][i]),int(metric['counts'][i])] for i in np.argsort(metric['rd'])[:10]]}
                connection.execute("INSERT OR REPLACE INTO retrospective_summary VALUES(?,?,?,?,?,?,?,?,?,?)",(run_id,scope,period,int(np.sum(metric['adjusted']<.05)),max_pass,None,int(np.sum(metric['rd']>0)),int(np.sum(metric['rd']<0)),int(np.sum(metric['rd']==0)),json.dumps(summary,separators=(",",":"))))
        connection.commit()
        wf = walkforward(connection,run_id,rows)
        permutation = round_order_permutation(connection,run_id,rows)
        temporal_pass_pairs={tuple(item["pair"]) for item in permutation["pair_results"] if item["adjusted_empirical_p"]<.05}
        reproduced_pairs=[item for item in wf["significant_pairs"] if tuple(item[:2]) in temporal_pass_pairs]
        independently_reproduced = False
        signal_candidate = bool(static_pass and reproduced_pairs)
        supported = signal_candidate and independently_reproduced
        retrospective_result = "STATIC_MAIN_SIGNAL" if static_pass else "NO_STATIC_MAIN_SIGNAL"
        walkforward_result = "REPRODUCED" if reproduced_pairs else "NOT_REPRODUCED"
        if supported: judgment="SUPPORTED"
        elif signal_candidate and not independently_reproduced: judgment="INCONCLUSIVE"
        elif static_pass and wf["eligible_pairs_200"]==0: judgment="INCONCLUSIVE"
        else: judgment="FAILED"
        code = "A" if supported else ("B" if static_pass and wf["eligible_pairs_200"]>0 and not reproduced_pairs else ("C" if static_pass or int(np.sum(main['OVERALL']['adjusted']<.05)) else "D"))
        judgment_payload={"static_pass_pairs":[list(x) for x in static_pass],"walkforward":wf,"round_order_permutation":{"eligible_pairs":permutation["eligible_pairs"],"pair_results":permutation["pair_results"]},"reproduced_pairs":reproduced_pairs,"independent_reproduction_verified":independently_reproduced,"retrospective_result":retrospective_result,"walkforward_result":walkforward_result,"judgment":judgment,"explanation_code":code}
        connection.execute("INSERT OR REPLACE INTO experiment_judgment VALUES(?,?,?,?,?,?,?,?)",(run_id,retrospective_result,walkforward_result,judgment,code,0,0,json.dumps(judgment_payload,separators=(",",":"))))
        connection.execute("UPDATE experiment_run SET execution_status='BACKTESTED',completed_at=datetime('now') WHERE run_id=?",(run_id,));connection.commit()
        report={"state":"EXP001_LOCKED_RUN_COMPLETE","engine":"FROZEN","experiment_id":EXPERIMENT_ID,"run_id":run_id,"run_status":"BACKTESTED","data_hash_verified":True,"protocol_hash_verified":True,"retrospective_complete":True,"walkforward_complete":wf['evaluation_rounds']==737,"main_pairs_tested":990,"holm_pass":int(np.sum(main['OVERALL']['adjusted']<.05)),"maxT_pass":int(np.sum(maxt_p<.05)),"static_main_pass":len(static_pass),"walkforward":wf,"retrospective_result":retrospective_result,"walkforward_result":walkforward_result,"final_experiment_judgment":judgment,"explanation_code":code,"future_leakage":0,"hash_mismatch":0,"failed_rounds":wf['failed_rounds'],"official_recommendation_allowed":False,"promotion_candidate":False,"protected_canonical_hash":protected_hash,"db_integrity":connection.execute('pragma integrity_check').fetchone()[0],"foreign_key_violations":len(connection.execute('pragma foreign_key_check').fetchall())}
        REPORT.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"status":report["state"],"run_id":run_id,"report":str(REPORT),"judgment":judgment,"code":code},ensure_ascii=False))
        return 0
    except Exception as exc:
        connection.rollback()
        print(json.dumps({"status":"EXP001_LOCKED_RUN_FAILED","error":f"{type(exc).__name__}:{exc}"},ensure_ascii=False))
        return 1
    finally:
        connection.close()


if __name__ == "__main__": raise SystemExit(main())

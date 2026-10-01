"""
PAIR DORMANCY / GEOMETRIC MEMORYLESS HAZARD V1 CALCULATOR
Canonical Experiment ID: EXP-DRAW-20261001-001-V1
Candidate ID: IDEA-1243-CROS-003
Protocol SHA256: 7e9b7ddedb71504cc1aaf80ebc1807e47e51243cbedc2e2ac038e8a34281850a
"""

import math
import hashlib
import json
import sqlite3
import csv
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

TOTAL_BALLS = 45
TOTAL_PAIRS = 990 # C(45, 2)
PAIRS_PER_DRAW = 15 # C(6, 2)
P0 = 1.0 / 66.0 # Analytic fair draw pair probability

# Fixed Bins (quantiles of Geom(1/66)):
# 1..12, 13..27, 28..46, 47..72, 73..118, 119+
BINS = [
    (1, 12),
    (13, 27),
    (28, 46),
    (47, 72),
    (73, 118),
    (119, None)
]

BIN_LABELS = [
    "B1 [1..12]",
    "B2 [13..27]",
    "B3 [28..46]",
    "B4 [47..72]",
    "B5 [73..118]",
    "B6 [119+]"
]

def derive_deterministic_seed(protocol_sha: str, canonical_id: str) -> int:
    raw = f"{protocol_sha}{canonical_id}PAIR_DORMANCY_MEMORYLESS_V1".encode("utf-8")
    seed_hex = hashlib.sha256(raw).hexdigest()[:8]
    return int(seed_hex, 16)

def get_pair_mappings() -> Tuple[Dict[Tuple[int, int], int], List[Tuple[int, int]]]:
    pair_to_id = {}
    id_to_pair = []
    idx = 0
    for b1 in range(1, TOTAL_BALLS + 1):
        for b2 in range(b1 + 1, TOTAL_BALLS + 1):
            pair_to_id[(b1, b2)] = idx
            id_to_pair.append((b1, b2))
            idx += 1
    return pair_to_id, id_to_pair

PAIR_TO_ID, ID_TO_PAIR = get_pair_mappings()

def load_draws_from_csv(csv_path: Path, max_round: int = 1243) -> List[Tuple[int, List[int]]]:
    draws = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r = int(row["round"])
            if r <= max_round: # Strict future leakage block
                numbers = [int(row[f"n{i}"]) for i in range(1, 7)]
                draws.append((r, sorted(numbers)))
    draws.sort(key=lambda x: x[0])
    return draws

def load_draws_from_db(db_path: Path, max_round: int = 1243) -> List[Tuple[int, List[int]]]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT draw_round, num1, num2, num3, num4, num5, num6 FROM draw_result WHERE draw_round <= ? ORDER BY draw_round ASC",
        (max_round,)
    )
    rows = cur.fetchall()
    conn.close()
    draws = []
    for row in rows:
        r = int(row[0])
        nums = sorted([int(x) for x in row[1:7]])
        draws.append((r, nums))
    return draws

def draws_to_pair_ids(draws: List[Tuple[int, List[int]]]) -> np.ndarray:
    T = len(draws)
    pair_ids = np.empty((T, PAIRS_PER_DRAW), dtype=np.int32)
    for t_idx, (_, nums) in enumerate(draws):
        p_idx = 0
        for i in range(6):
            for j in range(i + 1, 6):
                pair_ids[t_idx, p_idx] = PAIR_TO_ID[(nums[i], nums[j])]
                p_idx += 1
    return pair_ids

def compute_bin_counts_from_rows_cols(rows: np.ndarray, cols: np.ndarray, T: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Vectorized computation of 6-bin exposures and events across T draws.
    rows: (T*15,) integer draw index for each pair occurrence.
    cols: (T*15,) integer pair index (0..989) for each occurrence.
    """
    key = cols.astype(np.int64) * T + rows
    order = np.argsort(key)
    sorted_cols = cols[order]
    sorted_rows = rows[order]

    # Gaps between consecutive occurrences of identical pairs
    is_same = (sorted_cols[1:] == sorted_cols[:-1])
    gaps = sorted_rows[1:][is_same] - sorted_rows[:-1][is_same]

    # Tails after last occurrence
    is_last = np.empty(len(sorted_cols), dtype=bool)
    is_last[:-1] = (sorted_cols[:-1] != sorted_cols[1:])
    is_last[-1] = True
    last_rows = sorted_rows[is_last]
    tails = (T - 1) - last_rows
    tails = tails[tails > 0]

    # Events in each bin:
    evt_counts, _ = np.histogram(gaps, bins=[1, 13, 28, 47, 73, 119, 10000000])

    # Exposures in each bin:
    exp = np.zeros(6, dtype=np.int64)
    exp[0] = np.sum(np.clip(gaps, 0, 12)) + np.sum(np.clip(tails, 0, 12))
    exp[1] = np.sum(np.clip(gaps - 12, 0, 15)) + np.sum(np.clip(tails - 12, 0, 15))
    exp[2] = np.sum(np.clip(gaps - 27, 0, 19)) + np.sum(np.clip(tails - 27, 0, 19))
    exp[3] = np.sum(np.clip(gaps - 46, 0, 26)) + np.sum(np.clip(tails - 46, 0, 26))
    exp[4] = np.sum(np.clip(gaps - 72, 0, 46)) + np.sum(np.clip(tails - 72, 0, 46))
    exp[5] = np.sum(np.maximum(0, gaps - 118)) + np.sum(np.maximum(0, tails - 118))

    return exp, evt_counts

def compute_t_global(exp: np.ndarray, evt: np.ndarray) -> float:
    """
    Likelihood-ratio deviance between unconstrained 6-bin hazard model
    and pooled single-hazard model.
    """
    total_exp = float(np.sum(exp))
    total_evt = float(np.sum(evt))
    if total_exp == 0 or total_evt == 0:
        return 0.0

    h_bar = total_evt / total_exp
    h_hat = evt.astype(np.float64) / exp.astype(np.float64)

    t_stat = 0.0
    for b in range(len(exp)):
        e_b = float(evt[b])
        n_b = float(exp[b])
        h_b = h_hat[b]
        if e_b > 0 and h_b > 0 and h_bar > 0:
            t_stat += e_b * math.log(h_b / h_bar)
        if (n_b - e_b) > 0 and (1.0 - h_b) > 0 and (1.0 - h_bar) > 0:
            t_stat += (n_b - e_b) * math.log((1.0 - h_b) / (1.0 - h_bar))

    return 2.0 * t_stat

def run_historical_screening(
    pair_ids: np.ndarray,
    protocol_sha: str = "7e9b7ddedb71504cc1aaf80ebc1807e47e51243cbedc2e2ac038e8a34281850a",
    canonical_id: str = "EXP-DRAW-20261001-001-V1",
    B: int = 4999
) -> Dict[str, Any]:
    T = pair_ids.shape[0]
    rows = np.repeat(np.arange(T), PAIRS_PER_DRAW)
    cols = pair_ids.ravel()

    # Observed statistics
    obs_exp, obs_evt = compute_bin_counts_from_rows_cols(rows, cols, T)
    obs_t_global = compute_t_global(obs_exp, obs_evt)

    # Deterministic Seed
    seed_int = derive_deterministic_seed(protocol_sha, canonical_id)
    rng = np.random.default_rng(seed_int)

    # Permutations
    perm_t_values = np.empty(B, dtype=np.float64)
    perm_exceed_count = 0

    perm_inv = np.empty(T, dtype=np.int32)
    t_range = np.arange(T)

    for k in range(B):
        perm = rng.permutation(T)
        perm_inv[perm] = t_range
        new_rows = perm_inv[rows]
        p_exp, p_evt = compute_bin_counts_from_rows_cols(new_rows, cols, T)
        t_perm = compute_t_global(p_exp, p_evt)
        perm_t_values[k] = t_perm
        if t_perm >= obs_t_global:
            perm_exceed_count += 1

    p_perm = (1.0 + float(perm_exceed_count)) / (float(B) + 1.0)

    # Decision rule
    if p_perm <= 0.01:
        verdict = "RETROSPECTIVE_SIGNAL_CANDIDATE"
    elif p_perm <= 0.05:
        verdict = "INCONCLUSIVE_RETROSPECTIVE"
    else:
        verdict = "FAILED_RETROSPECTIVE_SCREEN"

    # Descriptive statistics
    h_bar = float(np.sum(obs_evt)) / float(np.sum(obs_exp))
    hazards = (obs_evt.astype(np.float64) / obs_exp.astype(np.float64)).tolist()
    hazard_ratios = [h / h_bar for h in hazards]
    hazard_ratios_p0 = [h / P0 for h in hazards]

    # Low support bins check (< 30 events)
    low_support_bins = [BIN_LABELS[i] for i, e in enumerate(obs_evt) if e < 30]

    return {
        "candidate_id": "IDEA-1243-CROS-003",
        "experiment_canonical_id": canonical_id,
        "protocol_sha256": protocol_sha,
        "deterministic_seed_int": seed_int,
        "total_rounds": T,
        "total_pairs": TOTAL_PAIRS,
        "total_risk_exposures": int(np.sum(obs_exp)),
        "total_events": int(np.sum(obs_evt)),
        "global_hazard_rate": h_bar,
        "analytic_p0": P0,
        "bin_labels": BIN_LABELS,
        "bin_exposures": obs_exp.tolist(),
        "bin_events": obs_evt.tolist(),
        "bin_hazards": hazards,
        "bin_hazard_ratios_to_global": hazard_ratios,
        "bin_hazard_ratios_to_p0": hazard_ratios_p0,
        "low_support_bins": low_support_bins,
        "T_global_observed": float(obs_t_global),
        "permutation_B": B,
        "permutation_exceed_count": int(perm_exceed_count),
        "permutation_p_value": float(p_perm),
        "permutation_t_min": float(np.min(perm_t_values)),
        "permutation_t_mean": float(np.mean(perm_t_values)),
        "permutation_t_median": float(np.median(perm_t_values)),
        "permutation_t_max": float(np.max(perm_t_values)),
        "permutation_t_p90": float(np.percentile(perm_t_values, 90)),
        "permutation_t_p95": float(np.percentile(perm_t_values, 95)),
        "permutation_t_p99": float(np.percentile(perm_t_values, 99)),
        "verdict": verdict
    }

def run_chronological_stability_blocks(pair_ids: np.ndarray, num_blocks: int = 5) -> List[Dict[str, Any]]:
    T = pair_ids.shape[0]
    block_size = T // num_blocks
    results = []

    for b in range(num_blocks):
        start = b * block_size
        end = (b + 1) * block_size if b < num_blocks - 1 else T
        sub_pair_ids = pair_ids[start:end]
        sub_T = end - start

        sub_rows = np.repeat(np.arange(sub_T), PAIRS_PER_DRAW)
        sub_cols = sub_pair_ids.ravel()
        exp, evt = compute_bin_counts_from_rows_cols(sub_rows, sub_cols, sub_T)
        t_stat = compute_t_global(exp, evt)
        h_bar = float(np.sum(evt)) / float(np.sum(exp)) if np.sum(exp) > 0 else 0.0
        hazards = (evt.astype(np.float64) / exp.astype(np.float64)).tolist()

        results.append({
            "block_index": b + 1,
            "round_start": start + 1,
            "round_end": end,
            "rounds_count": sub_T,
            "total_risk_exposures": int(np.sum(exp)),
            "total_events": int(np.sum(evt)),
            "global_hazard": h_bar,
            "bin_exposures": exp.tolist(),
            "bin_events": evt.tolist(),
            "bin_hazards": hazards,
            "T_global": float(t_stat)
        })

    return results

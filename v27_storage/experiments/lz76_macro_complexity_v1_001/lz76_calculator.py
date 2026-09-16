from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import multiprocessing as mp
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
INPUT = Path(r"E:\P45 프로젝트\v27_storage\experiments\exp020_lagged_winner_count_regime_signal_v1_001\P45_EXP_020_OFFICIAL_FULL_HISTORY_001.csv")
PROTOCOL = ROOT / "01_PROTOCOL_LOCKED.md"
THRESHOLD_SEED = 2026082901
NULL_SEED = 2026082902
N_THRESHOLD = 100_000
N_HISTORIES = 10_000
N_ROUNDS = 1_238
WINDOW_ROUNDS = 100
BITS_PER_ROUND = 45
WINDOW_BITS = WINDOW_ROUNDS * BITS_PER_ROUND
N_WINDOWS = N_ROUNDS - WINDOW_ROUNDS + 1
NORMALIZER = math.log2(WINDOW_BITS) / WINDOW_BITS


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def lz76_reference(data: bytes) -> int:
    """Deliberately slow, direct definition used only for synthetic tests."""
    n = len(data)
    pos = 0
    count = 0
    while pos < n:
        length = 1
        while pos + length <= n:
            candidate = data[pos : pos + length]
            prior = {
                data[start : start + length]
                for start in range(0, pos - length + 1)
            }
            if candidate not in prior:
                break
            length += 1
        count += 1
        pos += min(length, n - pos)
    return count


def lz76_count(data: bytes) -> int:
    """O(n) suffix-automaton implementation of the locked parsing rule."""
    n = len(data)
    capacity = 2 * n + 1
    next0 = [-1] * capacity
    next1 = [-1] * capacity
    link = [-1] * capacity
    length = [0] * capacity
    size = 1
    last = 0

    def extend(ch: int, size_: int, last_: int) -> tuple[int, int]:
        cur = size_
        size_ += 1
        length[cur] = length[last_] + 1
        p = last_
        transitions = next1 if ch else next0
        while p >= 0 and transitions[p] < 0:
            transitions[p] = cur
            p = link[p]
        if p < 0:
            link[cur] = 0
        else:
            q = transitions[p]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                clone = size_
                size_ += 1
                length[clone] = length[p] + 1
                link[clone] = link[q]
                next0[clone] = next0[q]
                next1[clone] = next1[q]
                while p >= 0 and transitions[p] == q:
                    transitions[p] = clone
                    p = link[p]
                link[q] = clone
                link[cur] = clone
        return size_, cur

    pos = 0
    count = 0
    while pos < n:
        state = 0
        end = pos
        while end < n:
            nxt = next1[state] if data[end] else next0[state]
            if nxt < 0:
                break
            state = nxt
            end += 1
        phrase_length = end - pos + 1 if end < n else n - pos
        count += 1
        for idx in range(pos, pos + phrase_length):
            size, last = extend(data[idx], size, last)
        pos += phrase_length
    return count


def synthetic_crosscheck() -> list[dict[str, object]]:
    rng = np.random.Generator(np.random.PCG64(2026082900))
    cases = {
        "repeating": bytes([0] * 256),
        "alternating": bytes(([0, 1] * 128)),
        "fixed_seed_random": rng.integers(0, 2, size=256, dtype=np.uint8).tobytes(),
    }
    results = []
    for name, data in cases.items():
        reference = lz76_reference(data)
        calculator = lz76_count(data)
        results.append(
            {
                "case": name,
                "length": len(data),
                "reference_c": reference,
                "calculator_c": calculator,
                "match": reference == calculator,
            }
        )
    return results


def load_input() -> tuple[np.ndarray, dict[str, object]]:
    rows: list[tuple[int, list[int]]] = []
    with INPUT.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = ["draw", "main1", "main2", "main3", "main4", "main5", "main6"]
        if not reader.fieldnames or any(field not in reader.fieldnames for field in required):
            raise ValueError("required MAIN6 columns missing")
        for row in reader:
            draw = int(row["draw"])
            main = [int(row[f"main{i}"]) for i in range(1, 7)]
            rows.append((draw, main))
    if [draw for draw, _ in rows] != list(range(1, N_ROUNDS + 1)):
        raise ValueError("round continuity failed")
    bits = np.zeros((N_ROUNDS, BITS_PER_ROUND), dtype=np.uint8)
    for idx, (_, main) in enumerate(rows):
        if len(set(main)) != 6 or any(number < 1 or number > 45 for number in main):
            raise ValueError(f"invalid MAIN6 at round {idx + 1}")
        bits[idx, np.asarray(main, dtype=np.int16) - 1] = 1
    if not np.all(bits.sum(axis=1) == 6):
        raise ValueError("45-bit one-count invariant failed")
    info = {
        "path": str(INPUT),
        "size_bytes": INPUT.stat().st_size,
        "sha256": sha256_file(INPUT),
        "row_count": len(rows),
        "round_first": rows[0][0],
        "round_last": rows[-1][0],
        "main6_only": True,
        "bonus_used": False,
        "future_data_used": 0,
    }
    return bits, info


def draws_to_bits(rng: np.random.Generator, draw_count: int) -> np.ndarray:
    # Continuous PCG64 stream; six smallest i.i.d. priorities form a uniform 6/45 subset.
    priorities = rng.random((draw_count, BITS_PER_ROUND))
    selected = np.argpartition(priorities, 6, axis=1)[:, :6]
    bits = np.zeros((draw_count, BITS_PER_ROUND), dtype=np.uint8)
    bits[np.arange(draw_count)[:, None], selected] = 1
    return bits


def _score_byte_strings(strings: list[bytes]) -> np.ndarray:
    return np.asarray([lz76_count(item) for item in strings], dtype=np.int16)


def score_matrix_parallel(matrix: np.ndarray, workers: int, chunk_rows: int = 32) -> np.ndarray:
    chunks = []
    for start in range(0, matrix.shape[0], chunk_rows):
        chunks.append([row.tobytes() for row in matrix[start : start + chunk_rows]])
    if workers == 1:
        arrays = [_score_byte_strings(chunk) for chunk in chunks]
    else:
        context = mp.get_context("spawn")
        with context.Pool(processes=workers) as pool:
            arrays = list(pool.imap(_score_byte_strings, chunks, chunksize=1))
    return np.concatenate(arrays)


def threshold_distribution(workers: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(THRESHOLD_SEED))
    result = np.empty(N_THRESHOLD, dtype=np.int16)
    batch = 1_000
    offset = 0
    while offset < N_THRESHOLD:
        count = min(batch, N_THRESHOLD - offset)
        bits = draws_to_bits(rng, count * WINDOW_ROUNDS).reshape(count, WINDOW_BITS)
        result[offset : offset + count] = score_matrix_parallel(bits, workers)
        offset += count
        print(f"threshold {offset}/{N_THRESHOLD}", flush=True)
    return result


def rolling_windows(bits: np.ndarray) -> np.ndarray:
    windows = np.lib.stride_tricks.sliding_window_view(bits, WINDOW_ROUNDS, axis=0)
    # sliding_window_view shape is (1139, 45, 100); transpose to round-major bit order.
    return windows.transpose(0, 2, 1).reshape(N_WINDOWS, WINDOW_BITS).copy()


def binary_lag1(states: np.ndarray) -> float | None:
    x = states[:-1].astype(np.float64)
    y = states[1:].astype(np.float64)
    sx = x.std(ddof=1)
    sy = y.std(ddof=1)
    if sx == 0.0 or sy == 0.0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def evaluate_history(bits: np.ndarray, q_count: int, workers: int) -> tuple[int, float, float | None]:
    counts = score_matrix_parallel(rolling_windows(bits), workers)
    states = counts <= q_count
    return int(states.sum()), float(states.mean()), binary_lag1(states)


def final_null(q_count: int, workers: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(NULL_SEED))
    occupancies = np.empty(N_HISTORIES, dtype=np.float64)
    autocorrs = np.empty(N_HISTORIES, dtype=np.float64)
    for history in range(N_HISTORIES):
        bits = draws_to_bits(rng, N_ROUNDS)
        _, occupancy, autocorr = evaluate_history(bits, q_count, workers)
        if autocorr is None or not math.isfinite(autocorr):
            raise RuntimeError(f"STOP_NULL_NOT_ESTIMABLE history={history + 1}")
        occupancies[history] = occupancy
        autocorrs[history] = autocorr
        if (history + 1) % 10 == 0:
            print(f"null {history + 1}/{N_HISTORIES}", flush=True)
    return occupancies, autocorrs


def environment_info(workers: int) -> dict[str, object]:
    return {
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "bit_generator": "PCG64",
        "workers": workers,
    }


def preflight(workers: int) -> dict[str, object]:
    synthetic = synthetic_crosscheck()
    if not all(item["match"] for item in synthetic):
        raise RuntimeError("STOP_LZ76_IMPLEMENTATION_MISMATCH")
    bits, input_info = load_input()
    return {
        "status": "PASS",
        "synthetic_crosscheck": synthetic,
        "input": input_info,
        "encoded_shape": list(bits.shape),
        "ones_per_round_all_six": bool(np.all(bits.sum(axis=1) == 6)),
        "window_bits": WINDOW_BITS,
        "window_count": N_WINDOWS,
        "adjacent_state_pairs": N_WINDOWS - 1,
        "environment": environment_info(workers),
    }


def run_once(workers: int) -> dict[str, object]:
    started = time.time()
    checks = preflight(workers)
    threshold_counts = threshold_distribution(workers)
    q_count = int(np.sort(threshold_counts)[19_999])
    q = q_count * NORMALIZER
    null_occupancy, null_autocorr = final_null(q_count, workers)
    actual_bits, _ = load_input()
    actual_count, actual_occupancy, actual_autocorr = evaluate_history(actual_bits, q_count, workers)
    if actual_autocorr is None:
        p1 = (int(np.sum(null_occupancy >= actual_occupancy)) + 1) / 10001
        p2 = None
        verdict = "FAILED_NOT_SUPPORTED"
        joint = False
    else:
        p1 = (int(np.sum(null_occupancy >= actual_occupancy)) + 1) / 10001
        p2 = (int(np.sum(null_autocorr >= actual_autocorr)) + 1) / 10001
        joint = p1 <= 0.025 and p2 <= 0.025
        verdict = "SUPPORTED_WITHIN_EXPERIMENT" if joint else "FAILED_NOT_SUPPORTED"
    return {
        "research_id": "P45_LZ76_MACRO_COMPLEXITY_V1",
        "protocol_sha256": sha256_file(PROTOCOL),
        "input_sha256": checks["input"]["sha256"],
        "data_range": "1..1238 MAIN6 ONLY",
        "future_data_used": 0,
        "lz_windows": N_WINDOWS,
        "threshold": {
            "seed": THRESHOLD_SEED,
            "virtual_windows": N_THRESHOLD,
            "order_statistic_1_based": 20000,
            "q_phrase_count": q_count,
            "q_normalized_lz76": q,
            "phrase_count_mean": float(threshold_counts.mean()),
        },
        "null": {
            "seed": NULL_SEED,
            "histories": N_HISTORIES,
            "occupancy_mean": float(null_occupancy.mean()),
            "lag1_autocorr_mean": float(null_autocorr.mean()),
            "not_estimable": 0,
        },
        "actual": {
            "state_a_count": actual_count,
            "occupancy": actual_occupancy,
            "lag1_autocorrelation": actual_autocorr,
        },
        "p1_occupancy": p1,
        "p2_autocorrelation": p2,
        "joint_criteria_pass": joint,
        "final_verdict": verdict,
        "preflight": checks,
        "elapsed_seconds": time.time() - started,
    }


def canonical_result(result: dict[str, object]) -> bytes:
    copy = dict(result)
    copy.pop("elapsed_seconds", None)
    return json.dumps(copy, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["preflight", "primary", "reproduce"])
    parser.add_argument("--workers", type=int, default=max(1, min(16, os.cpu_count() or 1)))
    args = parser.parse_args()
    if args.phase == "preflight":
        print(json.dumps(preflight(args.workers), ensure_ascii=False, indent=2))
        return
    if args.phase == "primary":
        result = run_once(args.workers)
        path = ROOT / "primary_calculation.json"
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
        return
    expected_path = ROOT / "primary_calculation.json"
    if not expected_path.exists():
        raise FileNotFoundError(expected_path)
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    reproduced = run_once(args.workers)
    match = canonical_result(expected) == canonical_result(reproduced)
    record = {
        "status": "PASS" if match else "REPRODUCIBILITY_FAIL",
        "canonical_numeric_result_match": match,
        "primary_sha256": sha256_file(expected_path),
        "reproduction_result": reproduced,
    }
    (ROOT / "reproduction_calculation.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(record, ensure_ascii=False, indent=2), flush=True)
    if not match:
        raise RuntimeError("REPRODUCIBILITY_FAIL")


if __name__ == "__main__":
    mp.freeze_support()
    main()


from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

import lz76_calculator as base


ROOT = Path(__file__).resolve().parent
DLL = ROOT / "Lz76Scorer.dll"
CS_SOURCE = ROOT / "Lz76Scorer.cs"
PWSH = Path(r"C:\Users\sung2\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe")
WORK = Path(tempfile.gettempdir()) / "p45_lz76_macro_complexity_v1_locked_run"
PRIMARY_TEMP = Path(tempfile.gettempdir()) / "p45_lz76_primary_calculation.json"
REPRO_TEMP = Path(tempfile.gettempdir()) / "p45_lz76_reproduction_calculation.json"


def write_uniform_draw_bits(path: Path, rng: np.random.Generator, draws: int, batch_draws: int) -> None:
    with path.open("wb") as f:
        remaining = draws
        while remaining:
            count = min(batch_draws, remaining)
            bits = base.draws_to_bits(rng, count)
            f.write(bits.tobytes(order="C"))
            remaining -= count


def run_scorer(mode: str, input_path: Path, output_path: Path, rows: int, workers: int, q_count: int | None = None) -> dict:
    args = [f"mode={mode}", f"input={input_path}", f"output={output_path}", f"rows={rows}", f"workers={workers}"]
    if q_count is not None:
        args.append(f"qCount={q_count}")
    quoted = ",".join("'" + item.replace("'", "''") + "'" for item in args)
    command = f"Add-Type -Path '{str(DLL).replace("'", "''")}'; [Lz76Scorer]::Main(@({quoted})) | Out-Null"
    subprocess.run([str(PWSH), "-NoLogo", "-NoProfile", "-Command", command], check=True)
    return json.loads(output_path.read_text(encoding="utf-8"))


def crosscheck_csharp(workers: int) -> list[dict[str, object]]:
    rng = np.random.Generator(np.random.PCG64(2026082900))
    cases = [
        ("repeating_4500", np.zeros(base.WINDOW_BITS, dtype=np.uint8)),
        ("alternating_4500", np.arange(base.WINDOW_BITS, dtype=np.uint8) % 2),
        ("fixed_seed_random_4500", rng.integers(0, 2, size=base.WINDOW_BITS, dtype=np.uint8)),
    ]
    raw = WORK / "crosscheck.bin"
    out = WORK / "crosscheck.json"
    with raw.open("wb") as f:
        for _, bits in cases:
            f.write(bits.tobytes())
    scored = run_scorer("threshold", raw, out, len(cases), workers)
    results = []
    for (name, bits), csharp_count in zip(cases, scored["counts"]):
        python_count = base.lz76_count(bits.tobytes())
        results.append(
            {
                "case": name,
                "python_suffix_automaton_c": python_count,
                "csharp_suffix_automaton_c": csharp_count,
                "match": python_count == csharp_count,
            }
        )
    if not all(item["match"] for item in results):
        raise RuntimeError("STOP_LZ76_IMPLEMENTATION_MISMATCH")
    return results


def canonical(result: dict) -> bytes:
    copy = dict(result)
    copy.pop("elapsed_seconds", None)
    return json.dumps(copy, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def execute(workers: int) -> dict:
    started = time.time()
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()
    try:
        preflight = base.preflight(workers)
        csharp_crosscheck = crosscheck_csharp(workers)
        print("crosscheck PASS", flush=True)

        threshold_raw = WORK / "threshold.bin"
        threshold_out = WORK / "threshold.json"
        threshold_rng = np.random.Generator(np.random.PCG64(base.THRESHOLD_SEED))
        write_uniform_draw_bits(
            threshold_raw,
            threshold_rng,
            base.N_THRESHOLD * base.WINDOW_ROUNDS,
            100_000,
        )
        print("threshold generation PASS", flush=True)
        threshold = run_scorer("threshold", threshold_raw, threshold_out, base.N_THRESHOLD, workers)
        threshold_counts = np.asarray(threshold["counts"], dtype=np.int16)
        q_count = int(np.sort(threshold_counts)[19_999])
        q = q_count * base.NORMALIZER
        print(f"threshold scoring PASS q_count={q_count} q={q:.17g}", flush=True)

        null_raw = WORK / "null_histories.bin"
        null_out = WORK / "null_histories.json"
        null_rng = np.random.Generator(np.random.PCG64(base.NULL_SEED))
        write_uniform_draw_bits(null_raw, null_rng, base.N_HISTORIES * base.N_ROUNDS, 61_900)
        print("null generation PASS", flush=True)
        null = run_scorer("histories", null_raw, null_out, base.N_HISTORIES, workers, q_count)
        estimable = np.asarray(null["estimable"], dtype=np.uint8)
        if not np.all(estimable == 1):
            bad = np.flatnonzero(estimable != 1)
            raise RuntimeError(f"STOP_NULL_NOT_ESTIMABLE histories={(bad + 1).tolist()}")
        null_occupancy = np.asarray(null["occupancy"], dtype=np.float64)
        null_autocorr = np.asarray(null["autocorr"], dtype=np.float64)
        print("null scoring PASS", flush=True)

        actual_bits, input_info = base.load_input()
        actual_raw = WORK / "actual.bin"
        actual_out = WORK / "actual.json"
        actual_raw.write_bytes(actual_bits.tobytes(order="C"))
        actual = run_scorer("histories", actual_raw, actual_out, 1, workers, q_count)
        actual_count = int(actual["stateCounts"][0])
        actual_occupancy = float(actual["occupancy"][0])
        actual_autocorr = float(actual["autocorr"][0]) if actual["estimable"][0] == 1 else None
        p1 = (int(np.sum(null_occupancy >= actual_occupancy)) + 1) / 10001
        if actual_autocorr is None:
            p2 = None
            joint = False
        else:
            p2 = (int(np.sum(null_autocorr >= actual_autocorr)) + 1) / 10001
            joint = p1 <= 0.025 and p2 <= 0.025
        verdict = "SUPPORTED_WITHIN_EXPERIMENT" if joint else "FAILED_NOT_SUPPORTED"
        print("actual scoring PASS", flush=True)

        return {
            "research_id": "P45_LZ76_MACRO_COMPLEXITY_V1",
            "protocol_sha256": base.sha256_file(base.PROTOCOL),
            "input_sha256": input_info["sha256"],
            "data_range": "1..1238 MAIN6 ONLY",
            "future_data_used": 0,
            "lz_windows": base.N_WINDOWS,
            "threshold": {
                "seed": base.THRESHOLD_SEED,
                "virtual_windows": base.N_THRESHOLD,
                "order_statistic_1_based": 20000,
                "q_phrase_count": q_count,
                "q_normalized_lz76": q,
                "phrase_count_mean": float(threshold_counts.mean()),
            },
            "null": {
                "seed": base.NULL_SEED,
                "histories": base.N_HISTORIES,
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
            "preflight": preflight,
            "csharp_crosscheck": csharp_crosscheck,
            "calculator": {
                "python_orchestrator_sha256": base.sha256_file(Path(__file__)),
                "python_reference_sha256": base.sha256_file(ROOT / "lz76_calculator.py"),
                "csharp_source_sha256": base.sha256_file(CS_SOURCE),
                "csharp_assembly_sha256": base.sha256_file(DLL),
                "workers": workers,
            },
            "elapsed_seconds": time.time() - started,
        }
    finally:
        if WORK.exists():
            shutil.rmtree(WORK)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["primary", "reproduce"])
    parser.add_argument("--workers", type=int, default=max(1, min(16, os.cpu_count() or 1)))
    args = parser.parse_args()
    result = execute(args.workers)
    if args.phase == "primary":
        output = PRIMARY_TEMP
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
        return
    primary_path = ROOT / "primary_calculation.json"
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    match = canonical(primary) == canonical(result)
    record = {
        "status": "PASS" if match else "REPRODUCIBILITY_FAIL",
        "canonical_numeric_result_match": match,
        "primary_sha256": base.sha256_file(primary_path),
        "reproduction_result": result,
    }
    REPRO_TEMP.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(record, ensure_ascii=False, indent=2), flush=True)
    if not match:
        raise RuntimeError("REPRODUCIBILITY_FAIL")


if __name__ == "__main__":
    main()

from __future__ import annotations

import concurrent.futures
import gzip
import pickle
from pathlib import Path

from p45_v27.pairs.production import ProductionPairPipeline
from p45_v27.stage6_diagnostics import diagnose_stage6
from p45_v27.trio_engine import build_current_trios
from p45_v27.units import DEFINITIONS

ROOT = Path(__file__).resolve().parents[3]
AUDIT = Path(__file__).resolve().parent
DATA = ROOT / "analysis/structure-1236/analysis-input.csv"
TRIO = AUDIT / "sandbox_trio_pair_adapter.sqlite3"
CACHE = AUDIT / "pair_input_cache"


def worker(bounds: tuple[int, int]) -> tuple[int, int, int]:
    start, end = bounds
    pipeline = ProductionPairPipeline(DATA, TRIO)
    count = 0
    for round_ in range(start, end + 1):
        path = CACHE / f"{round_}.pickle.gz"
        if path.exists():
            count += 1
            continue
        stage6 = diagnose_stage6(DATA, round_)
        trios = (build_current_trios(stage6, DEFINITIONS, pipeline._trio_history(round_))
                 if len(stage6["candidate_numbers"]) >= 6 else None)
        with gzip.open(path, "wb", compresslevel=1) as handle:
            pickle.dump((stage6, trios), handle, protocol=pickle.HIGHEST_PROTOCOL)
        count += 1
    return start, end, count


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    ranges = [(716, 780), (781, 845), (846, 910), (911, 975),
              (976, 1040), (1041, 1105), (1106, 1170), (1171, 1235)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as pool:
        print(list(pool.map(worker, ranges)))


if __name__ == "__main__":
    main()

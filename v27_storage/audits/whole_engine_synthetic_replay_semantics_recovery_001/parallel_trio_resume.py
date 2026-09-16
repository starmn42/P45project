from __future__ import annotations

import concurrent.futures
import sqlite3
import uuid
from pathlib import Path

from p45_v27.trio_walkforward import run

ROOT = Path(__file__).resolve().parents[3]
AUDIT = Path(__file__).resolve().parent
SANDBOX_ROOT = AUDIT / "sandbox_root"
DATA = ROOT / "analysis/structure-1236/analysis-input.csv"
TARGET = AUDIT / "sandbox_trio.sqlite3"


def worker(bounds: tuple[int, int]) -> tuple[int, int, dict]:
    start, end = bounds
    db = AUDIT / f"trio_chunk_{start}_{end}.sqlite3"
    result = run(project_root=SANDBOX_ROOT, db_path=db, data_path=DATA,
                 start_round=start, end_round=end, resume=True, max_seconds=7200)
    return start, end, result


def merge_chunk(target: sqlite3.Connection, start: int, end: int) -> None:
    path = AUDIT / f"trio_chunk_{start}_{end}.sqlite3"
    source = sqlite3.connect(path)
    source.row_factory = sqlite3.Row
    target_run = target.execute("SELECT run_id FROM wf_run WHERE start_round=43 AND end_round=1235 ORDER BY created_at DESC LIMIT 1").fetchone()[0]
    source_run = source.execute("SELECT run_id FROM wf_run LIMIT 1").fetchone()[0]
    for row in source.execute("SELECT * FROM wf_round WHERE run_id=? ORDER BY evaluation_round", (source_run,)):
        values = dict(row)
        if target.execute("SELECT 1 FROM wf_round WHERE run_id=? AND evaluation_round=?", (target_run, values["evaluation_round"])).fetchone():
            continue
        values["checkpoint_id"] = str(uuid.uuid4())
        values["run_id"] = target_run
        columns = list(values)
        target.execute(f"INSERT INTO wf_round ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})", tuple(values[c] for c in columns))
    for row in source.execute("SELECT * FROM wf_exposure WHERE run_id=? ORDER BY evaluation_round,trio_rule_signature", (source_run,)):
        values = dict(row)
        if target.execute("SELECT 1 FROM wf_round WHERE run_id=? AND evaluation_round=?", (target_run, values["evaluation_round"])).fetchone() is None:
            raise RuntimeError(("missing target round", values["evaluation_round"]))
        if target.execute("SELECT 1 FROM wf_exposure WHERE run_id=? AND evaluation_round=? AND trio_rule_signature=?", (target_run, values["evaluation_round"], values["trio_rule_signature"])).fetchone():
            continue
        values["exposure_id"] = str(uuid.uuid4())
        values["run_id"] = target_run
        columns = list(values)
        target.execute(f"INSERT INTO wf_exposure ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})", tuple(values[c] for c in columns))
    source.close()


def main() -> None:
    ranges = [(707, 773), (774, 840), (841, 907), (908, 974),
              (975, 1040), (1041, 1106), (1107, 1171), (1172, 1235)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(worker, ranges))
    if not all(item[2]["run_status"] == "WALKFORWARD_COMPLETE" for item in results):
        raise RuntimeError(results)
    target = sqlite3.connect(TARGET)
    try:
        target.execute("PRAGMA foreign_keys=ON")
        for start, end, _ in results:
            merge_chunk(target, start, end)
        target_run = target.execute("SELECT run_id FROM wf_run WHERE start_round=43 AND end_round=1235 ORDER BY created_at DESC LIMIT 1").fetchone()[0]
        count, low, high = target.execute("SELECT count(*),min(evaluation_round),max(evaluation_round) FROM wf_round WHERE run_id=?", (target_run,)).fetchone()
        if (count, low, high) != (1193, 43, 1235):
            raise RuntimeError((count, low, high))
        target.execute("UPDATE wf_run SET run_status='WALKFORWARD_COMPLETE',completed_at=datetime('now') WHERE run_id=?", (target_run,))
        target.commit()
    finally:
        target.close()
    print(results)


if __name__ == "__main__":
    main()

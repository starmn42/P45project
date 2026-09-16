import hashlib
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path

from p45_v27.draw_update import LIVE_DATA, LIVE_DB, run_update


def draw_digest(path: Path) -> str:
    db = sqlite3.connect(path)
    rows = db.execute("SELECT draw_round,draw_date,main_json,bonus,source_url,source_payload_sha256 FROM draw_result ORDER BY draw_round").fetchall()
    db.close()
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    db_path = root / "live.sqlite3"
    csv_path = root / "live.csv"
    shutil.copy2(LIVE_DB, db_path)
    shutil.copy2(LIVE_DATA, csv_path)
    csv_before = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    db_before = hashlib.sha256(db_path.read_bytes()).hexdigest()
    draw_before = draw_digest(db_path)
    result = run_update(db_path=db_path, live_data_path=csv_path)
    csv_after = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    db_after = hashlib.sha256(db_path.read_bytes()).hexdigest()
    draw_after = draw_digest(db_path)
    db = sqlite3.connect(db_path)
    integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_keys = db.execute("PRAGMA foreign_key_check").fetchall()
    draw_count = db.execute("SELECT COUNT(*) FROM draw_result").fetchone()[0]
    duplicate_count = db.execute("SELECT COUNT(*)-COUNT(DISTINCT draw_round) FROM draw_result").fetchone()[0]
    snapshot_1240 = db.execute("SELECT COUNT(*) FROM analysis_snapshot WHERE analysis_round=1240").fetchone()[0]
    db.close()
    report = {
        "result": result,
        "csv_unchanged": csv_before == csv_after,
        "sqlite_file_unchanged": db_before == db_after,
        "draw_result_unchanged": draw_before == draw_after,
        "draw_rows": draw_count,
        "duplicate_rows": duplicate_count,
        "snapshot_1240_preserved": snapshot_1240 == 1,
        "integrity": integrity,
        "foreign_key_violations": len(foreign_keys),
    }
    if result["status"] not in ("DRAW_ALREADY_CURRENT", "NO_NEW_DRAW") or not all((report["csv_unchanged"], report["sqlite_file_unchanged"], report["draw_result_unchanged"], report["snapshot_1240_preserved"])) or integrity != "ok" or foreign_keys:
        raise RuntimeError("NO_NEW_DRAW_REGRESSION_FAILED")
    output = Path(__file__).resolve().parent / "NO_NEW_DRAW_LIVE_CLONE_TEST.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

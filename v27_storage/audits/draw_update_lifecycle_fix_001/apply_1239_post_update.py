import json
import sqlite3
import uuid
from pathlib import Path

from p45_v27.draw_update import LIVE_DB, UPDATE_VERSION, _canonical, _now, _sha

source = Path(__file__).resolve().parent / "POST_UPDATE_1239_SNAPSHOT_REPRODUCTION.json"
payload = json.loads(source.read_text(encoding="utf-8"))
draw = payload["draw"]
evaluations = payload["evaluations"]
snapshot = payload["snapshot"]

db = sqlite3.connect(LIVE_DB)
try:
    draw_before = db.execute(
        "SELECT draw_date,main_json,bonus,source_url,source_payload_sha256 FROM draw_result WHERE draw_round=1239"
    ).fetchone()
    if draw_before is None:
        raise RuntimeError("POST_UPDATE_DRAW_1239_MISSING")
    if db.execute("SELECT 1 FROM analysis_snapshot WHERE analysis_round=1240").fetchone():
        raise RuntimeError("POST_UPDATE_SNAPSHOT_1240_ALREADY_EXISTS")
    db.execute("BEGIN IMMEDIATE")
    for item in evaluations:
        db.execute(
            "INSERT INTO prediction_evaluation VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (_sha([1239,item["scope"],item["key"]]),1239,item["scope"],item["key"],
             _canonical(item["a"]),_canonical(item["b"]),item["ia"],item["ib"],item["ma"],item["mb"],
             item["ip"],item["is"],item["mp"],item["ms"],_now()),
        )
    db.execute(
        "INSERT INTO analysis_snapshot VALUES(?,?,?,?,?,?,?,?,?,?)",
        (snapshot["analysis_round"],snapshot["source_end_round"],snapshot["status"],snapshot["valid_for_core"],
         _canonical(snapshot["official_selection"]),_canonical(snapshot["diagnostic_top3"]),
         _canonical(snapshot["pair_state_counts"]),snapshot["prediction_hash"],_now(),UPDATE_VERSION),
    )
    run_id = str(uuid.uuid4())
    now = _now()
    db.execute(
        "INSERT INTO update_run VALUES(?,?,?,?,?,?,?,?)",
        (run_id,now,now,1239,1239,"P45_POST_UPDATE_RECOVERY_READY",None,
         _sha({"draw_round":1239,"snapshot":snapshot,"recovery":"a_integrated_hits_compat"})),
    )
    db.commit()
    draw_after = db.execute(
        "SELECT draw_date,main_json,bonus,source_url,source_payload_sha256 FROM draw_result WHERE draw_round=1239"
    ).fetchone()
    if draw_after != draw_before:
        raise RuntimeError("POST_UPDATE_DRAW_1239_CHANGED")
    print(json.dumps({
        "status":"P45_POST_UPDATE_RECOVERY_READY",
        "prediction_evaluations_inserted":len(evaluations),
        "analysis_round":snapshot["analysis_round"],
        "source_end_round":snapshot["source_end_round"],
        "prediction_hash":snapshot["prediction_hash"],
        "draw_1239_unchanged":True,
        "run_id":run_id,
    }, indent=2))
except Exception:
    db.rollback()
    raise
finally:
    db.close()

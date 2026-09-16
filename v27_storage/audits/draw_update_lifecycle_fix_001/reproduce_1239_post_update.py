import json
import sqlite3
from pathlib import Path

from p45_v27.draw_update import Draw, LIVE_DATA, LIVE_DB, _previous_predictions, build_next_snapshot

out = Path(__file__).resolve().parent / "POST_UPDATE_1239_SNAPSHOT_REPRODUCTION.json"
db = sqlite3.connect(f"file:{LIVE_DB.resolve()}?mode=ro", uri=True)
db.row_factory = sqlite3.Row
row = db.execute("SELECT * FROM draw_result WHERE draw_round=1239").fetchone()
db.close()
draw = Draw(1239, row["draw_date"], tuple(json.loads(row["main_json"])), row["bonus"], row["source_url"], row["source_payload_sha256"])
print("DRAW_LOADED", flush=True)
evaluations = _previous_predictions(draw)
print(f"EVALUATIONS={len(evaluations)}", flush=True)
snapshot = build_next_snapshot(draw, LIVE_DATA, evaluations)
print("SNAPSHOT_BUILT", flush=True)
payload = {"draw": draw.__dict__, "evaluations": evaluations, "snapshot": snapshot}
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=list) + "\n", encoding="utf-8")
print(json.dumps({
    "evaluations": len(evaluations),
    "analysis_round": snapshot["analysis_round"],
    "source_end_round": snapshot["source_end_round"],
    "status": snapshot["status"],
    "valid_for_core": snapshot["valid_for_core"],
    "prediction_hash": snapshot["prediction_hash"],
}, indent=2), flush=True)

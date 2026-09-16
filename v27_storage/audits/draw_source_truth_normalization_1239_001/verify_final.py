import csv
import json
import pathlib
import re
import sqlite3

from p45_v27.draw_update import _evaluation, parse_official, validate_draw

root = pathlib.Path(__file__).resolve().parents[3]
raw = (pathlib.Path(__file__).parent / "ROUND_1239_OFFICIAL_RAW.json").read_bytes()
draw = parse_official(raw, 1239)
validate_draw(draw, 1238)
assert draw.main == (11, 13, 22, 32, 33, 36) and draw.bonus == 8
evaluation = _evaluation("TRIO", "fixed_b", (11, 13, 27), (), draw)
assert (evaluation["mp"], evaluation["ms"]) == (0, 1)

db_path = root / "v27_storage/live/p45_new_draw_update_v1.sqlite3"
db = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
assert db.execute("PRAGMA foreign_key_check").fetchall() == []
assert db.execute("SELECT COUNT(*),MIN(draw_round),MAX(draw_round) FROM draw_result").fetchone() == (1239, 1, 1239)
db.close()

log_path = root / "v27_storage/prospective/trio_orbit_v1_001/P45_TRIO_ORBIT_PROSPECTIVE_LOG_001.csv"
with log_path.open(encoding="utf-8-sig", newline="") as handle:
    log = list(csv.reader(handle))
assert all(len(row) == len(log[0]) for row in log)

registry = (root / "00_P45_STATE/experiment_lab/06_INITIAL_EXPERIMENT_REGISTRY.md").read_text(encoding="utf-8")
registry_count = sum(
    1 for line in registry.splitlines()
    if re.match(r"^\|EXP-(?:DRAW|CROWD|PRIZE|CROSS)-\d{8}-\d{3}-V\d\|", line)
)
assert registry_count == 68

inventory_path = root / "90_RESEARCH/P45_RESEARCH_EVIDENCE_INVENTORY_002.csv"
with inventory_path.open(encoding="utf-8-sig", newline="") as handle:
    inventory = list(csv.DictReader(handle))
lz_rows = [row for row in inventory if "lz76_macro_complexity_v1_001" in row["path"]]
assert len(lz_rows) == 16

print(json.dumps({
    "direct_updater_checks": "PASS",
    "sqlite_integrity": "PASS",
    "foreign_keys": "PASS",
    "prospective_log_rows": len(log) - 1,
    "prospective_log_columns": len(log[0]),
    "registry_count": registry_count,
    "inventory_rows": len(inventory),
    "lz76_inventory_rows": len(lz_rows),
}, indent=2))

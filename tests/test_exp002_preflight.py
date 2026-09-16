from pathlib import Path
import sqlite3

from p45_experiments.exp002.fallback import source_pool, select_disjoint_trios
from p45_experiments.exp002.storage import create_empty

def _row(number, state="NUMBER_HOLD", risk="LOW", structure="NORMAL"):
    return {"number":number,"number_state":state,"unit_state_vector":["UNIT_TEST"]*5,
      "number_opposite_risk":risk,"number_structure_state":structure,
      "primary_number_context":None,"relation_state":"UNIT_NO_SUPPORT","pareto_state":"UNIT_PARETO_NONDOMINATED",
      "overlap_profile":(0,0,0),"number_context_conflict":"NONE"}

def test_storage_empty_and_integrity(tmp_path: Path):
    path=tmp_path/"exp002.sqlite3";create_empty(path);db=sqlite3.connect(path)
    assert db.execute("pragma integrity_check").fetchone()[0]=="ok"
    assert db.execute("pragma foreign_key_check").fetchall()==[]
    assert db.execute("select count(*) from experiment_run").fetchone()[0]==0
    assert db.execute("select count(*) from prediction_lock").fetchone()[0]==0
    assert db.execute("select count(*) from experiment_outcome").fetchone()[0]==0
    db.close()

def test_source_pool_deterministic_and_excludes_risk():
    rows={n:_row(n) for n in range(1,14)};rows[13]=_row(13,risk="HIGH")
    assert [x["number"] for x in source_pool(rows)]==list(range(1,13))
    assert [x["number"] for x in source_pool(dict(reversed(list(rows.items()))))]==list(range(1,13))

def test_disjoint_selection_and_no_forced_output():
    rows=[{"trio":(1,2,3)},{"trio":(1,4,5)},{"trio":(4,5,6)}]
    assert select_disjoint_trios(rows)["trio_b"]==[4,5,6]
    assert select_disjoint_trios(rows[:2]) is None

def test_selection_determinism_ten_times():
    rows=[{"trio":(1,2,3)},{"trio":(4,5,6)}]
    assert len({select_disjoint_trios(rows)["selection_hash"] for _ in range(10)})==1

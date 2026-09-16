import csv
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from p45_v27.draw_update import (
    Draw,
    _connect,
    _normalize_lifecycle_outcome,
    assert_draw_sources_synchronized,
    run_update,
)


class LifecycleCompatibilityTests(unittest.TestCase):
    def test_current_canonical_shape(self):
        row = {"a_integrated_hits": 2, "b_integrated_hits": 1, "a_main_hits": 2,
               "b_main_hits": 1, "representative_conflict": False}
        self.assertEqual(_normalize_lifecycle_outcome(row), row)

    def test_compact_updater_shape(self):
        row = {"ia": 2, "ib": 1, "ma": 2, "mb": 1, "representative_conflict": False}
        out = _normalize_lifecycle_outcome(row)
        self.assertEqual((out["a_integrated_hits"], out["b_integrated_hits"],
                          out["a_main_hits"], out["b_main_hits"]), (2, 1, 2, 1))

    def test_repair_storage_shape_derives_locked_conflict(self):
        rank = [None] * 9
        rank[8] = [0, 2]
        row = {"a_integrated_hits": 0, "b_integrated_hits": 0, "a_main_hits": 0,
               "b_main_hits": 0, "rank_key_json": json.dumps(rank)}
        self.assertTrue(_normalize_lifecycle_outcome(row)["representative_conflict"])

    def test_damaged_shape_fails_loudly(self):
        with self.assertRaisesRegex(RuntimeError, "PAIR_LIFECYCLE_OUTCOME_SCHEMA_INVALID"):
            _normalize_lifecycle_outcome({"ia": 1, "ib": 0, "ma": 1,
                                          "representative_conflict": False})

    def test_source_mismatch_stops_before_fetch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); db_path = root / "live.sqlite3"; csv_path = root / "live.csv"
            db = _connect(db_path)
            db.execute("INSERT INTO draw_result VALUES(?,?,?,?,?,?,?)",
                       (1, "2002-12-07", "[10,23,29,33,37,40]", 16, "u", "h", "t"))
            db.commit(); db.close()
            with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle); writer.writerow(["round","date","n1","n2","n3","n4","n5","n6","bonus"])
                writer.writerow([1,"2002-12-07",10,23,29,33,37,41,16])
            called = False
            def fetcher(_):
                nonlocal called; called = True
                raise LookupError("NO_NEW_DRAW")
            with self.assertRaisesRegex(RuntimeError, "STOP_DRAW_SOURCE_OUT_OF_SYNC"):
                run_update(fetcher=fetcher, db_path=db_path, live_data_path=csv_path)
            self.assertFalse(called)

    def test_no_new_draw_preserves_draw_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); db_path = root / "live.sqlite3"; csv_path = root / "live.csv"
            db = _connect(db_path)
            db.execute("INSERT INTO draw_result VALUES(?,?,?,?,?,?,?)",
                       (1, "2002-12-07", "[10,23,29,33,37,40]", 16, "u", "h", "t"))
            db.commit(); db.close()
            with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle); writer.writerow(["round","date","n1","n2","n3","n4","n5","n6","bonus"])
                writer.writerow([1,"2002-12-07",10,23,29,33,37,40,16])
            result = run_update(fetcher=lambda _: (_ for _ in ()).throw(LookupError("NO_NEW_DRAW")),
                                db_path=db_path, live_data_path=csv_path)
            self.assertEqual(result["status"], "NO_NEW_DRAW")
            db = sqlite3.connect(db_path)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM draw_result").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM update_run").fetchone()[0], 0)
            db.close()


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from p45_v27.pairs import PairSignatureContext, PairStore, TrioInput, base_pair_rule_signature
from p45_v27.pairs.engine import SIGNATURE_VERSION


def _trio(name: str, numbers: tuple[int, int, int], marker: str) -> TrioInput:
    return TrioInput(name, numbers, "TRIO_TEST", marker * 64)


def _context(*, member_risk: str = "MEDIUM", member_structure: str = "CAUTION") -> PairSignatureContext:
    return PairSignatureContext("EXPANDED_TEST_POOL", ("A", "B", "C", "D", "E"),
                                (1, 2, 1, 2, 1), (0, 1, 0, 1, 0), member_risk, member_structure)


class PairSignatureV12Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.a = _trio("A", (1, 2, 3), "a"); self.b = _trio("B", (4, 5, 6), "b")

    def test_official_version_and_exact_payload_fields(self) -> None:
        _, payload = base_pair_rule_signature(self.a, self.b, _context())
        self.assertEqual("PAIR-RULE-SIGNATURE-1.2", SIGNATURE_VERSION)
        self.assertEqual(12, len(payload))
        self.assertIn("ranking_policy_hash", payload); self.assertIn("gate_state_policy_hash", payload)

    def test_v10_historical_and_outcome_fields_are_absent(self) -> None:
        _, payload = base_pair_rule_signature(self.a, self.b, _context())
        forbidden = {"pair_opposite_risk", "structure_context", "recent_support_state",
                     "bonus_dependence_state", "pair_historical_risk", "pair_recent",
                     "pair_structure", "pair_bonus_historical_metric", "outcome", "performance", "future"}
        self.assertTrue(forbidden.isdisjoint(payload))

    def test_post_signature_metrics_cannot_change_base_signature(self) -> None:
        baseline = base_pair_rule_signature(self.a, self.b, _context())[0]
        post_metrics = [
            {"risk": "LOW", "recent": "STABLE", "structure": "NORMAL", "bonus": "NONE", "outcome": 0},
            {"risk": "HIGH", "recent": "SEVERE", "structure": "SEVERE", "bonus": "HIGH", "outcome": 999},
        ]
        values = [base_pair_rule_signature(self.a, self.b, _context())[0] for _ in post_metrics]
        self.assertEqual([baseline, baseline], values)

    def test_number_identity_is_excluded(self) -> None:
        x = _trio("X", (10, 11, 12), "a"); y = _trio("Y", (20, 21, 22), "b")
        self.assertEqual(base_pair_rule_signature(self.a, self.b, _context())[0],
                         base_pair_rule_signature(x, y, _context())[0])

    def test_member_structural_context_does_not_change_signature(self) -> None:
        base = base_pair_rule_signature(self.a, self.b, _context())[0]
        self.assertEqual(base, base_pair_rule_signature(self.a, self.b, _context(member_risk="HIGH"))[0])
        self.assertEqual(base, base_pair_rule_signature(self.a, self.b, _context(member_structure="WARNING"))[0])

    def test_member_order_is_invariant(self) -> None:
        self.assertEqual(base_pair_rule_signature(self.a, self.b, _context())[0],
                         base_pair_rule_signature(self.b, self.a, _context())[0])

    def test_same_input_ten_times(self) -> None:
        values = [base_pair_rule_signature(self.a, self.b, _context())[0] for _ in range(10)]
        self.assertEqual(1, len(set(values)))


class PairOutcomePatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(); self.path = Path(self.temp.name) / "schema274.sqlite3"
        self.store = PairStore(self.path); self.store.initialize()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _parent(self) -> None:
        with self.store.transaction() as db:
            db.execute("INSERT INTO pair_walkforward_run VALUES (?,?,?,?,?,?,?)", ("WF", "c"*64, 1, 1, "RUNNING", "now", None))
            db.execute("INSERT INTO pair_walkforward_round VALUES (?,?,?,?,?,?,?)", ("WF", 1, "COMPLETE", "d"*64, "e"*64, 1, None,))

    def test_columns_exist_and_are_not_null_boolean(self) -> None:
        db = self.store.connect()
        try:
            cols = {r[1]: r for r in db.execute("PRAGMA table_info(pair_walkforward_outcome)")}
            for name in ("a_bonus_assisted_triple", "b_bonus_assisted_triple"):
                self.assertIn(name, cols); self.assertEqual("INTEGER", cols[name][2]); self.assertEqual(1, cols[name][3])
            sql = db.execute("SELECT sql FROM sqlite_master WHERE name='pair_walkforward_outcome'").fetchone()[0]
            self.assertIn("a_bonus_assisted_triple IN (0,1)", sql); self.assertIn("b_bonus_assisted_triple IN (0,1)", sql)
        finally: db.close()

    def _full_parent(self) -> None:
        with self.store.transaction() as db:
            db.execute("INSERT INTO pair_run VALUES (?,?,?,?,?,?)", ("PR", "SYNTHETIC_TEST", "a"*64, "b"*64, "CANDIDATE_ONLY", "now"))
            db.execute("INSERT INTO pair_rule_signature VALUES (?,?,?,?,?,?)", ("SIG", "PR", "V", "{}", "c"*64, "now"))
            for tid,key,nums in (("A","1-2-3",(1,2,3)),("B","4-5-6",(4,5,6))):
                db.execute("INSERT INTO pair_source_trio VALUES (?,?,?,?,?,?,?,?,?)", (tid,"PR",key,*nums,"TRIO_TEST","d"*64,1))
            db.execute("INSERT INTO pair_candidate VALUES (?,?,?,?,?,?,?,?,?)", ("PAIR","PR","1-2-3__4-5-6","SIG","CANDIDATE_ONLY",None,0,"e"*64,"now"))
            db.execute("INSERT INTO pair_walkforward_run VALUES (?,?,?,?,?,?,?)", ("WF","f"*64,1,1,"RUNNING","now",None))
            db.execute("INSERT INTO pair_walkforward_round VALUES (?,?,?,?,?,?,?)", ("WF",1,"COMPLETE","1"*64,"2"*64,1,None))
            db.execute("INSERT INTO pair_walkforward_exposure VALUES (?,?,?,?,?,?,?)", ("EXP","WF",1,"SIG","PAIR","SELECTION_RULE",1))

    def test_store_and_reload_boolean_flags(self) -> None:
        self._full_parent()
        self.store.save_walkforward_outcome("EXP", a_integrated_hits=3,b_integrated_hits=2,a_main_hits=2,b_main_hits=2,
            a_bonus_assisted_triple=True,b_bonus_assisted_triple=False,integrated_category="SINGLE_TRIPLE_SUCCESS",
            main_category="NO_TRIPLE_WITH_DOUBLE_EXACT2",outcome_hash="a"*64)
        row=self.store.load_walkforward_outcome("EXP"); self.assertEqual(1,row["a_bonus_assisted_triple"]); self.assertEqual(0,row["b_bonus_assisted_triple"])

    def test_invalid_boolean_rejected(self) -> None:
        self._full_parent()
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store.transaction() as db:
                db.execute("INSERT INTO pair_walkforward_outcome VALUES (?,?,?,?,?,?,?,?,?,?)", ("EXP",3,2,2,2,2,0,"X","Y","a"*64))

    def test_fk_and_unique(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.save_walkforward_outcome("MISSING",a_integrated_hits=0,b_integrated_hits=0,a_main_hits=0,b_main_hits=0,a_bonus_assisted_triple=False,b_bonus_assisted_triple=False,integrated_category="X",main_category="Y",outcome_hash="a"*64)
        self._full_parent(); kw=dict(a_integrated_hits=0,b_integrated_hits=0,a_main_hits=0,b_main_hits=0,a_bonus_assisted_triple=False,b_bonus_assisted_triple=False,integrated_category="X",main_category="Y",outcome_hash="a"*64)
        self.store.save_walkforward_outcome("EXP",**kw)
        with self.assertRaises(sqlite3.IntegrityError): self.store.save_walkforward_outcome("EXP",**kw)

    def test_integrity_and_foreign_keys(self) -> None:
        db=self.store.connect()
        try: self.assertEqual("ok",db.execute("PRAGMA integrity_check").fetchone()[0]); self.assertEqual([],db.execute("PRAGMA foreign_key_check").fetchall())
        finally: db.close()

    def test_rollback(self) -> None:
        self._full_parent()
        with self.assertRaises(RuntimeError):
            with self.store.transaction() as db:
                db.execute("INSERT INTO pair_walkforward_outcome VALUES (?,?,?,?,?,?,?,?,?,?)", ("EXP",0,0,0,0,0,0,"X","Y","a"*64)); raise RuntimeError("stop")
        self.assertIsNone(self.store.load_walkforward_outcome("EXP"))

if __name__ == "__main__": unittest.main()

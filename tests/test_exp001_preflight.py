from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from fractions import Fraction
from pathlib import Path

from p45_experiments.exp001.calculator import (
    baseline,
    clopper_pearson_95,
    holm_adjust,
    max_t_null_structure,
    period_rows,
    prediction_hash,
    risk_difference,
    unordered_pairs,
)
from p45_experiments.exp001.constants import INTEGRATED_CONDITIONAL, MAIN_CONDITIONAL, RECENT20_POLICY, SCHEMA_VERSION
from p45_experiments.exp001.snapshot import DrawRow
from p45_experiments.exp001.store import Exp001Store
from p45_experiments.exp001.walkforward_guard import PreResultGuard


class Exp001PreflightTests(unittest.TestCase):
    def test_01_exactly_990_unordered_pairs(self):
        pairs = unordered_pairs()
        self.assertEqual(990, len(pairs))
        self.assertEqual(990, len(set(pairs)))

    def test_02_no_reverse_or_self_pairs(self):
        pairs = set(unordered_pairs())
        self.assertTrue(all(a < b for a, b in pairs))
        self.assertTrue(all((b, a) not in pairs for a, b in pairs))

    def test_03_main_theory(self):
        self.assertEqual(Fraction(1, 66), baseline("MAIN"))
        self.assertEqual(Fraction(5, 44), MAIN_CONDITIONAL)

    def test_04_integrated_theory(self):
        self.assertEqual(Fraction(7, 330), baseline("INTEGRATED"))
        self.assertEqual(Fraction(6, 44), INTEGRATED_CONDITIONAL)

    def test_05_risk_difference(self):
        self.assertAlmostEqual(0.1 - 1 / 66, risk_difference(10, 100, Fraction(1, 66)))

    def test_06_holm_known_vector(self):
        adjusted = holm_adjust([0.01, 0.04, 0.03])
        self.assertEqual([0.03, 0.06, 0.06], [round(value, 8) for value in adjusted])

    def test_07_max_t_structure_deterministic(self):
        first = max_t_null_structure("MAIN", 3, repetitions=2)
        second = max_t_null_structure("MAIN", 3, repetitions=2)
        self.assertEqual(first, second)
        self.assertEqual("IID_FAIR_DRAW_NULL_MAXT", first["null"])

    def test_08_period_split_and_recent20(self):
        rows = [DrawRow(i, "2000-01-01", (1, 2, 3, 4, 5, 6), 7) for i in range(1, 61)]
        self.assertEqual(30, len(period_rows(rows, "FIRST_HALF", 60)))
        self.assertEqual(30, len(period_rows(rows, "SECOND_HALF", 60)))
        self.assertEqual(list(range(41, 61)), [x.round for x in period_rows(rows, "RECENT_20", 60)])
        self.assertEqual("TEST_ONLY", RECENT20_POLICY)

    def test_09_future_data_block(self):
        rows = [DrawRow(i, "2000-01-01", (1, 2, 3, 4, 5, 6), 7) for i in range(1, 12)]
        self.assertEqual(10, max(x.round for x in period_rows(rows, "OVERALL", 10)))

    def test_10_r_minus_one_boundary(self):
        evaluation_round = 11
        rows = [DrawRow(i, "2000-01-01", (1, 2, 3, 4, 5, 6), 7) for i in range(1, 12)]
        used = period_rows(rows, "OVERALL", evaluation_round - 1)
        self.assertNotIn(evaluation_round, [x.round for x in used])

    def test_11_prediction_hash_deterministic(self):
        payload = {"evaluation_round": 11, "source_end_round": 10, "pairs": [[1, 2]]}
        self.assertEqual(1, len({prediction_hash(payload) for _ in range(10)}))

    def test_12_store_schema_integrity_and_empty_results(self):
        with tempfile.TemporaryDirectory() as temp:
            store = Exp001Store(Path(temp) / "exp.sqlite3")
            store.initialize()
            self.assertEqual(("ok", 0), store.integrity())
            self.assertEqual(0, store.result_row_count())
            with closing(store.connect(read_only=True)) as connection:
                self.assertEqual(SCHEMA_VERSION, connection.execute("PRAGMA user_version").fetchone()[0])

    def test_13_store_rollback(self):
        with tempfile.TemporaryDirectory() as temp:
            store = Exp001Store(Path(temp) / "exp.sqlite3")
            store.initialize()
            connection = store.connect()
            try:
                connection.execute("BEGIN")
                connection.execute("INSERT INTO protocol_registry VALUES(?,?,?,?,?)", ("X", "H", "D", "{}", "LOCKED_BEFORE_BACKTEST"))
                connection.rollback()
            finally:
                connection.close()
            with closing(store.connect(read_only=True)) as check:
                self.assertEqual(0, check.execute("SELECT COUNT(*) FROM protocol_registry").fetchone()[0])

    def test_14_outcome_blocked_before_prediction_hash(self):
        guard = PreResultGuard(101, 100)
        with self.assertRaises(RuntimeError):
            guard.authorize_outcome_access()
        guard.lock_prediction({"evaluation_round": 101, "source_end_round": 100})
        guard.authorize_outcome_access()
        self.assertEqual(1, guard.outcome_accesses)

    def test_15_invalid_r_minus_one_boundary_rejected(self):
        with self.assertRaises(ValueError):
            PreResultGuard(101, 99)

    def test_16_clopper_pearson_boundaries(self):
        low_zero, high_zero = clopper_pearson_95(0, 100)
        low_all, high_all = clopper_pearson_95(100, 100)
        self.assertEqual(0.0, low_zero)
        self.assertEqual(1.0, high_all)
        self.assertGreater(high_zero, 0.0)
        self.assertLess(low_all, 1.0)


if __name__ == "__main__":
    unittest.main()

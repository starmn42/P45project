from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from p45_v27.pairs import (
    PairSignatureContext,
    PairStore,
    TrioInput,
    canonical_pair_key,
    generate_pair_candidates,
    pair_rule_signature,
)


def trio(name: str, numbers: tuple[int, int, int], marker: str) -> TrioInput:
    return TrioInput(name, numbers, "TRIO_TEST", marker * 64)


def context(_: TrioInput, __: TrioInput) -> PairSignatureContext:
    return PairSignatureContext(
        "EXPANDED_TEST_POOL",
        ("TEST", "TEST", "HOLD", "TEST", "HOLD"),
        (1, 2, 1, 2, 1),
        (0, 1, 0, 1, 0),
        "MEDIUM", "NORMAL",
    )


class PairStage12Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "pair274.sqlite3"
        self.store = PairStore(self.db_path)
        self.store.initialize()
        self.a = trio("T-A", (1, 2, 3), "a")
        self.b = trio("T-B", (4, 5, 6), "b")
        self.c = trio("T-C", (3, 7, 8), "c")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_schema_integrity_fk_and_table_count(self) -> None:
        db = self.store.connect()
        try:
            self.assertEqual(274, db.execute("PRAGMA user_version").fetchone()[0])
            self.assertEqual("ok", db.execute("PRAGMA integrity_check").fetchone()[0])
            self.assertEqual([], db.execute("PRAGMA foreign_key_check").fetchall())
        finally:
            db.close()
        self.assertEqual(18, self.store.table_count())

    def test_schema_foreign_key_is_enforced(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store.transaction() as db:
                db.execute("INSERT INTO pair_source_trio VALUES (?,?,?,?,?,?,?,?,?)", ("x", "missing", "1-2-3", 1, 2, 3, "TRIO_TEST", "a" * 64, 1))

    def test_store_and_reload(self) -> None:
        self.store.create_run("RUN-1", rule_hash="a" * 64, source_hash="b" * 64)
        self.store.add_source_trios("RUN-1", (self.a, self.b))
        candidate = generate_pair_candidates((self.a, self.b), context)[0]
        stored_id = self.store.save_candidate("RUN-1", candidate)
        rows = self.store.load_candidates("RUN-1")
        self.assertEqual(1, len(rows))
        self.assertEqual(stored_id, rows[0]["pair_candidate_id"])
        self.assertEqual(candidate.canonical_pair_key, rows[0]["canonical_pair_key"])
        self.assertEqual(dict(candidate.signature_payload), rows[0]["signature_payload"])

    def test_transaction_rolls_back(self) -> None:
        with self.assertRaises(RuntimeError):
            with self.store.transaction() as db:
                db.execute("INSERT INTO pair_run VALUES (?,?,?,?,?,?)", ("ROLLBACK", "SYNTHETIC_TEST", "a" * 64, "b" * 64, "CANDIDATE_ONLY", "now"))
                raise RuntimeError("synthetic failure")
        db = self.store.connect()
        try:
            self.assertEqual(0, db.execute("SELECT count(*) FROM pair_run WHERE pair_run_id='ROLLBACK'").fetchone()[0])
        finally:
            db.close()

    def test_only_disjoint_pairs_are_generated(self) -> None:
        candidates = generate_pair_candidates((self.a, self.b, self.c), context)
        self.assertEqual(2, len(candidates))
        for candidate in candidates:
            self.assertFalse(set(candidate.lower_member.numbers) & set(candidate.upper_member.numbers))

    def test_canonical_key_is_order_independent(self) -> None:
        self.assertEqual(canonical_pair_key(self.a, self.b), canonical_pair_key(self.b, self.a))

    def test_duplicate_candidates_are_eliminated(self) -> None:
        candidates = generate_pair_candidates((self.a, self.b, self.a, self.b), context)
        self.assertEqual(1, len(candidates))
        self.assertEqual(1, len({item.canonical_pair_key for item in candidates}))

    def test_signature_excludes_number_identity_and_performance(self) -> None:
        x = trio("T-X", (10, 11, 12), "a")
        y = trio("T-Y", (20, 21, 22), "b")
        first, payload = pair_rule_signature(self.a, self.b, context(self.a, self.b))
        second, _ = pair_rule_signature(x, y, context(x, y))
        self.assertEqual(first, second)
        forbidden = {"numbers", "trio_id", "hits", "outcome", "future", "performance"}
        self.assertTrue(forbidden.isdisjoint(payload))

    def test_signature_is_deterministic_ten_times(self) -> None:
        values = [pair_rule_signature(self.a, self.b, context(self.a, self.b))[0] for _ in range(10)]
        self.assertEqual(1, len(set(values)))

    def test_unique_candidate_constraint(self) -> None:
        self.store.create_run("RUN-U", rule_hash="a" * 64, source_hash="b" * 64)
        self.store.add_source_trios("RUN-U", (self.a, self.b))
        candidate = generate_pair_candidates((self.a, self.b), context)[0]
        self.store.save_candidate("RUN-U", candidate)
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.save_candidate("RUN-U", candidate)


if __name__ == "__main__":
    unittest.main()

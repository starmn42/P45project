"""Repository for standalone schema-274 PAIR storage."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .engine import SIGNATURE_VERSION, canonical_json
from .models import PairCandidate, TrioInput
from .schema274 import PAIR_SCHEMA_274, SCHEMA_VERSION


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class PairStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def initialize(self, *, fail_if_exists: bool = True) -> None:
        if fail_if_exists and self.path.exists():
            raise FileExistsError(self.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        try:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=FULL")
            with connection:
                connection.executescript(PAIR_SCHEMA_274)
                connection.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
            if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("PAIR_SCHEMA_274_INTEGRITY_FAILED")
        finally:
            connection.close()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def create_run(self, pair_run_id: str, *, rule_hash: str, source_hash: str) -> None:
        with self.transaction() as db:
            db.execute(
                "INSERT INTO pair_run VALUES (?,?,?,?,?,?)",
                (pair_run_id, "SYNTHETIC_TEST", rule_hash, source_hash, "CANDIDATE_ONLY", utc_now()),
            )

    def add_source_trios(self, pair_run_id: str, trios: tuple[TrioInput, ...]) -> None:
        with self.transaction() as db:
            db.executemany(
                "INSERT INTO pair_source_trio VALUES (?,?,?,?,?,?,?,?,?)",
                [
                    (
                        trio.trio_id, pair_run_id, trio.trio_key, *trio.numbers, trio.trio_state,
                        trio.trio_rule_signature, int(trio.valid_for_pair),
                    )
                    for trio in trios
                ],
            )

    def save_candidate(self, pair_run_id: str, candidate: PairCandidate) -> str:
        signature_id = "SIG-" + hashlib.sha256(
            f"{pair_run_id}|{candidate.pair_rule_signature}".encode("utf-8")
        ).hexdigest()
        stored_candidate_id = "PAIR-" + hashlib.sha256(
            f"{pair_run_id}|{candidate.canonical_pair_key}".encode("utf-8")
        ).hexdigest()
        now = utc_now()
        row_hash = hashlib.sha256(
            canonical_json({"run": pair_run_id, "key": candidate.canonical_pair_key, "signature": candidate.pair_rule_signature}).encode("utf-8")
        ).hexdigest()
        with self.transaction() as db:
            db.execute(
                "INSERT OR IGNORE INTO pair_rule_signature VALUES (?,?,?,?,?,?)",
                (signature_id, pair_run_id, SIGNATURE_VERSION, canonical_json(candidate.signature_payload), candidate.pair_rule_signature, now),
            )
            db.execute(
                "INSERT INTO pair_candidate VALUES (?,?,?,?,?,?,?,?,?)",
                (stored_candidate_id, pair_run_id, candidate.canonical_pair_key, signature_id, "CANDIDATE_ONLY", None, 0, row_hash, now),
            )
            db.executemany(
                "INSERT INTO pair_member VALUES (?,?,?,?)",
                (
                    (stored_candidate_id, "CANONICAL_LOWER", candidate.lower_member.trio_id, candidate.lower_member.trio_key),
                    (stored_candidate_id, "CANONICAL_UPPER", candidate.upper_member.trio_id, candidate.upper_member.trio_key),
                ),
            )
        return stored_candidate_id

    def load_candidates(self, pair_run_id: str) -> list[dict[str, object]]:
        db = self.connect()
        try:
            rows = db.execute(
                "SELECT c.*,s.signature_payload_json FROM pair_candidate c JOIN pair_rule_signature s USING(signature_id) WHERE c.pair_run_id=? ORDER BY c.canonical_pair_key",
                (pair_run_id,),
            ).fetchall()
        finally:
            db.close()
        return [{**dict(row), "signature_payload": json.loads(row["signature_payload_json"])} for row in rows]

    def table_count(self) -> int:
        db = self.connect()
        try:
            return db.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone()[0]
        finally:
            db.close()

    def save_walkforward_outcome(
        self, exposure_id: str, *, a_integrated_hits: int, b_integrated_hits: int,
        a_main_hits: int, b_main_hits: int, a_bonus_assisted_triple: bool,
        b_bonus_assisted_triple: bool, integrated_category: str,
        main_category: str, outcome_hash: str,
    ) -> None:
        with self.transaction() as db:
            db.execute(
                "INSERT INTO pair_walkforward_outcome VALUES (?,?,?,?,?,?,?,?,?,?)",
                (exposure_id, a_integrated_hits, b_integrated_hits, a_main_hits, b_main_hits,
                 int(a_bonus_assisted_triple), int(b_bonus_assisted_triple),
                 integrated_category, main_category, outcome_hash),
            )

    def load_walkforward_outcome(self, exposure_id: str) -> dict[str, object] | None:
        db = self.connect()
        try:
            row = db.execute("SELECT * FROM pair_walkforward_outcome WHERE exposure_id=?", (exposure_id,)).fetchone()
            return None if row is None else dict(row)
        finally:
            db.close()

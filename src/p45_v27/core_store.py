"""Write access for v2.7 CORE data only.

This module has no import dependency on the legacy ``p45`` package.
"""

from __future__ import annotations

import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterator

from .database import StoragePaths, connect_core
from .integrity import canonical_json, sha256_json


def utc_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class CoreStoreError(RuntimeError):
    pass


class CoreStore:
    def __init__(self, paths: StoragePaths) -> None:
        self.paths = paths

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = connect_core(self.paths)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def register_engine_version(
        self,
        *,
        version_label: str,
        directive_sha256: str,
        implementation_order_sha256: str,
        rule_hash: str,
        code_hash: str,
        effective_round: int,
        version_status: str = "DRAFT",
        engine_version_id: str | None = None,
        search_family_hash: str | None = None,
    ) -> str:
        version_id = engine_version_id or str(uuid.uuid4())
        with self.transaction() as db:
            db.execute(
                """
                INSERT INTO engine_version_record (
                    engine_version_id, version_label, directive_sha256,
                    implementation_order_sha256, rule_hash, code_hash,
                    search_family_hash, effective_round, version_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version_id, version_label, directive_sha256,
                    implementation_order_sha256, rule_hash, code_hash,
                    search_family_hash, effective_round, version_status, utc_now(),
                ),
            )
        return version_id

    def create_core_run(
        self,
        *,
        engine_version_id: str,
        analysis_round: int,
        record_class: str,
        raw_data_hash: str,
        normalized_data_hash: str,
        rule_hash: str,
        code_hash: str,
        search_family_hash: str | None = None,
        core_run_id: str | None = None,
    ) -> str:
        run_id = core_run_id or str(uuid.uuid4())
        now = utc_now()
        with self.transaction() as db:
            db.execute(
                """
                INSERT INTO core_run (
                    core_run_id, engine_version_id, analysis_round, record_class,
                    data_start_round, data_end_round, raw_data_hash,
                    normalized_data_hash, rule_hash, code_hash, search_family_hash,
                    core_status, calculation_status, started_at, created_at
                ) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, 'RUNNING', 'PARTIAL', ?, ?)
                """,
                (
                    run_id, engine_version_id, analysis_round, record_class,
                    analysis_round - 1, raw_data_hash, normalized_data_hash,
                    rule_hash, code_hash, search_family_hash, now, now,
                ),
            )
        return run_id

    def lock_core_result(
        self,
        *,
        core_run_id: str,
        core_status: str,
        report_hash: str,
        manifest_hash: str,
        sets: tuple[tuple[int, int, int], tuple[int, int, int]] | None = None,
        selected_pair_id: str | None = None,
        previous_lock_hash: str | None = None,
        audit_status_at_lock: str = "AUDIT_NOT_RUN",
        certification_at_lock: str = "EXPLORATORY",
        core_locked_result_id: str | None = None,
    ) -> str:
        lock_id = core_locked_result_id or str(uuid.uuid4())
        with self.transaction() as db:
            run = db.execute("SELECT * FROM core_run WHERE core_run_id = ?", (core_run_id,)).fetchone()
            if run is None:
                raise CoreStoreError(f"CORE 실행을 찾을 수 없습니다: {core_run_id}")
            if run["lock_status"] == "LOCKED":
                raise CoreStoreError("이미 잠긴 CORE 실행입니다.")
            if core_status in ("CORE_SET_READY", "CORE_TEST_SET_READY") and sets is None:
                raise CoreStoreError("세트 준비 상태에는 세트1·세트2가 필요합니다.")
            if core_status in ("CORE_RESEARCH_HOLD", "CORE_SYSTEM_HOLD"):
                values: tuple[int | None, ...] = (None, None, None, None, None, None)
            else:
                assert sets is not None
                left, right = tuple(sorted(sets[0])), tuple(sorted(sets[1]))
                if len(set((*left, *right))) != 6 or any(not 1 <= value <= 45 for value in (*left, *right)):
                    raise CoreStoreError("잠금 세트는 1~45의 서로 다른 숫자 6개여야 합니다.")
                values = (*left, *right)
            payload = {
                "core_run_id": core_run_id,
                "core_status": core_status,
                "record_class": run["record_class"],
                "analysis_round": run["analysis_round"],
                "sets": values,
                "selected_pair_id": selected_pair_id,
                "report_hash": report_hash,
                "manifest_hash": manifest_hash,
                "previous_lock_hash": previous_lock_hash,
            }
            result_hash = sha256_json(payload)
            now = utc_now()
            db.execute(
                """
                UPDATE core_run
                SET core_status = ?, calculation_status = 'COMPLETE', execution_hash = ?,
                    completed_at = ?, lock_status = 'LOCKED'
                WHERE core_run_id = ?
                """,
                (core_status, result_hash, now, core_run_id),
            )
            db.execute(
                """
                INSERT INTO core_locked_result (
                    core_locked_result_id, core_run_id, engine_version_id,
                    analysis_round, record_class, core_status, selected_pair_id,
                    set1_n1, set1_n2, set1_n3, set2_n1, set2_n2, set2_n3,
                    audit_status_at_lock, certification_at_lock, core_result_hash,
                    report_hash, manifest_hash, previous_lock_hash, locked_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lock_id, core_run_id, run["engine_version_id"], run["analysis_round"],
                    run["record_class"], core_status, selected_pair_id, *values,
                    audit_status_at_lock, certification_at_lock, result_hash,
                    report_hash, manifest_hash, previous_lock_hash, now,
                ),
            )
        return lock_id

    def locked_result(self, core_run_id: str) -> dict[str, Any] | None:
        db = connect_core(self.paths, readonly=True)
        try:
            row = db.execute("SELECT * FROM core_locked_result WHERE core_run_id = ?", (core_run_id,)).fetchone()
            return dict(row) if row else None
        finally:
            db.close()

    def explicit_result(
        self, *, engine_version_id: str, analysis_round: int, record_class: str
    ) -> list[dict[str, Any]]:
        """Never guesses by largest round; all identity fields are required."""
        db = connect_core(self.paths, readonly=True)
        try:
            rows = db.execute(
                """
                SELECT l.* FROM core_locked_result AS l
                WHERE l.engine_version_id = ? AND l.analysis_round = ? AND l.record_class = ?
                ORDER BY l.locked_at, l.core_locked_result_id
                """,
                (engine_version_id, analysis_round, record_class),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            db.close()


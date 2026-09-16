"""AUDIT-only persistence with read-only CORE references."""

from __future__ import annotations

import sqlite3
import uuid
from contextlib import contextmanager
from typing import Any, Iterator

from .core_store import utc_now
from .database import StoragePaths, connect_audit, connect_core


class AuditStoreError(RuntimeError):
    pass


class AuditStore:
    def __init__(self, paths: StoragePaths) -> None:
        self.paths = paths

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = connect_audit(self.paths)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def verify_core_reference(self, core_run_id: str, core_result_hash: str) -> dict[str, Any]:
        core = connect_core(self.paths, readonly=True)
        try:
            row = core.execute(
                "SELECT * FROM core_locked_result WHERE core_run_id = ? AND core_result_hash = ?",
                (core_run_id, core_result_hash),
            ).fetchone()
            if row is None:
                raise AuditStoreError("잠긴 CORE ID와 해시가 일치하지 않습니다.")
            return dict(row)
        finally:
            core.close()

    def create_audit_run(
        self,
        *,
        core_run_id: str,
        core_result_hash: str,
        normalized_data_hash: str,
        rule_hash: str,
        code_hash: str,
        search_family_hash: str,
        generator_id: str,
        seed_root: str,
        audit_kind: str,
        target_iterations: int,
        audit_run_id: str | None = None,
    ) -> str:
        locked = self.verify_core_reference(core_run_id, core_result_hash)
        run_id = audit_run_id or str(uuid.uuid4())
        with self.transaction() as db:
            db.execute(
                """
                INSERT INTO audit_run (
                    audit_run_id, engine_version_id, core_run_id, core_result_hash,
                    normalized_data_hash, rule_hash, code_hash, search_family_hash,
                    generator_id, seed_root, audit_kind, target_iterations,
                    audit_status, certification_level, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'AUDIT_PENDING', 'EXPLORATORY', ?)
                """,
                (
                    run_id, locked["engine_version_id"], core_run_id, core_result_hash,
                    normalized_data_hash, rule_hash, code_hash, search_family_hash,
                    generator_id, seed_root, audit_kind, target_iterations, utc_now(),
                ),
            )
        return run_id

    def add_chunk(
        self,
        *,
        audit_run_id: str,
        null_type: str,
        iteration_start: int,
        iteration_end: int,
        audit_chunk_id: str | None = None,
    ) -> str:
        chunk_id = audit_chunk_id or str(uuid.uuid4())
        with self.transaction() as db:
            db.execute(
                """
                INSERT INTO audit_chunk (
                    audit_chunk_id, audit_run_id, null_type, iteration_start,
                    iteration_end, chunk_status, created_at
                ) VALUES (?, ?, ?, ?, ?, 'PENDING', ?)
                """,
                (chunk_id, audit_run_id, null_type, iteration_start, iteration_end, utc_now()),
            )
        return chunk_id

    def complete_chunk(
        self,
        chunk_id: str,
        *,
        result_path: str,
        result_hash: str,
        distribution_hash: str,
        summary_json: str,
    ) -> None:
        with self.transaction() as db:
            changed = db.execute(
                """
                UPDATE audit_chunk
                SET chunk_status='COMPLETE', result_path=?, result_hash=?,
                    distribution_hash=?, summary_json=?, completed_at=?
                WHERE audit_chunk_id=? AND chunk_status IN ('PENDING','RUNNING')
                """,
                (result_path, result_hash, distribution_hash, summary_json, utc_now(), chunk_id),
            ).rowcount
            if changed != 1:
                raise AuditStoreError("완료할 수 있는 감사 청크가 아닙니다.")

    def add_cache_snapshot(
        self,
        *,
        audit_run_id: str,
        cache_key: str,
        null_type: str,
        completed_iterations: int,
        completed_ranges_json: str,
        distribution_path: str,
        distribution_hash: str,
        snapshot_hash: str,
        parent_cache_id: str | None = None,
        audit_cache_id: str | None = None,
    ) -> str:
        cache_id = audit_cache_id or str(uuid.uuid4())
        with self.transaction() as db:
            db.execute(
                """
                INSERT INTO audit_cache (
                    audit_cache_id, audit_run_id, parent_cache_id, cache_key,
                    null_type, completed_iterations, completed_ranges_json,
                    distribution_path, distribution_hash, cache_status,
                    snapshot_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETE', ?, ?)
                """,
                (
                    cache_id, audit_run_id, parent_cache_id, cache_key, null_type,
                    completed_iterations, completed_ranges_json, distribution_path,
                    distribution_hash, snapshot_hash, utc_now(),
                ),
            )
        return cache_id


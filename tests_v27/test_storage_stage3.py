from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from p45_v27.audit_store import AuditStore
from p45_v27.core_store import CoreStore
from p45_v27.database import (
    StoragePaths,
    connect_audit,
    connect_core,
    initialize_storage,
    schema_tables,
)
from p45_v27.legacy_readonly import LegacyReadOnlyAdapter, LegacyReadOnlyError
from p45_v27.maintenance import backup_database, export_tables, integrity_report
from p45_v27.schema import AUDIT_TABLES, CORE_TABLES


H = "a" * 64
H2 = "b" * 64
H3 = "c" * 64


class StorageStage3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.paths = initialize_storage(self.root / "v27_storage")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _locked_hold(self) -> tuple[CoreStore, str, str]:
        store = CoreStore(self.paths)
        version_id = store.register_engine_version(
            version_label="P45 v2.7 test",
            directive_sha256=H,
            implementation_order_sha256=H2,
            rule_hash=H,
            code_hash=H2,
            effective_round=1237,
        )
        run_id = store.create_core_run(
            engine_version_id=version_id,
            analysis_round=1237,
            record_class="LIVE_TEST",
            raw_data_hash=H,
            normalized_data_hash=H2,
            rule_hash=H,
            code_hash=H2,
            search_family_hash=H3,
        )
        store.lock_core_result(
            core_run_id=run_id,
            core_status="CORE_RESEARCH_HOLD",
            report_hash=H,
            manifest_hash=H2,
        )
        result = store.locked_result(run_id)
        assert result is not None
        return store, run_id, result["core_result_hash"]

    def test_creates_exact_approved_tables_in_two_databases(self) -> None:
        core = connect_core(self.paths, readonly=True)
        audit = connect_audit(self.paths, readonly=True)
        try:
            self.assertEqual(schema_tables(core), CORE_TABLES)
            self.assertEqual(schema_tables(audit), AUDIT_TABLES)
            self.assertNotEqual(self.paths.core_db, self.paths.audit_db)
        finally:
            audit.close()
            core.close()

    def test_locked_core_result_and_run_cannot_be_changed_or_deleted(self) -> None:
        _, run_id, _ = self._locked_hold()
        db = connect_core(self.paths)
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE core_run SET core_status='CORE_SYSTEM_HOLD' WHERE core_run_id=?", (run_id,))
            db.rollback()
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM core_locked_result WHERE core_run_id=?", (run_id,))
            db.rollback()
        finally:
            db.close()

    def test_audit_uses_hash_checked_read_only_core_reference(self) -> None:
        _, run_id, result_hash = self._locked_hold()
        audit = AuditStore(self.paths)
        audit_id = audit.create_audit_run(
            core_run_id=run_id,
            core_result_hash=result_hash,
            normalized_data_hash=H2,
            rule_hash=H,
            code_hash=H2,
            search_family_hash=H3,
            generator_id="TEST-GENERATOR",
            seed_root=H3,
            audit_kind="DEVELOPMENT_1K",
            target_iterations=1000,
        )
        db = connect_audit(self.paths, readonly=True)
        try:
            self.assertEqual(db.execute("SELECT core_run_id FROM audit_run WHERE audit_run_id=?", (audit_id,)).fetchone()[0], run_id)
        finally:
            db.close()

    def test_completed_chunks_and_cache_snapshots_are_immutable(self) -> None:
        _, run_id, result_hash = self._locked_hold()
        audit = AuditStore(self.paths)
        audit_id = audit.create_audit_run(
            core_run_id=run_id, core_result_hash=result_hash,
            normalized_data_hash=H2, rule_hash=H, code_hash=H2,
            search_family_hash=H3, generator_id="G", seed_root=H3,
            audit_kind="DEVELOPMENT_1K", target_iterations=1000,
        )
        chunk = audit.add_chunk(
            audit_run_id=audit_id, null_type="IID_SYNTHETIC_NULL",
            iteration_start=0, iteration_end=100,
        )
        audit.complete_chunk(chunk, result_path="chunk.jsonl", result_hash=H, distribution_hash=H2, summary_json="{}")
        cache = audit.add_cache_snapshot(
            audit_run_id=audit_id, cache_key=H, null_type="IID_SYNTHETIC_NULL",
            completed_iterations=100, completed_ranges_json="[[0,100]]",
            distribution_path="distribution.jsonl", distribution_hash=H2, snapshot_hash=H3,
        )
        db = connect_audit(self.paths)
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE audit_chunk SET result_path='changed' WHERE audit_chunk_id=?", (chunk,))
            db.rollback()
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM audit_cache WHERE audit_cache_id=?", (cache,))
            db.rollback()
        finally:
            db.close()

    def test_backup_integrity_and_auditable_export(self) -> None:
        self._locked_hold()
        backup = self.root / "backup" / "core.sqlite3"
        report = backup_database(self.paths.core_db, backup)
        self.assertTrue(report["pass"])
        self.assertTrue(integrity_report(backup)["pass"])
        manifest = export_tables(backup, self.root / "export", ["core_run", "core_locked_result"])
        document = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual([item["row_count"] for item in document["files"]], [1, 1])

    def test_legacy_adapter_has_no_write_surface_and_rejects_outside_paths(self) -> None:
        legacy = self.root / "ledger" / "sample.json"
        legacy.parent.mkdir()
        legacy.write_text('{"ok":true}', encoding="utf-8")
        adapter = LegacyReadOnlyAdapter(self.root)
        self.assertEqual(adapter.read_json("ledger/sample.json"), {"ok": True})
        self.assertFalse(hasattr(adapter, "write_text"))
        with self.assertRaises(LegacyReadOnlyError):
            adapter.read_text("v27_storage/db/p45_v27_core.sqlite3")


if __name__ == "__main__":
    unittest.main()


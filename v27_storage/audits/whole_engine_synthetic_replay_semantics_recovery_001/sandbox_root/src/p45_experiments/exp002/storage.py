"""Isolated EXP-002 storage. It never opens an official P45 DB for writing."""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_VERSION = 2002
SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS protocol_registry(
 experiment_id TEXT PRIMARY KEY, protocol_version TEXT NOT NULL, protocol_hash TEXT,
 lock_status TEXT NOT NULL CHECK(lock_status IN ('DRAFT','READY_TO_LOCK','LOCKED')),
 created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS coverage_audit_run(
 audit_id TEXT PRIMARY KEY, source_trio_run_id TEXT NOT NULL, source_pair_run_id TEXT NOT NULL,
 start_round INTEGER NOT NULL, end_round INTEGER NOT NULL, first_eligible_round INTEGER NOT NULL,
 audit_hash TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('RUNNING','COMPLETE','FAILED')),
 created_at TEXT NOT NULL, completed_at TEXT);
CREATE TABLE IF NOT EXISTS coverage_audit_round(
 audit_id TEXT NOT NULL, evaluation_round INTEGER NOT NULL, source_end_round INTEGER NOT NULL,
 availability_class TEXT NOT NULL, no_pick_stage TEXT,
 number_candidate_count INTEGER, number_pass INTEGER, number_weaken INTEGER,
 number_test INTEGER, number_hold INTEGER, number_fail INTEGER,
 valid_trio_count INTEGER, trio_pass INTEGER, trio_test INTEGER, trio_hold INTEGER,
 eligible_pair_count INTEGER, pair_ready INTEGER, pair_test_ready INTEGER,
 pair_research_hold INTEGER, pair_system_hold INTEGER, valid_for_core INTEGER NOT NULL,
 final_output_available INTEGER NOT NULL, row_hash TEXT NOT NULL,
 PRIMARY KEY(audit_id,evaluation_round),
 FOREIGN KEY(audit_id) REFERENCES coverage_audit_run(audit_id) ON DELETE RESTRICT);
CREATE TABLE IF NOT EXISTS experiment_run(
 run_id TEXT PRIMARY KEY, experiment_id TEXT NOT NULL, protocol_hash TEXT NOT NULL,
 data_snapshot_hash TEXT NOT NULL, prediction_count INTEGER NOT NULL DEFAULT 0,
 status TEXT NOT NULL CHECK(status IN ('PENDING','RUNNING','COMPLETE','FAILED','INVALID')),
 started_at TEXT, completed_at TEXT);
CREATE TABLE IF NOT EXISTS prediction_lock(
 run_id TEXT NOT NULL, evaluation_round INTEGER NOT NULL, source_end_round INTEGER NOT NULL,
 eligibility_json TEXT NOT NULL, trio_a_json TEXT, trio_b_json TEXT,
 prediction_hash TEXT NOT NULL, locked_before_outcome INTEGER NOT NULL CHECK(locked_before_outcome=1),
 PRIMARY KEY(run_id,evaluation_round), FOREIGN KEY(run_id) REFERENCES experiment_run(run_id));
CREATE TABLE IF NOT EXISTS experiment_outcome(
 run_id TEXT NOT NULL, evaluation_round INTEGER NOT NULL,
 integrated_primary_a INTEGER NOT NULL, integrated_primary_b INTEGER NOT NULL,
 main_primary_a INTEGER NOT NULL, main_primary_b INTEGER NOT NULL,
 integrated_exact2_a INTEGER NOT NULL, integrated_exact2_b INTEGER NOT NULL,
 main_exact2_a INTEGER NOT NULL, main_exact2_b INTEGER NOT NULL,
 outcome_hash TEXT NOT NULL, PRIMARY KEY(run_id,evaluation_round),
 FOREIGN KEY(run_id,evaluation_round) REFERENCES prediction_lock(run_id,evaluation_round));
CREATE TABLE IF NOT EXISTS experiment_judgment(
 run_id TEXT PRIMARY KEY, coverage_result TEXT NOT NULL, performance_result TEXT NOT NULL,
 final_judgment TEXT NOT NULL, promotion_candidate INTEGER NOT NULL CHECK(promotion_candidate IN (0,1)),
 judgment_json TEXT NOT NULL, FOREIGN KEY(run_id) REFERENCES experiment_run(run_id));
CREATE TABLE IF NOT EXISTS protocol_file(
 experiment_id TEXT NOT NULL, relative_path TEXT NOT NULL, file_sha256 TEXT NOT NULL,
 PRIMARY KEY(experiment_id,relative_path), FOREIGN KEY(experiment_id) REFERENCES protocol_registry(experiment_id));
CREATE TABLE IF NOT EXISTS data_snapshot(
 snapshot_hash TEXT PRIMARY KEY, relative_path TEXT NOT NULL, first_round INTEGER NOT NULL,
 last_round INTEGER NOT NULL, row_count INTEGER NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS prediction_detail(
 run_id TEXT NOT NULL, evaluation_round INTEGER NOT NULL, source_pool_json TEXT NOT NULL,
 ordered_trios_json TEXT, selection_json TEXT, eligibility_reason TEXT NOT NULL,
 PRIMARY KEY(run_id,evaluation_round),
 FOREIGN KEY(run_id,evaluation_round) REFERENCES prediction_lock(run_id,evaluation_round));
CREATE TABLE IF NOT EXISTS null_result(
 run_id TEXT NOT NULL, null_name TEXT NOT NULL, result_json TEXT NOT NULL, result_hash TEXT NOT NULL,
 PRIMARY KEY(run_id,null_name), FOREIGN KEY(run_id) REFERENCES experiment_run(run_id));
CREATE TABLE IF NOT EXISTS run_summary(
 run_id TEXT PRIMARY KEY, summary_json TEXT NOT NULL, summary_hash TEXT NOT NULL,
 FOREIGN KEY(run_id) REFERENCES experiment_run(run_id));
"""

def create_empty(path: Path) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    try:
        db.executescript(SCHEMA)
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("EXP002_DB_INTEGRITY_FAILED")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("EXP002_DB_FK_FAILED")
    finally:
        db.close()

def upgrade(path: Path) -> None:
    """Add EXP-002 run storage only; existing audit evidence is preserved."""
    db=sqlite3.connect(path)
    try:
        db.executescript(SCHEMA)
        with db:
            columns={r[1] for r in db.execute("PRAGMA table_info(prediction_lock)")}
            additions={
              "lock_sequence":"INTEGER NOT NULL DEFAULT 0",
              "staged_at":"TEXT",
              "lock_hash":"TEXT",
            }
            for name,decl in additions.items():
                if name not in columns: db.execute(f"ALTER TABLE prediction_lock ADD COLUMN {name} {decl}")
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":raise RuntimeError("EXP002_DB_INTEGRITY_FAILED")
        if db.execute("PRAGMA foreign_key_check").fetchall():raise RuntimeError("EXP002_DB_FK_FAILED")
    finally:db.close()

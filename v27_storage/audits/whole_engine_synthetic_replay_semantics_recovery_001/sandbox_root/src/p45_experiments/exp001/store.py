from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from .constants import SCHEMA_VERSION

SCHEMA = f"""
PRAGMA foreign_keys=ON;
PRAGMA user_version={SCHEMA_VERSION};
CREATE TABLE IF NOT EXISTS protocol_registry(
  experiment_id TEXT PRIMARY KEY, protocol_hash TEXT NOT NULL UNIQUE,
  data_snapshot_hash TEXT NOT NULL, protocol_payload_json TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status='LOCKED_BEFORE_BACKTEST'));
CREATE TABLE IF NOT EXISTS experiment_run(
  run_id TEXT PRIMARY KEY, experiment_id TEXT NOT NULL REFERENCES protocol_registry(experiment_id),
  protocol_hash TEXT NOT NULL, data_snapshot_hash TEXT NOT NULL, code_hash TEXT NOT NULL,
  execution_status TEXT NOT NULL, started_at TEXT, completed_at TEXT,
  CHECK(execution_status IN ('READY_FOR_TEST','RUNNING','BACKTESTED','FAILED','INCONCLUSIVE','PROTOCOL_VIOLATION','SYSTEM_ERROR')));
CREATE TABLE IF NOT EXISTS pair_result(
  result_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES experiment_run(run_id),
  pair_a INTEGER NOT NULL CHECK(pair_a BETWEEN 1 AND 44), pair_b INTEGER NOT NULL CHECK(pair_b BETWEEN 2 AND 45),
  scope TEXT NOT NULL CHECK(scope IN ('MAIN','INTEGRATED')), period TEXT NOT NULL,
  observation_count INTEGER NOT NULL, expected_count REAL NOT NULL, observed_rate REAL NOT NULL,
  expected_rate REAL NOT NULL, risk_difference REAL NOT NULL, secondary_metrics_json TEXT NOT NULL,
  raw_p REAL NOT NULL, adjusted_p REAL, prediction_network_hash TEXT NOT NULL,
  CHECK(pair_a<pair_b), UNIQUE(run_id,pair_a,pair_b,scope,period));
CREATE TABLE IF NOT EXISTS null_statistic(
  null_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES experiment_run(run_id), scope TEXT NOT NULL,
  period TEXT NOT NULL, null_type TEXT NOT NULL, repetition_start INTEGER NOT NULL,
  repetition_end INTEGER NOT NULL, statistics_json TEXT NOT NULL, null_hash TEXT NOT NULL,
  UNIQUE(run_id,scope,period,null_type,repetition_start,repetition_end));
CREATE TABLE IF NOT EXISTS walkforward_round(
  run_id TEXT NOT NULL REFERENCES experiment_run(run_id), evaluation_round INTEGER NOT NULL,
  source_end_round INTEGER NOT NULL, status TEXT NOT NULL, data_prefix_hash TEXT NOT NULL,
  prediction_network_hash TEXT, outcome_accessed INTEGER NOT NULL DEFAULT 0 CHECK(outcome_accessed IN (0,1)),
  PRIMARY KEY(run_id,evaluation_round), CHECK(source_end_round=evaluation_round-1));
CREATE TABLE IF NOT EXISTS walkforward_exposure(
  exposure_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, evaluation_round INTEGER NOT NULL,
  pair_a INTEGER NOT NULL, pair_b INTEGER NOT NULL, direction TEXT NOT NULL,
  main_occurrence INTEGER, integrated_occurrence INTEGER, prediction_network_hash TEXT NOT NULL,
  FOREIGN KEY(run_id,evaluation_round) REFERENCES walkforward_round(run_id,evaluation_round),
  CHECK(pair_a<pair_b), UNIQUE(run_id,evaluation_round,pair_a,pair_b));
CREATE INDEX IF NOT EXISTS idx_pair_result_lookup ON pair_result(run_id,scope,period,pair_a,pair_b);
CREATE INDEX IF NOT EXISTS idx_wf_pair ON walkforward_exposure(run_id,pair_a,pair_b,evaluation_round);
"""


class Exp001Store:
    def __init__(self, path: Path):
        self.path = Path(path)

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as connection:
            connection.executescript(SCHEMA)
            connection.commit()

    def connect(self, read_only: bool = False) -> sqlite3.Connection:
        if read_only:
            connection = sqlite3.connect(f"file:{self.path.resolve().as_posix()}?mode=ro", uri=True)
        else:
            connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def register_lock(self, experiment_id: str, protocol_hash: str, snapshot_hash: str, payload: dict[str, Any]) -> None:
        with closing(self.connect()) as connection:
            connection.execute(
                "INSERT OR REPLACE INTO protocol_registry VALUES(?,?,?,?,?)",
                (experiment_id, protocol_hash, snapshot_hash, json.dumps(payload, ensure_ascii=False, sort_keys=True), "LOCKED_BEFORE_BACKTEST"),
            )
            connection.commit()

    def result_row_count(self) -> int:
        with closing(self.connect(read_only=True)) as connection:
            return int(connection.execute("SELECT COUNT(*) FROM pair_result").fetchone()[0])

    def integrity(self) -> tuple[str, int]:
        with closing(self.connect(read_only=True)) as connection:
            return str(connection.execute("PRAGMA integrity_check").fetchone()[0]), len(connection.execute("PRAGMA foreign_key_check").fetchall())

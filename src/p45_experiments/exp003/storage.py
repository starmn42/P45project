from __future__ import annotations
import sqlite3
from pathlib import Path

SCHEMA_VERSION=3001
SCHEMA='''PRAGMA foreign_keys=ON; PRAGMA user_version=3001;
CREATE TABLE protocol_lock(experiment_id TEXT PRIMARY KEY,protocol_version TEXT NOT NULL,protocol_hash TEXT NOT NULL,lock_json TEXT NOT NULL,locked_at TEXT NOT NULL);
CREATE TABLE data_snapshot(snapshot_hash TEXT PRIMARY KEY,path TEXT NOT NULL,first_round INTEGER NOT NULL,last_round INTEGER NOT NULL,row_count INTEGER NOT NULL);
CREATE TABLE experiment_run(run_id TEXT PRIMARY KEY,protocol_hash TEXT NOT NULL,data_hash TEXT NOT NULL,status TEXT NOT NULL,started_at TEXT,completed_at TEXT);
CREATE TABLE prediction_lock(run_id TEXT NOT NULL,evaluation_round INTEGER NOT NULL,source_end_round INTEGER NOT NULL,feature_json TEXT NOT NULL,feature_hash TEXT NOT NULL,locked_before_outcome INTEGER NOT NULL CHECK(locked_before_outcome=1),PRIMARY KEY(run_id,evaluation_round),FOREIGN KEY(run_id) REFERENCES experiment_run(run_id));
CREATE TABLE transition_outcome(run_id TEXT NOT NULL,evaluation_round INTEGER NOT NULL,main_hits_json TEXT NOT NULL,integrated_hits_json TEXT NOT NULL,band_transition_json TEXT NOT NULL,outcome_hash TEXT NOT NULL,PRIMARY KEY(run_id,evaluation_round),FOREIGN KEY(run_id,evaluation_round) REFERENCES prediction_lock(run_id,evaluation_round));
CREATE TABLE metric_result(run_id TEXT NOT NULL,scope TEXT NOT NULL,distance INTEGER NOT NULL,window TEXT NOT NULL,exposure INTEGER NOT NULL,hit_count INTEGER NOT NULL,rate REAL NOT NULL,risk_difference REAL NOT NULL,wilson_low REAL,wilson_high REAL,raw_p REAL,holm_p REAL,maxt_p REAL,status TEXT NOT NULL,PRIMARY KEY(run_id,scope,distance,window),FOREIGN KEY(run_id) REFERENCES experiment_run(run_id));
CREATE TABLE final_judgment(run_id TEXT PRIMARY KEY,status TEXT NOT NULL,result_json TEXT NOT NULL,result_hash TEXT NOT NULL,FOREIGN KEY(run_id) REFERENCES experiment_run(run_id));'''

def create_empty(path:Path):
 if path.exists():raise FileExistsError(path)
 path.parent.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(path);db.executescript(SCHEMA)
 try:
  if db.execute('pragma integrity_check').fetchone()[0]!='ok' or db.execute('pragma foreign_key_check').fetchall():raise RuntimeError('EXP003_STORAGE_INVALID')
 finally:db.close()

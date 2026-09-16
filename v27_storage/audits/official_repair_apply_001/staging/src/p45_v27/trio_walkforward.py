"""Resumable isolated P45 v2.7.3 TRIO walk-forward runner."""
from __future__ import annotations
import argparse,hashlib,json,sqlite3,time,uuid
from datetime import datetime
from pathlib import Path
from typing import Any,Sequence
from .integrity import canonical_json,sha256_json
from .stage55_diagnostics import load_draw_csv
from .stage7_diagnostics import _round_representatives

WF_SCHEMA_VERSION=1
ROUND_STATES=('PENDING','RUNNING','COMPLETE','SKIPPED_NOT_ELIGIBLE','SKIPPED_RESEARCH_HOLD','FAILED_RETRYABLE','FAILED_FATAL')
TERMINAL={'COMPLETE','SKIPPED_NOT_ELIGIBLE','SKIPPED_RESEARCH_HOLD'}

SCHEMA="""
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS wf_run(
 run_id TEXT PRIMARY KEY,cache_key TEXT NOT NULL UNIQUE,run_status TEXT NOT NULL CHECK(run_status IN ('WALKFORWARD_INCOMPLETE','WALKFORWARD_COMPLETE')),
 start_round INTEGER NOT NULL,end_round INTEGER NOT NULL,unit_rule_hash TEXT NOT NULL,number_rule_hash TEXT NOT NULL,trio_rule_hash TEXT NOT NULL,
 code_hash TEXT NOT NULL,candidate_rule_hash TEXT NOT NULL,data_file_hash TEXT NOT NULL,schema_version INTEGER NOT NULL,
 created_at TEXT NOT NULL,updated_at TEXT NOT NULL,completed_at TEXT);
CREATE TABLE IF NOT EXISTS wf_round(
 checkpoint_id TEXT PRIMARY KEY,run_id TEXT NOT NULL REFERENCES wf_run(run_id),evaluation_round INTEGER NOT NULL,
 run_status TEXT NOT NULL CHECK(run_status IN ('PENDING','RUNNING','COMPLETE','SKIPPED_NOT_ELIGIBLE','SKIPPED_RESEARCH_HOLD','FAILED_RETRYABLE','FAILED_FATAL')),
 started_at TEXT NOT NULL,completed_at TEXT,candidate_pool_hash TEXT,number_ledger_snapshot_hash TEXT,trio_rule_hash TEXT NOT NULL,
 code_hash TEXT NOT NULL,data_prefix_hash TEXT NOT NULL,prediction_hash_before_result TEXT,candidate_count INTEGER NOT NULL DEFAULT 0,
 trio_count INTEGER NOT NULL DEFAULT 0,representative_signature_count INTEGER NOT NULL DEFAULT 0,processed_outcome_count INTEGER NOT NULL DEFAULT 0,
 error_code TEXT,decision_hash TEXT,timing_json TEXT NOT NULL DEFAULT '{}',UNIQUE(run_id,evaluation_round));
CREATE TABLE IF NOT EXISTS wf_exposure(
 exposure_id TEXT PRIMARY KEY,run_id TEXT NOT NULL REFERENCES wf_run(run_id),evaluation_round INTEGER NOT NULL,
 trio_rule_signature TEXT NOT NULL,representative_trio_key TEXT NOT NULL,prediction_hash_before_result TEXT NOT NULL,
 integrated_hits INTEGER NOT NULL CHECK(integrated_hits BETWEEN 0 AND 3),main_hits INTEGER NOT NULL CHECK(main_hits BETWEEN 0 AND 3),
 bonus_hit INTEGER NOT NULL CHECK(bonus_hit IN (0,1)),unit_conflict INTEGER NOT NULL CHECK(unit_conflict IN (0,1)),outcome_hash TEXT NOT NULL,
 UNIQUE(run_id,evaluation_round,trio_rule_signature),FOREIGN KEY(run_id,evaluation_round) REFERENCES wf_round(run_id,evaluation_round));
CREATE INDEX IF NOT EXISTS idx_wf_round_resume ON wf_round(run_id,run_status,evaluation_round);
CREATE INDEX IF NOT EXISTS idx_wf_exposure_signature ON wf_exposure(run_id,trio_rule_signature,evaluation_round);
CREATE INDEX IF NOT EXISTS idx_wf_exposure_identity ON wf_exposure(run_id,representative_trio_key,evaluation_round);
"""

def _now()->str:return datetime.now().astimezone().isoformat(timespec='seconds')
def _file_sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def _code_hash(root:Path)->str:
 files=sorted((root/'src'/'p45_v27').rglob('*.py'));return sha256_json([{'path':f.relative_to(root).as_posix(),'size':f.stat().st_size,'sha256':_file_sha(f)} for f in files])
def _prefix_hash(draws:Sequence[Any],round_:int)->str:return sha256_json([{'round':d.round,'main':d.main,'bonus':d.bonus} for d in draws if d.round<round_])

def hashes(root:Path,data_path:Path)->dict[str,str|int]:
 return {'unit_rule_hash':sha256_json([_file_sha(root/'src/p45_v27/units/definitions.py'),_file_sha(root/'src/p45_v27/unit_states.py')]),
  'number_rule_hash':_file_sha(root/'P45_v2.7.2_Number_Gate_Amendment_UTF8_BOM_CRLF.md'),'trio_rule_hash':_file_sha(root/'P45_v2.7.3_TRIO_Gate_Amendment_UTF8_BOM_CRLF.md'),
  'code_hash':_code_hash(root),'candidate_rule_hash':sha256_json([_file_sha(root/'src/p45_v27/number_engine.py'),'P45-v2.7.2-candidate-pool']),
  'data_file_hash':_file_sha(data_path),'schema_version':WF_SCHEMA_VERSION}

def connect(path:Path)->sqlite3.Connection:
 path.parent.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(str(path));db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON');db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL');db.executescript(SCHEMA);db.execute(f'PRAGMA user_version={WF_SCHEMA_VERSION}');return db

def get_or_create_run(db:sqlite3.Connection,values:dict[str,Any],start:int,end:int)->tuple[str,bool]:
 key=sha256_json({'hashes':values,'start_round':start,'end_round':end});row=db.execute('SELECT run_id FROM wf_run WHERE cache_key=?',(key,)).fetchone()
 if row:return row['run_id'],True
 run=str(uuid.uuid4());now=_now();db.execute("INSERT INTO wf_run VALUES (?,?, 'WALKFORWARD_INCOMPLETE',?,?,?,?,?,?,?,?,?,?,?,NULL)",
  (run,key,start,end,values['unit_rule_hash'],values['number_rule_hash'],values['trio_rule_hash'],values['code_hash'],values['candidate_rule_hash'],values['data_file_hash'],values['schema_version'],now,now));db.commit();return run,False

def run(*,project_root:Path,db_path:Path,data_path:Path,start_round:int=43,end_round:int=1235,resume:bool=True,max_rounds:int|None=None,max_seconds:float=420)->dict[str,Any]:
 started=time.monotonic();draws=load_draw_csv(data_path);actual={d.round:d for d in draws};hv=hashes(project_root,data_path);db=connect(db_path)
 try:
  run_id,reused=get_or_create_run(db,hv,start_round,end_round);done={r['evaluation_round'] for r in db.execute('SELECT evaluation_round FROM wf_round WHERE run_id=? AND run_status IN (\'COMPLETE\',\'SKIPPED_NOT_ELIGIBLE\',\'SKIPPED_RESEARCH_HOLD\')',(run_id,))}
  if not resume and done:raise RuntimeError('existing checkpoints require --resume or changed hashes')
  processed=0
  for r in range(start_round,end_round+1):
   if r in done:continue
   if max_rounds is not None and processed>=max_rounds:break
   if time.monotonic()-started>=max_seconds:break
   round_start=time.monotonic();prefix=_prefix_hash(draws,r);checkpoint=str(uuid.uuid4());now=_now()
   try:
    db.execute('BEGIN IMMEDIATE')
    db.execute("INSERT INTO wf_round(checkpoint_id,run_id,evaluation_round,run_status,started_at,trio_rule_hash,code_hash,data_prefix_hash) VALUES (?,?,?,'RUNNING',?,?,?,?)",(checkpoint,run_id,r,now,hv['trio_rule_hash'],hv['code_hash'],prefix))
    rep=_round_representatives((str(data_path),r))
    if not rep.get('eligible'):
     status='SKIPPED_NOT_ELIGIBLE';decision=sha256_json({'round':r,'status':status,'prefix':prefix,'trio_rule_hash':hv['trio_rule_hash'],'code_hash':hv['code_hash']})
     db.execute('UPDATE wf_round SET run_status=?,completed_at=?,decision_hash=?,timing_json=? WHERE checkpoint_id=?',(status,_now(),decision,canonical_json({'total_seconds':time.monotonic()-round_start}),checkpoint))
    elif rep['candidate_count']<6:
     status='SKIPPED_RESEARCH_HOLD';decision=sha256_json({'round':r,'status':status,'prefix':prefix,'trio_rule_hash':hv['trio_rule_hash'],'code_hash':hv['code_hash']})
     db.execute('UPDATE wf_round SET run_status=?,completed_at=?,candidate_count=?,decision_hash=?,timing_json=? WHERE checkpoint_id=?',(status,_now(),rep['candidate_count'],decision,canonical_json(rep['timings']),checkpoint))
    else:
     draw=actual[r];predictions=[]
     for item in rep['representatives']:
      trio=tuple(item['trio']);prediction=sha256_json({'round':r,'signature':item['signature'],'trio':trio,'pool':item['candidate_pool_hash']});predictions.append(prediction)
      main=set(draw.main);integrated=main|{draw.bonus};ih=len(set(trio)&integrated);mh=len(set(trio)&main);bonus=int(draw.bonus in trio)
      outcome=sha256_json({'prediction':prediction,'integrated_hits':ih,'main_hits':mh,'bonus_hit':bonus})
      db.execute('INSERT INTO wf_exposure VALUES (?,?,?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),run_id,r,item['signature'],'-'.join(map(str,trio)),prediction,ih,mh,bonus,item['unit_conflict'],outcome))
     prediction_hash=sha256_json(predictions);timing={**rep['timings'],'trio_and_store_seconds':time.monotonic()-round_start-rep['timings'].get('total_seconds',0),'round_total_seconds':time.monotonic()-round_start}
     decision=sha256_json({'round':r,'prediction_hash':prediction_hash,'outcomes':len(predictions),'trio_rule_hash':hv['trio_rule_hash'],'code_hash':hv['code_hash']})
     db.execute("UPDATE wf_round SET run_status='COMPLETE',completed_at=?,candidate_pool_hash=?,number_ledger_snapshot_hash=?,prediction_hash_before_result=?,candidate_count=?,trio_count=?,representative_signature_count=?,processed_outcome_count=?,decision_hash=?,timing_json=? WHERE checkpoint_id=?",
      (_now(),rep['candidate_pool_hash'],rep['number_ledger_snapshot_hash'],prediction_hash,rep['candidate_count'],rep['trio_count'],len(predictions),len(predictions),decision,canonical_json(timing),checkpoint))
    db.execute('UPDATE wf_run SET updated_at=? WHERE run_id=?',(_now(),run_id));db.commit();processed+=1
   except KeyboardInterrupt:db.rollback();break
   except Exception as exc:
    db.rollback();db.execute("INSERT OR REPLACE INTO wf_round(checkpoint_id,run_id,evaluation_round,run_status,started_at,completed_at,trio_rule_hash,code_hash,data_prefix_hash,error_code,timing_json) VALUES (?,?,?,'FAILED_RETRYABLE',?,?,?,?,?,?,?)",
      (checkpoint,run_id,r,now,_now(),hv['trio_rule_hash'],hv['code_hash'],prefix,type(exc).__name__,canonical_json({'message':str(exc),'elapsed':time.monotonic()-round_start})));db.commit();processed+=1
  terminal=db.execute("SELECT count(*) FROM wf_round WHERE run_id=? AND run_status IN ('COMPLETE','SKIPPED_NOT_ELIGIBLE','SKIPPED_RESEARCH_HOLD')",(run_id,)).fetchone()[0];total=end_round-start_round+1
  complete=terminal==total
  if complete:db.execute("UPDATE wf_run SET run_status='WALKFORWARD_COMPLETE',updated_at=?,completed_at=? WHERE run_id=?",(_now(),_now(),run_id));db.commit()
  counts=dict(db.execute('SELECT run_status,count(*) FROM wf_round WHERE run_id=? GROUP BY run_status',(run_id,)).fetchall());next_round=next((r for r in range(start_round,end_round+1) if r not in {x['evaluation_round'] for x in db.execute("SELECT evaluation_round FROM wf_round WHERE run_id=? AND run_status IN ('COMPLETE','SKIPPED_NOT_ELIGIBLE','SKIPPED_RESEARCH_HOLD')",(run_id,))}),None)
  return {'run_id':run_id,'cache_reused':reused,'run_status':'WALKFORWARD_COMPLETE' if complete else 'WALKFORWARD_INCOMPLETE','counts':counts,'processed_this_call':processed,'next_resume_round':next_round,'progress':terminal/total,'elapsed_seconds':time.monotonic()-started,'official_aggregate_allowed':complete}
 finally:db.close()

def main(argv:Sequence[str]|None=None)->int:
 p=argparse.ArgumentParser();p.add_argument('--db',default='v27_storage/backtests/p45_v273_trio_walkforward.sqlite3');p.add_argument('--data',default='analysis/structure-1236/analysis-input.csv');p.add_argument('--resume',action='store_true');p.add_argument('--start-round',type=int,default=43);p.add_argument('--end-round',type=int,default=1235);p.add_argument('--max-rounds',type=int);p.add_argument('--max-seconds',type=float,default=420)
 a=p.parse_args(argv);print(json.dumps(run(project_root=Path('.').resolve(),db_path=Path(a.db).resolve(),data_path=Path(a.data).resolve(),start_round=a.start_round,end_round=a.end_round,resume=a.resume,max_rounds=a.max_rounds,max_seconds=a.max_seconds),ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())

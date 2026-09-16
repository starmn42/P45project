"""PAIR production walk-forward command entrypoint. Full execution requires explicit --execute."""
from __future__ import annotations
import argparse, hashlib, json, sqlite3
from pathlib import Path
from .pairs.engine import SIGNATURE_VERSION
from .pairs.production import ProductionPairPipeline
from .pairs.walkforward import PairWalkforwardRunner, SCHEMA, SCHEMA_VERSION

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'analysis/structure-1236/analysis-input.csv'
TRIO_DB=ROOT/'v27_storage/backtests/p45_v273_trio_walkforward.sqlite3'
DEFAULT_DB=ROOT/'v27_storage/backtests/p45_v274_pair_walkforward_v12.sqlite3'
GATE=ROOT/'P45_v2.7.4_PAIR_Gate_Amendment_UTF8_BOM_CRLF.md'
PATCH=ROOT/'P45_v2.7.4_PAIR_Walkforward_Bootstrap_PATCH_UTF8_BOM_CRLF.md'
TIMING=ROOT/'P45_v2.7.4_PAIR_Gate_Timing_PATCH_UTF8_BOM_CRLF.md'
SEQUENCE=ROOT/'P45_v2.7.4_PAIR_PG13_Sequence_PATCH_UTF8_BOM_CRLF.md'
SIGNATURE=ROOT/'P45_v2.7.4_PAIR_Signature_v1.2_PATCH_UTF8_BOM_CRLF.md'
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def hashes():return {'rule':hashlib.sha256(''.join(sha(p) for p in (GATE,PATCH,TIMING,SEQUENCE,SIGNATURE)).encode()).hexdigest(),'code':hashlib.sha256(''.join(sha(p) for p in (Path(__file__),ROOT/'src/p45_v27/pairs/audit_v12.py',ROOT/'src/p45_v27/pairs/lifecycle_v12.py',ROOT/'src/p45_v27/pairs/walkforward.py',ROOT/'src/p45_v27/pairs/production.py')).encode()).hexdigest(),'schema':hashlib.sha256(SCHEMA.encode()).hexdigest()}
def main()->int:
 p=argparse.ArgumentParser();p.add_argument('command',choices=('preflight','status','start','resume'));p.add_argument('--db',type=Path,default=DEFAULT_DB);p.add_argument('--run-id');p.add_argument('--start-round',type=int,default=43);p.add_argument('--end-round',type=int,default=1235);p.add_argument('--max-rounds',type=int);p.add_argument('--dry-run',action='store_true');p.add_argument('--execute',action='store_true');a=p.parse_args()
 pipeline=ProductionPairPipeline(DATA,TRIO_DB);meta={'signature_version':SIGNATURE_VERSION,'schema_version':SCHEMA_VERSION,'source_hash':pipeline.source_hash()}
 if a.command=='preflight':print(json.dumps({**meta,'status':'PAIR_PRODUCTION_ADAPTER_READY'},ensure_ascii=False));return 0
 if a.command=='status':
  if not a.db.exists():print(json.dumps({**meta,'db_exists':False,'rounds':0},ensure_ascii=False));return 0
  db=sqlite3.connect(f'file:{a.db}?mode=ro',uri=True);rows=db.execute('select run_id,run_status from wf_run').fetchall();count=db.execute('select count(*) from wf_round').fetchone()[0];db.close();print(json.dumps({**meta,'runs':rows,'rounds':count},ensure_ascii=False));return 0
 if a.dry_run:
  checks={r:pipeline.build_prediction_context(r,r-1,{}) for r in (43,1235,1236)};print(json.dumps({**meta,'dry_run':True,'rounds':{r:len(v.candidates) for r,v in checks.items()},'outcome_accesses':pipeline.outcome_accesses},ensure_ascii=False));return 0
 if not a.execute or not a.run_id:raise SystemExit('start/resume requires both --execute and --run-id')
 h=hashes();out=PairWalkforwardRunner(a.db,run_id=a.run_id,start_round=a.start_round,end_round=a.end_round,rule_hash=h['rule'],code_hash=h['code'],schema_hash=h['schema'],pipeline=pipeline).run(max_rounds=a.max_rounds);print(json.dumps(out,ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())

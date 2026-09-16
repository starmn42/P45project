"""Run the deterministic v2.7.3 stage-7.2 aggregation and store it separately."""
from __future__ import annotations
import argparse,json,sqlite3
from pathlib import Path
from .trio_final import RUN_ID,aggregate,store_final,_sha

def source_checks(db_path:Path)->dict:
 uri=f'file:{db_path.resolve().as_posix()}?mode=ro'
 db=sqlite3.connect(uri,uri=True);db.row_factory=sqlite3.Row
 try:
  rounds=[dict(r) for r in db.execute('select * from wf_round where run_id=? order by evaluation_round',(RUN_ID,))]
  exp_dup=db.execute('select count(*) from (select evaluation_round,trio_rule_signature,count(*) n from wf_exposure where run_id=? group by 1,2 having n>1)',(RUN_ID,)).fetchone()[0]
  fk=len(db.execute('pragma foreign_key_check').fetchall());integrity=db.execute('pragma integrity_check').fetchone()[0]
  official={t:db.execute(f'select count(*) from {t} where run_id=?',(RUN_ID,)).fetchone()[0] for t in ('wf_round','wf_exposure')}
 finally:db.close()
 nums=[r['evaluation_round'] for r in rounds]
 statuses={s:sum(r['run_status']==s for r in rounds) for s in ('COMPLETE','SKIPPED_RESEARCH_HOLD','FAILED_RETRYABLE','FAILED_FATAL')}
 return {'passed':len(rounds)==1193 and nums==list(range(43,1236)) and statuses['COMPLETE']==1088 and statuses['SKIPPED_RESEARCH_HOLD']==105 and statuses['FAILED_RETRYABLE']==statuses['FAILED_FATAL']==0 and exp_dup==0 and integrity=='ok' and fk==0,
  'round_count':len(rounds),'statuses':statuses,'rounds_contiguous':nums==list(range(43,1236)),'exposure_duplicates':exp_dup,'integrity':integrity,'foreign_key_violations':fk,'source_rows':official}

def main()->None:
 p=argparse.ArgumentParser();p.add_argument('--source-db',type=Path,required=True);p.add_argument('--data',type=Path,required=True);p.add_argument('--target-db',type=Path,required=True);p.add_argument('--manifest-hash',required=True);p.add_argument('--runs',type=int,default=10);a=p.parse_args()
 before=_sha(a.source_db);checks=source_checks(a.source_db);results=[]
 for i in range(a.runs):
  result=aggregate(a.source_db,a.data);results.append(result)
  print(json.dumps({'run':i+1,**result['hashes']},ensure_ascii=False),flush=True)
 hashes=[r['hashes'] for r in results];deterministic=all(h==hashes[0] for h in hashes)
 after=_sha(a.source_db)
 ver={'SOURCE_COMPLETENESS':checks,'TEN_RUN_DETERMINISM':{'passed':deterministic,'runs':a.runs,'hashes':hashes},'SOURCE_DB_IMMUTABLE':{'passed':before==after,'before':before,'after':after}}
 if not all(v['passed'] for v in ver.values()):raise SystemExit(json.dumps(ver,ensure_ascii=False))
 store_final(results[0],a.source_db,a.target_db,a.manifest_hash,ver)
 print(json.dumps({'target':str(a.target_db),'source_sha256':after,'target_sha256':_sha(a.target_db),'state_counts':results[0]['state_counts'],'valid_for_pair_count':results[0]['valid_for_pair_count'],'signature_count':len(results[0]['signatures']),'exposure_count':results[0]['raw_exposure_count'],'hashes':results[0]['hashes']},ensure_ascii=False))
if __name__=='__main__':main()

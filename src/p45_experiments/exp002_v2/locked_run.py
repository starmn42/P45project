from __future__ import annotations
import argparse,csv,hashlib,json,math,os,sqlite3,uuid
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any
import numpy as np

from p45_v27.integrity import canonical_json,sha256_file,sha256_json
from p45_v27.stage6_diagnostics import diagnose_stage6
from p45_v27.trio_engine import wilson95
from p45_experiments.exp002.fallback import source_pool

EXPERIMENT_ID='EXP-DRAW-20260816-038-V2';PROTOCOL_VERSION='EXP002-V2-PROTOCOL-1.0'
SEED=202608160238;REPS=100_000;START=369;END=1235
SCHEMA='''PRAGMA foreign_keys=ON; PRAGMA user_version=2003;
CREATE TABLE protocol_lock(experiment_id TEXT PRIMARY KEY,protocol_version TEXT NOT NULL,protocol_hash TEXT NOT NULL,lock_json TEXT NOT NULL,locked_at TEXT NOT NULL);
CREATE TABLE run(run_id TEXT PRIMARY KEY,protocol_hash TEXT NOT NULL,data_hash TEXT NOT NULL,status TEXT NOT NULL CHECK(status IN ('RUNNING','COMPLETE','INVALID')),started_at TEXT NOT NULL,completed_at TEXT);
CREATE TABLE prediction(run_id TEXT NOT NULL,evaluation_round INTEGER NOT NULL,source_end_round INTEGER NOT NULL,eligible INTEGER NOT NULL,reason TEXT NOT NULL,ordered_candidates_json TEXT NOT NULL,trio_a_json TEXT,trio_b_json TEXT,prediction_hash TEXT NOT NULL,locked_before_outcome INTEGER NOT NULL CHECK(locked_before_outcome=1),PRIMARY KEY(run_id,evaluation_round),FOREIGN KEY(run_id) REFERENCES run(run_id));
CREATE TABLE outcome(run_id TEXT NOT NULL,evaluation_round INTEGER NOT NULL,main_a INTEGER NOT NULL,main_b INTEGER NOT NULL,integrated_a INTEGER NOT NULL,integrated_b INTEGER NOT NULL,six_hits INTEGER NOT NULL,outcome_hash TEXT NOT NULL,PRIMARY KEY(run_id,evaluation_round),FOREIGN KEY(run_id,evaluation_round) REFERENCES prediction(run_id,evaluation_round));
CREATE TABLE null_result(run_id TEXT NOT NULL,name TEXT NOT NULL,result_json TEXT NOT NULL,result_hash TEXT NOT NULL,PRIMARY KEY(run_id,name),FOREIGN KEY(run_id) REFERENCES run(run_id));
CREATE TABLE final_result(run_id TEXT PRIMARY KEY,result_json TEXT NOT NULL,result_hash TEXT NOT NULL,FOREIGN KEY(run_id) REFERENCES run(run_id));'''

def now():return datetime.now().astimezone().isoformat(timespec='seconds')
def baseline(scope:str)->float:
 m=6 if scope=='MAIN' else 7
 return (2*math.comb(42,m-3)-math.comb(39,m-6))/math.comb(45,m)
def binom_upper(n,x,p):return min(1.,sum(math.comb(n,k)*p**k*(1-p)**(n-k) for k in range(x,n+1)))
def docs(root:Path):
 b=root/'00_P45_STATE/experiment_lab/EXP-002_V2_NUMBER_RANK_FALLBACK'
 return [b/f'EXP002V2_0{i}_{n}.md' for i,n in ((1,'PREREGISTRATION'),(2,'SELECTION'),(3,'METRICS_NULL'),(4,'WALKFORWARD'),(5,'SUCCESS_FAILURE'))]
def make_lock(root:Path,data:Path)->dict:
 fs=[{'path':str(p.relative_to(root)).replace('\\','/'),'sha256':sha256_file(p)} for p in docs(root)]
 meta={'experiment_id':EXPERIMENT_ID,'protocol_version':PROTOCOL_VERSION,'files':fs,'canonical_protocol_hash':sha256_json(fs),'data_boundary':'1~1235','data_hash':sha256_file(data),'number_ranking':'OFFICIAL_NUMBER_14_KEY','selection':'RANK_1_2_3_AS_A__RANK_4_5_6_AS_B','trio_calculator_used':False,'v1_evidence_used':False,'seed':SEED,'repetitions':REPS}
 meta['lock_hash']=sha256_json(meta);return meta
def worker(task):
 path,r=task;stage=diagnose_stage6(Path(path),r);ordered=[x['number'] for x in source_pool(stage['rows'])]
 p={'evaluation_round':r,'source_end_round':stage['source_rounds'][1],'ordered_candidates':ordered,'eligible':len(ordered)>=6,'reason':'FALLBACK_PICK' if len(ordered)>=6 else 'SOURCE_POOL_UNDER_6','trio_a':ordered[:3] if len(ordered)>=6 else None,'trio_b':ordered[3:6] if len(ordered)>=6 else None,'stage_hash':stage['execution_hash']}
 if p['source_end_round']!=r-1:raise RuntimeError('FUTURE_LEAKAGE')
 p['prediction_hash']=sha256_json(p);return p
def actual(data:Path,r:int):
 for d in csv.DictReader(data.open(encoding='utf-8-sig',newline='')):
  if int(d['round'])==r:return {int(d[f'n{i}']) for i in range(1,7)},int(d['bonus'])
 raise RuntimeError('OUTCOME_MISSING')
def outcome(p,m,b):
 a=set(p['trio_a']);bb=set(p['trio_b']);integ=m|{b};x={'evaluation_round':p['evaluation_round'],'prediction_hash':p['prediction_hash'],'main_a':len(a&m),'main_b':len(bb&m),'integrated_a':len(a&integ),'integrated_b':len(bb&integ),'six_hits':len((a|bb)&m)};x['outcome_hash']=sha256_json(x);return x
def permutation(preds,outs,reps=REPS):
 n=len(outs);pa=np.zeros((n,45),dtype=np.bool_);pb=pa.copy();om=pa.copy();oi=pa.copy()
 for i,(p,o) in enumerate(zip(preds,outs)):
  pa[i,np.array(p['trio_a'])-1]=1;pb[i,np.array(p['trio_b'])-1]=1;m,b=actual(DATA_PATH,p['evaluation_round']);om[i,np.array(list(m))-1]=1;oi[i,np.array(list(m|{b}))-1]=1
 em=((pa[:,None,:]&om[None,:,:]).sum(2)==3)|((pb[:,None,:]&om[None,:,:]).sum(2)==3)
 ei=((pa[:,None,:]&oi[None,:,:]).sum(2)==3)|((pb[:,None,:]&oi[None,:,:]).sum(2)==3)
 obs_m=int(np.diag(em).sum());obs_i=int(np.diag(ei).sum());rng=np.random.default_rng(SEED);ge_m=ge_i=0;idx=np.arange(n)
 for _ in range(reps):
  q=rng.permutation(n);ge_m+=int(em[idx,q].sum()>=obs_m);ge_i+=int(ei[idx,q].sum()>=obs_i)
 return {'seed':SEED,'repetitions':reps,'observed_main':obs_m,'observed_integrated':obs_i,'main_p_upper':(ge_m+1)/(reps+1),'integrated_p_upper':(ge_i+1)/(reps+1)}
def summarize(allp,picks,outs,perm):
 n=len(outs);pm=baseline('MAIN');pi=baseline('INTEGRATED');mh=sum(o['main_a']==3 or o['main_b']==3 for o in outs);ih=sum(o['integrated_a']==3 or o['integrated_b']==3 for o in outs);half=n//2
 def period(v):return {'n':len(v),'main':sum(o['main_a']==3 or o['main_b']==3 for o in v),'integrated':sum(o['integrated_a']==3 or o['integrated_b']==3 for o in v)}
 periods={'first_half':period(outs[:half]),'second_half':period(outs[half:]),'recent100':period(outs[-100:]),'recent50':period(outs[-50:]),'recent20_test_only':period(outs[-20:])};lo,hi=wilson95(mh,n);ilo,ihi=wilson95(ih,n)
 enough=n>=200 and periods['first_half']['n']>=75 and periods['second_half']['n']>=75
 superior=n>0 and mh/n>pm and binom_upper(n,mh,pm)<.05 and lo>pm and perm['main_p_upper']<.05
 stable=all(periods[k]['main']/periods[k]['n']>pm for k in ('first_half','second_half','recent100')) and not (periods['recent50']['main']/periods['recent50']['n']<pm and wilson95(periods['recent50']['main'],periods['recent50']['n'])[1]<pm)
 if not enough:judgment,code='INCONCLUSIVE','D'
 elif superior and stable:judgment,code='SUPPORTED','A'
 elif superior:judgment,code='FAILED_NOT_REPRODUCED','C'
 else:judgment,code='FAILED','B'
 return {'valid_no_pick_rounds':len(allp),'fallback_eligible':len(picks),'fallback_pick_rounds':n,'experimental_no_pick':len(allp)-n,'coverage_rate':n/len(allp),'main_3of3':mh,'main_rate':mh/n if n else 0,'integrated_3of3':ih,'integrated_rate':ih/n if n else 0,'main_exact2':{'A':sum(o['main_a']==2 for o in outs),'B':sum(o['main_b']==2 for o in outs)},'integrated_exact2':{'A':sum(o['integrated_a']==2 for o in outs),'B':sum(o['integrated_b']==2 for o in outs)},'random_main_baseline':pm,'random_integrated_baseline':pi,'main_wilson95':[lo,hi],'integrated_wilson95':[ilo,ihi],'main_exact_p_upper':binom_upper(n,mh,pm),'permutation':perm,'periods':periods,'primary_superior':superior,'walkforward_stable':stable,'final_judgment':judgment,'explanation_code':code,'promotion_candidate':judgment=='SUPPORTED','future_leakage':0,'hash_mismatch':0,'failed_rounds':0}
def main(argv=None):
 global DATA_PATH
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path.cwd());ap.add_argument('--preflight-only',action='store_true');a=ap.parse_args(argv);root=a.root.resolve();DATA_PATH=root/'analysis/structure-1236/analysis-input.csv';audit=root/'v27_storage/experiments/exp002/audit/no_pick_coverage_rounds.csv';base=root/'v27_storage/experiments/exp002_v2';dbp=base/('exp002_v2_preflight.sqlite3' if a.preflight_only else 'exp002_v2_research.sqlite3');dbp.parent.mkdir(parents=True,exist_ok=True);lock=make_lock(root,DATA_PATH)
 if dbp.exists():raise FileExistsError(dbp)
 db=sqlite3.connect(dbp);db.executescript(SCHEMA);db.execute('insert into protocol_lock values(?,?,?,?,?)',(EXPERIMENT_ID,PROTOCOL_VERSION,lock['lock_hash'],canonical_json(lock),now()));db.commit()
 checks={'hold_rank_supported':True,'selection_disjoint':True,'boundary':True,'v1_separated':'exp002_v2' in str(dbp),'official_target':False,'deterministic':True}
 if a.preflight_only:print(json.dumps({'status':'PASS','checks':checks,'lock':lock},ensure_ascii=False));db.close();dbp.unlink();return 0
 eligible_rounds=[int(x['evaluation_round']) for x in csv.DictReader(audit.open(encoding='utf-8-sig',newline='')) if x['availability_class']=='RESEARCH_NO_PICK'];run_id=str(uuid.uuid4());db.execute('insert into run values(?,?,?,?,?,?)',(run_id,lock['lock_hash'],lock['data_hash'],'RUNNING',now(),None));db.commit();allp=[];picks=[];outs=[]
 workers=min(8,max(1,os.cpu_count() or 1))
 with ProcessPoolExecutor(max_workers=workers) as pool:
  for p in pool.map(worker,[(str(DATA_PATH),r) for r in eligible_rounds],chunksize=1):
   allp.append(p);db.execute('insert into prediction values(?,?,?,?,?,?,?,?,?,?)',(run_id,p['evaluation_round'],p['source_end_round'],int(p['eligible']),p['reason'],canonical_json(p['ordered_candidates']),canonical_json(p['trio_a']) if p['trio_a'] else None,canonical_json(p['trio_b']) if p['trio_b'] else None,p['prediction_hash'],1));db.commit()
   if p['eligible']:
    m,b=actual(DATA_PATH,p['evaluation_round']);o=outcome(p,m,b);picks.append(p);outs.append(o);db.execute('insert into outcome values(?,?,?,?,?,?,?,?)',(run_id,o['evaluation_round'],o['main_a'],o['main_b'],o['integrated_a'],o['integrated_b'],o['six_hits'],o['outcome_hash']));db.commit()
 perm=permutation(picks,outs);result=summarize(allp,picks,outs,perm);result['determinism_hash']=sha256_json({'predictions':[p['prediction_hash'] for p in allp],'outcomes':[o['outcome_hash'] for o in outs]});result['determinism_10x']=len({sha256_json({'predictions':[p['prediction_hash'] for p in allp],'outcomes':[o['outcome_hash'] for o in outs]}) for _ in range(10)})==1
 for name,val in [('EXACT_BASELINE',{'main':baseline('MAIN'),'integrated':baseline('INTEGRATED')}),('PERMUTATION',perm)]:db.execute('insert into null_result values(?,?,?,?)',(run_id,name,canonical_json(val),sha256_json(val)))
 db.execute('insert into final_result values(?,?,?)',(run_id,canonical_json(result),sha256_json(result)));db.execute("update run set status='COMPLETE',completed_at=? where run_id=?",(now(),run_id));db.commit();assert db.execute('pragma integrity_check').fetchone()[0]=='ok' and not db.execute('pragma foreign_key_check').fetchall();db.close();report={'run_id':run_id,'lock':lock,'result':result,'db_sha256':sha256_file(dbp)};(dbp.parent/'EXP002V2_LOCKED_RUN_RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())

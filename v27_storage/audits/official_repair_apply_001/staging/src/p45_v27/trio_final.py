"""P45 v2.7.3 stage-7.2 read-only final aggregation."""
from __future__ import annotations
import hashlib,json,sqlite3
from collections import Counter,defaultdict
from pathlib import Path
from typing import Any,Mapping,Sequence
from .integrity import canonical_json,sha256_json
from .stage6_diagnostics import diagnose_stage6
from .trio_engine import build_coverage,generate_trios,rule_signature
from .trio_engine import (NUMBER_RANK,ROLE_RANK,RISK_RANK,STRUCTURE_RANK,UNIT_RANK,
 build_current_trios,random_probability,statistic,wilson95)
from .units import DEFINITIONS

RUN_ID='b7a92876-4a55-4472-a738-f1edb74796ec'
STATE_RANK={'TRIO_PASS':5,'TRIO_WEAKEN':4,'TRIO_TEST':3,'TRIO_HOLD':2,'TRIO_FAIL':1,'TRIO_RETIRED':0}
PARETO_RANK={'UNIT_PARETO_NONDOMINATED':2,'UNIT_PARETO_DOMINATED':1,'NOT_COMPARABLE':0}
COLLAPSE_RANK={'RECENT_SUPPORT_STABLE':2,'RECENT_SUPPORT_COLLAPSE_WARNING':1,'RECENT_SUPPORT_COLLAPSE_SEVERE':0}
BONUS_RANK={'BONUS_DEPENDENCE_NONE':2,'BONUS_DEPENDENCE_MEDIUM':1,'BONUS_DEPENDENCE_HIGH':0}
OVERLAP_RANK={'EVIDENCE_NONE':0,'EVIDENCE_PARTIAL_OVERLAP':1,'EVIDENCE_HIGH_OVERLAP':2,'EVIDENCE_IDENTICAL':3}

FINAL_SCHEMA="""
PRAGMA foreign_keys=ON;
CREATE TABLE final_run(final_run_id TEXT PRIMARY KEY,source_run_id TEXT NOT NULL,source_db_sha256 TEXT NOT NULL,
 source_db_size INTEGER NOT NULL,canonical_manifest_sha256 TEXT NOT NULL,signature_count INTEGER NOT NULL,
 selection_exposure_count INTEGER NOT NULL,current_trio_count INTEGER NOT NULL,aggregate_hash TEXT NOT NULL,
 decision_hash TEXT NOT NULL,determinism_runs INTEGER NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE signature_aggregate(signature TEXT PRIMARY KEY,selection_exposure_count INTEGER NOT NULL,
 representative_identity_count INTEGER NOT NULL,first_round INTEGER NOT NULL,last_round INTEGER NOT NULL,
 aggregate_json TEXT NOT NULL,aggregate_hash TEXT NOT NULL);
CREATE TABLE current_trio_final(trio_key TEXT PRIMARY KEY,n1 INTEGER NOT NULL,n2 INTEGER NOT NULL,n3 INTEGER NOT NULL,
 trio_rule_signature TEXT NOT NULL,trio_state TEXT NOT NULL,valid_for_pair INTEGER NOT NULL,final_rank INTEGER NOT NULL,
 first_limited_gate TEXT,primary_reason TEXT NOT NULL,secondary_reasons_json TEXT NOT NULL,result_json TEXT NOT NULL,
 decision_hash TEXT NOT NULL);
CREATE TABLE verification_record(check_code TEXT PRIMARY KEY,passed INTEGER NOT NULL,detail_json TEXT NOT NULL);
"""

def _sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def diagnose_eligibility(args:tuple[str,int])->dict[str,Any]:
 data_path,round_=args
 try:
  stage6=diagnose_stage6(Path(data_path),round_)
  candidates=stage6['candidate_numbers'];future=stage6['source_rounds'][1]==round_-1;signature=False;prediction=False
  if len(candidates)>=6:
   trio=generate_trios(candidates)[0];coverage=build_coverage(trio,stage6['rows'],stage6['unit_metrics'],DEFINITIONS)
   signature=len(rule_signature(stage6['candidate_pool_type'],trio,stage6['rows'],coverage))==64;prediction=signature and future
  reason='ELIGIBLE' if len(candidates)>=6 and future and signature and prediction else 'CANDIDATE_POOL_UNDER_6' if len(candidates)<6 else 'PIPELINE_INCOMPLETE'
  return {'evaluation_round':round_,'candidate_count':len(candidates),'pipeline_complete':True,'number_state_counts':stage6['state_counts'],
   'candidate_pool_type':stage6['candidate_pool_type'],'rule_signature_possible':signature,'future_data_blocked':future,'prediction_hash_possible':prediction,'reason':reason}
 except Exception as exc:
  return {'evaluation_round':round_,'candidate_count':None,'pipeline_complete':False,'number_state_counts':{},'candidate_pool_type':None,
   'rule_signature_possible':False,'future_data_blocked':True,'prediction_hash_possible':False,'reason':f'{type(exc).__name__}:{exc}'}

def _signature_aggregate(items:list[dict[str,Any]])->dict[str,Any]:
 items=sorted(items,key=lambda x:x['outer_round']);n=len(items);periods={'OVERALL':items,'RECENT_100':items[-100:],'RECENT_50':items[-50:],'RECENT_20':items[-20:]}
 metrics={}
 for period,rows in periods.items():
  for scope,key in (('INTEGRATED','integrated_hits'),('MAIN','main_hits')):
   for k in (3,2,1,0):
    x=sum(r[key]==k for r in rows);metrics[f'{scope}|EXACT_{k}_OF_3|{period}']={'sample_count':len(rows),'hit_count':x,'rate':x/len(rows) if rows else 0.0}
 stats={}
 for scope,key in (('INTEGRATED','integrated_hits'),('MAIN','main_hits')):
  for k in (3,2,1,0):stats[f'{scope}|EXACT_{k}_OF_3']=statistic(sum(r[key]==k for r in items),n,random_probability(scope,k))
 i2=stats['INTEGRATED|EXACT_2_OF_3'];flags=[]
 for period in ('RECENT_100','RECENT_50'):
  m=metrics[f'INTEGRATED|EXACT_2_OF_3|{period}'];hi=wilson95(m['hit_count'],m['sample_count'])[1]
  flags.append(m['sample_count']>0 and m['rate']<random_probability('INTEGRATED',2) and hi<max(random_probability('INTEGRATED',2),i2['wilson_low']))
 collapse='RECENT_SUPPORT_COLLAPSE_SEVERE' if all(flags) else 'RECENT_SUPPORT_COLLAPSE_WARNING' if any(flags) else 'RECENT_SUPPORT_STABLE'
 bonus_assisted=sum(r['integrated_hits']==3 and r['main_hits']==2 and r['bonus_hit']==1 for r in items);main3=sum(r['main_hits']==3 for r in items)
 identity_counts=Counter('-'.join(map(str,r['trio'])) for r in items)
 return {'selection_rule_exposure_count':n,'representative_identity_exposure_count':sum(identity_counts.values()),
  'representative_identity_counts':dict(sorted(identity_counts.items())),'first_exposure_round':items[0]['outer_round'],'last_exposure_round':items[-1]['outer_round'],
  'metrics':metrics,'statistics':stats,'recent_support_collapse_state':collapse,'main_3_of_3_count':main3,'bonus_assisted_3_of_3_count':bonus_assisted}

def _rank_key(row:Mapping[str,Any])->tuple[Any,...]:
 st=row['performance']['statistics'];num=sorted((NUMBER_RANK.get(s,-1) for s in row['number_states']))
 return (-STATE_RANK[row['trio_state']],-int(row['valid_for_pair']),-PARETO_RANK[row['pareto_state']],tuple(-x for x in num),
  tuple(-UNIT_RANK[x] for x in row['coverage']['trio_unit_state_vector']),tuple(-ROLE_RANK[x] for x in row['coverage']['role_diversity_vector']),
  -st[('INTEGRATED','EXACT_3_OF_3')]['wilson_low'],-st[('INTEGRATED','EXACT_3_OF_3')]['rate'],
  -st[('MAIN','EXACT_3_OF_3')]['wilson_low'],-st[('INTEGRATED','EXACT_2_OF_3')]['wilson_low'],
  -COLLAPSE_RANK[row['recent_support_collapse_state']],RISK_RANK[row['trio_rule_opposite_risk']],
  STRUCTURE_RANK.get(row['final_structure_state'],4),-BONUS_RANK[row['bonus_dependency_state']],tuple(OVERLAP_RANK[x] for x in row['coverage']['evidence_overlap_vector']),tuple(row['trio']))

def aggregate(source_db:Path,data_path:Path,analysis_round:int=1236)->dict[str,Any]:
 uri=f'file:{source_db.resolve().as_posix()}?mode=ro';db=sqlite3.connect(uri,uri=True);db.row_factory=sqlite3.Row
 run=dict(db.execute('select * from wf_run where run_id=?',(RUN_ID,)).fetchone());rounds=[dict(x) for x in db.execute('select * from wf_round where run_id=? order by evaluation_round',(RUN_ID,))]
 raw=[dict(x) for x in db.execute('select * from wf_exposure where run_id=? order by evaluation_round,trio_rule_signature',(RUN_ID,))];db.close()
 grouped=defaultdict(list);identity=Counter()
 for x in raw:
  trio=tuple(map(int,x['representative_trio_key'].split('-')));identity[trio]+=1
  grouped[x['trio_rule_signature']].append({'outer_round':x['evaluation_round'],'trio':trio,'integrated_hits':x['integrated_hits'],'main_hits':x['main_hits'],'bonus_hit':x['bonus_hit'],'unit_conflict':x['unit_conflict'],'prediction_hash_before_result':x['prediction_hash_before_result']})
 signatures={s:_signature_aggregate(v) for s,v in sorted(grouped.items())}
 exposures={s:v for s,v in grouped.items()}
 stage6=diagnose_stage6(data_path,analysis_round);current=build_current_trios(stage6,DEFINITIONS,exposures)
 ranked=sorted(current['rows'].values(),key=_rank_key)
 for rank,row in enumerate(ranked,1):
  row['final_rank']=rank;row['representative_identity_exposure_count']=identity[row['trio']]
  row['first_limited_gate']=row['first_failed_gate'];row['primary_reason']=row['trio_state']
  row['secondary_reasons']=[x for x in (row['first_failed_gate'],row['recent_support_collapse_state'],row['trio_rule_opposite_risk'],row['final_structure_state'],row['bonus_dependency_state']) if x]
 hashes={'signature_hash':sha256_json(signatures),'current_hash':sha256_json({ '-'.join(map(str,r['trio'])):{'state':r['trio_state'],'rank':r['final_rank'],'valid':r['valid_for_pair'],'decision':r['decision_hash']} for r in ranked})}
 hashes['decision_hash']=sha256_json(hashes)
 counts=Counter(r['trio_state'] for r in ranked);valid=[r for r in ranked if r['valid_for_pair']]
 return {'source_run':run,'rounds':rounds,'raw_exposure_count':len(raw),'signatures':signatures,'current':current,'ranked':ranked,'identity_counts':identity,
  'hashes':hashes,'state_counts':dict(counts),'valid_for_pair_count':len(valid),'valid_top30':valid[:30]}

def store_final(result:Mapping[str,Any],source_db:Path,target_db:Path,manifest_hash:str,
                verifications:Mapping[str,Mapping[str,Any]]|None=None)->None:
 if target_db.exists():raise FileExistsError(target_db)
 db=sqlite3.connect(target_db);db.executescript(FINAL_SCHEMA)
 try:
  with db:
   db.execute('insert into final_run values (?,?,?,?,?,?,?,?,?,?,?,?,?)',('P45-v2.7.3-stage7.2',RUN_ID,_sha(source_db),source_db.stat().st_size,manifest_hash,len(result['signatures']),result['raw_exposure_count'],len(result['ranked']),result['hashes']['signature_hash'],result['hashes']['decision_hash'],10,'COMPLETE',__import__('datetime').datetime.now().astimezone().isoformat(timespec='seconds')))
   for sig,a in result['signatures'].items():
    db.execute('insert into signature_aggregate values (?,?,?,?,?,?,?)',(sig,a['selection_rule_exposure_count'],a['representative_identity_exposure_count'],a['first_exposure_round'],a['last_exposure_round'],canonical_json(a),sha256_json(a)))
   for r in result['ranked']:
    key='-'.join(map(str,r['trio']));payload={k:v for k,v in r.items() if k!='performance'}
    payload['performance']={'period_metrics':{'|'.join(k):v for k,v in r['performance']['period_metrics'].items()},'statistics':{'|'.join(k):v for k,v in r['performance']['statistics'].items()}}
    db.execute('insert into current_trio_final values (?,?,?,?,?,?,?,?,?,?,?,?,?)',(key,*r['trio'],r['trio_rule_signature'],r['trio_state'],int(r['valid_for_pair']),r['final_rank'],r['first_limited_gate'],r['primary_reason'],canonical_json(r['secondary_reasons']),canonical_json(payload),r['decision_hash']))
   for code, detail in sorted((verifications or {}).items()):
    db.execute('insert into verification_record values (?,?,?)',
               (code,int(bool(detail.get('passed'))),canonical_json(detail)))
  if db.execute('pragma integrity_check').fetchone()[0]!='ok' or db.execute('pragma foreign_key_check').fetchall():raise RuntimeError('final DB integrity failure')
 finally:db.close()

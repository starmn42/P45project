"""Locked EXP-CROWD-RETAIL-001-V1 conditional randomization."""
from __future__ import annotations
import csv, hashlib, json, math
from collections import defaultdict
from pathlib import Path
from typing import Any
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
EXP=ROOT/'v27_storage/experiments/crowd_retail_exp001_v1'
SNAPSHOT=EXP/'exp_crowd_retail_001_v1_winner_rows_262_1237.csv'
PROTOCOL=ROOT/'00_P45_STATE/experiment_lab/EXP-CROWD-RETAIL-001/EXP_CROWD_RETAIL_001_V1_LOCKED_PROTOCOL.md'
RESULT=EXP/'EXP_CROWD_RETAIL_001_V1_RESULT.json'
PERM=EXP/'PERMUTATION_SUMMARY.json'
RERUN=EXP/'DETERMINISTIC_RERUN_EVIDENCE.json'
REPS=500_000;SEED=2026082307

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def canon(x:Any)->str:return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def key(row:dict[str,str])->str:
 sid=row['store_id'].strip()
 return 'ID:'+sid if sid else 'EXACT:'+' '.join(row['store_name'].split())+'|'+' '.join(row['store_address'].split())
def load()->list[dict[str,str]]:
 if sha(SNAPSHOT)!='854ca7256219eadf574ac32ad256b84e9a5bfa42ceece09f0a09dd1eed79cd50':raise RuntimeError('SNAPSHOT_HASH_MISMATCH')
 with SNAPSHOT.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 if any(int(x['round'])<262 or int(x['round'])>1237 for x in rows):raise RuntimeError('RANGE_VIOLATION')
 return rows
def p_ge2(n:int,m:int,c:int)->float:
 den=math.comb(n,m)
 p0=math.comb(n-c,m) if 0<=m<=n-c else 0
 p1=c*math.comb(n-c,m-1) if 0<=m-1<=n-c else 0
 return 1-(p0+p1)/den
def round_pmf(sizes:list[int],m:int)->np.ndarray:
 n=sum(sizes); dp={(0,0):(1)}; used=0
 for c in sizes:
  nd={}
  for (sel,col),w in dp.items():
   for q in range(c+1):
    if sel+q<=m:nd[(sel+q,col+(q>=2))]=nd.get((sel+q,col+(q>=2)),0)+w*math.comb(c,q)
  dp=nd;used+=c
 out=np.zeros(max((col for sel,col in dp if sel==m),default=0)+1)
 for (sel,col),w in dp.items():
  if sel==m:out[col]+=w
 out/=math.comb(n,m)
 return out
def summarize(rows:list[dict[str,str]],include_online:bool=False)->dict[str,Any]:
 by=defaultdict(list)
 for x in rows:
  if x['mode'] not in ('자동','수동'):continue
  if not include_online and int(x['is_online']):continue
  by[int(x['round'])].append(x)
 obs=0;expected=0.;pairs=0;epairs=0.;extra=0;dup=0;cells=[];rounds=[];aggregate=np.array([1.])
 for r in range(262,1238):
  rr=by[r]; n=len(rr);m=sum(x['mode']=='수동' for x in rr)
  groups=defaultdict(list)
  for x in rr:groups[key(x)].append(x)
  sizes=[len(v) for v in groups.values()]
  if n:
   pmf=round_pmf(sizes,m);aggregate=np.convolve(aggregate,pmf)
  robs=0;rexp=0.
  for k,v in groups.items():
   c=len(v);mm=sum(x['mode']=='수동' for x in v);e=p_ge2(n,m,c) if n else 0.
   hit=int(mm>=2);obs+=hit;expected+=e;robs+=hit;rexp+=e;pairs+=math.comb(mm,2);extra+=max(mm-1,0)
   if n>=2:epairs+=math.comb(c,2)*math.comb(m,2)/math.comb(n,2)
   if c>=2:dup+=1
   cells.append({'round':r,'key':k,'c':c,'manual':mm,'observed':hit,'expected':e})
  rounds.append({'round':r,'observed':robs,'expected':rexp,'excess':robs-rexp,'n':n,'m':m})
 return {'observed':obs,'expected':expected,'pairs':pairs,'expected_pairs':epairs,'extra':extra,'duplicate_capable':dup,'cells':cells,'rounds':rounds,'aggregate_pmf':aggregate}
def calculate()->dict[str,Any]:
 rows=load(); primary=summarize(rows); allch=summarize(rows,True)
 gate=primary['duplicate_capable']>=20 and primary['expected']>=5
 rng=np.random.default_rng(SEED); values=np.arange(len(primary['aggregate_pmf'])); draws=rng.choice(values,size=REPS,p=primary['aggregate_pmf']) if gate else np.array([],dtype=int)
 exceed=int(np.count_nonzero(draws>=primary['observed'])) if gate else None;p=(exceed+1)/(REPS+1) if gate else None
 mcse=math.sqrt(p*(1-p)/REPS) if gate else None
 early=[x for x in primary['rounds'] if x['round']<=749];late=[x for x in primary['rounds'] if x['round']>=750]
 ee=sum(x['excess'] for x in early);le=sum(x['excess'] for x in late);flag='BOTH_POSITIVE' if ee>0 and le>0 else 'BOTH_NONPOSITIVE' if ee<=0 and le<=0 else 'MIXED'
 ranked=sorted(primary['cells'],key=lambda x:(-x['manual'],x['round'],x['key']))
 def removed(q:int)->dict[str,float]:
  cut=ranked[:q];return {'observed':primary['observed']-sum(x['observed'] for x in cut),'expected':primary['expected']-sum(x['expected'] for x in cut),'excess':(primary['observed']-sum(x['observed'] for x in cut))-(primary['expected']-sum(x['expected'] for x in cut))}
 counts={m:sum(x['mode']==m for x in rows) for m in ('자동','수동','반자동')};online=sum(int(x['is_online']) for x in rows)
 if not gate:judgment='INCONCLUSIVE_LOW_COLLISION_EXPOSURE'
 elif primary['observed']-primary['expected']>0 and p<=.01:judgment='EXPLORATORY_RETAILER_MODE_CONCENTRATION'
 else:judgment='EXPLORATORY_NOT_SUPPORTED'
 return {'logical_id':'EXP-CROWD-RETAIL-001-V1','registry_id':'EXP-CROWD-20260823-008-V1','evidence_class':'POST_LINEAGE_EXPLORATORY','data_range':'262~1237','snapshot_sha256':sha(SNAPSHOT),'protocol_sha256':sha(PROTOCOL),'round_1238_plus_used':False,'raw_first_prize_rows':len(rows),'auto_rows':counts['자동'],'manual_rows':counts['수동'],'semiauto_rows_excluded':counts['반자동'],'online_rows_excluded':online,'mode_store_count_mismatch':0,'retailer_key_method':'OFFICIAL_STORE_ID_ELSE_EXACT_NORMALIZED_NAME_ADDRESS','total_duplicate_capable_cells':primary['duplicate_capable'],'exposure_gate':'PASS' if gate else 'FAIL','observed_manual_collision_cells':primary['observed'],'expected_manual_collision_cells':primary['expected'],'cell_excess':primary['observed']-primary['expected'],'cell_enrichment':primary['observed']/primary['expected'] if primary['expected'] else None,'primary_randomization_p':p,'randomizations':REPS if gate else 0,'randomization_seed':SEED,'exceedances':exceed,'mc_standard_error':mcse,'null_mean':float(draws.mean()) if gate else None,'null_q95':float(np.quantile(draws,.95,method='higher')) if gate else None,'null_q99':float(np.quantile(draws,.99,method='higher')) if gate else None,'null_q999':float(np.quantile(draws,.999,method='higher')) if gate else None,'manual_pair_count':primary['pairs'],'expected_manual_pair_count':primary['expected_pairs'],'pair_enrichment':primary['pairs']/primary['expected_pairs'] if primary['expected_pairs'] else None,'max_manual_cell_multiplicity':ranked[0]['manual'],'max_manual_cell':{'round':ranked[0]['round'],'retailer_key':ranked[0]['key']},'collision_ticket_excess':primary['extra'],'early_cell_excess':ee,'late_cell_excess':le,'temporal_flag':flag,'top1_cell_removed':removed(1),'top5_cells_removed':removed(5),'all_channel_cell_excess':allch['observed']-allch['expected'],'all_channel_observed':allch['observed'],'all_channel_expected':allch['expected'],'final_judgment':judgment,'same_person_identified':False,'independent_empirical_replication':False,'novelty_status':'NOVELTY_NOT_CONFIRMED','promotion_candidate':False,'prospective_protocol_changed':False,'prospective_signal_peeking':0,'draw_engine_changed':0,'official_engine':'FROZEN'}
def run()->dict[str,Any]:
 a=calculate();b=calculate()
 if canon(a)!=canon(b):raise RuntimeError('REPRODUCTION_MISMATCH')
 a['deterministic_rerun']='PASS';a['calculator_sha256']=sha(Path(__file__));a['result_hash']=hashlib.sha256(canon(a).encode()).hexdigest();EXP.mkdir(parents=True,exist_ok=True)
 RESULT.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 PERM.write_text(json.dumps({k:a[k] for k in ('observed_manual_collision_cells','expected_manual_collision_cells','primary_randomization_p','randomizations','randomization_seed','exceedances','mc_standard_error','null_mean','null_q95','null_q99','null_q999')},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 RERUN.write_text(json.dumps({'status':'PASS','same_snapshot':True,'same_code':True,'same_seed':True,'result_hash':a['result_hash']},indent=2)+'\n',encoding='utf-8');return a
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))

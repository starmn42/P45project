"""EXP-CROWD-TOPO-003-V1 locked Johnson radial moment tomography."""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'downloads/official-1-1237/raw'
EXP=ROOT/'v27_storage/experiments/crowd_topology_exp003_v1'
DOC=ROOT/'00_P45_STATE/experiment_lab/EXP-CROWD-TOPO-003'
PROTOCOL=DOC/'EXP_CROWD_TOPO_003_V1_LOCKED_PROTOCOL.md'
SNAPSHOT=EXP/'exp_crowd_topo_003_v1_draws_1_1237.csv'
MANIFEST=EXP/'SNAPSHOT_MANIFEST.json'
RESULT=EXP/'EXP_CROWD_TOPO_003_V1_RESULT.json'
VAL=np.array([1,234,11115,182780,1233765,3454542,3262623],dtype=np.float64)
REPS=200_000; SEED=2026082306

def sha(p:Path)->str:
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def canon(x:Any)->str:return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def intersection(i:int,j:int,h:int)->int:
 total=0
 for x0 in range(7):
  xa,xb=6-i-x0,6-j-x0; xo=6-x0-xa-xb
  if min(xa,xb,xo)>=0 and x0<=6-h and xa<=h and xb<=h and xo<=39-h:
   total+=math.comb(6-h,x0)*math.comb(h,xa)*math.comb(h,xb)*math.comb(39-h,xo)
 return total
def rank_fraction(a:list[list[int]])->int:
 m=[[Fraction(x) for x in r] for r in a]; row=0
 for col in range(len(m[0])):
  pivot=next((r for r in range(row,len(m)) if m[r][col]),None)
  if pivot is None: continue
  m[row],m[pivot]=m[pivot],m[row]; q=m[row][col]; m[row]=[x/q for x in m[row]]
  for r in range(len(m)):
   if r!=row and m[r][col]: q=m[r][col]; m[r]=[x-q*y for x,y in zip(m[r],m[row])]
  row+=1
 return row
def algebra_preflight()->dict[str,Any]:
 pairs=[(a,b) for a in range(4) for b in range(a,4)]
 mat=[[intersection(a,b,h) for h in range(7)] for a,b in pairs]
 checks={'F13':[0,0,148,117,16,0,0],'F23':[0,7030,5772,2871,888,100,0],
         'F33':[182780,91390,47212,25123,12056,3500,400]}
 got={k:mat[pairs.index(tuple(map(int,k[1:])))] for k in checks}
 return {'pairs':pairs,'rank':rank_fraction(mat),'coefficient_checks':{k:got[k]==v for k,v in checks.items()},'matrix':mat}
def load_raw()->list[dict[str,Any]]:
 rows={}
 for p in sorted(RAW.glob('api-*.json')):
  obj=json.loads(p.read_text(encoding='utf-8-sig'))
  for x in obj['data']['list']:
   r=int(x['ltEpsd'])
   if 1<=r<=1237:
    price=2000 if r<=87 else 1000; sales=int(x['wholEpsdSumNtslAmt'])
    rows[r]={'round':r,'date':x['ltRflYmd'],'k1':int(x['rnk1WnNope']),'k2':int(x['rnk2WnNope']),'k3':int(x['rnk3WnNope']),'k4':int(x['rnk4WnNope']),'k5':int(x['rnk5WnNope']),'sales':sales,'price':price,'sold_lines':sales//price,'source_file':p.name,'source_sha256':sha(p)}
 if sorted(rows)!=list(range(1,1238)): raise RuntimeError('SOURCE_RANGE_GAP')
 return [rows[r] for r in range(1,1238)]
def snapshot()->dict[str,Any]:
 rows=load_raw(); EXP.mkdir(parents=True,exist_ok=True); fields=list(rows[0])
 with SNAPSHOT.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 out={'rows':1237,'range':'1~1237','round_1238_plus_rows':0,'snapshot_sha256':sha(SNAPSHOT),'fields':fields}
 MANIFEST.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); return out
def load()->dict[str,np.ndarray]:
 with SNAPSHOT.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 return {k:np.array([int(r[k]) for r in rows],dtype=np.float64) for k in ('round','k1','k2','k3','k4','k5','sold_lines')}
def reconstruct(y:np.ndarray)->tuple[np.ndarray,np.ndarray]:
 n=y.sum(axis=1); den=n*(n-1); F=np.empty((len(y),4,4))
 for a in range(4):
  for b in range(4): F[:,a,b]=y[:,a]*(y[:,b]-(1 if a==b else 0))/den
 g=np.empty((len(y),7));g[:,0]=F[:,0,0];g[:,1]=F[:,0,1];g[:,2]=F[:,0,2];g[:,3]=F[:,0,3]
 g[:,4]=(F[:,1,3]-148*g[:,2]-117*g[:,3])/16
 g[:,5]=(F[:,2,3]-7030*g[:,1]-5772*g[:,2]-2871*g[:,3]-888*g[:,4])/100
 g[:,6]=(F[:,3,3]-182780*g[:,0]-91390*g[:,1]-47212*g[:,2]-25123*g[:,3]-12056*g[:,4]-3500*g[:,5])/400
 return F,g
def summary(x:np.ndarray)->dict[str,float]:
 return {'mean':float(x.mean()),'median':float(np.median(x)),'se':float(x.std(ddof=1)/math.sqrt(len(x)))}
def calculate()->dict[str,Any]:
 a=algebra_preflight()
 if a['rank']!=7 or not all(a['coefficient_checks'].values()): raise RuntimeError('ALGEBRA_PREFLIGHT_FAILED')
 d=load(); y=np.column_stack((d['k1'],d['k2']+d['k3'],d['k4'],d['k5'])); F,g=reconstruct(y); M=d['sold_lines']
 prof=M[:,None]**2*g/VAL; z=prof[:,2:]-prof[:,1,None]; hold=z[800:]; blocks=hold.reshape(23,19,5).sum(axis=1)
 means=hold.mean(axis=0); sd=hold.std(axis=0,ddof=1); t=means/(sd/math.sqrt(437)); tmax=float(np.max(np.abs(t)))
 centered=hold-means; blocks=centered.reshape(23,19,5).sum(axis=1)
 rng=np.random.default_rng(SEED); exceed=0; sumsq=(centered**2).sum(axis=0); n=437
 for start in range(0,REPS,5000):
  q=min(5000,REPS-start); signs=rng.choice(np.array([-1.,1.]),size=(q,23)); mu=(signs@blocks)/n
  var=(sumsq-n*mu*mu)/(n-1); ts=mu/np.sqrt(var/n); exceed+=int(np.count_nonzero(np.max(np.abs(ts),axis=1)>=tmax))
 p=(exceed+1)/(REPS+1)
 residuals={'F11':F[:,1,1]-(234*g[:,0]+43*g[:,1]+4*g[:,2]),'F12':F[:,1,2]-(190*g[:,1]+82*g[:,2]+9*g[:,3]),'F22':F[:,2,2]-(11115*g[:,0]+3895*g[:,1]+1264*g[:,2]+351*g[:,3]+36*g[:,4])}
 diag={}
 for k,v in residuals.items():
  idx=int(np.argmax(np.abs(v))); diag[k]={'whole_mean_raw':float(v.mean()),'holdout_mean_raw':float(v[800:].mean()),'whole_mean_scaled':float((M*M*v).mean()),'holdout_mean_scaled':float((M[800:]**2*v[800:]).mean()),'largest_abs_round':idx+1,'largest_abs_raw':float(abs(v[idx]))}
 getcontext().prec=50; dec=[]
 for row in range(1237):
  yy=[Decimal(int(x)) for x in y[row]]; nn=sum(yy); de=nn*(nn-1); ff=lambda i,j: yy[i]*(yy[j]-(1 if i==j else 0))/de
  gg=[ff(0,0),ff(0,1),ff(0,2),ff(0,3)];gg.append((ff(1,3)-148*gg[2]-117*gg[3])/16);gg.append((ff(2,3)-7030*gg[1]-5772*gg[2]-2871*gg[3]-888*gg[4])/100);gg.append((ff(3,3)-182780*gg[0]-91390*gg[1]-47212*gg[2]-25123*gg[3]-12056*gg[4]-3500*gg[5])/400)
  mm=Decimal(int(M[row])); dec.append([mm*mm*(gg[h]/Decimal(int(VAL[h]))-gg[1]/Decimal(234)) for h in range(2,7)])
 decmean=np.array([float(sum(r[j] for r in dec)/Decimal(1237)) for j in range(5)]); diff=np.abs(decmean-z.mean(axis=0)); tol=np.maximum(np.abs(decmean)*1e-8,1e-10)
 shares=[float(np.sort(np.abs(hold[:,j]))[-10:].sum()/np.abs(hold[:,j]).sum()) for j in range(5)]
 profiles={f'd{h}':summary(prof[:,h])|{'difference_from_d1':float(prof[:,h].mean()-prof[:,1].mean())} for h in range(7)}
 return {'logical_id':'EXP-CROWD-TOPO-003-V1','registry_id':'EXP-CROWD-20260823-007-V1','data_range':'1~1237','holdout':'801~1237','round_1238_plus_used':False,'protocol_sha256':sha(PROTOCOL),'snapshot_sha256':sha(SNAPSHOT),'algebra':a,'t':t.tolist(),'t_max':tmax,'bootstrap_repetitions':REPS,'seed':SEED,'exceedances':exceed,'omnibus_p':p,'final_judgment':'EXPLORATORY_TOPOLOGY_DEVIATION' if p<=.05 else 'EXPLORATORY_NOT_SUPPORTED','promotion_candidate':False,'profiles':profiles,'identity_diagnostics':diag,'numeric_stability':{'decimal_means':decmean.tolist(),'float_means':z.mean(axis=0).tolist(),'absolute_differences':diff.tolist(),'tolerance_pass':bool(np.all(diff<=tol))},'top10_absolute_share':shares,'official_effect':'NONE','draw_engine_changed':0,'prospective_signal_peeking':0}
def run()->dict[str,Any]:
 one=calculate();two=calculate();
 if canon(one)!=canon(two): raise RuntimeError('DETERMINISTIC_RERUN_FAILED')
 one['deterministic_rerun']='PASS'; one['calculator_sha256']=sha(Path(__file__)); one['result_hash']=hashlib.sha256(canon(one).encode()).hexdigest(); EXP.mkdir(parents=True,exist_ok=True);RESULT.write_text(json.dumps(one,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return one
def main()->int:
 p=argparse.ArgumentParser();p.add_argument('command',choices=['algebra','snapshot','run']);x=p.parse_args(); out={'algebra':algebra_preflight,'snapshot':snapshot,'run':run}[x.command]();print(json.dumps(out,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())

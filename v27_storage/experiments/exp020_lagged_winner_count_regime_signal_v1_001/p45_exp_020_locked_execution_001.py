from __future__ import annotations
import csv, hashlib, json, math
from collections import Counter
from fractions import Fraction
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
PROTOCOL=HERE/'P45_EXP_020_LAGGED_WINNER_COUNT_REGIME_SIGNAL_V1_PROTOCOL_001.md'
PLOCK=HERE/'P45_EXP_020_PROTOCOL_LOCK_001.md'; SLOCK=HERE/'P45_EXP_020_SELECTION_LOCK_001.md'
DATA=HERE/'P45_EXP_020_OFFICIAL_FULL_HISTORY_001.csv'
CALC=HERE/'P45_EXP_020_LAGGED_WINNER_COUNT_REGIME_SIGNAL_V1_CALCULATION_001.json'
RESULT=HERE/'P45_EXP_020_LAGGED_WINNER_COUNT_REGIME_SIGNAL_V1_RESULT_001.md'
RAW_DIR=ROOT/'downloads/official-1-1237/raw'; RAW_1238=ROOT/'v27_storage/experiments/exp019_sales_adjusted_birthday_crowd_effect_v1_001/P45_EXP_019_OFFICIAL_RAW_BATCHES_001.jsonl'
CANON=ROOT/'v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv'
PROTOCOL_SHA='610da2d9522e37e8b35d4492abf750dcac5c42b264de4af52e32c1df8174475b'
PLOCK_SHA='273432ff04d812b35dbf2fba168c800448e14d4119665665141070317432b3be'
SOURCE_SHA='4ce76976f782d6ee06ea1d18eeab8420b1d3ef1e6f92f371ee0e8aa6a032e13f'
CANON_SHA='1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8'
DEN=math.comb(45,6); NULL=Fraction(6,45)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def source_sha(): return hashlib.sha256(b''.join(p.read_bytes() for p in sorted(RAW_DIR.glob('api-*.json')))+RAW_1238.read_bytes()).hexdigest()

def load():
    if sha(PROTOCOL)!=PROTOCOL_SHA or sha(PLOCK)!=PLOCK_SHA or source_sha()!=SOURCE_SHA or sha(CANON)!=CANON_SHA: raise RuntimeError('INTEGRITY_BLOCK')
    rec={}
    for p in sorted(RAW_DIR.glob('api-*.json')):
        for x in json.loads(p.read_text(encoding='utf-8'))['data']['list']: rec[int(x['ltEpsd'])]=x
    for line in RAW_1238.read_text(encoding='utf-8').splitlines():
        for x in json.loads(line)['records']:
            if int(x['ltEpsd'])==1238: rec[1238]=x
    can={int(r['round']):tuple(sorted(int(r[f'n{i}']) for i in range(1,7))) for r in csv.DictReader(CANON.open(encoding='utf-8-sig'))}
    if set(rec)!=set(range(1,1239)): raise RuntimeError('EXP_020_PROTOCOL_BLOCKED_FULL_HISTORY_DATA_GAP')
    rows=[]
    for t in range(1,1239):
        x=rec[t]; main=tuple(sorted(int(x[f'tm{i}WnNo']) for i in range(1,7)))
        if main!=can[t] or x.get('rnk1WnNope') is None: raise RuntimeError('EXP_020_PROTOCOL_BLOCKED_FULL_HISTORY_DATA_GAP')
        rows.append({'draw':t,'main':main,'winner':int(x['rnk1WnNope'])})
    with DATA.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,lineterminator='\n'); w.writerow(['draw','main1','main2','main3','main4','main5','main6','winner_count_1st'])
        for r in rows: w.writerow([r['draw'],*r['main'],r['winner']])
    return rows

def targets(rows,a,b):
    by={r['draw']:r for r in rows}
    return [{'t':t,'wprev':by[t-1]['winner'],'main':set(by[t]['main'])} for t in range(a,b+1)]

def enrich(ts,L,U):
    act=[r for r in ts if L<=r['wprev']<=U]; ina=[r for r in ts if not L<=r['wprev']<=U]
    delta={}
    for n in range(1,46): delta[n]=Fraction(sum(n in r['main'] for r in act),len(act))-Fraction(sum(n in r['main'] for r in ina),len(ina))
    return act,delta

def discover(rows):
    A=targets(rows,2,300); B=targets(rows,301,600); vals=[r['wprev'] for r in A+B]; lo,hi=min(vals),max(vals)
    before=(hi-lo+1)*(hi-lo+2)//2; covered=[]; stable=0; positive=[]
    for L in range(lo,hi+1):
      for U in range(L,hi+1):
        aa=[r for r in A if L<=r['wprev']<=U]; bb=[r for r in B if L<=r['wprev']<=U]
        if not (Fraction(1,10)<=Fraction(len(aa),len(A))<=Fraction(2,5) and Fraction(1,10)<=Fraction(len(bb),len(B))<=Fraction(2,5)): continue
        covered.append((L,U)); aa,da=enrich(A,L,U); bb,db=enrich(B,L,U)
        nums=[n for n in range(1,46) if da[n]>0 and db[n]>0]
        nums.sort(key=lambda n:(-min(da[n],db[n]),n)); S=tuple(nums[:6])
        if not S: continue
        stable+=1; ha=sum(len(set(S)&r['main']) for r in aa); hb=sum(len(set(S)&r['main']) for r in bb); k=len(S)
        la=Fraction(ha,len(aa)*k)-NULL; lb=Fraction(hb,len(bb)*k)-NULL
        if la<=0 or lb<=0: continue
        positive.append({'L':L,'U':U,'S':S,'k':k,'active_A':len(aa),'active_B':len(bb),'hits_A':ha,'hits_B':hb,'lift_A':la,'lift_B':lb,'score':min(la,lb)})
    positive.sort(key=lambda c:(-c['score'],c['U']-c['L'],c['L'],c['U']))
    return {'wmin':lo,'wmax':hi,'before':before,'after':len(covered),'stable':stable,'positive':len(positive),'top':positive[:10]}

def exact_upper(k,A,H):
    weights=[math.comb(k,x)*math.comb(45-k,6-x) for x in range(max(0,6-(45-k)),min(k,6)+1)]
    xmin=max(0,6-(45-k)); dp=[1]
    for _ in range(A):
        nd=[0]*(len(dp)+len(weights)-1)
        for i,v in enumerate(dp):
            for j,w in enumerate(weights): nd[i+j]+=v*w
        dp=nd
    idx=max(0,H-A*xmin)
    return Fraction(sum(dp[idx:]),DEN**A)

def select(rows,top):
    ts=targets(rows,601,867); out=[]
    for c in top:
        act=[r for r in ts if c['L']<=r['wprev']<=c['U']]; H=sum(len(set(c['S'])&r['main']) for r in act); X=len(act)*c['k']; rate=Fraction(H,X); p=exact_upper(c['k'],len(act),H)
        q={**c,'active':len(act),'exposures':X,'hits':H,'rate':rate,'lift':rate-NULL,'p':p,'eligible':len(act)>=30 and X>=90 and rate>NULL and p<=Fraction(1,10)}; out.append(q)
    elig=[q for q in out if q['eligible']]; elig.sort(key=lambda q:(q['p'],-q['lift'],-q['score'],q['U']-q['L'],q['L'],q['U']))
    return out,(elig[0] if elig else None)

def holdout(rows,s):
    ts=targets(rows,868,1238); act=[r for r in ts if s['L']<=r['wprev']<=s['U']]; H=sum(len(set(s['S'])&r['main']) for r in act); X=len(act)*s['k']
    if len(act)<30 or X<90: return {'active':len(act),'exposures':X,'hits':H,'verdict':'INCONCLUSIVE_HOLDOUT_INSUFFICIENT_EXPOSURE'}
    rate=Fraction(H,X); p=exact_upper(s['k'],len(act),H); ok=rate>NULL and p<=Fraction(1,20)
    return {'active':len(act),'exposures':X,'hits':H,'rate':rate,'lift':rate-NULL,'p':p,'verdict':'HISTORICAL_DISCOVERY_SELECTION_HOLDOUT_POSITIVE_PROSPECTIVE_REQUIRED' if ok else 'FAILED_NOT_REPRODUCED'}

def compact(v):
    if isinstance(v,Fraction): return {'numerator':v.numerator,'denominator':v.denominator,'decimal':float(v)}
    if isinstance(v,dict): return {k:compact(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)): return [compact(x) for x in v]
    return v

def lock_text(s,data_sha,timestamp):
    return '\n'.join(['# P45 EXP-020 SELECTION LOCK 001','',f'- EXP ID: `EXP-DRAW-20260828-020-V1`',f'- Protocol SHA-256: `{PROTOCOL_SHA}`',f'- Source proof SHA-256: `{SOURCE_SHA}`',f'- Derived dataset SHA-256: `{data_sha}`','- TRAIN-A: `2..300`','- TRAIN-B: `301..600`','- Selection: `601..867`',f"- Selected band: `[{s['L']},{s['U']}]`",f"- S_FINAL: `{' '.join(map(str,s['S']))}`",f"- k: `{s['k']}`",f"- TRAIN-A active/hits/lift: `{s['active_A']} / {s['hits_A']} / {float(s['lift_A'])!r}`",f"- TRAIN-B active/hits/lift: `{s['active_B']} / {s['hits_B']} / {float(s['lift_B'])!r}`",f"- Selection active/exposures/hits/rate/p: `{s['active']} / {s['exposures']} / {s['hits']} / {float(s['rate'])!r} / {float(s['p'])!r}`",f'- Selection timestamp: `{timestamp}`','- Holdout number relationship calculated: `NO`','- FUTURE_LEAKAGE: `0`',''])

def run_pre_holdout(rows):
    d=discover(rows); ev,s=select(rows,d['top']) if d['top'] else ([],None); return d,ev,s

def main():
    rows=load(); data_sha=sha(DATA); d1,e1,s1=run_pre_holdout(rows); d2,e2,s2=run_pre_holdout(rows)
    if compact([d1,e1,s1])!=compact([d2,e2,s2]): raise RuntimeError('REPRODUCIBILITY_FAILURE')
    if not d1['top']:
        final='FAILED_NO_TRAIN_CANDIDATE'; h=None; slock_sha=None
    elif s1 is None:
        final='FAILED_NO_SELECTION_SIGNAL'; h=None; slock_sha=None
    else:
        timestamp=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds'); SLOCK.write_text(lock_text(s1,data_sha,timestamp),encoding='utf-8',newline='\n'); slock_sha=sha(SLOCK)
        h1=holdout(rows,s1); h2=holdout(rows,s2)
        if compact(h1)!=compact(h2): raise RuntimeError('REPRODUCIBILITY_FAILURE')
        h=h1; final=h['verdict']
    proof=hashlib.sha256(json.dumps(compact([d1,e1,s1,h,final]),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    out={'experiment_id':'EXP-DRAW-20260828-020-V1','protocol_sha256':PROTOCOL_SHA,'protocol_lock_sha256':sha(PLOCK),'source_proof_sha256':SOURCE_SHA,'derived_dataset_sha256':data_sha,'full_history':{'rounds':1238,'missing':[],'main6_mismatch':[]},'train':compact(d1),'selection':compact({'evaluated':e1,'selected':s1}),'selection_lock_sha256':slock_sha,'holdout':compact(h),'final_verdict':final,'reproducibility':{'full_runs':2,'all_required_components':'PASS','deterministic_proof_sha256':proof},'protection':{'official':0,'DB':0,'Fixed':0,'Linked':0,'KTS':0,'sealed_1239':0,'prospective':0,'existing_verdicts':0,'FUTURE_LEAKAGE':0}}
    CALC.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    RESULT.write_text(f"# EXP-020 result\n\nFINAL_VERDICT = {final}\n\n- Protocol SHA: `{PROTOCOL_SHA}`\n- Full history: `1..1238 PASS`\n- TRAIN candidates after coverage: `{d1['after']}`\n- Stable number-set bands: `{d1['stable']}`\n- Positive-lift bands: `{d1['positive']}`\n- Selection eligible: `{sum(x['eligible'] for x in e1)}`\n- Selection lock SHA: `{slock_sha or 'NOT_CREATED'}`\n- Holdout: `{compact(h) if h else 'NOT_RUN'}`\n- Deterministic reproduction: `PASS`\n- Official protected changes: `0`\n- FUTURE_LEAKAGE: `0`\n",encoding='utf-8',newline='\n')
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__': main()

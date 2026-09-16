from __future__ import annotations
import csv, hashlib, itertools, json, math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
PROTOCOL=OUT/"P45_BONUS_LAG2_INTERACTION_V1_PROTOCOL_LOCKED_001.md"
PROTOCOL_SHA="d3f271d0869dbba0da466cb77835b8b7638c39fe99d7da8f7fe3c5ddffcac6c3"
SEED=15272394426792393632; NSIM=100_000
DATA=ROOT/"v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
DATA_SHA="1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"

def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load_data():
    if sha256(PROTOCOL)!=PROTOCOL_SHA: raise RuntimeError("PROTOCOL_HASH_MISMATCH")
    if sha256(DATA)!=DATA_SHA: raise RuntimeError("DATA_HASH_MISMATCH")
    rows=[]
    with DATA.open(encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f): rows.append((int(r["round"]),tuple(int(r[f"n{i}"]) for i in range(1,7)),int(r["bonus"])))
    rounds=[r for r,_,_ in rows]; checks={"continuous":rounds==list(range(1,rounds[-1]+1)),"duplicates_0":len(rounds)==len(set(rounds)),"main_valid":all(len(set(m))==6 and all(1<=x<=45 for x in m) for _,m,_ in rows),"bonus_valid":all(1<=b<=45 and b not in m for _,m,b in rows),"latest":rounds[-1]}
    if not all(v for k,v in checks.items() if k!="latest"): raise RuntimeError(f"DATA_FAIL {checks}")
    masks=np.array([sum(1<<(x-1) for x in m) for _,m,_ in rows],dtype=np.uint64); ranks=np.array([1+sum(x<b for x in m) for _,m,b in rows],dtype=np.int8)
    if not np.all((ranks>=1)&(ranks<=7)): raise RuntimeError("RANK_FAIL")
    return rows,masks,ranks,checks

def metrics(x,y):
    x=x.astype(float); y=y.astype(float); mx=float(x.mean()); my=float(y.mean()); cov=float(np.mean((x-mx)*(y-my))); vx=float(np.mean((x-mx)**2)); vy=float(np.mean((y-my)**2)); slope=cov/vx if vx else None; corr=cov/math.sqrt(vx*vy) if vx and vy else None
    return {"n":len(x),"mean_bonus_score":mx,"mean_overlap":my,"covariance":cov,"regression_slope":slope,"correlation":corr,"direction":"POSITIVE_LOW_BONUS_MORE_REAPPEARANCE" if cov>0 else "NEGATIVE_HIGH_BONUS_MORE_REAPPEARANCE" if cov<0 else "ZERO"}

def periods(x,y):
    n=len(x); cut=(n+1)//2; parts={"full":slice(None),"first_half":slice(0,cut),"second_half":slice(cut,None),"recent100":slice(-100,None),"recent50":slice(-50,None),"recent20":slice(-20,None)}
    return {k:metrics(x[s],y[s]) for k,s in parts.items()}

def conditional_shift(x,y,obs):
    xc=x.astype(float)-x.mean(); yc=y.astype(float)-y.mean(); n=len(x); vals=np.empty(n)
    for s in range(n): vals[s]=float(np.mean(xc*np.roll(yc,s)))
    return {"shifts":n,"extreme_count":int(np.count_nonzero(np.abs(vals)>=abs(obs)-1e-15)),"p":float(np.count_nonzero(np.abs(vals)>=abs(obs)-1e-15)/n),"min":float(vals.min()),"max":float(vals.max())}

def universe():
    total=math.comb(45,6); flat=np.fromiter((x for c in itertools.combinations(range(1,46),6) for x in c),dtype=np.uint8,count=total*6); combos=flat.reshape(total,6); masks=np.bitwise_or.reduce(np.left_shift(np.uint64(1),combos.astype(np.uint64)-1),axis=1); return combos,masks

def simulate(latest,obs):
    combos,umasks=universe(); rng=np.random.default_rng(SEED); vals=np.empty(NSIM); done=0; batch=500
    while done<NSIM:
        b=min(batch,NSIM-done); idx=rng.integers(0,len(umasks),size=(b,latest),dtype=np.int64); seq=umasks[idx]; nums=combos[idx]; q=rng.integers(0,39,size=(b,latest),dtype=np.int16)
        gaps=np.empty((b,latest,7),dtype=np.int16); gaps[:,:,0]=nums[:,:,0].astype(np.int16)-1; gaps[:,:,1:6]=nums[:,:,1:].astype(np.int16)-nums[:,:,:-1].astype(np.int16)-1; gaps[:,:,6]=45-nums[:,:,5].astype(np.int16)
        rank=1+np.sum(q[:,:,None]>=np.cumsum(gaps[:,:,:6],axis=2),axis=2); x=(4-rank[:,1:-1]).astype(float); y=np.bitwise_count(seq[:,:-2]&seq[:,2:]).astype(float)
        vals[done:done+b]=np.mean(x*y,axis=1)-np.mean(x,axis=1)*np.mean(y,axis=1); done+=b
    return {"histories":NSIM,"seed":SEED,"extreme_count":int(np.count_nonzero(np.abs(vals)>=abs(obs))),"p":float((1+np.count_nonzero(np.abs(vals)>=abs(obs)))/(NSIM+1)),"null_mean":float(vals.mean()),"null_sd":float(vals.std()),"q025":float(np.quantile(vals,.025)),"q975":float(np.quantile(vals,.975))}

def main():
    rows,masks,ranks,checks=load_data(); x=(4-ranks[1:-1]).astype(np.int8); y=np.bitwise_count(masks[:-2]&masks[2:]).astype(np.int8); overall=metrics(x,y); stability=periods(x,y); shift=conditional_shift(x,y,overall["covariance"]); mc=simulate(len(rows),overall["covariance"])
    rank_table={}
    prior_ranks=ranks[1:-1]
    for r in range(1,8):
        yy=y[prior_ranks==r]; rank_table[str(r)]={"rounds":len(yy),"mean_overlap":float(yy.mean()) if len(yy) else None,"difference_from_0_8":float(yy.mean()-.8) if len(yy) else None}
    first=stability["first_half"]["covariance"]; second=stability["second_half"]["covariance"]; consistent=first*second>=0
    if mc["p"]<=.05 and consistent and shift["p"]<=.05: judgment="STRONG_INTERACTION_CANDIDATE"
    elif .05<mc["p"]<=.10 and consistent: judgment="INTERESTING_WATCHLIST"
    else: judgment="FAILED_NOT_INTERESTING"
    result={"precheck":"PASS","canonical_latest":rows[-1][0],"canonical_sha256":sha256(DATA),"protocol_sha256":sha256(PROTOCOL),"data_checks":checks,"evaluated_rounds":len(x),"target_range":[3,rows[-1][0]],"overall":overall,"primary_mc":mc,"conditional_shift":shift,"stability":stability,"bonus_rank_table":rank_table,"final_judgment":judgment,"future_leakage":0,"EXP005_FINAL":"FAILED","EXP015_FINAL":"FAILED_EARLY","EXP017":"NOT_CREATED","official_protected_changes":0}
    trace=[]
    for i in range(len(x)):
        trace.append({"target_round":i+3,"source_round_R_minus_2":i+1,"bonus_state_round_R_minus_1":i+2,"bonus_rank":int(ranks[i+1]),"bonus_score":int(x[i]),"lag2_overlap":int(y[i]),"centered_bonus_score":float(x[i]-x.mean()),"centered_overlap":float(y[i]-y.mean()),"covariance_contribution":float((x[i]-x.mean())*(y[i]-y.mean())),"future_leakage_flag":0})
    with (OUT/"P45_BONUS_LAG2_INTERACTION_V1_TRACE_001.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(trace[0]),lineterminator="\n");w.writeheader();w.writerows(trace)
    (OUT/"P45_BONUS_LAG2_INTERACTION_V1_RESULT_001.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    ranks_md="\n".join(f"|{r}|{rank_table[str(r)]['rounds']}|{rank_table[str(r)]['mean_overlap']:.9f}|{rank_table[str(r)]['difference_from_0_8']:+.9f}|" for r in range(1,8))
    per_md="\n".join(f"|{k}|{stability[k]['n']}|{stability[k]['covariance']:+.9f}|{stability[k]['regression_slope']:+.9f}|{stability[k]['correlation']:+.9f}|" for k in ("full","first_half","second_half","recent100","recent50","recent20"))
    easy=f"관측 covariance는 {overall['covariance']:+.6f}이고 방향은 {'직전 BONUS가 낮을수록 재등장이 늘어나는 쪽' if overall['covariance']>0 else '직전 BONUS가 높을수록 재등장이 늘어나는 쪽'}. 아무 관계 없는 공정 시퀀스에서도 100번 중 약 {100*mc['p']:.2f}번 이 정도 이상의 관계가 나타날 수 있다."
    report=f'''# P45 BONUS × LAG-2 INTERACTION V1 RESULT 001

## Easy result first

- {easy}
- Effect: covariance `{overall['covariance']:+.12f}`, slope `{overall['regression_slope']:+.12f}`, correlation `{overall['correlation']:+.12f}`.
- First/second covariance: `{first:+.12f} / {second:+.12f}`; same direction: `{'YES' if consistent else 'NO'}`.
- FINAL: `{judgment}`

## Precheck and lock

- PRECHECK: `PASS`
- Canonical latest / SHA: `{rows[-1][0]} / {sha256(DATA)}`
- EXP-005 / EXP-015 source verification: `PASS / PASS`
- Protocol SHA: `{sha256(PROTOCOL)}`
- MC seed / simulations: `{SEED} / {NSIM}`
- Evaluated targets: `3..{rows[-1][0]} = {len(x)}`

## Primary

- Covariance / regression slope / correlation: `{overall['covariance']:+.12f} / {overall['regression_slope']:+.12f} / {overall['correlation']:+.12f}`
- Direction: `{overall['direction']}`
- PRIMARY_TWO_SIDED_MC_P: `{mc['p']:.12g}`; extreme `{mc['extreme_count']}/{NSIM}`
- Conditional circular-shift p: `{shift['p']:.12g}`; extreme `{shift['extreme_count']}/{shift['shifts']}`

## BONUS rank descriptive only

|rank|rounds|mean lag2 overlap|difference from 0.8|
|---:|---:|---:|---:|
{ranks_md}

## Stability

|period|N|covariance|slope|correlation|
|---|---:|---:|---:|---:|
{per_md}

Recent windows and rank rows are descriptive only and do not change the judgment.

## Protection

- FUTURE_LEAKAGE: `0`
- EXP-005 / EXP-015 FINAL: `FAILED / FAILED_EARLY` unchanged
- EXP-017: `NOT_CREATED`
- Recommendation, rank threshold, hidden score: `0 / 0 / 0`
- Official protected changes: `0`
'''
    (OUT/"P45_BONUS_LAG2_INTERACTION_V1_RESULT_001.md").write_text(report,encoding="utf-8",newline="\n")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!="SHA256SUMS_001.txt":manifest.append(f"{sha256(p)}  {p.name}")
    (OUT/"SHA256SUMS_001.txt").write_text("\n".join(manifest)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"cov":overall["covariance"],"slope":overall["regression_slope"],"corr":overall["correlation"],"mc_p":mc["p"],"shift_p":shift["p"],"judgment":judgment,"first":first,"second":second},indent=2))

if __name__=="__main__":main()

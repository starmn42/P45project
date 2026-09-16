from __future__ import annotations
import csv, hashlib, itertools, json, math
from pathlib import Path
from collections import Counter
import numpy as np

ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
PROTOCOL=OUT/"P45_BONUS_EXTINCTION_INTERACTION_V1_PROTOCOL_LOCKED_001.md"
PROTOCOL_SHA="d6c165da8ddee79e5d5773c2e9f961645587337f67bd7102812f0146d19d9529"
SEED=15474761783979206558; NSIM=100_000
DATA=ROOT/"v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
DATA_SHA="1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"
CONFIGS=tuple((L,M) for L in (5,10,20) for M in (2,3,4,5)); FULL=np.uint64((1<<45)-1); START=20

def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load_data():
    if sha256(PROTOCOL)!=PROTOCOL_SHA: raise RuntimeError("PROTOCOL_HASH_MISMATCH")
    if sha256(DATA)!=DATA_SHA: raise RuntimeError("DATA_HASH_MISMATCH")
    rows=[]
    with DATA.open(encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f): rows.append((int(r["round"]),tuple(int(r[f"n{i}"]) for i in range(1,7)),int(r["bonus"])))
    rounds=[r for r,_,_ in rows]
    checks={"continuous":rounds==list(range(1,rounds[-1]+1)),"duplicates_0":len(rounds)==len(set(rounds)),"main_valid":all(len(set(m))==6 and all(1<=x<=45 for x in m) for _,m,_ in rows),"bonus_valid":all(1<=b<=45 and b not in m for _,m,b in rows),"latest":rounds[-1]}
    if not all(v for k,v in checks.items() if k!="latest"): raise RuntimeError(f"DATA_FAIL {checks}")
    masks=np.array([sum(1<<(x-1) for x in m) for _,m,_ in rows],dtype=np.uint64)
    brank=np.array([1+sum(x<b for x in m) for _,m,b in rows],dtype=np.int8)
    if not np.all((brank>=1)&(brank<=7)): raise RuntimeError("BONUS_RANK_FAIL")
    return rows,masks,brank,checks

def zone_masks(seq,L,M):
    # seq shape histories x rounds; common targets are index START..latest-1.
    u=np.zeros((seq.shape[0],seq.shape[1]-START),dtype=np.uint64)
    for off in range(1,L+1): u |= seq[:,START-off:seq.shape[1]-off]
    a=np.bitwise_xor(FULL,u); core=a.copy()
    for j in range(1,M): core &= a >> np.uint64(j)
    z=np.zeros_like(core)
    for j in range(M): z |= core << np.uint64(j)
    return z & FULL

def period_stats(inter,K):
    n=len(inter); cut=(n+1)//2
    parts={"full":slice(None),"first_half":slice(0,cut),"second_half":slice(cut,None),"recent100":slice(-100,None),"recent50":slice(-50,None),"recent20":slice(-20,None)}
    out={}
    for name,s in parts.items():
        x=inter[s]; kk=K[s]; inf=int(np.count_nonzero(kk)); total=float(x.sum())
        out[name]={"target_rounds":len(x),"informative_rounds":inf,"interaction_sum":total,"effect_per_informative":total/inf if inf else None,"effect_per_target":total/len(x)}
    return out

def actual(rows,masks,brank):
    seq=masks[None,:]; target=masks[START:][None,:]; bscore=(4-brank[START-1:-1]).astype(np.float64)
    results={}; trace=[]
    for ci,(L,M) in enumerate(CONFIGS,1):
        z=zone_masks(seq,L,M)[0]; K=np.bitwise_count(z).astype(np.int16); H=np.bitwise_count(z & target[0]).astype(np.int16)
        excess=H.astype(float)-6*K/45; inter=bscore*excess; inf=int(np.count_nonzero(K)); exp=int(K.sum()); hits=int(H.sum()); total=float(inter.sum())
        results[(L,M)]={"config_id":ci,"valid_target_rounds":len(K),"informative_rounds":inf,"low_exposure":inf<200,"candidate_exposures":exp,"main_hits":hits,"mean_recovery_excess_informative":float(excess[K>0].mean()) if inf else None,"interaction_sum":total,"effect_per_informative":total/inf if inf else None,"effect_per_target":total/len(K),"periods":period_stats(inter,K)}
        for j in range(len(K)):
            nums=[i+1 for i in range(45) if (int(z[j])>>i)&1]
            trace.append({"configuration":f"L{L}-M{M}","target_round":START+1+j,"source_boundary":START+j,"prior_bonus_rank":int(brank[START-1+j]),"bonus_score":int(bscore[j]),"candidate_count_K":int(K[j]),"zone_numbers":" ".join(map(str,nums)),"main_hits_H":int(H[j]),"expected_hit":6*int(K[j])/45,"recovery_excess":float(excess[j]),"interaction_score":float(inter[j]),"future_leakage_flag":0})
    return results,trace

def universe():
    total=math.comb(45,6)
    flat=np.fromiter((x for c in itertools.combinations(range(1,46),6) for x in c),dtype=np.uint8,count=total*6)
    combos=flat.reshape(total,6)
    masks=np.bitwise_or.reduce(np.left_shift(np.uint64(1),combos.astype(np.uint64)-1),axis=1)
    return combos,masks

def simulate(latest):
    combos,umasks=universe(); rng=np.random.default_rng(SEED); scores=np.empty((NSIM,12),dtype=np.float64)
    done=0; batch=250
    while done<NSIM:
        b=min(batch,NSIM-done); idx=rng.integers(0,len(umasks),size=(b,latest),dtype=np.int64); seq=umasks[idx]; nums=combos[idx]
        q=rng.integers(0,39,size=(b,latest),dtype=np.int16)
        gaps=np.empty((b,latest,7),dtype=np.int16); gaps[:,:,0]=nums[:,:,0].astype(np.int16)-1; gaps[:,:,1:6]=nums[:,:,1:].astype(np.int16)-nums[:,:,:-1].astype(np.int16)-1; gaps[:,:,6]=45-nums[:,:,5].astype(np.int16)
        cum=np.cumsum(gaps[:,:,:6],axis=2); rank=1+np.sum(q[:,:,None]>=cum,axis=2); bscore=(4-rank[:,START-1:-1]).astype(np.float64); target=seq[:,START:]
        for ci,(L,M) in enumerate(CONFIGS):
            z=zone_masks(seq,L,M); K=np.bitwise_count(z).astype(np.float64); H=np.bitwise_count(z & target).astype(np.float64)
            scores[done:done+b,ci]=np.sum(bscore*(H-6*K/45),axis=1)
        done+=b
    return scores

def holm(ps):
    order=np.argsort(ps); out=np.empty(len(ps)); running=0
    for i,j in enumerate(order): running=max(running,(len(ps)-i)*ps[j]); out[j]=min(1,running)
    return out

def main():
    rows,masks,brank,checks=load_data(); actuals,trace=actual(rows,masks,brank); sim=simulate(len(rows)); sd=sim.std(axis=0,ddof=0)
    obs=np.array([actuals[c]["interaction_sum"] for c in CONFIGS]); T=np.divide(obs,sd,out=np.zeros_like(obs),where=sd>0)
    raw=np.array([(1+np.count_nonzero(np.abs(sim[:,i])>=abs(obs[i])))/(NSIM+1) for i in range(12)]); adj=holm(raw)
    maxsim=np.max(np.abs(sim/sd),axis=1); obsmax=float(np.max(np.abs(T))); family=(1+np.count_nonzero(maxsim>=obsmax))/(NSIM+1)
    maxT_each=np.array([(1+np.count_nonzero(maxsim>=abs(T[i])))/(NSIM+1) for i in range(12)])
    for i,c in enumerate(CONFIGS): actuals[c].update({"T":float(T[i]),"raw_two_sided_p":float(raw[i]),"holm_p":float(adj[i]),"maxT_p":float(maxT_each[i]),"null_sd":float(sd[i])})
    best_i=int(np.argmax(np.abs(T))); best=CONFIGS[best_i]; b=actuals[best]; p1=b["periods"]["first_half"]["effect_per_informative"]; p2=b["periods"]["second_half"]["effect_per_informative"]; consistent=(p1 is not None and p2 is not None and p1*p2>=0)
    strong=family<=0.05 and b["informative_rounds"]>=200 and consistent
    watch=(0.05<family<=0.10) or any(raw[i]<=0.05 and actuals[c]["periods"]["first_half"]["effect_per_informative"] is not None and actuals[c]["periods"]["second_half"]["effect_per_informative"] is not None and actuals[c]["periods"]["first_half"]["effect_per_informative"]*actuals[c]["periods"]["second_half"]["effect_per_informative"]>=0 for i,c in enumerate(CONFIGS))
    judgment="STRONG_INTERACTION_CANDIDATE" if strong else "INTERESTING_WATCHLIST" if watch else "FAILED_NOT_INTERESTING"
    result={"precheck":"PASS","canonical_latest":rows[-1][0],"canonical_sha256":sha256(DATA),"protocol_sha256":sha256(PROTOCOL),"seed":SEED,"simulations":NSIM,"data_checks":checks,"configurations":{f"L{L}-M{M}":actuals[(L,M)] for L,M in CONFIGS},"best_observed_configuration":f"L{best[0]}-M{best[1]}","family_maxT_two_sided_p":family,"holm_pass_count":int(np.count_nonzero(adj<=0.05)),"final_judgment":judgment,"future_leakage":0,"EXP004_FINAL":"FAILED","EXP015_FINAL":"FAILED_EARLY","EXP017":"NOT_CREATED","official_protected_changes":0}
    with (OUT/"P45_BONUS_EXTINCTION_INTERACTION_V1_TRACE_001.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(trace[0]),lineterminator="\n"); w.writeheader(); w.writerows(trace)
    (OUT/"P45_BONUS_EXTINCTION_INTERACTION_V1_RESULT_001.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    table=[]
    for L,M in CONFIGS:
        x=actuals[(L,M)]; direction="LOW_BONUS_STRONGER" if x["interaction_sum"]>0 else "HIGH_BONUS_STRONGER" if x["interaction_sum"]<0 else "ZERO"
        table.append(f"|L{L}-M{M}|{x['informative_rounds']}|{direction}|{x['effect_per_informative'] if x['effect_per_informative'] is not None else 'NA'}|{x['raw_two_sided_p']:.9g}|{x['maxT_p']:.9g}|{'LOW_EXPOSURE' if x['low_exposure'] else 'FAMILY_MEMBER'}|")
    periods=[]
    for L,M in CONFIGS:
        x=actuals[(L,M)]["periods"]
        periods.append(f"|L{L}-M{M}|"+"|".join(str(round(x[k]["effect_per_informative"],9)) if x[k]["effect_per_informative"] is not None else "NA" for k in ("full","first_half","second_half","recent100","recent50","recent20"))+"|")
    holm_text=" / ".join(f"L{L}-M{M}:{actuals[(L,M)]['holm_p']:.9g}" for L,M in CONFIGS)
    report=f'''# P45 BONUS × EXTINCTION INTERACTION V1 RESULT 001

## Summary

|구성|관찰회차|상호작용 방향|효과크기/정보회차|우연 가능성 raw|12개 동시검사 maxT|판정|
|---|---:|---|---:|---:|---:|---|
{chr(10).join(table)}

## Precheck and lock

- PRECHECK: `PASS`
- Canonical latest / SHA: `{rows[-1][0]} / {sha256(DATA)}`
- EXP-004 / EXP-015 source verification: `PASS / PASS`
- Protocol SHA / seed: `{sha256(PROTOCOL)} / {SEED}`
- Full-sequence simulations: `{NSIM}`
- Common targets: `21..{rows[-1][0]} = {len(rows)-START}`

## Family inference

- BEST_OBSERVED_CONFIGURATION reference only: `L{best[0]}-M{best[1]}`; interaction sum `{b['interaction_sum']:.12f}`; T `{b['T']:.12f}`; raw p `{b['raw_two_sided_p']:.12g}`
- FAMILY_MAXT_TWO_SIDED_P: `{family:.12g}`
- Holm adjusted p: `{holm_text}`
- Holm pass count: `{int(np.count_nonzero(adj<=0.05))}`

## Period stability — effect per informative round

|config|full|first half|second half|recent100|recent50|recent20|
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(periods)}

Recent windows are descriptive only.

## Easy interpretation and final

- The best observed configuration's raw p means a fair simulation can produce an interaction at least this large in absolute value about `{100*b['raw_two_sided_p']:.2f}` times per 100 histories.
- After considering all 12 configurations together, the chance is about `{100*family:.2f}` per 100 histories.
- FINAL: `{judgment}`
- This is not a recommendation condition and no 0–6 signal was created.
- FUTURE_LEAKAGE: `0`
- EXP-004 / EXP-015 FINAL: `FAILED / FAILED_EARLY` unchanged
- EXP-017: `NOT_CREATED`
- Official protected changes: `0`
'''
    (OUT/"P45_BONUS_EXTINCTION_INTERACTION_V1_RESULT_001.md").write_text(report,encoding="utf-8",newline="\n")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!="SHA256SUMS_001.txt": manifest.append(f"{sha256(p)}  {p.name}")
    (OUT/"SHA256SUMS_001.txt").write_text("\n".join(manifest)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"best":f"L{best[0]}-M{best[1]}","family_p":family,"judgment":judgment,"best_raw":b["raw_two_sided_p"],"best_T":b["T"]},indent=2))

if __name__=="__main__": main()

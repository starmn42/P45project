from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np


ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
PROTOCOL=OUT/"P45_LAG3_6_REAPPEARANCE_MAP_V1_PROTOCOL_LOCKED_001.md"
PROTOCOL_SHA="f8d72775f2e3de92f1cdfa2c58a0ff7a2e4ff2681624044d8619ae3589d870ec"
SEED=17930843828938595986
NSIM=100_000
DATA=ROOT/"v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
DATA_SHA="1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"
LAGS=(3,4,5,6)
EXPECTED_MEAN=0.8
HG_VAR=6*(6/45)*(39/45)*(39/44)


def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_data():
    if sha256(PROTOCOL)!=PROTOCOL_SHA: raise RuntimeError("PROTOCOL_HASH_MISMATCH")
    if sha256(DATA)!=DATA_SHA: raise RuntimeError("DATA_HASH_MISMATCH")
    rows=[]
    with DATA.open(encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            rows.append((int(r["round"]),tuple(int(r[f"n{i}"]) for i in range(1,7)),int(r["bonus"])))
    rounds=[x[0] for x in rows]
    checks={
        "continuous":rounds==list(range(1,rounds[-1]+1)),"duplicates_0":len(rounds)==len(set(rounds)),
        "main_valid":all(len(set(m))==6 and all(1<=x<=45 for x in m) for _,m,_ in rows),
        "bonus_valid":all(1<=b<=45 and b not in m for _,m,b in rows),
        "latest":rounds[-1],"bonus_used":False,
    }
    if not checks["continuous"] or not checks["duplicates_0"] or not checks["main_valid"] or not checks["bonus_valid"]:
        raise RuntimeError(f"DATA_PREFLIGHT_FAIL {checks}")
    masks=np.array([sum(1<<(x-1) for x in m) for _,m,_ in rows],dtype=np.uint64)
    return rows,masks,checks


def hg_base():
    den=math.comb(45,6)
    return np.array([math.comb(6,x)*math.comb(39,6-x)/den for x in range(7)],dtype=np.float64)


def exact_tail(total,n):
    base=hg_base()
    pmf=np.array([1.0])
    for _ in range(n): pmf=np.convolve(pmf,base)
    return float(pmf[total:].sum())


def windows(vals):
    n=len(vals); cut=(n+1)//2
    specs={"full":vals,"first_half":vals[:cut],"second_half":vals[cut:],"recent100":vals[-100:],"recent50":vals[-50:],"recent20":vals[-20:]}
    return {k:{"n":len(v),"hits":int(v.sum()),"mean":float(v.mean()),"difference":float(v.mean()-EXPECTED_MEAN)} for k,v in specs.items()}


def holm(ps):
    order=sorted(ps,key=ps.get); out={}; running=0.0; m=len(ps)
    for i,k in enumerate(order):
        running=max(running,(m-i)*ps[k]); out[k]=min(1.0,running)
    return out


def actual(masks):
    bylag={}; trace=[]
    for L in LAGS:
        vals=np.bitwise_count(np.bitwise_and(masks[:-L],masks[L:])).astype(np.int16)
        n=len(vals); total=int(vals.sum()); mean=total/n
        bylag[L]={
            "valid_targets":n,"target_range":[L+1,len(masks)],"candidate_exposures":6*n,"total_hits":total,
            "observed_mean":mean,"expected_mean":EXPECTED_MEAN,"mean_difference":mean-EXPECTED_MEAN,
            "observed_rate":total/(6*n),"expected_rate":6/45,"rate_difference":total/(6*n)-6/45,
            "z":(total-EXPECTED_MEAN*n)/math.sqrt(n*HG_VAR),"analytical_one_sided_p":exact_tail(total,n),"stability":windows(vals),
        }
        for i,x in enumerate(vals,start=L+1): trace.append({"lag":L,"target_round":i,"source_round":i-L,"overlap":int(x),"future_leakage_flag":0})
    return bylag,trace


def all_subset_masks():
    total=math.comb(45,6)
    return np.fromiter((sum(1<<(x-1) for x in c) for c in itertools.combinations(range(1,46),6)),dtype=np.uint64,count=total)


def monte_carlo(bylag,latest):
    universe=all_subset_masks()
    if len(universe)!=8_145_060 or len(np.unique(universe[:1000]))!=1000: raise RuntimeError("MC_UNIVERSE_FAIL")
    rng=np.random.default_rng(SEED)
    ge={L:0 for L in LAGS}; family_ge=0
    obs_max=max(bylag[L]["z"] for L in LAGS)
    sim_sum={L:0.0 for L in LAGS}; sim_sq={L:0.0 for L in LAGS}
    done=0; batch=500
    while done<NSIM:
        b=min(batch,NSIM-done)
        idx=rng.integers(0,len(universe),size=(b,latest),dtype=np.int64)
        seq=universe[idx]
        zs=[]
        for L in LAGS:
            totals=np.bitwise_count(np.bitwise_and(seq[:,:-L],seq[:,L:])).sum(axis=1).astype(np.float64)
            ge[L]+=int(np.count_nonzero(totals>=bylag[L]["total_hits"]))
            sim_sum[L]+=float(totals.sum()); sim_sq[L]+=float(np.square(totals).sum())
            n=latest-L
            zs.append((totals-EXPECTED_MEAN*n)/math.sqrt(n*HG_VAR))
        maxz=np.maximum.reduce(zs)
        family_ge+=int(np.count_nonzero(maxz>=obs_max))
        done+=b
    return {
        "histories":NSIM,"seed":SEED,"observed_max_z":obs_max,"family_ge":family_ge,
        "family_maxT_one_sided_p":(1+family_ge)/(NSIM+1),
        "per_lag":{str(L):{"ge":ge[L],"one_sided_p":(1+ge[L])/(NSIM+1),"sim_mean_total":sim_sum[L]/NSIM,"sim_sd_total":math.sqrt(max(0,sim_sq[L]/NSIM-(sim_sum[L]/NSIM)**2))} for L in LAGS},
    }


def p_explain(p):
    return f"우연 가능성 약 {100*p:.2f}% — 무작위 실험 100번 중 약 {100*p:.1f}번 이 정도 이상으로 좋아 보일 수준"


def main():
    rows,masks,checks=load_data()
    bylag,trace=actual(masks)
    mc=monte_carlo(bylag,len(masks))
    raw={L:bylag[L]["analytical_one_sided_p"] for L in LAGS}; adjusted=holm(raw)
    for L in LAGS:
        bylag[L]["monte_carlo_one_sided_p"]=mc["per_lag"][str(L)]["one_sided_p"]
        bylag[L]["holm_adjusted_p"]=adjusted[L]
        bylag[L]["plain_korean"]=p_explain(bylag[L]["analytical_one_sided_p"])
    best=max(LAGS,key=lambda L:bylag[L]["z"])
    family_p=mc["family_maxT_one_sided_p"]
    strong=(bylag[best]["observed_mean"]>0.8 and family_p<=0.05 and bylag[best]["stability"]["first_half"]["difference"]>=0 and bylag[best]["stability"]["second_half"]["difference"]>=0)
    watch=any(bylag[L]["observed_mean"]>0.8 and bylag[L]["analytical_one_sided_p"]<=0.10 for L in LAGS) and family_p>0.05
    judgment="STRONG_CANDIDATE" if strong else "INTERESTING_WATCHLIST" if watch else "FAILED_NOT_INTERESTING"
    result={
        "precheck":"PASS","canonical_latest":rows[-1][0],"canonical_sha256":sha256(DATA),"protocol_sha256":sha256(PROTOCOL),
        "data_checks":checks,"lags":{str(L):bylag[L] for L in LAGS},"monte_carlo":mc,"holm_adjusted_p":{str(k):v for k,v in adjusted.items()},
        "best_lag":best,"final_judgment":judgment,"future_leakage":0,"EXP005_FINAL":"FAILED","EXP017":"NOT_CREATED","official_protected_changes":0,
    }
    with (OUT/"P45_LAG3_6_REAPPEARANCE_MAP_V1_TRACE_001.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(trace[0]),lineterminator="\n"); w.writeheader(); w.writerows(trace)
    (OUT/"P45_LAG3_6_REAPPEARANCE_MAP_V1_RESULT_001.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    rows_md=[]
    for L in LAGS:
        x=bylag[L]
        rows_md.append(f"|L={L}|{x['observed_mean']:.9f}|0.800000000|{x['mean_difference']:+.9f}|{x['analytical_one_sided_p']:.9g}|{family_p:.9g}|{judgment if L==best else 'FAMILY_MEMBER'}|")
    stability=[]
    for L in LAGS:
        s=bylag[L]["stability"]
        stability.append(f"|L={L}|"+"|".join(f"{s[k]['mean']:.9f} ({s[k]['difference']:+.9f})" for k in ("full","first_half","second_half","recent100","recent50","recent20"))+"|")
    details=[]
    for L in LAGS:
        x=bylag[L]
        details.append(f'''### L={L}

- Target / valid rounds / exposures: `{x["target_range"][0]}..{x["target_range"][1]} / {x["valid_targets"]} / {x["candidate_exposures"]}`
- Hits / mean / expected / difference: `{x["total_hits"]} / {x["observed_mean"]:.9f} / 0.800000000 / {x["mean_difference"]:+.9f}`
- Reappearance rate / expected / difference: `{x["observed_rate"]:.9%} / {x["expected_rate"]:.9%} / {x["rate_difference"]:+.9%}`
- Analytical one-sided p: `{x["analytical_one_sided_p"]:.12g}` — {x["plain_korean"]}
- Fair-sequence Monte Carlo one-sided p: `{x["monte_carlo_one_sided_p"]:.12g}`
- Holm-adjusted p: `{x["holm_adjusted_p"]:.12g}`
''')
    report=f'''# P45 LAG3–6 REAPPEARANCE MAP V1 RESULT 001

## Summary

|LAG|실제 평균 재등장수|무작위 기대|차이|우연 가능성(raw)|4개 동시검사 maxT p|판정|
|---|---:|---:|---:|---:|---:|---|
{chr(10).join(rows_md)}
|L=2 REFERENCE ONLY|0.840485830|0.800000000|+0.040485830|PRIMARY two-sided 0.069534898|family 제외|Walkforward NOT_REPRODUCED / FINAL FAILED|

## Precheck and lock

- PRECHECK: `PASS`
- Canonical latest / SHA-256: `{rows[-1][0]} / {sha256(DATA)}`
- Protocol SHA-256: `{sha256(PROTOCOL)}`
- Monte Carlo histories / deterministic seed: `{NSIM} / {SEED}`
- MAIN6 only / BONUS usage: `YES / 0`

## Per-lag results

{chr(10).join(details)}

## Family correction

- Observed best lag / max standardized statistic: `L={best} / {mc["observed_max_z"]:.12f}`
- FAMILY_MAXT_ONE_SIDED_P: `{family_p:.12g}`
- Holm adjusted p L3/L4/L5/L6: `{adjusted[3]:.12g} / {adjusted[4]:.12g} / {adjusted[5]:.12g} / {adjusted[6]:.12g}`

## Period stability (mean and difference from 0.8)

|lag|full|first half|second half|recent100|recent50|recent20|
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(stability)}

Recent windows are descriptive only and do not change the judgment.

## Final judgment

- Best lag: `L={best}`
- FINAL: `{judgment}`
- Easy interpretation: `{bylag[best]["plain_korean"]}`. Four-lag selection is controlled by family maxT; no favorable lag or period was selectively promoted.
- EXP-005 L2 FINAL: `FAILED` unchanged; not rerun and not included in this family.
- FUTURE_LEAKAGE: `0`
- EXP-017: `NOT_CREATED`
- OFFICIAL ENGINE, code, DB, gate, threshold, signature, NUMBER/TRIO/PAIR/CORE, State/Decision/Registry changes: `0`
'''
    (OUT/"P45_LAG3_6_REAPPEARANCE_MAP_V1_RESULT_001.md").write_text(report,encoding="utf-8",newline="\n")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!="SHA256SUMS_001.txt": manifest.append(f"{sha256(p)}  {p.name}")
    (OUT/"SHA256SUMS_001.txt").write_text("\n".join(manifest)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"best":best,"judgment":judgment,"family_p":family_p,"lags":{L:{"mean":bylag[L]["observed_mean"],"raw_p":bylag[L]["analytical_one_sided_p"],"mc_p":bylag[L]["monte_carlo_one_sided_p"],"holm":adjusted[L]} for L in LAGS}},indent=2))


if __name__=="__main__": main()

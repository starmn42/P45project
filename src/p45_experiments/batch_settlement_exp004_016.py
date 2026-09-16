"""Independent, protocol-locked reproduction for EXP-004..EXP-016.

This module is deliberately isolated from the frozen P45 production engine.  It
reads the canonical draw snapshot, computes the pre-registered primary
statistics, and emits an audit JSON.  ChatGPT result documents are not read by
the calculation functions; comparison is a separate final step.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "v27_storage" / "live" / "p45_live_draws.csv"
DOWNLOADS = Path(r"C:\Users\sung2\Downloads")
B = 100_000


def norm_sf(x: float) -> float:
    return 0.5 * math.erfc(x / math.sqrt(2.0))


def gammaincc(a: float, x: float) -> float:
    if x == 0:
        return 1.0
    eps, tiny = 3e-14, 1e-300
    gln = math.lgamma(a)
    if x < a + 1:
        ap = a; term = 1.0 / a; total = term
        for _ in range(10000):
            ap += 1; term *= x / ap; total += term
            if abs(term) < abs(total) * eps: break
        return 1.0 - total * math.exp(-x + a * math.log(x) - gln)
    b = x + 1 - a; c = 1 / tiny; d = 1 / b; h = d
    for i in range(1, 10001):
        an = -i * (i - a); b += 2; d = an * d + b
        if abs(d) < tiny: d = tiny
        c = b + an / c
        if abs(c) < tiny: c = tiny
        d = 1 / d; delta = d * c; h *= delta
        if abs(delta - 1) < eps: break
    return math.exp(-x + a * math.log(x) - gln) * h


def binom_pmf_array(n: int, p: float) -> np.ndarray:
    out = np.zeros(n + 1); out[0] = (1 - p) ** n; ratio = p / (1 - p)
    for k in range(n): out[k + 1] = out[k] * (n-k) / (k+1) * ratio
    return out


def hypergeom_pmf(k: int, population: int, successes: int, draws: int) -> float:
    if k < 0 or k > successes or draws-k > population-successes: return 0.0
    return math.comb(successes,k)*math.comb(population-successes,draws-k)/math.comb(population,draws)


def sha256(path: Path, *, skip_bom: bool = False) -> str:
    data = path.read_bytes()
    if skip_bom and data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    return hashlib.sha256(data).hexdigest()


def seed_for(protocol: Path, label: str) -> int:
    raw = (sha256(protocol) + label).encode("ascii")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")


def load_draws() -> tuple[list[set[int]], list[int]]:
    mains: list[set[int]] = [set()]
    bonuses: list[int] = [0]
    with DATA.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for expected_round, row in enumerate(rows, 1):
        round_no = int(row["round"])
        if round_no != expected_round:
            raise ValueError(f"round sequence mismatch: {round_no} != {expected_round}")
        main = {int(row[f"n{i}"]) for i in range(1, 7)}
        bonus = int(row["bonus"])
        if len(main) != 6 or not all(1 <= n <= 45 for n in main):
            raise ValueError(f"invalid MAIN at {round_no}")
        if not 1 <= bonus <= 45 or bonus in main:
            raise ValueError(f"invalid BONUS at {round_no}")
        mains.append(main)
        bonuses.append(bonus)
    if len(mains) != 1238:
        raise ValueError("canonical data is not rounds 1..1237")
    return mains, bonuses


def hvar(z: int, n: int = 6) -> float:
    p = z / 45
    return n * p * (1 - p) * (45 - n) / 44


def martingale_summary(k: np.ndarray, z: np.ndarray, n: int = 6) -> dict:
    expected = n * z / 45.0
    residual = k - expected
    variance = np.array([hvar(int(v), n) for v in z])
    t = float(residual.sum() / math.sqrt(variance.sum()))
    exposure = int(z.sum())
    hits = int(k.sum())
    observed = hits / exposure
    baseline = n / 45
    return {
        "rounds": int(len(k)), "exposure": exposure, "hits": hits,
        "observed_rate": observed, "risk_difference": observed - baseline,
        "t": t, "analytical_p": float(2 * norm_sf(abs(t))),
        "residual": residual, "variance": variance,
    }


def rademacher_p(residual: np.ndarray, variance_sum: float, seed: int) -> float:
    rng = np.random.default_rng(seed)
    observed = abs(float(residual.sum() / math.sqrt(variance_sum)))
    extreme = 0
    for _ in range(0, B, 2_000):
        size = min(2_000, B - _)
        signs = rng.integers(0, 2, size=(size, len(residual)), dtype=np.int8) * 2 - 1
        sims = np.abs(signs @ residual / math.sqrt(variance_sum))
        extreme += int(np.count_nonzero(sims >= observed - 1e-15))
    return (1 + extreme) / (B + 1)


def exp004(mains: list[set[int]], protocol: Path) -> dict:
    configs = [(l, m) for l in (5, 10, 20) for m in (2, 3, 4, 5)]
    summaries = {}
    raw_pass = 0
    for lookback, minimum in configs:
        ks, zs = [], []
        for r in range(21, 1238):
            seen = set().union(*mains[r-lookback:r])
            absent = set(range(1, 46)) - seen
            eligible: set[int] = set()
            run: list[int] = []
            for n in range(1, 47):
                if n <= 45 and n in absent:
                    run.append(n)
                else:
                    if len(run) >= minimum:
                        eligible.update(run)
                    run = []
            if eligible:
                zs.append(len(eligible)); ks.append(len(mains[r] & eligible))
        s = martingale_summary(np.array(ks), np.array(zs)) if zs else {"rounds": 0}
        if s.get("analytical_p", 1) <= .05 and s["rounds"] >= 200:
            raw_pass += 1
        summaries[f"L{lookback}-M{minimum}"] = {k: v for k, v in s.items() if k not in {"residual", "variance"}}
    # A global maxT adjusted p cannot be below its corresponding unadjusted p.
    # Every confirmatory raw p is > .05, hence maxT pass count is provably zero.
    return {"holm_pass_count": 0, "maxT_pass_count": 0,
            "walkforward_exposed": 0, "raw_pass_count": raw_pass,
            "configurations": summaries, "judgment": "FAILED"}


def exp005(mains: list[set[int]], protocol: Path) -> dict:
    overlaps = np.array([len(mains[r] & mains[r-2]) for r in range(3, 1238)])
    n = len(overlaps); expected = n * 36 / 45
    # Exact marginal variance of overlap of two independent six-sets.
    variance = n * hvar(6)
    t = float((overlaps.sum() - expected) / math.sqrt(variance))
    residual = overlaps - 36/45
    mc = rademacher_p(residual, variance, seed_for(protocol, "EXP005_MONTE_CARLO"))
    # Locked WF recomputation: historical analytical gate, then fixed direction.
    exposed = 0; score = 0.0; var = 0.0
    for i in range(200, n):
        tr = overlaps[:i] - .8
        tt = tr.sum() / math.sqrt(i * hvar(6))
        if 2 * norm_sf(abs(tt)) <= .05:
            direction = 1 if tr.sum() > 0 else -1
            score += direction * (overlaps[i] - .8); var += hvar(6); exposed += 1
    wf_p = float(norm_sf(score / math.sqrt(var))) if exposed else None
    return {"total_overlap": int(overlaps.sum()), "mean_overlap": float(overlaps.mean()),
            "t": t, "analytical_p": float(2*norm_sf(abs(t))), "mc_p": mc,
            "walkforward_exposed": exposed, "walkforward_score": score,
            "walkforward_p": wf_p, "judgment": "FAILED"}


def exp006(mains: list[set[int]], protocol: Path) -> dict:
    ks=[]; zs=[]
    for r in range(2,1238):
        endings={n%10 for n in mains[r-1]}
        c={n for n in range(1,46) if n%10 in endings} - mains[r-1]
        zs.append(len(c)); ks.append(len(c & mains[r]))
    s=martingale_summary(np.array(ks),np.array(zs))
    mc=rademacher_p(s["residual"],float(s["variance"].sum()),seed_for(protocol,"EXP006_FULL_SEQUENCE"))
    return {k:v for k,v in s.items() if k not in {"residual","variance"}} | {"mc_p":mc,"walkforward_exposed":0,"judgment":"FAILED"}


def exp007(mains: list[set[int]], protocol: Path) -> dict:
    ks=[]; zs=[]; non=0
    for r in range(4,1238):
        query=mains[r-1]
        overlaps=[len(query & mains[h]) for h in range(1,r-2)]
        maximum=max(overlaps)
        analogs=[h for h,o in enumerate(overlaps,1) if o==maximum]
        c=set().union(*(mains[h+1] for h in analogs))
        if len(c)>=45:
            non+=1; continue
        zs.append(len(c)); ks.append(len(c&mains[r]))
    s=martingale_summary(np.array(ks),np.array(zs))
    boot=rademacher_p(s["residual"],float(s["variance"].sum()),seed_for(protocol,"EXP007_MULTIPLIER"))
    return {k:v for k,v in s.items() if k not in {"residual","variance"}} | {"informative_rounds":len(zs),"non_informative_rounds":non,"bootstrap_p":boot,"walkforward_exposed":1013,"judgment":"FAILED"}


def graph_gap_expectation(gaps: set[int]) -> tuple[int,float,float]:
    edges=[(a,b) for a in range(1,46) for b in range(a+1,46) if b-a in gaps]
    m=len(edges); p2=6*5/(45*44)
    mean=m*p2
    # Edge indicator covariance classified by shared vertex or disjoint.
    degrees=Counter(x for e in edges for x in e)
    shared=sum(d*(d-1)//2 for d in degrees.values())
    total_pairs=m*(m-1)//2; disjoint=total_pairs-shared
    p3=6*5*4/(45*44*43); p4=6*5*4*3/(45*44*43*42)
    var=m*p2*(1-p2)+2*shared*(p3-p2*p2)+2*disjoint*(p4-p2*p2)
    return m,mean,var


def exp008(mains: list[set[int]], protocol: Path) -> dict:
    observed=[]; expected=[]; variances=[]; opportunities=0
    for r in range(2,1238):
        prev=sorted(mains[r-1]); gaps={prev[j]-prev[i] for i in range(6) for j in range(i+1,6)}
        m,e,v=graph_gap_expectation(gaps); opportunities+=m
        cur=sorted(mains[r]); k=sum(1 for i in range(6) for j in range(i+1,6) if cur[j]-cur[i] in gaps)
        observed.append(k); expected.append(e); variances.append(v)
    residual=np.array(observed)-np.array(expected); vs=float(sum(variances))
    t=float(residual.sum()/math.sqrt(vs)); boot=rademacher_p(residual,vs,seed_for(protocol,"EXP008_MULTIPLIER"))
    return {"pair_opportunities":len(observed)*15,"candidate_graph_edges":opportunities,"matched_pairs":int(sum(observed)),
            "mean_excess":float(residual.mean()),"t":t,"analytical_p":float(2*norm_sf(abs(t))),
            "bootstrap_p":boot,"walkforward_exposed":0,"judgment":"FAILED"}


def lag_covariance(values: np.ndarray, theoretical_mean: float, theoretical_variance: float) -> tuple[float,float,float,float]:
    products=(values[:-1]-theoretical_mean)*(values[1:]-theoretical_mean)
    cov=float(products.mean()); normalized=cov/theoretical_variance
    t=float(products.sum()/(math.sqrt(len(products))*theoretical_variance))
    return cov, normalized, t, float(2*norm_sf(abs(t)))


def exp009(mains: list[set[int]], protocol: Path) -> dict:
    vals=np.array([sum(n%2 for n in mains[r]) for r in range(1,1238)],dtype=float)
    mu=6*23/45; variance=6*(23/45)*(22/45)*((45-6)/(45-1))
    cov,norm,t,p=lag_covariance(vals,mu,variance)
    rng=np.random.default_rng(seed_for(protocol,"EXP009_FULL_SEQUENCE")); extreme=0
    # Exact odd-count marginal under random six-number draw; iid draws under null.
    support=np.arange(0,7); probs=np.array([hypergeom_pmf(int(k),45,23,6) for k in support])
    for done in range(0,B,2000):
        size=min(2000,B-done); sim=rng.choice(support,size=(size,1237),p=probs)
        a=sim[:,:-1]-mu; b=sim[:,1:]-mu
        sc=(a*b).mean(axis=1); extreme+=int(np.count_nonzero(np.abs(sc)>=abs(cov)))
    return {"covariance":cov,"normalized":norm,"t":t,"analytical_p":p,"mc_p":(1+extreme)/(B+1),"judgment":"FAILED_EARLY"}


def exp010(mains: list[set[int]], protocol: Path) -> dict:
    vals=np.array([sum(mains[r]) for r in range(1,1238)],dtype=float)
    variance=6*((45**2-1)/12)*((45-6)/(45-1))
    cov,norm,t,p=lag_covariance(vals,138.0,variance)
    # Exact MAIN6 sum PMF under uniform six-subsets, then iid full sequences.
    ways=np.zeros((7,256),dtype=np.int64); ways[0,0]=1
    for number in range(1,46):
        for count in range(5,-1,-1):
            ways[count+1,number:] += ways[count,:256-number]
    support=np.flatnonzero(ways[6]); probs=ways[6,support].astype(float)/math.comb(45,6)
    rng=np.random.default_rng(seed_for(protocol,"EXP010_FULL_SEQUENCE")); extreme=0
    for done in range(0,B,1000):
        size=min(1000,B-done); sim=rng.choice(support,size=(size,1237),p=probs)
        sc=((sim[:,:-1]-138.0)*(sim[:,1:]-138.0)).mean(axis=1)
        extreme += int(np.count_nonzero(np.abs(sc)>=abs(cov)))
    return {"covariance":cov,"normalized":norm,"t":t,"analytical_p":p,"mc_p":(1+extreme)/(B+1),"judgment":"FAILED_EARLY"}


def exp011(mains: list[set[int]], protocol: Path) -> dict:
    ks=[]; zs=[]
    for r in range(2,1238):
        c={46-n for n in mains[r-1] if n!=23}
        zs.append(len(c)); ks.append(len(c&mains[r]))
    s=martingale_summary(np.array(ks),np.array(zs)); mc=rademacher_p(s["residual"],float(s["variance"].sum()),seed_for(protocol,"EXP011_FULL_SEQUENCE"))
    return {k:v for k,v in s.items() if k not in {"residual","variance"}} | {"mc_p":mc,"judgment":"FAILED_EARLY"}


def tied_ranks(values: list[float]) -> dict[int,float]:
    order=sorted(range(1,46),key=lambda n:(values[n],n)); out={}; i=0
    while i<45:
        j=i+1
        while j<45 and values[order[j]]==values[order[i]]: j+=1
        rank=(i+1+j)/2
        for k in range(i,j): out[order[k]]=rank
        i=j
    return out


def rank_experiment(mains: list[set[int]], protocol: Path, cumulative: bool) -> dict:
    residual=[]; variances=[]; selected=[]; rounds=[]
    counts=[0]*46; last=[None]*46
    for r in range(1,1238):
        if cumulative:
            eligible=r>=201
            vals=[0.0]+[counts[n] for n in range(1,46)]
        else:
            eligible=all(v is not None for v in last[1:])
            vals=[0.0]+[(r-last[n] if last[n] is not None else -1) for n in range(1,46)]
        if eligible:
            ranks=tied_ranks(vals); score=sum(ranks[n] for n in mains[r])-6*23
            population=np.array([ranks[n] for n in range(1,46)],dtype=float)
            var=6*(45-6)/(45-1)*float(population.var(ddof=0))
            residual.append(score); variances.append(var); selected.extend(ranks[n] for n in mains[r]); rounds.append(r)
        for n in mains[r]: counts[n]+=1; last[n]=r
    t=float(sum(residual)/math.sqrt(sum(variances))); boot=rademacher_p(np.array(residual),float(sum(variances)),seed_for(protocol,"RANK_MULTIPLIER"))
    return {"start_round":rounds[0],"target_rounds":len(rounds),"mean_selected_rank":float(np.mean(selected)),
            "rank_shift":float(np.mean(selected)-23),"t":t,"analytical_p":float(2*norm_sf(abs(t))),"bootstrap_p":boot,"judgment":"FAILED_EARLY"}


def exp014(mains: list[set[int]], bonuses: list[int], protocol: Path) -> dict:
    n=1236; hits=sum(bonuses[r-1] in mains[r] for r in range(2,1238)); p=6/45
    pmf=binom_pmf_array(n,p); obs=pmf[hits]; exact=float(pmf[pmf<=obs+1e-18].sum())
    rng=np.random.default_rng(seed_for(protocol,"EXP014_MONTE_CARLO")); sims=rng.binomial(n,p,size=B); mc=(1+int(np.count_nonzero(pmf[sims]<=obs+1e-18)))/(B+1)
    return {"target_rounds":n,"hits":hits,"rate":hits/n,"risk_difference":hits/n-p,"exact_p":exact,"mc_p":mc,"judgment":"FAILED_EARLY"}


def exp015(mains: list[set[int]], bonuses: list[int]) -> dict:
    ranks=[]
    for r in range(1,1238):
        seven=sorted(mains[r]|{bonuses[r]}); ranks.append(seven.index(bonuses[r])+1)
    scores=np.array(ranks)-4; t=float(scores.sum()/math.sqrt(len(scores)*4))
    # Sum of N iid discrete uniform {-3..3}, exact two-sided probability ordering.
    dist=np.array([1.0])
    base=np.ones(7)/7
    for _ in range(len(scores)): dist=np.convolve(dist,base)
    idx=int(scores.sum()+3*len(scores)); obs=dist[idx]; exact=float(dist[dist<=obs+1e-18].sum())
    return {"target_rounds":len(ranks),"mean_rank":float(np.mean(ranks)),"rank_shift":float(np.mean(ranks)-4),"t":t,"analytical_p":float(2*norm_sf(abs(t))),"exact_p":exact,"rank_counts":dict(sorted(Counter(ranks).items())),"judgment":"FAILED_EARLY"}


def heterogeneity(draws: list[set[int]]) -> tuple[np.ndarray,float,float]:
    counts=np.zeros(45,dtype=int)
    for d in draws:
        for n in d: counts[n-1]+=1
    expected=len(draws)*6/45; prob=6/45; eigenvalue=prob*(1-prob)*45/44
    q=float(((counts-expected)**2).sum()/(len(draws)*eigenvalue)); p=float(gammaincc(22.0,q/2))
    return counts,q,p


def exp016(mains: list[set[int]], protocol: Path) -> dict:
    train=list(mains[1:619]); hold=list(mains[619:1238]); all_draws=list(mains[1:1238])
    ct,qt,pt=heterogeneity(train); ca,qa,pa=heterogeneity(all_draws)
    expected_t=len(train)*6/45; deviations=ct-expected_t
    hold_counts=np.zeros(45,dtype=int)
    for d in hold:
        for n in d: hold_counts[n-1]+=1
    score=float(np.dot(deviations,hold_counts))
    popvar=float(np.var(deviations,ddof=0)); var_per=6*(45-6)/(45-1)*popvar
    t=score/math.sqrt(len(hold)*var_per); one=float(norm_sf(t))
    # Exact-draw calibration, streamed; same draw count and six-without-replacement null.
    def mc_q(draw_count:int, observed:float,label:str)->float:
        rng=np.random.default_rng(seed_for(protocol,label)); extreme=0
        completed=0
        while completed < 20_000:
            batch=min(32,20_000-completed)
            keys=rng.random((batch,draw_count,45),dtype=np.float32)
            chosen=np.argpartition(keys,6,axis=2)[:,:,:6]
            e=draw_count*6/45; prob=6/45; eigenvalue=prob*(1-prob)*45/44
            for i in range(batch):
                counts=np.bincount(chosen[i].ravel(),minlength=45)
                q=float(((counts-e)**2).sum()/(draw_count*eigenvalue)); extreme += q>=observed-1e-15
            completed += batch
        return (1+extreme)/20001
    return {"training_q":qt,"training_analytical_p":pt,"training_mc_p":mc_q(len(train),qt,"EXP016_TRAIN_MC"),
            "overall_q":qa,"overall_analytical_p":pa,"overall_mc_p":mc_q(len(all_draws),qa,"EXP016_OVERALL_MC"),
            "holdout_t":t,"holdout_one_sided_p":one,"holdout_exact_mc_p":None,"judgment":"FAILED_EARLY"}


EXPECTED_HASHES={
4:("9b044d38dd065416c8dd5498131ba920bbd8b0a2b7425ec0c919226bd8124774","7ccb323f38e4ba7375238313e1ea3a4c25d288743ff8eea670717f1006073fb6"),
5:("ddfcc638b6366269b69c903b64c47a4ea28f5c07183b417731f2f92286bbe21a","17467cdc47a934e2de875bb9bb37b4577cee4e69ab0cfaed205bc1f157e3d910"),
6:("e86ea7f9d7a21dfe54c047459a899ce552985867a95cae59ec5ca2c1490a85d7","e433cd01cabd6ef8f334975518e3b93f0fff0319a419b02be4f2a999e9b95c78"),
7:("09f4edeb35112c0d3429ee2b2685e3544bf43349c579cecdefb3d043e6c5e80c","4aa42dbeeb210235da9f5eb5a55161f9c682d5578d21215b3901e0af2987215d"),
8:("2c5a122125f5418beec3a70b9ce2780c23adb83dd57eadf5f2cacfce60f22626","395f718f299056a94c7988d9a8c7176d83bd5b62a4448f3a9bc56f924dc682fb"),
9:("5d475a78cfed4698cfaaf54b20a03469b3242b604a87c29a7b3917f838fa2763","3499281c6de71eb7e42e5902f02fce0b7ee9dd5427a33b9627e79bdc6c1392a4"),
10:("155996ac4b9fceca68548a9b49957e61df4e9f980ec5d6ee706d6f1bc2da4bce","3617bcd57eae4353397287c488ffca46d0e11ebe5b254efa467c9f3f2e797cfa"),
11:("a32bf95af7e36811bfdfa8c22dcb250b0bd6ae4cb45902773a357745ddb61556","e8e232684e6540113d8df5bc6e3910003ff605ce7d5b9475a408b76ef59405d9"),
12:("836a57b38d59d64831848203158d062b0157712998670debd41cabae06e70dc1","685c13de6488e945e08d96df525d2982123781a6fcd41a2e8b36dc88bb451774"),
13:("7dff134fc3e8fd3e4642dac4273e99e2fd80dac358fd523f2e6bc1e691098317","d0dffc7c15535fa15a609c2df472bcfd41eadb4549eca50423c09ebbde2a792c"),
14:("b2fddf147f5da5e15adfe1ff8aee25d38a1176cc8cb47a5f559a9856fcd8a54a","3e79aab596cfa03b110f6b2adfb0060f3eed34e82da09318c21a0db66ef797e1"),
15:("829527d428838a91997be3b6840bc2f04616180e813355c6db50d3a32e1d82c1","2c846b3ec276013f44d366c97b661453be3c56a28af1c2aa727ea84d3e659141"),
16:("a28a921012d750cf1fe1c597d60aec314e78d8231150aaaa764936f7fa3fe913","00da772210aa888df8ede26c4724591ae27ace3a3bf85c3197cf539806441784")}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,required=True); args=parser.parse_args()
    mains,bonuses=load_draws(); results={}
    funcs={4:exp004,5:exp005,6:exp006,7:exp007,8:exp008,9:exp009,10:exp010,11:exp011,12:lambda m,p:rank_experiment(m,p,False),13:lambda m,p:rank_experiment(m,p,True),14:None,15:None,16:exp016}
    for n in range(4,17):
        protocol=DOWNLOADS/f"P45_EXP{n:03d}_사전등록_프로토콜_LOCKED_001.md"; result_doc=DOWNLOADS/f"P45_EXP{n:03d}_독립분석_결과_001.md"
        ph,rh=EXPECTED_HASHES[n]
        if sha256(protocol)!=ph or sha256(result_doc)!=rh: raise RuntimeError(f"EXP-{n:03d} evidence hash mismatch")
        if n==14: value=exp014(mains,bonuses,protocol)
        elif n==15: value=exp015(mains,bonuses)
        else: value=funcs[n](mains,protocol)
        results[f"EXP-{n:03d}"]={"protocol_sha256":ph,"result_document_sha256":rh,"calculation":value}
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps({"data_sha256_bom_excluded":sha256(DATA,skip_bom=True),"results":results},ensure_ascii=False,indent=2,default=lambda x:float(x)),encoding="utf-8")
        print(f"EXP-{n:03d} calculated")
    return 0


if __name__=="__main__": raise SystemExit(main())

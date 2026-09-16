from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROTOCOL = OUT / "P45_SIGNAL_KTS_COLLISION_V1_PROTOCOL_LOCKED_001.md"
PROTOCOL_SHA = "8d3a7d1a3ae80083aad2ce132c228dd4901b1a406c2983c2b3bb30801d9d5a98"
KTS = ROOT / "v27_storage/experiments/trio_orbit_v1_001/P45_TRIO_ORBIT_V1_KTS45_SCHEDULE_001.csv"
KTS_SHA = "5f212342c6c27fca8eafbc75d20a55fc4be4ca2961a9c70c3a7af0eca26f1075"
DATA = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
DATA_SHA = "1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pair_map():
    if sha256(PROTOCOL) != PROTOCOL_SHA:
        raise RuntimeError("PROTOCOL_BLOCKED_PROTOCOL_HASH_MISMATCH")
    if sha256(KTS) != KTS_SHA:
        raise RuntimeError("PROTOCOL_BLOCKED_KTS_HASH_MISMATCH")
    trios = []
    with KTS.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            trios.append(tuple(sorted((int(r["n1"]), int(r["n2"]), int(r["n3"])))))
    pair_map = {}
    pair_occ = Counter()
    for t in trios:
        for a,b in itertools.combinations(t,2):
            pair_occ[(a,b)] += 1
            pair_map[(a,b)] = next(n for n in t if n not in (a,b))
    checks = {
        "trios_330": len(trios) == 330,
        "unique_trios_330": len(set(trios)) == 330,
        "pair_map_990": len(pair_map) == 990,
        "each_pair_once": set(pair_occ.values()) == {1},
    }
    if not all(checks.values()):
        raise RuntimeError(f"PROTOCOL_BLOCKED_KTS_PAIR_MAP: {checks}")
    return pair_map, checks


def signal(source, pair_map):
    votes = Counter(pair_map[tuple(sorted((a,b)))] for a,b in itertools.combinations(source,2))
    candidates = tuple(sorted((n for n,v in votes.items() if v >= 2), key=lambda n:(-votes[n],n)))
    completions = tuple((a,b,pair_map[tuple(sorted((a,b)))]) for a,b in itertools.combinations(source,2))
    return votes, candidates, completions


def structure_audit(pair_map, kts_checks):
    dist = Counter()
    vote_max = 0
    over6 = over3 = 0
    total = math.comb(45,6)
    for source in itertools.combinations(range(1,46),6):
        votes = {}
        for a,b in itertools.combinations(source,2):
            x = pair_map[(a,b)]
            votes[x] = votes.get(x,0)+1
        vm = max(votes.values())
        k = sum(v >= 2 for v in votes.values())
        dist[k] += 1
        if vm > vote_max: vote_max = vm
        over6 += k > 6
        over3 += vm > 3
    checks = {
        **kts_checks,
        "enumerated_C45_6": sum(dist.values()) == total == 8_145_060,
        "candidate_count_min_0": min(dist) == 0,
        "candidate_count_max_6": max(dist) == 6,
        "candidate_count_over_6_zero": over6 == 0,
        "vote_max_3": vote_max == 3,
        "vote_over_3_zero": over3 == 0,
        "all_bins_0_to_6_present": set(dist) == set(range(7)),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    audit = {
        "status": status, "total_source_sets": total,
        "candidate_count_min": min(dist), "candidate_count_max": max(dist),
        "vote_max": vote_max, "candidate_over_6": over6, "vote_over_3": over3,
        "distribution": {str(k): {"count": dist[k], "rate": dist[k]/total} for k in range(7)},
        "checks": checks,
    }
    (OUT/"P45_SIGNAL_KTS_COLLISION_V1_STRUCTURE_AUDIT_001.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    lines = [
        "# P45 SIGNAL KTS COLLISION V1 STRUCTURE AUDIT 001", "", f"- STATUS: `{status}`",
        f"- Enumerated source MAIN6: `{total}`", f"- Candidate count min/max: `{min(dist)}/{max(dist)}`",
        f"- Vote max: `{vote_max}`", f"- candidate_count >6 / vote >3: `{over6}/{over3}`", "", "|candidate_count|count|rate|", "|---:|---:|---:|",
    ]
    lines += [f"|{k}|{dist[k]}|{dist[k]/total:.12%}|" for k in range(7)]
    lines += ["", "## Checks", ""] + [f"- {k}: `{'PASS' if v else 'FAIL'}`" for k,v in checks.items()]
    (OUT/"P45_SIGNAL_KTS_COLLISION_V1_STRUCTURE_AUDIT_001.md").write_text("\n".join(lines)+"\n",encoding="utf-8",newline="\n")
    if status != "PASS":
        raise RuntimeError("PROTOCOL_BLOCKED_STRUCTURAL_MISMATCH")
    return audit


def load_draws():
    if sha256(DATA) != DATA_SHA:
        raise RuntimeError("PROTOCOL_BLOCKED_CANONICAL_HASH_MISMATCH")
    rows=[]
    with DATA.open(encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            rows.append({"round":int(r["round"]),"date":r["date"],"main":tuple(int(r[f"n{i}"]) for i in range(1,7)),"bonus":int(r["bonus"])})
    rounds=[r["round"] for r in rows]
    checks={
        "continuous":rounds==list(range(rounds[0],rounds[-1]+1)),
        "duplicate_rounds_0":len(rounds)==len(set(rounds)),
        "main_range_unique":all(len(set(r["main"]))==6 and all(1<=n<=45 for n in r["main"]) for r in rows),
        "bonus_valid":all(1<=r["bonus"]<=45 and r["bonus"] not in r["main"] for r in rows),
    }
    if not all(checks.values()): raise RuntimeError(f"PROTOCOL_BLOCKED_CANONICAL_DATA: {checks}")
    return rows,checks


def hypergeom_pmf(N,K,n):
    pmf=np.zeros(n+1,dtype=np.float64)
    den=math.comb(N,n)
    for x in range(max(0,n-(N-K)),min(n,K)+1):
        pmf[x]=math.comb(K,x)*math.comb(N-K,n-x)/den
    return pmf


def round_null_pmf(k,r,c):
    return np.convolve(hypergeom_pmf(6,c,r),hypergeom_pmf(39,6-c,k-r))


def evaluate(rows,pair_map):
    trace=[]
    output_dist=Counter()
    exposures=hits=nonzero=0
    null_expect=0.0
    null_pmf=np.array([1.0])
    A3=A2=B3=B2=AB_any3=0
    leftover_exp=leftover_hits=0
    leakage=0
    for target in range(rows[0]["round"]+1,rows[-1]["round"]+1):
        src=rows[target-2]; cur=rows[target-1]
        if src["round"] != target-1 or cur["round"] != target: leakage += 1
        votes,cands,comps=signal(src["main"],pair_map)
        if len(cands)>6: raise RuntimeError("PROTOCOL_BLOCKED_STRUCTURAL_MISMATCH")
        k=len(cands); r=sum(n in src["main"] for n in cands); c=len(set(src["main"])&set(cur["main"]))
        h=sum(n in cur["main"] for n in cands)
        pmf=round_null_pmf(k,r,c)
        null_pmf=np.convolve(null_pmf,pmf)
        null_expect += r*c/6 + (k-r)*(6-c)/39
        output_dist[k]+=1; exposures+=k; hits+=h; nonzero+=k>0
        A=cands[:3] if k>=3 else (); B=cands[3:6] if k==6 else (); leftovers=cands[3:] if k in (4,5) else ()
        ah=sum(n in cur["main"] for n in A); bh=sum(n in cur["main"] for n in B)
        A3+=ah==3; A2+=ah==2; B3+=bh==3; B2+=bh==2; AB_any3+=(ah==3 or bh==3)
        leftover_exp+=len(leftovers); leftover_hits+=sum(n in cur["main"] for n in leftovers)
        trace.append({
            "target_round":target,"source_round":target-1,"source_main6":" ".join(map(str,src["main"])),
            "pair_completions":";".join(f"{a}-{b}>{x}" for a,b,x in comps),
            "vote_counts":" ".join(f"{n}:{votes[n]}" for n in sorted(votes,key=lambda n:(-votes[n],n))),
            "candidate_count":k,"candidates_ordered":" ".join(map(str,cands)),"source_member_candidate_count_r":r,
            "source_target_intersection_c":c,"research_A":" ".join(map(str,A)),"research_B":" ".join(map(str,B)),"leftovers":" ".join(map(str,leftovers)),
            "candidate_hit_count":h,"A_exact_hit_count":ah if A else "","B_exact_hit_count":bh if B else "",
            "future_leakage_flag":0,
        })
    p_exact=float(null_pmf[hits:].sum())
    return {
        "trace":trace,"output_dist":output_dist,"evaluated":len(trace),"exposures":exposures,"hits":hits,"nonzero":nonzero,
        "null_expect":null_expect,"null_pmf":null_pmf,"p_exact":p_exact,
        "A3":A3,"A2":A2,"B3":B3,"B2":B2,"AB_any3":AB_any3,
        "leftover_exp":leftover_exp,"leftover_hits":leftover_hits,"leakage":leakage,
    }


def write_trace(rows):
    path=OUT/"P45_SIGNAL_KTS_COLLISION_V1_ROUND_TRACE_001.csv"
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n"); w.writeheader(); w.writerows(rows)


def main():
    pair_map,kts_checks=load_pair_map()
    audit=structure_audit(pair_map,kts_checks)
    rows,data_checks=load_draws()
    ev=evaluate(rows,pair_map)
    write_trace(ev["trace"])
    n=ev["evaluated"]
    if n<1000: judgment="INCONCLUSIVE_LOW_SAMPLE"
    elif ev["exposures"]<500: judgment="INCONCLUSIVE_LOW_OUTPUT"
    elif ev["leakage"]!=0: judgment="PROTOCOL_BLOCKED"
    elif ev["hits"]>ev["null_expect"] and ev["p_exact"]<=0.05: judgment="SUPPORTED_SIGNAL_LEVEL_BACKTEST"
    else: judgment="FAILED_NOT_SUPPORTED"
    result={
        "protocol_sha256":sha256(PROTOCOL),"kts_source":str(KTS),"kts_sha256":sha256(KTS),"canonical_source":str(DATA),"canonical_sha256":sha256(DATA),
        "data_range":[rows[0]["round"],rows[-1]["round"]],"evaluated_rounds":n,"data_checks":data_checks,
        "structure_audit":audit,"historical_output_count_distribution":{str(k):ev["output_dist"][k] for k in range(7)},
        "nonzero_rounds":ev["nonzero"],"nonzero_rate":ev["nonzero"]/n,"average_candidate_count":ev["exposures"]/n,
        "candidate_exposures":ev["exposures"],"observed_hits":ev["hits"],"observed_rate":ev["hits"]/ev["exposures"],
        "matched_null_expected_hits":ev["null_expect"],"matched_null_expected_rate":ev["null_expect"]/ev["exposures"],"exact_one_sided_p":ev["p_exact"],
        "research_A":{"exact3_rounds":ev["A3"],"exact2_rounds":ev["A2"]},"research_B":{"exact3_rounds":ev["B3"],"exact2_rounds":ev["B2"]},
        "A_or_B_any_exact3_rounds":ev["AB_any3"],"leftovers":{"exposures":ev["leftover_exp"],"hits":ev["leftover_hits"]},
        "future_leakage":ev["leakage"],"HISTORICAL_ONE_STEP_WALKFORWARD":"YES","final_judgment":judgment,
    }
    (OUT/"P45_SIGNAL_KTS_COLLISION_V1_RESULT_001.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    structural_rows="\n".join(f"|{k}|{audit['distribution'][str(k)]['count']}|{audit['distribution'][str(k)]['rate']:.12%}|" for k in range(7))
    hist_rows="\n".join(f"|{k}|{ev['output_dist'][k]}|{ev['output_dist'][k]/n:.12%}|" for k in range(7))
    report=f'''# P45 SIGNAL KTS COLLISION V1 BACKTEST RESULT 001

## FINAL_JUDGMENT

`{judgment}`

## Locked inputs and preflight

- Protocol SHA-256: `{sha256(PROTOCOL)}`
- KTS source / SHA: `{KTS}` / `{sha256(KTS)}` (`PASS`)
- Canonical source / SHA: `{DATA}` / `{sha256(DATA)}`
- Data range / evaluated targets: `{rows[0]["round"]}..{rows[-1]["round"]} / {rows[0]["round"]+1}..{rows[-1]["round"]} = {n}`
- Data checks: `{json.dumps(data_checks,ensure_ascii=False)}`
- HISTORICAL_ONE_STEP_WALKFORWARD: `YES`
- FUTURE_LEAKAGE: `{ev["leakage"]}`

## Exhaustive structural audit

- Status: `{audit["status"]}`
- Enumerated: `{audit["total_source_sets"]}`
- Candidate count min/max / vote max: `{audit["candidate_count_min"]}/{audit["candidate_count_max"]}/{audit["vote_max"]}`
- count>6 / vote>3: `{audit["candidate_over_6"]}/{audit["vote_over_3"]}`

|candidate_count|all-source-set count|rate|
|---:|---:|---:|
{structural_rows}

## Historical output availability

|candidate_count|rounds|rate|
|---:|---:|---:|
{hist_rows}

- Nonzero output: `{ev["nonzero"]}/{n} = {ev["nonzero"]/n:.12%}`
- Average candidate count: `{ev["exposures"]/n:.12f}`
- Total candidate exposures: `{ev["exposures"]}`

## SIGNAL_VALIDITY_PRIMARY

- Observed hits / rate: `{ev["hits"]}/{ev["exposures"]} = {ev["hits"]/ev["exposures"]:.12%}`
- Simple 6/45 reference: `13.333333333333%`
- Carryover-matched exact-null expected hits / rate: `{ev["null_expect"]:.12f} / {ev["null_expect"]/ev["exposures"]:.12%}`
- Exact one-sided p `P(H_null >= H_observed)`: `{ev["p_exact"]:.15g}`
- This is the single confirmatory test.

## P45 TRIO support (descriptive only)

- Research A exact3 / exact2 rounds: `{ev["A3"]} / {ev["A2"]}`
- Research B exact3 / exact2 rounds: `{ev["B3"]} / {ev["B2"]}`
- A or B at least one exact3: `{ev["AB_any3"]}`
- Leftover individual exposures / hits: `{ev["leftover_exp"]} / {ev["leftover_hits"]}`
- These metrics do not alter SIGNAL_VALIDITY_PRIMARY.

## Protection boundary

- OFFICIAL ENGINE / EXP-017 / DRAW_DISCOVERY_PAUSE: `FROZEN / NOT_CREATED / ACTIVE`
- Official code/DB/gate/threshold/signature/semantics/State/Decision/Registry changes: `0`
- V1 threshold and rules were not changed after observing results.
'''
    (OUT/"P45_SIGNAL_KTS_COLLISION_V1_BACKTEST_RESULT_001.md").write_text(report,encoding="utf-8",newline="\n")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name != "SHA256SUMS_001.txt": manifest.append(f"{sha256(p)}  {p.name}")
    (OUT/"SHA256SUMS_001.txt").write_text("\n".join(manifest)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()

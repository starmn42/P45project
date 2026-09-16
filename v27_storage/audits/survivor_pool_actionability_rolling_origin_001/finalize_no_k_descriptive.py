from __future__ import annotations

import csv, hashlib, json
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from p45_v27.stage55_diagnostics import load_draw_csv
from p45_v27.stage6_diagnostics import diagnose_stage6

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"v27_storage/audits/survivor_pool_actionability_rolling_origin_001"
STAGING=ROOT/"v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
EVIDENCE=OUT/"P45_SURVIVOR_POOL_ACTIONABILITY_PER_TARGET_EVIDENCE_001.csv"
EXACT=OUT/"P45_SURVIVOR_POOL_ACTIONABILITY_EXACT_N_PROFILE_001.csv"
BINS=OUT/"P45_SURVIVOR_POOL_ACTIONABILITY_COARSE_BIN_PROFILE_001.csv"
RESULT=OUT/"P45_SURVIVOR_POOL_ACTIONABILITY_RESULT_001.json"
P0=6/45

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def feature(t):
    s=diagnose_stage6(STAGING,t)
    if tuple(s["source_rounds"])!=(1,t-1): raise RuntimeError("SOURCE_BOUNDARY")
    ids=[n for n,r in s["rows"].items() if r["number_state"] in ("NUMBER_PASS","NUMBER_WEAKEN") or r["valid_test_status"]]
    return t,ids
def bin_name(n):
    if n==0:return "0"
    if n<=2:return "1-2"
    if n<=5:return "3-5"
    if n<=9:return "6-9"
    if n<=14:return "10-14"
    if n<=19:return "15-19"
    if n<=29:return "20-29"
    if n<=39:return "30-39"
    return "40-45"
def summ(rows):
    rounds=len(rows);obs=sum(r["n"] for r in rows);hits=sum(r["hits"] for r in rows);rate=hits/obs if obs else None
    return rounds,obs,hits,rate,(rate-P0 if rate is not None else None),(hits/rounds if rounds else None),(obs/rounds if rounds else None)
def main():
    result=json.loads(RESULT.read_text(encoding="utf-8"))
    if result["k_discovery"] is not None: raise RuntimeError("EXPECTED_NO_DISCOVERY_K")
    outcomes={d.round:tuple(d.main) for d in load_draw_csv(STAGING)}
    with EVIDENCE.open("r",encoding="utf-8-sig",newline="") as h:
        prior=list(csv.DictReader(h))
    rows=[]
    for r in prior:
        rows.append({"segment":r["segment"],"target":int(r["target"]),"source_max":int(r["source_max"]),"ids":[int(x) for x in r["raw_survivor_identities"].split()] if r["raw_survivor_identities"] else [],"n":int(r["raw_survivor_count"]),"main":[int(x) for x in r["main6"].split()],"hits":int(r["survivor_main_hits"]),"state":r["official_output_state"]})
    with ProcessPoolExecutor(max_workers=8) as ex: frozen=list(ex.map(feature,range(868,1239),chunksize=1))
    for t,ids in frozen:
        main=outcomes[t];n=len(ids);hits=len(set(ids)&set(main));rows.append({"segment":"CONFIRMATION_DESCRIPTIVE_ONLY","target":t,"source_max":t-1,"ids":ids,"n":n,"main":list(main),"hits":hits,"state":"NUMBER_POOL_AVAILABLE" if n>=6 else "NO_NUMBER_POOL"})
    rows.sort(key=lambda r:r["target"])
    with EVIDENCE.open("w",encoding="utf-8-sig",newline="") as h:
        w=csv.writer(h,lineterminator="\n");w.writerow(["segment","target","source_max","raw_survivor_identities","raw_survivor_count","main6","survivor_main_hits","candidate_observations","survivor_hit_rate","official_output_state","future_data_check"])
        for r in rows:w.writerow([r["segment"],r["target"],r["source_max"]," ".join(map(str,r["ids"])),r["n"]," ".join(map(str,r["main"])),r["hits"],r["n"],r["hits"]/r["n"] if r["n"] else None,r["state"],0])
    groups=defaultdict(list)
    for r in rows:groups[r["n"]].append(r)
    with EXACT.open("w",encoding="utf-8-sig",newline="") as h:
        w=csv.writer(h,lineterminator="\n");w.writerow(["exact_n","rounds","candidate_observations","main_hits","candidate_hit_rate","delta_random","average_main_hits_per_round"])
        for n in range(46):
            rounds,obs,hits,rate,delta,avgh,_=summ(groups[n]);w.writerow([n,rounds,obs,hits,rate,delta,avgh])
    bg=defaultdict(list)
    for r in rows:bg[bin_name(r["n"])].append(r)
    with BINS.open("w",encoding="utf-8-sig",newline="") as h:
        w=csv.writer(h,lineterminator="\n");w.writerow(["bin","rounds","average_pool_size","candidate_observations","main_hits","candidate_hit_rate","average_main_hits_captured","random_expected_hits","lift"])
        for name in ["0","1-2","3-5","6-9","10-14","15-19","20-29","30-39","40-45"]:
            rounds,obs,hits,rate,_,avgh,avgn=summ(bg[name]);expected=avgn*P0 if avgn is not None else None;w.writerow([name,rounds,avgn,obs,hits,rate,avgh,expected,avgh/expected if expected else None])
    result["confirmation_predictive_test_performed"]=False
    result["confirmation_outcome_accessed_for_descriptive_only"]=True
    result["full_historical_evidence_target_count"]=len(rows)
    result["artifacts"]["per_target_sha256"]=sha(EVIDENCE);result["artifacts"]["exact_n_sha256"]=sha(EXACT);result["artifacts"]["coarse_bin_sha256"]=sha(BINS)
    RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"targets":len(rows),"k_discovery":result["k_discovery"],"primary":result["primary_verdict"],"hashes":result["artifacts"]},ensure_ascii=False))
if __name__=="__main__":main()

"""EXP-002 sealed, outcome-separated historical evaluation.

Official P45 modules and databases are read only. All writes are confined to the
EXP-002 research directory and database.
"""
from __future__ import annotations

import argparse, csv, hashlib, json, math, os, random, shutil, sqlite3, uuid
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping

from p45_v27.integrity import canonical_json, sha256_file, sha256_json
from p45_v27.stage6_diagnostics import diagnose_stage6
from p45_v27.trio_engine import build_current_trios, wilson95
from p45_v27.trio_final import _rank_key
from p45_v27.units import DEFINITIONS
from .fallback import POOL_TYPE, PROTOCOL_ID, select_disjoint_trios, source_pool
from .storage import upgrade

EXPERIMENT_ID="EXP-DRAW-20260816-038-V1"
PROTOCOL_VERSION="EXP002-PROTOCOL-1.0"
CALCULATOR_VERSION="EXP002-CALCULATOR-1.0"
NULL_VERSION="EXP002-NULL-1.0"
SEED=202608160038
IID_REPETITIONS=100_000
PERMUTATION_REPETITIONS=100_000
START_ROUND=369
END_ROUND=1235

def now()->str:return datetime.now().astimezone().isoformat(timespec="seconds")

def exact_baseline(scope:str)->float:
    m=6 if scope=="MAIN" else 7
    # Inclusion/exclusion for at least one of two fixed, disjoint trios.
    return (2*math.comb(42,m-3)-math.comb(39,m-6))/math.comb(45,m)

def binomial_upper(n:int,x:int,p:float)->float:
    return min(1.0,sum(math.comb(n,k)*p**k*(1-p)**(n-k) for k in range(x,n+1)))

def _worker(task:tuple[str,int])->tuple[int,dict[str,Any]]:
    path,r=task
    stage=diagnose_stage6(Path(path),r)
    ordered=source_pool(stage["rows"])
    compact={"analysis_round":r,"source_end_round":stage["source_rounds"][1],
      "execution_hash":stage["execution_hash"],"ordered_numbers":[x["number"] for x in ordered],
      "stage":stage}
    return r,compact

def protocol_files(root:Path)->list[Path]:
    base=root/"00_P45_STATE/experiment_lab/EXP-002_NO_PICK_FALLBACK"
    return [base/f"EXP002_0{i}_{name}.md" for i,name in (
      (1,"PREREGISTRATION"),(2,"ELIGIBILITY_AND_SELECTION"),(3,"METRIC_NULL_POLICY"),
      (4,"WALKFORWARD_DESIGN"),(5,"SUCCESS_FAILURE_CRITERIA"))]

def protocol_lock(root:Path,data_source:Path)->dict[str,Any]:
    files=protocol_files(root)
    if not all(p.exists() for p in files):raise RuntimeError("PROTOCOL_FILE_MISSING")
    entries=[{"path":str(p.relative_to(root)).replace('\\','/'),"sha256":sha256_file(p)} for p in files]
    canonical_hash=sha256_json(entries)
    snapshot=root/"v27_storage/experiments/exp002/data/exp002_draws_1_1235.csv"
    snapshot.parent.mkdir(parents=True,exist_ok=True)
    if not snapshot.exists():shutil.copyfile(data_source,snapshot)
    if sha256_file(snapshot)!=sha256_file(data_source):raise RuntimeError("DATA_SNAPSHOT_MISMATCH")
    rows=list(csv.DictReader(snapshot.open(encoding="utf-8-sig",newline="")))
    if len(rows)!=1235 or int(rows[-1]["round"])!=1235:raise RuntimeError("DATA_BOUNDARY_INVALID")
    meta={"experiment_id":EXPERIMENT_ID,"protocol_version":PROTOCOL_VERSION,"protocol_files":entries,
      "canonical_protocol_hash":canonical_hash,"draft_protocol_hash_declared":"832e7df52854a61ae5b769ebdf529e48b6df0ca622606a583b5fa9c9055b7c46",
      "data_snapshot":str(snapshot.relative_to(root)).replace('\\','/'),"data_snapshot_hash":sha256_file(snapshot),
      "data_boundary":"1~1235","pool_type":POOL_TYPE,"number_order":"OFFICIAL_NUMBER_14_KEY",
      "trio_order":"OFFICIAL_TRIO_15_KEY","trio_exposure_policy":"EXP002_ONLY_R_MINUS_1",
      "selection":"FIRST_TRIO_PLUS_FIRST_LATER_DISJOINT_TRIO","seed":SEED,
      "iid_repetitions":IID_REPETITIONS,"permutation_repetitions":PERMUTATION_REPETITIONS,
      "outcome_separation":"EACH_ROUND_PREDICTION_COMMITTED_BEFORE_ITS_OUTCOME;R_OUTCOME_USED_FROM_R_PLUS_1","locked_at":now()}
    meta["lock_hash"]=sha256_json({k:v for k,v in meta.items() if k!="locked_at"})
    lock_path=root/"00_P45_STATE/experiment_lab/EXP-002_NO_PICK_FALLBACK/EXP002_PROTOCOL_LOCK.json"
    if lock_path.exists():
        old=json.loads(lock_path.read_text(encoding="utf-8"))
        if old["lock_hash"]!=meta["lock_hash"]:raise RuntimeError("PROTOCOL_ALREADY_LOCKED_DIFFERENT")
        return old
    lock_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return meta

def _prediction_payload(r:int,item:Mapping[str,Any],history:dict[str,list[dict]])->tuple[dict[str,Any],dict[tuple[int,...],tuple[str,int]]]:
    stage=dict(item["stage"]); nums=item["ordered_numbers"]
    if item["source_end_round"]!=r-1:raise RuntimeError("FUTURE_LEAKAGE")
    base={"evaluation_round":r,"source_end_round":r-1,"pool_type":POOL_TYPE,
      "ordered_numbers":nums,"protocol":PROTOCOL_ID}
    if len(nums)<6:
        return ({**base,"eligible":False,"reason":"SOURCE_POOL_UNDER_6","ordered_trios":[],"selection":None},{})
    stage["candidate_numbers"]=nums;stage["candidate_pool_type"]=POOL_TYPE
    trios=build_current_trios(stage,DEFINITIONS,history)
    ranked=sorted(trios["rows"].values(),key=_rank_key)
    selection=select_disjoint_trios(ranked)
    order=["-".join(map(str,x["trio"])) for x in ranked]
    payload={**base,"eligible":selection is not None,"reason":"FALLBACK_PICK" if selection else "NO_DISJOINT_TRIO",
      "ordered_trios":order,"selection":selection,"stage_execution_hash":stage["execution_hash"]}
    signatures={tuple(x["trio"]):(x["trio_rule_signature"],int("UNIT_TRIO_CONFLICT" in x["coverage"]["trio_unit_state_vector"])) for x in ranked}
    return payload,signatures

def _load_one_outcome(snapshot:Path,r:int)->dict[str,Any]:
    # This function is called only after the prediction row was committed.
    for d in csv.DictReader(snapshot.open(encoding="utf-8-sig",newline="")):
        if int(d["round"])==r:
            return {"main":{int(d[f"n{i}"]) for i in range(1,7)},"bonus":int(d["bonus"])}
    raise RuntimeError(f"OUTCOME_MISSING:{r}")

def _outcome_row(p:Mapping[str,Any],actual:Mapping[str,Any])->dict[str,Any]:
    main=set(actual["main"]);bonus=int(actual["bonus"]);integ=main|{bonus}
    a=set(p["selection"]["trio_a"]);b=set(p["selection"]["trio_b"])
    row={"evaluation_round":p["evaluation_round"],"prediction_hash":p["prediction_hash"],
      "main_a":len(a&main),"main_b":len(b&main),"integrated_a":len(a&integ),"integrated_b":len(b&integ),
      "six_hits":len((a|b)&main),"bonus":bonus}
    row["outcome_hash"]=sha256_json(row);return row

def build_predictions(root:Path,snapshot:Path,audit_csv:Path,db_path:Path,run_id:str)->tuple[list[dict],list[dict]]:
    audit={int(x["evaluation_round"]):x for x in csv.DictReader(audit_csv.open(encoding="utf-8-sig",newline=""))}
    rounds=[r for r in range(START_ROUND,END_ROUND+1) if audit[r]["availability_class"]=="RESEARCH_NO_PICK"]
    predictions=[];outcomes=[];history:dict[str,list[dict]]={}
    db=sqlite3.connect(db_path)
    existing_locks={r:h for r,h in db.execute("SELECT evaluation_round,prediction_hash FROM prediction_lock WHERE run_id=?",(run_id,))}
    existing_outcomes={r:h for r,h in db.execute("SELECT evaluation_round,outcome_hash FROM experiment_outcome WHERE run_id=?",(run_id,))}
    workers=min(8,max(1,os.cpu_count() or 1))
    with ProcessPoolExecutor(max_workers=workers) as pool:
      stream=pool.map(_worker,[(str(snapshot),r) for r in rounds],chunksize=1)
      for r,item in stream:
        p,signatures=_prediction_payload(r,item,history);p["prediction_hash"]=sha256_json(p);predictions.append(p)
        if r in existing_locks:
            if existing_locks[r]!=p["prediction_hash"]:raise RuntimeError(f"RESUME_PREDICTION_HASH_MISMATCH:{r}")
        else:
            sel=p["selection"] or {};eh=canonical_json({"eligible":p["eligible"],"reason":p["reason"]})
            with db:
                db.execute("INSERT INTO prediction_lock(run_id,evaluation_round,source_end_round,eligibility_json,trio_a_json,trio_b_json,prediction_hash,locked_before_outcome,lock_sequence,staged_at,lock_hash) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                  (run_id,r,r-1,eh,canonical_json(sel.get("trio_a")) if sel else None,canonical_json(sel.get("trio_b")) if sel else None,p["prediction_hash"],1,len(predictions),now(),p["prediction_hash"]))
                db.execute("INSERT INTO prediction_detail VALUES(?,?,?,?,?,?)",(run_id,r,canonical_json(p["ordered_numbers"]),canonical_json(p["ordered_trios"]),canonical_json(sel) if sel else None,p["reason"]))
        if not p["eligible"]:continue
        actual=_load_one_outcome(snapshot,r);x=_outcome_row(p,actual);outcomes.append(x)
        if r in existing_outcomes:
            if existing_outcomes[r]!=x["outcome_hash"]:raise RuntimeError(f"RESUME_OUTCOME_HASH_MISMATCH:{r}")
        else:
            with db:
                db.execute("INSERT INTO experiment_outcome VALUES(?,?,?,?,?,?,?,?,?,?,?)",(run_id,r,int(x["integrated_a"]==3),int(x["integrated_b"]==3),int(x["main_a"]==3),int(x["main_b"]==3),int(x["integrated_a"]==2),int(x["integrated_b"]==2),int(x["main_a"]==2),int(x["main_b"]==2),x["outcome_hash"]))
        for key in ("trio_a","trio_b"):
            trio=tuple(p["selection"][key]);signature,unit_conflict=signatures[tuple(sorted(trio))]
            history.setdefault(signature,[]).append({"outer_round":r,"trio":trio,
              "integrated_hits":len(set(trio)&(actual["main"]|{actual["bonus"]})),"main_hits":len(set(trio)&actual["main"]),
              "bonus_hit":int(actual["bonus"] in trio),"unit_conflict":unit_conflict})
    db.close();return predictions,outcomes

def _permutation(predictions:list[dict],snapshot:Path,reps:int=PERMUTATION_REPETITIONS)->dict[str,Any]:
    eligible=[p for p in predictions if p["eligible"]]
    draws={int(x["round"]):x for x in csv.DictReader(snapshot.open(encoding="utf-8-sig",newline=""))}
    pred=[(set(p["selection"]["trio_a"]),set(p["selection"]["trio_b"])) for p in eligible]
    results=[]
    for p in eligible:
        d=draws[p["evaluation_round"]];m={int(d[f"n{i}"]) for i in range(1,7)};results.append((m,m|{int(d["bonus"])}))
    observed_main=sum(len(a&m)==3 or len(b&m)==3 for (a,b),(m,_) in zip(pred,results))
    observed_int=sum(len(a&i)==3 or len(b&i)==3 for (a,b),(_,i) in zip(pred,results))
    rng=random.Random(SEED);ge_m=ge_i=0;idx=list(range(len(results)))
    for _ in range(reps):
        rng.shuffle(idx);cm=ci=0
        for j,k in enumerate(idx):
            a,b=pred[j];m,i=results[k];cm+=len(a&m)==3 or len(b&m)==3;ci+=len(a&i)==3 or len(b&i)==3
        ge_m+=cm>=observed_main;ge_i+=ci>=observed_int
    return {"version":NULL_VERSION,"seed":SEED,"repetitions":reps,"observed_main":observed_main,
      "observed_integrated":observed_int,"main_p_upper":(ge_m+1)/(reps+1),"integrated_p_upper":(ge_i+1)/(reps+1)}

def summarize(predictions:list[dict],outcomes:list[dict],perm:dict)->dict[str,Any]:
    n=len(outcomes);main=sum(x["main_a"]==3 or x["main_b"]==3 for x in outcomes);integ=sum(x["integrated_a"]==3 or x["integrated_b"]==3 for x in outcomes)
    m2a=sum(x["main_a"]==2 for x in outcomes);m2b=sum(x["main_b"]==2 for x in outcomes)
    i2a=sum(x["integrated_a"]==2 for x in outcomes);i2b=sum(x["integrated_b"]==2 for x in outcomes)
    pm=exact_baseline("MAIN");pi=exact_baseline("INTEGRATED");half=n//2
    periods={"FIRST_HALF":outcomes[:half],"SECOND_HALF":outcomes[half:],"RECENT_100":outcomes[-100:],"RECENT_50":outcomes[-50:],"RECENT_20_TEST_ONLY":outcomes[-20:]}
    period_metrics={k:{"n":len(v),"main_primary":sum(x["main_a"]==3 or x["main_b"]==3 for x in v),
      "integrated_primary":sum(x["integrated_a"]==3 or x["integrated_b"]==3 for x in v)} for k,v in periods.items()}
    ml,mh=wilson95(main,n);il,ih=wilson95(integ,n)
    enough=n>=200 and len(periods["FIRST_HALF"])>=75 and len(periods["SECOND_HALF"])>=75
    primary_superior=n>0 and main/n>pm and binomial_upper(n,main,pm)<.05 and ml>pm and perm["main_p_upper"]<.05
    directions=all((v["main_primary"]/v["n"] if v["n"] else 0)>=pm for k,v in period_metrics.items() if k in ("FIRST_HALF","SECOND_HALF","RECENT_100"))
    supported=enough and primary_superior and directions
    if not enough:judgment,code="INCONCLUSIVE","D"
    elif supported:judgment,code="INCONCLUSIVE","A_PENDING_INDEPENDENT_REPRODUCTION"
    elif n>0:judgment,code="FAILED","B"
    else:judgment,code="FAILED","D"
    return {"valid_no_pick_rounds":len(predictions),"fallback_pick_rounds":n,"experimental_no_pick_rounds":len(predictions)-n,
      "coverage_rate":n/len(predictions) if predictions else 0,"main_primary":main,"main_rate":main/n if n else 0,
      "integrated_primary":integ,"integrated_rate":integ/n if n else 0,"main_exact2_support":{"A":m2a,"B":m2b},
      "integrated_exact2_support":{"A":i2a,"B":i2b},"random_main_baseline":pm,"random_integrated_baseline":pi,
      "main_wilson95":[ml,mh],"integrated_wilson95":[il,ih],"main_exact_p_upper":binomial_upper(n,main,pm),
      "integrated_exact_p_upper":binomial_upper(n,integ,pi),"permutation":perm,"period_metrics":period_metrics,
      "minimum_sample_met":enough,"primary_superior":primary_superior,"direction_stability":directions,
      "independent_reproduction_complete":False,"final_judgment":judgment,"explanation_code":code,
      "promotion_candidate":False,"official_pick_allowed":False,"future_leakage":0,"failed_rounds":0}

def start_run(db_path:Path,lock:dict)->str:
    upgrade(db_path);run_id=str(uuid.uuid4());db=sqlite3.connect(db_path)
    try:
        existing=db.execute("SELECT run_id,protocol_hash,data_snapshot_hash FROM experiment_run WHERE status='RUNNING' ORDER BY started_at DESC LIMIT 1").fetchone()
        if existing:
            if existing[1]!=lock["lock_hash"] or existing[2]!=lock["data_snapshot_hash"]:raise RuntimeError("RESUME_RUN_HASH_MISMATCH")
            return existing[0]
        with db:
            db.execute("UPDATE protocol_registry SET protocol_version=?,protocol_hash=?,lock_status='LOCKED' WHERE experiment_id=?",(PROTOCOL_VERSION,lock["lock_hash"],EXPERIMENT_ID))
            for f in lock["protocol_files"]:db.execute("INSERT OR REPLACE INTO protocol_file VALUES(?,?,?)",(EXPERIMENT_ID,f["path"],f["sha256"]))
            db.execute("INSERT OR REPLACE INTO data_snapshot VALUES(?,?,?,?,?,?)",(lock["data_snapshot_hash"],lock["data_snapshot"],1,1235,1235,lock["locked_at"]))
            db.execute("INSERT INTO experiment_run VALUES(?,?,?,?,?,?,?,?)",(run_id,EXPERIMENT_ID,lock["lock_hash"],lock["data_snapshot_hash"],0,'RUNNING',now(),None))
    finally:db.close()
    return run_id

def finalize_store(db_path:Path,run_id:str,predictions:list[dict],summary:dict)->None:
    db=sqlite3.connect(db_path)
    try:
        with db:
            for name,val in (("EXACT_BASELINES",{"main":exact_baseline('MAIN'),"integrated":exact_baseline('INTEGRATED')}),("SELECTION_LABEL_PERMUTATION",summary["permutation"])):
                db.execute("INSERT INTO null_result VALUES(?,?,?,?)",(run_id,name,canonical_json(val),sha256_json(val)))
            sh=sha256_json(summary);db.execute("INSERT INTO run_summary VALUES(?,?,?)",(run_id,canonical_json(summary),sh))
            db.execute("INSERT INTO experiment_judgment VALUES(?,?,?,?,?,?)",(run_id,"COVERAGE_IMPROVED" if summary['coverage_rate']>0 else "NO_COVERAGE", "PRIMARY_SUPERIOR" if summary['primary_superior'] else "RANDOM_LEVEL_OR_INFERIOR",summary['final_judgment'],0,canonical_json(summary)))
            db.execute("UPDATE experiment_run SET prediction_count=?,status='COMPLETE',completed_at=? WHERE run_id=?",(len(predictions),now(),run_id))
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():raise RuntimeError("DB_INTEGRITY_FAILURE")
    finally:db.close()

def main(argv:list[str]|None=None)->int:
    ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path.cwd());ap.add_argument("--preflight-only",action="store_true");a=ap.parse_args(argv);root=a.root.resolve()
    source=root/"analysis/structure-1236/analysis-input.csv";db=root/"v27_storage/experiments/exp002/exp002_research.sqlite3";audit=root/"v27_storage/experiments/exp002/audit/no_pick_coverage_rounds.csv"
    lock=protocol_lock(root,source);upgrade(db)
    checks={"protocol_locked":bool(lock["lock_hash"]),"source_boundary":lock["data_boundary"]=="1~1235","seed_locked":lock["seed"]==SEED,
      "official_db_not_target":str(db).startswith(str(root/"v27_storage/experiments/exp002")),"audit_exists":audit.exists()}
    if not all(checks.values()):raise RuntimeError(f"PREFLIGHT_FAILED:{checks}")
    if a.preflight_only:print(json.dumps({"status":"PASS","checks":checks,"lock":lock},ensure_ascii=False));return 0
    run_id=start_run(db,lock)
    predictions,outcomes=build_predictions(root,root/lock["data_snapshot"],audit,db,run_id)
    if len(predictions)!=867 or any(not p.get("prediction_hash") for p in predictions):raise RuntimeError("PREDICTION_LOCK_INCOMPLETE")
    perm=_permutation(predictions,root/lock["data_snapshot"]);summary=summarize(predictions,outcomes,perm)
    finalize_store(db,run_id,predictions,summary);result={"run_id":run_id,"protocol_lock":lock,"summary":summary,"db_sha256":sha256_file(db)}
    out=root/"v27_storage/experiments/exp002/EXP002_LOCKED_RUN_RESULT.json";out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False));return 0

if __name__=="__main__":raise SystemExit(main())

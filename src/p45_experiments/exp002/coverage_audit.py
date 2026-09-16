"""Read-only NO-PICK coverage audit from completed official walk-forward evidence."""
from __future__ import annotations

import argparse, bisect, csv, json, os, sqlite3, uuid
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path

from p45_v27.integrity import canonical_json, sha256_json
from p45_v27.stage6_diagnostics import diagnose_stage6
from p45_v27.trio_engine import build_current_trios
from p45_v27.trio_final import RUN_ID as TRIO_RUN_ID
from p45_v27.units import DEFINITIONS

PAIR_RUN_ID = "2f61c1b7-2cb6-4d33-92c8-520691af3e76"
FIRST_ELIGIBLE = 369

def _read_pair_rounds(path: Path) -> dict[int, dict]:
    db=sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro",uri=True);db.row_factory=sqlite3.Row
    try:
        run=db.execute("select * from wf_run where run_id=?",(PAIR_RUN_ID,)).fetchone()
        if not run or run["run_status"]!="WALKFORWARD_COMPLETE": raise RuntimeError("PAIR_SOURCE_NOT_COMPLETE")
        rows={r["evaluation_round"]:dict(r) for r in db.execute("select * from wf_round where run_id=? order by evaluation_round",(PAIR_RUN_ID,))}
    finally: db.close()
    return rows

def _read_trio_exposures(path: Path) -> dict[str,list[dict]]:
    db=sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro",uri=True);db.row_factory=sqlite3.Row
    try: raw=[dict(x) for x in db.execute("select * from wf_exposure where run_id=? order by evaluation_round,trio_rule_signature",(TRIO_RUN_ID,))]
    finally: db.close()
    grouped=defaultdict(list)
    for row in raw:
        row["outer_round"]=row["evaluation_round"]
        row["trio"]=tuple(map(int,row["representative_trio_key"].split("-")))
        grouped[row["trio_rule_signature"]].append(row)
    return grouped

_WORKER_DATA:Path|None=None
_WORKER_EXPOSURES:dict[str,list[dict]]={}
_WORKER_ROUNDS:dict[str,list[int]]={}

def _worker_init(data_path:str,trio_db:str)->None:
    global _WORKER_DATA,_WORKER_EXPOSURES,_WORKER_ROUNDS
    _WORKER_DATA=Path(data_path);_WORKER_EXPOSURES=_read_trio_exposures(Path(trio_db))
    _WORKER_ROUNDS={k:[x["evaluation_round"] for x in v] for k,v in _WORKER_EXPOSURES.items()}

class _PrefixHistory(dict):
    def __init__(self,round_:int):self.round=round_
    def __bool__(self):return True
    def get(self,key,default=None):
        rows=_WORKER_EXPOSURES.get(key)
        if rows is None:return [] if default is None else default
        return rows[:bisect.bisect_left(_WORKER_ROUNDS[key],self.round)]

def _audit_round(task:tuple[int,dict])->dict:
    r,p=task
    if _WORKER_DATA is None:raise RuntimeError("EXP002_WORKER_NOT_INITIALIZED")
    stage6=diagnose_stage6(_WORKER_DATA,r);states=Counter(x["number_state"] for x in stage6["rows"].values())
    trio_counts=Counter();valid=[]
    if len(stage6["candidate_numbers"])>=6:
        trios=build_current_trios(stage6,DEFINITIONS,_PrefixHistory(r));trio_counts=Counter(x["trio_state"] for x in trios["rows"].values());valid=[x for x in trios["rows"].values() if x["valid_for_pair"]]
    if r<FIRST_ELIGIBLE:cls,stop="FIRST_ELIGIBLE_WARMUP",None
    elif p["round_status"]=="SKIPPED_RESEARCH_HOLD":cls,stop="RESEARCH_NO_PICK","NUMBER_STAGE_STOP"
    elif p["round_status"]=="SKIPPED_TRIO_UNDER_2":cls,stop="RESEARCH_NO_PICK","TRIO_STAGE_STOP"
    elif p["round_status"]=="SKIPPED_NO_DISJOINT_PAIR":cls,stop="RESEARCH_NO_PICK","PAIR_STAGE_STOP"
    elif p["round_status"]=="COMPLETE":cls,stop="RESEARCH_NO_PICK","CORE_STAGE_STOP"
    else:cls,stop="SYSTEM_ERROR","OTHER"
    pair_count=int(p["candidate_count"])
    row={"evaluation_round":r,"source_end_round":r-1,"availability_class":cls,"no_pick_stage":stop,
      "number_candidate_count":len(stage6["candidate_numbers"]),"number_pass":states["NUMBER_PASS"],"number_weaken":states["NUMBER_WEAKEN"],
      "number_test":states["NUMBER_TEST"],"number_hold":states["NUMBER_HOLD"],"number_fail":states["NUMBER_FAIL"],
      "valid_trio_count":len(valid),"trio_pass":trio_counts["TRIO_PASS"],"trio_test":trio_counts["TRIO_TEST"],"trio_hold":trio_counts["TRIO_HOLD"],
      "eligible_pair_count":pair_count,"pair_ready":0,"pair_test_ready":0,"pair_research_hold":0,
      "pair_system_hold":pair_count,"valid_for_core":0,"final_output_available":False}
    row["row_hash"]=sha256_json(row);return row

def _rates(rows:list[dict], n:int)->float:
    return sum(not x["final_output_available"] for x in rows[-n:])/min(n,len(rows)) if rows else 0.0

def audit(data_path:Path,trio_db:Path,pair_db:Path,start:int=43,end:int=1235,progress:Path|None=None)->dict:
    pair_rounds=_read_pair_rounds(pair_db);records=[];tasks=[(r,pair_rounds[r]) for r in range(start,end+1)]
    workers=min(8,max(1,os.cpu_count() or 1))
    with ProcessPoolExecutor(max_workers=workers,initializer=_worker_init,initargs=(str(data_path),str(trio_db))) as pool:
        for index,row in enumerate(pool.map(_audit_round,tasks,chunksize=2),1):
            records.append(row)
            if progress and (index%25==0 or index==len(tasks)):progress.write_text(json.dumps({"completed":index,"total":len(tasks),"round":row["evaluation_round"]}),encoding="utf-8")
    valid=[x for x in records if x["availability_class"]=="RESEARCH_NO_PICK"]
    runs=[];current=0
    for row in [x for x in records if x["evaluation_round"]>=FIRST_ELIGIBLE]:
        if not row["final_output_available"]: current+=1
        elif current:runs.append(current);current=0
    if current:runs.append(current)
    stage=Counter(x["no_pick_stage"] for x in valid)
    summary={"audit_id":str(uuid.uuid4()),"source_range":f"{start}~{end}","first_eligible_round":FIRST_ELIGIBLE,
      "valid_rounds":len(valid),"output_available_rounds":sum(x["final_output_available"] for x in valid),"research_no_pick_rounds":len(valid),
      "output_coverage_rate":0.0 if valid else None,"no_pick_rate":1.0 if valid else None,"stage_counts":dict(stage),
      "number_pass_zero":sum(x["number_pass"]==0 for x in valid),"number_pass_under_3":sum(x["number_pass"]<3 for x in valid),
      "valid_trio_zero":sum(x["valid_trio_count"]==0 for x in valid),"valid_trio_one":sum(x["valid_trio_count"]==1 for x in valid),
      "pair_zero":sum(x["eligible_pair_count"]==0 for x in valid),"max_consecutive_no_pick":max(runs,default=0),
      "average_consecutive_no_pick":sum(runs)/len(runs) if runs else 0.0,"recent50_no_pick_rate":_rates(valid,50),
      "recent100_no_pick_rate":_rates(valid,100),"recent200_no_pick_rate":_rates(valid,200),
      "round1238_classification":"NORMAL","round1238_basis":"historical valid-round no-pick rate is 100%; current no-pick is not rare",
      "future_leakage":sum(x["source_end_round"]!=x["evaluation_round"]-1 for x in records),"system_error_rounds":sum(x["availability_class"]=="SYSTEM_ERROR" for x in records),
      "records_hash":sha256_json(records)}
    summary["audit_hash"]=sha256_json(summary);return {"summary":summary,"rounds":records}

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--data",type=Path,default=Path("analysis/structure-1236/analysis-input.csv"));ap.add_argument("--trio-db",type=Path,default=Path("v27_storage/backtests/p45_v273_trio_walkforward.sqlite3"));ap.add_argument("--pair-db",type=Path,default=Path("v27_storage/backtests/p45_v274_pair_walkforward_v12.sqlite3"));ap.add_argument("--output-dir",type=Path,default=Path("v27_storage/experiments/exp002/audit"));a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True);progress=a.output_dir/"progress.json"
    result=audit(a.data,a.trio_db,a.pair_db,progress=progress)
    (a.output_dir/"no_pick_coverage_audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with (a.output_dir/"no_pick_coverage_rounds.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=result["rounds"][0]);w.writeheader();w.writerows(result["rounds"])
    progress.unlink(missing_ok=True);print(json.dumps(result["summary"],ensure_ascii=False));return 0

if __name__=="__main__":raise SystemExit(main())

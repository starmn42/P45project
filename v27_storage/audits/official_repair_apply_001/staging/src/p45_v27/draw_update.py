"""Safe operational update for newly published official lotto draws."""
from __future__ import annotations

import argparse, csv, hashlib, json, os, shutil, sqlite3, tempfile, urllib.request, uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

from .pairs.final_aggregation import _primary, _support
from .pairs.production import ProductionPairPipeline

OFFICIAL_URL="https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do?srchDir=center&srchLtEpsd={round}"
UPDATE_VERSION="P45-NEW-DRAW-UPDATE-1.0"
ROOT=Path(__file__).resolve().parents[2]
BASE_DATA=ROOT/"analysis/structure-1236/analysis-input.csv"
TRIO_WF_DB=ROOT/"v27_storage/backtests/p45_v273_trio_walkforward.sqlite3"
TRIO_FINAL_DB=ROOT/"v27_storage/backtests/p45_v273_trio_final.sqlite3"
PAIR_WF_DB=ROOT/"v27_storage/backtests/p45_v274_pair_walkforward_v12.sqlite3"
FINAL_REPORT=ROOT/"v27_storage/reports/p45_v274_pair_v12_final_aggregation.json"
LIVE_DIR=ROOT/"v27_storage/live"; LIVE_DB=LIVE_DIR/"p45_new_draw_update_v1.sqlite3"; LIVE_DATA=LIVE_DIR/"p45_live_draws.csv"

SCHEMA="""PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS draw_result(draw_round INTEGER PRIMARY KEY,draw_date TEXT NOT NULL,main_json TEXT NOT NULL,bonus INTEGER NOT NULL,source_url TEXT NOT NULL,source_payload_sha256 TEXT NOT NULL,fetched_at TEXT NOT NULL,CHECK(bonus BETWEEN 1 AND 45));
CREATE TABLE IF NOT EXISTS update_run(run_id TEXT PRIMARY KEY,started_at TEXT NOT NULL,completed_at TEXT,stored_latest_round INTEGER NOT NULL,external_latest_round INTEGER,status TEXT NOT NULL,error_code TEXT,decision_hash TEXT);
CREATE TABLE IF NOT EXISTS prediction_evaluation(evaluation_id TEXT PRIMARY KEY,result_round INTEGER NOT NULL REFERENCES draw_result(draw_round),scope TEXT NOT NULL,prediction_key TEXT NOT NULL,set_a_json TEXT NOT NULL,set_b_json TEXT NOT NULL,integrated_a_hits INTEGER NOT NULL,integrated_b_hits INTEGER NOT NULL,main_a_hits INTEGER NOT NULL,main_b_hits INTEGER NOT NULL,integrated_primary INTEGER NOT NULL,integrated_exact2_support INTEGER NOT NULL,main_primary INTEGER NOT NULL,main_exact2_support INTEGER NOT NULL,evaluated_at TEXT NOT NULL,UNIQUE(result_round,scope,prediction_key));
CREATE TABLE IF NOT EXISTS analysis_snapshot(analysis_round INTEGER PRIMARY KEY,source_end_round INTEGER NOT NULL,status TEXT NOT NULL,valid_for_core INTEGER NOT NULL,official_selection_json TEXT NOT NULL,diagnostic_top3_json TEXT NOT NULL,pair_state_counts_json TEXT NOT NULL,prediction_hash TEXT NOT NULL,created_at TEXT NOT NULL,update_version TEXT NOT NULL,CHECK(analysis_round=source_end_round+1));
CREATE TABLE IF NOT EXISTS provenance(key TEXT PRIMARY KEY,value TEXT NOT NULL);"""

@dataclass(frozen=True)
class Draw:
    round:int; date:str; main:tuple[int,...]; bonus:int; source_url:str; source_sha256:str

def _now()->str:return datetime.now().astimezone().isoformat(timespec="seconds")
def _canonical(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def _sha(v:Any)->str:return hashlib.sha256(v if isinstance(v,bytes) else _canonical(v).encode()).hexdigest()

def validate_draw(draw:Draw,stored_latest:int)->None:
    if draw.round!=stored_latest+1:raise ValueError("DRAW_ROUND_NOT_CONTIGUOUS")
    if len(draw.main)!=6 or len(set(draw.main))!=6:raise ValueError("DRAW_MAIN_INVALID")
    if any(not 1<=n<=45 for n in (*draw.main,draw.bonus)):raise ValueError("DRAW_NUMBER_OUT_OF_RANGE")
    if draw.bonus in draw.main:raise ValueError("DRAW_BONUS_DUPLICATE")

def parse_official(payload:bytes,expected_round:int)->Draw:
    rows=json.loads(payload.decode("utf-8")).get("data",{}).get("list",[])
    row=next((x for x in rows if int(x.get("ltEpsd",-1))==expected_round),None)
    if row is None:raise LookupError("NO_NEW_DRAW")
    ymd=str(row["ltRflYmd"])
    if len(ymd)!=8 or not ymd.isdigit():raise ValueError("DRAW_DATE_INVALID")
    return Draw(expected_round,f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}",tuple(int(row[f"tm{i}WnNo"]) for i in range(1,7)),int(row["bnsWnNo"]),OFFICIAL_URL.format(round=expected_round),hashlib.sha256(payload).hexdigest())

def fetch_official(expected_round:int,timeout:float=15)->Draw:
    req=urllib.request.Request(OFFICIAL_URL.format(round=expected_round),headers={"User-Agent":"P45-New-Draw-Updater/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as res:return parse_official(res.read(),expected_round)

def _base_latest()->int:
    with BASE_DATA.open("r",encoding="utf-8-sig",newline="") as f:return max(int(r[0]) for r in csv.reader(f) if r and r[0].isdigit())
def _connect(path:Path=LIVE_DB)->sqlite3.Connection:
    path.parent.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(path);db.row_factory=sqlite3.Row;db.executescript(SCHEMA);return db
def stored_latest(db:sqlite3.Connection)->int:
    value=db.execute("SELECT MAX(draw_round) FROM draw_result").fetchone()[0];return max(_base_latest(),int(value or 0))

def _materialize_csv(draws:Sequence[Draw],target:Path)->None:
    target.parent.mkdir(parents=True,exist_ok=True)
    with BASE_DATA.open("r",encoding="utf-8-sig",newline="") as src,target.open("w",encoding="utf-8-sig",newline="") as dst:
        rd,wr=csv.reader(src),csv.writer(dst,lineterminator="\n")
        for row in rd:wr.writerow(row)
        for d in sorted(draws,key=lambda x:x.round):wr.writerow([d.round,d.date,*d.main,d.bonus])

def _category(a:int,b:int)->str:
    if a==3 and b==3:return "DOUBLE_TRIPLE_SUCCESS"
    if a==3 or b==3:return "SINGLE_TRIPLE_SUCCESS"
    if a==2 or b==2:return "EXACT2_SUPPORT"
    return "NO_PRIMARY_OR_SUPPORT"
def _hits(nums:Sequence[int],draw:Draw,integrated:bool)->int:
    return len(set(nums)&(set(draw.main)|({draw.bonus} if integrated else set())))
def _evaluation(scope:str,key:str,a:Sequence[int],b:Sequence[int],draw:Draw)->dict[str,Any]:
    ia,ib=_hits(a,draw,True),_hits(b,draw,True);ma,mb=_hits(a,draw,False),_hits(b,draw,False)
    raw={"a_integrated_hits":ia,"b_integrated_hits":ib,"a_main_hits":ma,"b_main_hits":mb}
    return {"scope":scope,"key":key,"a":list(a),"b":list(b),"ia":ia,"ib":ib,"ma":ma,"mb":mb,"ip":int(_primary(raw,"integrated")),"is":int(_support(raw,"integrated")),"mp":int(_primary(raw,"main")),"ms":int(_support(raw,"main")),"integrated_category":_category(ia,ib),"main_category":_category(ma,mb)}

def _previous_predictions(draw:Draw)->list[dict[str,Any]]:
    report=json.loads(FINAL_REPORT.read_text(encoding="utf-8"))
    result=[_evaluation("PAIR_DIAGNOSTIC",x["pair"],x["set1"],x["set2"],draw) for x in report.get("ranking",[])]
    db=sqlite3.connect(f"file:{TRIO_FINAL_DB.resolve()}?mode=ro",uri=True);db.row_factory=sqlite3.Row
    try:
        for row in db.execute("SELECT trio_key,n1,n2,n3 FROM current_trio_final WHERE valid_for_pair=1 ORDER BY final_rank"):
            result.append(_evaluation("TRIO_DIAGNOSTIC",row["trio_key"],(row["n1"],row["n2"],row["n3"]),(),draw))
    finally:db.close()
    return result

def _history_map(draw:Draw,evaluations:Sequence[Mapping[str,Any]])->dict[str,list[dict[str,Any]]]:
    db=sqlite3.connect(f"file:{PAIR_WF_DB.resolve()}?mode=ro",uri=True);db.row_factory=sqlite3.Row
    try:raw=[dict(x) for x in db.execute("SELECT s.*,o.* FROM wf_selection_exposure s JOIN wf_outcome o USING(selection_id) ORDER BY s.evaluation_round")]
    finally:db.close()
    result:dict[str,list[dict[str,Any]]]={}
    for row in raw:result.setdefault(row["base_pair_rule_signature"],[]).append(row)
    pair_evaluations=[x for x in evaluations if x["scope"]=="PAIR_DIAGNOSTIC"]
    if pair_evaluations and result:
        signature=next(iter(result));top=dict(pair_evaluations[0]);top["evaluation_round"]=draw.round;result[signature].append(top)
    return result

def build_next_snapshot(draw:Draw,live_csv:Path,evaluations:Sequence[Mapping[str,Any]])->dict[str,Any]:
    pipeline=ProductionPairPipeline(live_csv,TRIO_WF_DB);prediction=pipeline.build_prediction_context(draw.round+1,draw.round,_history_map(draw,evaluations))
    if pipeline.outcome_accesses:raise RuntimeError("DRAW_UPDATE_FUTURE_LEAKAGE")
    ordered=sorted(prediction.candidates,key=lambda x:(x.rank_key,x.canonical_pair_key));counts={"ready":0,"test_ready":0,"research_hold":0,"system_hold":0};state_key={"PAIR_READY":"ready","PAIR_TEST_READY":"test_ready","PAIR_RESEARCH_HOLD":"research_hold","PAIR_SYSTEM_HOLD":"system_hold"}
    for item in ordered:
        state=item.context["pair_state"]
        if state not in state_key:raise RuntimeError("PAIR_STATE_UNRECOGNIZED")
        counts[state_key[state]]+=1
    valid=[x for x in ordered if x.context["pair_state"] in ("PAIR_READY","PAIR_TEST_READY")]
    official=sorted((*valid[0].member_a,*valid[0].member_b)) if valid else []
    top=[{"rank":i,"pair_key":x.canonical_pair_key,"set_1":list(x.member_a),"set_2":list(x.member_b),"state":x.context["pair_state"],"label":"DIAGNOSTIC ONLY","official_recommendation":False} for i,x in enumerate(ordered[:3],1)]
    out={"analysis_round":draw.round+1,"source_end_round":draw.round,"status":prediction.skip_status or "LIVE_ANALYSIS_READY","valid_for_core":len(valid),"official_selection":official,"diagnostic_top3":top,"pair_state_counts":counts,"source_hash":pipeline.source_hash()};out["prediction_hash"]=_sha(out);return out

def run_update(*,fetcher=fetch_official,db_path:Path=LIVE_DB)->dict[str,Any]:
    db=_connect(db_path);run_id=str(uuid.uuid4());latest=stored_latest(db);db.execute("INSERT INTO update_run(run_id,started_at,stored_latest_round,status) VALUES(?,?,?,?)",(run_id,_now(),latest,"RUNNING"));db.commit()
    try:
        try:draw=fetcher(latest+1)
        except LookupError:
            status="DRAW_ALREADY_CURRENT" if latest>_base_latest() else "NO_NEW_DRAW"
            db.execute("UPDATE update_run SET completed_at=?,external_latest_round=?,status=? WHERE run_id=?",(_now(),latest,status,run_id));db.commit();return {"status":status,"latest_completed_draw":latest}
        if db.execute("SELECT 1 FROM draw_result WHERE draw_round=?",(draw.round,)).fetchone():return {"status":"DRAW_ALREADY_CURRENT","latest_completed_draw":latest}
        validate_draw(draw,latest)
        old=[Draw(int(x["draw_round"]),x["draw_date"],tuple(json.loads(x["main_json"])),int(x["bonus"]),x["source_url"],x["source_payload_sha256"]) for x in db.execute("SELECT * FROM draw_result ORDER BY draw_round")]
        evaluations=_previous_predictions(draw)
        with tempfile.TemporaryDirectory(dir=LIVE_DIR) as temp:
            candidate=Path(temp)/"live.csv";_materialize_csv([*old,draw],candidate);snapshot=build_next_snapshot(draw,candidate,evaluations);published=Path(temp)/"published.csv";shutil.copy2(candidate,published)
            db.execute("BEGIN IMMEDIATE");db.execute("INSERT INTO draw_result VALUES(?,?,?,?,?,?,?)",(draw.round,draw.date,_canonical(draw.main),draw.bonus,draw.source_url,draw.source_sha256,_now()))
            for x in evaluations:db.execute("INSERT INTO prediction_evaluation VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(_sha([draw.round,x["scope"],x["key"]]),draw.round,x["scope"],x["key"],_canonical(x["a"]),_canonical(x["b"]),x["ia"],x["ib"],x["ma"],x["mb"],x["ip"],x["is"],x["mp"],x["ms"],_now()))
            db.execute("INSERT INTO analysis_snapshot VALUES(?,?,?,?,?,?,?,?,?,?)",(snapshot["analysis_round"],snapshot["source_end_round"],snapshot["status"],snapshot["valid_for_core"],_canonical(snapshot["official_selection"]),_canonical(snapshot["diagnostic_top3"]),_canonical(snapshot["pair_state_counts"]),snapshot["prediction_hash"],_now(),UPDATE_VERSION))
            db.execute("UPDATE update_run SET completed_at=?,external_latest_round=?,status=?,decision_hash=? WHERE run_id=?",(_now(),draw.round,"P45_NEW_DRAW_UPDATE_V1_READY",_sha({"draw":draw.__dict__,"snapshot":snapshot}),run_id))
            db.execute("INSERT OR REPLACE INTO provenance VALUES(?,?)",("official_source",draw.source_url));db.commit();os.replace(published,LIVE_DATA)
        return {"status":"P45_NEW_DRAW_UPDATE_V1_READY","run_id":run_id,"latest_completed_draw":draw.round,"current_analysis_draw":draw.round+1,"draw":draw.__dict__,"evaluated_predictions":len(evaluations),**snapshot}
    except ValueError as exc:
        db.rollback();db.execute("UPDATE update_run SET completed_at=?,status=?,error_code=? WHERE run_id=?",(_now(),"DRAW_DATA_INVALID",str(exc),run_id));db.commit();return {"status":"DRAW_DATA_INVALID","error":str(exc),"latest_completed_draw":latest}
    except Exception as exc:
        db.rollback();db.execute("UPDATE update_run SET completed_at=?,status=?,error_code=? WHERE run_id=?",(_now(),"DRAW_UPDATE_FAILED",f"{type(exc).__name__}:{exc}",run_id));db.commit();raise
    finally:db.close()

def read_live_status(db_path:Path=LIVE_DB)->dict[str,Any]|None:
    if not db_path.exists():return None
    db=sqlite3.connect(f"file:{db_path.resolve()}?mode=ro",uri=True);db.row_factory=sqlite3.Row
    try:
        draw=db.execute("SELECT * FROM draw_result ORDER BY draw_round DESC LIMIT 1").fetchone();snap=db.execute("SELECT * FROM analysis_snapshot ORDER BY analysis_round DESC LIMIT 1").fetchone();run=db.execute("SELECT * FROM update_run ORDER BY started_at DESC LIMIT 1").fetchone()
        if not draw or not snap:return None
        return {"latest_completed_draw":draw["draw_round"],"current_analysis_draw":snap["analysis_round"],"draw_update_status":run["status"],"last_update_time":run["completed_at"],"official_selection":json.loads(snap["official_selection_json"]),"diagnostic_top3":json.loads(snap["diagnostic_top3_json"]),"pair_state_counts":json.loads(snap["pair_state_counts_json"]),"valid_for_core":snap["valid_for_core"]}
    finally:db.close()

def main(argv:Sequence[str]|None=None)->int:
    p=argparse.ArgumentParser();p.add_argument("command",choices=("update","status"));a=p.parse_args(argv);result=(read_live_status() or {"status":"NOT_RUN","latest_completed_draw":_base_latest()}) if a.command=="status" else run_update();print(json.dumps(result,ensure_ascii=False,indent=2,default=list));return 0
if __name__=="__main__":raise SystemExit(main())

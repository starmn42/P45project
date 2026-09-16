"""Read-only v2.7.3 outer walk-forward diagnostic; writes no official ledger."""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any
from .integrity import sha256_json
from .stage55_diagnostics import load_draw_csv
from .stage6_diagnostics import diagnose_stage6
from .trio_engine import build_current_trios,build_coverage,generate_trios,rule_signature
from .units import DEFINITIONS

def _round_representatives(args:tuple[str,int])->dict[str,Any]:
    path,outer=args
    try:stage6=diagnose_stage6(Path(path),outer)
    except (ValueError,RuntimeError,IndexError):return {"round":outer,"eligible":False}
    if stage6["source_rounds"][1]>=outer:return {"round":outer,"eligible":False}
    if len(stage6["candidate_numbers"])<6:
        return {"round":outer,"eligible":True,"representatives":[],"candidate_count":len(stage6["candidate_numbers"]),"trio_count":0,
          "candidate_pool_hash":result_pool_hash(stage6),"number_ledger_snapshot_hash":sha256_json({n:stage6["rows"][n]["decision_hash"] for n in sorted(stage6["rows"])}),"timings":stage6.get("timings",{})}
    groups={}
    pool_type=stage6["candidate_pool_type"]
    for trio in generate_trios(stage6["candidate_numbers"]):
        coverage=build_coverage(trio,stage6["rows"],stage6["unit_metrics"],DEFINITIONS)
        signature=rule_signature(pool_type,trio,stage6["rows"],coverage)
        groups.setdefault(signature,[]).append({"trio":trio,"candidate_pool_hash":__import__('p45_v27.integrity',fromlist=['sha256_json']).sha256_json({'type':pool_type,'numbers':stage6['candidate_numbers'],'number_hash':stage6['execution_hash']}),"coverage":coverage})
    representatives=[]
    for signature,choices in groups.items():
        chosen=min(choices,key=lambda x:x["trio"])
        representatives.append({"signature":signature,"trio":chosen["trio"],"candidate_pool_hash":chosen["candidate_pool_hash"],
          "unit_conflict":int("UNIT_TRIO_CONFLICT" in chosen["coverage"]["trio_unit_state_vector"])})
    return {"round":outer,"eligible":True,"representatives":representatives,"candidate_count":len(stage6["candidate_numbers"]),
      "trio_count":sum(1 for _ in generate_trios(stage6["candidate_numbers"])),"candidate_pool_hash":result_pool_hash(stage6),
      "number_ledger_snapshot_hash":sha256_json({n:stage6["rows"][n]["decision_hash"] for n in sorted(stage6["rows"])}),"timings":stage6.get("timings",{})}

def result_pool_hash(stage6:dict[str,Any])->str:
    return sha256_json({'type':stage6['candidate_pool_type'],'numbers':stage6['candidate_numbers'],'number_hash':stage6['execution_hash']})

def diagnose_stage7(path:Path,analysis_round:int,workers:int=8)->dict[str,Any]:
    draws=load_draw_csv(path);actual={d.round:{"main":d.main,"bonus":d.bonus} for d in draws}
    rounds=[r for r in sorted(actual) if r<analysis_round]
    with ProcessPoolExecutor(max_workers=workers) as pool:snapshots=list(pool.map(_round_representatives,((str(path),r) for r in rounds),chunksize=4))
    exposures={};identity={};first=None
    for snap in snapshots:
        if not snap.get("eligible"):continue
        outer=snap["round"];first=outer if first is None else first;draw=actual[outer]
        for rep in snap["representatives"]:
            trio=tuple(rep["trio"]);main=set(draw["main"]);integrated=main|{draw["bonus"]}
            event={"outer_round":outer,"trio":trio,"integrated_hits":len(set(trio)&integrated),"main_hits":len(set(trio)&main),
              "bonus_hit":int(draw["bonus"] in trio),"unit_conflict":rep["unit_conflict"],
              "prediction_hash_before_result":sha256_json({"round":outer,"signature":rep["signature"],"trio":trio,"pool":rep["candidate_pool_hash"]})}
            exposures.setdefault(rep["signature"],[]).append(event);identity[trio]=identity.get(trio,0)+1
    current6=diagnose_stage6(path,analysis_round);current=build_current_trios(current6,DEFINITIONS,exposures)
    return {"analysis_round":analysis_round,"first_eligible_round":first,"eligible_round_count":sum(s.get("eligible",False) for s in snapshots),
      "exposures":exposures,"identity_counts":identity,"current_stage6":current6,"trios":current,"future_blocked":True,
      "execution_hash":sha256_json({"current":current["execution_hash"],"exposures":exposures})}

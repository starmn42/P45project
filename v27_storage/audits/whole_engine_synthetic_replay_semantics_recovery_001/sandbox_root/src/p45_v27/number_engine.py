"""P45 v2.7.2 stage-6 number states and candidate-pool compression."""

from __future__ import annotations

from math import floor
from typing import Any, Iterable, Mapping

from .integrity import sha256_json
from .unit_relations import UNIT_ORDER
from .units.models import Draw, UnitDefinition

EVIDENCE_RANK={"POSITIVE_CONFIRMED":5,"POSITIVE_TENTATIVE":4,"NEUTRAL":3,
               "NEGATIVE_TENTATIVE":2,"NEGATIVE_CONFIRMED":1,"INSUFFICIENT":0}
SAMPLE_RANK={"SUFFICIENT":2,"BORDERLINE":1,"INSUFFICIENT":0}
PERIOD_RANK={"OFFICIAL":2,"BORDERLINE":1,"REFERENCE_ONLY":0,"REFERENCE":0,"TEST_ONLY":0}
BONUS_RANK={"BONUS_DEPENDENCE_NONE":0,"BONUS_DEPENDENCE_MEDIUM":1,"BONUS_DEPENDENCE_HIGH":2}
RISK_RANK={"LOW":0,"MEDIUM":1,"HIGH":2}
STRUCTURE_RANK={"NORMAL":0,"CAUTION":1,"WARNING":2,"SEVERE":3}
STATE_RANK={"NUMBER_PASS":3,"NUMBER_WEAKEN":2,"NUMBER_TEST":1,"NUMBER_HOLD":0,"NUMBER_FAIL":-1,"NUMBER_RETIRED":-2}
GATES=tuple(f"NUMBER_PASS_GATE_{i:02d}" for i in range(1,19))


def _value(mapping: Mapping[str,Any], *path: str, default: Any=None) -> Any:
    cur: Any=mapping
    for key in path:
        if not isinstance(cur,Mapping) or key not in cur:return default
        cur=cur[key]
    return cur


def select_number_context(unit_metrics: Mapping[str,Mapping[str,Any]]) -> tuple[dict[str,Any]|None,list[dict[str,Any]],tuple[Any,...]|None]:
    candidates=[]
    for unit in UNIT_ORDER:
        metric=unit_metrics.get(unit)
        if not metric or metric.get("unit_state") in ("UNIT_SYSTEM_ERROR","UNIT_NOT_APPLICABLE","UNIT_HOLD","UNIT_FAIL"):
            continue
        name=metric.get("primary_context","NO_EVALUABLE_CONTEXT")
        if name=="NO_EVALUABLE_CONTEXT":continue
        base=name.replace("_BORDERLINE","")
        context=metric["contexts"].get(base)
        if not context:continue
        overall=context["overall"]
        r100=context["recent100"];r50=context["recent50"]
        key=(0 if base=="EXACT_VECTOR_CONTEXT" else 1,
             -SAMPLE_RANK[context["sample_state"]],-EVIDENCE_RANK[overall["integrated"]["evidence_label"]],
             -float(overall["integrated"]["wilson_low_95"] or -1),-float(overall["main"]["wilson_low_95"] or -1),
             -PERIOD_RANK[r100["sample_level"]],-float(r100["integrated"]["rate"] or -1),
             -PERIOD_RANK[r50["sample_level"]],-float(r50["integrated"]["rate"] or -1),UNIT_ORDER.index(unit))
        candidates.append({"unit_type":unit,"context_name":base,"context":context,"selection_key":key,
                           "independent_evidence_keys":metric.get("independent_evidence_keys",[])})
    candidates.sort(key=lambda row:row["selection_key"])
    return (candidates[0] if candidates else None,candidates[1:],candidates[0]["selection_key"] if candidates else None)


def combine_number_risk(unit_metrics: Mapping[str,Mapping[str,Any]]) -> dict[str,Any]:
    evaluable=[m for m in unit_metrics.values() if m.get("unit_state") not in ("UNIT_SYSTEM_ERROR","UNIT_NOT_APPLICABLE")]
    bonus=max((m.get("bonus_dependence","BONUS_DEPENDENCE_NONE") for m in evaluable),key=lambda x:BONUS_RANK[x],default="BONUS_DEPENDENCE_NONE")
    risk=max((m.get("opposite_risk","LOW") for m in evaluable),key=lambda x:RISK_RANK[x],default="LOW")
    actual=[m.get("structure_state") for m in evaluable if m.get("structure_state") in STRUCTURE_RANK]
    structure=max(actual,key=lambda x:STRUCTURE_RANK[x],default="NORMAL")
    insufficient=any(m.get("structure_state")=="INSUFFICIENT_SAMPLE" for m in evaluable)
    labels=[_value(m,"contexts",m.get("primary_context","").replace("_BORDERLINE",""),"overall","integrated","evidence_label") for m in evaluable]
    if "POSITIVE_CONFIRMED" in labels and "NEGATIVE_CONFIRMED" in labels:conflict="HIGH"
    elif any(x in ("POSITIVE_CONFIRMED","POSITIVE_TENTATIVE") for x in labels) and "NEGATIVE_TENTATIVE" in labels:conflict="MEDIUM"
    else:conflict="NONE"
    return {"number_bonus_dependence":bonus,"number_opposite_risk":risk,"number_structure_state":structure,
            "structure_insufficient_sample":insufficient,"number_context_conflict":conflict}


def _percentile25(values:list[int])->float:
    if not values:raise ValueError("occupancy history missing")
    ordered=sorted(values);return float(ordered[floor(.25*(len(ordered)-1))])


def calculate_roles(definitions:Mapping[str,UnitDefinition],draws:Iterable[Draw],analysis_round:int,number:int,
                    primary_unit:str|None,unit_metrics:Mapping[str,Mapping[str,Any]])->dict[str,Any]:
    history=sorted((d for d in draws if d.round<analysis_round),key=lambda d:d.round)
    if not history or history[-1].round!=analysis_round-1:raise ValueError("role boundary R-1 missing")
    roles=[]
    for unit in UNIT_ORDER:
        definition=definitions[unit];group=next(g for g in definition.groups if number in g.members)
        occupancies=[len(set((*d.main,d.bonus))&set(group.members)) for d in history]
        current=occupancies[-1];q25=_percentile25(occupancies[:-1])
        role="RETURN_FROM_ANNIHILATION" if current==0 else "RETURN_FROM_LOW_OCCUPANCY" if current<=q25 else "CONTINUATION_CONTEXT"
        evidence=f"{unit}:{group.label}:R{analysis_round-1}:O{current}:Q25={q25:g}"
        roles.append({"unit_type":unit,"role_type":role,"group_id":group.label,"evidence_key":evidence,
                      "occupancy":current,"historical_q25":q25,"structure_state":unit_metrics[unit]["structure_state"]})
    priority={"RETURN_FROM_ANNIHILATION":0,"RETURN_FROM_LOW_OCCUPANCY":1,"CONTINUATION_CONTEXT":2}
    roles.sort(key=lambda r:(priority[r["role_type"]],STRUCTURE_RANK.get(r["structure_state"],4),
                             0 if r["unit_type"]==primary_unit else 1,UNIT_ORDER.index(r["unit_type"])))
    signature=sorted((r["unit_type"],r["role_type"],r["group_id"],r["evidence_key"]) for r in roles)
    return {"return_roles":roles,"primary_return_role":roles[0],"role_signature":signature,
            "has_return_role":any(r["role_type"].startswith("RETURN_") for r in roles)}


def _opposite_directions(primary:Mapping[str,Any])->bool:
    a=EVIDENCE_RANK[primary["overall"]["integrated"]["evidence_label"]]
    b=EVIDENCE_RANK[primary["recent100"]["integrated"]["evidence_label"]]
    return (a>=4 and b<=2) or (a<=2 and b>=4)


def decide_number(number:int,unit_metrics:Mapping[str,Mapping[str,Any]],relation:Mapping[str,Any],pareto_state:str,
                  roles:Mapping[str,Any],*,future_blocked:bool=True,data_ok:bool=True,rules_frozen:bool=True,
                  deterministic_ok:bool=True,gate_order_ok:bool=True,retired_reason:str|None=None)->dict[str,Any]:
    primary,secondary,selection_key=select_number_context(unit_metrics);risk=combine_number_risk(unit_metrics)
    if retired_reason:
        state="NUMBER_RETIRED";first_failed=None;first_limited="RETIRED_VERSION";gate_results={g:False for g in GATES}
    elif not data_ok or not future_blocked or any(m.get("unit_state")=="UNIT_SYSTEM_ERROR" for m in unit_metrics.values()):
        raise RuntimeError("SYSTEM/DATA ERROR must be recorded as CORE_SYSTEM_HOLD, not NUMBER state")
    else:
        ctx=primary["context"] if primary else None
        overall=_value(ctx or {},"overall",default={});r100=_value(ctx or {},"recent100",default={});r50=_value(ctx or {},"recent50",default={})
        integrated=overall.get("integrated",{});main=overall.get("main",{})
        positive_units=[m for m in unit_metrics.values() if m.get("unit_state") in ("UNIT_PASS","UNIT_WEAKEN")]
        negative_sufficient=any(_value(m,"contexts",m.get("primary_context","").replace("_BORDERLINE",""),"overall","integrated","evidence_label")=="NEGATIVE_CONFIRMED" and
                                _value(m,"contexts",m.get("primary_context","").replace("_BORDERLINE",""),"sample_state") == "SUFFICIENT" for m in unit_metrics.values())
        all_negative=bool(unit_metrics) and all(m.get("unit_state")=="UNIT_FAIL" or _value(m,"contexts",m.get("primary_context","").replace("_BORDERLINE",""),"overall","integrated","evidence_label")=="NEGATIVE_CONFIRMED" for m in unit_metrics.values())
        fail=(relation["relation_state"]=="UNIT_NO_SUPPORT" and integrated.get("evidence_label")=="NEGATIVE_CONFIRMED") or \
             (integrated.get("evidence_label")=="NEGATIVE_CONFIRMED" and not positive_units) or \
             (main.get("evidence_label")=="NEGATIVE_CONFIRMED" and integrated.get("evidence_label")!="POSITIVE_CONFIRMED") or \
             (risk["number_opposite_risk"]=="HIGH" and negative_sufficient) or \
             (risk["number_structure_state"]=="SEVERE" and integrated.get("evidence_label")=="NEGATIVE_CONFIRMED") or all_negative
        hold=(primary is None or relation["relation_state"]=="UNIT_RELATION_INCOMPLETE" or
              (relation["relation_state"]=="UNIT_NO_SUPPORT" and integrated.get("evidence_label")!="NEGATIVE_CONFIRMED") or
              risk["number_context_conflict"]=="HIGH" or risk["number_opposite_risk"]=="HIGH" or
              risk["number_bonus_dependence"]=="BONUS_DEPENDENCE_HIGH" or
              (risk["number_structure_state"]=="SEVERE" and integrated.get("evidence_label") not in ("POSITIVE_CONFIRMED","POSITIVE_TENTATIVE")) or
              (ctx is not None and _opposite_directions(ctx) and integrated.get("evidence_label") not in ("POSITIVE_CONFIRMED","NEGATIVE_CONFIRMED")))
        gate_results={
          GATES[0]:future_blocked,GATES[1]:len(unit_metrics)==5 and all(m.get("calculation_status","COMPLETE")=="COMPLETE" for m in unit_metrics.values()),
          GATES[2]:len(relation["unit_state_vector"])==5 and None not in relation["unit_state_vector"],
          GATES[3]:relation["relation_state"]!="UNIT_RELATION_INCOMPLETE",GATES[4]:relation["relation_state"]!="UNIT_NO_SUPPORT",
          GATES[5]:pareto_state=="UNIT_PARETO_NONDOMINATED",GATES[6]:ctx is not None and integrated.get("sample_count",0)>=30,
          GATES[7]:integrated.get("rate") is not None and integrated["rate"]>=7/45+.015,
          GATES[8]:r100.get("integrated",{}).get("sample_count",0)>=15 and (r100.get("integrated",{}).get("rate") or 0)>=7/45,
          GATES[9]:r50.get("integrated",{}).get("sample_count",0)>=8 and (r50.get("integrated",{}).get("rate") or 0)>=7/45-.02,
          GATES[10]:main.get("rate") is not None and main["rate"]>=6/45,GATES[11]:risk["number_bonus_dependence"]=="BONUS_DEPENDENCE_NONE",
          GATES[12]:risk["number_opposite_risk"]!="HIGH",GATES[13]:data_ok,GATES[14]:rules_frozen,GATES[15]:deterministic_ok,
          GATES[16]:risk["number_structure_state"]!="SEVERE",GATES[17]:gate_order_ok}
        pass_caps=risk["number_context_conflict"]!="HIGH" and risk["number_structure_state"]!="WARNING" and pareto_state=="UNIT_PARETO_NONDOMINATED"
        pass_ok=all(gate_results.values()) and pass_caps
        strong=all(gate_results[GATES[i]] for i in range(6,17)) and pass_caps
        mandatory_weaken=(relation["relation_state"]!="UNIT_RELATION_INCOMPLETE" and relation["relation_state"]!="UNIT_NO_SUPPORT" and
            integrated.get("sample_count",0)>=20 and integrated.get("evidence_label") in ("POSITIVE_CONFIRMED","POSITIVE_TENTATIVE") and
            main.get("evidence_label")!="NEGATIVE_CONFIRMED" and risk["number_opposite_risk"]!="HIGH" and
            risk["number_bonus_dependence"]!="BONUS_DEPENDENCE_HIGH" and risk["number_context_conflict"]!="HIGH")
        weak_reason=(not all(gate_results[GATES[i]] for i in (6,8,9,10)) or
            (relation["relation_state"]=="UNIT_CONFLICT" and strong) or risk["number_opposite_risk"]=="MEDIUM" or
            risk["number_bonus_dependence"]=="BONUS_DEPENDENCE_MEDIUM" or risk["number_structure_state"]=="WARNING" or
            (pareto_state=="UNIT_PARETO_DOMINATED") or r100.get("integrated",{}).get("evidence_label") in ("NEUTRAL","INSUFFICIENT"))
        test_reason=(integrated.get("evidence_label") in ("NEUTRAL","NEGATIVE_TENTATIVE") or 20<=integrated.get("sample_count",0)<=29 or
            8<=r100.get("integrated",{}).get("sample_count",0)<=14 or 5<=r50.get("integrated",{}).get("sample_count",0)<=7 or
            pareto_state=="UNIT_PARETO_NOT_COMPARABLE")
        if fail:state="NUMBER_FAIL"
        elif hold:state="NUMBER_HOLD"
        elif pass_ok:state="NUMBER_PASS"
        elif mandatory_weaken and weak_reason:state="NUMBER_WEAKEN"
        elif test_reason:state="NUMBER_TEST"
        else:state="NUMBER_TEST"
        first_failed=next((g for g in GATES if not gate_results[g]),None)
        first_limited=("NUMBER_FAIL_RULE" if state=="NUMBER_FAIL" else "NUMBER_HOLD_RULE" if state=="NUMBER_HOLD" else first_failed)
    ctx=primary["context"] if primary else None
    valid_test=(state=="NUMBER_TEST" and primary is not None and relation["relation_state"]!="UNIT_RELATION_INCOMPLETE" and
        _value(ctx,"overall","integrated","sample_count",default=0)>=20 and _value(ctx,"recent100","integrated","sample_count",default=0)>=8 and
        _value(ctx,"overall","integrated","evidence_label")!="NEGATIVE_CONFIRMED" and _value(ctx,"overall","main","evidence_label")!="NEGATIVE_CONFIRMED" and
        risk["number_opposite_risk"]!="HIGH" and risk["number_bonus_dependence"]!="BONUS_DEPENDENCE_HIGH" and
        risk["number_structure_state"]!="SEVERE" and risk["number_context_conflict"]!="HIGH")
    eligible=state in ("NUMBER_PASS","NUMBER_WEAKEN") or valid_test
    official_return=eligible and roles["has_return_role"] and state not in ("NUMBER_HOLD","NUMBER_FAIL")
    payload={"number":number,"number_state":state,"valid_test_status":valid_test,"primary_number_context":primary,
             "secondary_number_contexts":secondary,"primary_context_selection_key":selection_key,**risk,
             "relation_state":relation["relation_state"],"pareto_state":pareto_state,"gate_results":gate_results,
             "expected_gate_sequence":GATES,"executed_gate_sequence":GATES,"first_failed_gate":first_failed,
             "first_limited_gate":first_limited,"return_roles":roles["return_roles"],"primary_return_role":roles["primary_return_role"],
             "role_signature":roles["role_signature"],"official_return_candidate":official_return,
             "nonreturn_role":"NONRETURN_CANDIDATE" if eligible and not official_return else None,"retired_reason":retired_reason}
    return {**payload,"decision_hash":sha256_json(payload)}


def _overlap(a:set[tuple],b:set[tuple],pa:Mapping[str,Any],pb:Mapping[str,Any])->str:
    if a==b:return "IDENTICAL"
    ta=(pa["unit_type"],pa["role_type"],pa["group_id"]);tb=(pb["unit_type"],pb["role_type"],pb["group_id"])
    if ta==tb:return "HIGH"
    if a&b:return "PARTIAL"
    return "NONE"


def _tie_key(row:Mapping[str,Any])->tuple[Any,...]:
    primary=row["primary_number_context"];ctx=primary["context"] if primary else {}
    overall=ctx.get("overall",{});r100=ctx.get("recent100",{});r50=ctx.get("recent50",{})
    relation_rank={"UNIT_CONSENSUS_SUPPORT":3,"UNIT_PARTIAL_SUPPORT":2,"UNIT_CONFLICT":1,"UNIT_NO_SUPPORT":0}.get(row["relation_state"],-1)
    pareto_rank={"UNIT_PARETO_NONDOMINATED":2,"UNIT_PARETO_DOMINATED":1,"UNIT_PARETO_NOT_COMPARABLE":0}.get(row["pareto_state"],0)
    independent=len(set(primary.get("independent_evidence_keys",[]))) if primary else 0
    independent_rank=2 if independent>=2 else 1 if independent==1 else 0
    period=(EVIDENCE_RANK.get(_value(overall,"integrated","evidence_label"),0),EVIDENCE_RANK.get(_value(r100,"integrated","evidence_label"),0),
            EVIDENCE_RANK.get(_value(r50,"integrated","evidence_label"),0),_value(r100,"integrated","rate",default=-1) or -1,
            _value(r50,"integrated","rate",default=-1) or -1)
    return (-STATE_RANK[row["number_state"]],-int(len(row["unit_state_vector"])==5),-pareto_rank,-relation_rank,
            -(_value(overall,"integrated","wilson_low_95",default=-1) or -1),tuple(-x for x in period),
            -(_value(overall,"main","wilson_low_95",default=-1) or -1),-independent_rank,
            (-SAMPLE_RANK.get(ctx.get("sample_state","INSUFFICIENT"),0),-_value(overall,"integrated","sample_count",default=0)),
            STRUCTURE_RANK[row["number_structure_state"]],tuple(row["overlap_profile"]),
            {"NONE":0,"MEDIUM":1,"HIGH":2}[row["number_context_conflict"]],RISK_RANK[row["number_opposite_risk"]],row["number"])


def finalize_numbers(rows:dict[int,dict[str,Any]])->dict[str,Any]:
    valid=[r for r in rows.values() if r["number_state"] in ("NUMBER_PASS","NUMBER_WEAKEN") or r["valid_test_status"]]
    for row in rows.values():
        counts={"IDENTICAL":0,"HIGH":0,"PARTIAL":0}
        a=set(map(tuple,row["role_signature"]))
        for other in valid:
            if other["number"]==row["number"]:continue
            state=_overlap(a,set(map(tuple,other["role_signature"])),row["primary_return_role"],other["primary_return_role"])
            if state in counts:counts[state]+=1
        row["overlap_profile"]=(counts["IDENTICAL"],counts["HIGH"],counts["PARTIAL"])
    # Pre-tie rank is a dense rank by NUMBER state only; no hidden key resolves ties here.
    state_order=sorted(rows.values(),key=lambda r:-STATE_RANK[r["number_state"]])
    dense_rank=0;previous=None
    for row in state_order:
        current=STATE_RANK[row["number_state"]]
        if current!=previous:dense_rank+=1;previous=current
        row["rank_before_tie_break"]=dense_rank
    ranked=sorted(rows.values(),key=_tie_key)
    for row in ranked:row["tie_break_key"]=_tie_key(row)
    passes=[r for r in ranked if r["number_state"]=="NUMBER_PASS"]
    if len(passes)>=6:pool_type="CORE_PASS_POOL";source=passes
    else:
        pool_type="EXPANDED_TEST_POOL";eligible=[r for r in ranked if r["number_state"] in ("NUMBER_PASS","NUMBER_WEAKEN") or r["valid_test_status"]]
        nondominated=[r for r in eligible if r["pareto_state"]=="UNIT_PARETO_NONDOMINATED"]
        source=nondominated if len(nondominated)>=6 else nondominated+[r for r in eligible if r not in nondominated]
        if len(source)<6:pool_type="RESEARCH_HOLD"
    selected=source[:12] if len(source)>=6 else []
    selected_numbers={r["number"] for r in selected}
    for rank,row in enumerate(ranked,1):
        row["rank_after_tie_break"]=rank;row["candidate_pool_type"]=pool_type if row["number"] in selected_numbers else "NOT_SELECTED"
        row["selected_pool"]=row["number"] in selected_numbers
        row["elimination_stage"]="NUMBER_SELECTED_POOL" if row["selected_pool"] else "NUMBER_RUNNER_UP" if row in source else "NUMBER_MIDDLE_ELIMINATED"
        row["unit_state_vector"]=row.get("unit_state_vector",[])
        row["row_hash"]=sha256_json({k:v for k,v in row.items() if k not in ("row_hash",)})
    result={"candidate_pool_type":pool_type,"candidate_numbers":[r["number"] for r in selected],"rows":rows}
    result["execution_hash"]=sha256_json({"candidate_pool_type":pool_type,"candidate_numbers":result["candidate_numbers"],
                                          "row_hashes":{n:rows[n]["row_hash"] for n in sorted(rows)}})
    return result

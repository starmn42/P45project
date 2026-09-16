"""P45 v2.7.3 stage-7 deterministic TRIO research engine."""
from __future__ import annotations

from itertools import combinations
from math import comb,sqrt
from typing import Any,Iterable,Mapping,Sequence

from .integrity import sha256_json
from .unit_relations import UNIT_ORDER

RULE_VERSION="P45-v2.7.3-TRIO"
NUMBER_RANK={"NUMBER_PASS":3,"NUMBER_WEAKEN":2,"NUMBER_TEST":1}
UNIT_RANK={"UNIT_TRIO_COMPLETE_SUPPORT":4,"UNIT_TRIO_PARTIAL_SUPPORT":3,"UNIT_TRIO_TEST_MIXED":2,"UNIT_TRIO_CONFLICT":1,"UNIT_TRIO_INCOMPLETE":0}
ROLE_RANK={"ROLE_COMPLETE_DIVERSITY":2,"ROLE_PARTIAL_DIVERSITY":1,"ROLE_DUPLICATED":0}
RISK_RANK={"LOW":0,"MEDIUM":1,"HIGH":2}
STRUCTURE_RANK={"NORMAL":0,"CAUTION":1,"WARNING":2,"SEVERE":3}
GATES=tuple(f"TRIO_PASS_GATE_{i:02d}" for i in range(1,17))

def random_probability(scope:str,k:int)->float:
    m=7 if scope=="INTEGRATED" else 6
    return comb(3,k)*comb(42,m-k)/comb(45,m)

def wilson95(x:int,n:int)->tuple[float,float]:
    if n<=0:return (0.0,1.0)
    z=1.959963984540054;p=x/n;d=1+z*z/n
    c=(p+z*z/(2*n))/d;h=z*sqrt((p*(1-p)+z*z/(4*n))/n)/d
    low=max(0.0,c-h);high=min(1.0,c+h)
    return (0.0 if abs(low)<1e-15 else low),high

def _binomial_tail(n:int,x:int,p:float,upper:bool)->float:
    if n<=0:return 1.0
    rng=range(x,n+1) if upper else range(0,x+1)
    return min(1.0,sum(comb(n,k)*(p**k)*((1-p)**(n-k)) for k in rng))

def statistic(x:int,n:int,p0:float,minimum:int=200)->dict[str,Any]:
    rate=x/n if n else 0.0;lo,hi=wilson95(x,n);pu=_binomial_tail(n,x,p0,True);pl=_binomial_tail(n,x,p0,False)
    if n<minimum:label="INSUFFICIENT"
    elif rate>p0 and pu<.05 and lo>p0:label="SUPERIOR_CONFIRMED"
    elif rate>p0:label="SUPERIOR_TENTATIVE"
    elif rate<p0 and pl<.05 and hi<p0:label="INFERIOR_CONFIRMED"
    elif rate<p0:label="INFERIOR_TENTATIVE"
    else:label="NEUTRAL"
    return {"sample_count":n,"success_count":x,"rate":rate,"p0":p0,"wilson_low":lo,"wilson_high":hi,
            "p_upper":pu,"p_lower":pl,"evidence_label":label}

def generate_trios(numbers:Sequence[int])->list[tuple[int,int,int]]:
    clean=sorted(set(numbers))
    if len(clean)!=len(numbers) or not 6<=len(clean)<=12 or any(n<1 or n>45 for n in clean):raise ValueError("candidate pool must contain 6..12 unique numbers")
    return list(combinations(clean,3))

def _role(row:Mapping[str,Any],unit:str)->Mapping[str,Any]:
    return next(r for r in row["return_roles"] if r["unit_type"]==unit)

def build_coverage(trio:Sequence[int],rows:Mapping[int,Mapping[str,Any]],unit_metrics:Mapping[str,Mapping[int,Mapping[str,Any]]],definitions:Mapping[str,Any])->dict[str,Any]:
    cells=[];unit_states=[];diversities=[];overlaps=[]
    for unit in UNIT_ORDER:
        ucells=[]
        for number in trio:
            row=rows[number];metric=unit_metrics[unit][number];role=_role(row,unit)
            group=next(g for g in definitions[unit].groups if number in g.members)
            cell={"number":number,"unit_type":unit,"unit_group_id":group.label,"unit_group_members":list(group.members),
                  "unit_state":metric["unit_state"],"primary_context_key":metric.get("primary_context"),"role_type":role["role_type"],
                  "return_role":role["role_type"] if role["role_type"].startswith("RETURN_") else None,
                  "nonreturn_role":"NONRETURN_CANDIDATE" if not role["role_type"].startswith("RETURN_") else None,
                  "opposite_risk":metric.get("opposite_risk","LOW"),"structure_state":metric.get("structure_state","NORMAL"),
                  "raw_evidence_ids":[role["evidence_key"]],"related_evidence_ids":[],
                  "independent_evidence_ids":metric.get("independent_evidence_keys",[]),"duplicate_evidence_ids":[],
                  "source_metric_hash":sha256_json(metric)}
            ucells.append(cell);cells.append(cell)
        states=[c["unit_state"] for c in ucells];high=any(c["opposite_risk"]=="HIGH" for c in ucells)
        if any(s in ("UNIT_SYSTEM_ERROR","UNIT_NOT_APPLICABLE") for s in states):us="UNIT_TRIO_INCOMPLETE"
        elif any(s=="UNIT_FAIL" for s in states) or high:us="UNIT_TRIO_CONFLICT"
        elif all(s in ("UNIT_PASS","UNIT_WEAKEN") for s in states):us="UNIT_TRIO_COMPLETE_SUPPORT"
        elif sum(s in ("UNIT_PASS","UNIT_WEAKEN") for s in states)==2 and states.count("UNIT_TEST")==1:us="UNIT_TRIO_PARTIAL_SUPPORT"
        elif sum(s in ("UNIT_PASS","UNIT_WEAKEN") for s in states)==1 and states.count("UNIT_TEST")==2:us="UNIT_TRIO_TEST_MIXED"
        else:us="UNIT_TRIO_CONFLICT"
        kinds=len(set(c["role_type"] for c in ucells));div="ROLE_COMPLETE_DIVERSITY" if kinds==3 else "ROLE_PARTIAL_DIVERSITY" if kinds==2 else "ROLE_DUPLICATED"
        sets=[set(c["raw_evidence_ids"]+c["independent_evidence_ids"]+c["related_evidence_ids"]) for c in ucells]
        if sets[0]==sets[1]==sets[2]:ov="EVIDENCE_IDENTICAL"
        elif set.intersection(*sets):ov="EVIDENCE_HIGH_OVERLAP"
        elif any(sets[i]&sets[j] for i,j in combinations(range(3),2)):ov="EVIDENCE_PARTIAL_OVERLAP"
        else:ov="EVIDENCE_NONE"
        unit_states.append(us);diversities.append(div);overlaps.append(ov)
    return {"cells":cells,"trio_unit_state_vector":unit_states,"role_diversity_vector":diversities,"evidence_overlap_vector":overlaps,
            "matrix_hash":sha256_json(cells)}

def rule_signature(pool_type:str,trio:Sequence[int],rows:Mapping[int,Mapping[str,Any]],coverage:Mapping[str,Any])->str:
    payload={"candidate_pool_type":pool_type,"number_state_vector":sorted((rows[n]["number_state"] for n in trio),key=lambda s:NUMBER_RANK.get(s,-9)),
      "trio_unit_state_vector":coverage["trio_unit_state_vector"],"role_diversity_vector":coverage["role_diversity_vector"],
      "member_opposite_risk":max((rows[n]["number_opposite_risk"] for n in trio),key=lambda x:RISK_RANK[x]),
      "member_structure":max((rows[n]["number_structure_state"] for n in trio),key=lambda x:STRUCTURE_RANK.get(x,-1)),
      "evidence_overlap":coverage["evidence_overlap_vector"]}
    return sha256_json(payload)

def pareto_classify(rows:Mapping[str,Mapping[str,Any]])->tuple[dict[str,str],list[tuple[str,str]]]:
    def vector(r:Mapping[str,Any])->tuple[int,...]:
        ns=sorted((NUMBER_RANK[s] for s in r["number_states"]));return tuple(ns)+tuple(UNIT_RANK[s] for s in r["coverage"]["trio_unit_state_vector"])+tuple(ROLE_RANK[s] for s in r["coverage"]["role_diversity_vector"])
    vec={k:vector(v) for k,v in rows.items()};dom=[]
    for a,b in combinations(sorted(rows),2):
        va,vb=vec[a],vec[b]
        if all(x>=y for x,y in zip(va,vb)) and any(x>y for x,y in zip(va,vb)):dom.append((a,b))
        elif all(y>=x for x,y in zip(va,vb)) and any(y>x for x,y in zip(va,vb)):dom.append((b,a))
    dominated={b for _,b in dom};states={k:("UNIT_PARETO_DOMINATED" if k in dominated else "UNIT_PARETO_NONDOMINATED") for k in rows}
    return states,dom

def performance(outcomes:Sequence[Mapping[str,Any]])->dict[str,Any]:
    periods={"OVERALL":list(outcomes),"FIRST_HALF":list(outcomes[:len(outcomes)//2]),"SECOND_HALF":list(outcomes[len(outcomes)//2:]),
      "RECENT_100":list(outcomes[-100:]),"RECENT_50":list(outcomes[-50:]),"RECENT_20":list(outcomes[-20:])}
    metrics={}
    for period,items in periods.items():
      for scope,key in (("INTEGRATED","integrated_hits"),("MAIN","main_hits")):
       for k in (3,2,1,0):
        n=len(items);x=sum(o[key]==k for o in items);metrics[(scope,f"EXACT_{k}_OF_3",period)]={"sample_count":n,"hit_count":x,"rate":x/n if n else 0.0}
    stats={(scope,f"EXACT_{k}_OF_3"):statistic(metrics[(scope,f"EXACT_{k}_OF_3","OVERALL")]["hit_count"],len(outcomes),random_probability(scope,k)) for scope in ("INTEGRATED","MAIN") for k in (3,2,1,0)}
    return {"period_metrics":metrics,"statistics":stats}

def recent_collapse(perf:Mapping[str,Any])->str:
    m=perf["period_metrics"];overall=perf["statistics"][("INTEGRATED","EXACT_2_OF_3")];p0=random_probability("INTEGRATED",2)
    flags=[]
    for p in ("RECENT_100","RECENT_50"):
        x=m[("INTEGRATED","EXACT_2_OF_3",p)];w=wilson95(x["hit_count"],x["sample_count"])
        flags.append(x["sample_count"]>0 and x["rate"]<p0 and w[1]<max(p0,overall["wilson_low"]))
    return "RECENT_SUPPORT_COLLAPSE_SEVERE" if all(flags) else "RECENT_SUPPORT_COLLAPSE_WARNING" if any(flags) else "RECENT_SUPPORT_STABLE"

def structure_collapse(outcomes:Sequence[Mapping[str,Any]])->dict[str,Any]:
    """Percentile collapse ledger over eligible historical endpoints; recent20 is excluded."""
    def values(items:Sequence[Mapping[str,Any]])->list[float]:
        if not items:return [0.0]*6
        def rate(seq:Sequence[Mapping[str,Any]],key:str,k:int)->float:return sum(x[key]==k for x in seq)/len(seq) if seq else 0.0
        r100=items[-100:];r50=items[-50:]
        return [max(0.,rate(items,'integrated_hits',3)-rate(r100,'integrated_hits',3)),max(0.,rate(items,'integrated_hits',3)-rate(r50,'integrated_hits',3)),
          max(0.,rate(items,'integrated_hits',2)-rate(r100,'integrated_hits',2)),max(0.,rate(items,'integrated_hits',2)-rate(r50,'integrated_hits',2)),
          max(0.,rate(r50,'integrated_hits',0)-rate(items,'integrated_hits',0)),max(0.,rate(r50,'unit_conflict',1)-rate(items,'unit_conflict',1))]
    current=values(outcomes);history=[values(outcomes[:end]) for end in range(50,len(outcomes))]
    if len(history)<50:return {"state":"INSUFFICIENT_SAMPLE","sample_count":len(history),"percentiles":[],"current_values":current}
    percentiles=[100*sum(p[i]<=current[i] for p in history)/len(history) for i in range(6)];p=max(percentiles)
    state="NORMAL" if p<90 else "CAUTION" if p<95 else "WARNING" if p<99 else "SEVERE"
    return {"state":state,"sample_count":len(history),"percentiles":percentiles,"overall_percentile":p,"current_values":current}

def run_walkforward(rounds:Iterable[int],pipeline:Any,actual_by_round:Mapping[int,Mapping[str,Any]],definitions:Mapping[str,Any])->dict[str,Any]:
    """Recompute the complete upstream pipeline for every R and expose one TRIO per signature."""
    exposures:dict[str,list[dict[str,Any]]]={};identity:dict[tuple[int,int,int],int]={};first=None;calls=[]
    for outer_round in rounds:
        stage6=pipeline(outer_round);calls.append(outer_round)
        if stage6.get("analysis_round")!=outer_round or stage6.get("source_rounds",(0,0))[1]>=outer_round:raise RuntimeError("future data leakage")
        if len(stage6.get("candidate_numbers",[]))<6:continue
        current=build_current_trios(stage6,definitions,exposures)
        if first is None:first=outer_round
        grouped:dict[str,list[dict[str,Any]]]={}
        for row in current["rows"].values():grouped.setdefault(row["trio_rule_signature"],[]).append(row)
        for signature,choices in grouped.items():
            # Pre-result structural order; current-round result is never an input.
            choices.sort(key=lambda r:(tuple(-NUMBER_RANK[s] for s in sorted(r["number_states"],key=lambda s:NUMBER_RANK[s])),
              tuple(-UNIT_RANK[s] for s in r["coverage"]["trio_unit_state_vector"]),tuple(-ROLE_RANK[s] for s in r["coverage"]["role_diversity_vector"]),r["trio"]))
            chosen=choices[0];actual=actual_by_round[outer_round];main=set(actual["main"]);integrated=main|{actual["bonus"]};trio=set(chosen["trio"])
            payload={"outer_round":outer_round,"trio":chosen["trio"],"integrated_hits":len(trio&integrated),"main_hits":len(trio&main),
              "bonus_hit":int(actual["bonus"] in trio),"unit_conflict":int("UNIT_TRIO_CONFLICT" in chosen["coverage"]["trio_unit_state_vector"]),
              "prediction_hash_before_result":sha256_json({"round":outer_round,"signature":signature,"trio":chosen["trio"],"pool":chosen["candidate_pool_hash"]})}
            exposures.setdefault(signature,[]).append(payload);identity[chosen["trio"]]=identity.get(chosen["trio"],0)+1
    return {"first_eligible_round":first,"exposures":exposures,"identity_counts":identity,"pipeline_calls":calls,
      "future_blocked":True,"execution_hash":sha256_json(exposures)}

def classify_trio(row:dict[str,Any])->dict[str,Any]:
    st=row["performance"]["statistics"];i3=st[("INTEGRATED","EXACT_3_OF_3")];m3=st[("MAIN","EXACT_3_OF_3")];i2=st[("INTEGRATED","EXACT_2_OF_3")]
    n=row["selection_rule_exposure_count"];conf=row["coverage"]["trio_unit_state_vector"].count("UNIT_TRIO_CONFLICT");inc=row["coverage"]["trio_unit_state_vector"].count("UNIT_TRIO_INCOMPLETE")
    positive=i3["evidence_label"] in ("SUPERIOR_CONFIRMED","SUPERIOR_TENTATIVE")
    bonus=("BONUS_DEPENDENCE_HIGH" if i3["evidence_label"]=="SUPERIOR_CONFIRMED" and m3["evidence_label"]=="INFERIOR_CONFIRMED" else
           "BONUS_DEPENDENCE_MEDIUM" if positive and m3["rate"]<random_probability("MAIN",3) and m3["evidence_label"]!="INFERIOR_CONFIRMED" else "BONUS_DEPENDENCE_NONE")
    member_risk=max(row["member_risks"],key=lambda x:RISK_RANK[x]);collapse=recent_collapse(row["performance"])
    high=(member_risk=="HIGH" or (positive and i2["evidence_label"]=="INFERIOR_CONFIRMED") or bonus=="BONUS_DEPENDENCE_HIGH" or collapse=="RECENT_SUPPORT_COLLAPSE_SEVERE" or conf>=2)
    medium=(member_risk=="MEDIUM" or (positive and i2["evidence_label"]=="INFERIOR_TENTATIVE") or bonus=="BONUS_DEPENDENCE_MEDIUM" or collapse=="RECENT_SUPPORT_COLLAPSE_WARNING" or conf==1)
    risk="HIGH" if high else "MEDIUM" if medium else "LOW"
    structure=row.get("final_structure_state","INSUFFICIENT_SAMPLE")
    fail=(n>=200 and i3["evidence_label"]=="INFERIOR_CONFIRMED") or (not positive and i2["evidence_label"]=="INFERIOR_CONFIRMED") or conf>=3 or (risk=="HIGH" and (i3["evidence_label"]=="INFERIOR_CONFIRMED" or i2["evidence_label"]=="INFERIOR_CONFIRMED")) or (structure=="SEVERE" and i3["evidence_label"]=="INFERIOR_CONFIRMED")
    hold=n<50 or risk=="HIGH" or structure=="SEVERE" or bonus=="BONUS_DEPENDENCE_HIGH" or conf>=2
    gates=(all(s=="NUMBER_PASS" for s in row["number_states"]),inc==0,len(row["coverage"]["cells"])==15,row["pareto_state"]=="UNIT_PARETO_NONDOMINATED",row["future_blocked"],n>=200,i3["evidence_label"]=="SUPERIOR_CONFIRMED",True,m3["rate"]>=random_probability("MAIN",3) and m3["evidence_label"]!="INFERIOR_CONFIRMED",i2["rate"]>=random_probability("INTEGRATED",2) and i2["evidence_label"]!="INFERIOR_CONFIRMED",collapse!="RECENT_SUPPORT_COLLAPSE_SEVERE",risk!="HIGH",structure!="SEVERE",True,row["deterministic_ok"],True)
    pass_ok=all(gates) and row["candidate_pool_type"]=="CORE_PASS_POOL" and bonus!="BONUS_DEPENDENCE_HIGH" and conf==0
    weaken=n>=200 and all(s in ("NUMBER_PASS","NUMBER_WEAKEN") for s in row["number_states"]) and i3["evidence_label"] in ("SUPERIOR_CONFIRMED","SUPERIOR_TENTATIVE") and i2["evidence_label"]!="INFERIOR_CONFIRMED" and risk!="HIGH" and structure!="SEVERE" and bonus!="BONUS_DEPENDENCE_HIGH"
    test=(50<=n<=199 or "NUMBER_TEST" in row["number_states"] or i3["evidence_label"] in ("NEUTRAL","SUPERIOR_TENTATIVE","INFERIOR_TENTATIVE") or structure=="INSUFFICIENT_SAMPLE" or row["pareto_state"]=="NOT_COMPARABLE")
    state="TRIO_FAIL" if fail else "TRIO_HOLD" if hold else "TRIO_PASS" if pass_ok else "TRIO_WEAKEN" if weaken else "TRIO_TEST" if test else "TRIO_TEST"
    valid_test=state=="TRIO_TEST" and n>=50 and i3["evidence_label"]!="INFERIOR_CONFIRMED" and i2["evidence_label"]!="INFERIOR_CONFIRMED" and risk!="HIGH" and structure!="SEVERE" and bonus!="BONUS_DEPENDENCE_HIGH" and inc==0 and conf<2 and row["future_blocked"] and row["deterministic_ok"]
    row.update({"trio_state":state,"valid_trio_test":valid_test,"valid_for_pair":state in ("TRIO_PASS","TRIO_WEAKEN") or valid_test,
      "bonus_dependency_state":bonus,"member_opposite_risk":member_risk,"trio_rule_opposite_risk":risk,"recent_support_collapse_state":collapse,
      "gate_results":dict(zip(GATES,gates)),"first_failed_gate":next((g for g,v in zip(GATES,gates) if not v),None)})
    hash_payload={k:v for k,v in row.items() if k not in ("decision_hash","performance")}
    hash_payload["performance_hash"]=sha256_json({"period_metrics":{"|".join(k):v for k,v in row["performance"]["period_metrics"].items()},
      "statistics":{"|".join(k):v for k,v in row["performance"]["statistics"].items()}})
    row["decision_hash"]=sha256_json(hash_payload);return row

def build_current_trios(stage6:Mapping[str,Any],definitions:Mapping[str,Any],exposures:Mapping[str,Sequence[Mapping[str,Any]]]|None=None)->dict[str,Any]:
    pool=stage6["candidate_numbers"];rows={};exposures=exposures or {}
    pool_hash=sha256_json({"type":stage6["candidate_pool_type"],"numbers":pool,"number_hash":stage6["execution_hash"]})
    for trio in generate_trios(pool):
        key="-".join(map(str,trio));cov=build_coverage(trio,stage6["rows"],stage6["unit_metrics"],definitions)
        rows[key]={"trio":trio,"candidate_pool_type":stage6["candidate_pool_type"],"candidate_pool_hash":pool_hash,
          "number_states":[stage6["rows"][n]["number_state"] for n in trio],"member_risks":[stage6["rows"][n]["number_opposite_risk"] for n in trio],
          "coverage":cov,"trio_rule_signature":rule_signature(stage6["candidate_pool_type"],trio,stage6["rows"],cov),"pareto_state":"NOT_COMPARABLE",
          "selection_rule_exposure_count":0,"trio_identity_exposure_count":0,"performance":performance([]),"future_blocked":True,"deterministic_ok":True,
          "member_structure_summary":max((stage6["rows"][n]["number_structure_state"] for n in trio),key=lambda x:STRUCTURE_RANK.get(x,-1)),"trio_rule_structure_state":"INSUFFICIENT_SAMPLE","final_structure_state":"INSUFFICIENT_SAMPLE"}
    ps,dom=pareto_classify(rows)
    for key,row in rows.items():
        row["pareto_state"]=ps[key];out=list(exposures.get(row["trio_rule_signature"],[]));row["selection_rule_exposure_count"]=len(out)
        row["trio_identity_exposure_count"]=sum(tuple(o.get("trio",()))==row["trio"] for o in out);row["performance"]=performance(out)
        sc=structure_collapse(out);row["trio_rule_structure_state"]=sc["state"]
        member=row["member_structure_summary"];row["final_structure_state"]=(max((member,sc["state"]),key=lambda x:STRUCTURE_RANK.get(x,-1)) if sc["state"]!="INSUFFICIENT_SAMPLE" else member)
        row["structure_ledger"]=sc;classify_trio(row)
    result={"rows":rows,"pareto_relations":dom,"candidate_pool_hash":pool_hash,"trio_count":len(rows)}
    result["execution_hash"]=sha256_json({k:rows[k]["decision_hash"] for k in sorted(rows)});return result

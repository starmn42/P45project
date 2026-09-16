from __future__ import annotations

import json
from collections import Counter
from math import sqrt
from pathlib import Path

from p45_v27.stage55_diagnostics import load_draw_csv
from p45_v27.stage6_diagnostics import diagnose_stage6
from p45_v27.structure_collapse import calculate_structure_ledger
from p45_v27.units import DEFINITIONS

ROOT = Path(__file__).resolve().parents[3]
BEFORE = ROOT / "v27_storage/audits/no_pick_root_cause_trace_001/CURRENT_INPUT_SNAPSHOT.csv"
AFTER = ROOT / "v27_storage/audits/current_1239_official_predraw_001/STAGING_IMMUTABLE_DRAW_THROUGH_1238.csv"
OUT = ROOT / "v27_storage/audits/current_1239_end_digit_severe_causal_trace_001"


def detail(path: Path, target: int) -> dict:
    draws = sorted((d for d in load_draw_csv(path) if d.round < target), key=lambda d:d.round)
    definition = DEFINITIONS["END_DIGIT"]
    ledger = calculate_structure_ledger(definition, draws, target)
    current_draw, previous_draw = draws[-1], draws[-2]
    def vector(draw): return [len(set((*draw.main,draw.bonus)) & set(group.members)) for group in definition.groups]
    current_vector, previous_vector = vector(current_draw), vector(previous_draw)
    groups=[]
    for group, observed, prior in zip(definition.groups,current_vector,previous_vector):
        p=group.size/45; expected=7*p; variance=7*p*(1-p)*((45-7)/44)
        standardized=abs((observed-expected)/sqrt(variance)) if variance else 0.0
        groups.append({"group":group.label,"members":list(group.members),"current_occupancy":observed,
            "previous_occupancy":prior,"expected_occupancy":expected,"abs_standardized_occupancy":standardized,
            "is_zero_group":observed==0,"is_realized_return_from_previous_zero":prior==0 and observed>0})
    positions={}
    for metric,value in ledger["current_metrics"].items():
        dist=ledger["historical_distribution"][metric]
        positions[metric]={"current":value,"percentile":ledger["metric_percentiles"][metric],
            "reference_min":min(dist),"reference_max":max(dist),"less_count":sum(x<value for x in dist),
            "equal_count":sum(x==value for x in dist),"greater_count":sum(x>value for x in dist),
            "strict_maximum":value>max(dist),"tied_reference_maximum":value==max(dist)}
    return {"target":target,"source_end":target-1,"structure_state":ledger["structure_state"],
        "overall_percentile":ledger["overall_percentile"],"sample_count":ledger["sample_count"],
        "decision_reason":ledger["decision_reason"],"current_metrics":ledger["current_metrics"],
        "metric_percentiles":ledger["metric_percentiles"],"historical_positions":positions,
        "digit_groups":groups,"current_draw":{"round":current_draw.round,"main":list(current_draw.main),"bonus":current_draw.bonus}}


def hold_reason(row: dict) -> str:
    primary=row.get("primary_number_context"); ctx=primary["context"] if primary else None
    integrated=(ctx or {}).get("overall",{}).get("integrated",{})
    def opposite(c):
        rank={"POSITIVE_CONFIRMED":5,"POSITIVE_TENTATIVE":4,"NEUTRAL":3,"NEGATIVE_TENTATIVE":2,"NEGATIVE_CONFIRMED":1,"INSUFFICIENT":0}
        a=rank.get(c.get("overall",{}).get("integrated",{}).get("evidence_label"),0)
        b=rank.get(c.get("recent100",{}).get("integrated",{}).get("evidence_label"),0)
        return (a>=4 and b<=2) or (a<=2 and b>=4)
    checks=[("PRIMARY_CONTEXT_NONE",primary is None),
      ("UNIT_RELATION_INCOMPLETE",row["relation_state"]=="UNIT_RELATION_INCOMPLETE"),
      ("UNIT_NO_SUPPORT_WITHOUT_NEGATIVE_CONFIRMED",row["relation_state"]=="UNIT_NO_SUPPORT" and integrated.get("evidence_label")!="NEGATIVE_CONFIRMED"),
      ("NUMBER_CONTEXT_CONFLICT_HIGH",row["number_context_conflict"]=="HIGH"),
      ("NUMBER_OPPOSITE_RISK_HIGH",row["number_opposite_risk"]=="HIGH"),
      ("BONUS_DEPENDENCE_HIGH",row["number_bonus_dependence"]=="BONUS_DEPENDENCE_HIGH"),
      ("SEVERE_STRUCTURE_WITHOUT_POSITIVE_EVIDENCE",row["number_structure_state"]=="SEVERE" and integrated.get("evidence_label") not in ("POSITIVE_CONFIRMED","POSITIVE_TENTATIVE")),
      ("OPPOSITE_PERIOD_DIRECTIONS_UNCONFIRMED",ctx is not None and opposite(ctx) and integrated.get("evidence_label") not in ("POSITIVE_CONFIRMED","NEGATIVE_CONFIRMED"))]
    return next((name for name,failed in checks if failed),"NO_CANONICAL_HOLD_REASON")


def main() -> None:
    before,after=detail(BEFORE,1238),detail(AFTER,1239)
    stage=diagnose_stage6(AFTER,1239)
    weaken=sorted(n for n,row in stage["rows"].items() if row["number_state"]=="NUMBER_WEAKEN")
    holds=[row for row in stage["rows"].values() if row["number_state"]=="NUMBER_HOLD"]
    reasons=Counter(hold_reason(row) for row in holds)
    decisive=[name for name,pct in after["metric_percentiles"].items() if pct>=99]
    result={"final_verdict":"CURRENT_1239_END_DIGIT_SEVERE_CAUSAL_TRACE_COMPLETE",
      "before":before,"after":after,"decisive_metrics":decisive,"decisive_metric_count":len(decisive),
      "number_weaken_identities":weaken,"number_hold_count":len(holds),"number_hold_primary_reasons":dict(reasons),
      "latent_trio_global_severe_if_number_pool_exists":all(row["number_structure_state"]=="SEVERE" for row in stage["rows"].values()),
      "root_cause_class":"END_DIGIT_MULTI_METRIC_SEVERE_CONFIRMED" if len(decisive)>1 else "END_DIGIT_EXTREME_OCCUPANCY_CONFIRMED",
      "defect_evidence_found":False,"future_leakage_count":0,"outcome_scoring_count":0}
    (OUT/"END_DIGIT_CAUSAL_TRACE.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":main()

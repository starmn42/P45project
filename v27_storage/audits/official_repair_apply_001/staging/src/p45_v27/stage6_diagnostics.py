"""Read-only P45 v2.7.2 stage-6 orchestration; creates no TRIO or CORE lock."""

from __future__ import annotations

from collections import Counter
from time import perf_counter
from pathlib import Path
from typing import Any

from .number_engine import calculate_roles,decide_number,finalize_numbers
from .stage55_diagnostics import load_draw_csv
from .structure_collapse import calculate_structure_ledger
from .unit_relations import build_number_relations,pareto_classify
from .unit_states import evaluate_all_units
from .units import DEFINITIONS


def diagnose_stage6(path:Path,analysis_round:int)->dict[str,Any]:
    started=perf_counter()
    draws=load_draw_csv(path)
    loaded=perf_counter()
    structures={u:calculate_structure_ledger(d,draws,analysis_round) for u,d in DEFINITIONS.items()}
    metrics=evaluate_all_units(DEFINITIONS,draws,analysis_round,{u:x["structure_state"] for u,x in structures.items()})
    units_done=perf_counter()
    relations=build_number_relations(metrics)
    pareto=pareto_classify({str(n):relations[n] for n in range(1,46)})
    relations_done=perf_counter()
    rows={}
    for n in range(1,46):
        unit_metrics={u:metrics[u][n] for u in DEFINITIONS}
        primary,_,_=__import__("p45_v27.number_engine",fromlist=["select_number_context"]).select_number_context(unit_metrics)
        roles=calculate_roles(DEFINITIONS,draws,analysis_round,n,primary["unit_type"] if primary else None,unit_metrics)
        row=decide_number(n,unit_metrics,relations[n],pareto[str(n)],roles)
        row["unit_state_vector"]=relations[n]["unit_state_vector"]
        rows[n]=row
    numbers_done=perf_counter()
    result=finalize_numbers(rows)
    candidates_done=perf_counter()
    used=[d for d in draws if d.round<analysis_round]
    result.update({"analysis_round":analysis_round,"source_rounds":(used[0].round,used[-1].round),
        "state_counts":dict(Counter(r["number_state"] for r in rows.values())),
        "valid_test_count":sum(r["valid_test_status"] for r in rows.values()),
        "return_candidate_count":sum(r["official_return_candidate"] for r in rows.values()),
        "nonreturn_candidate_count":sum(r["nonreturn_role"]=="NONRETURN_CANDIDATE" for r in rows.values()),
        "relation_counts":dict(Counter(r["relation_state"] for r in rows.values())),
        "structures":structures,"unit_metrics":metrics,"relations":relations,"pareto":pareto,
        "timings":{"load_seconds":loaded-started,"unit_seconds":units_done-loaded,"relation_seconds":relations_done-units_done,
                   "number_seconds":numbers_done-relations_done,"candidate_seconds":candidates_done-numbers_done,"total_seconds":candidates_done-started}})
    return result

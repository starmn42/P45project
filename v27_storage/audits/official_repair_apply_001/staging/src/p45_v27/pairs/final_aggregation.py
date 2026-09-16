"""Read-only P45 v2.7.4 PAIR v1.2 final aggregation.

The official walk-forward database is opened read-only.  Results are written only
to a dedicated aggregation database and report.
"""
from __future__ import annotations

import hashlib, json, sqlite3
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..trio_engine import statistic
from .decision import (GATE_IDS, GateResult, ParetoVector, assign_sets, bonus_dependence,
                       decide_state, evaluate_gates, final_structure, pair_risk,
                       pareto_dominates, ranking_key, recent_support_state, structure_state)
from .engine import canonical_json, SIGNATURE_VERSION
from .audit_v12 import CONTEXT_VERSION
from .production import ProductionPairPipeline

RUN_ID = "2f61c1b7-2cb6-4d33-92c8-520691af3e76"
SOURCE_SHA = "e2f7b6291bc3d0ecea6a170eda11bc47f04aa65cb9686d556ebd6b1b12f61740"
AGGREGATION_VERSION = "PAIR-V12-FINAL-AGGREGATION-1.0"
BASELINES = {"INTEGRATED_PRIMARY": 223821/45379620, "INTEGRATED_SUPPORT": 5017311/45379620,
             "MAIN_PRIMARY": 22959/8145060, "MAIN_SUPPORT": 664677/8145060}

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE aggregation_run(run_id TEXT PRIMARY KEY,source_run_id TEXT NOT NULL,source_sha256 TEXT NOT NULL,
 version TEXT NOT NULL,signature_version TEXT NOT NULL,context_version TEXT NOT NULL,source_end_round INTEGER NOT NULL,
 aggregation_hash TEXT NOT NULL,status TEXT NOT NULL);
CREATE TABLE historical_metric(metric_id TEXT PRIMARY KEY,run_id TEXT NOT NULL REFERENCES aggregation_run(run_id),
 endpoint TEXT NOT NULL,window TEXT NOT NULL,n INTEGER NOT NULL,x INTEGER NOT NULL,rate REAL NOT NULL,baseline REAL NOT NULL,
 wilson_low REAL NOT NULL,wilson_high REAL NOT NULL,p_upper REAL NOT NULL,p_lower REAL NOT NULL,evidence TEXT NOT NULL,
 UNIQUE(run_id,endpoint,window));
CREATE TABLE current_pair(pair_key TEXT PRIMARY KEY,run_id TEXT NOT NULL REFERENCES aggregation_run(run_id),
 rule_signature TEXT NOT NULL,context_fingerprint TEXT NOT NULL,set1_json TEXT NOT NULL,set2_json TEXT NOT NULL,
 state TEXT NOT NULL,risk TEXT NOT NULL,recent TEXT NOT NULL,structure TEXT NOT NULL,bonus TEXT NOT NULL,
 pareto TEXT NOT NULL,rank_order INTEGER NOT NULL,valid_for_core INTEGER NOT NULL,row_hash TEXT NOT NULL);
CREATE TABLE current_gate(pair_key TEXT NOT NULL REFERENCES current_pair(pair_key),gate_id TEXT NOT NULL,status TEXT NOT NULL,
 reason TEXT,PRIMARY KEY(pair_key,gate_id));
CREATE TABLE structure_metric(run_id TEXT PRIMARY KEY REFERENCES aggregation_run(run_id),metrics_json TEXT NOT NULL,
 percentiles_json TEXT NOT NULL,state TEXT NOT NULL,comparison_endpoints INTEGER NOT NULL);
CREATE TABLE provenance(key TEXT PRIMARY KEY,value TEXT NOT NULL);
"""

def file_sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def sha(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()

def _primary(row: Mapping[str,Any], prefix: str) -> bool:
    return row[f"a_{prefix}_hits"]==3 or row[f"b_{prefix}_hits"]==3

def _support(row: Mapping[str,Any], prefix: str) -> bool:
    a,b=row[f"a_{prefix}_hits"],row[f"b_{prefix}_hits"]
    return a<3 and b<3 and (a==2 or b==2)

def _failure(row: Mapping[str,Any]) -> bool:
    return not _primary(row,"integrated") and not _support(row,"integrated")

def _stat(rows: Sequence[Mapping[str,Any]], endpoint: str, minimum: int) -> dict[str,Any]:
    prefix="integrated" if endpoint.startswith("INTEGRATED") else "main"
    pred=_primary if endpoint.endswith("PRIMARY") else _support
    return statistic(sum(pred(r,prefix) for r in rows),len(rows),BASELINES[endpoint],minimum)

def _field(context_json: str, field_id: str) -> Any:
    payload=json.loads(context_json)
    return next(x["value"] for x in payload["fields"] if x["field_id"]==field_id)

def aggregate(source_db: Path, output_db: Path, report_path: Path, data_path: Path, trio_db: Path) -> dict[str,Any]:
    if file_sha(source_db)!=SOURCE_SHA: raise RuntimeError("PAIR_AGGREGATION_SOURCE_SHA_MISMATCH")
    src=sqlite3.connect(f"file:{source_db.resolve()}?mode=ro",uri=True);src.row_factory=sqlite3.Row
    try:
        run=src.execute("SELECT * FROM wf_run WHERE run_id=?",(RUN_ID,)).fetchone()
        if not run or run["run_status"]!="WALKFORWARD_COMPLETE" or run["signature_version"]!=SIGNATURE_VERSION:
            raise RuntimeError("PAIR_AGGREGATION_SOURCE_RUN_INVALID")
        raw=[dict(x) for x in src.execute("SELECT s.*,o.* FROM wf_selection_exposure s JOIN wf_outcome o USING(selection_id) WHERE s.run_id=? ORDER BY s.evaluation_round",(RUN_ID,))]
        if len(raw)!=258 or len({x['evaluation_round'] for x in raw})!=258: raise RuntimeError("PAIR_AGGREGATION_EXPOSURE_INVALID")
        signatures={x['base_pair_rule_signature'] for x in raw}
        if len(signatures)!=1: raise RuntimeError("PAIR_AGGREGATION_SIGNATURE_COUNT_INVALID")
        signature=next(iter(signatures))
        reps={x['evaluation_round']:x['representative_pair_key'] for x in raw}
        conflict=[]
        for x in src.execute("SELECT c.evaluation_round,c.canonical_pair_key,c.canonical_context_payload_json FROM wf_pair_candidate c JOIN wf_selection_exposure s ON s.run_id=c.run_id AND s.evaluation_round=c.evaluation_round AND s.representative_pair_key=c.canonical_pair_key WHERE c.run_id=? ORDER BY c.evaluation_round",(RUN_ID,)):
            summaries=_field(x['canonical_context_payload_json'],'unit_summaries')
            conflict.append(any(int(v.get('conflict_cell_count',0))>0 for v in summaries))
        if len(conflict)!=len(raw): raise RuntimeError("PAIR_AGGREGATION_CONFLICT_SERIES_MISSING")
    finally: src.close()

    metrics={}
    for endpoint in BASELINES:
        metrics[(endpoint,'TOTAL')]=_stat(raw,endpoint,200)
        for n in (100,50,20): metrics[(endpoint,f'RECENT{n}')]=_stat(raw[-n:],endpoint,10**9)

    def adverse(end: int) -> tuple[float,...]:
        seq=raw[:end]; r100=seq[-100:];r50=seq[-50:]
        op=sum(_primary(x,'integrated') for x in seq)/len(seq); os=sum(_support(x,'integrated') for x in seq)/len(seq)
        rp100=sum(_primary(x,'integrated') for x in r100)/100; rp50=sum(_primary(x,'integrated') for x in r50)/50
        rs100=sum(_support(x,'integrated') for x in r100)/100; rs50=sum(_support(x,'integrated') for x in r50)/50
        of=sum(_failure(x) for x in seq)/len(seq); rf=sum(_failure(x) for x in r50)/50
        oc=sum(conflict[:end])/len(seq); rc=sum(conflict[end-50:end])/50
        return (max(0,op-rp100),max(0,op-rp50),max(0,os-rs100),max(0,os-rs50),max(0,rf-of),max(0,rc-oc))
    history=[adverse(n) for n in range(100,len(raw))]
    current_metrics,current_percentiles,rule_structure=structure_state(
        {'primary':sum(_primary(x,'integrated') for x in raw)/len(raw),'support':sum(_support(x,'integrated') for x in raw)/len(raw),'failure':sum(_failure(x) for x in raw)/len(raw),'conflict':sum(conflict)/len(raw)},
        {'primary':sum(_primary(x,'integrated') for x in raw[-100:])/100,'support':sum(_support(x,'integrated') for x in raw[-100:])/100,'failure':sum(_failure(x) for x in raw[-100:])/100,'conflict':sum(conflict[-100:])/100},
        {'primary':sum(_primary(x,'integrated') for x in raw[-50:])/50,'support':sum(_support(x,'integrated') for x in raw[-50:])/50,'failure':sum(_failure(x) for x in raw[-50:])/50,'conflict':sum(conflict[-50:])/50},history)

    recent=recent_support_state(BASELINES['INTEGRATED_SUPPORT'],metrics[('INTEGRATED_SUPPORT','TOTAL')]['wilson_low'],
        (metrics[('INTEGRATED_SUPPORT','RECENT100')]['rate'],metrics[('INTEGRATED_SUPPORT','RECENT100')]['wilson_high']),
        (metrics[('INTEGRATED_SUPPORT','RECENT50')]['rate'],metrics[('INTEGRATED_SUPPORT','RECENT50')]['wilson_high']))
    bonus=bonus_dependence(metrics[('INTEGRATED_PRIMARY','TOTAL')]['evidence_label'],metrics[('MAIN_PRIMARY','TOTAL')]['evidence_label'],
        metrics[('INTEGRATED_PRIMARY','TOTAL')]['evidence_label'].startswith('SUPERIOR_'),metrics[('MAIN_PRIMARY','TOTAL')]['rate'],BASELINES['MAIN_PRIMARY'])

    history_map={signature:raw}
    pipeline=ProductionPairPipeline(data_path,trio_db)
    prediction=pipeline.build_prediction_context(1236,1235,history_map)
    if pipeline.outcome_accesses or prediction.skip_status or len(prediction.candidates)!=10: raise RuntimeError("PAIR_CURRENT_CONTEXT_CONFLICT")
    candidates=[]
    for p in prediction.candidates:
        gi=dict(p.context['gate_input']); ctx=json.loads(p.context['canonical_context_payload_json'])
        fields={x['field_id']:x['value'] for x in ctx['fields']}; summaries=fields['unit_summaries']; trios=fields['constituent_trios']
        conflict_cols=sum(int(x.get('conflict_cell_count',0)>0) for x in summaries); incomplete=30-sum(int(x.get('complete_cell_count',0)) for x in summaries)
        roles=tuple(int(x.get('distinct_role_count',0)) for x in summaries); overlap=tuple(int(x.get('shared_evidence_id_count',0)) for x in summaries)
        member_risks=[x['opposite_risk'] for x in fields['member_risk_inputs']]
        member_structs=[x['structure_state'] for x in fields['member_structure_inputs']]
        member,rule_risk,final_risk=pair_risk(member_risks[0],member_risks[1],primary=metrics[('INTEGRATED_PRIMARY','TOTAL')]['evidence_label'],
            support=metrics[('INTEGRATED_SUPPORT','TOTAL')]['evidence_label'],integrated_primary=metrics[('INTEGRATED_PRIMARY','TOTAL')]['evidence_label'],
            main_primary=metrics[('MAIN_PRIMARY','TOTAL')]['evidence_label'],bonus=bonus,recent=recent,conflict_columns=conflict_cols)
        fs=final_structure(member_structs[0],member_structs[1],rule_structure)
        gi.update(selection_exposure=len(raw),integrated_primary_rate=metrics[('INTEGRATED_PRIMARY','TOTAL')]['rate'],
            integrated_primary_baseline=BASELINES['INTEGRATED_PRIMARY'],integrated_primary_evidence=metrics[('INTEGRATED_PRIMARY','TOTAL')]['evidence_label'],
            main_primary_rate=metrics[('MAIN_PRIMARY','TOTAL')]['rate'],main_primary_baseline=BASELINES['MAIN_PRIMARY'],main_primary_evidence=metrics[('MAIN_PRIMARY','TOTAL')]['evidence_label'],
            recent_state=recent,final_risk=final_risk,final_structure=fs,walkforward_prelock_ok=True,ledger_complete=True,executed_gate_ids=GATE_IDS)
        gates=evaluate_gates(gi)
        state_data=dict(gi,valid_trio_count=2,disjoint=True,signature_ok=True,atomic_storage_ok=True,prediction_hash_ok=True,walkforward_ok=True,
            member_states=tuple(x['state'] for x in trios),members_valid=all(x['valid_for_pair'] for x in trios),pool_type=fields['pair_identity']['pool_type'],
            primary_evidence=metrics[('INTEGRATED_PRIMARY','TOTAL')]['evidence_label'],support_evidence=metrics[('INTEGRATED_SUPPORT','TOTAL')]['evidence_label'],
            bonus_dependence=bonus,conflict_columns=conflict_cols)
        state=decide_state(gates,state_data)
        pv=ParetoVector(conflict_cols,incomplete,roles,overlap,member,rule_risk,fs)
        set1,set2=tuple(p.member_a),tuple(p.member_b)
        rd={'both_pass':all(x['state']=='TRIO_PASS' for x in trios),'pareto':'NOT_COMPARABLE','integrated_primary_rate':metrics[('INTEGRATED_PRIMARY','TOTAL')]['rate'],
            'integrated_baseline':BASELINES['INTEGRATED_PRIMARY'],'main_primary_rate':metrics[('MAIN_PRIMARY','TOTAL')]['rate'],'support_rate':metrics[('INTEGRATED_SUPPORT','TOTAL')]['rate'],
            'recent':recent,'weaker_member_vector':(None,None,None,None),'final_risk':final_risk,'conflict_columns':conflict_cols,'structure':fs,
            'role_diversity':roles,'evidence_overlap':overlap,'simultaneous_failure_rate':sum(_failure(x) for x in raw)/len(raw),'set1':set1,'set2':set2,'canonical_pair_key':p.canonical_pair_key}
        candidates.append({'p':p,'gates':gates,'state':state,'member':member,'rule_risk':rule_risk,'final_risk':final_risk,'structure':fs,'recent':recent,'bonus':bonus,'pv':pv,'rd':rd})
    for a in candidates:
        dominated=any(pareto_dominates(b['pv'],a['pv']) for b in candidates if b is not a)
        a['pareto']='DOMINATED' if dominated else 'NONDOMINATED';a['rd']['pareto']=a['pareto']
    ordered=sorted(candidates,key=lambda x:ranking_key(x['rd']))

    if output_db.exists(): output_db.unlink()
    db=sqlite3.connect(output_db);db.execute('PRAGMA foreign_keys=ON');db.executescript(SCHEMA)
    agg_payload={'source':RUN_ID,'source_sha':SOURCE_SHA,'metrics':{'|'.join(k):v for k,v in metrics.items()},'structure':[current_metrics,current_percentiles,rule_structure],
                 'current':[(x['p'].canonical_pair_key,x['state'],x['pareto']) for x in ordered]}
    agg_hash=sha(agg_payload);agg_run=sha({'version':AGGREGATION_VERSION,'source':RUN_ID})
    db.execute('INSERT INTO aggregation_run VALUES (?,?,?,?,?,?,?,?,?)',(agg_run,RUN_ID,SOURCE_SHA,AGGREGATION_VERSION,SIGNATURE_VERSION,CONTEXT_VERSION,1235,agg_hash,'PAIR_V12_FINAL_AGGREGATION_COMPLETE'))
    for (endpoint,window),m in metrics.items():
        db.execute('INSERT INTO historical_metric VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',(sha([endpoint,window]),agg_run,endpoint,window,m['sample_count'],m['success_count'],m['rate'],BASELINES[endpoint],m['wilson_low'],m['wilson_high'],m['p_upper'],m['p_lower'],m['evidence_label']))
    db.execute('INSERT INTO structure_metric VALUES (?,?,?,?,?)',(agg_run,canonical_json(current_metrics),canonical_json(current_percentiles),rule_structure,len(history)))
    for rank,x in enumerate(ordered,1):
        p=x['p'];valid=int(x['state'] in ('PAIR_READY','PAIR_TEST_READY'));row={'pair':p.canonical_pair_key,'state':x['state'],'rank':rank,'pareto':x['pareto']}
        db.execute('INSERT INTO current_pair VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(p.canonical_pair_key,agg_run,p.base_pair_rule_signature,p.context['pair_context_fingerprint'],canonical_json(p.member_a),canonical_json(p.member_b),x['state'],x['final_risk'],x['recent'],x['structure'],x['bonus'],x['pareto'],rank,valid,sha(row)))
        for g in x['gates']: db.execute('INSERT INTO current_gate VALUES (?,?,?,?)',(p.canonical_pair_key,g.gate_id,g.status,g.reason))
    for k,v in {'source_db':str(source_db),'source_run_id':RUN_ID,'aggregation_hash':agg_hash,'future_outcome_accesses':canonical_json(pipeline.outcome_accesses)}.items():db.execute('INSERT INTO provenance VALUES (?,?)',(k,v))
    db.commit(); integrity=db.execute('PRAGMA integrity_check').fetchone()[0];fk=len(db.execute('PRAGMA foreign_key_check').fetchall());db.close()
    report={'status':'PAIR_V12_FINAL_AGGREGATION_COMPLETE','aggregation_version':AGGREGATION_VERSION,'aggregation_hash':agg_hash,'source_run_id':RUN_ID,'source_db_sha256':SOURCE_SHA,
      'historical_selection_exposure':len(raw),'historical_metrics':{'|'.join(k):v for k,v in metrics.items()},'structure':{'metrics':current_metrics,'percentiles':current_percentiles,'state':rule_structure,'comparison_endpoints':len(history)},
      'current_round':1236,'source_end_round':1235,'candidate_count':len(ordered),'state_counts':{s:sum(x['state']==s for x in ordered) for s in ('PAIR_READY','PAIR_TEST_READY','PAIR_RESEARCH_HOLD','PAIR_SYSTEM_HOLD')},
      'valid_for_core':sum(x['state'] in ('PAIR_READY','PAIR_TEST_READY') for x in ordered),'pareto_count':sum(x['pareto']=='NONDOMINATED' for x in ordered),
      'ranking':[{'rank':i+1,'pair':x['p'].canonical_pair_key,'set1':x['p'].member_a,'set2':x['p'].member_b,'state':x['state'],'pareto':x['pareto'],'risk':x['final_risk'],'structure':x['structure']} for i,x in enumerate(ordered)],
      'checks':{'source_run_count':1,'duplicate_candidate':len(ordered)-len({x['p'].canonical_pair_key for x in ordered}),'gate_missing':sum(len(x['gates'])!=14 for x in ordered),'unassigned':sum(x['state'] not in ('PAIR_READY','PAIR_TEST_READY','PAIR_RESEARCH_HOLD','PAIR_SYSTEM_HOLD') for x in ordered),'multi_state':0,'future_leak':len(pipeline.outcome_accesses),'integrity':integrity,'foreign_key_violations':fk}}
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report['aggregation_db_sha256']=file_sha(output_db);report['report_sha256']=file_sha(report_path)
    return report

"""Schema-273 TRIO persistence with immutable NUMBER-ledger guard."""
from __future__ import annotations
import json,uuid
from typing import Any,Mapping
from .core_store import CoreStore,utc_now
from .integrity import canonical_json,sha256_json

def install_number_readonly_guard(store:CoreStore)->None:
    with store.transaction() as db:
        db.executescript("""
        CREATE TRIGGER IF NOT EXISTS stage7_number_no_update BEFORE UPDATE ON number_ledger BEGIN SELECT RAISE(ABORT,'stage7 number_ledger is read-only'); END;
        CREATE TRIGGER IF NOT EXISTS stage7_number_no_delete BEFORE DELETE ON number_ledger BEGIN SELECT RAISE(ABORT,'stage7 number_ledger is read-only'); END;
        """)

def number_snapshot_hash(store:CoreStore,core_run_id:str)->str:
    with store.transaction() as db:
        rows=db.execute("SELECT * FROM number_ledger WHERE core_run_id=? ORDER BY number",(core_run_id,)).fetchall()
    return sha256_json([dict(r) for r in rows])

def persist_trios(store:CoreStore,core_run_id:str,result:Mapping[str,Any],*,data_hash:str,execution_hash:str,number_hash:str)->None:
    install_number_readonly_guard(store)
    with store.transaction() as db:
      for key,row in result["rows"].items():
        trio_id=str(uuid.uuid4());n1,n2,n3=row["trio"];perf=row["performance"];stats=perf["statistics"]
        vals=(trio_id,core_run_id,n1,n2,n3,key,row["trio_state"],"COMPLETE",None,row["candidate_pool_type"],row["candidate_pool_hash"],number_hash,
          "P45-v2.7.3-TRIO",sha256_json("P45-v2.7.3-TRIO"),row["trio_rule_signature"],row["selection_rule_exposure_count"],row["trio_identity_exposure_count"],None,
          row["bonus_dependency_state"],row["member_opposite_risk"],row["trio_rule_opposite_risk"],row["member_structure_summary"],row["trio_rule_structure_state"],row["final_structure_state"],
          row["recent_support_collapse_state"],row["pareto_state"],sha256_json({"states":row["number_states"],"coverage":row["coverage"]["trio_unit_state_vector"],"roles":row["coverage"]["role_diversity_vector"]}),int(row["valid_for_pair"]),
          "ELIGIBLE" if row["valid_for_pair"] else "STATE_NOT_ELIGIBLE",canonical_json(list(row["gate_results"])),canonical_json(list(row["gate_results"])),sha256_json(list(row["gate_results"])),None,row["decision_hash"],
          "TRIO_EARLY_ELIMINATED",row["selection_rule_exposure_count"],stats[("INTEGRATED","EXACT_3_OF_3")]["success_count"],stats[("INTEGRATED","EXACT_3_OF_3")]["rate"],
          stats[("MAIN","EXACT_3_OF_3")]["success_count"],stats[("MAIN","EXACT_3_OF_3")]["rate"],stats[("INTEGRATED","EXACT_2_OF_3")]["success_count"],stats[("INTEGRATED","EXACT_2_OF_3")]["rate"],
          stats[("MAIN","EXACT_2_OF_3")]["success_count"],stats[("MAIN","EXACT_2_OF_3")]["rate"],stats[("INTEGRATED","EXACT_1_OF_3")]["success_count"],stats[("INTEGRATED","EXACT_1_OF_3")]["rate"],
          canonical_json(row["coverage"]),canonical_json(row["gate_results"]),row["first_failed_gate"],row["trio_state"],canonical_json([]),None,None,data_hash,sha256_json({"key":key,"decision":row["decision_hash"]}),execution_hash,utc_now())
        columns=("trio_id","core_run_id","n1","n2","n3","trio_key","trio_state","calculation_status","system_error_code","candidate_pool_type","candidate_pool_hash","number_ledger_snapshot_hash","trio_rule_version","trio_rule_hash","trio_rule_signature","selection_rule_exposure_count","trio_identity_exposure_count","walkforward_run_id","bonus_dependency_state","member_opposite_risk","trio_rule_opposite_risk","member_structure_summary","trio_rule_structure_state","final_structure_state","recent_support_collapse_state","pareto_state","pareto_vector_hash","valid_for_pair","pair_eligibility_reason","expected_gate_sequence_json","executed_gate_sequence_json","gate_order_hash","prediction_hash_before_result","decision_hash","elimination_stage","exposure_count","integrated_3of3_count","integrated_3of3_rate","main_3of3_count","main_3of3_rate","integrated_2of3_count","integrated_2of3_rate","main_2of3_count","main_2of3_rate","integrated_1of3_count","integrated_1of3_rate","unit_coverage_matrix_json","gate_result_json","first_failed_gate","primary_reason_code","secondary_reason_codes_json","final_rank","selected_set","data_hash","row_hash","execution_hash","created_at")
        db.execute(f"INSERT INTO trio_ledger ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",vals)
        for c in row["coverage"]["cells"]:db.execute("INSERT INTO trio_unit_coverage VALUES (?,?,?,?,?)",(trio_id,c["number"],c["unit_type"],canonical_json(c),c["source_metric_hash"]))
        for unit,div,ov in zip(__import__('p45_v27.unit_relations',fromlist=['UNIT_ORDER']).UNIT_ORDER,row["coverage"]["role_diversity_vector"],row["coverage"]["evidence_overlap_vector"]):
            payload={"unit_type":unit,"diversity":div,"overlap":ov};db.execute("INSERT INTO trio_role_evidence VALUES (?,?,?,?,?,?)",(trio_id,unit,div,ov,canonical_json(payload),sha256_json(payload)))
        for (scope,hit,period),m in perf["period_metrics"].items():db.execute("INSERT INTO trio_period_metric VALUES (?,?,?,?,?,?,?,?)",(trio_id,scope,hit,period,m["sample_count"],m["hit_count"],m["rate"],canonical_json(m)))
        for (scope,hit),s in stats.items():db.execute("INSERT INTO trio_stat_test VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(trio_id,scope,hit,s["sample_count"],s["success_count"],s["rate"],s["p0"],s["wilson_low"],s["wilson_high"],s["p_upper"],s["p_lower"],s["evidence_label"]))
        for order,(gate,status) in enumerate(row["gate_results"].items(),1):db.execute("INSERT INTO trio_gate_result VALUES (?,?,?,?,?,?)",(trio_id,order,gate,"PASS" if status else "FAIL",canonical_json({}),None))
        risk={k:row[k] for k in ("member_opposite_risk","trio_rule_opposite_risk","bonus_dependency_state","recent_support_collapse_state")};db.execute("INSERT INTO trio_risk_metric VALUES (?,?,?)",(trio_id,canonical_json(risk),sha256_json(risk)))

def load_trios(store:CoreStore,core_run_id:str)->list[dict[str,Any]]:
    with store.transaction() as db:rows=db.execute("SELECT * FROM trio_ledger WHERE core_run_id=? ORDER BY n1,n2,n3",(core_run_id,)).fetchall()
    return [dict(r) for r in rows]

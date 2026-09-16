"""Schema-272 persistence for all 45 stage-6 number ledger rows."""

from __future__ import annotations

import json
from typing import Any,Mapping

from .core_store import CoreStore,utc_now
from .integrity import canonical_json,sha256_json


def persist_number_ledger(store:CoreStore,core_run_id:str,result:Mapping[str,Any],data_hash:str,execution_hash:str)->None:
    columns=("core_run_id","number","candidate_role","number_state","elimination_stage","unit_state_vector_json",
      "unit_relation_state","first_failed_gate","primary_reason_code","secondary_reason_codes_json","gate_input_values_json",
      "gate_output_values_json","expected_gate_sequence_json","executed_gate_sequence_json","status_after_each_gate_json",
      "tie_break_key_json","rank_before_tie_break","rank_after_tie_break","candidate_pool_type","return_roles_json",
      "primary_return_role","nonreturn_role","role_signature_json","role_overlap_json","number_performance_context_json",
      "secondary_contexts_json","number_bonus_dependence","number_opposite_risk","number_structure_state",
      "structure_insufficient_sample","number_context_conflict","valid_test_status","retired_reason","first_limited_gate",
      "decision_hash","final_rank","selected_pool","data_hash","row_hash","execution_hash","created_at")
    with store.transaction() as db:
        for n in range(1,46):
            row=result["rows"][n]
            role="RETURN_CANDIDATE" if row["official_return_candidate"] else "NONRETURN_CANDIDATE" if row["nonreturn_role"] else "NOT_ELIGIBLE"
            primary_reason=row["first_limited_gate"] or "ALL_NUMBER_PASS_GATES"
            gate_inputs={"primary_number_context":row["primary_number_context"],"relation_state":row["relation_state"],
                         "pareto_state":row["pareto_state"],"number_bonus_dependence":row["number_bonus_dependence"],
                         "number_opposite_risk":row["number_opposite_risk"],"number_structure_state":row["number_structure_state"]}
            values=(core_run_id,n,role,row["number_state"],row["elimination_stage"],canonical_json(row["unit_state_vector"]),
              row["relation_state"],row["first_failed_gate"],primary_reason,canonical_json([row["first_limited_gate"]] if row["first_limited_gate"] else []),
              canonical_json(gate_inputs),canonical_json(row["gate_results"]),canonical_json(row["expected_gate_sequence"]),
              canonical_json(row["executed_gate_sequence"]),canonical_json(row["gate_results"]),canonical_json(row["tie_break_key"]),
              row["rank_before_tie_break"],row["rank_after_tie_break"],row["candidate_pool_type"],canonical_json(row["return_roles"]),
              canonical_json(row["primary_return_role"]),row["nonreturn_role"],canonical_json(row["role_signature"]),
              canonical_json(row["overlap_profile"]),canonical_json(row["primary_number_context"]),
              canonical_json(row["secondary_number_contexts"]),row["number_bonus_dependence"],row["number_opposite_risk"],
              row["number_structure_state"],int(row["structure_insufficient_sample"]),row["number_context_conflict"],
              int(row["valid_test_status"]),row["retired_reason"],row["first_limited_gate"],row["decision_hash"],
              row["rank_after_tie_break"],int(row["selected_pool"]),data_hash,row["row_hash"],execution_hash,utc_now())
            db.execute(f"INSERT INTO number_ledger ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",values)


def load_number_ledger(store:CoreStore,core_run_id:str)->list[dict[str,Any]]:
    with store.transaction() as db:rows=db.execute("SELECT * FROM number_ledger WHERE core_run_id=? ORDER BY number",(core_run_id,)).fetchall()
    return [dict(row) for row in rows]

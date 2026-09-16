"""Schema-271 persistence for v2.7.1 stage-5.5 decisions."""

from __future__ import annotations

import json
from typing import Any, Mapping

from .core_store import CoreStore
from .integrity import canonical_json


def update_unit_decisions(store: CoreStore, core_run_id: str, unit_type: str,
                          decisions: Mapping[int, Mapping[str, Any]]) -> None:
    with store.transaction() as db:
        for number, decision in decisions.items():
            cursor = db.execute(
                """UPDATE unit_number_metric SET
                   overall_metrics_json=?, recent_100_metrics_json=?, recent_50_metrics_json=?, recent_20_metrics_json=?,
                   exact_vector_metrics_json=?, local_state_metrics_json=?, sample_state=?, risk_state=?, unit_state=?,
                   primary_context=?, secondary_context=?, context_relation=?, bonus_dependence=?, opposite_risk=?,
                   structure_state=?, first_limiting_gate=?, reason_codes_json=?, decision_json=?, decision_hash=?
                   WHERE core_run_id=? AND number=? AND unit_definition_id IN
                   (SELECT unit_definition_id FROM unit_definition WHERE unit_type=?)""",
                (canonical_json(decision["contexts"].get(decision["primary_context"].replace("_BORDERLINE", ""), {})),
                 canonical_json(decision["contexts"].get(decision["primary_context"].replace("_BORDERLINE", ""), {}).get("recent100", {})),
                 canonical_json(decision["contexts"].get(decision["primary_context"].replace("_BORDERLINE", ""), {}).get("recent50", {})),
                 canonical_json(decision["contexts"].get(decision["primary_context"].replace("_BORDERLINE", ""), {}).get("recent20", {})),
                 canonical_json(decision["contexts"]["EXACT_VECTOR_CONTEXT"]),
                 canonical_json(decision["contexts"]["LOCAL_GROUP_CONTEXT"]),
                 decision["contexts"].get(decision["primary_context"].replace("_BORDERLINE", ""), {}).get("sample_state", "INSUFFICIENT"),
                 decision["opposite_risk"], decision["unit_state"], decision["primary_context"],
                 decision["secondary_context"], decision["context_relation"], decision["bonus_dependence"],
                 decision["opposite_risk"], decision["structure_state"], decision["first_limiting_gate"],
                 canonical_json(decision["reason_codes"]), canonical_json(decision), decision["decision_hash"],
                 core_run_id, number, unit_type),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"missing stage-4 number row: {unit_type}/{number}")


def load_unit_decisions(store: CoreStore, core_run_id: str) -> dict[str, dict[int, dict[str, Any]]]:
    with store.transaction() as db:
        rows = db.execute("""SELECT d.unit_type,m.number,m.unit_state,m.decision_json,m.decision_hash
            FROM unit_number_metric m JOIN unit_definition d ON d.unit_definition_id=m.unit_definition_id
            WHERE m.core_run_id=? ORDER BY d.display_order,m.number""", (core_run_id,)).fetchall()
    result: dict[str, dict[int, dict[str, Any]]] = {}
    for row in rows:
        decision = json.loads(row["decision_json"])
        decision["unit_state"] = row["unit_state"]
        decision["decision_hash"] = row["decision_hash"]
        result.setdefault(row["unit_type"], {})[row["number"]] = decision
    return result

"""Persistence for schema-271 structure-collapse ledgers."""

from __future__ import annotations

import json, uuid
from typing import Any, Mapping

from .core_store import CoreStore, utc_now
from .integrity import canonical_json


def persist_structure_ledger(store: CoreStore, core_run_id: str, ledger: Mapping[str, Any]) -> None:
    with store.transaction() as db:
        definition = db.execute("""SELECT d.unit_definition_id FROM unit_definition d
            JOIN core_run r ON r.engine_version_id=d.engine_version_id
            WHERE r.core_run_id=? AND d.unit_type=?""",(core_run_id,ledger["unit_type"])).fetchone()
        if definition is None: raise ValueError("unit definition missing")
        identity=str(uuid.uuid5(uuid.NAMESPACE_URL,f"p45-v271:structure:{core_run_id}:{ledger['unit_type']}"))
        db.execute("""INSERT INTO unit_structure_ledger VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (identity,core_run_id,definition[0],ledger["analysis_round"],ledger["reference_start_round"],
             ledger["reference_end_round"],ledger["sample_count"],canonical_json(ledger["metric_names"]),
             canonical_json(ledger["current_metrics"]),canonical_json(ledger["historical_distribution"]),
             canonical_json(ledger["metric_percentiles"]),ledger["overall_percentile"],ledger["structure_state"],
             ledger["decision_reason"],ledger["data_hash"],ledger["calculation_hash"],utc_now()))


def load_structure_ledger(store: CoreStore, core_run_id: str, unit_type: str) -> dict[str, Any] | None:
    with store.transaction() as db:
        row=db.execute("""SELECT s.* FROM unit_structure_ledger s JOIN unit_definition d
            ON d.unit_definition_id=s.unit_definition_id WHERE s.core_run_id=? AND d.unit_type=?""",
            (core_run_id,unit_type)).fetchone()
    if row is None:return None
    result=dict(row)
    for key in ("metric_names_json","current_metrics_json","historical_distribution_json","metric_percentiles_json"):
        result[key]=json.loads(result[key])
    return result

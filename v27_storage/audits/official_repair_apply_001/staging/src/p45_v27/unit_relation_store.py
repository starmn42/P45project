"""Persistence for stage-5 relationship records only."""

from __future__ import annotations

import uuid
from typing import Any, Mapping

from .core_store import CoreStore, utc_now
from .integrity import canonical_json, sha256_json


def _id(core_run_id: str, entity_type: str, entity_key: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"p45-v27:relation:{core_run_id}:{entity_type}:{entity_key}"))


def persist_relation(store: CoreStore, core_run_id: str, relation: Mapping[str, Any],
                     pareto_result: str, execution_hash: str) -> None:
    db_pareto = {"UNIT_PARETO_DOMINATE": "NON_DOMINATED",
                 "UNIT_PARETO_NONDOMINATED": "NON_DOMINATED",
                 "UNIT_PARETO_DOMINATED": "DOMINATED",
                 "UNIT_PARETO_NOT_COMPARABLE": "NOT_COMPARABLE"}[pareto_result]
    evidence = relation["evidence"]
    with store.transaction() as db:
        db.execute(
            """INSERT INTO unit_relation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (_id(core_run_id, relation["entity_type"], relation["entity_key"]), core_run_id,
             relation["entity_type"], relation["entity_key"], canonical_json(relation["unit_state_vector"]),
             canonical_json(relation["support_units"]), canonical_json(relation["weaken_units"]),
             canonical_json(relation["test_units"]), canonical_json(relation["hold_units"]),
             canonical_json(relation["fail_units"]), canonical_json(evidence["RELATED_UNIT_SUPPORT"]),
             canonical_json(evidence["INDEPENDENT_CONTEXT_SUPPORT"]), canonical_json(evidence["UNIT_CONFLICT"]),
             relation["relation_state"], db_pareto, relation["relation_hash"], execution_hash, utc_now()),
        )


def load_relation(store: CoreStore, core_run_id: str, entity_type: str, entity_key: str) -> dict[str, Any] | None:
    with store.transaction() as db:
        row = db.execute("SELECT * FROM unit_relation WHERE core_run_id=? AND entity_type=? AND entity_key=?",
                         (core_run_id, entity_type, entity_key)).fetchone()
        return dict(row) if row else None

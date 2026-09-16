"""Pre-result EXP-002 fallback ordering skeleton; no historical outcomes are read."""
from __future__ import annotations

from typing import Any, Mapping, Sequence
from p45_v27.number_engine import _tie_key
from p45_v27.integrity import sha256_json

ALLOWED_STATES = frozenset(("NUMBER_PASS", "NUMBER_WEAKEN", "NUMBER_TEST", "NUMBER_HOLD"))
PROTOCOL_ID = "EXP002-FALLBACK-ORDER-1.0"
POOL_TYPE = "EXP002_FALLBACK_POOL_V1"

def source_pool(rows: Mapping[int, Mapping[str, Any]], maximum: int = 12) -> list[Mapping[str, Any]]:
    """Reuse the official deterministic NUMBER tie ordering without scores or weights."""
    eligible = [row for row in rows.values()
                if row["number_state"] in ALLOWED_STATES
                and len(row.get("unit_state_vector", ())) == 5
                and row.get("number_opposite_risk") != "HIGH"
                and row.get("number_structure_state") != "SEVERE"]
    return sorted(eligible, key=_tie_key)[:maximum]

def select_disjoint_trios(ranked_trios: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    """Take the first official-ranked trio and the first later disjoint trio."""
    for index, first in enumerate(ranked_trios):
        a = tuple(first["trio"])
        for second in ranked_trios[index + 1:]:
            b = tuple(second["trio"])
            if set(a).isdisjoint(b):
                payload = {"protocol": PROTOCOL_ID, "trio_a": list(a), "trio_b": list(b)}
                return {**payload, "selection_hash": sha256_json(payload)}
    return None

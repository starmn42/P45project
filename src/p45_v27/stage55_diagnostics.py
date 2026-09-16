"""Read-only stage-5.5 diagnostics; never creates candidate or official results."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from .unit_relations import build_number_relations
from .unit_states import evaluate_all_units
from .structure_collapse import calculate_structure_ledger
from .units import DEFINITIONS, Draw


def load_draw_csv(path: Path) -> list[Draw]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        return [Draw(int(r["round"]), tuple(int(r[f"n{i}"]) for i in range(1, 7)), int(r["bonus"])) for r in rows]


def diagnose(path: Path, analysis_round: int, *, connect_structure: bool = True) -> dict[str, Any]:
    draws = load_draw_csv(path)
    ledgers = {unit: calculate_structure_ledger(definition, draws, analysis_round)
               for unit, definition in DEFINITIONS.items()} if connect_structure else {}
    decisions = evaluate_all_units(DEFINITIONS, draws, analysis_round,
                                   {unit: row["structure_state"] for unit, row in ledgers.items()})
    relations = build_number_relations(decisions)
    state_counts = Counter(d["unit_state"] for unit in decisions.values() for d in unit.values())
    relation_counts = Counter(r["relation_state"] for r in relations.values())
    vectors = {n: relations[n]["unit_state_vector"] for n in range(1, 46)}
    no_support_all = all(r["relation_state"] == "UNIT_NO_SUPPORT" for r in relations.values())
    reason_counts = Counter(reason for unit in decisions.values() for d in unit.values() for reason in d["reason_codes"])
    return {"analysis_round": analysis_round, "source_rounds": [draws[0].round, draws[-1].round],
            "state_counts": dict(state_counts), "relation_counts": dict(relation_counts),
            "all_no_support": no_support_all, "vectors": vectors, "reason_counts": dict(reason_counts),
            "structure_ledgers": ledgers, "decisions": decisions, "relations": relations}

"""Thin production adapter from the official UNIT/NUMBER/TRIO engines to PAIR walk-forward."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..integrity import sha256_json
from ..stage55_diagnostics import load_draw_csv
from ..stage6_diagnostics import diagnose_stage6
from ..trio_engine import build_current_trios
from ..trio_final import RUN_ID as TRIO_WALKFORWARD_RUN_ID
from ..units import DEFINITIONS
from .decision import RISK_ORDER, final_structure, pair_unit_coverage, ranking_key
from .engine import SIGNATURE_VERSION, generate_pair_candidates
from .audit_v12 import rule_signature
from .lifecycle_v12 import build_official_prediction_audit
from .models import PairSignatureContext, TrioInput
from .walkforward import PairPrediction, RoundPrediction

UNIT_ORDER = ("UNIT_3", "UNIT_5", "UNIT_9", "UNIT_10", "END_DIGIT")

def _finite_rank(value: Any) -> Any:
    """Make the official NULL-last rank serializable without changing its ordering."""
    if isinstance(value, float) and math.isinf(value): return 1.0e308 if value > 0 else -1.0e308
    if isinstance(value, tuple): return tuple(_finite_rank(item) for item in value)
    return value


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _matrix(result: Mapping[str, Any]) -> tuple[tuple[tuple[dict[str, Any], ...], ...], ...]:
    lookup = {(cell["number"], cell["unit_type"]): cell for cell in result["coverage"]["cells"]}
    members = []
    for number in result["trio"]:
        cells = []
        for unit in UNIT_ORDER:
            raw = lookup[(number, unit)]
            evidence = tuple(raw.get("raw_evidence_ids", ())) + tuple(raw.get("related_evidence_ids", ())) + tuple(raw.get("independent_evidence_ids", ()))
            state = raw["unit_state"]
            cells.append({"calculation_status": "COMPLETE", "support": state in ("UNIT_PASS", "UNIT_WEAKEN"),
                          "conflict": state == "UNIT_FAIL" or raw.get("opposite_risk") == "HIGH",
                          "role": raw.get("role_type"), "evidence_ids": evidence, "source": raw})
        members.append(tuple(cells))
    return tuple(members)


class ProductionPairPipeline:
    """Read-only adapter. Prediction and outcome access are deliberately separate methods."""

    def __init__(self, data_path: Path, trio_walkforward_db: Path) -> None:
        self.data_path = Path(data_path)
        self.trio_walkforward_db = Path(trio_walkforward_db)
        self._draws = {draw.round: draw for draw in load_draw_csv(self.data_path)}
        self.outcome_accesses: list[int] = []

    def source_hash(self) -> str:
        return sha256_json({"draws": _file_sha(self.data_path), "trio_walkforward": _file_sha(self.trio_walkforward_db)})

    def _trio_history(self, evaluation_round: int) -> dict[str, list[dict[str, Any]]]:
        db = sqlite3.connect(f"file:{self.trio_walkforward_db}?mode=ro", uri=True); db.row_factory = sqlite3.Row
        try:
            rows = db.execute("SELECT * FROM wf_exposure WHERE run_id=? AND evaluation_round<? ORDER BY evaluation_round,trio_rule_signature",
                              (TRIO_WALKFORWARD_RUN_ID, evaluation_round)).fetchall()
        finally:
            db.close()
        history: dict[str, list[dict[str, Any]]] = {}
        for item in rows:
            row = dict(item); row["outer_round"] = row["evaluation_round"]
            row["trio"] = tuple(map(int, row["representative_trio_key"].split("-")))
            history.setdefault(row["trio_rule_signature"], []).append(row)
        return history

    def build_prediction_context(self, evaluation_round: int, source_end_round: int,
                                 history: Mapping[str, Sequence[Mapping[str, Any]]]) -> RoundPrediction:
        if source_end_round != evaluation_round - 1:
            raise RuntimeError("PAIR_FUTURE_LEAKAGE")
        stage6 = diagnose_stage6(self.data_path, evaluation_round)
        if stage6["source_rounds"][1] != source_end_round:
            raise RuntimeError("PAIR_SOURCE_BOUNDARY_MISMATCH")
        prefix_base = sha256_json({"data": _file_sha(self.data_path), "end": source_end_round,
                                   "number": stage6["execution_hash"]})
        if len(stage6["candidate_numbers"]) < 6:
            return RoundPrediction(source_end_round, prefix_base, (), "SKIPPED_RESEARCH_HOLD")
        trios_result = build_current_trios(stage6, DEFINITIONS, self._trio_history(evaluation_round))
        valid_rows = [row for row in trios_result["rows"].values() if row["valid_for_pair"]]
        prefix = sha256_json({"base": prefix_base, "trio": trios_result["execution_hash"]})
        if len(valid_rows) < 2:
            return RoundPrediction(source_end_round, prefix, (), "SKIPPED_TRIO_UNDER_2")
        details = {"-".join(map(str, row["trio"])): row for row in valid_rows}
        trio_inputs = [TrioInput(key, tuple(row["trio"]), row["trio_state"], row["trio_rule_signature"], True)
                       for key, row in sorted(details.items())]
        matrices = {key: _matrix(row) for key, row in details.items()}

        def signature_context(a: TrioInput, b: TrioInput) -> PairSignatureContext:
            coverage = pair_unit_coverage((matrices[a.trio_key], matrices[b.trio_key]))
            ar, br = details[a.trio_key], details[b.trio_key]
            risk = max((ar["member_opposite_risk"], br["member_opposite_risk"]), key=RISK_ORDER.__getitem__)
            structure = final_structure(ar["final_structure_state"], br["final_structure_state"], "INSUFFICIENT_SAMPLE")
            relation = tuple("/".join(cell["source"]["unit_state"] for cell in unit["raw_cells"]) for unit in coverage)
            return PairSignatureContext(stage6["candidate_pool_type"], relation,
                tuple(unit["distinct_role_count"] for unit in coverage),
                tuple(unit["shared_evidence_id_count"] for unit in coverage), risk, structure)

        candidates = generate_pair_candidates(trio_inputs, signature_context)
        if not candidates:
            return RoundPrediction(source_end_round, prefix, (), "SKIPPED_NO_DISJOINT_PAIR")
        predictions = []
        for candidate in candidates:
            pair_context = signature_context(candidate.lower_member, candidate.upper_member)
            past = list(history.get(candidate.pair_rule_signature, ()))
            n = len(past)
            integrated = sum(x["integrated_category"] in ("DOUBLE_TRIPLE_SUCCESS", "SINGLE_TRIPLE_SUCCESS") for x in past) / n if n else None
            main = sum(x["main_category"] in ("DOUBLE_TRIPLE_SUCCESS", "SINGLE_TRIPLE_SUCCESS") for x in past) / n if n else None
            support = sum("EXACT2" in x["integrated_category"] for x in past) / n if n else None
            context = {"signature_version": SIGNATURE_VERSION, "source_end_round": source_end_round,
                       "selection_exposure": n, "trio_a": candidate.lower_member.trio_key,
                       "trio_b": candidate.upper_member.trio_key, "pair_pool_type": stage6["candidate_pool_type"],
                       "integrated_primary_rate": integrated, "main_primary_rate": main, "support_rate": support}
            rank_data = {"both_pass": all(x.trio_state == "TRIO_PASS" for x in (candidate.lower_member, candidate.upper_member)),
                         "pareto": "NOT_COMPARABLE", "integrated_primary_rate": integrated, "integrated_baseline": 0.004932192028051359,
                         "main_primary_rate": main, "support_rate": support, "recent": "INSUFFICIENT",
                         "weaker_member_vector": (0,), "final_risk": pair_context.member_maximum_risk,
                         "conflict_columns": 0, "structure": pair_context.member_structure_summary,
                         "role_diversity": pair_context.role_diversity_vector,
                         "evidence_overlap": pair_context.evidence_overlap_vector,
                         "simultaneous_failure_rate": None, "set1": candidate.lower_member.numbers, "set2": candidate.upper_member.numbers,
                         "canonical_pair_key": candidate.canonical_pair_key}
            rank = _finite_rank(ranking_key(rank_data))
            signature, rule_json, _ = rule_signature(stage6["candidate_pool_type"])
            coverage = pair_unit_coverage((matrices[candidate.lower_member.trio_key], matrices[candidate.upper_member.trio_key]))
            cells=[]
            for unit in coverage:
                for cell_index, cell in enumerate(unit["raw_cells"]):
                    cells.append({"member_index":cell_index//3,"number_index":cell_index%3,"unit_id":unit["unit_type"],
                        "unit_state":cell["source"]["unit_state"],"support_relation":cell["source"].get("relation_state","UNIT_NO_SUPPORT"),
                        "role":cell.get("role") or "NON_RETURN","evidence_ids":sorted(set(cell.get("evidence_ids",()))),
                        "conflict":bool(cell.get("conflict")),"complete":cell.get("calculation_status")=="COMPLETE"})
            summaries=[{"unit_id":x["unit_type"],"complete_cell_count":x["complete_cell_count"],"support_cell_count":x["support_cell_count"],
                "conflict_cell_count":x["conflict_cell_count"],"distinct_role_count":x["distinct_role_count"],"shared_evidence_id_count":x["shared_evidence_id_count"]} for x in coverage]
            members=[]
            for member in (candidate.lower_member,candidate.upper_member):
                members.append({"canonical_trio_key":member.trio_key,"numbers":list(member.numbers),"state":member.trio_state,
                    "trio_rule_signature":member.trio_rule_signature,"valid_for_pair":member.valid_for_pair})
            ar,br=details[candidate.lower_member.trio_key],details[candidate.upper_member.trio_key]
            risks=[{"canonical_trio_key":candidate.lower_member.trio_key,"opposite_risk":ar["member_opposite_risk"]},
                   {"canonical_trio_key":candidate.upper_member.trio_key,"opposite_risk":br["member_opposite_risk"]}]
            structures=[{"canonical_trio_key":candidate.lower_member.trio_key,"structure_state":ar["final_structure_state"],"insufficient_sample":ar["final_structure_state"]=="INSUFFICIENT_SAMPLE"},
                        {"canonical_trio_key":candidate.upper_member.trio_key,"structure_state":br["final_structure_state"],"insufficient_sample":br["final_structure_state"]=="INSUFFICIENT_SAMPLE"}]
            gate_data={"member_states":(candidate.lower_member.trio_state,candidate.upper_member.trio_state),
                "member_numbers":(candidate.lower_member.numbers,candidate.upper_member.numbers),"unit_statuses":tuple("COMPLETE" for _ in range(5)),
                "coverage_complete_cells":sum(x["complete_cell_count"] for x in coverage),"selection_exposure":n,
                "integrated_primary_rate":integrated,"integrated_primary_baseline":0.004932192028051359,"integrated_primary_evidence":None,
                "main_primary_rate":main,"main_primary_baseline":0.002146690518783542,"main_primary_evidence":None,
                "recent_state":"INSUFFICIENT_SAMPLE","final_risk":pair_context.member_maximum_risk,"final_structure":pair_context.member_structure_summary,"determinism_ok":True}
            audit=build_official_prediction_audit(evaluation_round=evaluation_round,source_end_round=source_end_round,
                data_prefix_hash=prefix,canonical_pair_key=candidate.canonical_pair_key,pair_numbers=candidate.numbers,
                pool_type=stage6["candidate_pool_type"],set1_key=candidate.lower_member.trio_key,set2_key=candidate.upper_member.trio_key,
                constituent_trios=members,unit_cells=cells,unit_summaries=summaries,member_risks=risks,member_structures=structures,
                selection_exposure=n,rule_signature=signature,canonical_rule_payload_json=rule_json,rank_values=rank,
                stable_key=candidate.canonical_pair_key,representative_selected=True,gate_data=gate_data)
            context.update(audit)
            context["gate_input"] = gate_data
            context["gate_results"] = {x["gate_id"]:x["status"] for x in audit["gate_records"]}
            context["pair_state"] = audit["pair_state"]
            context["canonical_rule_payload_json"] = rule_json
            predictions.append(PairPrediction(candidate.canonical_pair_key, signature,
                candidate.lower_member.numbers, candidate.upper_member.numbers, rank, context))
        return RoundPrediction(source_end_round, prefix, tuple(predictions))

    def compute_pre_result(self, evaluation_round: int, source_end_round: int,
                           history: Mapping[str, Sequence[Mapping[str, Any]]]) -> RoundPrediction:
        return self.build_prediction_context(evaluation_round, source_end_round, history)

    def load_round_outcome(self, evaluation_round: int) -> Mapping[str, Any]:
        self.outcome_accesses.append(evaluation_round)
        draw = self._draws[evaluation_round]
        return {"main": draw.main, "bonus": draw.bonus}

    def read_result(self, evaluation_round: int) -> Mapping[str, Any]:
        return self.load_round_outcome(evaluation_round)

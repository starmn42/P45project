"""Stage-4 persistence into an explicitly supplied v2.7 CORE store."""

from __future__ import annotations

import uuid

from ..core_store import CoreStore, utc_now
from ..integrity import canonical_json, sha256_json
from .models import UnitAnalysis


def _id(*parts: object) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "p45-v27:" + ":".join(map(str, parts))))


def persist_unit_analysis(store: CoreStore, core_run_id: str, analysis: UnitAnalysis) -> None:
    """Persist definitions and metrics; never creates or locks an official result."""
    with store.transaction() as db:
        run = db.execute("SELECT engine_version_id FROM core_run WHERE core_run_id=?", (core_run_id,)).fetchone()
        if run is None:
            raise ValueError("unknown core run")
        engine_id = run["engine_version_id"]
        unit_id = _id(engine_id, analysis.unit_type)
        definition_json = canonical_json(analysis.definition)
        db.execute(
            "INSERT OR IGNORE INTO unit_definition VALUES (?,?,?,?,?,?,?,?,?,?)",
            (unit_id, engine_id, analysis.unit_type, len(analysis.definition["groups"]),
             analysis.definition["correction_method"], list(("UNIT_3","UNIT_5","UNIT_9","UNIT_10","END_DIGIT")).index(analysis.unit_type)+1,
             "ACTIVE", definition_json, sha256_json(analysis.definition), utc_now()),
        )
        group_ids = {}
        for group in analysis.definition["groups"]:
            gid = _id(unit_id, group["order"])
            group_ids[group["label"]] = gid
            members = list(group["members"])
            payload = {"label": group["label"], "members": members}
            db.execute(
                """INSERT OR IGNORE INTO unit_group
                   (unit_group_id,unit_definition_id,group_order,group_label,group_size,start_number,end_number,
                    member_numbers_json,group_status,group_hash,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (gid, unit_id, group["order"], group["label"], group["size"], min(members), max(members),
                 canonical_json(members), "ACTIVE", sha256_json(payload), utc_now()),
            )
        for row in analysis.round_metrics:
            rid = _id(core_run_id, analysis.unit_type, row["group_label"], row["source_round"])
            vector_hash = sha256_json(row["occupancy_vector"])
            columns = ("unit_round_metric_id","core_run_id","unit_group_id","source_round","integrated_occupancy",
                "main_occupancy","group_size","integrated_occupancy_rate","main_occupancy_rate",
                "expected_integrated_count","expected_main_count","raw_integrated_deviation","raw_main_deviation",
                "standardized_integrated_deviation","standardized_main_deviation","is_annihilated",
                "consecutive_annihilation_length","next_return_count","return_depth","occupancy_vector_json",
                "period_metrics_json","opposite_hypothesis_json","structure_collapse_json","unit_state",
                "calculation_status","data_hash","vector_hash","row_hash","execution_hash","created_at")
            values = (rid, core_run_id, group_ids[row["group_label"]], row["source_round"], row["integrated"], row["main"],
                 row["group_size"], row["integrated_occupancy_rate"], row["main_occupancy_rate"],
                 row["expected_integrated_count"], row["expected_main_count"], row["raw_integrated_deviation"],
                 row["raw_main_deviation"], row["standardized_integrated_deviation"], row["standardized_main_deviation"],
                 int(row["is_annihilated"]), row["consecutive_annihilation_length"],
                 row["next_return_count"], row["return_depth"], canonical_json(row["occupancy_vector"]),
                 canonical_json(analysis.period_metrics[row["group_label"]]), canonical_json(analysis.opposite_hypothesis_inputs),
                 canonical_json(analysis.structure_collapse_inputs), analysis.unit_state, analysis.calculation_status,
                 analysis.data_hash, vector_hash, sha256_json(row), analysis.execution_hash, utc_now())
            db.execute(f"INSERT INTO unit_round_metric ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})", values)
        for number, metric in analysis.number_metrics.items():
            mid = _id(core_run_id, analysis.unit_type, number)
            columns = ("unit_number_metric_id","core_run_id","unit_definition_id","number","sample_count",
                "overall_metrics_json","recent_100_metrics_json","recent_50_metrics_json","recent_20_metrics_json",
                "exact_vector_metrics_json","local_state_metrics_json","opposite_hypothesis_json",
                "structure_collapse_json","sample_state","risk_state","unit_state","primary_context",
                "secondary_context","context_relation","bonus_dependence","opposite_risk","structure_state",
                "first_limiting_gate","reason_codes_json","decision_json","decision_hash","data_hash","metric_hash",
                "execution_hash","created_at")
            placeholder = {"stage": "4", "status": "AWAITING_STAGE_5_5"}
            values = (mid, core_run_id, unit_id, number, metric["sample_count"], canonical_json(metric["overall"]),
                 canonical_json(metric["recent100"]), canonical_json(metric["recent50"]), canonical_json(metric["recent20"]),
                 canonical_json(metric["exact_vector"]), canonical_json(metric["local_state"]),
                 canonical_json(metric["opposite_hypothesis_inputs"]), canonical_json(metric["structure_collapse_inputs"]),
                 metric["sample_state"], "INSUFFICIENT_SAMPLE" if metric["sample_state"] == "INSUFFICIENT" else "NOT_APPLICABLE",
                 analysis.unit_state, "NO_EVALUABLE_CONTEXT", "NONE", "CONTEXT_INCONCLUSIVE",
                 "BONUS_DEPENDENCE_NONE", "LOW", "INSUFFICIENT_SAMPLE", "STAGE_5_5_NOT_RUN",
                 canonical_json(["STAGE_5_5_NOT_RUN"]), canonical_json(placeholder), sha256_json(placeholder),
                 analysis.data_hash, sha256_json(metric), analysis.execution_hash, utc_now())
            db.execute(f"INSERT INTO unit_number_metric ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})", values)


def load_unit_analysis_counts(store: CoreStore, core_run_id: str, unit_type: str) -> dict[str, int]:
    with store.transaction() as db:
        groups = db.execute("""SELECT count(*) FROM unit_group g JOIN unit_definition d
            ON d.unit_definition_id=g.unit_definition_id WHERE d.unit_type=? AND d.engine_version_id=
            (SELECT engine_version_id FROM core_run WHERE core_run_id=?)""", (unit_type, core_run_id)).fetchone()[0]
        rounds = db.execute("""SELECT count(*) FROM unit_round_metric m JOIN unit_group g ON g.unit_group_id=m.unit_group_id
            JOIN unit_definition d ON d.unit_definition_id=g.unit_definition_id WHERE m.core_run_id=? AND d.unit_type=?""",
            (core_run_id, unit_type)).fetchone()[0]
        numbers = db.execute("""SELECT count(*) FROM unit_number_metric m JOIN unit_definition d
            ON d.unit_definition_id=m.unit_definition_id WHERE m.core_run_id=? AND d.unit_type=?""",
            (core_run_id, unit_type)).fetchone()[0]
        return {"groups": groups, "round_metrics": rounds, "number_metrics": numbers}

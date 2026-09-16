from __future__ import annotations

import hashlib
import gzip
import json
import pickle
import sqlite3
from pathlib import Path

from p45_v27.pairs.production import ProductionPairPipeline
from p45_v27.pairs.walkforward import PairWalkforwardRunner, SCHEMA

ROOT = Path(__file__).resolve().parents[3]
AUDIT = Path(__file__).resolve().parent
DATA = ROOT / "analysis/structure-1236/analysis-input.csv"
TRIO = AUDIT / "sandbox_trio_pair_adapter.sqlite3"
DB = AUDIT / "sandbox_pair.sqlite3"
CACHE = AUDIT / "pair_input_cache"

_cached_round = None
_cached_stage6 = None
_cached_trios = None


def cached_diagnose(data_path, evaluation_round):
    global _cached_round, _cached_stage6, _cached_trios
    path = CACHE / f"{evaluation_round}.pickle.gz"
    if not path.exists():
        from p45_v27.stage6_diagnostics import diagnose_stage6
        return diagnose_stage6(data_path, evaluation_round)
    with gzip.open(path, "rb") as handle:
        _cached_stage6, _cached_trios = pickle.load(handle)
    _cached_round = evaluation_round
    return _cached_stage6


def cached_build(stage6, definitions, history):
    if stage6 is _cached_stage6 and _cached_trios is not None:
        return _cached_trios
    from p45_v27.trio_engine import build_current_trios
    return build_current_trios(stage6, definitions, history)


class RecoveredSemanticsRunner(PairWalkforwardRunner):
    """Audit-only adapter for the already-approved locked-rank conflict recovery."""

    def _history(self, db: sqlite3.Connection, round_: int):
        rows = db.execute(
            "SELECT s.*,o.*,c.rank_key_json FROM wf_selection_exposure s "
            "JOIN wf_outcome o USING(selection_id) "
            "JOIN wf_round r USING(run_id,evaluation_round) "
            "JOIN wf_pair_candidate c ON c.run_id=s.run_id "
            "AND c.evaluation_round=s.evaluation_round "
            "AND c.canonical_pair_key=s.representative_pair_key "
            "WHERE s.run_id=? AND s.evaluation_round<? AND r.round_status='COMPLETE' "
            "ORDER BY s.evaluation_round,s.selection_id", (self.run_id, round_)).fetchall()
        out = {}
        for raw in rows:
            row = dict(raw)
            rank = json.loads(row["rank_key_json"])
            row["representative_conflict"] = int(rank[8][1]) > 0
            out.setdefault(row["base_pair_rule_signature"], []).append(row)
        return out


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    import p45_v27.pairs.production as production
    production.diagnose_stage6 = cached_diagnose
    production.build_current_trios = cached_build
    pipeline = ProductionPairPipeline(DATA, TRIO)
    code_files = [ROOT / "src/p45_v27/pair_walkforward.py",
                  ROOT / "src/p45_v27/pairs/audit_v12.py",
                  ROOT / "src/p45_v27/pairs/lifecycle_v12.py",
                  ROOT / "src/p45_v27/pairs/walkforward.py",
                  ROOT / "src/p45_v27/pairs/production.py"]
    runner = RecoveredSemanticsRunner(
        DB, run_id="synthetic-semantics-rebuild-001", start_round=43, end_round=1235,
        rule_hash=hashlib.sha256(b"approved-existing-official-pair-rule").hexdigest(),
        code_hash=hashlib.sha256("".join(sha(p) for p in code_files).encode()).hexdigest(),
        schema_hash=hashlib.sha256(SCHEMA.encode()).hexdigest(), pipeline=pipeline)
    print(json.dumps(runner.run(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

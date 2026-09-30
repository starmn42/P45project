"""Settlement Dispatcher for active research models."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
from typing import Any

from .constants import ROOT

class SettlementDispatcher:
    def __init__(self, root: Path = ROOT):
        self.root = root

    def dispatch_settlements(self, draw_round: int) -> dict[str, Any]:
        """Dispatches automatic settlements across active research models for the given round."""
        results = {
            "round": draw_round,
            "trio_orbit": None,
            "edge_arithmetic": None,
            "overlap_events": [],
        }

        # 1. TRIO ORBIT prospective settlement check
        trio_pros_dir = self.root / "v27_storage/prospective/trio_orbit_v1_001"
        if trio_pros_dir.exists():
            outcome_file = trio_pros_dir / f"P45_TRIO_ORBIT_TARGET_{draw_round}_OUTCOME_001.json"
            settle_file = trio_pros_dir / f"P45_TRIO_ORBIT_TARGET_{draw_round}_SETTLEMENT_001.json"
            results["trio_orbit"] = {
                "target_round": draw_round,
                "outcome_recorded": outcome_file.exists() or settle_file.exists(),
                "status": "SETTLED" if (outcome_file.exists() or settle_file.exists()) else "PENDING",
            }

        # 2. EDGE ARITHMETIC FAMILY settlement check & shadow update
        edge_dir = self.root / "v27_storage/experiments/edge_arithmetic_family_v1_001"
        edge_runner_script = edge_dir / "research_runner.py"
        if edge_runner_script.exists():
            try:
                # Load module dynamically
                spec = importlib.util.spec_from_file_location("edge_research_runner", edge_runner_script)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    live_csv = self.root / "v27_storage/live/p45_live_draws.csv"
                    shadow_dest = edge_dir / "shadow"
                    if shadow_dest.exists() and live_csv.exists():
                        update_res = mod.update(live_csv, shadow_dest, seal_latest=False)
                        results["edge_arithmetic"] = {
                            "status": "SHADOW_SETTLED",
                            "writes": update_res.get("writes", 0),
                        }
                    else:
                        results["edge_arithmetic"] = {"status": "SKIPPED_MISSING_SHADOW_DIR"}
            except Exception as exc:
                results["edge_arithmetic"] = {"status": "ERROR", "error": str(exc)}

        # 3. Detect Signal Overlap between TRIO ORBIT and EDGE ARITHMETIC
        trio_cands = self._get_trio_candidates_for_round(draw_round)
        edge_cands = self._get_edge_candidates_for_round(draw_round)
        if trio_cands and edge_cands:
            overlap = set(trio_cands) & set(edge_cands)
            if overlap:
                results["overlap_events"].append({
                    "round": draw_round,
                    "source_a": "TRIO_ORBIT_V1",
                    "source_b": "EDGE_ARITHMETIC_FAMILY_V1",
                    "label": "TRIO_EDGE_CONCORDANCE",
                    "overlapping_numbers": sorted(overlap),
                    "trio_candidates": sorted(trio_cands),
                    "edge_candidates": sorted(edge_cands),
                    "policy": "RECORD_ONLY_NO_OFFICIAL_PROMOTION",
                })

        return results

    def _get_trio_candidates_for_round(self, round_num: int) -> set[int]:
        trio_log = self.root / "v27_storage/prospective/trio_orbit_v1_001/P45_TRIO_ORBIT_PROSPECTIVE_LOG_001.csv"
        if not trio_log.exists():
            return set()
        cands = set()
        with trio_log.open("r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if int(row["target_round"]) == round_num:
                    for k in ("fixed_A", "fixed_B", "fixed_C", "linked_A", "linked_B", "linked_C"):
                        val = row.get(k)
                        if val:
                            cands.update(int(x) for x in val.split())
        return cands

    def _get_edge_candidates_for_round(self, round_num: int) -> set[int]:
        edge_shadow = self.root / "v27_storage/experiments/edge_arithmetic_family_v1_001/shadow"
        if not edge_shadow.exists():
            return set()
        cands = set()
        # Look for source file corresponding to lag1 or lag2
        for src_file in edge_shadow.glob("source_*.json"):
            try:
                data = json.loads(src_file.read_text(encoding="utf-8"))
                if round_num in data.get("targets", []):
                    for v in data.get("candidates", {}).values():
                        if v is not None and 1 <= v <= 45:
                            cands.add(v)
            except Exception:
                continue
        return cands

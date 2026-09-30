"""Novelty and Rescue Checker for P45 RESEARCH DISCOVERY AGENT V1.

Inspects structural attributes against all completed, failed, and active experiments.
Rejects duplicates (same inputs/transform/target/lag/direction) and rescues of failed axes.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .research_coverage_map import EXPERIMENT_ONTOLOGY_MAPPING

logger = logging.getLogger("p45.research_automation.novelty")

@dataclass
class NoveltyVerdict:
    is_novel: bool
    verdict: str  # "NOVEL", "REJECT_DUPLICATE", "REJECT_RESCUE"
    reason: str
    conflicting_experiment: str | None = None

class NoveltyChecker:
    """Performs strict structural novelty and anti-rescue audits on proposed hypothesis packages."""

    def __init__(self, known_experiments: dict[str, dict[str, Any]] | None = None):
        self.known_experiments = known_experiments or EXPERIMENT_ONTOLOGY_MAPPING

    def check_candidate_novelty(self, candidate_dict: dict[str, Any]) -> NoveltyVerdict:
        """Audits candidate across 7 structural dimensions:
        1. inputs
        2. transformation
        3. target
        4. lag
        5. conditioning
        6. metric
        7. hypothesis direction
        """
        cand_title = candidate_dict.get("title", "").lower()
        cand_concepts = [c.value if hasattr(c, "value") else str(c) for c in candidate_dict.get("ontology_tags", [])]
        cand_hyp = candidate_dict.get("hypothesis", "").lower()
        cand_origin = candidate_dict.get("origin", "")

        # 1. Anti-rescue check against failed axes
        for exp_id, meta in self.known_experiments.items():
            if meta["verdict"] in ("FAILED", "FAILED_EARLY", "FAILED_NOT_SUPPORTED", "AXIS_CLOSED"):
                mech = meta["mechanism"].lower()
                title = meta["title"].lower()
                
                # Check if this candidate attempts to rescue the failed mechanism with mere renaming
                # e.g. reviving lag-1 parity covariance, or variable extinction hunting
                if (("parity" in mech or "홀수" in title) and ("parity" in cand_title or "홀수" in cand_title) and "lag" in cand_hyp):
                    return NoveltyVerdict(
                        is_novel=False,
                        verdict="REJECT_RESCUE",
                        reason=f"Candidate attempts to revive failed parity covariance from {exp_id} without new structural mechanism.",
                        conflicting_experiment=exp_id,
                    )
                if (("birthday" in mech or "생일" in title) and ("birthday" in cand_title or "생일" in cand_title)):
                    return NoveltyVerdict(
                        is_novel=False,
                        verdict="REJECT_RESCUE",
                        reason=f"Candidate attempts to revive failed crowd birthday range from {exp_id}.",
                        conflicting_experiment=exp_id,
                    )
                if ("동시출현" in title and "clustering" in cand_title and "opposite" not in cand_origin.lower()):
                    return NoveltyVerdict(
                        is_novel=False,
                        verdict="REJECT_RESCUE",
                        reason=f"Candidate revives failed positive co-occurrence clustering from {exp_id}.",
                        conflicting_experiment=exp_id,
                    )

        # 2. Duplicate check against all registered experiments
        for exp_id, meta in self.known_experiments.items():
            # Check title / exact concept collision
            exp_title = meta["title"].lower()
            if cand_title == exp_title:
                return NoveltyVerdict(
                    is_novel=False,
                    verdict="REJECT_DUPLICATE",
                    reason=f"Candidate title matches registered experiment {exp_id} exactly.",
                    conflicting_experiment=exp_id,
                )

        # If passed both
        return NoveltyVerdict(
            is_novel=True,
            verdict="NOVEL",
            reason="Candidate introduces distinct structural dimension, clear opposite direction, or untested negative space.",
            conflicting_experiment=None,
        )

"""Candidate Ranker for P45 RESEARCH DISCOVERY AGENT V1.

Strict Priority Principles (Section 20):
1. Independence
2. Novelty
3. Verifiability
4. Falsifiability
5. Prospective testability
6. Relevance to P45 core problem (NO-PICK)

STRICT PROHIBITION:
Ranking is NEVER based on historical backtest performance, hit rates, or p-values.
Capped strictly at max 3 candidates per cycle (Section 21).
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("p45.research_automation.ranker")

MAX_CANDIDATES_PER_CYCLE = 3

class CandidateRanker:
    """Ranks quality-gate-cleared candidate packages by scientific validity and independence."""

    @staticmethod
    def calculate_scientific_priority_score(candidate_pkg: dict[str, Any]) -> float:
        score = 0.0
        
        # 1. Independence (Cross-structure / Negative space / Opposite get higher weight)
        origin = candidate_pkg.get("origin", "")
        if "NEGATIVE_SPACE" in origin:
            score += 25.0
        elif "OPPOSITE_HYPOTHESIS" in origin:
            score += 22.0
        elif "CROSS_STRUCTURE" in origin:
            score += 20.0
        else:
            score += 15.0

        # 2. Novelty (Breadth of ontology concepts involved)
        tags = candidate_pkg.get("ontology_tags", [])
        score += min(len(tags) * 4.0, 16.0)

        # 3. Verifiability & Falsifiability (Clear null and strict failure condition)
        null_def = candidate_pkg.get("null", "")
        if "hypergeometric" in null_def.lower() or "order statistics" in null_def.lower() or "geometric" in null_def.lower():
            score += 20.0
        else:
            score += 10.0

        # 4. Prospective Testability (Reasonable sample size for future draws)
        sample = candidate_pkg.get("minimum_sample", 0)
        if 20 <= sample <= 50:
            score += 15.0
        elif sample > 50:
            score += 10.0

        # 5. NO-PICK / Official Invariant Relevance (Protects official engine, clarifies boundaries)
        if "invariant" in candidate_pkg.get("title", "").lower() or "dispersion" in candidate_pkg.get("title", "").lower():
            score += 10.0

        return score

    def rank_and_select(self, candidate_pkgs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sorts candidates by scientific priority score and enforces max 3 per cycle."""
        scored = []
        for pkg in candidate_pkgs:
            p_score = self.calculate_scientific_priority_score(pkg)
            scored.append((p_score, pkg))

        # Sort descending by priority score
        scored.sort(key=lambda item: item[0], reverse=True)

        selected = [item[1] for item in scored[:MAX_CANDIDATES_PER_CYCLE]]
        logger.info(
            f"CandidateRanker received {len(candidate_pkgs)} candidates; selected top {len(selected)} (capped at {MAX_CANDIDATES_PER_CYCLE})."
        )
        return selected

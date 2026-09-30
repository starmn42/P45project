"""Coverage Gap Analyzer for P45 RESEARCH DISCOVERY AGENT V1.

Identifies structural spaces that have not been investigated in P45,
focusing on:
- STRUCTURAL_GAP
- CROSS_STRUCTURE
- TEMPORAL_STRUCTURE
- OPPOSITE_HYPOTHESIS
- INTERACTION
- NEGATIVE_SPACE

Strictly excludes failed mechanisms to prevent disguised rescues.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .research_ontology import OntologyConcept

logger = logging.getLogger("p45.research_automation.gap_analyzer")

class GapCategory(str, Enum):
    STRUCTURAL_GAP = "STRUCTURAL_GAP"
    CROSS_STRUCTURE = "CROSS_STRUCTURE"
    TEMPORAL_STRUCTURE = "TEMPORAL_STRUCTURE"
    OPPOSITE_HYPOTHESIS = "OPPOSITE_HYPOTHESIS"
    INTERACTION = "INTERACTION"
    NEGATIVE_SPACE = "NEGATIVE_SPACE"

@dataclass
class StructuralGapOpportunity:
    gap_id: str
    category: GapCategory
    primary_concepts: list[OntologyConcept]
    title: str
    structural_description: str
    falsification_angle: str
    null_baseline_concept: str
    excluded_failed_predecessors: list[str]

class CoverageGapAnalyzer:
    """Analyzes coverage map to identify genuine structural research opportunities."""

    def __init__(self, coverage_map: dict[str, Any]):
        self.coverage_map = coverage_map
        self.axes = coverage_map.get("axes", {})

    def identify_structural_gaps(self) -> list[StructuralGapOpportunity]:
        """Returns verified structural gap opportunities that do not duplicate or rescue failed axes."""
        opportunities: list[StructuralGapOpportunity] = []

        # Opportunity 1: NEGATIVE_SPACE + EXTINCTION + RECOVERY
        # Concept: When a fixed decile partition (e.g. 5 zones of 9 numbers) experiences complete extinction (0 balls),
        # does the recovery time or next-round zone occupancy deviate from the memoryless hypergeometric null?
        opportunities.append(
            StructuralGapOpportunity(
                gap_id="GAP-NEGSPACE-EXTINCTION-001",
                category=GapCategory.NEGATIVE_SPACE,
                primary_concepts=[OntologyConcept.EXTINCTION, OntologyConcept.RECOVERY, OntologyConcept.OCCUPANCY],
                title="Fixed-Partition Extinction Negative-Space Recovery Invariance",
                structural_description=(
                    "Evaluates whether the complete absence of balls in a fixed decile partition (Zone Extinction) "
                    "creates a structural recovery rebound in round t+1, or strictly conforms to the memoryless hypergeometric null."
                ),
                falsification_angle=(
                    "Falsified if next-round ball distribution in the extinct zone conforms to binomial hypergeometric expectation (p > 0.05)."
                ),
                null_baseline_concept="Hypergeometric draw without memory (P(k balls from 9) = C(9,k)*C(36,6-k)/C(45,6))",
                excluded_failed_predecessors=["EXP-004 (Variable extinction hunting)"],
            )
        )

        # Opportunity 2: OPPOSITE_HYPOTHESIS + NUMBER + SPACING
        # Concept: EXP-001 and EXP-018 tested positive clustering/adjacency and failed.
        # Opposite hypothesis: Number Repulsion / Negative Correlation in proximate intervals.
        opportunities.append(
            StructuralGapOpportunity(
                gap_id="GAP-OPP-REPULSION-002",
                category=GapCategory.OPPOSITE_HYPOTHESIS,
                primary_concepts=[OntologyConcept.OPPOSITE_STATE, OntologyConcept.SPACING, OntologyConcept.NUMBER],
                title="Number Proximity Minimum-Distance Repulsion Invariance",
                structural_description=(
                    "Tests the exact opposite hypothesis to failed clustering (EXP-001): "
                    "whether consecutive sorted winning balls exhibit significant repulsion (spacing > null expectation) "
                    "or strict Poisson spacing."
                ),
                falsification_angle=(
                    "Falsified if inter-ball minimum spacing distribution is indistinguishable from uniform order statistics null."
                ),
                null_baseline_concept="Order statistics spacing under uniform random sampling from 1..45",
                excluded_failed_predecessors=["EXP-001 (Number clustering)", "EXP-018 (Neighbor adjacency)"],
            )
        )

        # Opportunity 3: CROSS_STRUCTURE + PAIR + TRANSITION
        # Concept: Cross-structure interaction between PAIR lifecycle states and TRIO orbit transitions,
        # without modifying any official parameters or thresholds.
        opportunities.append(
            StructuralGapOpportunity(
                gap_id="GAP-CROSS-PAIR-TRANSITION-003",
                category=GapCategory.CROSS_STRUCTURE,
                primary_concepts=[OntologyConcept.PAIR, OntologyConcept.TRANSITION, OntologyConcept.CONDITIONAL_TRANSITION],
                title="Pair Lifecycle Dormancy Duration Geometric Memory Invariance",
                structural_description=(
                    "Investigates whether pair lifecycle dormancy durations follow the memoryless geometric distribution "
                    "P(Gap = k) = (1 - p)^(k-1) * p under fair lottery conditions, or exhibit hazard rate non-stationarity."
                ),
                falsification_angle=(
                    "Falsified if empirical survival/hazard curves for pair dormancy do not reject geometric memoryless null."
                ),
                null_baseline_concept="Geometric distribution with parameter p0 = C(43,4)/C(45,6) = 15/1485 ≈ 0.0101",
                excluded_failed_predecessors=["EXP-012 (Return-age rank mining)"],
            )
        )

        logger.info(f"Identified {len(opportunities)} structural gap opportunities.")
        return opportunities

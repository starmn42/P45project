"""Idea Providers for P45 RESEARCH DISCOVERY AGENT V1.

Implements provider abstraction:
- BaseIdeaProvider (ABC)
- DeterministicStructuralProvider (ACTIVE: structural gap synthesizer without outcome mining)
- OptionalLLMIdeaProvider (NOT_CONFIGURED: secure fallback when external AI is not configured)
"""
from __future__ import annotations

import abc
import logging
import os
from typing import Any

from .coverage_gap_analyzer import CoverageGapAnalyzer, GapCategory, StructuralGapOpportunity
from .research_ontology import OntologyConcept

logger = logging.getLogger("p45.research_automation.idea_provider")

class BaseIdeaProvider(abc.ABC):
    @abc.abstractmethod
    def get_provider_name(self) -> str:
        pass

    @abc.abstractmethod
    def get_status(self) -> str:
        pass

    @abc.abstractmethod
    def generate_candidate_hypotheses(
        self,
        coverage_map: dict[str, Any],
        canonical_round: int,
    ) -> list[dict[str, Any]]:
        pass

class DeterministicStructuralProvider(BaseIdeaProvider):
    """Generates rigorous structural research hypotheses purely from ontology coverage gaps.
    
    Strict Rule:
    Never scans historical draw outcomes to optimize hit rates or cherry-pick combinations.
    Formulates hypotheses strictly from theoretical structural gap opportunities.
    """

    def get_provider_name(self) -> str:
        return "DeterministicStructuralProvider"

    def get_status(self) -> str:
        return "ACTIVE"

    def generate_candidate_hypotheses(
        self,
        coverage_map: dict[str, Any],
        canonical_round: int,
    ) -> list[dict[str, Any]]:
        analyzer = CoverageGapAnalyzer(coverage_map)
        opportunities = analyzer.identify_structural_gaps()

        candidates: list[dict[str, Any]] = []

        # Safe confirmatory start round calculation:
        # If canonical is 1243 and 1244 is pending and uncorrupted, confirmatory starts at 1244.
        confirmatory_start = canonical_round + 1

        for idx, opp in enumerate(opportunities, start=1):
            cand_id = f"IDEA-{canonical_round}-{opp.category.value[:4]}-{idx:03d}"
            
            if opp.category == GapCategory.NEGATIVE_SPACE:
                hypothesis = (
                    "When a fixed 5-zone partition (Zones 1..5, each 9 balls) experiences complete extinction (0 balls drawn) "
                    "in round t, the occupancy count in round t+1 exhibits positive compensatory rebound exceeding hypergeometric expectation."
                )
                opp_hypothesis = (
                    "Zone extinction has zero memory effect: next-round zone occupancy conforms strictly to the memoryless hypergeometric "
                    "distribution P(k balls | 9 balls in zone, 6 drawn from 45)."
                )
                source_vars = ["fixed_5_zone_occupancy_t"]
                target_var = "fixed_5_zone_occupancy_t_plus_1"
                primary_metric = "next_round_zone_rebound_excess_z"
                null_def = "Memoryless hypergeometric sampling: E[k] = 6 * (9/45) = 1.2 balls"
                fail_cond = "Observed two-sided exact binomial/hypergeometric p-value > 0.05 on prospective test draws."
                min_sample = 30
            elif opp.category == GapCategory.OPPOSITE_HYPOTHESIS:
                hypothesis = (
                    "Consecutive sorted winning numbers exhibit significant repulsion (minimum adjacent spacing > Poisson null), "
                    "acting as a structural dispersion constraint."
                )
                opp_hypothesis = (
                    "Adjacent ball spacing is completely memoryless and conforms strictly to the uniform order-statistics spacing null distribution."
                )
                source_vars = ["sorted_main6_numbers_t"]
                target_var = "adjacent_spacing_vector_t"
                primary_metric = "minimum_adjacent_spacing_ks_statistic"
                null_def = "Uniform order statistics spacing on {1..45} with 6 balls"
                fail_cond = "Kolmogorov-Smirnov test against order statistics null fails to reject null at alpha=0.05."
                min_sample = 40
            else: # CROSS_STRUCTURE
                hypothesis = (
                    "Pair lifecycle dormancy durations (gap rounds between occurrences) follow the memoryless geometric distribution, "
                    "confirming complete temporal independence of ball pairings."
                )
                opp_hypothesis = (
                    "Pair lifecycle dormancy exhibits non-geometric hazard aging or structural clustering."
                )
                source_vars = ["pair_dormancy_gap_history"]
                target_var = "next_pair_activation_gap"
                primary_metric = "geometric_hazard_log_rank_p"
                null_def = "Geometric distribution with p0 = C(43,4)/C(45,6) ≈ 0.010101"
                fail_cond = "Log-rank or chi-squared goodness-of-fit fails to detect significant hazard deviation from geometric null."
                min_sample = 50

            pkg = {
                "candidate_id": cand_id,
                "title": opp.title,
                "origin": f"STRUCTURAL_DISCOVERY_AGENT_V1:{opp.category.value}",
                "ontology_tags": [c.value for c in opp.primary_concepts],
                "novelty_reason": opp.structural_description,
                "hypothesis": hypothesis,
                "opposite_hypothesis": opp_hypothesis,
                "source_variables": source_vars,
                "target_variable": target_var,
                "lag": 1,
                "primary_metric": primary_metric,
                "null": null_def,
                "minimum_sample": min_sample,
                "failure_condition": fail_cond,
                "future_validation_plan": f"Eligible for confirmatory start from round {confirmatory_start} onwards, strictly locked upon protocol completion (minimum sample {min_sample}).",
                "duplicate_check": "PENDING_SEMANTIC_AUDIT",
                "rescue_check": f"PENDING_SEMANTIC_AUDIT: Excluded predecessors: {', '.join(opp.excluded_failed_predecessors)}",
                "discovery_data_end_round": canonical_round,
                "earliest_eligible_confirmatory_round": confirmatory_start,
                "confirmatory_start_round": None,
                "confirmatory_lock_status": "PENDING_PROTOCOL_LOCK",
            }
            candidates.append(pkg)

        logger.info(f"DeterministicStructuralProvider synthesized {len(candidates)} candidates.")
        return candidates

class OptionalLLMIdeaProvider(BaseIdeaProvider):
    """Optional LLM Idea Provider interface.
    
    Strict Safety Constraint:
    If no secure LLM API is configured in the environment, reports NOT_CONFIGURED.
    Does NOT fabricate fake keys, does NOT prompt the user, and does NOT store credentials in code.
    """

    def __init__(self):
        self.api_key = os.getenv("P45_EXTERNAL_LLM_API_KEY")

    def get_provider_name(self) -> str:
        return "OptionalLLMIdeaProvider"

    def get_status(self) -> str:
        if not self.api_key:
            return "NOT_CONFIGURED"
        return "CONFIGURED_STANDBY"

    def generate_candidate_hypotheses(
        self,
        coverage_map: dict[str, Any],
        canonical_round: int,
    ) -> list[dict[str, Any]]:
        # When not configured, safely return empty list without failing or throwing
        if self.get_status() == "NOT_CONFIGURED":
            logger.info("OptionalLLMIdeaProvider is NOT_CONFIGURED; skipping external AI generation.")
            return []
        # Interface placeholder for future authenticated provider
        return []

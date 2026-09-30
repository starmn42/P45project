"""Research Ontology for P45 RESEARCH DISCOVERY AGENT V1.

Defines the explicit conceptual structural space for P45 research.
Strict Principle:
Ontology is a map for detecting structural coverage gaps.
Brute-force cartesian combinations and endless arithmetic permutations are STRICTLY PROHIBITED.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class OntologyConcept(str, Enum):
    # Core entities
    NUMBER = "NUMBER"
    TRIO = "TRIO"
    PAIR = "PAIR"
    CORE = "CORE"
    
    # State & Lifecycle dynamics
    OCCUPANCY = "occupancy"
    EXTINCTION = "extinction"
    RECOVERY = "recovery"
    TRANSITION = "transition"
    RECURRENCE = "recurrence"
    
    # Spatial & Temporal measures
    LAG = "lag"
    GAP = "gap"
    SPACING = "spacing"
    RANGE = "range"
    SIMILARITY = "similarity"
    
    # Dynamics & Polarization
    OPPOSITE_STATE = "opposite-state"
    PERSISTENCE = "persistence"
    DECAY = "decay"
    REGIME = "regime"
    ORDER_RANK = "order/rank"
    
    # Transformations & Interactions
    ARITHMETIC_TRANSFORM = "arithmetic transform"
    INTERACTION = "interaction"
    CONDITIONAL_TRANSITION = "conditional transition"
    BONUS_INTERACTION = "bonus interaction"
    CROSS_ROUND_RELATION = "cross-round relation"

# 24 Explicit Concept Axes
ALL_ONTOLOGY_CONCEPTS: list[OntologyConcept] = list(OntologyConcept)

@dataclass(frozen=True)
class StructuralAxisDefinition:
    concept: OntologyConcept
    category: str
    description: str
    allowed_roles: list[str]
    forbidden_mining_patterns: list[str]

AXIS_DEFINITIONS: dict[OntologyConcept, StructuralAxisDefinition] = {
    OntologyConcept.NUMBER: StructuralAxisDefinition(
        concept=OntologyConcept.NUMBER,
        category="CORE_ENTITY",
        description="Individual lottery ball index (1..45)",
        allowed_roles=["target", "source", "conditioning"],
        forbidden_mining_patterns=["brute-force label selection", "post-hoc hot/cold cherry-picking"],
    ),
    OntologyConcept.TRIO: StructuralAxisDefinition(
        concept=OntologyConcept.TRIO,
        category="CORE_ENTITY",
        description="3-element subsets of balls / orbit triads",
        allowed_roles=["candidate_set", "orbit_state", "target"],
        forbidden_mining_patterns=["infinite subset testing", "arbitrary 3-tuple scoring"],
    ),
    OntologyConcept.PAIR: StructuralAxisDefinition(
        concept=OntologyConcept.PAIR,
        category="CORE_ENTITY",
        description="Pair-level relations and lifecycle structures",
        allowed_roles=["pair_lifecycle", "state_transition"],
        forbidden_mining_patterns=["unfiltered pair scan without pre-registered null"],
    ),
    OntologyConcept.CORE: StructuralAxisDefinition(
        concept=OntologyConcept.CORE,
        category="CORE_ENTITY",
        description="P45 Official Core Engine representations and invariant rules",
        allowed_roles=["baseline", "official_invariant"],
        forbidden_mining_patterns=["unauthorized engine parameter mutation"],
    ),
    OntologyConcept.OCCUPANCY: StructuralAxisDefinition(
        concept=OntologyConcept.OCCUPANCY,
        category="LIFECYCLE",
        description="Presence/absence of balls across partition buckets",
        allowed_roles=["bucket_distribution", "conditioning"],
        forbidden_mining_patterns=["arbitrary bin redefinition to fit past hits"],
    ),
    OntologyConcept.EXTINCTION: StructuralAxisDefinition(
        concept=OntologyConcept.EXTINCTION,
        category="LIFECYCLE",
        description="Complete absence of balls in specific ranges/zones",
        allowed_roles=["state_detection", "conditioning"],
        forbidden_mining_patterns=["variable zone hunting until p < 0.05"],
    ),
    OntologyConcept.RECOVERY: StructuralAxisDefinition(
        concept=OntologyConcept.RECOVERY,
        category="LIFECYCLE",
        description="Return velocity/probability after an extinction event",
        allowed_roles=["temporal_dynamics", "transition_target"],
        forbidden_mining_patterns=["post-hoc threshold tuning on recovery intervals"],
    ),
    OntologyConcept.TRANSITION: StructuralAxisDefinition(
        concept=OntologyConcept.TRANSITION,
        category="DYNAMICS",
        description="State-to-state conditional mapping between consecutive rounds",
        allowed_roles=["transition_matrix", "conditional_state"],
        forbidden_mining_patterns=["high-order transition graph fitting"],
    ),
    OntologyConcept.RECURRENCE: StructuralAxisDefinition(
        concept=OntologyConcept.RECURRENCE,
        category="DYNAMICS",
        description="Re-emergence of past winning elements into subsequent draws",
        allowed_roles=["anchor_recurrence", "carryover_test"],
        forbidden_mining_patterns=["selecting best recurrence window post-hoc"],
    ),
    OntologyConcept.LAG: StructuralAxisDefinition(
        concept=OntologyConcept.LAG,
        category="SPATIAL_TEMPORAL",
        description="Temporal displacement in round steps (t - k)",
        allowed_roles=["temporal_lag"],
        forbidden_mining_patterns=["scanning k from 1 to 100 to report lowest p"],
    ),
    OntologyConcept.GAP: StructuralAxisDefinition(
        concept=OntologyConcept.GAP,
        category="SPATIAL_TEMPORAL",
        description="Consecutive intervals of non-appearance for numbers/structures",
        allowed_roles=["interval_length", "hazard_rate"],
        forbidden_mining_patterns=["hazard curve fitting to past lottery draws"],
    ),
    OntologyConcept.SPACING: StructuralAxisDefinition(
        concept=OntologyConcept.SPACING,
        category="SPATIAL_TEMPORAL",
        description="Numerical distances between sorted winning numbers",
        allowed_roles=["dispersion_measure", "spread_metric"],
        forbidden_mining_patterns=["custom spacing combinations"],
    ),
    OntologyConcept.RANGE: StructuralAxisDefinition(
        concept=OntologyConcept.RANGE,
        category="SPATIAL_TEMPORAL",
        description="Max - min spread or fixed decile partitions (1-10, 11-20, etc.)",
        allowed_roles=["structural_envelope", "partition"],
        forbidden_mining_patterns=["arbitrary window shifting"],
    ),
    OntologyConcept.SIMILARITY: StructuralAxisDefinition(
        concept=OntologyConcept.SIMILARITY,
        category="SPATIAL_TEMPORAL",
        description="Vector or set distance between multi-round draw configurations",
        allowed_roles=["clustering_metric", "distance_test"],
        forbidden_mining_patterns=["distance metric searching to maximize match"],
    ),
    OntologyConcept.OPPOSITE_STATE: StructuralAxisDefinition(
        concept=OntologyConcept.OPPOSITE_STATE,
        category="DYNAMICS",
        description="Structural complement or inverse hypothesis of a tested state",
        allowed_roles=["falsification_control", "negative_space_test"],
        forbidden_mining_patterns=["symmetrical overfitting"],
    ),
    OntologyConcept.PERSISTENCE: StructuralAxisDefinition(
        concept=OntologyConcept.PERSISTENCE,
        category="DYNAMICS",
        description="Multi-round stability of a structural state (e.g. regime length)",
        allowed_roles=["duration_test", "autocorrelation"],
        forbidden_mining_patterns=["survival function optimization"],
    ),
    OntologyConcept.DECAY: StructuralAxisDefinition(
        concept=OntologyConcept.DECAY,
        category="DYNAMICS",
        description="Rate of signal or carryover dampening over consecutive rounds",
        allowed_roles=["attenuation_model"],
        forbidden_mining_patterns=["exponential decay rate tuning"],
    ),
    OntologyConcept.REGIME: StructuralAxisDefinition(
        concept=OntologyConcept.REGIME,
        category="DYNAMICS",
        description="Macro-state classification (e.g. dispersion, crowd, volatility)",
        allowed_roles=["conditioning_context", "regime_indicator"],
        forbidden_mining_patterns=["hidden Markov model state hunting"],
    ),
    OntologyConcept.ORDER_RANK: StructuralAxisDefinition(
        concept=OntologyConcept.ORDER_RANK,
        category="TRANSFORMATION",
        description="Ordinal ranking (return-age rank, frequency rank, size rank)",
        allowed_roles=["rank_transformation"],
        forbidden_mining_patterns=["rank permutation mining"],
    ),
    OntologyConcept.ARITHMETIC_TRANSFORM: StructuralAxisDefinition(
        concept=OntologyConcept.ARITHMETIC_TRANSFORM,
        category="TRANSFORMATION",
        description="Deterministic algebraic transforms (sums, parity, differences)",
        allowed_roles=["congruence_test", "invariance_check"],
        forbidden_mining_patterns=["infinite polynomial / modulo brute-forcing"],
    ),
    OntologyConcept.INTERACTION: StructuralAxisDefinition(
        concept=OntologyConcept.INTERACTION,
        category="INTERACTION",
        description="Joint concordance or discordance between two independent axes",
        allowed_roles=["bivariate_agreement", "cross_signal"],
        forbidden_mining_patterns=["pairwise n-choose-2 interaction hunting"],
    ),
    OntologyConcept.CONDITIONAL_TRANSITION: StructuralAxisDefinition(
        concept=OntologyConcept.CONDITIONAL_TRANSITION,
        category="INTERACTION",
        description="Transition probability P(State_{t} | Context_{t-1})",
        allowed_roles=["conditional_likelihood"],
        forbidden_mining_patterns=["context conditioning tree pruning"],
    ),
    OntologyConcept.BONUS_INTERACTION: StructuralAxisDefinition(
        concept=OntologyConcept.BONUS_INTERACTION,
        category="INTERACTION",
        description="Specific cross-talk between the 7th ball (Bonus) and MAIN6",
        allowed_roles=["bonus_migration", "exchangeability_test"],
        forbidden_mining_patterns=["arbitrary bonus weighting"],
    ),
    OntologyConcept.CROSS_ROUND_RELATION: StructuralAxisDefinition(
        concept=OntologyConcept.CROSS_ROUND_RELATION,
        category="INTERACTION",
        description="Structural relationships bridging non-consecutive rounds",
        allowed_roles=["lag_relation", "periodic_resonance"],
        forbidden_mining_patterns=["scanning all round lag pairings"],
    ),
}

def validate_ontology_tags(tags: list[str]) -> list[OntologyConcept]:
    """Validates that tags belong to the authoritative ontology."""
    validated = []
    for tag in tags:
        try:
            concept = OntologyConcept(tag)
            validated.append(concept)
        except ValueError:
            # Check case-insensitive match
            matched = False
            for c in OntologyConcept:
                if c.value.lower() == tag.lower() or c.name.lower() == tag.lower():
                    validated.append(c)
                    matched = True
                    break
            if not matched:
                raise ValueError(f"Unknown ontology tag: '{tag}'. Must be one of {[c.value for c in OntologyConcept]}")
    return validated

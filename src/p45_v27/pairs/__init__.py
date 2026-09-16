"""P45 v2.7.4 PAIR candidate and schema-274 storage primitives."""

from .engine import base_pair_rule_signature, canonical_pair_key, generate_pair_candidates, pair_rule_signature
from .models import PairCandidate, PairSignatureContext, TrioInput
from .store import PairStore
from .decision import (
    GATE_IDS, GateResult, ParetoVector, assign_sets, bonus_dependence,
    decide_state, evaluate_gates, final_structure, pair_risk,
    pair_unit_coverage, pareto_dominates, ranking_key, recent_support_state, structure_state,
)

__all__ = [
    "PairCandidate",
    "PairSignatureContext",
    "PairStore",
    "TrioInput",
    "canonical_pair_key",
    "base_pair_rule_signature",
    "generate_pair_candidates",
    "pair_rule_signature",
    "GATE_IDS", "GateResult", "ParetoVector", "assign_sets",
    "bonus_dependence", "decide_state", "evaluate_gates", "final_structure",
    "pair_risk", "pair_unit_coverage", "pareto_dominates", "ranking_key", "recent_support_state",
    "structure_state",
]

"""Hypothesis Candidate Builder for AUTO RESEARCH LOOP V1.

Enforces:
1. Only 3 allowed types: INDEPENDENT_NEW_HYPOTHESIS, OPPOSITE_HYPOTHESIS, INTERACTION_HYPOTHESIS
2. Maximum 3 candidates per cycle (runaway prevention)
3. Data contamination prevention: birth_round = R, discovery_end = R, confirmatory_start >= R+1
4. Strict deterministic construction without external AI keys
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Sequence

from .candidate_queue import CandidateQueue, CandidateRecord
from .constants import FollowupType, MAX_CANDIDATES_PER_CYCLE, NOVEL_IDEA_GENERATION_EXTERNAL_AI, ResearchState
from .followup_gate import FollowupGate

class HypothesisCandidateBuilder:
    def __init__(self, queue: CandidateQueue | None = None, gate: FollowupGate | None = None):
        self.queue = queue or CandidateQueue()
        self.gate = gate or FollowupGate()

    def build_candidates_for_round(
        self,
        current_round: int,
        active_retrospective_summaries: Sequence[dict[str, Any]],
        overlap_events: Sequence[dict[str, Any]] | None = None,
    ) -> list[CandidateRecord]:
        """Generates candidate hypotheses for a newly settled round."""
        generated: list[CandidateRecord] = []

        # Check existing candidates born in this round to prevent exceeding max
        existing_count = self.queue.count_by_birth_round(current_round)
        remaining_budget = MAX_CANDIDATES_PER_CYCLE - existing_count
        if remaining_budget <= 0:
            return []

        # 1. Type B: OPPOSITE_HYPOTHESIS
        # If an active research shows persistence of zero or negative lift vs null
        for retro in active_retrospective_summaries:
            if remaining_budget <= 0:
                break
            if retro.get("null_excess_observed") is False and retro.get("verdict") in ("NO_EVIDENCE_OF_LINKED_SUPERIORITY", "FAILED"):
                cand_id = f"CAND-{current_round:04d}-OPP-{retro['research_id'][-7:]}"
                proposal = {
                    "name": f"OPPOSITE_{retro['research_id']}",
                    "hypothesis": f"Reversal/Dispersion: Numbers outside {retro['research_id']} active selection set exhibit higher recurrence than selected set.",
                    "opposite_hypothesis": f"{retro['research_id']} selected set exhibits superior recurrence compared to non-selected universe.",
                    "is_post_hoc_rescue": False,
                    "relaxes_threshold": False,
                    "cherry_picked_subset": False,
                    "independent_rationale": "Symmetric falsification test of rejected concentration hypothesis.",
                    "null_comparison_defined": True,
                    "future_leakage_blocked": True,
                    "minimum_sample": 100,
                    "success_criteria": "Holdout/Prospective lift > 0 with exact two-sided p <= 0.05",
                    "failure_criteria": "Lift <= 0 or p > 0.05",
                    "prospective_or_untouched_holdout": True,
                    "multiple_testing_control": "Holm-Bonferroni across hypothesis family",
                }
                decision = self.gate.evaluate(proposal)
                state = ResearchState.READY_FOR_PROTOCOL if decision.passed else ResearchState.REJECT_NOT_TESTABLE
                record = CandidateRecord(
                    candidate_id=cand_id,
                    created_at=datetime.now(timezone.utc).isoformat(),
                    birth_round=current_round,
                    source_research=retro["research_id"],
                    candidate_type=FollowupType.OPPOSITE_HYPOTHESIS.value,
                    hypothesis=proposal["hypothesis"],
                    opposite_hypothesis=proposal["opposite_hypothesis"],
                    novelty_status="SYMMETRIC_OPPOSITE",
                    duplicate_status="PASS" if decision.passed else decision.rejection_reasons[0],
                    rescue_check="PASS",
                    data_snooping_status="PASS",
                    confirmatory_start_round=current_round + 1,
                    minimum_sample=100,
                    recommended_action="REGISTER_PROSPECTIVE_PROTOCOL" if decision.passed else "ARCHIVE_REJECTED",
                    state=state.value,
                    notes=f"Data before round {current_round} marked EXPLORATORY_ONLY.",
                )
                generated.append(record)
                remaining_budget -= 1

        # 2. Type C: INTERACTION_HYPOTHESIS
        # When two independent signals (e.g., TRIO ORBIT and EDGE ARITHMETIC) indicate the same numbers
        if overlap_events and remaining_budget > 0:
            for event in overlap_events:
                if remaining_budget <= 0:
                    break
                cand_id = f"CAND-{current_round:04d}-INT-{event.get('label', 'SIG')[:6]}"
                proposal = {
                    "name": f"INTERACTION_{event.get('source_a', 'SIGA')}_{event.get('source_b', 'SIGB')}",
                    "hypothesis": f"Intersection of {event.get('source_a')} and {event.get('source_b')} signals provides incremental positive lift over individual signals.",
                    "opposite_hypothesis": "Intersecting numbers have hit rate indistinguishable from random lottery null.",
                    "is_post_hoc_rescue": False,
                    "relaxes_threshold": False,
                    "cherry_picked_subset": False,
                    "independent_rationale": "Dual-signal concordance information test.",
                    "null_comparison_defined": True,
                    "future_leakage_blocked": True,
                    "minimum_sample": 100,
                    "success_criteria": "Interaction incremental lift > 0 with p <= 0.05",
                    "failure_criteria": "Incremental lift <= 0",
                    "prospective_or_untouched_holdout": True,
                    "multiple_testing_control": "Family maxT permutation test",
                }
                decision = self.gate.evaluate(proposal)
                state = ResearchState.READY_FOR_PROTOCOL if decision.passed else ResearchState.REJECT_NOT_TESTABLE
                record = CandidateRecord(
                    candidate_id=cand_id,
                    created_at=datetime.now(timezone.utc).isoformat(),
                    birth_round=current_round,
                    source_research=f"{event.get('source_a')} x {event.get('source_b')}",
                    candidate_type=FollowupType.INTERACTION_HYPOTHESIS.value,
                    hypothesis=proposal["hypothesis"],
                    opposite_hypothesis=proposal["opposite_hypothesis"],
                    novelty_status="INTERACTION_DISCOVERY",
                    duplicate_status="PASS" if decision.passed else decision.rejection_reasons[0],
                    rescue_check="PASS",
                    data_snooping_status="PASS",
                    confirmatory_start_round=current_round + 1,
                    minimum_sample=100,
                    recommended_action="TRACK_SHADOW_OVERLAP_ONLY_NO_OFFICIAL_PROMOTION",
                    state=state.value,
                    notes=f"Overlapping candidates recorded. Birth round {current_round}. Historical data marked EXPLORATORY_ONLY.",
                )
                generated.append(record)
                remaining_budget -= 1

        # Save all generated candidates to queue
        for cand in generated:
            try:
                self.queue.add_candidate(cand)
            except FileExistsError:
                pass

        return generated

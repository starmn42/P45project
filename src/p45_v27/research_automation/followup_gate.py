"""Follow-up Gate enforcing the 12 non-negotiable criteria for new hypotheses."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .duplicate_checker import DuplicateChecker

@dataclass
class GateCheckResult:
    check_number: int
    name: str
    passed: bool
    reason: str

@dataclass
class GateDecision:
    passed: bool
    verdict: str  # "PASS" or "NO_FOLLOWUP_RESEARCH"
    checks: list[GateCheckResult] = field(default_factory=list)
    rejection_reasons: list[str] = field(default_factory=list)

class FollowupGate:
    def __init__(self, duplicate_checker: DuplicateChecker | None = None):
        self.duplicate_checker = duplicate_checker or DuplicateChecker()

    def evaluate(self, candidate_proposal: dict[str, Any]) -> GateDecision:
        """Evaluates all 12 mandatory follow-up criteria."""
        checks = []

        # 1. Registry/Master exact duplicate check
        dup = self.duplicate_checker.check_duplicate(
            candidate_proposal.get("name", ""),
            candidate_proposal.get("hypothesis", "")
        )
        checks.append(GateCheckResult(
            1, "NO_EXACT_DUPLICATE", not dup["is_duplicate"],
            "PASS" if not dup["is_duplicate"] else f"Duplicate found in {dup['matched_source']}: {dup['reason']}"
        ))

        # 2. Failed research post-hoc rescue check
        is_rescue = candidate_proposal.get("is_post_hoc_rescue", False)
        checks.append(GateCheckResult(
            2, "NOT_POST_HOC_RESCUE", not is_rescue,
            "PASS" if not is_rescue else "Proposal attempts post-hoc rescue of a previously failed hypothesis."
        ))

        # 3. Threshold relaxation check
        is_relax = candidate_proposal.get("relaxes_threshold", False)
        checks.append(GateCheckResult(
            3, "NO_THRESHOLD_RELAXATION", not is_relax,
            "PASS" if not is_relax else "Proposal relaxes statistical significance thresholds."
        ))

        # 4. Best-subset selection check
        is_cherry = candidate_proposal.get("cherry_picked_subset", False)
        checks.append(GateCheckResult(
            4, "NO_CHERRY_PICKED_SUBSET", not is_cherry,
            "PASS" if not is_cherry else "Proposal selectively chooses a favorable subset of past outcomes."
        ))

        # 5. Independent logic existence
        has_logic = bool(candidate_proposal.get("independent_rationale"))
        checks.append(GateCheckResult(
            5, "INDEPENDENT_LOGIC_EXISTS", has_logic,
            "PASS" if has_logic else "Proposal lacks an independent theoretical or empirical rationale."
        ))

        # 6. Counter-hypothesis formulatable
        has_counter = bool(candidate_proposal.get("opposite_hypothesis"))
        checks.append(GateCheckResult(
            6, "COUNTER_HYPOTHESIS_FORMULATED", has_counter,
            "PASS" if has_counter else "Falsifiable opposite hypothesis is missing."
        ))

        # 7. Null/random comparison feasible
        has_null = bool(candidate_proposal.get("null_comparison_defined"))
        checks.append(GateCheckResult(
            7, "NULL_COMPARISON_FEASIBLE", has_null,
            "PASS" if has_null else "Well-defined fair null/random comparison is missing."
        ))

        # 8. Future leakage blocked
        leakage_blocked = candidate_proposal.get("future_leakage_blocked", True)
        checks.append(GateCheckResult(
            8, "FUTURE_LEAKAGE_BLOCKED", leakage_blocked,
            "PASS" if leakage_blocked else "Future outcome data leakage protection is not verified."
        ))

        # 9. Minimum sample configurable
        min_sample = candidate_proposal.get("minimum_sample", 0)
        checks.append(GateCheckResult(
            9, "MINIMUM_SAMPLE_CONFIGURED", min_sample >= 50,
            "PASS" if min_sample >= 50 else f"Minimum sample {min_sample} is below acceptable threshold (>=50)."
        ))

        # 10. Success/failure criteria pre-lockable
        has_criteria = bool(candidate_proposal.get("success_criteria")) and bool(candidate_proposal.get("failure_criteria"))
        checks.append(GateCheckResult(
            10, "CRITERIA_PRE_LOCKED", has_criteria,
            "PASS" if has_criteria else "Explicit objective success/failure criteria are missing."
        ))

        # 11. Untouched holdout or prospective verifiable
        is_prospective = candidate_proposal.get("prospective_or_untouched_holdout", True)
        checks.append(GateCheckResult(
            11, "UNTOUCHED_EVALUATION_PLAN", is_prospective,
            "PASS" if is_prospective else "Proposal lacks an untouched holdout or prospective verification design."
        ))

        # 12. Multiple testing control plan
        mt_control = bool(candidate_proposal.get("multiple_testing_control"))
        checks.append(GateCheckResult(
            12, "MULTIPLE_TESTING_CONTROLLED", mt_control,
            "PASS" if mt_control else "Multiple testing adjustment / control plan is missing."
        ))

        failures = [c.reason for c in checks if not c.passed]
        if failures:
            return GateDecision(
                passed=False,
                verdict="NO_FOLLOWUP_RESEARCH",
                checks=checks,
                rejection_reasons=failures,
            )
        return GateDecision(
            passed=True,
            verdict="PASS",
            checks=checks,
            rejection_reasons=[],
        )

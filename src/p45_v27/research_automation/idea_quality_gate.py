"""Idea Quality Gate V1.1 for P45 RESEARCH DISCOVERY AGENT V1.1.

Enforces:
1. NOVEL
2. NON_RESCUE
3. FALSIFIABLE
4. CLEAR_OPPOSITE
5. NULL_DEFINED
6. FUTURE_TESTABLE
7. DATA_AVAILABLE
8. MIN_SAMPLE_DEFINABLE
9. NO_LEAKAGE (strictly enforces earliest_eligible > discovery_end)
10. MULTIPLE_TESTING_CONTROLLABLE

Plus V1.1 Mandatory Semantic Novelty Gates for READY_FOR_PROTOCOL:
11. SEMANTIC_DUPLICATE_CHECK = PASS
12. FAILED_AXIS_RESCUE_CHECK = PASS
13. NOVELTY_EVIDENCE_EXISTS = YES
14. NOVELTY_JUSTIFICATION = VALID
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .novelty_checker import NoveltyChecker
from .semantic_novelty_checker import CandidateNoveltyAuditResult, NoveltyFinalVerdict, SemanticNoveltyCheckerV1_1

logger = logging.getLogger("p45.research_automation.quality_gate")

@dataclass
class QualityGateResult:
    passed: bool
    verdict: str  # "PASS" or "FAIL"
    ready_for_protocol: bool = False
    checks: dict[str, bool] = field(default_factory=dict)
    failed_checks: list[str] = field(default_factory=list)
    failure_reasons: dict[str, str] = field(default_factory=dict)

class IdeaQualityGate:
    """Evaluates an idea candidate against the 10 baseline gates + 4 semantic novelty gates."""

    def __init__(
        self,
        novelty_checker: NoveltyChecker | None = None,
        semantic_checker: SemanticNoveltyCheckerV1_1 | None = None,
    ):
        self.novelty_checker = novelty_checker or NoveltyChecker()
        self.semantic_checker = semantic_checker

    def evaluate(
        self,
        candidate_pkg: dict[str, Any],
        current_canonical_round: int,
        semantic_audit: CandidateNoveltyAuditResult | None = None,
    ) -> QualityGateResult:
        checks: dict[str, bool] = {}
        failure_reasons: dict[str, str] = {}

        # 1. NOVEL & 2. NON_RESCUE (Syntactic baseline)
        novelty_res = self.novelty_checker.check_candidate_novelty(candidate_pkg)
        if novelty_res.verdict == "REJECT_DUPLICATE":
            checks["NOVEL"] = False
            checks["NON_RESCUE"] = True
            failure_reasons["NOVEL"] = novelty_res.reason
        elif novelty_res.verdict == "REJECT_RESCUE":
            checks["NOVEL"] = False
            checks["NON_RESCUE"] = False
            failure_reasons["NON_RESCUE"] = novelty_res.reason
        else:
            checks["NOVEL"] = True
            checks["NON_RESCUE"] = True

        # 3. FALSIFIABLE
        failure_cond = candidate_pkg.get("failure_condition", "").strip()
        if len(failure_cond) >= 15:
            checks["FALSIFIABLE"] = True
        else:
            checks["FALSIFIABLE"] = False
            failure_reasons["FALSIFIABLE"] = "Failure condition is missing or too short to be mathematically falsifiable."

        # 4. CLEAR_OPPOSITE
        opp_hyp = candidate_pkg.get("opposite_hypothesis", "").strip()
        if len(opp_hyp) >= 15:
            checks["CLEAR_OPPOSITE"] = True
        else:
            checks["CLEAR_OPPOSITE"] = False
            failure_reasons["CLEAR_OPPOSITE"] = "Explicit opposite hypothesis is not defined."

        # 5. NULL_DEFINED
        null_def = candidate_pkg.get("null", "").strip()
        if len(null_def) >= 10:
            checks["NULL_DEFINED"] = True
        else:
            checks["NULL_DEFINED"] = False
            failure_reasons["NULL_DEFINED"] = "Rigorous mathematical null model is missing."

        # 6. FUTURE_TESTABLE
        fut_plan = candidate_pkg.get("future_validation_plan", "").strip()
        if len(fut_plan) >= 15:
            checks["FUTURE_TESTABLE"] = True
        else:
            checks["FUTURE_TESTABLE"] = False
            failure_reasons["FUTURE_TESTABLE"] = "Prospective future validation plan is not defined."

        # 7. DATA_AVAILABLE
        src_vars = candidate_pkg.get("source_variables", [])
        tgt_var = candidate_pkg.get("target_variable", "")
        if src_vars and tgt_var:
            checks["DATA_AVAILABLE"] = True
        else:
            checks["DATA_AVAILABLE"] = False
            failure_reasons["DATA_AVAILABLE"] = "Source variables or target variable not specified."

        # 8. MIN_SAMPLE_DEFINABLE
        min_samp = candidate_pkg.get("minimum_sample", 0)
        if isinstance(min_samp, int) and min_samp >= 10:
            checks["MIN_SAMPLE_DEFINABLE"] = True
        else:
            checks["MIN_SAMPLE_DEFINABLE"] = False
            failure_reasons["MIN_SAMPLE_DEFINABLE"] = f"Minimum sample size must be an integer >= 10, got {min_samp}."

        # 9. NO_LEAKAGE (checks earliest eligible confirmatory round > discovery end)
        discovery_end = candidate_pkg.get("discovery_data_end_round", 0)
        earliest_eligible = candidate_pkg.get("earliest_eligible_confirmatory_round") or candidate_pkg.get("confirmatory_start_round", 0)
        if discovery_end <= current_canonical_round and earliest_eligible > discovery_end:
            checks["NO_LEAKAGE"] = True
        else:
            checks["NO_LEAKAGE"] = False
            failure_reasons["NO_LEAKAGE"] = (
                f"Leakage detected: discovery_end={discovery_end}, earliest_eligible={earliest_eligible}, "
                f"canonical_round={current_canonical_round}. Earliest eligible confirmatory round must strictly exceed discovery end."
            )

        # 10. MULTIPLE_TESTING_CONTROLLABLE
        primary_metric = candidate_pkg.get("primary_metric", "").strip()
        if primary_metric:
            checks["MULTIPLE_TESTING_CONTROLLABLE"] = True
        else:
            checks["MULTIPLE_TESTING_CONTROLLABLE"] = False
            failure_reasons["MULTIPLE_TESTING_CONTROLLABLE"] = "Primary endpoint metric not isolated for multiplicity control."

        # Perform Semantic Audit if provided or if semantic_checker is available
        if semantic_audit is None and self.semantic_checker is not None:
            semantic_audit = self.semantic_checker.audit_candidate(candidate_pkg)

        # V1.1 Semantic Gates
        ready_for_protocol = False
        if semantic_audit is not None:
            # 11. SEMANTIC_DUPLICATE_CHECK
            if semantic_audit.final_verdict == NoveltyFinalVerdict.REJECT_DUPLICATE.value:
                checks["SEMANTIC_DUPLICATE_CHECK"] = False
                failure_reasons["SEMANTIC_DUPLICATE_CHECK"] = f"Semantic duplication detected: {', '.join(semantic_audit.exact_overlaps)}"
            else:
                checks["SEMANTIC_DUPLICATE_CHECK"] = True

            # 12. FAILED_AXIS_RESCUE_CHECK
            if semantic_audit.final_verdict == NoveltyFinalVerdict.REJECT_RESCUE.value:
                checks["FAILED_AXIS_RESCUE_CHECK"] = False
                failure_reasons["FAILED_AXIS_RESCUE_CHECK"] = f"Failed axis rescue detected: {', '.join(semantic_audit.failed_axis_rescues)}"
            else:
                checks["FAILED_AXIS_RESCUE_CHECK"] = True

            # 13. NOVELTY_EVIDENCE_EXISTS
            checks["NOVELTY_EVIDENCE_EXISTS"] = bool(semantic_audit.novelty_evidence_exists)

            # 14. NOVELTY_JUSTIFICATION
            if semantic_audit.final_verdict == NoveltyFinalVerdict.READY_FOR_PROTOCOL.value:
                checks["NOVELTY_JUSTIFICATION"] = True
            elif semantic_audit.final_verdict == NoveltyFinalVerdict.NEEDS_EVIDENCE.value:
                checks["NOVELTY_JUSTIFICATION"] = False
                failure_reasons["NOVELTY_JUSTIFICATION"] = "NEEDS_EVIDENCE: Structural differentiation is plausible but pre-specified evidence is incomplete."
            else:
                checks["NOVELTY_JUSTIFICATION"] = False
                failure_reasons["NOVELTY_JUSTIFICATION"] = semantic_audit.novelty_justification

            # READY_FOR_PROTOCOL requires all 14 checks to pass
            ready_for_protocol = all(checks.values()) and (semantic_audit.final_verdict == NoveltyFinalVerdict.READY_FOR_PROTOCOL.value)
        else:
            # When evaluated without a semantic checker/audit, baseline 10 quality checks determine passed,
            # but READY_FOR_PROTOCOL strictly requires semantic audit
            ready_for_protocol = False
            failure_reasons["NOVELTY_EVIDENCE_EXISTS"] = "Mandatory CANDIDATE_NOVELTY_EVIDENCE has not been evaluated."

        failed_checks = [name for name, passed in checks.items() if not passed]
        all_passed = len(failed_checks) == 0

        verdict = "PASS" if all_passed else "FAIL"
        return QualityGateResult(
            passed=all_passed,
            verdict=verdict,
            ready_for_protocol=ready_for_protocol,
            checks=checks,
            failed_checks=failed_checks,
            failure_reasons=failure_reasons,
        )

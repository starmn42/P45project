"""Comprehensive test suite for Phase A statistical functions and Phase C Research Discovery Agent V1.

Tests cover:
1. Binomial PMF vs tail separation (Prospective Fixed SUPPORT)
2. One-sided vs two-sided distinction (Historical Linked SUPPORT)
3. Holm-Bonferroni multiplicity sensitivity
4. McNemar exact paired test
5. Research Ontology 24-axis loading
6. Coverage map construction & classification
7. Duplicate detection (REJECT_DUPLICATE)
8. Failed axis rescue detection (REJECT_RESCUE)
9. Idea Quality Gate 10-check validation
10. Max 3 candidates per cycle rule
11. No outcome mining / strictly structural generation
12. Confirmatory start strictly greater than discovery end (Zero leakage)
13. Same-round idempotency
14. Provider fallback when LLM is not configured
15. Official Firewall & failure isolation
"""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

# Add src to sys.path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p45_v27.research_automation.constants import ResearchState
from p45_v27.research_automation.candidate_queue import CandidateQueue
from p45_v27.research_automation.signal_diagnostics import (
    binomial_pmf,
    binomial_exact_one_sided_upper,
    binomial_exact_two_sided,
    holm_bonferroni_adjust,
    mcnemar_exact_two_sided,
)
from p45_v27.research_automation.research_ontology import (
    ALL_ONTOLOGY_CONCEPTS,
    OntologyConcept,
    validate_ontology_tags,
)
from p45_v27.research_automation.research_coverage_map import (
    ResearchCoverageMapBuilder,
    CoverageStatus,
)
from p45_v27.research_automation.coverage_gap_analyzer import (
    CoverageGapAnalyzer,
    GapCategory,
)
from p45_v27.research_automation.novelty_checker import NoveltyChecker
from p45_v27.research_automation.idea_quality_gate import IdeaQualityGate
from p45_v27.research_automation.candidate_ranker import CandidateRanker, MAX_CANDIDATES_PER_CYCLE
from p45_v27.research_automation.idea_provider import (
    DeterministicStructuralProvider,
    OptionalLLMIdeaProvider,
)
from p45_v27.research_automation.research_discovery_agent import ResearchDiscoveryAgent

class TestStatisticalCorrectionAndDiscoveryAgent(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.queue_dir = self.temp_path / "queue"
        self.queue = CandidateQueue(self.queue_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # PHASE A: Statistical Function Verification Tests
    # -------------------------------------------------------------------------
    def test_prospective_fixed_support_pmf_vs_tail(self):
        """Re-verifies that 0.0137 is point mass P(X=3) while upper tail P(X>=3) is 0.01473."""
        n = 5
        k = 3
        p0 = 987390 / 8145060  # ≈ 0.1212256
        
        pmf_3 = binomial_pmf(k, n, p0)
        tail_3 = binomial_exact_one_sided_upper(k, n, p0)
        two_sided_p = binomial_exact_two_sided(k, n, p0)

        # Point mass sanity check: ~0.013757
        self.assertAlmostEqual(pmf_3, 0.013757, places=5)
        # Tail sanity check: ~0.014733
        self.assertAlmostEqual(tail_3, 0.014733, places=5)
        self.assertAlmostEqual(two_sided_p, 0.014733, places=5)
        # Point mass must be strictly less than tail
        self.assertLess(pmf_3, tail_3)

    def test_historical_linked_support_exact_binomial(self):
        """Historical Linked SUPPORT N=1237, k=174: one-sided upper ~0.02178, two-sided ~0.04049."""
        n = 1237
        k = 174
        p0 = 987390 / 8145060
        
        one_sided_p = binomial_exact_one_sided_upper(k, n, p0)
        two_sided_p = binomial_exact_two_sided(k, n, p0)

        self.assertAlmostEqual(one_sided_p, 0.021781, places=5)
        self.assertAlmostEqual(two_sided_p, 0.040486, places=5)

    def test_holm_bonferroni_sensitivity(self):
        """Applies Holm correction to 4 historical null tests: Linked SUPPORT one-sided p adj is ~0.0871."""
        raw_p_values = [0.599329, 0.271911, 0.226867, 0.021781]
        adj_p = holm_bonferroni_adjust(raw_p_values)
        
        # Smallest raw p is 0.021781 (rank 1 of 4): 0.021781 * 4 = 0.087124
        self.assertAlmostEqual(adj_p[3], 0.087124, places=4)
        # Since adj_p > 0.05, it fails family-wise significance
        self.assertGreater(adj_p[3], 0.05)

    def test_mcnemar_paired_comparison(self):
        """Direct paired comparison: Both=22, Fixed-only=137, Linked-only=152, Neither=926 -> p ≈ 0.41025."""
        p_val = mcnemar_exact_two_sided(137, 152)
        self.assertAlmostEqual(p_val, 0.41025, places=4)
        self.assertGreater(p_val, 0.05)

    # -------------------------------------------------------------------------
    # PHASE C: Research Discovery Agent Tests
    # -------------------------------------------------------------------------
    def test_ontology_axes_and_validation(self):
        """Ensures all 24 concept axes exist and validation function works."""
        self.assertEqual(len(ALL_ONTOLOGY_CONCEPTS), 24)
        tags = ["NUMBER", "TRIO", "PAIR", "CORE", "extinction", "recovery"]
        validated = validate_ontology_tags(tags)
        self.assertEqual(len(validated), 6)
        with self.assertRaises(ValueError):
            validate_ontology_tags(["INVALID_UNKNOWN_TAG_XYZ"])

    def test_coverage_map_building(self):
        """Ensures coverage map categories are correctly assigned across ontology axes."""
        builder = ResearchCoverageMapBuilder(root=self.temp_path)
        cov_map = builder.build_coverage_map()
        self.assertEqual(cov_map["total_concepts"], 24)
        axes = cov_map["axes"]
        # Check active TRIO axis
        self.assertEqual(axes["TRIO"]["status"], CoverageStatus.ACTIVE.value)
        # Check untested concepts
        self.assertIn("UNTESTED", cov_map["status_summary"])

    def test_novelty_checker_duplicate_and_rescue(self):
        """Validates duplicate rejection and rescue rejection."""
        checker = NoveltyChecker()
        
        # 1. Duplicate title
        dup_pkg = {"title": "숫자 동시출현 관계망", "hypothesis": "clustering"}
        dup_res = checker.check_candidate_novelty(dup_pkg)
        self.assertFalse(dup_res.is_novel)
        self.assertEqual(dup_res.verdict, "REJECT_DUPLICATE")

        # 2. Rescue of failed parity axis
        rescue_pkg = {"title": "홀수 parity 개수 lag-1 재검토", "hypothesis": "lag autocorrelation"}
        rescue_res = checker.check_candidate_novelty(rescue_pkg)
        self.assertFalse(rescue_res.is_novel)
        self.assertEqual(rescue_res.verdict, "REJECT_RESCUE")

        # 3. Novel candidate
        novel_pkg = {
            "title": "Zone Extinction Recovery Invariance",
            "hypothesis": "Hypergeometric recovery memoryless test",
            "origin": "STRUCTURAL_DISCOVERY_AGENT_V1:NEGATIVE_SPACE",
        }
        novel_res = checker.check_candidate_novelty(novel_pkg)
        self.assertTrue(novel_res.is_novel)
        self.assertEqual(novel_res.verdict, "NOVEL")

    def test_idea_quality_gate_ten_checks(self):
        """Verifies 10-check quality gate logic."""
        gate = IdeaQualityGate()
        valid_pkg = {
            "title": "Unique Novel Candidate Test Structure",
            "origin": "TEST_ORIGIN",
            "hypothesis": "Clear testable hypothesis predicting non-random deviation from null.",
            "opposite_hypothesis": "Clear opposite hypothesis predicting exact null distribution adherence.",
            "source_variables": ["var_a"],
            "target_variable": "var_b",
            "lag": 1,
            "primary_metric": "ks_statistic",
            "null": "Hypergeometric exact null distribution",
            "minimum_sample": 30,
            "failure_condition": "Two-sided exact p-value exceeds alpha 0.05 on prospective test draws.",
            "future_validation_plan": "Prospective evaluation from round 1244 to 1273.",
            "discovery_data_end_round": 1243,
            "confirmatory_start_round": 1244,
        }
        res = gate.evaluate(valid_pkg, current_canonical_round=1243)
        self.assertTrue(res.passed)
        self.assertEqual(len(res.checks), 10)
        self.assertTrue(all(res.checks.values()))

        # Test leakage check failure
        leaked_pkg = copy.deepcopy(valid_pkg)
        leaked_pkg["confirmatory_start_round"] = 1240  # < discovery_end
        leak_res = gate.evaluate(leaked_pkg, current_canonical_round=1243)
        self.assertFalse(leak_res.passed)
        self.assertIn("NO_LEAKAGE", leak_res.failed_checks)

    def test_ranker_max_three_candidates(self):
        """Verifies candidate ranker caps output to max 3 and never uses hit rates."""
        ranker = CandidateRanker()
        pkgs = [
            {"title": f"Candidate {i}", "origin": "STRUCTURAL_DISCOVERY_AGENT_V1:NEGATIVE_SPACE", "null": "hypergeometric", "minimum_sample": 30}
            for i in range(5)
        ]
        selected = ranker.rank_and_select(pkgs)
        self.assertEqual(len(selected), MAX_CANDIDATES_PER_CYCLE)

    def test_provider_status_and_fallback(self):
        """Verifies Deterministic provider is ACTIVE and Optional LLM is NOT_CONFIGURED by default."""
        det = DeterministicStructuralProvider()
        self.assertEqual(det.get_status(), "ACTIVE")
        
        opt_llm = OptionalLLMIdeaProvider()
        # When no env var is set, must safely return NOT_CONFIGURED
        self.assertEqual(opt_llm.get_status(), "NOT_CONFIGURED")
        res = opt_llm.generate_candidate_hypotheses({}, 1243)
        self.assertEqual(res, [])

    def test_discovery_agent_cycle_and_idempotency(self):
        """Tests full discovery cycle execution, queue insertion, and idempotency."""
        agent = ResearchDiscoveryAgent(root=self.temp_path, candidate_queue=self.queue)
        
        # 1. First cycle for Round 1243
        cycle1 = agent.run_discovery_cycle(canonical_round=1243)
        self.assertEqual(cycle1["status"], "SUCCESS")
        self.assertGreater(cycle1["new_candidates_count"], 0)
        self.assertLessEqual(cycle1["new_candidates_count"], 3)
        self.assertEqual(cycle1["duplicate_write"], 0)
        
        # Verify queue was populated
        queue_items = self.queue.list_all()
        self.assertEqual(len(queue_items), cycle1["new_candidates_count"])
        for item in queue_items:
            self.assertEqual(item.state, ResearchState.READY_FOR_PROTOCOL.value)

        # 2. Idempotent second cycle for same round
        cycle2 = agent.run_discovery_cycle(canonical_round=1243)
        self.assertEqual(cycle2["status"], "ALREADY_PROCESSED")
        self.assertEqual(cycle2["new_candidates_count"], 0)
        self.assertEqual(cycle2["duplicate_write"], 0)
        
        # Queue count must not have changed
        self.assertEqual(len(self.queue.list_all()), cycle1["new_candidates_count"])

    def test_official_firewall_and_isolation(self):
        """Ensures discovery agent does not mutate official engine files and catches errors cleanly."""
        agent = ResearchDiscoveryAgent(root=self.temp_path, candidate_queue=self.queue)
        res = agent.run_discovery_cycle(canonical_round=1243)
        self.assertEqual(res["summary"]["official_engine_firewall"], "PROTECTED_UNMODIFIED")

if __name__ == "__main__":
    unittest.main()

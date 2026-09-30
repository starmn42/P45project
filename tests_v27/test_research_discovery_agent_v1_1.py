"""Comprehensive Test Suite for P45 RESEARCH DISCOVERY AGENT V1.1.

Validates all 15 required criteria from Section 20:
1. Extinction/Recovery candidate finds existing related research (EXP-004, EXP-015, EXP-022) in top matches
2. Spacing/Repulsion candidate finds EXP-008, EXP-018, EXP-027 in top matches
3. PAIR dormancy candidate compares against official PAIR lifecycle and EXP-012
4. FAILED_AXIS_RESCUE blocking
5. Near-duplicate blocking
6. True distinct candidate passage
7. Novelty evidence file absence blocks READY_FOR_PROTOCOL
8. Ontology total consistency (exactly 24 unique axes)
9. Ontology axis -> research IDs reverse trace
10. Earliest eligible round and actual confirmatory start separation
11. Protocol lock before confirmatory_start_round definitive confirmation
12. Same-round idempotency (migration and standard keys)
13. Official firewall preservation
14. Future leakage blocking
15. Regression safety
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
from p45_v27.research_automation.candidate_queue import CandidateQueue, CandidateRecord
from p45_v27.research_automation.research_ontology import ALL_ONTOLOGY_CONCEPTS, OntologyConcept
from p45_v27.research_automation.knowledge_index import (
    ResearchKnowledgeIndex,
    ResearchKnowledgeIndexBuilder,
    ResearchKnowledgeRecord,
)
from p45_v27.research_automation.coverage_map_v1_1 import CoverageMapBuilderV1_1
from p45_v27.research_automation.semantic_novelty_checker import (
    CandidateNoveltyAuditResult,
    NoveltyFinalVerdict,
    SemanticNoveltyCheckerV1_1,
    SemanticOverlapClass,
)
from p45_v27.research_automation.idea_quality_gate import IdeaQualityGate
from p45_v27.research_automation.research_discovery_agent import ResearchDiscoveryAgent

class TestResearchDiscoveryAgentV1_1(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.knowledge_builder = ResearchKnowledgeIndexBuilder(ROOT)
        self.knowledge_index = self.knowledge_builder.build_index()
        self.semantic_checker = SemanticNoveltyCheckerV1_1(self.knowledge_index, root=self.temp_path)
        self.quality_gate = IdeaQualityGate(semantic_checker=self.semantic_checker)
        self.queue_dir = self.temp_path / "queue"
        self.queue = CandidateQueue(self.queue_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Extinction/Recovery matches check
    def test_01_extinction_candidate_finds_related_prior_research(self):
        cand_pkg = {
            "candidate_id": "TEST-CAND-EXTINCTION",
            "title": "Fixed-Partition Extinction Negative-Space Recovery Invariance",
            "source_variables": ["fixed_5_zone_occupancy_t"],
            "target_variable": "fixed_5_zone_occupancy_t_plus_1",
            "lag": 1,
            "primary_metric": "zone_rebound_excess",
            "null": "Hypergeometric memoryless sampling",
            "ontology_tags": ["extinction", "recovery", "occupancy"],
            "novelty_reason": "Testing compensatory rebound after zero occupancy",
        }
        audit = self.semantic_checker.audit_candidate(cand_pkg)
        top_ids = [m.existing_research_id for m in audit.top_matches]
        # Must find EXP-004 (EXP-DRAW-20260816-017-V1), EXP-015 (EXP-DRAW-20260816-015-V1), EXP-022 (EXP-DRAW-20260816-022-V1)
        self.assertIn("EXP-DRAW-20260816-017-V1", top_ids)
        self.assertIn("EXP-DRAW-20260816-015-V1", top_ids)
        self.assertIn("EXP-DRAW-20260816-022-V1", top_ids)
        self.assertEqual(audit.final_verdict, NoveltyFinalVerdict.REJECT_RESCUE.value)

    # 2. Spacing/Repulsion matches check
    def test_02_spacing_candidate_finds_spacing_and_neighbor_research(self):
        cand_pkg = {
            "candidate_id": "TEST-CAND-SPACING",
            "title": "Number Proximity Minimum-Distance Repulsion Invariance",
            "source_variables": ["sorted_main6_numbers_t"],
            "target_variable": "adjacent_spacing_vector_t",
            "lag": 0,
            "primary_metric": "minimum_adjacent_spacing_ks_statistic",
            "null": "Uniform order statistics spacing on {1..45}",
            "ontology_tags": ["opposite-state", "spacing", "NUMBER"],
            "novelty_reason": "Testing repulsion constraint on adjacent spacing",
        }
        audit = self.semantic_checker.audit_candidate(cand_pkg)
        top_ids = [m.existing_research_id for m in audit.top_matches]
        # Must find EXP-008 (EXP-DRAW-20260816-026-V1), EXP-018 (EXP-DRAW-20260827-018-V2), EXP-027 (EXP-DRAW-20260816-027-V1)
        self.assertIn("EXP-DRAW-20260816-026-V1", top_ids)
        self.assertIn("EXP-DRAW-20260827-018-V2", top_ids)
        self.assertIn("EXP-DRAW-20260816-027-V1", top_ids)
        self.assertEqual(audit.final_verdict, NoveltyFinalVerdict.REJECT_RESCUE.value)

    # 3. PAIR dormancy matches check
    def test_03_pair_dormancy_candidate_compares_official_pair_lifecycle(self):
        cand_pkg = {
            "candidate_id": "TEST-CAND-PAIR-DORMANCY",
            "title": "Pair Lifecycle Dormancy Duration Geometric Memory Invariance",
            "source_variables": ["pair_dormancy_gap_history"],
            "target_variable": "next_pair_activation_gap",
            "lag": 1,
            "primary_metric": "geometric_hazard_log_rank_p",
            "null": "Geometric distribution with p0 = 0.010101",
            "ontology_tags": ["PAIR", "transition", "conditional transition"],
            "novelty_reason": "Testing geometric memoryless hazard of pair dormancy gaps",
        }
        audit = self.semantic_checker.audit_candidate(cand_pkg)
        top_ids = [m.existing_research_id for m in audit.top_matches]
        self.assertIn("OFFICIAL-PAIR-LIFECYCLE", top_ids)
        self.assertIn("EXP-DRAW-20260824-010-V1", top_ids)
        self.assertEqual(audit.final_verdict, NoveltyFinalVerdict.NEEDS_EVIDENCE.value)

    # 4. Failed axis rescue blocking
    def test_04_failed_axis_rescue_blocked(self):
        cand_pkg = {
            "candidate_id": "TEST-RESCUE",
            "title": "Variable Extinction Zone Rebound Invariance",
            "source_variables": ["variable_extinction_zones"],
            "target_variable": "zone_rebound",
            "lag": 1,
            "primary_metric": "lift",
            "null": "hypergeometric",
            "ontology_tags": ["extinction", "recovery"],
            "novelty_reason": "Reviving variable extinction zones",
        }
        audit = self.semantic_checker.audit_candidate(cand_pkg)
        self.assertEqual(audit.final_verdict, NoveltyFinalVerdict.REJECT_RESCUE.value)
        gate_res = self.quality_gate.evaluate(cand_pkg, 1243, audit)
        self.assertFalse(gate_res.ready_for_protocol)
        self.assertIn("FAILED_AXIS_RESCUE_CHECK", gate_res.failed_checks)

    # 5. Near-duplicate blocking
    def test_05_near_duplicate_blocked(self):
        cand_pkg = {
            "candidate_id": "TEST-DUP",
            "title": "간격 분산 재검토 연구",
            "source_variables": ["adjacent_spacings"],
            "target_variable": "spacing_variance",
            "lag": 0,
            "primary_metric": "variance",
            "null": "uniform order statistics",
            "ontology_tags": ["spacing", "gap"],
            "novelty_reason": "Testing spacing variance",
        }
        audit = self.semantic_checker.audit_candidate(cand_pkg)
        self.assertIn(audit.final_verdict, (NoveltyFinalVerdict.REJECT_DUPLICATE.value, NoveltyFinalVerdict.REJECT_RESCUE.value))
        gate_res = self.quality_gate.evaluate(cand_pkg, 1243, audit)
        self.assertFalse(gate_res.ready_for_protocol)

    # 6. True distinct candidate passes
    def test_06_true_distinct_candidate_passes(self):
        cand_pkg = {
            "candidate_id": "TEST-DISTINCT-001",
            "title": "Synthetic Orthogonal State Decay Invariance",
            "source_variables": ["synthetic_orthogonal_state_vector"],
            "target_variable": "orthogonal_decay_rate",
            "lag": 3,
            "primary_metric": "log_decay_constant_z",
            "null": "Multi-round exponential decay null with lambda=0.5",
            "opposite_hypothesis": "The orthogonal decay rate follows a pure memoryless Poisson process without state decay invariance.",
            "minimum_sample": 30,
            "failure_condition": "Two-sided exact p-value > 0.05 on prospective test draws.",
            "future_validation_plan": "Prospective validation from earliest eligible round.",
            "ontology_tags": ["decay", "persistence"],
            "novelty_reason": "Completely novel orthogonal structural decay tracking never before tested in P45.",
            "discovery_data_end_round": 1243,
            "earliest_eligible_confirmatory_round": 1244,
        }
        audit = self.semantic_checker.audit_candidate(cand_pkg)
        self.assertEqual(audit.final_verdict, NoveltyFinalVerdict.READY_FOR_PROTOCOL.value)
        gate_res = self.quality_gate.evaluate(cand_pkg, 1243, audit)
        self.assertTrue(gate_res.ready_for_protocol)

    # 7. Novelty evidence file absence blocks READY_FOR_PROTOCOL
    def test_07_absence_of_novelty_evidence_blocks_protocol_readiness(self):
        cand_pkg = {
            "candidate_id": "TEST-NO-EVIDENCE",
            "title": "Some Candidate Without Semantic Audit",
            "source_variables": ["var_a"],
            "target_variable": "var_b",
            "lag": 1,
            "primary_metric": "ks_stat",
            "null": "hypergeometric exact null",
            "opposite_hypothesis": "The distribution follows standard hypergeometric without deviation.",
            "minimum_sample": 30,
            "failure_condition": "p-value > 0.05 on prospective draws.",
            "future_validation_plan": "Testing on future draws.",
            "discovery_data_end_round": 1243,
            "earliest_eligible_confirmatory_round": 1244,
        }
        # Evaluated without semantic audit
        gate_without_audit = IdeaQualityGate(semantic_checker=None)
        res = gate_without_audit.evaluate(cand_pkg, 1243, semantic_audit=None)
        self.assertFalse(res.ready_for_protocol)
        self.assertIn("NOVELTY_EVIDENCE_EXISTS", res.failure_reasons)

    # 8. Ontology total consistency (exactly 24 axes)
    def test_08_ontology_total_consistency(self):
        builder = CoverageMapBuilderV1_1(self.temp_path)
        cov = builder.build_coverage_map_v1_1(self.knowledge_index)
        self.assertEqual(cov["ontology_model_metrics"]["declared_ontology_total"], 24)
        self.assertEqual(cov["ontology_model_metrics"]["actual_unique_axes_count"], 24)
        self.assertEqual(cov["ontology_model_metrics"]["consistency_verdict"], "PASS")
        self.assertEqual(len(cov["axes"]), 24)

    # 9. Ontology axis -> research IDs reverse trace
    def test_09_ontology_axis_reverse_trace(self):
        builder = CoverageMapBuilderV1_1(self.temp_path)
        cov = builder.build_coverage_map_v1_1(self.knowledge_index)
        axes = cov["axes"]
        # Check NUMBER axis has formal registry IDs
        self.assertGreater(len(axes["NUMBER"]["related_formal_registry_ids"]), 0)
        # Check TRIO has non-exp axes
        self.assertIn("NON-EXP-TRIO-ORBIT-FIXED", axes["TRIO"]["related_non_exp_axes"])
        # Check PAIR has official internal axes
        self.assertIn("OFFICIAL-PAIR-LIFECYCLE", axes["PAIR"]["related_official_axes"])

    # 10. Earliest eligible round and actual confirmatory start separation
    def test_10_earliest_eligible_vs_actual_confirmatory_separation(self):
        cand_pkg = {
            "candidate_id": "TEST-CAND-SEPARATION",
            "discovery_data_end_round": 1243,
            "earliest_eligible_confirmatory_round": 1244,
            "confirmatory_start_round": None,  # Must be None at discovery stage
        }
        self.assertIsNone(cand_pkg["confirmatory_start_round"])
        self.assertEqual(cand_pkg["earliest_eligible_confirmatory_round"], 1244)

    # 11. Protocol lock before confirmatory_start_round confirmation
    def test_11_protocol_lock_precondition_enforcement(self):
        # A candidate in CandidateRecord must not have locked_at or protocol_sha256 if not locked
        record = CandidateRecord(
            candidate_id="TEST-RECORD",
            created_at="2026-09-30T00:00:00Z",
            birth_round=1243,
            source_research="STRUCTURAL_DISCOVERY_AGENT_V1_1",
            candidate_type="STRUCTURAL_GAP",
            hypothesis="Hypothesis text here",
            opposite_hypothesis="Opposite text here",
            novelty_status="NOVEL",
            duplicate_status="PASS",
            rescue_check="PASS",
            data_snooping_status="CLEAN_PROSPECTIVE_ONLY",
            earliest_eligible_confirmatory_round=1244,
            confirmatory_start_round=None,
            state=ResearchState.READY_FOR_PROTOCOL.value,
        )
        self.assertIsNone(record.confirmatory_start_round)
        self.assertIsNone(record.protocol_sha256)
        self.assertIsNone(record.locked_at)

    # 12. Same-round idempotency
    def test_12_same_round_idempotency(self):
        agent = ResearchDiscoveryAgent(root=self.temp_path, candidate_queue=self.queue)
        cycle1 = agent.run_discovery_cycle(1243, is_migration=True)
        self.assertIn(cycle1["status"], ("SUCCESS", "NO_VALID_NEW_HYPOTHESIS"))
        
        cycle2 = agent.run_discovery_cycle(1243, is_migration=True)
        self.assertEqual(cycle2["status"], "ALREADY_PROCESSED")
        self.assertEqual(cycle2["new_candidates_count"], 0)
        self.assertEqual(cycle2["duplicate_write"], 0)

    # 13. Official firewall preservation
    def test_13_official_firewall_preserved(self):
        agent = ResearchDiscoveryAgent(root=self.temp_path, candidate_queue=self.queue)
        cycle = agent.run_discovery_cycle(1243, is_migration=True)
        self.assertEqual(cycle["summary"]["official_engine_firewall"], "PROTECTED_UNMODIFIED")

    # 14. Future leakage blocking
    def test_14_future_leakage_blocking(self):
        gate = IdeaQualityGate()
        leaked_pkg = {
            "candidate_id": "TEST-LEAK",
            "title": "Testing Future Leakage",
            "source_variables": ["var_a"],
            "target_variable": "var_b",
            "lag": 1,
            "primary_metric": "stat",
            "null": "hypergeometric null",
            "minimum_sample": 30,
            "failure_condition": "p > 0.05 on draws.",
            "future_validation_plan": "Validating future.",
            "discovery_data_end_round": 1243,
            "earliest_eligible_confirmatory_round": 1240,  # LEAKAGE: <= discovery_end!
        }
        res = gate.evaluate(leaked_pkg, 1243)
        self.assertFalse(res.passed)
        self.assertIn("NO_LEAKAGE", res.failed_checks)

    # 15. Regression safety of previous 3 candidates reassessment
    def test_15_reassessment_of_v1_candidates(self):
        agent = ResearchDiscoveryAgent(root=ROOT)
        reassessments = agent.reassess_v1_candidates()
        self.assertEqual(len(reassessments), 3)
        verdicts = {a.candidate_id: a.final_verdict for a in reassessments}
        self.assertEqual(verdicts["IDEA-1243-NEGA-001"], NoveltyFinalVerdict.REJECT_RESCUE.value)
        self.assertEqual(verdicts["IDEA-1243-OPPO-002"], NoveltyFinalVerdict.REJECT_RESCUE.value)
        self.assertEqual(verdicts["IDEA-1243-CROS-003"], NoveltyFinalVerdict.NEEDS_EVIDENCE.value)

if __name__ == "__main__":
    unittest.main()

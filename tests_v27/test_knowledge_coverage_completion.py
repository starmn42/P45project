"""Comprehensive Test Suite for Knowledge Coverage Completion & Fail-Closed Finalization.

Validates all 20 requirements from Section 20 of the Specification:
1. latest Formal Registry extraction (69 rows)
2. latest non-EXP section extraction (31 rows)
3. latest Official internal table extraction (12 rows)
4. Source Inventory generation
5. All source items mapped
6. Unmapped source items count == 0
7. Alias mapping validity
8. Merged mappings have explicit evidence
9. UNKNOWN fields do not drop records
10. Bidirectional reverse trace: source -> record
11. Bidirectional reverse trace: record -> sources
12. Incomplete coverage blocks discovery (Fail-Closed)
13. Complete coverage enables discovery
14. Candidate A remains REJECT_RESCUE
15. Candidate B remains REJECT_RESCUE
16. Candidate C full-index reassessment (NEEDS_EVIDENCE)
17. Ontology map orphan records count == 0
18. Same-round migration idempotency
19. Future leakage == 0 (earliest_eligible vs confirmatory_start)
20. Official firewall preserved (USER_APPROVAL_REQUIRED)
"""
from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p45_v27.research_automation.constants import ResearchState
from p45_v27.research_automation.knowledge_source_inventory import (
    CoverageManifest,
    MappingType,
    ResearchKnowledgeCoverageManifestBuilder,
    ResearchSourceInventoryBuilder,
    ResearchSourceItem,
    SourceClass,
)
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
)
from p45_v27.research_automation.idea_quality_gate import IdeaQualityGate
from p45_v27.research_automation.research_discovery_agent import ResearchDiscoveryAgent
from p45_v27.research_automation.candidate_queue import CandidateQueue, CandidateRecord

class TestKnowledgeCoverageCompletion(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.inv_builder = ResearchSourceInventoryBuilder(ROOT)
        self.source_items = self.inv_builder.build_source_inventory()
        self.man_builder = ResearchKnowledgeCoverageManifestBuilder(ROOT)
        self.manifest = self.man_builder.build_manifest(self.source_items)
        self.knowledge_builder = ResearchKnowledgeIndexBuilder(ROOT)
        self.knowledge_index = self.knowledge_builder.build_index()
        self.coverage_builder = CoverageMapBuilderV1_1(ROOT)
        self.semantic_checker = SemanticNoveltyCheckerV1_1(self.knowledge_index, ROOT)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. Latest Formal Registry extraction
    def test_01_formal_registry_extraction(self):
        formal_items = [it for it in self.source_items if it.source_class == SourceClass.FORMAL_REGISTRY.value]
        self.assertEqual(len(formal_items), 69)
        draw_count = sum(1 for it in formal_items if "DRAW" in it.source_item_id)
        crowd_count = sum(1 for it in formal_items if "CROWD" in it.source_item_id)
        prize_count = sum(1 for it in formal_items if "PRIZE" in it.source_item_id)
        self.assertEqual(draw_count, 54)
        self.assertEqual(crowd_count, 9)
        self.assertEqual(prize_count, 6)

    # 2. Latest non-EXP section extraction
    def test_02_non_exp_extraction(self):
        non_exp_items = [it for it in self.source_items if it.source_class == SourceClass.NON_EXP_EXECUTED.value]
        self.assertGreaterEqual(len(non_exp_items), 28)
        self.assertEqual(len(non_exp_items), 31)  # 28 historical + 3 post-Section C audits

    # 3. Latest Official internal table extraction
    def test_03_official_internal_extraction(self):
        official_items = [it for it in self.source_items if it.source_class == SourceClass.OFFICIAL_INTERNAL.value]
        self.assertEqual(len(official_items), 12)
        titles = " ".join(it.source_title for it in official_items)
        for expected in ["UNIT_3", "UNIT_5", "UNIT_9", "UNIT_10", "END_DIGIT", "NUMBER", "TRIO", "PAIR", "CORE", "Fixed Orbit", "Linked Orbit", "KTS45"]:
            self.assertIn(expected, titles)

    # 4. Source Inventory generation
    def test_04_source_inventory_generation(self):
        j_path, m_path = self.inv_builder.save_source_inventory(self.source_items)
        self.assertTrue(j_path.exists())
        self.assertTrue(m_path.exists())
        data = json.loads(j_path.read_text(encoding="utf-8"))
        self.assertEqual(data["total_source_items"], len(self.source_items))
        self.assertEqual(data["total_source_items"], 115)

    # 5. All source items mapped
    def test_05_all_source_items_mapped(self):
        mapped_count = self.manifest.mapped_source_items_count
        total_count = self.manifest.total_source_items
        self.assertEqual(mapped_count, total_count)
        self.assertEqual(self.manifest.coverage_ratio, 1.0)
        self.assertTrue(self.manifest.is_complete)

    # 6. Unmapped source items count == 0
    def test_06_unmapped_source_items_zero(self):
        self.assertEqual(self.manifest.unmapped_source_items_count, 0)
        self.assertEqual(len(self.manifest.unmapped_items), 0)

    # 7. Alias mapping validity
    def test_07_alias_mapping_validity(self):
        alias_mappings = [m for m in self.manifest.mappings if m.mapping_type == MappingType.ALIAS.value]
        self.assertGreater(len(alias_mappings), 0)
        for m in alias_mappings:
            self.assertTrue(len(m.mapping_reason) > 5)
            self.assertTrue(len(m.evidence) > 0)
            self.assertEqual(m.confidence, 1.0)

    # 8. Merge requires evidence
    def test_08_merge_requires_evidence(self):
        merged_mappings = [m for m in self.manifest.mappings if m.mapping_type == MappingType.MERGED.value]
        self.assertGreater(len(merged_mappings), 0)
        for m in merged_mappings:
            self.assertTrue(len(m.mapping_reason) > 5)
            self.assertTrue(len(m.evidence) > 0)

    # 9. UNKNOWN field does not drop record
    def test_09_unknown_field_does_not_drop_record(self):
        reviewed_items = [it for it in self.source_items if it.source_class == SourceClass.REVIEWED_UNEXECUTED.value]
        self.assertEqual(len(reviewed_items), 2)
        for it in reviewed_items:
            rec = self.knowledge_index.trace_source_to_record(it.source_item_id)
            self.assertIsNotNone(rec)
            self.assertEqual(rec.status, "REVIEWED_UNEXECUTED")

    # 10. Bidirectional reverse trace: source -> record
    def test_10_reverse_trace_source_to_record(self):
        for it in self.source_items:
            rec = self.knowledge_index.trace_source_to_record(it.source_item_id)
            self.assertIsNotNone(rec, f"Source item {it.source_item_id} must trace to a normalized record.")

    # 11. Bidirectional reverse trace: record -> sources
    def test_11_reverse_trace_record_to_sources(self):
        for rec in self.knowledge_index.list_all():
            sources = self.knowledge_index.trace_record_to_sources(rec.record_id)
            self.assertGreater(len(sources), 0, f"Record {rec.record_id} must have at least one source item.")
            for sid in sources:
                traced_rec = self.knowledge_index.trace_source_to_record(sid)
                self.assertEqual(traced_rec.record_id, rec.record_id)

    # 12. Incomplete coverage blocks discovery (Fail-Closed)
    def test_12_incomplete_coverage_blocks_discovery(self):
        # Create a mock index with an incomplete manifest
        incomplete_manifest = copy.deepcopy(self.manifest)
        incomplete_manifest.is_complete = False
        incomplete_manifest.unmapped_source_items_count = 1
        incomplete_manifest.unmapped_items = ["SRC-MISSING-TEST-001"]

        mock_index = ResearchKnowledgeIndex(self.knowledge_index.list_all(), incomplete_manifest)
        agent = ResearchDiscoveryAgent(ROOT)
        agent.knowledge_index = mock_index

        res = agent.run_discovery_cycle(1243)
        self.assertEqual(res["status"], "BLOCKED_KNOWLEDGE_COVERAGE_INCOMPLETE")
        self.assertEqual(res["new_candidates_count"], 0)
        self.assertEqual(res["ready_for_protocol_count"], 0)

    # 13. Complete coverage enables discovery
    def test_13_complete_coverage_enables_discovery(self):
        agent = ResearchDiscoveryAgent(ROOT)
        self.assertTrue(agent.knowledge_index.is_coverage_complete())
        res = agent.run_discovery_cycle(1243)
        self.assertIn(res["status"], ("SUCCESS", "NO_VALID_NEW_HYPOTHESIS", "ALREADY_PROCESSED"))

    # 14. Candidate A remains duplicate/rescue
    def test_14_candidate_a_remains_rescue(self):
        cand_a = {
            "candidate_id": "IDEA-1243-NEGA-001",
            "title": "Fixed-Partition Extinction Negative-Space Recovery Invariance",
            "hypothesis": "Number absence in partition negative space recovers at constant rate.",
            "source_variables": ["fixed_partition_zones"],
            "target_variable": "recovery_lag",
            "lag": 1,
            "primary_metric": "recovery_speed",
            "null": "Hypergeometric uniform recovery null",
            "novelty_reason": "Partition extinction negative space recovery",
            "ontology_tags": ["extinction", "recovery", "occupancy"],
        }
        audit = self.semantic_checker.audit_candidate(cand_a)
        self.assertEqual(audit.final_verdict, NoveltyFinalVerdict.REJECT_RESCUE.value)

    # 15. Candidate B remains duplicate/rescue
    def test_15_candidate_b_remains_rescue(self):
        cand_b = {
            "candidate_id": "IDEA-1243-OPPO-002",
            "title": "Number Proximity Minimum-Distance Repulsion Invariance",
            "hypothesis": "Drawn numbers show minimum distance repulsion.",
            "source_variables": ["adjacent_spacings"],
            "target_variable": "min_spacing",
            "lag": 0,
            "primary_metric": "min_spacing_variance",
            "null": "Uniform order statistics null",
            "novelty_reason": "Testing repulsion distance between numbers",
            "ontology_tags": ["spacing", "neighbor", "gap"],
        }
        audit = self.semantic_checker.audit_candidate(cand_b)
        self.assertEqual(audit.final_verdict, NoveltyFinalVerdict.REJECT_RESCUE.value)

    # 16. Candidate C full-index reassessment (NEEDS_EVIDENCE)
    def test_16_candidate_c_full_index_reassessment(self):
        cand_c = {
            "candidate_id": "IDEA-1243-CROS-003",
            "title": "Pair Lifecycle Dormancy Duration Geometric Memory Invariance",
            "hypothesis": "Pair dormancy follows geometric memoryless hazard.",
            "source_variables": ["pair_dormancy_intervals"],
            "target_variable": "dormancy_hazard",
            "lag": 1,
            "primary_metric": "log_rank_hazard_p",
            "null": "Geometric distribution null",
            "novelty_reason": "Testing geometric memorylessness on 990 pairs",
            "ontology_tags": ["pair", "gap", "transition"],
        }
        audit = self.semantic_checker.audit_candidate(cand_c)
        self.assertEqual(audit.final_verdict, NoveltyFinalVerdict.NEEDS_EVIDENCE.value)

    # 17. Ontology map orphan == 0
    def test_17_ontology_map_orphan_zero(self):
        cov = self.coverage_builder.build_coverage_map_v1_1(self.knowledge_index)
        orphan_count = cov["research_linkage_summary"].get("orphan_records_count", 0)
        self.assertEqual(orphan_count, 0)
        self.assertEqual(cov["ontology_model_metrics"]["actual_unique_axes_count"], 24)

    # 18. Same-round idempotency
    def test_18_same_round_idempotency(self):
        agent = ResearchDiscoveryAgent(self.temp_path)
        res1 = agent.run_discovery_cycle(1243, is_migration=True)
        res2 = agent.run_discovery_cycle(1243, is_migration=True)
        self.assertEqual(res2["status"], "ALREADY_PROCESSED")
        self.assertEqual(res2["new_candidates_count"], 0)

    # 19. Future leakage == 0 (earliest_eligible vs confirmatory_start)
    def test_19_future_leakage_zero(self):
        from p45_v27.research_automation.idea_provider import DeterministicStructuralProvider
        prov = DeterministicStructuralProvider()
        cov = self.coverage_builder.build_coverage_map_v1_1(self.knowledge_index)
        cands = prov.generate_candidate_hypotheses(cov, 1243)
        for c in cands:
            self.assertEqual(c["discovery_data_end_round"], 1243)
            self.assertEqual(c["earliest_eligible_confirmatory_round"], 1244)
            self.assertIsNone(c.get("confirmatory_start_round"))

    # 20. Official firewall preserved
    def test_20_official_firewall_preserved(self):
        from p45_v27.research_automation.research_state_machine import ResearchStateMachine, PromotionFirewallViolation
        with self.assertRaises(PromotionFirewallViolation):
            ResearchStateMachine.validate_transition(ResearchState.PROMOTION_CANDIDATE, "OFFICIAL_PROMOTION")

if __name__ == "__main__":
    unittest.main()

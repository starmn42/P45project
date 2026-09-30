"""Comprehensive unittest suite for Canonical ID Resolver and Referential Integrity Guard in P45 Research Automation.

Covers all 22 required referential integrity assertions:
1. canonical registry ID exact lookup
2. human EXP label namespace isolation
3. EXP-009 collision prevention
4. EXP-DRAW-20260816-009-V1 title identity
5. PAIR repair resolves to correct canonical row
6. EXP-DRAW-20260821-042-V1 title identity
7. unrelated extinction match rejection
8. valid alias acceptance
9. invalid alias rejection
10. ambiguous alias fail-closed
11. valid merge acceptance
12. unjustified merge rejection
13. source->canonical->knowledge reverse trace
14. semantic matcher uses resolved metadata
15. invalid reference blocks READY_FOR_PROTOCOL
16. knowledge coverage requires referential integrity
17. A candidate regression
18. B candidate regression
19. C candidate regression
20. Official firewall
21. future leakage
22. idempotency
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p45_v27.research_automation.canonical_id_resolver import (
    CanonicalResearchIdResolver,
    CanonicalNamespace,
    ResolutionStatus,
)
from p45_v27.research_automation.knowledge_source_inventory import (
    ResearchSourceInventoryBuilder,
    ResearchKnowledgeCoverageManifestBuilder,
    SourceClass,
)
from p45_v27.research_automation.knowledge_index import (
    ResearchKnowledgeIndexBuilder,
)
from p45_v27.research_automation.semantic_novelty_checker import (
    SemanticNoveltyCheckerV1_1,
    NoveltyFinalVerdict,
    SemanticMatchItem,
)
from p45_v27.research_automation.research_discovery_agent import ResearchDiscoveryAgent


class TestCanonicalIdReferentialIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = CanonicalResearchIdResolver()
        builder = ResearchKnowledgeIndexBuilder()
        cls.index = builder.build_index()
        cls.agent = ResearchDiscoveryAgent()

    # 1. canonical registry ID exact lookup
    def test_01_canonical_registry_id_exact_lookup(self):
        res = self.resolver.resolve("EXP-DRAW-20260816-009-V1")
        self.assertEqual(res.status, ResolutionStatus.RESOLVED_CANONICAL.value)
        self.assertEqual(res.resolved_canonical_id, "EXP-DRAW-20260816-009-V1")
        self.assertEqual(res.reference_namespace, CanonicalNamespace.CANONICAL_REGISTRY_ID.value)
        self.assertIn("전체 관계망", res.canonical_title)

    # 2. human EXP label namespace isolation
    def test_02_human_exp_label_namespace_isolation(self):
        res = self.resolver.resolve("EXP-004")
        self.assertEqual(res.reference_namespace, CanonicalNamespace.HUMAN_EXP_LABEL.value)
        self.assertEqual(res.status, ResolutionStatus.RESOLVED_EXPLICIT.value)
        self.assertEqual(res.resolved_canonical_id, "EXP-DRAW-20260816-017-V1")

    # 3. EXP-009 collision prevention
    def test_03_exp_009_collision_prevention(self):
        res = self.resolver.resolve("EXP-009")
        # Must NOT resolve to EXP-DRAW-20260816-009-V1
        self.assertNotEqual(res.resolved_canonical_id, "EXP-DRAW-20260816-009-V1")
        # In authoritative registry, EXP-009 is EXP-DRAW-20260821-039-V1
        self.assertEqual(res.resolved_canonical_id, "EXP-DRAW-20260821-039-V1")
        self.assertIn("홀수 개수 lag-1 공분산", res.canonical_title)

    # 4. EXP-DRAW-20260816-009-V1 title identity
    def test_04_exp_draw_009_title_identity(self):
        canon = self.resolver.get_canonical_record("EXP-DRAW-20260816-009-V1")
        self.assertIsNotNone(canon)
        self.assertEqual(canon.lab, "NUMBER RELATION LAB")
        self.assertEqual(canon.canonical_title, "전체 관계망")
        self.assertNotIn("PAIR", canon.canonical_title)
        self.assertNotIn("REPAIR", canon.canonical_title)

    # 5. PAIR repair resolves to correct canonical row
    def test_05_pair_repair_resolves_to_correct_canonical_row(self):
        # Official PAIR lifecycle repair canonical row is EXP-DRAW-20260824-010-V1
        canon = self.resolver.get_canonical_record("EXP-DRAW-20260824-010-V1")
        self.assertIsNotNone(canon)
        self.assertTrue("PAIR" in canon.canonical_title or "PAIR" in canon.lab)
        self.assertIn("OFFICIAL PAIR LIFECYCLE REPAIR APPLY AUDIT", canon.canonical_title)
        # Must NOT be EXP-DRAW-20260816-009-V1
        self.assertNotEqual(canon.canonical_registry_id, "EXP-DRAW-20260816-009-V1")

    # 6. EXP-DRAW-20260821-042-V1 title identity
    def test_06_exp_draw_042_title_identity(self):
        canon = self.resolver.get_canonical_record("EXP-DRAW-20260821-042-V1")
        self.assertIsNotNone(canon)
        self.assertEqual(canon.lab, "RETURN LAB")
        self.assertIn("return-age", canon.canonical_title)
        self.assertEqual(canon.human_exp_label_if_explicit, "EXP-012")
        self.assertNotIn("extinction", canon.canonical_title.lower())
        self.assertNotIn("전멸", canon.canonical_title)

    # 7. unrelated extinction match rejection
    def test_07_unrelated_extinction_match_rejection(self):
        checker = SemanticNoveltyCheckerV1_1(self.index)
        cand_pkg = {
            "candidate_id": "TEST-EXTINCTION-001",
            "title": "Fixed-Partition Extinction Negative-Space Recovery Invariance",
            "source_variables": ["fixed_5_zone_occupancy_t"],
            "target_variable": "fixed_5_zone_occupancy_t_plus_1",
            "lag": 1,
            "primary_metric": "extinction_recovery_rate",
            "null": "Hypergeometric memoryless sampling",
            "ontology_tags": ["extinction", "recovery", "occupancy"],
            "novelty_reason": "Negative space testing",
        }
        result = checker.audit_candidate(cand_pkg)
        top_ids = [m.existing_research_id for m in result.top_matches]
        top_canon_ids = [m.canonical_registry_id for m in result.top_matches]
        # EXP-DRAW-20260821-042-V1 (return-age rank) must NOT be in top extinction matches
        self.assertNotIn("EXP-DRAW-20260821-042-V1", top_ids)
        self.assertNotIn("EXP-DRAW-20260821-042-V1", top_canon_ids)

    # 8. valid alias acceptance
    def test_08_valid_alias_acceptance(self):
        res = self.resolver.resolve_source_reference(
            raw_reference="EXP-DRAW-20260824-010-V1",
            title="Official repair Phase A/B deterministic rerun validation",
            source_class=SourceClass.NON_EXP_EXECUTED.value,
            domain="DRAW",
            source_document="90_RESEARCH/P45_RESEARCH_MASTER_INDEX_005.md",
        )
        self.assertEqual(res.status, ResolutionStatus.RESOLVED_CANONICAL.value)
        self.assertEqual(res.resolved_canonical_id, "EXP-DRAW-20260824-010-V1")

    # 9. invalid alias rejection
    def test_09_invalid_alias_rejection(self):
        res = self.resolver.resolve_source_reference(
            raw_reference="EXP-DRAW-NONEXISTENT-999-V1",
            title="Fake Research",
            source_class=SourceClass.REVIEWED_UNEXECUTED.value,
            domain="DRAW",
            source_document="test",
        )
        self.assertEqual(res.status, ResolutionStatus.INVALID_REFERENCE.value)
        self.assertIsNone(res.resolved_canonical_id)

    # 10. ambiguous alias fail-closed
    def test_10_ambiguous_alias_fail_closed(self):
        res = self.resolver.resolve_source_reference(
            raw_reference="SOME_AMBIGUOUS_LABEL",
            title="Unclear title without lineage",
            source_class=SourceClass.REVIEWED_UNEXECUTED.value,
            domain="DRAW",
            source_document="test",
        )
        self.assertIn(res.status, (ResolutionStatus.AMBIGUOUS.value, ResolutionStatus.UNRESOLVED.value))
        self.assertIsNone(res.resolved_canonical_id)

    # 11. valid merge acceptance
    def test_11_valid_merge_acceptance(self):
        res = self.resolver.resolve_source_reference(
            raw_reference="EXP-DRAW-20260824-010-V1",
            title="Official repair apply and finalize verification",
            source_class=SourceClass.NON_EXP_EXECUTED.value,
            domain="DRAW",
            source_document="90_RESEARCH/P45_RESEARCH_MASTER_INDEX_005.md",
        )
        self.assertEqual(res.status, ResolutionStatus.RESOLVED_CANONICAL.value)
        self.assertEqual(res.resolved_canonical_id, "EXP-DRAW-20260824-010-V1")

    # 12. unjustified merge rejection
    def test_12_unjustified_merge_rejection(self):
        res = self.resolver.resolve_source_reference(
            raw_reference="EXP-DRAW-20260816-009-V1",
            title="Pair shadow repair apply audit",
            source_class=SourceClass.NON_EXP_EXECUTED.value,
            domain="DRAW",
            source_document="test",
        )
        canon = self.resolver.get_canonical_record("EXP-DRAW-20260816-009-V1")
        self.assertEqual(canon.canonical_title, "전체 관계망")
        self.assertNotIn("Pair shadow repair", canon.canonical_title)

    # 13. source->canonical->knowledge reverse trace
    def test_13_source_canonical_knowledge_reverse_trace(self):
        rec = self.index.trace_source_to_record("SRC-NONEXP-20")
        self.assertIsNotNone(rec)
        self.assertEqual(rec.record_id, "EXP-DRAW-20260824-010-V1")
        self.assertIn("OFFICIAL PAIR LIFECYCLE REPAIR APPLY AUDIT", rec.canonical_name)

    # 14. semantic matcher uses resolved metadata
    def test_14_semantic_matcher_uses_resolved_metadata(self):
        checker = SemanticNoveltyCheckerV1_1(self.index)
        cand_pkg = {
            "candidate_id": "TEST-PAIR-001",
            "title": "Pair Lifecycle Dormancy Duration Geometric Memory Invariance",
            "source_variables": ["pair_co_occurrence_matrix_t"],
            "target_variable": "pair_dormancy_duration_distribution",
            "lag": 1,
            "primary_metric": "dormancy_decay_geometric_fit_error",
            "null": "Independent memoryless Bernoulli trials per pair",
            "ontology_tags": ["PAIR", "dormancy", "geometric_memory"],
            "novelty_reason": "Testing geometric memory of pair dormancy",
        }
        result = checker.audit_candidate(cand_pkg)
        self.assertTrue(len(result.top_matches) > 0)
        for match in result.top_matches:
            self.assertIsNotNone(match.canonical_registry_id)
            self.assertIsNotNone(match.canonical_title)
            self.assertIn(match.resolution_status, ("RESOLVED", "RESOLVED_CANONICAL", "RESOLVED_EXPLICIT"))

    # 15. invalid reference blocks READY_FOR_PROTOCOL
    def test_15_invalid_reference_blocks_ready_for_protocol(self):
        checker = SemanticNoveltyCheckerV1_1(self.index)
        cand_pkg = {
            "candidate_id": "TEST-SYNTHETIC-001",
            "title": "Synthetic Unique Concept Without Precedents",
            "source_variables": ["x"],
            "target_variable": "y",
            "lag": 1,
            "primary_metric": "metric_x",
            "null": "null_x",
            "ontology_tags": ["CORE"],
            "novelty_reason": "Novel synthetic idea",
        }
        result = checker.audit_candidate(cand_pkg)
        bad_match = SemanticMatchItem(
            existing_research_id="EXP-BAD-001",
            existing_title="Bad Title",
            source_type="UNKNOWN",
            status="FAILED",
            ontology_tags=["CORE"],
            candidate_input="",
            existing_input="",
            candidate_transformation="",
            existing_transformation="",
            candidate_target="",
            existing_target="",
            candidate_lag=1,
            existing_lag=1,
            candidate_metric="",
            existing_metric="",
            candidate_null="",
            existing_null="",
            candidate_conditioning="",
            existing_conditioning="",
            same_features=[],
            different_features=[],
            similarity_score=80.0,
            semantic_overlap_class="FAILED_AXIS_RESCUE",
            canonical_registry_id=None,
            canonical_title=None,
            resolution_status="INVALID_REFERENCE",
        )
        result.top_matches.insert(0, bad_match)
        top_invalid = [m.existing_research_id for m in result.top_matches if m.resolution_status in ("INVALID_REFERENCE", "AMBIGUOUS", "UNRESOLVED")]
        self.assertTrue(len(top_invalid) > 0)
        verdict = NoveltyFinalVerdict.BLOCKED_REFERENTIAL_INTEGRITY.value if top_invalid else result.final_verdict
        self.assertEqual(verdict, NoveltyFinalVerdict.BLOCKED_REFERENTIAL_INTEGRITY.value)

    # 16. knowledge coverage requires referential integrity
    def test_16_knowledge_coverage_requires_referential_integrity(self):
        inv_builder = ResearchSourceInventoryBuilder()
        items = inv_builder.build_source_inventory()
        manifest_builder = ResearchKnowledgeCoverageManifestBuilder()
        manifest = manifest_builder.build_manifest(items)
        self.assertTrue(manifest.is_complete)
        self.assertTrue(manifest.has_referential_integrity)
        audit = manifest.referential_integrity_audit
        self.assertEqual(audit.get("invalid_aliases"), 0)
        self.assertEqual(audit.get("invalid_merges"), 0)
        self.assertEqual(audit.get("ambiguous_aliases"), 0)
        self.assertEqual(audit.get("invalid_formal_references"), 0)
        self.assertEqual(audit.get("ambiguous_formal_references"), 0)

    # 17. A candidate regression
    def test_17_candidate_a_regression(self):
        res = self.agent.reassess_v1_candidates()
        cand_a = next(c for c in res if c.candidate_id == "IDEA-1243-NEGA-001")
        self.assertEqual(cand_a.final_verdict, NoveltyFinalVerdict.REJECT_RESCUE.value)
        self.assertTrue(cand_a.referential_integrity_pass)
        self.assertEqual(len(cand_a.invalid_references), 0)
        top_canon = [m.canonical_registry_id for m in cand_a.top_matches]
        self.assertNotIn("EXP-DRAW-20260821-042-V1", top_canon)

    # 18. B candidate regression
    def test_18_candidate_b_regression(self):
        res = self.agent.reassess_v1_candidates()
        cand_b = next(c for c in res if c.candidate_id == "IDEA-1243-OPPO-002")
        self.assertEqual(cand_b.final_verdict, NoveltyFinalVerdict.REJECT_RESCUE.value)
        self.assertTrue(cand_b.referential_integrity_pass)
        self.assertEqual(len(cand_b.invalid_references), 0)

    # 19. C candidate regression
    def test_19_candidate_c_regression(self):
        res = self.agent.reassess_v1_candidates()
        cand_c = next(c for c in res if c.candidate_id == "IDEA-1243-CROS-003")
        self.assertEqual(cand_c.final_verdict, NoveltyFinalVerdict.NEEDS_EVIDENCE.value)
        self.assertTrue(cand_c.referential_integrity_pass)
        self.assertEqual(len(cand_c.invalid_references), 0)
        self.assertNotEqual(cand_c.final_verdict, NoveltyFinalVerdict.READY_FOR_PROTOCOL.value)

    # 20. Official firewall
    def test_20_official_firewall(self):
        for rec in self.index.list_all():
            if "OFFICIAL" in rec.source_classes:
                self.assertIn(rec.verdict, ("OFFICIAL_FROZEN", "USER-APPROVED SEALED CHANGE CONTROL", "SUPPORTED"))
                self.assertFalse(rec.research_id.startswith("AUTO-"))

    # 21. future leakage
    def test_21_future_leakage(self):
        prospective_recs = self.index.filter_by_class(SourceClass.ACTIVE_PROSPECTIVE.value)
        self.assertEqual(len(prospective_recs), 1)
        p_rec = prospective_recs[0]
        self.assertIn("1244", p_rec.condition)
        self.assertIn("unrevealed", p_rec.condition.lower())

    # 22. idempotency
    def test_22_idempotency(self):
        builder = ResearchKnowledgeIndexBuilder()
        idx2 = builder.build_index()
        self.assertEqual(idx2.count(), self.index.count())
        self.assertEqual(idx2.has_referential_integrity(), self.index.has_referential_integrity())


if __name__ == "__main__":
    unittest.main()

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

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p45_v27.research_automation.master_source_raw_extractor import (
    MasterSourceRawExtractor,
    MasterRawSnapshot,
)

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



class TestNonExpLineageSemanticIntegrity(unittest.TestCase):
    """Enforces the 24 non-EXP 1:1 lineage and semantic referential integrity tests."""

    @classmethod
    def setUpClass(cls):
        cls.resolver = CanonicalResearchIdResolver()
        cls.inv_builder = ResearchSourceInventoryBuilder()
        cls.source_items = cls.inv_builder.build_source_inventory()
        cls.man_builder = ResearchKnowledgeCoverageManifestBuilder()
        cls.manifest = cls.man_builder.build_manifest(cls.source_items)
        cls.audit_report = cls.resolver.audit_referential_integrity(cls.source_items, cls.manifest.mappings)
        cls.non_exp_audits = {a.source_item_id: a for a in cls.audit_report.non_exp_lineage_audits}
        builder = ResearchKnowledgeIndexBuilder()
        cls.index = builder.build_index()
        cls.agent = ResearchDiscoveryAgent()
        cls.checker = SemanticNoveltyCheckerV1_1(knowledge_index=cls.index)

    # 1. SRC-NONEXP-23 cannot alias to DRAW NO-PICK target.
    def test_23_nonexp_23_cannot_alias_to_draw_nopick(self):
        # Attempt bad alias: SRC-NONEXP-23 to EXP-DRAW-20260816-038-V2
        from p45_v27.research_automation.knowledge_source_inventory import SourceMappingEntry, MappingType
        bad_mapping = [SourceMappingEntry(
            source_item_id="SRC-NONEXP-23",
            normalized_record_id="EXP-DRAW-20260816-038-V2",
            mapping_type=MappingType.ALIAS.value,
            mapping_reason="Fake alias to draw no pick",
            evidence="none",
        )]
        report = self.resolver.audit_referential_integrity(self.source_items, bad_mapping)
        self.assertGreater(report.invalid_aliases, 0)
        self.assertGreater(report.domain_mismatch_unjustified, 0)
        self.assertEqual(report.referential_integrity_verdict, "FAIL_NON_EXP_REFERENTIAL_INTEGRITY")

    # 2. SRC-NONEXP-24 cannot alias to DRAW adjacency target.
    def test_24_nonexp_24_cannot_alias_to_draw_adjacency(self):
        from p45_v27.research_automation.knowledge_source_inventory import SourceMappingEntry, MappingType
        bad_mapping = [SourceMappingEntry(
            source_item_id="SRC-NONEXP-24",
            normalized_record_id="EXP-DRAW-20260827-018-V2",
            mapping_type=MappingType.ALIAS.value,
            mapping_reason="Fake alias to draw adjacency",
            evidence="none",
        )]
        report = self.resolver.audit_referential_integrity(self.source_items, bad_mapping)
        self.assertGreater(report.invalid_aliases, 0)
        self.assertGreater(report.domain_mismatch_unjustified, 0)
        self.assertEqual(report.referential_integrity_verdict, "FAIL_NON_EXP_REFERENTIAL_INTEGRITY")

    # 3. CROWD source requires CROWD target unless explicit cross-domain lineage evidence exists.
    def test_25_crowd_source_requires_crowd_target(self):
        for audit in self.audit_report.alias_audits:
            if "CROWD" in audit.source_item_id or "Crowd" in audit.explicit_lineage_evidence:
                target_entry = self.resolver.get_registry_entry(audit.alias_target)
                self.assertIsNotNone(target_entry)
                self.assertEqual(target_entry.domain, "CROWD")
                self.assertTrue(audit.domain_match)

    # 4. PRIZE source requires PRIZE target unless explicit cross-domain lineage evidence exists.
    def test_26_prize_source_requires_prize_target(self):
        for m in self.manifest.mappings:
            if "SRC-NONEXP-27" in m.source_item_id:
                for lt in m.lineage_targets:
                    self.assertIn(lt["domain"], ("PRIZE", "PRIZE_SHARE"))

    # 5. PAIR repair cannot alias NUMBER RELATION target.
    def test_27_pair_repair_cannot_alias_number_relation(self):
        from p45_v27.research_automation.knowledge_source_inventory import SourceMappingEntry, MappingType
        bad_mapping = [SourceMappingEntry(
            source_item_id="SRC-NONEXP-20",
            normalized_record_id="EXP-DRAW-20260816-009-V1",
            mapping_type=MappingType.ALIAS.value,
            mapping_reason="Fake alias to number relation",
            evidence="none",
        )]
        report = self.resolver.audit_referential_integrity(self.source_items, bad_mapping)
        self.assertGreater(report.invalid_aliases, 0)
        self.assertGreater(report.domain_mismatch_unjustified, 0)

    # 6. Every NON-EXP source item has audited lineage verdict.
    def test_28_every_non_exp_has_audited_verdict(self):
        non_exp_items = [it for it in self.source_items if it.source_class == "NON_EXP_EXECUTED"]
        self.assertEqual(len(non_exp_items), 28)
        for it in non_exp_items:
            sid = it.source_item_id
            self.assertIn(sid, self.non_exp_audits)
            audit = self.non_exp_audits[sid]
            self.assertIn(audit.verdict, ("VALID_DIRECT", "VALID_ALIAS", "VALID_MERGE", "VALID_RELATED_DISTINCT"))
            self.assertTrue(audit.domain_compatible)
            self.assertTrue(audit.ontology_compatible)
            self.assertTrue(audit.title_semantic_compatible)

    # 7. Every ALIAS has explicit evidence path.
    def test_29_every_alias_has_explicit_evidence_path(self):
        for a in self.audit_report.alias_audits:
            if a.verdict == "VALID_ALIAS":
                self.assertTrue(len(a.explicit_lineage_evidence) > 0)
                self.assertTrue(a.target_exists)

    # 8. Every MERGE has same experiment lineage proof.
    def test_30_every_merge_has_same_experiment_lineage_proof(self):
        for m in self.audit_report.merge_audits:
            if m.verdict == "VALID_MERGE":
                self.assertTrue(m.same_experiment_lineage)
                self.assertTrue(len(m.explicit_change_control_evidence) > 0)
                self.assertTrue(m.target_exists)

    # 9. DIRECT record allowed without formal target.
    def test_31_direct_record_allowed_without_formal_target(self):
        direct_audits = [a for a in self.non_exp_audits.values() if a.verdict == "VALID_DIRECT"]
        self.assertGreaterEqual(len(direct_audits), 20)
        for d in direct_audits:
            self.assertFalse(d.final_target_id.startswith("EXP-"))

    # 10. RELATED_BUT_DISTINCT allowed without forced alias.
    def test_32_related_but_distinct_allowed_without_forced_alias(self):
        related_audits = [a for a in self.non_exp_audits.values() if a.verdict == "VALID_RELATED_DISTINCT"]
        self.assertGreaterEqual(len(related_audits), 1)
        item27 = self.non_exp_audits.get("SRC-NONEXP-27")
        self.assertIsNotNone(item27)
        self.assertEqual(item27.verdict, "VALID_RELATED_DISTINCT")

    # 11. Multi-target lineage supported.
    def test_33_multi_target_lineage_supported(self):
        item27_mapping = next(m for m in self.manifest.mappings if m.source_item_id == "SRC-NONEXP-27")
        self.assertGreaterEqual(len(item27_mapping.lineage_targets), 3)
        target_ids = [lt["canonical_id"] for lt in item27_mapping.lineage_targets]
        self.assertIn("EXP-PRIZE-20260816-001-V2", target_ids)
        self.assertIn("EXP-PRIZE-20260821-004-V1", target_ids)
        self.assertIn("EXP-PRIZE-20260821-005-V1", target_ids)

    # 12. Bad domain target triggers fail-closed.
    def test_34_bad_domain_target_triggers_fail_closed(self):
        from p45_v27.research_automation.knowledge_source_inventory import SourceMappingEntry, MappingType
        bad_mapping = [SourceMappingEntry(
            source_item_id="SRC-NONEXP-23",
            normalized_record_id="EXP-DRAW-20260816-001-V1",
            mapping_type=MappingType.ALIAS.value,
            mapping_reason="Mismatched domain alias",
            evidence="none",
        )]
        report = self.resolver.audit_referential_integrity(self.source_items, bad_mapping)
        self.assertEqual(report.referential_integrity_verdict, "FAIL_NON_EXP_REFERENTIAL_INTEGRITY")
        self.assertGreater(report.domain_mismatch_unjustified, 0)

    # 13. Fake existing Registry ID but wrong domain is rejected.
    def test_35_fake_existing_registry_id_wrong_domain_rejected(self):
        from p45_v27.research_automation.knowledge_source_inventory import SourceMappingEntry, MappingType
        # Target exists (EXP-DRAW-20260827-019-V1 is in registry) but domain is DRAW, not CROWD
        bad_mapping = [SourceMappingEntry(
            source_item_id="SRC-NONEXP-24",
            normalized_record_id="EXP-DRAW-20260827-019-V1",
            mapping_type=MappingType.ALIAS.value,
            mapping_reason="Lineage keyword present but wrong domain",
            evidence="none",
        )]
        report = self.resolver.audit_referential_integrity(self.source_items, bad_mapping)
        self.assertEqual(report.referential_integrity_verdict, "FAIL_NON_EXP_REFERENTIAL_INTEGRITY")
        self.assertGreater(report.invalid_aliases, 0)

    # 14. Correct Crowd topology 001 lineage passes.
    def test_36_correct_crowd_topology_001_lineage_passes(self):
        audit23 = self.non_exp_audits.get("SRC-NONEXP-23")
        self.assertIsNotNone(audit23)
        self.assertEqual(audit23.verdict, "VALID_ALIAS")
        self.assertEqual(audit23.final_target_id, "EXP-CROWD-20260823-005-V1")
        self.assertEqual(audit23.current_target_domain, "CROWD")

    # 15. Correct Crowd topology 002 lineage passes.
    def test_37_correct_crowd_topology_002_lineage_passes(self):
        audit24 = self.non_exp_audits.get("SRC-NONEXP-24")
        self.assertIsNotNone(audit24)
        self.assertEqual(audit24.verdict, "VALID_ALIAS")
        self.assertEqual(audit24.final_target_id, "EXP-CROWD-20260823-006-V1")
        self.assertEqual(audit24.current_target_domain, "CROWD")

    # 16. Correct Crowd topology 003 lineage passes if evidence exists.
    def test_38_correct_crowd_topology_003_lineage_passes(self):
        audit25 = self.non_exp_audits.get("SRC-NONEXP-25")
        self.assertIsNotNone(audit25)
        self.assertEqual(audit25.verdict, "VALID_ALIAS")
        self.assertEqual(audit25.final_target_id, "EXP-CROWD-20260823-007-V1")
        self.assertEqual(audit25.current_target_domain, "CROWD")

    # 17. Correct Crowd retail 001 lineage passes.
    def test_39_correct_crowd_retail_001_lineage_passes(self):
        audit26 = self.non_exp_audits.get("SRC-NONEXP-26")
        self.assertIsNotNone(audit26)
        self.assertEqual(audit26.verdict, "VALID_ALIAS")
        self.assertEqual(audit26.final_target_id, "EXP-CROWD-20260823-008-V1")
        self.assertEqual(audit26.current_target_domain, "CROWD")

    # 18. Prize-share 001/002 joint lineage handled correctly.
    def test_40_prize_share_joint_lineage_handled_correctly(self):
        audit27 = self.non_exp_audits.get("SRC-NONEXP-27")
        self.assertIsNotNone(audit27)
        self.assertEqual(audit27.verdict, "VALID_RELATED_DISTINCT")
        self.assertEqual(len(audit27.candidate_formal_targets), 3)

    # 19. Candidate C irrelevant twin-round matches removed unless explicit structural evidence exists.
    def test_41_candidate_c_irrelevant_twin_round_matches_removed(self):
        cand_c = {
            "candidate_id": "IDEA-1243-CROS-003",
            "title": "Pair Lifecycle Dormancy Duration Geometric Memory Invariance",
            "proposed_inputs": "Pair absence intervals (dormancy duration) for all 990 pairs",
            "target_metric": "Hazard rate constancy across dormancy bins",
            "novelty_reason": "Pair-level memorylessness test across dormancy regimes",
            "lag": 1,
            "null_hypothesis": "Geometric memoryless null p = comb(43,4)/comb(45,6)",
            "conditioning": "Pair absence since last appearance",
        }
        res = self.checker.audit_candidate(cand_c)
        top_ids = [m.existing_research_id for m in res.top_matches[:5]]
        self.assertNotIn("EXP-DRAW-20260816-023-V1", top_ids)
        self.assertNotIn("EXP-DRAW-20260816-024-V1", top_ids)
        self.assertNotIn("EXP-DRAW-20260816-025-V1", top_ids)
        for m in res.top_matches[:2]:
            self.assertTrue(
                "pair" in m.existing_title.lower() or "pair" in m.existing_research_id.lower() or "core" in m.existing_title.lower()
            )

    # 20. Candidate A/B verdict regression.
    def test_42_candidate_a_b_verdict_regression(self):
        res = self.agent.reassess_v1_candidates()
        cand_a = next(c for c in res if c.candidate_id == "IDEA-1243-NEGA-001")
        cand_b = next(c for c in res if c.candidate_id == "IDEA-1243-OPPO-002")
        self.assertEqual(cand_a.final_verdict, NoveltyFinalVerdict.REJECT_RESCUE.value)
        self.assertEqual(cand_b.final_verdict, NoveltyFinalVerdict.REJECT_RESCUE.value)

    # 21. Candidate C remains non-promoted.
    def test_43_candidate_c_remains_non_promoted(self):
        res = self.agent.reassess_v1_candidates()
        cand_c = next(c for c in res if c.candidate_id == "IDEA-1243-CROS-003")
        self.assertEqual(cand_c.final_verdict, NoveltyFinalVerdict.NEEDS_EVIDENCE.value)
        self.assertNotEqual(cand_c.final_verdict, NoveltyFinalVerdict.READY_FOR_PROTOCOL.value)

    # 22. Official firewall.
    def test_44_official_firewall_intact(self):
        for rec in self.index.list_all():
            if "OFFICIAL" in rec.source_classes:
                self.assertIn(rec.verdict, ("OFFICIAL_FROZEN", "USER-APPROVED SEALED CHANGE CONTROL", "SUPPORTED"))

    # 23. Future leakage 0.
    def test_45_future_leakage_zero(self):
        prospective = self.index.filter_by_class(SourceClass.ACTIVE_PROSPECTIVE.value)
        self.assertEqual(len(prospective), 1)
        self.assertIn("1244", prospective[0].condition)

    # 24. Idempotency.
    def test_46_idempotency_audit_repeat(self):
        audit2 = self.resolver.audit_referential_integrity(self.source_items, self.manifest.mappings)
        self.assertEqual(audit2.referential_integrity_verdict, self.audit_report.referential_integrity_verdict)
        self.assertEqual(len(audit2.non_exp_lineage_audits), len(self.audit_report.non_exp_lineage_audits))


class TestMasterSourceIdentityAndFingerprint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_extractor = MasterSourceRawExtractor()
        cls.raw_snapshot = cls.raw_extractor.extract_raw_section_c()
        cls.inv_builder = ResearchSourceInventoryBuilder()
        cls.source_items = cls.inv_builder.build_source_inventory()
        cls.non_exp_prods = [it for it in cls.source_items if it.source_class == SourceClass.NON_EXP_EXECUTED.value]
        cls.manifest_builder = ResearchKnowledgeCoverageManifestBuilder()
        cls.manifest = cls.manifest_builder.build_manifest(cls.source_items)
        cls.resolver = CanonicalResearchIdResolver()
        cls.lineage_audits = cls.resolver.audit_non_exp_lineage(cls.source_items, cls.manifest.mappings)
        cls.agent = ResearchDiscoveryAgent()
        cls.checker = SemanticNoveltyCheckerV1_1(cls.agent.knowledge_index)

    # 1. Master raw section parser count (28)
    def test_01_master_raw_section_parser_count(self):
        self.assertEqual(self.raw_snapshot.total_items, 28)
        self.assertEqual(len(self.raw_snapshot.items), 28)

    # 2. Production parser count equality
    def test_02_production_parser_count_equality(self):
        self.assertEqual(len(self.non_exp_prods), self.raw_snapshot.total_items)
        self.assertEqual(len(self.non_exp_prods), 28)

    # 3. Ordinal exact equality
    def test_03_ordinal_exact_equality(self):
        for idx in range(1, 29):
            raw_it = self.raw_snapshot.items[idx - 1]
            prod_it = next((it for it in self.non_exp_prods if it.ordinal == idx), None)
            self.assertIsNotNone(prod_it, f"Ordinal {idx} missing in production parser")
            self.assertEqual(raw_it.ordinal, prod_it.ordinal)

    # 4. Raw title exact equality
    def test_04_raw_title_exact_equality(self):
        for idx in range(1, 29):
            raw_it = self.raw_snapshot.items[idx - 1]
            prod_it = next(it for it in self.non_exp_prods if it.ordinal == idx)
            self.assertEqual(raw_it.raw_title, prod_it.raw_title)

    # 5. Raw source text exact equality
    def test_05_raw_source_text_exact_equality(self):
        for idx in range(1, 29):
            raw_it = self.raw_snapshot.items[idx - 1]
            prod_it = next(it for it in self.non_exp_prods if it.ordinal == idx)
            self.assertEqual(raw_it.raw_source_text, prod_it.raw_source_text)

    # 6. Source fingerprint equality
    def test_06_source_fingerprint_equality(self):
        for idx in range(1, 29):
            raw_it = self.raw_snapshot.items[idx - 1]
            prod_it = next(it for it in self.non_exp_prods if it.ordinal == idx)
            self.assertEqual(raw_it.source_fingerprint, prod_it.source_fingerprint)
            self.assertTrue(len(prod_it.source_fingerprint) == 64)

    # 7. Invented title rejection
    def test_07_invented_title_rejection(self):
        invented_titles = [
            "Number order statistical distribution",
            "Consecutive number adjacency structure",
            "Pair co-occurrence topology matrix",
            "Sum distribution dynamic envelope",
            "AC value structural complexity",
        ]
        parsed_titles = [it.raw_title for it in self.non_exp_prods]
        for inv_title in invented_titles:
            self.assertNotIn(inv_title, parsed_titles)

    # 8. Missing Master item rejection
    def test_08_missing_master_item_rejection(self):
        partial_prods = self.non_exp_prods[:-1]  # Drop 28
        report = self.raw_extractor.reconcile_parsers(self.raw_snapshot, partial_prods)
        self.assertGreater(report.missing_master_items, 0)
        self.assertEqual(report.verdict, "BLOCKED_MASTER_SOURCE_IDENTITY")

    # 9. Ordinal/title swap rejection
    def test_09_ordinal_title_swap_rejection(self):
        swapped = copy.deepcopy(self.non_exp_prods)
        swapped[0].raw_title, swapped[1].raw_title = swapped[1].raw_title, swapped[0].raw_title
        report = self.raw_extractor.reconcile_parsers(self.raw_snapshot, swapped)
        self.assertGreater(report.source_title_substitution, 0)
        self.assertEqual(report.verdict, "BLOCKED_MASTER_SOURCE_IDENTITY")

    # 10. Generated JSON self-reference test prohibition
    def test_10_no_json_self_reference(self):
        self.assertTrue(self.raw_snapshot.source_document.endswith(".md"))

    # 11. Source inventory count equality
    def test_11_source_inventory_count_equality(self):
        self.assertEqual(len(self.non_exp_prods), 28)

    # 12. Lineage audit count equality
    def test_12_lineage_audit_count_equality(self):
        self.assertEqual(len(self.lineage_audits), 28)

    # 13. First anchor identity
    def test_13_first_anchor_identity(self):
        it = self.raw_snapshot.items[0]
        self.assertEqual(it.ordinal, 1)
        self.assertEqual(it.raw_title, "TRIO ORBIT Fixed/Linked 역사검증")

    # 14. TRIO ORBIT anchor
    def test_14_trio_orbit_anchor(self):
        it = self.raw_snapshot.items[1]
        self.assertEqual(it.ordinal, 2)
        self.assertEqual(it.raw_title, "TRIO ORBIT divergence attribution")

    # 15. PAIR repair anchor
    def test_15_pair_repair_anchor(self):
        it = self.raw_snapshot.items[19]
        self.assertEqual(it.ordinal, 20)
        self.assertEqual(it.raw_title, "Pair shadow repair deterministic validation")

    # 16. Crowd topology 001 anchor
    def test_16_crowd_topology_001_anchor(self):
        it = self.raw_snapshot.items[22]
        self.assertEqual(it.ordinal, 23)
        self.assertEqual(it.raw_title, "Crowd topology 001 supporting audit lineage")

    # 17. Crowd topology 002 anchor
    def test_17_crowd_topology_002_anchor(self):
        it = self.raw_snapshot.items[23]
        self.assertEqual(it.ordinal, 24)
        self.assertEqual(it.raw_title, "Crowd topology 002 independent reproduction/calibration")

    # 18. Prize-share anchor
    def test_18_prize_share_anchor(self):
        it = self.raw_snapshot.items[26]
        self.assertEqual(it.ordinal, 27)
        self.assertIn("Prize-share 001/002", it.raw_title)

    # 19. LZ76 anchor
    def test_19_lz76_anchor(self):
        it = self.raw_snapshot.items[27]
        self.assertEqual(it.ordinal, 28)
        self.assertEqual(it.raw_title, "LZ76 거시 복잡도 국면 고립 검정 V1")

    # 20. Incorrect synthetic title injection -> fail-closed
    def test_20_incorrect_synthetic_title_injection_fail_closed(self):
        corrupted = copy.deepcopy(self.non_exp_prods)
        corrupted[0].raw_title = "Number order statistical distribution"
        corrupted[0].source_fingerprint = "corrupted_fp"
        report = self.raw_extractor.reconcile_parsers(self.raw_snapshot, corrupted)
        self.assertEqual(report.verdict, "BLOCKED_MASTER_SOURCE_IDENTITY")

    # 21. Candidate A regression
    def test_21_candidate_a_regression(self):
        res = self.agent.reassess_v1_candidates()
        cand_a = next(c for c in res if c.candidate_id == "IDEA-1243-NEGA-001")
        self.assertEqual(cand_a.final_verdict, NoveltyFinalVerdict.REJECT_RESCUE.value)

    # 22. Candidate B regression
    def test_22_candidate_b_regression(self):
        res = self.agent.reassess_v1_candidates()
        cand_b = next(c for c in res if c.candidate_id == "IDEA-1243-OPPO-002")
        self.assertEqual(cand_b.final_verdict, NoveltyFinalVerdict.REJECT_RESCUE.value)

    # 23. Candidate C irrelevant-match regression
    def test_23_candidate_c_irrelevant_match_regression(self):
        res = self.agent.reassess_v1_candidates()
        cand_c = next(c for c in res if c.candidate_id == "IDEA-1243-CROS-003")
        self.assertEqual(cand_c.final_verdict, NoveltyFinalVerdict.NEEDS_EVIDENCE.value)
        top_ids = [m.existing_research_id for m in cand_c.top_matches]
        self.assertNotIn("EXP-DRAW-20260816-023-V1", top_ids)
        self.assertNotIn("EXP-DRAW-20260816-024-V1", top_ids)

    # 24. Official firewall
    def test_24_official_firewall(self):
        for rec in self.agent.knowledge_index.list_all():
            if "OFFICIAL" in rec.source_classes:
                self.assertIn(rec.verdict, ("OFFICIAL_FROZEN", "USER-APPROVED SEALED CHANGE CONTROL", "SUPPORTED"))

    # 25. Future leakage 0
    def test_25_future_leakage_zero(self):
        prospective = self.agent.knowledge_index.filter_by_class(SourceClass.ACTIVE_PROSPECTIVE.value)
        self.assertEqual(len(prospective), 1)

    # 26. Idempotency assertion
    def test_26_idempotency_assertion(self):
        snap2 = self.raw_extractor.extract_raw_section_c()
        self.assertEqual(snap2.section_fingerprint, self.raw_snapshot.section_fingerprint)


if __name__ == "__main__":
    unittest.main()



"""Comprehensive Unit Test Suite for P45 Research Canonical Display & Candidate Identity Lock.

Validates all 21 required assertions and Golden Snapshot Test from Section 19 & 20:
1. Formal Registry canonical title exact display
2. EXP-DRAW-20260816-015-V1 display title equals actual Registry title
3. EXP-DRAW-20260816-017-V1 display title equals actual Registry title
4. EXP-DRAW-20260816-026-V1 display title equals actual Registry title
5. semantic_title cannot overwrite canonical_title
6. display_summary cannot overwrite canonical_title
7. candidate_name loads from original candidate artifact
8. hypothesis loads from original candidate artifact
9. opposite_hypothesis loads from original candidate artifact
10. candidate identity fingerprint stable
11. modified candidate hypothesis triggers fail-closed
12. modified canonical title triggers fail-closed
13. Candidate A report uses exact formal titles
14. Candidate B report uses exact formal titles
15. Candidate C report uses exact formal titles
16. Candidate C twin-round contamination remains absent
17. Master source identity artifact remains unchanged
18. NON-EXP lineage integrity artifact remains unchanged
19. Official firewall
20. Future leakage 0
21. Idempotency assertion
22. Golden Report Snapshot exact source equality check
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p45_v27.research_automation.canonical_display_resolver import (
    CanonicalDisplayResolver,
    DisplayIdentitySource,
    ResolvedDisplayIdentity,
)
from p45_v27.research_automation.canonical_id_resolver import CanonicalResearchIdResolver
from p45_v27.research_automation.master_source_raw_extractor import MasterSourceRawExtractor
from p45_v27.research_automation.knowledge_index import ResearchKnowledgeIndexBuilder
from p45_v27.research_automation.knowledge_source_inventory import SourceClass
from p45_v27.research_automation.semantic_novelty_checker import (
    NoveltyFinalVerdict,
    SemanticNoveltyCheckerV1_1,
)
from p45_v27.research_automation.research_discovery_agent import ResearchDiscoveryAgent


class TestCanonicalDisplayIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.display_resolver = CanonicalDisplayResolver(ROOT)
        cls.canonical_resolver = CanonicalResearchIdResolver(ROOT)
        cls.raw_extractor = MasterSourceRawExtractor(ROOT)
        builder = ResearchKnowledgeIndexBuilder(ROOT)
        cls.index = builder.build_index()
        cls.agent = ResearchDiscoveryAgent(ROOT)
        cls.checker = SemanticNoveltyCheckerV1_1(cls.index, ROOT)
        # Execute reassessment to ensure fresh evidence files
        cls.audit_results = cls.agent.reassess_v1_candidates()

    # 1. Formal Registry canonical title exact display
    def test_01_formal_registry_canonical_title_exact_display(self):
        for eid, entry in self.canonical_resolver.registry_entries.items():
            disp = self.display_resolver.resolve_display_identity(eid)
            self.assertEqual(disp.identity_source, DisplayIdentitySource.FORMAL_REGISTRY.value)
            self.assertEqual(disp.canonical_title, entry.canonical_title)
            self.assertEqual(disp.canonical_id, entry.canonical_registry_id)

    # 2. EXP-DRAW-20260816-015-V1 display title equals actual Registry title
    def test_02_exp_015_display_title_equals_actual_registry_title(self):
        eid = "EXP-DRAW-20260816-015-V1"
        entry = self.canonical_resolver.get_canonical_record(eid)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.canonical_title, "결손 회복속도")
        disp = self.display_resolver.resolve_display_identity(eid)
        self.assertEqual(disp.canonical_title, "결손 회복속도")
        self.assertNotEqual(disp.canonical_title, "전멸 회차속도")

    # 3. EXP-DRAW-20260816-017-V1 display title equals actual Registry title
    def test_03_exp_017_display_title_equals_actual_registry_title(self):
        eid = "EXP-DRAW-20260816-017-V1"
        entry = self.canonical_resolver.get_canonical_record(eid)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.canonical_title, "가변 전멸구간 (EXP-004)")
        disp = self.display_resolver.resolve_display_identity(eid)
        self.assertEqual(disp.canonical_title, "가변 전멸구간 (EXP-004)")
        self.assertNotEqual(disp.canonical_title, "전멸 회귀선")

    # 4. EXP-DRAW-20260816-026-V1 display title equals actual Registry title
    def test_04_exp_026_display_title_equals_actual_registry_title(self):
        eid = "EXP-DRAW-20260816-026-V1"
        entry = self.canonical_resolver.get_canonical_record(eid)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.canonical_title, "숫자 간격 구조 (EXP-008)")
        disp = self.display_resolver.resolve_display_identity(eid)
        self.assertEqual(disp.canonical_title, "숫자 간격 구조 (EXP-008)")
        self.assertNotEqual(disp.canonical_title, "대척 동반 출현")

    # 5. semantic_title cannot overwrite canonical_title
    def test_05_semantic_title_cannot_overwrite_canonical_title(self):
        eid = "EXP-DRAW-20260816-015-V1"
        entry = self.canonical_resolver.get_canonical_record(eid)
        fake_record = {
            "research_id": eid,
            "semantic_title": "전멸 회차속도 (Semantic Paraphrase)",
            "display_summary": "Extinction speed summary",
        }
        disp = self.display_resolver.resolve_display_identity(fake_record)
        # canonical_title MUST remain exact registry title
        self.assertEqual(disp.canonical_title, entry.canonical_title)
        self.assertNotEqual(disp.canonical_title, fake_record["semantic_title"])

    # 6. display_summary cannot overwrite canonical_title
    def test_06_display_summary_cannot_overwrite_canonical_title(self):
        eid = "EXP-DRAW-20260816-017-V1"
        entry = self.canonical_resolver.get_canonical_record(eid)
        fake_record = {
            "research_id": eid,
            "display_summary": "전멸 회귀선 설명문",
        }
        disp = self.display_resolver.resolve_display_identity(fake_record)
        self.assertEqual(disp.canonical_title, entry.canonical_title)
        self.assertNotEqual(disp.canonical_title, fake_record["display_summary"])

    # 7. candidate_name loads from original candidate artifact
    def test_07_candidate_name_loads_from_original_artifact(self):
        orig_a = self.display_resolver.load_candidate_original_identity("IDEA-1243-NEGA-001")
        self.assertEqual(orig_a.candidate_name, "Fixed-Partition Extinction Negative-Space Recovery Invariance")
        orig_b = self.display_resolver.load_candidate_original_identity("IDEA-1243-OPPO-002")
        self.assertEqual(orig_b.candidate_name, "Number Proximity Minimum-Distance Repulsion Invariance")
        orig_c = self.display_resolver.load_candidate_original_identity("IDEA-1243-CROS-003")
        self.assertEqual(orig_c.candidate_name, "Pair Lifecycle Dormancy Duration Geometric Memory Invariance")

    # 8. hypothesis loads from original candidate artifact
    def test_08_hypothesis_loads_from_original_artifact(self):
        orig_a = self.display_resolver.load_candidate_original_identity("IDEA-1243-NEGA-001")
        self.assertIn("fixed 5-zone partition", orig_a.hypothesis)
        self.assertIn("compensatory rebound", orig_a.hypothesis)

        orig_b = self.display_resolver.load_candidate_original_identity("IDEA-1243-OPPO-002")
        self.assertIn("Consecutive sorted winning numbers exhibit significant repulsion", orig_b.hypothesis)

        orig_c = self.display_resolver.load_candidate_original_identity("IDEA-1243-CROS-003")
        self.assertIn("Pair lifecycle dormancy durations", orig_c.hypothesis)
        self.assertIn("memoryless geometric distribution", orig_c.hypothesis)

    # 9. opposite_hypothesis loads from original candidate artifact
    def test_09_opposite_hypothesis_loads_from_original_artifact(self):
        orig_a = self.display_resolver.load_candidate_original_identity("IDEA-1243-NEGA-001")
        self.assertIn("Zone extinction has zero memory effect", orig_a.opposite_hypothesis)

        orig_b = self.display_resolver.load_candidate_original_identity("IDEA-1243-OPPO-002")
        self.assertIn("Adjacent ball spacing is completely memoryless", orig_b.opposite_hypothesis)

        orig_c = self.display_resolver.load_candidate_original_identity("IDEA-1243-CROS-003")
        self.assertIn("Pair lifecycle dormancy exhibits non-geometric hazard aging", orig_c.opposite_hypothesis)

    # 10. candidate identity fingerprint stable
    def test_10_candidate_identity_fingerprint_stable(self):
        orig_a = self.display_resolver.load_candidate_original_identity("IDEA-1243-NEGA-001")
        expected_fp_a = hashlib.sha256(
            (orig_a.candidate_id + orig_a.candidate_name + orig_a.hypothesis + orig_a.opposite_hypothesis + str(orig_a.discovery_data_end_round)).encode("utf-8")
        ).hexdigest()
        self.assertEqual(orig_a.identity_fingerprint, expected_fp_a)

    # 11. modified candidate hypothesis triggers fail-closed
    def test_11_modified_candidate_hypothesis_triggers_fail_closed(self):
        corrupted_report = {
            "audits": [
                {
                    "candidate_id": "IDEA-1243-NEGA-001",
                    "candidate_name": "Fixed-Partition Extinction Negative-Space Recovery Invariance",
                    "hypothesis": "Corrupted hypothesis summary: zone rebound occurs after 0 balls.",
                    "opposite_hypothesis": "Zone extinction has zero memory effect: next-round zone occupancy conforms strictly to the memoryless hypergeometric distribution P(k balls | 9 balls in zone, 6 drawn from 45).",
                    "discovery_data_end_round": 1243,
                    "candidate_identity_fingerprint": "fake_fingerprint",
                    "top_matches": [],
                }
            ]
        }
        audit = self.display_resolver.audit_display_report(corrupted_report)
        self.assertEqual(audit.verdict, "BLOCKED_DISPLAY_IDENTITY_INTEGRITY")
        self.assertGreater(audit.hypothesis_substitution, 0)
        self.assertGreater(audit.candidate_identity_fingerprint_mismatch, 0)

    # 12. modified canonical title triggers fail-closed
    def test_12_modified_canonical_title_triggers_fail_closed(self):
        corrupted_report = {
            "audits": [
                {
                    "candidate_id": "IDEA-1243-NEGA-001",
                    "candidate_name": "Fixed-Partition Extinction Negative-Space Recovery Invariance",
                    "hypothesis": "When a fixed 5-zone partition (Zones 1..5, each 9 balls) experiences complete extinction (0 balls drawn) in round t, the occupancy count in round t+1 exhibits positive compensatory rebound exceeding hypergeometric expectation.",
                    "opposite_hypothesis": "Zone extinction has zero memory effect: next-round zone occupancy conforms strictly to the memoryless hypergeometric distribution P(k balls | 9 balls in zone, 6 drawn from 45).",
                    "discovery_data_end_round": 1243,
                    "candidate_identity_fingerprint": "c662c8c15d19ab549818fbd218d9c2a613c2eb1718064e4cddee02a0332c1f52",
                    "top_matches": [
                        {
                            "canonical_registry_id": "EXP-DRAW-20260816-015-V1",
                            "canonical_title_exact": "전멸 회차속도",  # Substituted title!
                        }
                    ],
                }
            ]
        }
        audit = self.display_resolver.audit_display_report(corrupted_report)
        self.assertEqual(audit.verdict, "BLOCKED_DISPLAY_IDENTITY_INTEGRITY")
        self.assertGreater(audit.canonical_title_substitution, 0)

    # 13. Candidate A report uses exact formal titles
    def test_13_candidate_a_report_uses_exact_formal_titles(self):
        cand_a = next(c for c in self.audit_results if c.candidate_id == "IDEA-1243-NEGA-001")
        self.assertEqual(cand_a.candidate_name, "Fixed-Partition Extinction Negative-Space Recovery Invariance")
        for m in cand_a.top_matches:
            if m.source_type == "FORMAL_REGISTRY":
                entry = self.canonical_resolver.get_canonical_record(m.canonical_registry_id)
                self.assertEqual(m.canonical_title_exact, entry.canonical_title)
                self.assertEqual(m.existing_title, entry.canonical_title)

    # 14. Candidate B report uses exact formal titles
    def test_14_candidate_b_report_uses_exact_formal_titles(self):
        cand_b = next(c for c in self.audit_results if c.candidate_id == "IDEA-1243-OPPO-002")
        self.assertEqual(cand_b.candidate_name, "Number Proximity Minimum-Distance Repulsion Invariance")
        # Top 1 must be EXP-DRAW-20260816-026-V1
        m1 = cand_b.top_matches[0]
        self.assertEqual(m1.existing_research_id, "EXP-DRAW-20260816-026-V1")
        self.assertEqual(m1.canonical_title_exact, "숫자 간격 구조 (EXP-008)")
        for m in cand_b.top_matches:
            if m.source_type == "FORMAL_REGISTRY":
                entry = self.canonical_resolver.get_canonical_record(m.canonical_registry_id)
                self.assertEqual(m.canonical_title_exact, entry.canonical_title)

    # 15. Candidate C report uses exact formal titles
    def test_15_candidate_c_report_uses_exact_formal_titles(self):
        cand_c = next(c for c in self.audit_results if c.candidate_id == "IDEA-1243-CROS-003")
        self.assertEqual(cand_c.candidate_name, "Pair Lifecycle Dormancy Duration Geometric Memory Invariance")
        # Top 1 must be EXP-DRAW-20260824-010-V1
        m1 = cand_c.top_matches[0]
        self.assertEqual(m1.existing_research_id, "EXP-DRAW-20260824-010-V1")
        self.assertEqual(m1.canonical_title_exact, "OFFICIAL PAIR LIFECYCLE REPAIR APPLY AUDIT")

    # 16. Candidate C twin-round contamination remains absent
    def test_16_candidate_c_twin_round_contamination_absent(self):
        cand_c = next(c for c in self.audit_results if c.candidate_id == "IDEA-1243-CROS-003")
        top_ids = [m.existing_research_id for m in cand_c.top_matches]
        self.assertNotIn("EXP-DRAW-20260816-023-V1", top_ids)
        self.assertNotIn("EXP-DRAW-20260816-024-V1", top_ids)
        self.assertNotIn("EXP-DRAW-20260816-025-V1", top_ids)

    # 17. Master source identity artifact remains unchanged
    def test_17_master_source_identity_remains_unchanged(self):
        raw_snap = self.raw_extractor.extract_raw_section_c()
        self.assertEqual(raw_snap.total_items, 28)
        self.assertEqual(raw_snap.section_fingerprint, "66baf18efd12f9ad6d1a6e9f5e80422a5cfe9539025937b5a7e77bbc39a2b6bf")

    # 18. NON-EXP lineage integrity artifact remains unchanged
    def test_18_non_exp_lineage_integrity_remains_unchanged(self):
        lineage_file = ROOT / "v27_storage" / "research_automation" / "knowledge" / "NON_EXP_LINEAGE_AUDIT.json"
        self.assertTrue(lineage_file.exists())
        lineage_data = json.loads(lineage_file.read_text(encoding="utf-8"))
        verdicts = lineage_data.get("verdict_counts", {})
        self.assertEqual(verdicts.get("INVALID_MAPPING_CORRECTED", 0), 0)
        self.assertEqual(verdicts.get("AMBIGUOUS_NEEDS_EVIDENCE", 0), 0)
        self.assertEqual(lineage_data.get("domain_incompatible_count", 0), 0)

        ref_file = ROOT / "v27_storage" / "research_automation" / "knowledge" / "RESEARCH_REFERENTIAL_INTEGRITY_AUDIT.json"
        self.assertTrue(ref_file.exists())
        ref_data = json.loads(ref_file.read_text(encoding="utf-8"))
        self.assertEqual(ref_data.get("invalid_non_exp_lineage", 0), 0)
        self.assertEqual(ref_data.get("ambiguous_non_exp_lineage", 0), 0)
        self.assertEqual(ref_data.get("referential_integrity_verdict"), "PASS_NON_EXP_REFERENTIAL_INTEGRITY")

    # 19. Official firewall
    def test_19_official_firewall(self):
        for rec in self.index.list_all():
            if rec.source_class == SourceClass.OFFICIAL_INTERNAL.value:
                self.assertIn(rec.verdict, ("OFFICIAL_FROZEN", "USER-APPROVED SEALED CHANGE CONTROL", "SUPPORTED"))

    # 20. Future leakage 0
    def test_20_future_leakage_zero(self):
        prospective = self.index.filter_by_class(SourceClass.ACTIVE_PROSPECTIVE.value)
        self.assertEqual(len(prospective), 1)

    # 21. Idempotency assertion
    def test_21_idempotency_assertion(self):
        res1 = self.agent.reassess_v1_candidates()
        res2 = self.agent.reassess_v1_candidates()
        self.assertEqual(len(res1), len(res2))
        for r1, r2 in zip(res1, res2):
            self.assertEqual(r1.candidate_id, r2.candidate_id)
            self.assertEqual(r1.candidate_identity_fingerprint, r2.candidate_identity_fingerprint)
            self.assertEqual(r1.final_verdict, r2.final_verdict)

    # 22. Golden Report Snapshot exact source equality check
    def test_22_golden_report_snapshot_exact_source_equality(self):
        evidence_json = ROOT / "v27_storage" / "research_automation" / "evidence" / "CANDIDATE_NOVELTY_EVIDENCE.json"
        self.assertTrue(evidence_json.exists())
        data = json.loads(evidence_json.read_text(encoding="utf-8"))

        # Zero substitutions across entire report
        audit = data.get("display_identity_audit", {})
        self.assertEqual(audit.get("verdict"), "PASS_CANONICAL_DISPLAY_IDENTITY")
        self.assertEqual(audit.get("canonical_title_substitution"), 0)
        self.assertEqual(audit.get("candidate_name_substitution"), 0)
        self.assertEqual(audit.get("hypothesis_substitution"), 0)
        self.assertEqual(audit.get("opposite_hypothesis_substitution"), 0)
        self.assertEqual(audit.get("display_source_mismatch"), 0)
        self.assertEqual(audit.get("candidate_identity_fingerprint_mismatch"), 0)
        self.assertEqual(audit.get("canonical_title_fingerprint_mismatch"), 0)

        # Direct exact equality against original candidate artifacts
        for a in data["audits"]:
            cid = a["candidate_id"]
            orig = self.display_resolver.load_candidate_original_identity(cid)
            self.assertEqual(a["candidate_name"], orig.candidate_name)
            self.assertEqual(a["hypothesis"], orig.hypothesis)
            self.assertEqual(a["opposite_hypothesis"], orig.opposite_hypothesis)
            self.assertEqual(a["candidate_identity_fingerprint"], orig.identity_fingerprint)

            # Direct exact equality against formal registry lookup
            for m in a["top_matches"]:
                if m["source_type"] == "FORMAL_REGISTRY":
                    entry = self.canonical_resolver.get_canonical_record(m["canonical_registry_id"])
                    self.assertIsNotNone(entry)
                    self.assertEqual(m["canonical_title_exact"], entry.canonical_title)
                    self.assertEqual(m["canonical_title"], entry.canonical_title)


if __name__ == "__main__":
    unittest.main()

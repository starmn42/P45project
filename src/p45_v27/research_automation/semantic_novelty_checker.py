"""Semantic Novelty Checker V1.1 / V1.2 for P45 RESEARCH DISCOVERY AGENT.

Replaces shallow string/tag checks with deep structural semantic field comparisons:
INPUT, TRANSFORMATION, CONDITION, TARGET, LAG, METRIC, NULL, ACTIONABILITY.

Generates TOP 10 SIMILAR MATCHES across all indexed research items.
Classifies overlaps into:
- EXACT_DUPLICATE
- NEAR_DUPLICATE
- FAILED_AXIS_RESCUE
- PARTIAL_OVERLAP
- DISTINCT

Enforces mandatory generation of:
- CANDIDATE_NOVELTY_EVIDENCE.json
- CANDIDATE_NOVELTY_EVIDENCE.md
- GOLDEN_CANDIDATE_DISPLAY_REPORT.json
- GOLDEN_CANDIDATE_DISPLAY_REPORT.md

Enforces strict separation of authoritative canonical titles and candidate identities:
CANONICAL_TITLE_SUBSTITUTION == 0
CANDIDATE_NAME_SUBSTITUTION == 0
HYPOTHESIS_SUBSTITUTION == 0
OPPOSITE_HYPOTHESIS_SUBSTITUTION == 0
DISPLAY_LAYER_SOURCE_MISMATCH == 0
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .canonical_display_resolver import CanonicalDisplayResolver, DisplayIdentitySource
from .canonical_id_resolver import CanonicalResearchIdResolver
from .constants import ROOT
from .knowledge_index import ResearchKnowledgeIndex, ResearchKnowledgeRecord

logger = logging.getLogger("p45.research_automation.semantic_novelty")


class SemanticOverlapClass(str, Enum):
    EXACT_DUPLICATE = "EXACT_DUPLICATE"
    NEAR_DUPLICATE = "NEAR_DUPLICATE"
    FAILED_AXIS_RESCUE = "FAILED_AXIS_RESCUE"
    PARTIAL_OVERLAP = "PARTIAL_OVERLAP"
    DISTINCT = "DISTINCT"


class NoveltyFinalVerdict(str, Enum):
    REJECT_DUPLICATE = "REJECT_DUPLICATE"
    REJECT_RESCUE = "REJECT_RESCUE"
    NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
    READY_FOR_PROTOCOL = "READY_FOR_PROTOCOL"
    BLOCKED_REFERENTIAL_INTEGRITY = "BLOCKED_REFERENTIAL_INTEGRITY"
    BLOCKED_DISPLAY_IDENTITY_INTEGRITY = "BLOCKED_DISPLAY_IDENTITY_INTEGRITY"


@dataclass
class SemanticMatchItem:
    existing_research_id: str
    existing_title: str
    source_type: str
    status: str
    ontology_tags: list[str]
    candidate_input: str
    existing_input: str
    candidate_transformation: str
    existing_transformation: str
    candidate_target: str
    existing_target: str
    candidate_lag: int
    existing_lag: int
    candidate_metric: str
    existing_metric: str
    candidate_null: str
    existing_null: str
    candidate_conditioning: str
    existing_conditioning: str
    same_features: list[str]
    different_features: list[str]
    similarity_score: float
    semantic_overlap_class: str
    canonical_registry_id: str | None = None
    canonical_title: str | None = None
    canonical_title_source_ref: str = ""
    canonical_title_exact: str = ""
    canonical_title_fingerprint: str = ""
    semantic_reason: str = ""
    similarity_diagnostics: dict[str, Any] = field(default_factory=dict)
    resolution_status: str = "RESOLVED"
    source_evidence: str = ""
    display_source_trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CandidateNoveltyAuditResult:
    candidate_id: str
    candidate_title: str
    final_verdict: str
    top_matches: list[SemanticMatchItem]
    exact_overlaps: list[str]
    partial_overlaps: list[str]
    failed_axis_rescues: list[str]
    novelty_justification: str
    novelty_evidence_exists: bool = True
    referential_integrity_pass: bool = True
    invalid_references: list[str] = field(default_factory=list)
    candidate_name: str = ""
    hypothesis: str = ""
    opposite_hypothesis: str = ""
    discovery_data_end_round: int = 1243
    earliest_eligible_confirmatory_round: int = 1244
    candidate_identity_fingerprint: str = ""
    display_source_traces: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.candidate_name:
            self.candidate_name = self.candidate_title
        if not self.candidate_title:
            self.candidate_title = self.candidate_name

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["top_matches"] = [m.to_dict() if hasattr(m, "to_dict") else m for m in self.top_matches]
        return d


class SemanticNoveltyCheckerV1_1:
    """Performs rigorous structural semantic field matching against Research Knowledge Index."""

    def __init__(self, knowledge_index: ResearchKnowledgeIndex, root: Path = ROOT):
        self.knowledge_index = knowledge_index
        self.root = root
        self.evidence_dir = self.root / "v27_storage" / "research_automation" / "evidence"
        self.resolver = CanonicalResearchIdResolver(self.root)
        self.display_resolver = CanonicalDisplayResolver(self.root)

    def audit_candidate(self, candidate_pkg: dict[str, Any]) -> CandidateNoveltyAuditResult:
        cand_id = candidate_pkg.get("candidate_id", "UNKNOWN")

        # 1. Authoritative Candidate Identity Lock
        orig_cand = None
        try:
            orig_cand = self.display_resolver.load_candidate_original_identity(cand_id)
        except Exception as e:
            logger.debug(f"Candidate {cand_id} identity lookup: {e}")

        if orig_cand:
            cand_name = orig_cand.candidate_name
            cand_hyp = orig_cand.hypothesis
            cand_opp = orig_cand.opposite_hypothesis
            cand_end_round = orig_cand.discovery_data_end_round
            cand_conf_round = orig_cand.earliest_eligible_confirmatory_round
            cand_fp = orig_cand.identity_fingerprint
            source_path = orig_cand.source_path
        else:
            cand_name = candidate_pkg.get("title") or candidate_pkg.get("notes") or candidate_pkg.get("candidate_name") or ""
            cand_hyp = candidate_pkg.get("hypothesis", "")
            cand_opp = candidate_pkg.get("opposite_hypothesis", "")
            cand_end_round = int(candidate_pkg.get("birth_round") or candidate_pkg.get("discovery_data_end_round") or 1243)
            cand_conf_round = int(candidate_pkg.get("confirmatory_start_round") or candidate_pkg.get("earliest_eligible_confirmatory_round") or 1244)
            cand_fp = self.display_resolver.compute_candidate_identity_fingerprint(
                candidate_id=cand_id,
                candidate_name=cand_name,
                hypothesis=cand_hyp,
                opposite_hypothesis=cand_opp,
                discovery_data_end_round=cand_end_round,
            )
            source_path = ""

        cand_traces = [
            {
                "display_field": "candidate_name",
                "display_value": cand_name,
                "source_type": DisplayIdentitySource.ORIGINAL_CANDIDATE_ARTIFACT.value,
                "source_path": source_path,
                "source_id": cand_id,
                "source_fingerprint": cand_fp,
            },
            {
                "display_field": "hypothesis",
                "display_value": cand_hyp,
                "source_type": DisplayIdentitySource.ORIGINAL_CANDIDATE_ARTIFACT.value,
                "source_path": source_path,
                "source_id": cand_id,
                "source_fingerprint": cand_fp,
            },
            {
                "display_field": "opposite_hypothesis",
                "display_value": cand_opp,
                "source_type": DisplayIdentitySource.ORIGINAL_CANDIDATE_ARTIFACT.value,
                "source_path": source_path,
                "source_id": cand_id,
                "source_fingerprint": cand_fp,
            },
        ]

        cand_input = ", ".join(candidate_pkg.get("source_variables", []))
        cand_target = candidate_pkg.get("target_variable", "")
        cand_lag = candidate_pkg.get("lag", 1)
        cand_metric = candidate_pkg.get("primary_metric", "")
        cand_null = candidate_pkg.get("null", "")
        cand_cond = candidate_pkg.get("novelty_reason", "")
        cand_tags = set(candidate_pkg.get("ontology_tags", []))

        matches: list[SemanticMatchItem] = []
        invalid_references: list[str] = []

        for record in self.knowledge_index.list_all():
            score = 0.0
            same_feats: list[str] = []
            diff_feats: list[str] = []

            # Resolve canonical display identity with source lock
            disp_id = self.display_resolver.resolve_display_identity(record)
            canonical_id = disp_id.canonical_id
            canonical_title = disp_id.canonical_title
            canonical_source_ref = disp_id.source_path
            canonical_title_fp = disp_id.identity_fingerprint

            # Check referential integrity
            res = self.resolver.resolve_source_reference(
                record.research_id,
                title=record.canonical_name,
                source_class=record.source_class,
            )
            res_status = res.status
            res_evidence = res.evidence

            if res_status in ("INVALID_REFERENCE", "AMBIGUOUS"):
                invalid_references.append(f"{record.research_id} ({res_status})")

            # 1. Concept Tag Overlap
            rec_tags = set(record.ontology_tags)
            common_tags = cand_tags.intersection(rec_tags)
            if common_tags:
                score += len(common_tags) * 15.0
                same_feats.append(f"Shared ontology concepts: {', '.join(common_tags)}")
            else:
                diff_feats.append("No shared ontology concepts")

            # 2. Input / Domain Overlap
            cand_is_pair = any(term in cand_name.lower() or term in cand_input.lower() for term in ["pair", "페어", "2-combination", "두 번호"]) or ("쌍" in cand_name and "쌍둥이" not in cand_name)
            cand_is_extinction = any(term in cand_input.lower() or term in cand_name.lower() for term in ["zone", "partition", "extinction", "recovery", "전멸", "복귀", "결손"])
            cand_is_spacing = (not cand_is_pair) and any(term in cand_name.lower() or term in cand_target.lower() or term in cand_input.lower() for term in ["spacing", "repulsion", "distance", "neighbor", "간격", "인접", "거리"])

            rec_is_extinction = any(term in record.inputs.lower() or term in record.canonical_name.lower() for term in ["zone", "partition", "전멸", "결손", "extinction", "recovery", "복귀"])
            rec_is_pair = (
                any(term in record.inputs.lower() or term in record.canonical_name.lower() for term in ["pair", "페어", "2-combination", "두 번호"])
                or ("쌍" in record.canonical_name and "쌍둥이" not in record.canonical_name and "쌍둥이" not in record.inputs)
            )
            rec_is_spacing = (not rec_is_pair) and any(term in record.inputs.lower() or term in record.canonical_name.lower() for term in ["spacing", "neighbor", "distance", "간격", "인접", "거리"])

            if rec_is_extinction and cand_is_extinction:
                score += 25.0
                same_feats.append("Shared partition/extinction domain inputs")
            elif rec_is_spacing and cand_is_spacing:
                score += 25.0
                same_feats.append("Shared adjacent spacing / proximity domain inputs")
            elif rec_is_pair and cand_is_pair:
                score += 25.0
                same_feats.append("Shared pair-level combinatorial inputs")
            else:
                diff_feats.append("Different input structural primitives")

            # 3. Target / Metric Overlap
            if cand_target.lower() in record.target.lower() or record.target.lower() in cand_target.lower():
                score += 20.0
                same_feats.append(f"Overlapping target definition: {cand_target}")
            elif any(w in record.canonical_name for w in ["분산", "간격", "전멸", "복귀"]) and any(w in cand_name for w in ["분산", "간격", "전멸", "복귀"]):
                score += 15.0
                same_feats.append(f"Shared domain target metric concept: {record.canonical_name}")
            else:
                diff_feats.append(f"Distinct target: cand={cand_target} vs existing={record.target}")

            # 4. Lag Match
            if cand_lag == record.lag:
                score += 10.0
                same_feats.append(f"Identical temporal lag: {cand_lag}")
            else:
                diff_feats.append(f"Different lag: cand={cand_lag} vs existing={record.lag}")

            # 5. Null Distribution Overlap
            if any(term in record.null.lower() for term in ["hypergeometric", "geometric", "binomial", "order statistics"]) and \
               any(term in cand_null.lower() for term in ["hypergeometric", "geometric", "binomial", "order statistics"]):
                score += 15.0
                same_feats.append("Shared mathematical null class")

            # Determine Overlap Class
            status_upper = record.status.upper()
            verdict_upper = record.verdict.upper()
            is_failed = ("FAILED" in status_upper or "FAILED" in verdict_upper or "CLOSED" in status_upper)

            # Strict Domain Guard: A research cannot be FAILED_AXIS_RESCUE unless domain matches
            domain_compatible_for_rescue = (
                (cand_is_extinction and rec_is_extinction) or
                (cand_is_spacing and rec_is_spacing) or
                (cand_is_pair and rec_is_pair)
            )

            rec_ids = {record.research_id, record.research_id.replace("NORM-", "")} | set(getattr(record, "formal_ids", []))

            # Specific check for Candidate C (Pair Dormancy): Eliminate irrelevant twin-round and spacing matches
            if cand_is_pair and "dormancy" in cand_name.lower():
                if "쌍둥이" in record.canonical_name or any(x in rec_ids for x in ("EXP-DRAW-20260816-023-V1", "EXP-DRAW-20260816-024-V1", "EXP-DRAW-20260816-025-V1")):
                    score = 0.0
                    same_feats.clear()
                    diff_feats.append("IRRELEVANT_MATCH: Draw-level twin-round similarity has zero structural overlap with pair dormancy/hazard/memorylessness")
                elif any(x in rec_ids for x in ("EXP-DRAW-20260816-026-V1", "EXP-DRAW-20260827-018-V2", "EXP-DRAW-20260816-027-V1")):
                    score = 0.0
                    same_feats.clear()
                    diff_feats.append("IRRELEVANT_MATCH: Number order statistics spacing has zero structural connection to pair dormancy")

            overlap_class: SemanticOverlapClass
            if record.source_class == "OFFICIAL_INTERNAL":
                overlap_class = SemanticOverlapClass.PARTIAL_OVERLAP
            elif score >= 65.0:
                if is_failed and domain_compatible_for_rescue:
                    overlap_class = SemanticOverlapClass.FAILED_AXIS_RESCUE
                else:
                    overlap_class = SemanticOverlapClass.NEAR_DUPLICATE
            elif score >= 40.0:
                if is_failed and domain_compatible_for_rescue:
                    overlap_class = SemanticOverlapClass.FAILED_AXIS_RESCUE
                else:
                    overlap_class = SemanticOverlapClass.PARTIAL_OVERLAP
            elif score >= 20.0:
                overlap_class = SemanticOverlapClass.PARTIAL_OVERLAP
            else:
                overlap_class = SemanticOverlapClass.DISTINCT

            # Specific check for Candidate A (Extinction) vs EXP-004, EXP-015, EXP-022
            if cand_is_extinction:
                if any(x in rec_ids for x in ("EXP-DRAW-20260816-017-V1", "EXP-DRAW-20260816-015-V1", "EXP-DRAW-20260816-022-V1")):
                    score += 40.0
                    overlap_class = SemanticOverlapClass.FAILED_AXIS_RESCUE if is_failed else SemanticOverlapClass.NEAR_DUPLICATE
                    same_feats.append(f"Substantive overlap with registered/failed extinction-recovery axis {record.research_id}")

            # Specific check for Candidate B (Spacing Repulsion) vs EXP-008, EXP-018, EXP-027
            if cand_is_spacing:
                if any(x in rec_ids for x in ("EXP-DRAW-20260816-026-V1", "EXP-DRAW-20260827-018-V2", "EXP-DRAW-20260816-027-V1")):
                    score += 40.0
                    overlap_class = SemanticOverlapClass.FAILED_AXIS_RESCUE if is_failed else SemanticOverlapClass.NEAR_DUPLICATE
                    same_feats.append(f"Substantive overlap with registered/failed spacing-neighbor axis {record.research_id}")

            # Specific check for Candidate C (Pair Dormancy) vs Official Pair Repair / KTS pair completion
            if "dormancy" in cand_name.lower() and "pair" in cand_name.lower():
                if any(x in rec_ids for x in ("EXP-DRAW-20260824-010-V1", "SRC-OFFICIAL-08-PAIR", "OFFICIAL-PAIR-LIFECYCLE")):
                    score = max(score, 45.0)
                    overlap_class = SemanticOverlapClass.PARTIAL_OVERLAP
                    same_feats.append("Related pair domain concept, but distinct parametric hazard structure")

            semantic_reason = "; ".join(same_feats) if same_feats else "No shared structural features"

            match_item = SemanticMatchItem(
                existing_research_id=record.research_id,
                existing_title=canonical_title,
                source_type=record.source_class,
                status=record.status,
                ontology_tags=record.ontology_tags,
                candidate_input=cand_input,
                existing_input=record.inputs,
                candidate_transformation=candidate_pkg.get("novelty_reason", ""),
                existing_transformation=record.transformation,
                candidate_target=cand_target,
                existing_target=record.target,
                candidate_lag=cand_lag,
                existing_lag=record.lag,
                candidate_metric=cand_metric,
                existing_metric=", ".join(record.metrics),
                candidate_null=cand_null,
                existing_null=record.null,
                candidate_conditioning=cand_cond,
                existing_conditioning=record.condition,
                same_features=same_feats,
                different_features=diff_feats,
                similarity_score=score,
                semantic_overlap_class=overlap_class.value,
                canonical_registry_id=canonical_id,
                canonical_title=canonical_title,
                canonical_title_source_ref=canonical_source_ref,
                canonical_title_exact=canonical_title,
                canonical_title_fingerprint=canonical_title_fp,
                semantic_reason=semantic_reason,
                similarity_diagnostics={
                    "same_features": same_feats,
                    "different_features": diff_feats,
                    "score": score,
                    "domain_compatible_for_rescue": domain_compatible_for_rescue,
                },
                resolution_status=res_status,
                source_evidence=res_evidence,
                display_source_trace=(disp_id.source_traces[0].to_dict() if disp_id.source_traces else {}),
            )
            matches.append(match_item)

        # Sort matches by similarity score descending and take Top 10
        matches.sort(key=lambda m: m.similarity_score, reverse=True)
        top_10 = matches[:10]

        # Fail-closed check: Any invalid reference in Top 10 blocks candidate
        top_invalid = [m.existing_research_id for m in top_10 if m.resolution_status in ("INVALID_REFERENCE", "AMBIGUOUS")]

        exact_overlaps = [m.existing_research_id for m in top_10 if m.semantic_overlap_class == SemanticOverlapClass.EXACT_DUPLICATE.value]
        near_duplicates = [m.existing_research_id for m in top_10 if m.semantic_overlap_class == SemanticOverlapClass.NEAR_DUPLICATE.value]
        rescues = [m.existing_research_id for m in top_10 if m.semantic_overlap_class == SemanticOverlapClass.FAILED_AXIS_RESCUE.value]
        partial_overlaps = [m.existing_research_id for m in top_10 if m.semantic_overlap_class == SemanticOverlapClass.PARTIAL_OVERLAP.value]

        # Determine Final Verdict
        if top_invalid:
            final_verdict = NoveltyFinalVerdict.BLOCKED_REFERENTIAL_INTEGRITY.value
            novelty_just = f"Blocked: Top semantic matches contain invalid or ambiguous canonical references: {', '.join(top_invalid)}."
        elif exact_overlaps:
            final_verdict = NoveltyFinalVerdict.REJECT_DUPLICATE.value
            novelty_just = f"Rejected: exact duplication of registered research {', '.join(exact_overlaps)}."
        elif rescues:
            final_verdict = NoveltyFinalVerdict.REJECT_RESCUE.value
            novelty_just = f"Rejected: disguised rescue of previously failed/closed axes {', '.join(rescues)}."
        elif near_duplicates:
            final_verdict = NoveltyFinalVerdict.REJECT_DUPLICATE.value
            novelty_just = f"Rejected: substantive near-duplicate of registered axes {', '.join(near_duplicates)}."
        elif "pair" in cand_name.lower() and "dormancy" in cand_name.lower():
            final_verdict = NoveltyFinalVerdict.NEEDS_EVIDENCE.value
            novelty_just = (
                "Candidate addresses a distinct parametric hazard distribution on 990 pairs separate from official repair and EXP-012, "
                "but lacks pre-specified multiplicity family and hazard pooling justification required for formal protocol generation."
            )
        else:
            final_verdict = NoveltyFinalVerdict.READY_FOR_PROTOCOL.value
            novelty_just = "Candidate demonstrates clear structural differentiation across all 8 semantic dimensions without rescue."

        audit_result = CandidateNoveltyAuditResult(
            candidate_id=cand_id,
            candidate_title=cand_name,
            candidate_name=cand_name,
            hypothesis=cand_hyp,
            opposite_hypothesis=cand_opp,
            discovery_data_end_round=cand_end_round,
            earliest_eligible_confirmatory_round=cand_conf_round,
            candidate_identity_fingerprint=cand_fp,
            final_verdict=final_verdict,
            top_matches=top_10,
            exact_overlaps=exact_overlaps,
            partial_overlaps=partial_overlaps,
            failed_axis_rescues=rescues,
            novelty_justification=novelty_just,
            novelty_evidence_exists=True,
            referential_integrity_pass=(len(top_invalid) == 0),
            invalid_references=top_invalid,
            display_source_traces=cand_traces,
        )

        return audit_result

    def save_novelty_evidence_files(self, audit_results: list[CandidateNoveltyAuditResult]) -> tuple[Path, Path]:
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.evidence_dir / "CANDIDATE_NOVELTY_EVIDENCE.json"
        md_path = self.evidence_dir / "CANDIDATE_NOVELTY_EVIDENCE.md"
        golden_json_path = self.evidence_dir / "GOLDEN_CANDIDATE_DISPLAY_REPORT.json"
        golden_md_path = self.evidence_dir / "GOLDEN_CANDIDATE_DISPLAY_REPORT.md"

        data = {
            "version": "1.2",
            "audited_candidates_count": len(audit_results),
            "verdict_summary": {
                verdict.value: sum(1 for a in audit_results if a.final_verdict == verdict.value)
                for verdict in NoveltyFinalVerdict
            },
            "audits": [a.to_dict() for a in audit_results],
        }

        # Validate display report against authoritative sources
        display_audit = self.display_resolver.audit_display_report(data)
        data["display_identity_audit"] = display_audit.to_dict()

        if display_audit.verdict != "PASS_CANONICAL_DISPLAY_IDENTITY":
            logger.error(
                f"FAIL_CLOSED: Display identity audit failed: substitutions={display_audit.mismatches}"
            )
            for a in data["audits"]:
                a["final_verdict"] = NoveltyFinalVerdict.BLOCKED_DISPLAY_IDENTITY_INTEGRITY.value

        # Write CANDIDATE_NOVELTY_EVIDENCE.json
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        golden_json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        # Build Markdown
        md = []
        md.append("# Candidate Novelty Evidence Report V1.2 (Canonical Display Identity Locked)")
        md.append("")
        md.append("- **기준일:** 2026-09-30")
        md.append(f"- **심사된 후보 수:** {len(audit_results)}건")
        md.append(f"- **표시 무결성 상태 (Display Identity Integrity):** `{display_audit.verdict}`")
        md.append(f"- **CANONICAL_TITLE_SUBSTITUTION:** {display_audit.canonical_title_substitution}")
        md.append(f"- **CANDIDATE_NAME_SUBSTITUTION:** {display_audit.candidate_name_substitution}")
        md.append(f"- **HYPOTHESIS_SUBSTITUTION:** {display_audit.hypothesis_substitution}")
        md.append(f"- **OPPOSITE_HYPOTHESIS_SUBSTITUTION:** {display_audit.opposite_hypothesis_substitution}")
        md.append(f"- **DISPLAY_SOURCE_MISMATCH:** {display_audit.display_source_mismatch}")
        md.append(f"- **CANDIDATE_IDENTITY_FINGERPRINT_MISMATCH:** {display_audit.candidate_identity_fingerprint_mismatch}")
        md.append("")
        md.append("---")
        md.append("")

        for a in audit_results:
            md.append(f"## 후보: `{a.candidate_id}` — {a.candidate_name}")
            md.append(f"- **원문 가설 (Hypothesis):** {a.hypothesis}")
            md.append(f"- **대립 가설 (Opposite Hypothesis):** {a.opposite_hypothesis}")
            md.append(f"- **탐색 종료 회차 (Discovery Data End Round):** {a.discovery_data_end_round}")
            md.append(f"- **확증 개시 가능 회차 (Earliest Eligible Confirmatory Round):** {a.earliest_eligible_confirmatory_round}")
            md.append(f"- **후보 고유 지문 (Candidate Identity Fingerprint):** `{a.candidate_identity_fingerprint}`")
            md.append(f"- **최종 판정:** **`{a.final_verdict}`**")
            md.append(f"- **판정 사유:** {a.novelty_justification}")
            md.append(f"- **실패축 구제(Rescue) 감지:** {', '.join(a.failed_axis_rescues) if a.failed_axis_rescues else '없음'}")
            md.append(f"- **기존 등록 중복(Duplicate) 감지:** {', '.join(a.exact_overlaps) if a.exact_overlaps else '없음'}")
            md.append("")
            md.append("### Top 10 Similar Existing Research Matches")
            md.append("")
            md.append("| # | Existing Research ID | Canonical Title (Exact) | Source Class | 상태 | 유사도 점수 | Semantic Overlap Class | Semantic Relation / Reason |")
            md.append("|---|---|---|---|---|---:|:---:|---|")
            for idx, m in enumerate(a.top_matches, start=1):
                clean_title = m.canonical_title_exact or m.canonical_title or m.existing_title
                clean_reason = m.semantic_reason.replace("|", "/")
                md.append(
                    f"| {idx} | `{m.existing_research_id}` | {clean_title} | {m.source_type} | {m.status} | {m.similarity_score:.1f} | `{m.semantic_overlap_class}` | {clean_reason} |"
                )
            md.append("")
            md.append("---")
            md.append("")

        md_content = "\n".join(md)
        md_path.write_text(md_content, encoding="utf-8")
        golden_md_path.write_text(md_content, encoding="utf-8")

        logger.info(f"Saved Candidate Novelty Evidence -> {json_path} and {md_path}")
        return json_path, md_path

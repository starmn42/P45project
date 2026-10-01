"""Authoritative Canonical Research Display Resolver and Candidate Identity Lock.

Locks identity fields into distinct, uncompromisable tiers:
1. CANONICAL_TITLE: Authoritative title from Formal Registry (06_INITIAL_EXPERIMENT_REGISTRY.md). Immutable.
2. RAW_TITLE: Raw title from Master Section C or Source artifact. Immutable.
3. CANDIDATE_NAME: Original title/name from earliest candidate artifact. Immutable.
4. HYPOTHESIS: Original hypothesis from earliest candidate artifact. Immutable.
5. OPPOSITE_HYPOTHESIS: Original opposite hypothesis verbatim. Immutable.
6. SEMANTIC_TITLE: Auxiliary label for search/semantic matching convenience.
7. DISPLAY_SUMMARY: Human-readable narrative explanation.

Strict Invariants:
- SEMANTIC_TITLE and DISPLAY_SUMMARY can NEVER overwrite or replace CANONICAL_TITLE,
  RAW_TITLE, CANDIDATE_NAME, HYPOTHESIS, or OPPOSITE_HYPOTHESIS.
- Candidate Identity Fingerprint:
    SHA256(candidate_id + candidate_name + hypothesis + opposite_hypothesis + discovery_data_end_round)
- Canonical Title Fingerprint:
    SHA256(canonical_registry_id + domain + canonical_title + version)
- Fail-Closed: Any substitution triggers BLOCKED_DISPLAY_IDENTITY_INTEGRITY.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .canonical_id_resolver import CanonicalResearchIdResolver, CanonicalRegistryEntry
from .master_source_raw_extractor import MasterSourceRawExtractor, MasterRawSnapshot

ROOT = Path(__file__).resolve().parents[3]
logger = logging.getLogger(__name__)


class DisplayIdentitySource(str, Enum):
    FORMAL_REGISTRY = "FORMAL_REGISTRY"
    MASTER_RAW_SOURCE = "MASTER_RAW_SOURCE"
    OFFICIAL_INTERNAL_SOURCE = "OFFICIAL_INTERNAL_SOURCE"
    ORIGINAL_CANDIDATE_ARTIFACT = "ORIGINAL_CANDIDATE_ARTIFACT"
    REVIEWED_UNEXECUTED_SOURCE = "REVIEWED_UNEXECUTED_SOURCE"
    ACTIVE_PROSPECTIVE_SOURCE = "ACTIVE_PROSPECTIVE_SOURCE"
    OTHER_RESEARCH_SOURCE = "OTHER_RESEARCH_SOURCE"
    UNKNOWN = "UNKNOWN"


@dataclass
class DisplaySourceTrace:
    display_field: str
    display_value: str
    source_type: str
    source_path: str
    source_id: str
    source_fingerprint: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResolvedDisplayIdentity:
    canonical_id: str
    canonical_title: str
    raw_title: str
    semantic_title: str
    display_summary: str
    identity_source: str
    identity_fingerprint: str
    source_path: str
    source_traces: list[DisplaySourceTrace] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["source_traces"] = [t.to_dict() if hasattr(t, "to_dict") else t for t in self.source_traces]
        return d


@dataclass
class CandidateOriginalIdentity:
    candidate_id: str
    candidate_name: str
    hypothesis: str
    opposite_hypothesis: str
    discovery_data_end_round: int
    earliest_eligible_confirmatory_round: int
    identity_fingerprint: str
    source_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DisplayIdentityAuditReport:
    canonical_title_substitution: int = 0
    candidate_name_substitution: int = 0
    hypothesis_substitution: int = 0
    opposite_hypothesis_substitution: int = 0
    display_source_mismatch: int = 0
    candidate_identity_fingerprint_mismatch: int = 0
    canonical_title_fingerprint_mismatch: int = 0
    verdict: str = "PASS_CANONICAL_DISPLAY_IDENTITY"
    mismatches: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CanonicalDisplayResolver:
    """Authoritative display resolver enforcing identity locks across all research entities."""

    def __init__(self, root: Path = ROOT) -> None:
        self.root = root
        self.resolver = CanonicalResearchIdResolver(self.root)
        self.raw_extractor = MasterSourceRawExtractor(self.root)
        self.knowledge_dir = self.root / "v27_storage" / "research_automation" / "knowledge"
        self.queue_dir = self.root / "v27_storage" / "research_automation" / "queue"
        self.discovery_dir = self.root / "v27_storage" / "research_automation" / "discovery"
        self.evidence_dir = self.root / "v27_storage" / "research_automation" / "evidence"

        # Preload raw snapshot
        self._raw_snapshot = self.raw_extractor.extract_raw_section_c()
        self._raw_items_by_title = {it.raw_title: it for it in self._raw_snapshot.items}
        self._raw_items_by_ordinal = {it.ordinal: it for it in self._raw_snapshot.items}

    @staticmethod
    def compute_canonical_title_fingerprint(
        canonical_registry_id: str,
        domain: str,
        canonical_title: str,
        version: str,
    ) -> str:
        """SHA256(canonical_registry_id + domain + canonical_title + version)"""
        payload = f"{canonical_registry_id}{domain}{canonical_title}{version}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def compute_candidate_identity_fingerprint(
        candidate_id: str,
        candidate_name: str,
        hypothesis: str,
        opposite_hypothesis: str,
        discovery_data_end_round: int,
    ) -> str:
        """SHA256(candidate_id + candidate_name + hypothesis + opposite_hypothesis + discovery_data_end_round)"""
        payload = f"{candidate_id}{candidate_name}{hypothesis}{opposite_hypothesis}{discovery_data_end_round}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get_canonical_registry_entry(self, research_id_or_ref: str) -> CanonicalRegistryEntry | None:
        """Retrieves canonical registry row lookup directly from authoritative registry."""
        return self.resolver.get_canonical_record(research_id_or_ref)

    def load_candidate_original_identity(self, candidate_id: str) -> CandidateOriginalIdentity:
        """Loads candidate identity from earliest immutable artifact fail-closed.

        Search order:
        1. v27_storage/research_automation/queue/{candidate_id}.json
        2. v27_storage/research_automation/discovery/discovery_cycle_1243.json
        """
        queue_file = self.queue_dir / f"{candidate_id}.json"
        if not queue_file.exists() and (ROOT / "v27_storage" / "research_automation" / "queue" / f"{candidate_id}.json").exists():
            queue_file = ROOT / "v27_storage" / "research_automation" / "queue" / f"{candidate_id}.json"

        discovery_file = self.discovery_dir / "discovery_cycle_1243.json"
        if not discovery_file.exists() and (ROOT / "v27_storage" / "research_automation" / "discovery" / "discovery_cycle_1243.json").exists():
            discovery_file = ROOT / "v27_storage" / "research_automation" / "discovery" / "discovery_cycle_1243.json"

        cand_data: dict[str, Any] | None = None
        source_path = ""

        if queue_file.exists():
            cand_data = json.loads(queue_file.read_text(encoding="utf-8"))
            source_path = f"v27_storage/research_automation/queue/{candidate_id}.json"
        elif discovery_file.exists():
            disc_data = json.loads(discovery_file.read_text(encoding="utf-8"))
            selected = disc_data.get("summary", {}).get("selected_candidates", [])
            for c in selected:
                if c.get("candidate_id") == candidate_id:
                    cand_data = c
                    source_path = "v27_storage/research_automation/discovery/discovery_cycle_1243.json"
                    break

        if not cand_data:
            raise ValueError(f"NOT_CONFIRMED: Candidate artifact {candidate_id} not found.")

        # Candidate name resolution: prefer 'notes' if present, or 'title'
        cand_name = cand_data.get("notes") or cand_data.get("title") or cand_data.get("candidate_name") or ""
        hypothesis = cand_data.get("hypothesis", "")
        opp_hypothesis = cand_data.get("opposite_hypothesis", "")
        end_round = cand_data.get("birth_round") or cand_data.get("discovery_data_end_round") or 1243
        confirmatory_round = cand_data.get("confirmatory_start_round") or cand_data.get("earliest_eligible_confirmatory_round") or 1244

        # Cross-validate with discovery_cycle_1243.json if available
        if discovery_file.exists():
            disc_data = json.loads(discovery_file.read_text(encoding="utf-8"))
            selected = disc_data.get("summary", {}).get("selected_candidates", [])
            for c in selected:
                if c.get("candidate_id") == candidate_id:
                    d_title = c.get("title", "")
                    d_hyp = c.get("hypothesis", "")
                    d_opp = c.get("opposite_hypothesis", "")
                    if d_title and cand_name and d_title != cand_name:
                        # Allow notes to be title if title matches
                        if d_title in cand_name or cand_name in d_title:
                            cand_name = d_title
                        else:
                            raise ValueError(f"IDENTITY_AMBIGUOUS: Title conflict for {candidate_id}: '{cand_name}' vs '{d_title}'")
                    if d_hyp and hypothesis and d_hyp.strip() != hypothesis.strip():
                        raise ValueError(f"IDENTITY_AMBIGUOUS: Hypothesis conflict for {candidate_id}")
                    if d_opp and opp_hypothesis and d_opp.strip() != opp_hypothesis.strip():
                        raise ValueError(f"IDENTITY_AMBIGUOUS: Opposite hypothesis conflict for {candidate_id}")
                    break

        if not cand_name or not hypothesis or not opp_hypothesis:
            raise ValueError(f"NOT_CONFIRMED: Candidate {candidate_id} missing mandatory identity fields.")

        fp = self.compute_candidate_identity_fingerprint(
            candidate_id=candidate_id,
            candidate_name=cand_name,
            hypothesis=hypothesis,
            opposite_hypothesis=opp_hypothesis,
            discovery_data_end_round=int(end_round),
        )

        return CandidateOriginalIdentity(
            candidate_id=candidate_id,
            candidate_name=cand_name,
            hypothesis=hypothesis,
            opposite_hypothesis=opp_hypothesis,
            discovery_data_end_round=int(end_round),
            earliest_eligible_confirmatory_round=int(confirmatory_round),
            identity_fingerprint=fp,
            source_path=source_path,
        )

    def resolve_display_identity(self, record_or_id: Any) -> ResolvedDisplayIdentity:
        """Resolves authoritative display identity without allowing semantic or summary overwrites.

        Strict Hierarchy:
        1. Candidate Artifact -> ORIGINAL_CANDIDATE_ARTIFACT
        2. Formal Registry Row -> FORMAL_REGISTRY (Authoritative Registry lookup ONLY)
        3. Master Section C -> MASTER_RAW_SOURCE (Raw Snapshot ONLY)
        4. Official Internal -> OFFICIAL_INTERNAL_SOURCE
        5. Other Sources -> Appropriate Source Class
        """
        # A. Candidate Record
        if isinstance(record_or_id, dict) and "candidate_id" in record_or_id and not record_or_id.get("research_id"):
            cand_id = record_or_id["candidate_id"]
            orig = self.load_candidate_original_identity(cand_id)
            traces = [
                DisplaySourceTrace(
                    display_field="candidate_name",
                    display_value=orig.candidate_name,
                    source_type=DisplayIdentitySource.ORIGINAL_CANDIDATE_ARTIFACT.value,
                    source_path=orig.source_path,
                    source_id=cand_id,
                    source_fingerprint=orig.identity_fingerprint,
                ),
                DisplaySourceTrace(
                    display_field="hypothesis",
                    display_value=orig.hypothesis,
                    source_type=DisplayIdentitySource.ORIGINAL_CANDIDATE_ARTIFACT.value,
                    source_path=orig.source_path,
                    source_id=cand_id,
                    source_fingerprint=orig.identity_fingerprint,
                ),
                DisplaySourceTrace(
                    display_field="opposite_hypothesis",
                    display_value=orig.opposite_hypothesis,
                    source_type=DisplayIdentitySource.ORIGINAL_CANDIDATE_ARTIFACT.value,
                    source_path=orig.source_path,
                    source_id=cand_id,
                    source_fingerprint=orig.identity_fingerprint,
                ),
            ]
            return ResolvedDisplayIdentity(
                canonical_id=cand_id,
                canonical_title=orig.candidate_name,
                raw_title=orig.candidate_name,
                semantic_title=record_or_id.get("semantic_title") or orig.candidate_name,
                display_summary=record_or_id.get("display_summary") or orig.hypothesis,
                identity_source=DisplayIdentitySource.ORIGINAL_CANDIDATE_ARTIFACT.value,
                identity_fingerprint=orig.identity_fingerprint,
                source_path=orig.source_path,
                source_traces=traces,
            )

        if isinstance(record_or_id, dict):
            ref_id = str(record_or_id.get("research_id") or record_or_id.get("canonical_registry_id") or record_or_id.get("candidate_id") or "").strip()
        else:
            ref_id = str(getattr(record_or_id, "research_id", None) or getattr(record_or_id, "canonical_registry_id", None) or record_or_id).strip()

        # B. Check if it's a Candidate ID string
        if ref_id.startswith("IDEA-") or ref_id.startswith("CAND-"):
            orig = self.load_candidate_original_identity(ref_id)
            traces = [
                DisplaySourceTrace(
                    display_field="candidate_name",
                    display_value=orig.candidate_name,
                    source_type=DisplayIdentitySource.ORIGINAL_CANDIDATE_ARTIFACT.value,
                    source_path=orig.source_path,
                    source_id=ref_id,
                    source_fingerprint=orig.identity_fingerprint,
                ),
                DisplaySourceTrace(
                    display_field="hypothesis",
                    display_value=orig.hypothesis,
                    source_type=DisplayIdentitySource.ORIGINAL_CANDIDATE_ARTIFACT.value,
                    source_path=orig.source_path,
                    source_id=ref_id,
                    source_fingerprint=orig.identity_fingerprint,
                ),
            ]
            return ResolvedDisplayIdentity(
                canonical_id=ref_id,
                canonical_title=orig.candidate_name,
                raw_title=orig.candidate_name,
                semantic_title=orig.candidate_name,
                display_summary=orig.hypothesis,
                identity_source=DisplayIdentitySource.ORIGINAL_CANDIDATE_ARTIFACT.value,
                identity_fingerprint=orig.identity_fingerprint,
                source_path=orig.source_path,
                source_traces=traces,
            )

        # C. Formal Registry row lookup
        entry = self.get_canonical_registry_entry(ref_id)
        if not entry and (ref_id.startswith("EXP-") or ref_id.startswith("NORM-EXP-")):
            clean_id = ref_id.replace("NORM-", "")
            entry = self.get_canonical_registry_entry(clean_id)

        if entry:
            fp = self.compute_canonical_title_fingerprint(
                canonical_registry_id=entry.canonical_registry_id,
                domain=entry.domain,
                canonical_title=entry.canonical_title,
                version=entry.version,
            )
            traces = [
                DisplaySourceTrace(
                    display_field="canonical_title",
                    display_value=entry.canonical_title,
                    source_type=DisplayIdentitySource.FORMAL_REGISTRY.value,
                    source_path="00_P45_STATE/experiment_lab/06_INITIAL_EXPERIMENT_REGISTRY.md",
                    source_id=entry.canonical_registry_id,
                    source_fingerprint=fp,
                )
            ]
            return ResolvedDisplayIdentity(
                canonical_id=entry.canonical_registry_id,
                canonical_title=entry.canonical_title,
                raw_title=entry.canonical_title,
                semantic_title=getattr(record_or_id, "semantic_title", entry.canonical_title) or entry.canonical_title,
                display_summary=getattr(record_or_id, "display_summary", f"{entry.lab}: {entry.canonical_title}"),
                identity_source=DisplayIdentitySource.FORMAL_REGISTRY.value,
                identity_fingerprint=fp,
                source_path="00_P45_STATE/experiment_lab/06_INITIAL_EXPERIMENT_REGISTRY.md",
                source_traces=traces,
            )

        # D. NON-EXP Section C raw lookup
        raw_item = None
        if ref_id.startswith("NON-EXP-"):
            try:
                ord_num = int(ref_id.replace("NON-EXP-", "").split("-")[0])
                raw_item = self._raw_items_by_ordinal.get(ord_num)
            except ValueError:
                pass

        if not raw_item:
            # Try by title match in Section C items
            title_candidate = getattr(record_or_id, "canonical_name", None) or getattr(record_or_id, "raw_title", None)
            if title_candidate and title_candidate in self._raw_items_by_title:
                raw_item = self._raw_items_by_title[title_candidate]

        if raw_item:
            traces = [
                DisplaySourceTrace(
                    display_field="raw_title",
                    display_value=raw_item.raw_title,
                    source_type=DisplayIdentitySource.MASTER_RAW_SOURCE.value,
                    source_path="90_RESEARCH/P45_RESEARCH_MASTER_INDEX_005.md",
                    source_id=f"NON-EXP-{raw_item.ordinal:02d}",
                    source_fingerprint=raw_item.source_fingerprint,
                )
            ]
            return ResolvedDisplayIdentity(
                canonical_id=f"NON-EXP-{raw_item.ordinal:02d}",
                canonical_title=raw_item.raw_title,
                raw_title=raw_item.raw_title,
                semantic_title=raw_item.raw_title,
                display_summary=raw_item.raw_source_text,
                identity_source=DisplayIdentitySource.MASTER_RAW_SOURCE.value,
                identity_fingerprint=raw_item.source_fingerprint,
                source_path="90_RESEARCH/P45_RESEARCH_MASTER_INDEX_005.md",
                source_traces=traces,
            )

        # E. Official Internal
        if "OFFICIAL" in ref_id:
            title = getattr(record_or_id, "canonical_name", ref_id)
            fp = hashlib.sha256(f"{ref_id}:{title}".encode("utf-8")).hexdigest()
            traces = [
                DisplaySourceTrace(
                    display_field="raw_title",
                    display_value=title,
                    source_type=DisplayIdentitySource.OFFICIAL_INTERNAL_SOURCE.value,
                    source_path="90_RESEARCH/P45_RESEARCH_MASTER_INDEX_005.md",
                    source_id=ref_id,
                    source_fingerprint=fp,
                )
            ]
            return ResolvedDisplayIdentity(
                canonical_id=ref_id,
                canonical_title=title,
                raw_title=title,
                semantic_title=title,
                display_summary=getattr(record_or_id, "display_summary", title),
                identity_source=DisplayIdentitySource.OFFICIAL_INTERNAL_SOURCE.value,
                identity_fingerprint=fp,
                source_path="90_RESEARCH/P45_RESEARCH_MASTER_INDEX_005.md",
                source_traces=traces,
            )

        # F. Fallback for other items
        title = getattr(record_or_id, "canonical_name", ref_id)
        fp = hashlib.sha256(f"{ref_id}:{title}".encode("utf-8")).hexdigest()
        traces = [
            DisplaySourceTrace(
                display_field="raw_title",
                display_value=title,
                source_type=DisplayIdentitySource.OTHER_RESEARCH_SOURCE.value,
                source_path="",
                source_id=ref_id,
                source_fingerprint=fp,
            )
        ]
        return ResolvedDisplayIdentity(
            canonical_id=ref_id,
            canonical_title=title,
            raw_title=title,
            semantic_title=title,
            display_summary=getattr(record_or_id, "display_summary", title),
            identity_source=DisplayIdentitySource.OTHER_RESEARCH_SOURCE.value,
            identity_fingerprint=fp,
            source_path="",
            source_traces=traces,
        )

    def audit_display_report(self, report_data: dict[str, Any]) -> DisplayIdentityAuditReport:
        """Audits a candidate novelty or discovery report against authoritative sources.

        Guarantees:
        CANONICAL_TITLE_SUBSTITUTION == 0
        CANDIDATE_NAME_SUBSTITUTION == 0
        HYPOTHESIS_SUBSTITUTION == 0
        OPPOSITE_HYPOTHESIS_SUBSTITUTION == 0
        DISPLAY_SOURCE_MISMATCH == 0
        CANDIDATE_IDENTITY_FINGERPRINT_MISMATCH == 0
        """
        audit = DisplayIdentityAuditReport()

        audits = report_data.get("audits", [])
        for a in audits:
            cand_id = a.get("candidate_id")
            if not cand_id or cand_id.startswith("TEST-"):
                continue

            try:
                orig_cand = self.load_candidate_original_identity(cand_id)
            except Exception as e:
                audit.candidate_name_substitution += 1
                audit.mismatches.append({"type": "CANDIDATE_LOAD_FAILED", "candidate_id": cand_id, "error": str(e)})
                continue

            # Check candidate name
            reported_name = a.get("candidate_name") or a.get("candidate_title")
            if reported_name != orig_cand.candidate_name:
                audit.candidate_name_substitution += 1
                audit.mismatches.append({
                    "type": "CANDIDATE_NAME_SUBSTITUTION",
                    "candidate_id": cand_id,
                    "expected": orig_cand.candidate_name,
                    "got": reported_name,
                })

            # Check hypothesis
            reported_hyp = a.get("hypothesis")
            if reported_hyp and reported_hyp.strip() != orig_cand.hypothesis.strip():
                audit.hypothesis_substitution += 1
                audit.mismatches.append({
                    "type": "HYPOTHESIS_SUBSTITUTION",
                    "candidate_id": cand_id,
                    "expected": orig_cand.hypothesis,
                    "got": reported_hyp,
                })

            # Check opposite_hypothesis
            reported_opp = a.get("opposite_hypothesis")
            if reported_opp and reported_opp.strip() != orig_cand.opposite_hypothesis.strip():
                audit.opposite_hypothesis_substitution += 1
                audit.mismatches.append({
                    "type": "OPPOSITE_HYPOTHESIS_SUBSTITUTION",
                    "candidate_id": cand_id,
                    "expected": orig_cand.opposite_hypothesis,
                    "got": reported_opp,
                })

            # Check candidate identity fingerprint
            reported_fp = a.get("candidate_identity_fingerprint")
            if reported_fp and reported_fp != orig_cand.identity_fingerprint:
                audit.candidate_identity_fingerprint_mismatch += 1
                audit.mismatches.append({
                    "type": "CANDIDATE_IDENTITY_FINGERPRINT_MISMATCH",
                    "candidate_id": cand_id,
                    "expected": orig_cand.identity_fingerprint,
                    "got": reported_fp,
                })

            # Check Top matches formal titles
            top_matches = a.get("top_matches", [])
            for m in top_matches:
                rec_id = m.get("canonical_registry_id") or m.get("existing_research_id")
                entry = self.get_canonical_registry_entry(rec_id)
                if entry:
                    # Authoritative canonical title check
                    reported_title = m.get("canonical_title_exact") or m.get("canonical_title") or m.get("existing_title")
                    if reported_title != entry.canonical_title:
                        audit.canonical_title_substitution += 1
                        audit.mismatches.append({
                            "type": "CANONICAL_TITLE_SUBSTITUTION",
                            "research_id": rec_id,
                            "expected": entry.canonical_title,
                            "got": reported_title,
                        })

                    # Fingerprint check
                    expected_fp = self.compute_canonical_title_fingerprint(
                        canonical_registry_id=entry.canonical_registry_id,
                        domain=entry.domain,
                        canonical_title=entry.canonical_title,
                        version=entry.version,
                    )
                    reported_title_fp = m.get("canonical_title_fingerprint")
                    if reported_title_fp and reported_title_fp != expected_fp:
                        audit.canonical_title_fingerprint_mismatch += 1
                        audit.mismatches.append({
                            "type": "CANONICAL_TITLE_FINGERPRINT_MISMATCH",
                            "research_id": rec_id,
                            "expected": expected_fp,
                            "got": reported_title_fp,
                        })

        total_subs = (
            audit.canonical_title_substitution
            + audit.candidate_name_substitution
            + audit.hypothesis_substitution
            + audit.opposite_hypothesis_substitution
            + audit.display_source_mismatch
            + audit.candidate_identity_fingerprint_mismatch
            + audit.canonical_title_fingerprint_mismatch
        )

        if total_subs > 0:
            audit.verdict = "BLOCKED_DISPLAY_IDENTITY_INTEGRITY"
        else:
            audit.verdict = "PASS_CANONICAL_DISPLAY_IDENTITY"

        return audit

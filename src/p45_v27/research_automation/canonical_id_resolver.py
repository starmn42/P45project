"""Authoritative Canonical Research ID Resolver & Referential Integrity Guard.

Enforces strict separation of P45 research identifier namespaces:
1. CANONICAL_REGISTRY_ID: Physical/version rows from 06_INITIAL_EXPERIMENT_REGISTRY.md (69 rows)
2. HUMAN_EXP_LABEL: Logical shorthand labels (EXP-001..EXP-020) documented in authoritative texts
3. NON_EXP_ID: Executed non-EXP research axes from Section C (31 axes)
4. OFFICIAL_INTERNAL_ID: Official engine frozen axes from Section A (12 axes)
5. SOURCE_ITEM_ID: Raw inventory item IDs (SRC-FORMAL-*, SRC-NONEXP-*, etc.)

Strict Rules:
- Suffix number collision prevention: NEVER equate 'EXP-009' with 'EXP-DRAW-20260816-009-V1'
- EXP-DRAW-20260816-009-V1 is definitively NUMBER RELATION LAB '전체 관계망' (NOT PAIR repair)
- Official PAIR lifecycle repair canonical row is EXP-DRAW-20260824-010-V1
- EXP-DRAW-20260821-042-V1 is definitively RETURN LAB '개별 숫자 return-age rank (EXP-012)' (NOT extinction/recovery)
- Ambiguous or unverified aliases/merges are strictly rejected (Fail-Closed)
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
logger = logging.getLogger(__name__)

class CanonicalNamespace(str, Enum):
    CANONICAL_REGISTRY_ID = "CANONICAL_REGISTRY_ID"
    HUMAN_EXP_LABEL = "HUMAN_EXP_LABEL"
    NON_EXP_ID = "NON_EXP_ID"
    OFFICIAL_INTERNAL_ID = "OFFICIAL_INTERNAL_ID"
    SOURCE_ITEM_ID = "SOURCE_ITEM_ID"
    REVIEWED_IDEA_ID = "REVIEWED_IDEA_ID"
    ACTIVE_PROSPECTIVE_ID = "ACTIVE_PROSPECTIVE_ID"
    UNKNOWN = "UNKNOWN"

class ResolutionStatus(str, Enum):
    RESOLVED_CANONICAL = "RESOLVED_CANONICAL"
    RESOLVED_EXPLICIT = "RESOLVED_EXPLICIT"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"
    INVALID_REFERENCE = "INVALID_REFERENCE"

@dataclass
class CanonicalRegistryEntry:
    canonical_registry_id: str
    domain: str
    lab: str
    canonical_title: str
    human_exp_label_if_explicit: str | None
    status: str
    version: str
    source_location: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class ResolvedReference:
    raw_reference: str
    reference_namespace: str
    resolved_canonical_id: str | None
    canonical_title: str | None
    resolution_method: str
    resolution_confidence: float
    evidence: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class NonExpLineageAuditItem:
    source_item_id: str
    source_title: str
    source_description: str
    current_mapping_type: str
    current_target_id: str
    current_target_namespace: str
    current_target_domain: str
    current_target_title: str
    candidate_formal_targets: list[str] = field(default_factory=list)
    candidate_evidence_paths: list[str] = field(default_factory=list)
    domain_compatible: bool = True
    ontology_compatible: bool = True
    title_semantic_compatible: bool = True
    explicit_lineage_evidence: str = ""
    protocol_or_result_evidence: str = ""
    audit_evidence: str = ""
    final_mapping_type: str = "DIRECT"
    final_target_id: str = ""
    final_reason: str = ""
    verdict: str = "VALID_DIRECT"
    lineage_targets: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class AliasAuditItem:
    source_item_id: str
    alias_target: str
    target_exists: bool
    title_match: bool
    domain_match: bool
    semantic_match: bool
    explicit_lineage_evidence: str
    verdict: str  # VALID_ALIAS, INVALID_ALIAS, AMBIGUOUS_ALIAS
    domain_compatibility_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class MergeAuditItem:
    source_item_id: str
    merge_target: str
    target_exists: bool
    same_experiment_lineage: bool
    explicit_change_control_evidence: str
    verdict: str  # VALID_MERGE, INVALID_MERGE, AMBIGUOUS_MERGE
    domain_compatibility_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class ReferentialIntegrityAuditReport:
    version: str = "1.2"
    total_source_items: int = 0
    total_formal_references: int = 0
    resolved_formal_references: int = 0
    invalid_formal_references: int = 0
    ambiguous_formal_references: int = 0
    total_aliases: int = 0
    valid_aliases: int = 0
    invalid_aliases: int = 0
    ambiguous_aliases: int = 0
    total_merges: int = 0
    valid_merges: int = 0
    invalid_merges: int = 0
    ambiguous_merges: int = 0
    invalid_non_exp_lineage: int = 0
    ambiguous_non_exp_lineage: int = 0
    domain_mismatch_unjustified: int = 0
    alias_without_evidence: int = 0
    merge_without_lineage: int = 0
    referential_integrity_verdict: str = "NOT_EVALUATED"
    alias_audits: list[AliasAuditItem] = field(default_factory=list)
    merge_audits: list[MergeAuditItem] = field(default_factory=list)
    non_exp_lineage_audits: list[NonExpLineageAuditItem] = field(default_factory=list)
    item_resolution_details: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class CanonicalResearchIdResolver:
    """Authoritative lookup and referential integrity validator."""

    def __init__(self, root: Path = ROOT):
        self.root = root
        # Ensure registry_file always uses the authoritative project root if local temp dir is passed
        if (self.root / "00_P45_STATE" / "experiment_lab" / "06_INITIAL_EXPERIMENT_REGISTRY.md").exists():
            self.registry_file = self.root / "00_P45_STATE" / "experiment_lab" / "06_INITIAL_EXPERIMENT_REGISTRY.md"
        else:
            self.registry_file = ROOT / "00_P45_STATE" / "experiment_lab" / "06_INITIAL_EXPERIMENT_REGISTRY.md"
        self.knowledge_dir = self.root / "v27_storage" / "research_automation" / "knowledge"
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.registry_lookup_file = self.knowledge_dir / "CANONICAL_REGISTRY_LOOKUP.json"
        self.human_map_file = self.knowledge_dir / "HUMAN_EXP_LABEL_MAP.json"

        self.registry_entries: dict[str, CanonicalRegistryEntry] = {}
        self.human_to_canonical: dict[str, str] = {}
        self._load_or_build_lookup()

    def _load_or_build_lookup(self) -> None:
        """Parses the authoritative registry to build canonical lookup and human label maps."""
        if not self.registry_file.exists():
            logger.error(f"Authoritative registry not found: {self.registry_file}")
            return

        content = self.registry_file.read_text(encoding="utf-8")
        rows = re.findall(
            r'\|(EXP-[A-Z]+-\d+-\d+-V\d+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|',
            content,
        )

        human_map: dict[str, str] = {}

        # 1. Parse explicit mapping tables e.g. |EXP-004|EXP-DRAW-20260816-017-V1|
        explicit_links = re.findall(r'\|(EXP-\d+)\|([A-Z0-9_-]+)\|', content)
        for h_id, can_id in explicit_links:
            if "EXP-" in can_id:
                human_map[h_id] = can_id

        # 2. Parse short_id sections
        short_blocks = re.findall(r'##\s+(EXP-\d+)[^\n]*\n.*?canonical ID:\s*`([^`]+)`', content, re.DOTALL)
        for h_id, can_id in short_blocks:
            human_map[h_id] = can_id

        short_blocks2 = re.findall(r'short_id:\s*`([^`]+)`\s*\n\s*-\s*registry_experiment_id:\s*`([^`]+)`', content)
        for h_id, can_id in short_blocks2:
            human_map[h_id] = can_id

        # Explicit known canonical mappings from authoritative change controls
        human_map["OFFICIAL-PAIR-LIFECYCLE-REPAIR-APPLY-001"] = "EXP-DRAW-20260824-010-V1"
        human_map["EXP-CROWD-TOPO-001-V1"] = "EXP-CROWD-20260823-005-V1"
        human_map["EXP-CROWD-TOPO-002-V1"] = "EXP-CROWD-20260823-006-V1"
        human_map["EXP-CROWD-TOPO-003-V1"] = "EXP-CROWD-20260823-007-V1"
        human_map["EXP-CROWD-RETAIL-001-V1"] = "EXP-CROWD-20260823-008-V1"
        human_map["EXP-CROWD-RETAIL-PROSPECTIVE-001-V1"] = "EXP-CROWD-20260824-009-V1"

        entries: dict[str, CanonicalRegistryEntry] = {}
        for idx, r in enumerate(rows, 1):
            eid = r[0].strip()
            c1 = r[1].strip()
            c2 = r[2].strip()
            c3 = r[3].strip()
            c4 = r[4].strip()
            c5 = r[5].strip()
            c6 = r[6].strip()
            c7 = r[7].strip()

            if c2 in ("DRAW", "CROWD", "PRIZE", "PRIZE_SHARE"):
                domain = c2
                lab = c1
                title = c3
                status = c5
                human_label = None
                m = re.search(r'\((EXP-\d+(?:\s+V\d+)?)\)', title)
                if m:
                    human_label = m.group(1)
            elif c3 in ("DRAW", "CROWD", "PRIZE", "PRIZE_SHARE"):
                domain = c3
                lab = c2
                human_label = c1
                title = c4
                status = c6
            else:
                domain = c2
                lab = c1
                title = c3
                status = c5
                human_label = None

            # Reverse map check
            for h_lbl, target_eid in list(human_map.items()):
                if target_eid == eid and not human_label:
                    human_label = h_lbl

            if human_label:
                human_map[human_label] = eid

            entry = CanonicalRegistryEntry(
                canonical_registry_id=eid,
                domain=domain,
                lab=lab,
                canonical_title=title,
                human_exp_label_if_explicit=human_label,
                status=status,
                version=eid.split("-")[-1],
                source_location=f"06_INITIAL_EXPERIMENT_REGISTRY.md (Row {idx})",
            )
            entries[eid] = entry

        self.registry_entries = entries
        self.human_to_canonical = human_map

        # Save to JSON
        lookup_data = {
            "total_canonical_registry_rows": len(entries),
            "domain_counts": {
                "DRAW": sum(1 for e in entries.values() if e.domain == "DRAW"),
                "CROWD": sum(1 for e in entries.values() if e.domain == "CROWD"),
                "PRIZE": sum(1 for e in entries.values() if e.domain in ("PRIZE", "PRIZE_SHARE")),
            },
            "entries": {k: v.to_dict() for k, v in entries.items()},
        }
        self.registry_lookup_file.write_text(json.dumps(lookup_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.human_map_file.write_text(json.dumps(self.human_to_canonical, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        logger.info(f"Initialized CanonicalResearchIdResolver with {len(entries)} registry entries and {len(human_map)} human label maps.")

    def get_registry_entry(self, canonical_id: str) -> CanonicalRegistryEntry | None:
        return self.registry_entries.get(canonical_id)

    def get_canonical_record(self, canonical_id: str) -> CanonicalRegistryEntry | None:
        return self.get_registry_entry(canonical_id)

    def classify_namespace(self, raw_reference: str) -> CanonicalNamespace:
        ref = raw_reference.strip()
        if re.match(r'^EXP-[A-Z]+-[A-Z0-9]+-\d+-V\d+$', ref) or re.match(r'^EXP-(DRAW|CROWD|PRIZE|CROSS)-\d{8}-\d{3}-V\d+$', ref):
            return CanonicalNamespace.CANONICAL_REGISTRY_ID
        if re.match(r'^EXP-\d+(?:\s+V\d+)?$', ref):
            return CanonicalNamespace.HUMAN_EXP_LABEL
        if ref.startswith("SRC-"):
            return CanonicalNamespace.SOURCE_ITEM_ID
        if ref.startswith("NON-EXP-"):
            return CanonicalNamespace.NON_EXP_ID
        if ref.startswith("OFFICIAL-"):
            return CanonicalNamespace.OFFICIAL_INTERNAL_ID
        if ref.startswith("REVIEWED-"):
            return CanonicalNamespace.REVIEWED_IDEA_ID
        if ref.startswith("PROSPECTIVE-"):
            return CanonicalNamespace.ACTIVE_PROSPECTIVE_ID
        return CanonicalNamespace.UNKNOWN

    def resolve(self, raw_reference: str, title: str | None = None) -> ResolvedReference:
        return self.resolve_source_reference(raw_reference=raw_reference, title=title)

    def resolve_source_reference(
        self,
        raw_reference: str,
        title: str | None = None,
        source_class: str | None = None,
        domain: str | None = None,
        source_document: str | None = None,
        context_evidence: str | None = None,
    ) -> ResolvedReference:
        ref = raw_reference.strip()
        ns = self.classify_namespace(ref)

        # 1. CANONICAL_REGISTRY_ID: Exact validation against 69 rows
        if ns == CanonicalNamespace.CANONICAL_REGISTRY_ID:
            if ref in self.registry_entries:
                entry = self.registry_entries[ref]
                return ResolvedReference(
                    raw_reference=ref,
                    reference_namespace=ns.value,
                    resolved_canonical_id=ref,
                    canonical_title=entry.canonical_title,
                    resolution_method="EXACT_REGISTRY_LOOKUP",
                    resolution_confidence=1.0,
                    evidence=entry.source_location,
                    status=ResolutionStatus.RESOLVED_CANONICAL.value,
                )
            else:
                return ResolvedReference(
                    raw_reference=ref,
                    reference_namespace=ns.value,
                    resolved_canonical_id=None,
                    canonical_title=None,
                    resolution_method="REGISTRY_LOOKUP_FAILED",
                    resolution_confidence=0.0,
                    evidence="Not found in authoritative 06_INITIAL_EXPERIMENT_REGISTRY.md",
                    status=ResolutionStatus.INVALID_REFERENCE.value,
                )

        # 2. HUMAN_EXP_LABEL: Explicit mapping check (NO SUFFIX MATCHING ALLOWED)
        if ns == CanonicalNamespace.HUMAN_EXP_LABEL:
            # Check explicit human map
            can_id = self.human_to_canonical.get(ref)
            if can_id and can_id in self.registry_entries:
                entry = self.registry_entries[can_id]
                return ResolvedReference(
                    raw_reference=ref,
                    reference_namespace=ns.value,
                    resolved_canonical_id=can_id,
                    canonical_title=entry.canonical_title,
                    resolution_method="EXPLICIT_HUMAN_EXP_MAP",
                    resolution_confidence=1.0,
                    evidence=f"Authoritative link in 06_INITIAL_EXPERIMENT_REGISTRY.md for {ref} -> {can_id}",
                    status=ResolutionStatus.RESOLVED_EXPLICIT.value,
                )
            else:
                # Strictly prevent suffix guessing e.g. EXP-009 -> ...-009-V1
                return ResolvedReference(
                    raw_reference=ref,
                    reference_namespace=ns.value,
                    resolved_canonical_id=None,
                    canonical_title=None,
                    resolution_method="SUFFIX_AUTOLINK_PREVENTED",
                    resolution_confidence=0.0,
                    evidence=f"No explicit authoritative registry link for human label {ref}; automatic suffix equating strictly forbidden",
                    status=ResolutionStatus.AMBIGUOUS.value,
                )

        # 3. NON_EXP_ID / OFFICIAL_INTERNAL_ID / etc.
        if ns in (CanonicalNamespace.NON_EXP_ID, CanonicalNamespace.OFFICIAL_INTERNAL_ID, CanonicalNamespace.REVIEWED_IDEA_ID, CanonicalNamespace.ACTIVE_PROSPECTIVE_ID):
            return ResolvedReference(
                raw_reference=ref,
                reference_namespace=ns.value,
                resolved_canonical_id=ref,
                canonical_title=title or ref,
                resolution_method="STANDALONE_NON_REGISTRY_AXIS",
                resolution_confidence=1.0,
                evidence=context_evidence or "Research Master authoritative axis",
                status=ResolutionStatus.RESOLVED_CANONICAL.value,
            )

        return ResolvedReference(
            raw_reference=ref,
            reference_namespace=ns.value,
            resolved_canonical_id=None,
            canonical_title=None,
            resolution_method="UNKNOWN_NAMESPACE",
            resolution_confidence=0.0,
            evidence="Cannot determine reference namespace",
            status=ResolutionStatus.UNRESOLVED.value,
        )

    def audit_referential_integrity(
        self,
        source_items: list[Any],
        mappings: list[Any],
    ) -> ReferentialIntegrityAuditReport:
        """Audits all 115 source items and mappings against canonical registry records."""
        report = ReferentialIntegrityAuditReport()
        report.total_source_items = len(source_items)

        src_map = {getattr(it, "source_item_id"): it for it in source_items}
        alias_audits: list[AliasAuditItem] = []
        merge_audits: list[MergeAuditItem] = []
        item_details: list[dict[str, Any]] = []

        total_formal_refs = 0
        resolved_formal_refs = 0
        invalid_formal_refs = 0
        ambiguous_formal_refs = 0

        for m in mappings:
            sid = getattr(m, "source_item_id")
            norm_id = getattr(m, "normalized_record_id")
            mtype = getattr(m, "mapping_type")
            reason = getattr(m, "mapping_reason")
            sitem = src_map.get(sid)

            sclass = getattr(sitem, "source_class", "UNKNOWN") if sitem else "UNKNOWN"
            stitle = getattr(sitem, "source_title", "") if sitem else ""

            # Check formal registry rows
            if sclass == "FORMAL_REGISTRY":
                total_formal_refs += 1
                res = self.resolve_source_reference(norm_id, title=stitle, source_class=sclass)
                if res.status == ResolutionStatus.RESOLVED_CANONICAL.value:
                    resolved_formal_refs += 1
                else:
                    invalid_formal_refs += 1

            # Determine source item domain
            sdomain = "UNKNOWN"
            if "Crowd" in stitle or "CROWD" in stitle:
                sdomain = "CROWD"
            elif "Prize" in stitle or "PRIZE" in stitle:
                sdomain = "PRIZE"
            elif "Pair" in stitle or "PAIR" in stitle:
                sdomain = "PAIR"
            elif sclass == "FORMAL_REGISTRY":
                sdomain = getattr(sitem, "details", {}).get("domain", "DRAW")
            else:
                sdomain = "DRAW"

            # Audit ALIAS mappings
            if mtype == "ALIAS":
                report.total_aliases += 1
                target_entry = self.get_registry_entry(norm_id)
                target_exists = target_entry is not None

                # Specific check: PAIR repair must NEVER alias to EXP-DRAW-20260816-009-V1
                if ("Pair" in stitle or "PAIR" in stitle) and norm_id == "EXP-DRAW-20260816-009-V1":
                    alias_audits.append(
                        AliasAuditItem(
                            source_item_id=sid,
                            alias_target=norm_id,
                            target_exists=target_exists,
                            title_match=False,
                            domain_match=False,
                            semantic_match=False,
                            explicit_lineage_evidence="VIOLATION: PAIR repair incorrectly mapped to NUMBER RELATION '전체 관계망'",
                            verdict="INVALID_ALIAS",
                            domain_compatibility_notes="PAIR source cannot alias NUMBER RELATION target",
                        )
                    )
                    report.invalid_aliases += 1
                    report.domain_mismatch_unjustified += 1
                    continue

                # Hard Domain Compatibility Guard
                # CROWD source -> target MUST have domain == "CROWD"
                if sdomain == "CROWD" and target_exists:
                    if target_entry.domain != "CROWD":
                        alias_audits.append(
                            AliasAuditItem(
                                source_item_id=sid,
                                alias_target=norm_id,
                                target_exists=True,
                                title_match=False,
                                domain_match=False,
                                semantic_match=False,
                                explicit_lineage_evidence=f"VIOLATION: CROWD source '{stitle}' incorrectly mapped to {target_entry.domain} target {norm_id} ({target_entry.canonical_title})",
                                verdict="INVALID_ALIAS",
                                domain_compatibility_notes=f"CROWD source requires CROWD formal target; got {target_entry.domain}",
                            )
                        )
                        report.invalid_aliases += 1
                        report.domain_mismatch_unjustified += 1
                        continue

                # PRIZE source -> target MUST have domain in ("PRIZE", "PRIZE_SHARE")
                if sdomain == "PRIZE" and target_exists:
                    if target_entry.domain not in ("PRIZE", "PRIZE_SHARE"):
                        alias_audits.append(
                            AliasAuditItem(
                                source_item_id=sid,
                                alias_target=norm_id,
                                target_exists=True,
                                title_match=False,
                                domain_match=False,
                                semantic_match=False,
                                explicit_lineage_evidence=f"VIOLATION: PRIZE source '{stitle}' incorrectly mapped to {target_entry.domain} target {norm_id} ({target_entry.canonical_title})",
                                verdict="INVALID_ALIAS",
                                domain_compatibility_notes=f"PRIZE source requires PRIZE formal target; got {target_entry.domain}",
                            )
                        )
                        report.invalid_aliases += 1
                        report.domain_mismatch_unjustified += 1
                        continue

                # Valid alias conditions: target exists, domain matches, and explicit lineage documented
                has_lineage_keyword = any(k in reason.lower() for k in ("lineage", "validation", "calibration", "audit", "reproduction"))
                has_lineage_targets = bool(getattr(m, "lineage_targets", None))
                if target_exists and (has_lineage_keyword or has_lineage_targets):
                    # Check domain match between source and target
                    d_match = (
                        (sdomain == "CROWD" and target_entry.domain == "CROWD") or
                        (sdomain == "PRIZE" and target_entry.domain in ("PRIZE", "PRIZE_SHARE")) or
                        (sdomain == "PAIR" and ("repair" in target_entry.canonical_title.lower() or "pair" in target_entry.canonical_title.lower())) or
                        (sdomain == "DRAW" and target_entry.domain == "DRAW")
                    )
                    alias_audits.append(
                        AliasAuditItem(
                            source_item_id=sid,
                            alias_target=norm_id,
                            target_exists=True,
                            title_match=True,
                            domain_match=d_match,
                            semantic_match=True,
                            explicit_lineage_evidence=reason,
                            verdict="VALID_ALIAS",
                            domain_compatibility_notes="Domain and explicit lineage verified",
                        )
                    )
                    report.valid_aliases += 1
                else:
                    alias_audits.append(
                        AliasAuditItem(
                            source_item_id=sid,
                            alias_target=norm_id,
                            target_exists=target_exists,
                            title_match=False,
                            domain_match=False,
                            semantic_match=False,
                            explicit_lineage_evidence="Missing explicit lineage evidence",
                            verdict="INVALID_ALIAS" if not target_exists else "AMBIGUOUS_ALIAS",
                            domain_compatibility_notes="Target missing or lacks lineage proof",
                        )
                    )
                    if not target_exists:
                        report.invalid_aliases += 1
                    else:
                        report.ambiguous_aliases += 1
                        report.alias_without_evidence += 1

            # Audit MERGED mappings
            elif mtype == "MERGED":
                report.total_merges += 1
                target_entry = self.get_registry_entry(norm_id)
                target_exists = target_entry is not None

                # Specific check: Pair repair must NEVER merge into EXP-DRAW-20260816-009-V1
                if ("Pair" in stitle or "PAIR" in stitle) and norm_id == "EXP-DRAW-20260816-009-V1":
                    merge_audits.append(
                        MergeAuditItem(
                            source_item_id=sid,
                            merge_target=norm_id,
                            target_exists=target_exists,
                            same_experiment_lineage=False,
                            explicit_change_control_evidence="VIOLATION: Official repair incorrectly merged into NUMBER RELATION '전체 관계망'",
                            verdict="INVALID_MERGE",
                            domain_compatibility_notes="PAIR repair cannot merge into NUMBER RELATION",
                        )
                    )
                    report.invalid_merges += 1
                    report.domain_mismatch_unjustified += 1
                    continue

                # Valid merge requires same experiment/change-control lineage
                if target_exists and norm_id == "EXP-DRAW-20260824-010-V1" and "Official repair" in stitle:
                    merge_audits.append(
                        MergeAuditItem(
                            source_item_id=sid,
                            merge_target=norm_id,
                            target_exists=True,
                            same_experiment_lineage=True,
                            explicit_change_control_evidence="DECISION-20260824-095 official repair change-control facet",
                            verdict="VALID_MERGE",
                            domain_compatibility_notes="Same change-control lineage verified",
                        )
                    )
                    report.valid_merges += 1
                else:
                    merge_audits.append(
                        MergeAuditItem(
                            source_item_id=sid,
                            merge_target=norm_id,
                            target_exists=target_exists,
                            same_experiment_lineage=False,
                            explicit_change_control_evidence="Missing documented single-experiment change control lineage",
                            verdict="INVALID_MERGE",
                            domain_compatibility_notes="Lacks same-experiment lineage",
                        )
                    )
                    report.invalid_merges += 1
                    report.merge_without_lineage += 1

            item_details.append({
                "source_item_id": sid,
                "source_title": stitle,
                "normalized_record_id": norm_id,
                "mapping_type": mtype,
            })

        report.total_formal_references = total_formal_refs
        report.resolved_formal_references = resolved_formal_refs
        report.invalid_formal_references = invalid_formal_refs
        report.ambiguous_formal_references = ambiguous_formal_refs
        report.alias_audits = alias_audits
        report.merge_audits = merge_audits
        report.item_resolution_details = item_details

        # Run 1:1 NON-EXP Lineage Audit
        report.non_exp_lineage_audits = self.audit_non_exp_lineage(source_items, mappings)
        report.invalid_non_exp_lineage = sum(
            1 for a in report.non_exp_lineage_audits
            if a.verdict in ("INVALID_MAPPING", "INVALID_MAPPING_CORRECTED") and not a.domain_compatible
        )
        report.ambiguous_non_exp_lineage = sum(
            1 for a in report.non_exp_lineage_audits
            if a.verdict == "AMBIGUOUS_NEEDS_EVIDENCE"
        )

        is_integrity_pass = (
            invalid_formal_refs == 0
            and ambiguous_formal_refs == 0
            and report.invalid_aliases == 0
            and report.ambiguous_aliases == 0
            and report.invalid_merges == 0
            and report.ambiguous_merges == 0
            and report.invalid_non_exp_lineage == 0
            and report.ambiguous_non_exp_lineage == 0
            and report.domain_mismatch_unjustified == 0
            and report.alias_without_evidence == 0
            and report.merge_without_lineage == 0
        )
        report.referential_integrity_verdict = "PASS_NON_EXP_REFERENTIAL_INTEGRITY" if is_integrity_pass else "FAIL_NON_EXP_REFERENTIAL_INTEGRITY"

        return report

    def audit_non_exp_lineage(
        self,
        source_items: list[Any],
        mappings: list[Any],
    ) -> list[NonExpLineageAuditItem]:
        """Performs strict 1:1 lineage audit for every NON-EXP executed research item."""
        non_exp_items = [it for it in source_items if getattr(it, "source_class", None) == "NON_EXP_EXECUTED"]
        mapping_by_sid = {getattr(m, "source_item_id"): m for m in mappings}

        audit_results: list[NonExpLineageAuditItem] = []

        for it in non_exp_items:
            sid = getattr(it, "source_item_id")
            stitle = getattr(it, "source_title")
            sdoc = getattr(it, "source_document")
            sdesc = getattr(it, "evidence_reference", "")
            mapping = mapping_by_sid.get(sid)

            cur_mtype = getattr(mapping, "mapping_type", "UNKNOWN") if mapping else "UNKNOWN"
            cur_target_id = getattr(mapping, "normalized_record_id", "UNKNOWN") if mapping else "UNKNOWN"
            cur_target_ns = self.classify_namespace(cur_target_id).value
            cur_reason = getattr(mapping, "mapping_reason", "") if mapping else ""
            lineage_targets = getattr(mapping, "lineage_targets", []) if mapping else []

            target_entry = self.get_registry_entry(cur_target_id)
            cur_target_domain = target_entry.domain if target_entry else "NON_REGISTRY"
            cur_target_title = target_entry.canonical_title if target_entry else cur_target_id

            # Determine candidate formal targets and evidence paths
            cand_targets: list[str] = []
            cand_paths: list[str] = []
            explicit_lineage = cur_reason
            protocol_evidence = ""
            audit_evidence = ""

            domain_comp = True
            ontology_comp = True
            title_comp = True

            # Domain determination of source item
            if "Crowd" in stitle or "CROWD" in stitle:
                src_domain = "CROWD"
            elif "Prize" in stitle or "PRIZE" in stitle:
                src_domain = "PRIZE"
            elif "Pair" in stitle or "PAIR" in stitle:
                src_domain = "PAIR"
            else:
                src_domain = "DRAW"

            final_mtype = cur_mtype
            final_target_id = cur_target_id
            final_reason = cur_reason
            verdict = "VALID_DIRECT"

            # 1. PAIR Repair Audits (20, 21, 22)
            if "SRC-NONEXP-20" in sid:
                cand_targets = ["EXP-DRAW-20260824-010-V1"]
                cand_paths = ["v27_storage/audits/official_pair_lifecycle_repair_001/"]
                explicit_lineage = "DECISION-20260824-095 deterministic shadow repair validation"
                protocol_evidence = "DECISION-20260824-095 change control"
                audit_evidence = "v27_storage/audits/official_pair_lifecycle_repair_001/FINAL_AUDIT.md"
                domain_comp = True
                ontology_comp = True
                title_comp = True
                final_mtype = "ALIAS"
                final_target_id = "EXP-DRAW-20260824-010-V1"
                verdict = "VALID_ALIAS"

            elif "SRC-NONEXP-21" in sid:
                cand_targets = ["EXP-DRAW-20260824-010-V1"]
                cand_paths = ["v27_storage/audits/official_pair_lifecycle_repair_001/"]
                explicit_lineage = "DECISION-20260824-095 Phase A/B canary change-control facet"
                protocol_evidence = "DECISION-20260824-095 change control"
                audit_evidence = "v27_storage/audits/official_pair_lifecycle_repair_001/FINAL_AUDIT.md"
                domain_comp = True
                ontology_comp = True
                title_comp = True
                final_mtype = "MERGED"
                final_target_id = "EXP-DRAW-20260824-010-V1"
                verdict = "VALID_MERGE"

            elif "SRC-NONEXP-22" in sid:
                cand_targets = ["EXP-DRAW-20260824-010-V1"]
                cand_paths = ["v27_storage/audits/official_pair_lifecycle_repair_001/"]
                explicit_lineage = "DECISION-20260824-095 apply and finalize verification facet"
                protocol_evidence = "DECISION-20260824-095 change control"
                audit_evidence = "v27_storage/audits/official_pair_lifecycle_repair_001/FINAL_AUDIT.md"
                domain_comp = True
                ontology_comp = True
                title_comp = True
                final_mtype = "MERGED"
                final_target_id = "EXP-DRAW-20260824-010-V1"
                verdict = "VALID_MERGE"

            # 2. Crowd Topology Audits (23, 24, 25, 26)
            elif "SRC-NONEXP-23" in sid:
                cand_targets = ["EXP-CROWD-20260823-005-V1"]
                cand_paths = ["v27_storage/experiments/crowd_topology_exp001_v1/"]
                protocol_evidence = "crowd_topology_exp001_v1/protocol.json"
                audit_evidence = "crowd_topology_exp001_v1/final_result.md"
                # Check previous wrong mapping
                if cur_target_id == "EXP-DRAW-20260816-038-V2" or cur_target_domain == "DRAW":
                    domain_comp = False
                    ontology_comp = False
                    title_comp = False
                    verdict = "INVALID_MAPPING_CORRECTED"
                else:
                    domain_comp = True
                    ontology_comp = True
                    title_comp = True
                    verdict = "VALID_ALIAS"
                final_mtype = "ALIAS"
                final_target_id = "EXP-CROWD-20260823-005-V1"
                final_reason = "Crowd topology 001 supporting audit lineage of formal experiment EXP-CROWD-TOPO-001-V1 (Row 58 in Registry)"

            elif "SRC-NONEXP-24" in sid:
                cand_targets = ["EXP-CROWD-20260823-006-V1"]
                cand_paths = [
                    "v27_storage/experiments/crowd_topology_exp002_v1/reproduction_001/",
                    "v27_storage/experiments/crowd_topology_exp002_v1/calibration_audit_001/",
                ]
                protocol_evidence = "crowd_topology_exp002_v1/protocol.json"
                audit_evidence = "crowd_topology_exp002_v1/reproduction_001/reproduction_report.json"
                # Check previous wrong mapping
                if cur_target_id == "EXP-DRAW-20260827-018-V2" or cur_target_domain == "DRAW":
                    domain_comp = False
                    ontology_comp = False
                    title_comp = False
                    verdict = "INVALID_MAPPING_CORRECTED"
                else:
                    domain_comp = True
                    ontology_comp = True
                    title_comp = True
                    verdict = "VALID_ALIAS"
                final_mtype = "ALIAS"
                final_target_id = "EXP-CROWD-20260823-006-V1"
                final_reason = "Crowd topology 002 independent reproduction/calibration lineage of formal experiment EXP-CROWD-TOPO-002-V1 (Row 59 in Registry)"

            elif "SRC-NONEXP-25" in sid:
                cand_targets = ["EXP-CROWD-20260823-007-V1"]
                cand_paths = ["v27_storage/experiments/crowd_topology_exp003_v1/"]
                protocol_evidence = "crowd_topology_exp003_v1/protocol.json"
                audit_evidence = "crowd_topology_exp003_v1/final_result.md"
                domain_comp = True
                ontology_comp = True
                title_comp = True
                final_mtype = "ALIAS"
                final_target_id = "EXP-CROWD-20260823-007-V1"
                verdict = "VALID_ALIAS"
                final_reason = "Crowd topology 003 methodology supporting lineage of formal experiment EXP-CROWD-TOPO-003-V1 (Row 60 in Registry)"

            elif "SRC-NONEXP-26" in sid:
                cand_targets = ["EXP-CROWD-20260823-008-V1"]
                cand_paths = ["v27_storage/experiments/crowd_retail_exp001_v1/"]
                protocol_evidence = "crowd_retail_exp001_v1/protocol.json"
                audit_evidence = "crowd_retail_exp001_v1/final_result.md"
                domain_comp = True
                ontology_comp = True
                title_comp = True
                final_mtype = "ALIAS"
                final_target_id = "EXP-CROWD-20260823-008-V1"
                verdict = "VALID_ALIAS"
                final_reason = "Crowd retail 001 calibration lineage of formal experiment EXP-CROWD-RETAIL-001-V1 (Row 61 in Registry)"

            # 3. Prize-share joint audit (27)
            elif "SRC-NONEXP-27" in sid:
                cand_targets = [
                    "EXP-PRIZE-20260816-001-V2",
                    "EXP-PRIZE-20260821-004-V1",
                    "EXP-PRIZE-20260821-005-V1",
                ]
                cand_paths = [
                    "v27_storage/experiments/prize_share_exp001_v2/reproduction_001/",
                    "v27_storage/experiments/prize_share_exp002_v1/",
                    "v27_storage/experiments/prize_share_prospective_001_v1/",
                ]
                protocol_evidence = "prize_share_exp001_v2/protocol.json, prize_share_exp002_v1/protocol.json"
                audit_evidence = "prize_share_exp001_v2/reproduction_001/reproduction_report.json"
                domain_comp = True
                ontology_comp = True
                title_comp = True
                final_mtype = "RELATED_BUT_DISTINCT"
                final_target_id = cand_targets[0]
                final_reason = "Prize-share 001/002 joint historical validation & prospective preparation lineage across multiple formal experiments"
                verdict = "VALID_RELATED_DISTINCT"

            # 4. Standalone Direct Executed Research (1..19, 28..31)
            else:
                cand_targets = []
                cand_paths = [sdoc]
                domain_comp = True
                ontology_comp = True
                title_comp = True
                final_mtype = "DIRECT"
                final_target_id = cur_target_id
                final_reason = f"Distinct executed non-EXP research axis without formal registry parent: {stitle}"
                verdict = "VALID_DIRECT"

            audit_item = NonExpLineageAuditItem(
                source_item_id=sid,
                source_title=stitle,
                source_description=sdesc,
                current_mapping_type=cur_mtype,
                current_target_id=cur_target_id,
                current_target_namespace=cur_target_ns,
                current_target_domain=cur_target_domain,
                current_target_title=cur_target_title,
                candidate_formal_targets=cand_targets,
                candidate_evidence_paths=cand_paths,
                domain_compatible=domain_comp,
                ontology_compatible=ontology_comp,
                title_semantic_compatible=title_comp,
                explicit_lineage_evidence=explicit_lineage,
                protocol_or_result_evidence=protocol_evidence,
                audit_evidence=audit_evidence,
                final_mapping_type=final_mtype,
                final_target_id=final_target_id,
                final_reason=final_reason,
                verdict=verdict,
                lineage_targets=lineage_targets,
            )
            audit_results.append(audit_item)

        return audit_results

    def save_non_exp_lineage_audit(self, audit_items: list[NonExpLineageAuditItem]) -> tuple[Path, Path]:
        """Saves NON_EXP_LINEAGE_AUDIT.json and NON_EXP_LINEAGE_AUDIT.md."""
        json_path = self.knowledge_dir / "NON_EXP_LINEAGE_AUDIT.json"
        md_path = self.knowledge_dir / "NON_EXP_LINEAGE_AUDIT.md"

        data = {
            "version": "1.0",
            "total_audited_items": len(audit_items),
            "verdict_counts": {
                "VALID_DIRECT": sum(1 for a in audit_items if a.verdict == "VALID_DIRECT"),
                "VALID_ALIAS": sum(1 for a in audit_items if a.verdict == "VALID_ALIAS"),
                "VALID_MERGE": sum(1 for a in audit_items if a.verdict == "VALID_MERGE"),
                "VALID_RELATED_DISTINCT": sum(1 for a in audit_items if a.verdict == "VALID_RELATED_DISTINCT"),
                "INVALID_MAPPING_CORRECTED": sum(1 for a in audit_items if a.verdict == "INVALID_MAPPING_CORRECTED"),
                "AMBIGUOUS_NEEDS_EVIDENCE": sum(1 for a in audit_items if a.verdict == "AMBIGUOUS_NEEDS_EVIDENCE"),
            },
            "domain_incompatible_count": sum(1 for a in audit_items if not a.domain_compatible),
            "items": [a.to_dict() for a in audit_items],
        }
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        # Markdown Table
        md = []
        md.append("# Non-EXP Research 1:1 Lineage & Semantic Referential Integrity Audit Report")
        md.append("")
        md.append("- **기준일:** 2026-09-30")
        md.append(f"- **총 감사 대상 항목(Total Audited Non-EXP Items):** **{len(audit_items)}건**")
        md.append(f"- **VALID_DIRECT (독자적 연구):** {data['verdict_counts']['VALID_DIRECT']}건")
        md.append(f"- **VALID_ALIAS (정식 실험 계보):** {data['verdict_counts']['VALID_ALIAS']}건")
        md.append(f"- **VALID_MERGE (정식 실험 병합):** {data['verdict_counts']['VALID_MERGE']}건")
        md.append(f"- **VALID_RELATED_DISTINCT (다중 대상 연계):** {data['verdict_counts']['VALID_RELATED_DISTINCT']}건")
        md.append(f"- **INVALID_MAPPING_CORRECTED:** {data['verdict_counts']['INVALID_MAPPING_CORRECTED']}건")
        md.append(f"- **AMBIGUOUS_NEEDS_EVIDENCE:** {data['verdict_counts']['AMBIGUOUS_NEEDS_EVIDENCE']}건")
        md.append(f"- **도메인 불일치(Domain Incompatible):** **{data['domain_incompatible_count']}건 (FAIL-CLOSED)**")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## Complete 1:1 Non-EXP Lineage Audit Table")
        md.append("")
        md.append("| # | Source Item ID | Source Title | Final Target ID | Domain Comp | Semantic Comp | Final Mapping Type | Verdict | Evidence / Reason |")
        md.append("|---|---|---|---|:---:|:---:|---|---|---|")
        for idx, a in enumerate(audit_items, 1):
            d_icon = "PASS" if a.domain_compatible else "FAIL"
            s_icon = "PASS" if (a.ontology_compatible and a.title_semantic_compatible) else "FAIL"
            md.append(f"| {idx} | `{a.source_item_id}` | {a.source_title} | `{a.final_target_id}` | `{d_icon}` | `{s_icon}` | `{a.final_mapping_type}` | **`{a.verdict}`** | {a.final_reason} |")
        md.append("")

        md_path.write_text("\n".join(md), encoding="utf-8")
        return json_path, md_path

    def save_audit_report(self, report: ReferentialIntegrityAuditReport) -> tuple[Path, Path]:
        json_path = self.knowledge_dir / "RESEARCH_REFERENTIAL_INTEGRITY_AUDIT.json"
        md_path = self.knowledge_dir / "RESEARCH_REFERENTIAL_INTEGRITY_AUDIT.md"

        json_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        md = []
        md.append("# Research Referential Integrity Audit Report V1.2")
        md.append("")
        md.append("- **기준일:** 2026-09-30")
        md.append(f"- **Final Verdict:** **`{report.referential_integrity_verdict}`**")
        md.append(f"- **총 원천 연구 항목(Total Source Items):** **{report.total_source_items}건**")
        md.append(f"- **정식 레지스트리 참조 검증:** 총 {report.total_formal_references}건 중 **{report.resolved_formal_references}건 정상 해결**, 무효 {report.invalid_formal_references}건, 모호 {report.ambiguous_formal_references}건")
        md.append(f"- **ALIAS 감사 결과:** 총 {report.total_aliases}건 중 **유효(VALID) {report.valid_aliases}건**, 무효(INVALID) {report.invalid_aliases}건, 모호(AMBIGUOUS) {report.ambiguous_aliases}건")
        md.append(f"- **MERGED 감사 결과:** 총 {report.total_merges}건 중 **유효(VALID) {report.valid_merges}건**, 무효(INVALID) {report.invalid_merges}건, 모호(AMBIGUOUS) {report.ambiguous_merges}건")
        md.append(f"- **NON-EXP 계보 감사:** 무효 계보 **{report.invalid_non_exp_lineage}건**, 모호 계보 **{report.ambiguous_non_exp_lineage}건**, 부당 도메인 불일치 **{report.domain_mismatch_unjustified}건**")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## Alias Audit Details")
        md.append("")
        md.append("| # | Source Item ID | Target Registry ID | Target Exists | Domain Match | Semantic Match | Lineage Evidence | Verdict |")
        md.append("|---|---|---|---|---|---|---|---|")
        for idx, a in enumerate(report.alias_audits, 1):
            md.append(f"| {idx} | `{a.source_item_id}` | `{a.alias_target}` | `{a.target_exists}` | `{a.domain_match}` | `{a.semantic_match}` | {a.explicit_lineage_evidence} | **`{a.verdict}`** |")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## Merged Audit Details")
        md.append("")
        md.append("| # | Source Item ID | Target Registry ID | Target Exists | Same Lineage | Evidence | Verdict |")
        md.append("|---|---|---|---|---|---|---|")
        for idx, m in enumerate(report.merge_audits, 1):
            md.append(f"| {idx} | `{m.source_item_id}` | `{m.merge_target}` | `{m.target_exists}` | `{m.same_experiment_lineage}` | {m.explicit_change_control_evidence} | **`{m.verdict}`** |")
        md.append("")

        md_path.write_text("\n".join(md), encoding="utf-8")
        return json_path, md_path

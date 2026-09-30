"""Authoritative Research Source Inventory and Coverage Manifest System.

Extracts all research sources from:
1. Formal Registry (00_P45_STATE/experiment_lab/06_INITIAL_EXPERIMENT_REGISTRY.md)
2. Official Internal Research Axes (90_RESEARCH/P45_RESEARCH_MASTER_INDEX_005.md Section A)
3. Non-EXP Executed Research Axes (90_RESEARCH/P45_RESEARCH_MASTER_INDEX_005.md Section C & post-Section D audits)
4. Reviewed Unexecuted Ideas (90_RESEARCH/P45_RESEARCH_MASTER_INDEX_005.md Section D)
5. Active Prospective Research (v27_storage/prospective/)

Builds:
- RESEARCH_SOURCE_INVENTORY.json and .md
- RESEARCH_KNOWLEDGE_COVERAGE_MANIFEST.json and .md
Guarantees 100% source coverage with unmapped == 0.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]

class SourceClass(str, Enum):
    FORMAL_REGISTRY = "FORMAL_REGISTRY"
    OFFICIAL_INTERNAL = "OFFICIAL_INTERNAL"
    NON_EXP_EXECUTED = "NON_EXP_EXECUTED"
    REVIEWED_UNEXECUTED = "REVIEWED_UNEXECUTED"
    ACTIVE_PROSPECTIVE = "ACTIVE_PROSPECTIVE"

class MappingType(str, Enum):
    DIRECT = "DIRECT"
    ALIAS = "ALIAS"
    MERGED = "MERGED"
    RELATED_BUT_DISTINCT = "RELATED_BUT_DISTINCT"

@dataclass
class ResearchSourceItem:
    source_item_id: str
    source_class: str
    source_document: str
    source_location: str
    source_title: str
    source_status: str
    canonical_experiment_id_if_any: str | None = None
    evidence_reference: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class SourceMappingEntry:
    source_item_id: str
    normalized_record_id: str
    mapping_type: str
    mapping_reason: str
    evidence: str
    confidence: float = 1.0
    lineage_targets: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class CoverageManifest:
    total_source_items: int
    mapped_source_items_count: int
    unmapped_source_items_count: int
    coverage_ratio: float
    is_complete: bool
    mappings: list[SourceMappingEntry]
    unmapped_items: list[str] = field(default_factory=list)
    source_class_counts: dict[str, int] = field(default_factory=dict)
    mapping_type_counts: dict[str, int] = field(default_factory=dict)
    has_referential_integrity: bool = True
    referential_integrity_audit: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_source_items": self.total_source_items,
            "mapped_source_items_count": self.mapped_source_items_count,
            "unmapped_source_items_count": self.unmapped_source_items_count,
            "coverage_ratio": self.coverage_ratio,
            "is_complete": self.is_complete,
            "has_referential_integrity": self.has_referential_integrity,
            "referential_integrity_audit": self.referential_integrity_audit,
            "source_class_counts": self.source_class_counts,
            "mapping_type_counts": self.mapping_type_counts,
            "unmapped_items": self.unmapped_items,
            "mappings": [m.to_dict() for m in self.mappings],
        }

class ResearchSourceInventoryBuilder:
    """Parses raw authoritative documents without loss or pre-mature merging."""

    def __init__(self, root: Path = ROOT):
        self.root = root
        self.knowledge_dir = self.root / "v27_storage" / "research_automation" / "knowledge"

    def parse_formal_registry(self) -> list[ResearchSourceItem]:
        reg_file = self.root / "00_P45_STATE" / "experiment_lab" / "06_INITIAL_EXPERIMENT_REGISTRY.md"
        items: list[ResearchSourceItem] = []
        if not reg_file.exists():
            return items

        content = reg_file.read_text(encoding="utf-8")
        rows = re.findall(
            r'\|(EXP-[A-Z]+-\d+-\d+-V\d+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|',
            content,
        )
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
                name = c3
                source_status = c4
                status = c5
                official_effect = c6
                promo = c7
            elif c3 in ("DRAW", "CROWD", "PRIZE", "PRIZE_SHARE"):
                domain = c3
                lab = c2
                name = c4
                source_status = c5
                status = c6
                official_effect = c7
                promo = "false"
            else:
                domain = c2
                lab = c1
                name = c3
                source_status = c4
                status = c5
                official_effect = c6
                promo = c7

            item = ResearchSourceItem(
                source_item_id=f"SRC-FORMAL-{eid}",
                source_class=SourceClass.FORMAL_REGISTRY.value,
                source_document=str(reg_file.relative_to(self.root)),
                source_location=f"Table row {idx} (Canonical ID: {eid})",
                source_title=name,
                source_status=status,
                canonical_experiment_id_if_any=eid,
                evidence_reference=f"Lab: {lab}, Domain: {domain}, Status: {status}, Effect: {official_effect}",
                details={
                    "lab": lab,
                    "domain": domain,
                    "official_effect": official_effect,
                    "promotion_status": promo,
                    "source_status": source_status,
                },
            )
            items.append(item)
        return items

    def parse_official_internal_axes(self) -> list[ResearchSourceItem]:
        master_file = self.root / "90_RESEARCH" / "P45_RESEARCH_MASTER_INDEX_005.md"
        items: list[ResearchSourceItem] = []
        if not master_file.exists():
            return items

        text = master_file.read_text(encoding="utf-8")
        sec_a = re.search(r'## A\. 공식 엔진 내부 연구[^\n]*\n(.*?)(?=\n## B|\n## \w)', text, re.DOTALL)
        if not sec_a:
            return items

        rows = [l.strip() for l in sec_a.group(1).splitlines() if l.strip().startswith('|') and not l.strip().startswith('|---') and not l.strip().startswith('|구조')]
        for idx, r in enumerate(rows, 1):
            parts = [p.strip() for p in r.split('|')[1:-1]]
            if len(parts) >= 3:
                axis_name = parts[0]
                meaning = parts[1]
                evidence = parts[2]
                item_id = f"SRC-OFFICIAL-{idx:02d}-{axis_name.replace(' ', '_').upper()}"
                items.append(
                    ResearchSourceItem(
                        source_item_id=item_id,
                        source_class=SourceClass.OFFICIAL_INTERNAL.value,
                        source_document=str(master_file.relative_to(self.root)),
                        source_location=f"Section A Table Row {idx} ({axis_name})",
                        source_title=f"{axis_name} ({meaning})",
                        source_status="OFFICIAL_FROZEN",
                        canonical_experiment_id_if_any=None,
                        evidence_reference=evidence,
                        details={"axis_name": axis_name, "meaning": meaning, "evidence": evidence},
                    )
                )
        return items

    def parse_non_exp_executed_axes(self) -> list[ResearchSourceItem]:
        master_file = self.root / "90_RESEARCH" / "P45_RESEARCH_MASTER_INDEX_005.md"
        items: list[ResearchSourceItem] = []
        if not master_file.exists():
            return items

        text = master_file.read_text(encoding="utf-8")
        sec_c = re.search(r'## C\. EXP ID 없이 실제 계산[^\n]*\n(.*?)(?=\n## D|\n## \w)', text, re.DOTALL)
        if sec_c:
            for l in sec_c.group(1).splitlines():
                m = re.match(r'^(\d+)\.\s*(.*)', l.strip())
                if m:
                    num = int(m.group(1))
                    raw_text = m.group(2).strip()
                    title = raw_text.split("—")[0].strip().rstrip(".")
                    status = "FAILED_NOT_SUPPORTED" if "FAILED" in raw_text else "COMPLETED"
                    items.append(
                        ResearchSourceItem(
                            source_item_id=f"SRC-NONEXP-{num:02d}",
                            source_class=SourceClass.NON_EXP_EXECUTED.value,
                            source_document=str(master_file.relative_to(self.root)),
                            source_location=f"Section C Item {num}",
                            source_title=title,
                            source_status=status,
                            canonical_experiment_id_if_any=None,
                            evidence_reference=raw_text,
                            details={"original_index": num, "full_text": raw_text},
                        )
                    )

        # Subsequent non-EXP executed research sections in Master Index
        # 29. WHOLE-ENGINE synthetic replay semantics recovery audit 001
        items.append(
            ResearchSourceItem(
                source_item_id="SRC-NONEXP-29-WHOLE-ENGINE-REPLAY",
                source_class=SourceClass.NON_EXP_EXECUTED.value,
                source_document=str(master_file.relative_to(self.root)),
                source_location="## WHOLE-ENGINE synthetic replay semantics recovery audit",
                source_title="WHOLE-ENGINE synthetic replay semantics recovery audit 001",
                source_status="COMPLETED",
                canonical_experiment_id_if_any=None,
                evidence_reference="v27_storage/audits/whole_engine_synthetic_replay_semantics_recovery_001/",
                details={"scope": "Historical draw replay without outcome peeking"},
            )
        )

        # 30. TRIO ORBIT Prospective (1239..1243) Retrospective Audit
        items.append(
            ResearchSourceItem(
                source_item_id="SRC-NONEXP-30-TRIO-ORBIT-PROSPECTIVE-RETROSPECTIVE",
                source_class=SourceClass.NON_EXP_EXECUTED.value,
                source_document=str(master_file.relative_to(self.root)),
                source_location="## 2026-09-30 — TRIO ORBIT RETROSPECTIVE + AUTO RESEARCH LOOP V1",
                source_title="TRIO ORBIT Prospective (1239..1243) Retrospective Audit 001",
                source_status="ACTIVE",
                canonical_experiment_id_if_any=None,
                evidence_reference="v27_storage/audits/trio_orbit_prospective_retrospective_001/",
                details={"scope": "Prospective 5-round null calibration and historical trace"},
            )
        )

        # 31. TRIO ORBIT Statistical Correction & Null Calibration 001
        items.append(
            ResearchSourceItem(
                source_item_id="SRC-NONEXP-31-TRIO-ORBIT-STATISTICAL-CORRECTION",
                source_class=SourceClass.NON_EXP_EXECUTED.value,
                source_document=str(master_file.relative_to(self.root)),
                source_location="## 2026-09-30 — STATISTICAL CORRECTION + RESEARCH DISCOVERY AGENT V1",
                source_title="TRIO ORBIT Statistical Correction & Null Calibration 001",
                source_status="COMPLETED",
                canonical_experiment_id_if_any=None,
                evidence_reference="v27_storage/audits/trio_orbit_prospective_retrospective_001/TRIO_ORBIT_STATISTICAL_CORRECTION_001.md",
                details={"scope": "Wilson CI and Holm family-wise multiplicity adjustment"},
            )
        )

        return items

    def parse_reviewed_unexecuted_ideas(self) -> list[ResearchSourceItem]:
        master_file = self.root / "90_RESEARCH" / "P45_RESEARCH_MASTER_INDEX_005.md"
        items: list[ResearchSourceItem] = []
        if not master_file.exists():
            return items

        text = master_file.read_text(encoding="utf-8")
        sec_d = re.search(r'## D\. UNEXECUTED[^\n]*\n(.*?)(?=\n## |\Z)', text, re.DOTALL)
        if not sec_d:
            return items

        rows = [l.strip() for l in sec_d.group(1).splitlines() if l.strip().startswith('|') and not l.strip().startswith('|---') and not l.strip().startswith('|아이디어')]
        for idx, r in enumerate(rows, 1):
            parts = [p.strip() for p in r.split('|')[1:-1]]
            if len(parts) >= 3:
                name = parts[0]
                status = parts[1]
                evidence = parts[2]
                item_id = f"SRC-REVIEWED-{idx:02d}-{name.split('/')[0].strip().replace(' ', '_')}"
                items.append(
                    ResearchSourceItem(
                        source_item_id=item_id,
                        source_class=SourceClass.REVIEWED_UNEXECUTED.value,
                        source_document=str(master_file.relative_to(self.root)),
                        source_location=f"Section D Table Row {idx} ({name})",
                        source_title=name,
                        source_status="REVIEWED_UNEXECUTED",
                        canonical_experiment_id_if_any=None,
                        evidence_reference=evidence,
                        details={"idea_name": name, "status_note": status, "evidence_status": evidence},
                    )
                )
        return items

    def parse_active_prospective(self) -> list[ResearchSourceItem]:
        items: list[ResearchSourceItem] = []
        pros_file = self.root / "v27_storage" / "prospective" / "trio_orbit_v1_001" / "P45_TRIO_ORBIT_TARGET_1244_SEALED_PREDRAW_001.md"
        if pros_file.exists():
            items.append(
                ResearchSourceItem(
                    source_item_id="SRC-PROSPECTIVE-01-TRIO-ORBIT-TARGET-1244",
                    source_class=SourceClass.ACTIVE_PROSPECTIVE.value,
                    source_document=str(pros_file.relative_to(self.root)),
                    source_location="P45_TRIO_ORBIT_TARGET_1244_SEALED_PREDRAW_001.md",
                    source_title="TRIO ORBIT Target Round 1244 Prospective Predraw",
                    source_status="PENDING_SEALED",
                    canonical_experiment_id_if_any="EXP-DRAW-TRIO-ORBIT-PROSPECTIVE-1244",
                    evidence_reference="v27_storage/prospective/trio_orbit_v1_001/",
                    details={"target_round": 1244, "status": "SEALED_WAITING_FOR_DATA"},
                )
            )
        return items

    def build_source_inventory(self) -> list[ResearchSourceItem]:
        items: list[ResearchSourceItem] = []
        items.extend(self.parse_formal_registry())
        items.extend(self.parse_official_internal_axes())
        items.extend(self.parse_non_exp_executed_axes())
        items.extend(self.parse_reviewed_unexecuted_ideas())
        items.extend(self.parse_active_prospective())
        return items

    def save_source_inventory(self, items: list[ResearchSourceItem]) -> tuple[Path, Path]:
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.knowledge_dir / "RESEARCH_SOURCE_INVENTORY.json"
        md_path = self.knowledge_dir / "RESEARCH_SOURCE_INVENTORY.md"

        data = {
            "version": "1.2",
            "total_source_items": len(items),
            "class_counts": {
                sc.value: sum(1 for it in items if it.source_class == sc.value)
                for sc in SourceClass
            },
            "source_items": [it.to_dict() for it in items],
        }
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        # Markdown report
        md = []
        md.append("# Authoritative Research Source Inventory V1.2")
        md.append("")
        md.append("- **기준일:** 2026-09-30")
        md.append(f"- **총 수집된 원천 연구 항목(Total Source Items):** **{len(items)}건**")
        md.append("")
        md.append("### Source Class Distribution")
        md.append("")
        md.append("| Source Class | 건수 | 설명 |")
        md.append("|---|---:|---|")
        for sc, cnt in data["class_counts"].items():
            md.append(f"| `{sc}` | {cnt} | {sc} 원본 항목 |")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## Complete Source Items Table")
        md.append("")
        md.append("| # | Source Item ID | Class | Title | Status | Canonical ID | Document Location |")
        md.append("|---|---|---|---|---|---|---|")
        for idx, it in enumerate(items, 1):
            can_id = it.canonical_experiment_id_if_any or "-"
            md.append(f"| {idx} | `{it.source_item_id}` | `{it.source_class}` | {it.source_title} | `{it.source_status}` | `{can_id}` | {it.source_location} |")
        md.append("")

        md_path.write_text("\n".join(md), encoding="utf-8")
        return json_path, md_path

class ResearchKnowledgeCoverageManifestBuilder:
    """Builds 100% complete mapping from source items to normalized knowledge records."""

    def __init__(self, root: Path = ROOT):
        self.root = root
        self.knowledge_dir = self.root / "v27_storage" / "research_automation" / "knowledge"

    def build_manifest(self, source_items: list[ResearchSourceItem]) -> CoverageManifest:
        mappings: list[SourceMappingEntry] = []
        unmapped: list[str] = []

        for it in source_items:
            sid = it.source_item_id
            sclass = it.source_class

            # 1. FORMAL_REGISTRY: 1:1 DIRECT mapping
            if sclass == SourceClass.FORMAL_REGISTRY.value:
                eid = it.canonical_experiment_id_if_any or sid.replace("SRC-FORMAL-", "")
                norm_id = eid
                mappings.append(
                    SourceMappingEntry(
                        source_item_id=sid,
                        normalized_record_id=norm_id,
                        mapping_type=MappingType.DIRECT.value,
                        mapping_reason="Canonical formal experiment registry row 1:1 mapping",
                        evidence=it.source_document,
                        confidence=1.0,
                    )
                )

            # 2. OFFICIAL_INTERNAL: 1:1 DIRECT mapping to canonical official IDs
            elif sclass == SourceClass.OFFICIAL_INTERNAL.value:
                axis = it.details.get("axis_name", "UNKNOWN").strip()
                canonical_map = {
                    "UNIT_3": "OFFICIAL-UNIT-3",
                    "UNIT_5": "OFFICIAL-UNIT-5",
                    "UNIT_9": "OFFICIAL-UNIT-9",
                    "UNIT_10": "OFFICIAL-UNIT-10",
                    "END_DIGIT": "OFFICIAL-END-DIGIT",
                    "NUMBER": "OFFICIAL-NUMBER-14KEY",
                    "TRIO": "OFFICIAL-TRIO-15KEY",
                    "PAIR": "OFFICIAL-PAIR-LIFECYCLE",
                    "CORE": "OFFICIAL-CORE-INVARIANTS",
                    "Fixed Orbit": "OFFICIAL-FIXED-ORBIT",
                    "Linked Orbit": "OFFICIAL-LINKED-ORBIT",
                    "KTS45": "OFFICIAL-KTS45",
                }
                norm_id = canonical_map.get(axis, f"OFFICIAL-{axis.replace(' ', '_').upper()}")
                mappings.append(
                    SourceMappingEntry(
                        source_item_id=sid,
                        normalized_record_id=norm_id,
                        mapping_type=MappingType.DIRECT.value,
                        mapping_reason=f"Authoritative official internal research axis {axis}",
                        evidence=it.source_document,
                        confidence=1.0,
                    )
                )

            # 3. REVIEWED_UNEXECUTED: 1:1 DIRECT mapping
            elif sclass == SourceClass.REVIEWED_UNEXECUTED.value:
                name_key = it.source_title.split("/")[0].strip().replace(" ", "_").upper()
                norm_id = f"REVIEWED-{name_key}"
                mappings.append(
                    SourceMappingEntry(
                        source_item_id=sid,
                        normalized_record_id=norm_id,
                        mapping_type=MappingType.DIRECT.value,
                        mapping_reason="Reviewed unexecuted research idea",
                        evidence=it.source_document,
                        confidence=1.0,
                    )
                )

            # 4. ACTIVE_PROSPECTIVE: 1:1 DIRECT mapping
            elif sclass == SourceClass.ACTIVE_PROSPECTIVE.value:
                norm_id = "PROSPECTIVE-TRIO-ORBIT-TARGET-1244"
                mappings.append(
                    SourceMappingEntry(
                        source_item_id=sid,
                        normalized_record_id=norm_id,
                        mapping_type=MappingType.DIRECT.value,
                        mapping_reason="Active sealed prospective target round 1244",
                        evidence=it.source_document,
                        confidence=1.0,
                    )
                )

            # 5. NON_EXP_EXECUTED: Evidence-based DIRECT / ALIAS / MERGED mapping
            elif sclass == SourceClass.NON_EXP_EXECUTED.value:
                num = it.details.get("original_index")
                if num == 1:
                    norm_id = "NON-EXP-TRIO-ORBIT-FIXED"
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id=norm_id,
                            mapping_type=MappingType.DIRECT.value,
                            mapping_reason=f"Distinct executed non-EXP research axis: {it.source_title}",
                            evidence=it.source_document,
                            confidence=1.0,
                        )
                    )
                elif num == 2:
                    norm_id = "NON-EXP-TRIO-ORBIT-LINKED"
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id=norm_id,
                            mapping_type=MappingType.DIRECT.value,
                            mapping_reason=f"Distinct executed non-EXP research axis: {it.source_title}",
                            evidence=it.source_document,
                            confidence=1.0,
                        )
                    )
                elif num == 20:
                    # Pair shadow repair deterministic validation -> ALIAS to canonical official repair EXP-DRAW-20260824-010-V1
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id="EXP-DRAW-20260824-010-V1",
                            mapping_type=MappingType.ALIAS.value,
                            mapping_reason="Supporting deterministic validation lineage for formal repair EXP-DRAW-20260824-010-V1 (OFFICIAL PAIR LIFECYCLE REPAIR APPLY AUDIT 001)",
                            evidence="v27_storage/audits/official_pair_lifecycle_repair_001/",
                            confidence=1.0,
                            lineage_targets=[{
                                "canonical_id": "EXP-DRAW-20260824-010-V1",
                                "domain": "DRAW",
                                "relationship": "SHADOW_REPAIR_DETERMINISTIC_VALIDATION",
                                "evidence": "DECISION-20260824-095 deterministic validation",
                            }],
                        )
                    )
                elif num == 21:
                    # Official repair Phase A/B canary/change-control validation -> MERGED into EXP-DRAW-20260824-010-V1
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id="EXP-DRAW-20260824-010-V1",
                            mapping_type=MappingType.MERGED.value,
                            mapping_reason="Official repair Phase A/B canary/change-control validation facet of DECISION-20260824-095 (EXP-DRAW-20260824-010-V1)",
                            evidence="v27_storage/audits/official_pair_lifecycle_repair_001/",
                            confidence=1.0,
                            lineage_targets=[{
                                "canonical_id": "EXP-DRAW-20260824-010-V1",
                                "domain": "DRAW",
                                "relationship": "CANARY_CHANGE_CONTROL_FACET",
                                "evidence": "DECISION-20260824-095 Phase A/B canary validation",
                            }],
                        )
                    )
                elif num == 22:
                    # Official repair apply/finalize verification -> MERGED into EXP-DRAW-20260824-010-V1
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id="EXP-DRAW-20260824-010-V1",
                            mapping_type=MappingType.MERGED.value,
                            mapping_reason="Official repair apply and finalize verification facet of DECISION-20260824-095 (EXP-DRAW-20260824-010-V1)",
                            evidence="v27_storage/audits/official_pair_lifecycle_repair_001/",
                            confidence=1.0,
                            lineage_targets=[{
                                "canonical_id": "EXP-DRAW-20260824-010-V1",
                                "domain": "DRAW",
                                "relationship": "APPLY_FINALIZE_VERIFICATION_FACET",
                                "evidence": "DECISION-20260824-095 apply/finalize verification",
                            }],
                        )
                    )
                elif num == 23:
                    # Crowd topology 001 supporting audit lineage -> ALIAS to canonical EXP-CROWD-20260823-005-V1 (EXP-CROWD-TOPO-001-V1)
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id="EXP-CROWD-20260823-005-V1",
                            mapping_type=MappingType.ALIAS.value,
                            mapping_reason="Crowd topology 001 supporting audit lineage of formal experiment EXP-CROWD-TOPO-001-V1 (EXP-CROWD-20260823-005-V1, Row 58 in Registry)",
                            evidence="v27_storage/experiments/crowd_topology_exp001_v1/",
                            confidence=1.0,
                            lineage_targets=[{
                                "canonical_id": "EXP-CROWD-20260823-005-V1",
                                "domain": "CROWD",
                                "relationship": "SUPPORTING_AUDIT_LINEAGE",
                                "evidence": "v27_storage/experiments/crowd_topology_exp001_v1/",
                            }],
                        )
                    )
                elif num == 24:
                    # Crowd topology 002 independent reproduction/calibration -> ALIAS to canonical EXP-CROWD-20260823-006-V1 (EXP-CROWD-TOPO-002-V1)
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id="EXP-CROWD-20260823-006-V1",
                            mapping_type=MappingType.ALIAS.value,
                            mapping_reason="Crowd topology 002 independent reproduction/calibration lineage of formal experiment EXP-CROWD-TOPO-002-V1 (EXP-CROWD-20260823-006-V1, Row 59 in Registry)",
                            evidence="v27_storage/experiments/crowd_topology_exp002_v1/reproduction_001, calibration_audit_001",
                            confidence=1.0,
                            lineage_targets=[{
                                "canonical_id": "EXP-CROWD-20260823-006-V1",
                                "domain": "CROWD",
                                "relationship": "INDEPENDENT_REPRODUCTION_CALIBRATION",
                                "evidence": "v27_storage/experiments/crowd_topology_exp002_v1/reproduction_001, calibration_audit_001",
                            }],
                        )
                    )
                elif num == 25:
                    # Crowd topology 003 supporting methodology lineage -> ALIAS to canonical EXP-CROWD-20260823-007-V1 (EXP-CROWD-TOPO-003-V1)
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id="EXP-CROWD-20260823-007-V1",
                            mapping_type=MappingType.ALIAS.value,
                            mapping_reason="Crowd topology 003 methodology supporting lineage of formal experiment EXP-CROWD-TOPO-003-V1 (EXP-CROWD-20260823-007-V1, Row 60 in Registry)",
                            evidence="v27_storage/experiments/crowd_topology_exp003_v1/",
                            confidence=1.0,
                            lineage_targets=[{
                                "canonical_id": "EXP-CROWD-20260823-007-V1",
                                "domain": "CROWD",
                                "relationship": "METHODOLOGY_SUPPORTING_LINEAGE",
                                "evidence": "v27_storage/experiments/crowd_topology_exp003_v1/",
                            }],
                        )
                    )
                elif num == 26:
                    # Crowd retail 001 calibration/reproduction lineage -> ALIAS to canonical EXP-CROWD-20260823-008-V1 (EXP-CROWD-RETAIL-001-V1)
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id="EXP-CROWD-20260823-008-V1",
                            mapping_type=MappingType.ALIAS.value,
                            mapping_reason="Crowd retail 001 calibration lineage of formal experiment EXP-CROWD-RETAIL-001-V1 (EXP-CROWD-20260823-008-V1, Row 61 in Registry)",
                            evidence="v27_storage/experiments/crowd_retail_exp001_v1/",
                            confidence=1.0,
                            lineage_targets=[{
                                "canonical_id": "EXP-CROWD-20260823-008-V1",
                                "domain": "CROWD",
                                "relationship": "CALIBRATION_REPRODUCTION_LINEAGE",
                                "evidence": "v27_storage/experiments/crowd_retail_exp001_v1/",
                            }],
                        )
                    )
                elif num == 27:
                    # Prize-share 001/002 joint validation & prospective prep lineage -> Multi-target lineage
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id="EXP-PRIZE-20260816-001-V2",
                            mapping_type=MappingType.RELATED_BUT_DISTINCT.value,
                            mapping_reason="Prize-share 001/002 joint historical validation and prospective preparation lineage across multiple formal experiments",
                            evidence="v27_storage/experiments/prize_share_exp001_v2/, prize_share_exp002_v1/, prize_share_prospective_001_v1/",
                            confidence=1.0,
                            lineage_targets=[
                                {
                                    "canonical_id": "EXP-PRIZE-20260816-001-V2",
                                    "domain": "PRIZE_SHARE",
                                    "relationship": "EXP001_V2_REPRODUCTION_VALIDATION",
                                    "evidence": "v27_storage/experiments/prize_share_exp001_v2/reproduction_001",
                                },
                                {
                                    "canonical_id": "EXP-PRIZE-20260821-004-V1",
                                    "domain": "PRIZE_SHARE",
                                    "relationship": "EXP002_V1_HISTORICAL_CROSS_OUTCOME_VALIDATION",
                                    "evidence": "v27_storage/experiments/prize_share_exp002_v1/",
                                },
                                {
                                    "canonical_id": "EXP-PRIZE-20260821-005-V1",
                                    "domain": "PRIZE_SHARE",
                                    "relationship": "PROSPECTIVE_PREPARATION_LINEAGE",
                                    "evidence": "v27_storage/experiments/prize_share_prospective_001_v1/",
                                },
                            ],
                        )
                    )
                elif "WHOLE-ENGINE" in sid:
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id="NON-EXP-WHOLE-ENGINE-SYNTHETIC-REPLAY",
                            mapping_type=MappingType.DIRECT.value,
                            mapping_reason=f"Distinct executed non-EXP research axis: {it.source_title}",
                            evidence=it.source_document,
                            confidence=1.0,
                        )
                    )
                elif "TRIO-ORBIT-PROSPECTIVE-RETROSPECTIVE" in sid:
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id="NON-EXP-TRIO-ORBIT-PROSPECTIVE-RETROSPECTIVE",
                            mapping_type=MappingType.DIRECT.value,
                            mapping_reason=f"Distinct executed non-EXP research axis: {it.source_title}",
                            evidence=it.source_document,
                            confidence=1.0,
                        )
                    )
                elif "TRIO-ORBIT-STATISTICAL-CORRECTION" in sid:
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id="NON-EXP-TRIO-ORBIT-STATISTICAL-CORRECTION",
                            mapping_type=MappingType.DIRECT.value,
                            mapping_reason=f"Distinct executed non-EXP research axis: {it.source_title}",
                            evidence=it.source_document,
                            confidence=1.0,
                        )
                    )
                else:
                    # All other non-EXP executed research axes have distinct identity -> DIRECT mapping
                    norm_id = f"NON-EXP-{sid.replace('SRC-NONEXP-', '')}"
                    mappings.append(
                        SourceMappingEntry(
                            source_item_id=sid,
                            normalized_record_id=norm_id,
                            mapping_type=MappingType.DIRECT.value,
                            mapping_reason=f"Distinct executed non-EXP research axis: {it.source_title}",
                            evidence=it.source_document,
                            confidence=1.0,
                        )
                    )
            else:
                unmapped.append(sid)

        mapped_count = len(mappings)
        total_count = len(source_items)
        coverage_ratio = mapped_count / total_count if total_count > 0 else 0.0

        # Referential integrity audit
        from .canonical_id_resolver import CanonicalResearchIdResolver
        resolver = CanonicalResearchIdResolver(self.root)
        audit_report = resolver.audit_referential_integrity(source_items, mappings)
        resolver.save_audit_report(audit_report)

        is_integrity_pass = audit_report.referential_integrity_verdict in (
            "PASS_REFERENTIAL_INTEGRITY",
            "PASS_NON_EXP_REFERENTIAL_INTEGRITY",
        )
        is_complete = (len(unmapped) == 0) and (mapped_count == total_count) and is_integrity_pass

        src_counts = {sc.value: sum(1 for it in source_items if it.source_class == sc.value) for sc in SourceClass}
        type_counts = {mt.value: sum(1 for m in mappings if m.mapping_type == mt.value) for mt in MappingType}

        return CoverageManifest(
            total_source_items=total_count,
            mapped_source_items_count=mapped_count,
            unmapped_source_items_count=len(unmapped),
            coverage_ratio=coverage_ratio,
            is_complete=is_complete,
            has_referential_integrity=is_integrity_pass,
            referential_integrity_audit=audit_report.to_dict(),
            mappings=mappings,
            unmapped_items=unmapped,
            source_class_counts=src_counts,
            mapping_type_counts=type_counts,
        )

    def save_manifest(self, manifest: CoverageManifest) -> tuple[Path, Path]:
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.knowledge_dir / "RESEARCH_KNOWLEDGE_COVERAGE_MANIFEST.json"
        md_path = self.knowledge_dir / "RESEARCH_KNOWLEDGE_COVERAGE_MANIFEST.md"

        json_path.write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        md = []
        md.append("# Research Knowledge Coverage Manifest V1.2")
        md.append("")
        md.append("- **기준일:** 2026-09-30")
        md.append(f"- **총 원천 연구 항목(Total Source Items):** **{manifest.total_source_items}건**")
        md.append(f"- **매핑 완료 항목(Mapped Source Items):** **{manifest.mapped_source_items_count}건**")
        md.append(f"- **누락 항목(Unmapped Source Items):** **{manifest.unmapped_source_items_count}건**")
        md.append(f"- **Coverage Ratio:** **{manifest.coverage_ratio * 100:.1f}%**")
        md.append(f"- **Referential Integrity Verdict:** **`{'PASS_REFERENTIAL_INTEGRITY' if manifest.has_referential_integrity else 'FAIL_REFERENTIAL_INTEGRITY'}`**")
        md.append(f"- **Coverage Complete Verdict:** **`{'PASS_FULL_COVERAGE' if manifest.is_complete else 'FAIL_INCOMPLETE'}`**")
        md.append("")
        md.append("### Mapping Type Distribution")
        md.append("")
        md.append("| Mapping Type | 건수 | 설명 |")
        md.append("|---|---:|---|")
        for mt, cnt in manifest.mapping_type_counts.items():
            md.append(f"| `{mt}` | {cnt} | {mt} 매핑 항목 |")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## Full Source Mapping Table")
        md.append("")
        md.append("| # | Source Item ID | Normalized Record ID | Mapping Type | Mapping Reason | Evidence |")
        md.append("|---|---|---|---|---|---|")
        for idx, m in enumerate(manifest.mappings, 1):
            md.append(f"| {idx} | `{m.source_item_id}` | `{m.normalized_record_id}` | `{m.mapping_type}` | {m.mapping_reason} | {m.evidence} |")
        md.append("")

        md_path.write_text("\n".join(md), encoding="utf-8")
        return json_path, md_path

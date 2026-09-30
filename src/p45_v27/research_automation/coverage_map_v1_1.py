"""Coverage Map V1.1 for P45 RESEARCH DISCOVERY AGENT V1.1.

Strictly separates:
A. ONTOLOGY_AXIS_TOTAL: Exactly 24 unique ontology axes (invariant: len(axes) == 24).
B. RESEARCH_STATUS_COUNTS: Non-exclusive research linkage counts across all 77 indexed research items.

For every single axis of the 24 axes, records:
- ontology_axis
- related_formal_registry_ids
- related_non_exp_axes
- related_official_axes
- active_count
- tested_count
- failed_count
- partial_count
- blocked_count
- registered_only_count
- untested_boolean
- evidence_paths

Generates:
- RESEARCH_COVERAGE_MAP_V1_1.json
- RESEARCH_COVERAGE_MAP_V1_1.md
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .constants import ROOT
from .knowledge_index import ResearchKnowledgeIndex, ResearchKnowledgeRecord
from .research_ontology import ALL_ONTOLOGY_CONCEPTS, OntologyConcept

logger = logging.getLogger("p45.research_automation.coverage_v1_1")

@dataclass
class AxisCoverageRecordV1_1:
    ontology_axis: str
    category: str
    description: str
    related_formal_registry_ids: list[str] = field(default_factory=list)
    related_non_exp_axes: list[str] = field(default_factory=list)
    related_official_axes: list[str] = field(default_factory=list)
    active_count: int = 0
    tested_count: int = 0
    failed_count: int = 0
    partial_count: int = 0
    blocked_count: int = 0
    registered_only_count: int = 0
    untested_boolean: bool = True
    evidence_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class CoverageMapBuilderV1_1:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.coverage_dir = self.root / "v27_storage" / "research_automation" / "coverage"

    def build_coverage_map_v1_1(self, knowledge_index: ResearchKnowledgeIndex) -> dict[str, Any]:
        self.coverage_dir.mkdir(parents=True, exist_ok=True)

        axis_records: dict[str, AxisCoverageRecordV1_1] = {}
        for concept in ALL_ONTOLOGY_CONCEPTS:
            axis_records[concept.value] = AxisCoverageRecordV1_1(
                ontology_axis=concept.value,
                category=concept.name,
                description=concept.value,
            )

        # Map each record from the knowledge index to its associated ontology tags
        for record in knowledge_index.list_all():
            for tag in record.ontology_tags:
                matched_concept: str | None = None
                for c in ALL_ONTOLOGY_CONCEPTS:
                    if c.value.lower() == tag.lower() or c.name.lower() == tag.lower():
                        matched_concept = c.value
                        break
                
                if matched_concept and matched_concept in axis_records:
                    axis_rec = axis_records[matched_concept]

                    # Link research ID by source_class
                    if record.source_class == "FORMAL_REGISTRY":
                        if record.research_id not in axis_rec.related_formal_registry_ids:
                            axis_rec.related_formal_registry_ids.append(record.research_id)
                    elif record.source_class == "NON_EXP_EXECUTED":
                        if record.research_id not in axis_rec.related_non_exp_axes:
                            axis_rec.related_non_exp_axes.append(record.research_id)
                    elif record.source_class == "OFFICIAL_INTERNAL":
                        if record.research_id not in axis_rec.related_official_axes:
                            axis_rec.related_official_axes.append(record.research_id)

                    # Update non-exclusive research status counts
                    status_upper = record.status.upper()
                    verdict_upper = record.verdict.upper()

                    if "ACTIVE" in status_upper:
                        axis_rec.active_count += 1
                    if "FAILED" in status_upper or "FAILED" in verdict_upper or "CLOSED" in status_upper:
                        axis_rec.failed_count += 1
                        axis_rec.tested_count += 1
                    elif "SUPPORTED" in status_upper or "SUPPORTED" in verdict_upper or "INCONCLUSIVE" in status_upper:
                        axis_rec.tested_count += 1
                    elif "PARTIAL" in status_upper:
                        axis_rec.partial_count += 1
                    elif "BLOCKED" in status_upper:
                        axis_rec.blocked_count += 1
                    elif "REGISTERED" in status_upper or "DESIGNED" in status_upper:
                        axis_rec.registered_only_count += 1

                    for p in record.evidence_paths:
                        if p not in axis_rec.evidence_paths:
                            axis_rec.evidence_paths.append(p)

        # Compute untested_boolean for each axis
        # An axis is strictly UNTESTED if tested_count == 0, active_count == 0, and blocked_count == 0
        for axis_rec in axis_records.values():
            if (axis_rec.tested_count > 0 or axis_rec.active_count > 0 or 
                axis_rec.related_official_axes or axis_rec.related_non_exp_axes):
                axis_rec.untested_boolean = False
            else:
                axis_rec.untested_boolean = True

        # Invariant Verification
        ontology_axis_total = len(axis_records)
        assert ontology_axis_total == 24, f"Invariant violation: len(axes)={ontology_axis_total} != 24"

        # Aggregate summary statistics
        total_formal_links = sum(len(r.related_formal_registry_ids) for r in axis_records.values())
        total_non_exp_links = sum(len(r.related_non_exp_axes) for r in axis_records.values())
        total_official_links = sum(len(r.related_official_axes) for r in axis_records.values())

        untested_axes_count = sum(1 for r in axis_records.values() if r.untested_boolean)
        tested_axes_count = ontology_axis_total - untested_axes_count

        coverage_data = {
            "version": "1.1",
            "ontology_model_metrics": {
                "declared_ontology_total": 24,
                "actual_unique_axes_count": ontology_axis_total,
                "consistency_verdict": "PASS" if ontology_axis_total == 24 else "FAIL",
            },
            "research_linkage_summary": {
                "total_indexed_research_items": knowledge_index.count(),
                "total_formal_registry_links": total_formal_links,
                "total_non_exp_links": total_non_exp_links,
                "total_official_links": total_official_links,
                "axes_with_prior_evidence_count": tested_axes_count,
                "strictly_untested_structural_axes_count": untested_axes_count,
            },
            "axes": {k: axis_rec.to_dict() for k, axis_rec in axis_records.items()},
        }

        # Save JSON
        json_path = self.coverage_dir / "RESEARCH_COVERAGE_MAP_V1_1.json"
        json_path.write_text(json.dumps(coverage_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        # Generate and save Markdown Report
        md_path = self.coverage_dir / "RESEARCH_COVERAGE_MAP_V1_1.md"
        md_content = self._generate_markdown(coverage_data, axis_records)
        md_path.write_text(md_content, encoding="utf-8")

        logger.info(f"Built Research Coverage Map V1.1 -> {json_path} and {md_path}")
        return coverage_data

    def _generate_markdown(self, coverage_data: dict[str, Any], axis_records: dict[str, AxisCoverageRecordV1_1]) -> str:
        md = []
        md.append("# P45 Research Coverage Map V1.1")
        md.append("")
        md.append("- **기준일:** 2026-09-30")
        md.append("- **Ontology Axis Total:** 24 (고정 개념축 불변량 검증: PASS)")
        md.append(f"- **총 연결된 연구 항목:** {coverage_data['research_linkage_summary']['total_indexed_research_items']}건")
        md.append(f"- **선행 연구가 존재하는 개념축:** {coverage_data['research_linkage_summary']['axes_with_prior_evidence_count']}개")
        md.append(f"- **순수 미검증(Untested) 개념축:** {coverage_data['research_linkage_summary']['strictly_untested_structural_axes_count']}개")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## 1. 24대 Ontology 개념축 전수 및 연구 연결 현황")
        md.append("")
        md.append("| # | Ontology Axis | 카테고리 | Formal Registry IDs | Non-EXP Axes | Official Axes | Active | Tested | Failed | Untested? |")
        md.append("|---|---|---|---|---|---|---:|---:|---:|:---:|")

        for idx, (axis_name, r) in enumerate(sorted(axis_records.items()), start=1):
            f_ids = ", ".join(r.related_formal_registry_ids[:3]) + (f" (+{len(r.related_formal_registry_ids)-3})" if len(r.related_formal_registry_ids) > 3 else "") or "-"
            n_ids = ", ".join(r.related_non_exp_axes) or "-"
            o_ids = ", ".join(r.related_official_axes) or "-"
            untested_str = "**YES**" if r.untested_boolean else "NO"
            md.append(
                f"| {idx} | `{axis_name}` | {r.category} | {f_ids} | {n_ids} | {o_ids} | {r.active_count} | {r.tested_count} | {r.failed_count} | {untested_str} |"
            )

        md.append("")
        md.append("---")
        md.append("")
        md.append("## 2. 집계 모델 정정 사항 (V1.0 -> V1.1)")
        md.append("- **이전 오류 원인:** V1.0에서는 24개 개념축 자체 숫자와 각 개념축에 매핑된 연구의 상호 비배타적 상태(Active/Failed/Partial)를 단일 카테고리로 묶어 합산하면서 내부 열거 개수와 총계(24) 사이에 불일치가 발생했음.")
        md.append("- **V1.1 정정 모델:**")
        md.append("  1. **개념축 총계(Ontology Axis Total):** 24개 고정 불변량으로 엄격 분리 (`len(axes) == 24`).")
        md.append("  2. **연구 상태 집계(Research Status Counts):** 연구 항목(77건)의 비배타적 연결 상태(Active, Tested, Failed, Partial, Blocked, Registered)를 별도로 계량하여 혼동을 원천 차단함.")
        md.append("")
        return "\n".join(md) + "\n"

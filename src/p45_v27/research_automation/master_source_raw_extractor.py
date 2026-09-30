"""Independent Raw Extractor, Fingerprint Locker, and Reconciliation Guard for Research Master Section C.

Extracts authoritative numbered research rows from:
90_RESEARCH/P45_RESEARCH_MASTER_INDEX_005.md (Section C)
WITHOUT translation, rewriting, summarization, or substitution.

Generates:
- MASTER_NON_EXP_RAW_SNAPSHOT.json
- MASTER_NON_EXP_RAW_SNAPSHOT.md
- MASTER_NON_EXP_SOURCE_FINGERPRINTS.json
- MASTER_SOURCE_IDENTITY_AUDIT.json
- MASTER_SOURCE_IDENTITY_AUDIT.md
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]


@dataclass
class MasterRawSourceItem:
    ordinal: int
    raw_source_text: str
    raw_title: str
    source_document: str
    source_heading: str
    source_line_start: int
    source_line_end: int
    source_fingerprint: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MasterRawSnapshot:
    source_document: str
    section_heading: str
    total_items: int
    section_fingerprint: str
    items: list[MasterRawSourceItem]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_document": self.source_document,
            "section_heading": self.section_heading,
            "total_items": self.total_items,
            "section_fingerprint": self.section_fingerprint,
            "items": [it.to_dict() for it in self.items],
        }


@dataclass
class MasterSourceIdentityAuditReport:
    raw_count: int = 0
    parsed_count: int = 0
    source_title_substitution: int = 0
    source_fingerprint_mismatch: int = 0
    missing_master_items: int = 0
    invented_source_items: int = 0
    ordinal_title_mismatch: int = 0
    raw_parser_disagreement: int = 0
    verdict: str = "PASS_MASTER_SOURCE_IDENTITY"
    mismatches: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MasterSourceRawExtractor:
    """Independent extractor for Research Master Section C without dependencies on knowledge builder."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.master_file = self.root / "90_RESEARCH" / "P45_RESEARCH_MASTER_INDEX_005.md"
        if not self.master_file.exists() and (ROOT / "90_RESEARCH" / "P45_RESEARCH_MASTER_INDEX_005.md").exists():
            self.master_file = ROOT / "90_RESEARCH" / "P45_RESEARCH_MASTER_INDEX_005.md"
        self.knowledge_dir = self.root / "v27_storage" / "research_automation" / "knowledge"

    @staticmethod
    def compute_item_fingerprint(
        source_doc_rel: str,
        section_heading: str,
        ordinal: int,
        raw_source_text: str,
    ) -> str:
        payload = f"{source_doc_rel}:{section_heading}:{ordinal}:{raw_source_text}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def compute_section_fingerprint(item_fingerprints: list[str]) -> str:
        payload = "|".join(item_fingerprints)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def extract_raw_section_c(self) -> MasterRawSnapshot:
        if not self.master_file.exists():
            raise FileNotFoundError(f"Master file not found: {self.master_file}")

        text = self.master_file.read_text(encoding="utf-8")
        lines = text.splitlines()

        sec_c_start = -1
        sec_c_end = -1
        sec_heading = ""

        for idx, line in enumerate(lines):
            if line.strip().startswith("## C. EXP ID 없이 실제 계산"):
                sec_c_start = idx
                sec_heading = line.strip()
            elif sec_c_start != -1 and line.strip().startswith("## D."):
                sec_c_end = idx
                break

        if sec_c_start == -1:
            raise ValueError("Section C heading not found in Research Master")
        if sec_c_end == -1:
            sec_c_end = len(lines)

        doc_base = self.root if self.master_file.is_relative_to(self.root) else ROOT
        rel_doc = str(self.master_file.relative_to(doc_base)).replace("\\", "/")

        items: list[MasterRawSourceItem] = []
        item_fingerprints: list[str] = []

        for line_idx in range(sec_c_start + 1, sec_c_end):
            line_str = lines[line_idx].strip()
            m = re.match(r"^(\d+)\.\s*(.*)", line_str)
            if not m:
                continue

            ordinal = int(m.group(1))
            raw_source_text = m.group(2).strip()

            # Raw title: clean text before status/em-dash if any, keeping full untouched Korean title
            raw_title = raw_source_text.split("—")[0].strip().rstrip(".")

            fp = self.compute_item_fingerprint(
                source_doc_rel=rel_doc,
                section_heading=sec_heading,
                ordinal=ordinal,
                raw_source_text=raw_source_text,
            )
            item_fingerprints.append(fp)

            items.append(
                MasterRawSourceItem(
                    ordinal=ordinal,
                    raw_source_text=raw_source_text,
                    raw_title=raw_title,
                    source_document=rel_doc,
                    source_heading=sec_heading,
                    source_line_start=line_idx + 1,
                    source_line_end=line_idx + 1,
                    source_fingerprint=fp,
                )
            )

        sec_fp = self.compute_section_fingerprint(item_fingerprints)

        return MasterRawSnapshot(
            source_document=rel_doc,
            section_heading=sec_heading,
            total_items=len(items),
            section_fingerprint=sec_fp,
            items=items,
        )

    def reconcile_parsers(
        self,
        raw_snapshot: MasterRawSnapshot,
        production_items: list[Any],
    ) -> MasterSourceIdentityAuditReport:
        """Reconciles 1st independent raw extractor with 2nd production parser."""
        report = MasterSourceIdentityAuditReport()
        report.raw_count = raw_snapshot.total_items
        report.parsed_count = len(production_items)

        if report.raw_count != report.parsed_count:
            report.raw_parser_disagreement += abs(report.raw_count - report.parsed_count)
            report.mismatches.append({
                "type": "COUNT_MISMATCH",
                "raw_count": report.raw_count,
                "parsed_count": report.parsed_count,
            })

        prod_by_ordinal = {}
        for it in production_items:
            ord_val = getattr(it, "ordinal", None)
            if ord_val is None:
                # Try parsing from source_item_id or details
                sid = getattr(it, "source_item_id", "")
                m = re.search(r"SRC-NONEXP-(\d+)", sid)
                if m:
                    ord_val = int(m.group(1))
            if ord_val is not None:
                prod_by_ordinal[ord_val] = it

        # Check each raw item against production
        for raw_it in raw_snapshot.items:
            prod_it = prod_by_ordinal.get(raw_it.ordinal)
            if prod_it is None:
                report.missing_master_items += 1
                report.mismatches.append({
                    "type": "MISSING_MASTER_ITEM",
                    "ordinal": raw_it.ordinal,
                    "raw_title": raw_it.raw_title,
                })
                continue

            prod_raw_title = getattr(prod_it, "raw_title", getattr(prod_it, "source_title", ""))
            prod_raw_text = getattr(prod_it, "raw_source_text", getattr(prod_it, "evidence_reference", ""))
            prod_fp = getattr(prod_it, "source_fingerprint", "")

            # Check title substitution
            if prod_raw_title != raw_it.raw_title:
                report.source_title_substitution += 1
                report.mismatches.append({
                    "type": "TITLE_SUBSTITUTION",
                    "ordinal": raw_it.ordinal,
                    "expected_raw_title": raw_it.raw_title,
                    "actual_parsed_title": prod_raw_title,
                })

            # Check fingerprint match
            if prod_fp and prod_fp != raw_it.source_fingerprint:
                report.source_fingerprint_mismatch += 1
                report.mismatches.append({
                    "type": "FINGERPRINT_MISMATCH",
                    "ordinal": raw_it.ordinal,
                    "expected_fp": raw_it.source_fingerprint,
                    "actual_fp": prod_fp,
                })

        # Check for invented items in production parser
        raw_ordinals = {it.ordinal for it in raw_snapshot.items}
        for ord_val, prod_it in prod_by_ordinal.items():
            if ord_val not in raw_ordinals:
                report.invented_source_items += 1
                report.mismatches.append({
                    "type": "INVENTED_ITEM",
                    "ordinal": ord_val,
                    "title": getattr(prod_it, "source_title", ""),
                })

        # Final verdict determination
        total_errors = (
            report.source_title_substitution
            + report.source_fingerprint_mismatch
            + report.missing_master_items
            + report.invented_source_items
            + report.ordinal_title_mismatch
            + report.raw_parser_disagreement
        )

        if total_errors == 0:
            report.verdict = "PASS_MASTER_SOURCE_IDENTITY"
        else:
            report.verdict = "BLOCKED_MASTER_SOURCE_IDENTITY"

        return report

    def save_snapshot(self, snapshot: MasterRawSnapshot) -> tuple[Path, Path, Path]:
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.knowledge_dir / "MASTER_NON_EXP_RAW_SNAPSHOT.json"
        md_path = self.knowledge_dir / "MASTER_NON_EXP_RAW_SNAPSHOT.md"
        fp_path = self.knowledge_dir / "MASTER_NON_EXP_SOURCE_FINGERPRINTS.json"

        # 1. JSON Snapshot
        json_path.write_text(json.dumps(snapshot.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

        # 2. Markdown Snapshot
        md = [
            "# Research Master Section C — Raw Source Snapshot",
            "",
            f"- **Source Document:** `{snapshot.source_document}`",
            f"- **Section Heading:** `{snapshot.section_heading}`",
            f"- **Total Non-EXP Raw Items:** **{snapshot.total_items}**",
            f"- **Section Fingerprint:** `{snapshot.section_fingerprint}`",
            "",
            "---",
            "",
            "## Exact Raw Source Items",
            "",
            "| # | Raw Title | Line Range | SHA-256 Fingerprint | Raw Source Text |",
            "|---|---|---|---|---|",
        ]
        for it in snapshot.items:
            md.append(
                f"| {it.ordinal} | **{it.raw_title}** | L{it.source_line_start} | `{it.source_fingerprint[:16]}...` | {it.raw_source_text} |"
            )
        md.append("")
        md_path.write_text("\n".join(md), encoding="utf-8")

        # 3. Fingerprints JSON
        fp_dict = {
            "source_document": snapshot.source_document,
            "section_heading": snapshot.section_heading,
            "section_fingerprint": snapshot.section_fingerprint,
            "total_items": snapshot.total_items,
            "item_fingerprints": {
                str(it.ordinal): {
                    "raw_title": it.raw_title,
                    "fingerprint": it.source_fingerprint,
                    "line_number": it.source_line_start,
                }
                for it in snapshot.items
            },
        }
        fp_path.write_text(json.dumps(fp_dict, indent=2, ensure_ascii=False), encoding="utf-8")

        return json_path, md_path, fp_path

    def save_identity_audit(self, report: MasterSourceIdentityAuditReport) -> tuple[Path, Path]:
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.knowledge_dir / "MASTER_SOURCE_IDENTITY_AUDIT.json"
        md_path = self.knowledge_dir / "MASTER_SOURCE_IDENTITY_AUDIT.md"

        json_path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

        md = [
            "# Master Source Identity & Fingerprint Reconciliation Audit Report",
            "",
            f"- **Final Verdict:** **`{report.verdict}`**",
            f"- **Master Raw Snapshot Count:** **{report.raw_count}**",
            f"- **Production Parser Count:** **{report.parsed_count}**",
            f"- **Source Title Substitution:** **{report.source_title_substitution}**",
            f"- **Source Fingerprint Mismatch:** **{report.source_fingerprint_mismatch}**",
            f"- **Missing Master Items:** **{report.missing_master_items}**",
            f"- **Invented Source Items:** **{report.invented_source_items}**",
            f"- **Ordinal/Title Mismatch:** **{report.ordinal_title_mismatch}**",
            f"- **Raw/Parser Disagreement:** **{report.raw_parser_disagreement}**",
            "",
            "---",
            "",
            "## Reconciliation Status",
            "",
        ]
        if report.verdict == "PASS_MASTER_SOURCE_IDENTITY":
            md.append("> [!NOTE]")
            md.append("> **PASS_MASTER_SOURCE_IDENTITY**: 1차 독립 Raw 추출 스냅샷과 2차 Production 파서 결과가 1:1 완벽하게 일치합니다.")
            md.append("> 제목 변형, 번역, 요약, 임의 발명, 누락이 전혀 없습니다.")
        else:
            md.append("> [!CAUTION]")
            md.append(f"> **{report.verdict}**: 원천 연구 마스터와의 불일치가 발견되어 자동 연구 생성이 차단(Fail-Closed)되었습니다.")
            md.append("")
            md.append("### Mismatches")
            md.append("")
            for m in report.mismatches:
                md.append(f"- `{m}`")

        md.append("")
        md_path.write_text("\n".join(md), encoding="utf-8")

        return json_path, md_path

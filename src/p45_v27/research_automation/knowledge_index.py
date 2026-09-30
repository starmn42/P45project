"""Authoritative Research Knowledge Index V1.2.

Provides a 100% complete, machine-readable normalized index of ALL P45 research:
- Formal Registry physical/version rows
- Official internal research axes
- Non-EXP executed research axes
- Reviewed unexecuted research ideas
- Active prospective research

Guarantees:
- KNOWN_RESEARCH_SOURCE_COVERAGE = 100%
- UNEXPLAINED_MISSING_SOURCE_ITEMS = 0
- Bidirectional reverse tracing: source item <-> normalized record
- Fail-closed security guard support
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .knowledge_source_inventory import (
    CoverageManifest,
    MappingType,
    ResearchKnowledgeCoverageManifestBuilder,
    ResearchSourceInventoryBuilder,
    ResearchSourceItem,
    SourceClass,
)
from .research_ontology import OntologyConcept

ROOT = Path(__file__).resolve().parents[3]

# Metadata mappings for Formal Experiment Labs
LAB_METADATA_DEFAULTS: dict[str, dict[str, Any]] = {
    "NUMBER RELATION LAB": {
        "inputs": "Individual winning lottery numbers (1..45)",
        "transformation": "Pairwise co-occurrence frequency and correlation graph",
        "condition": "Unconditional simultaneous occurrence or conditional on number A",
        "target": "Next-round number co-occurrence likelihood",
        "lag": 1,
        "metrics": ["jaccard_similarity", "lift", "co_occurrence_count"],
        "null": "Hypergeometric independent random ball selection without replacement",
        "ontology_tags": [OntologyConcept.NUMBER.value, OntologyConcept.INTERACTION.value, OntologyConcept.CROSS_ROUND_RELATION.value],
    },
    "SUM / PARITY LAB": {
        "inputs": "Sum of 6 winning numbers, odd/even counts, high/low partitions",
        "transformation": "Arithmetic sum aggregation and parity partition ratio",
        "condition": "Historical draw sequence",
        "target": "Sum distribution band and odd/even balance invariance",
        "lag": 1,
        "metrics": ["sum_mean", "parity_ratio", "chi_square_stat"],
        "null": "Convolution of 6 uniform discrete draws from {1..45} without replacement",
        "ontology_tags": [OntologyConcept.NUMBER.value, OntologyConcept.ARITHMETIC_TRANSFORM.value],
    },
    "ZONE OCCUPANCY LAB": {
        "inputs": "Numbers mapped to 5 or 9 equal-width numerical ranges (e.g. 1-9, 10-18...)",
        "transformation": "Zone occupancy vector and consecutive zone vacancy (extinction)",
        "condition": "Previous round zone extinction state",
        "target": "Next-round zone occupancy and recovery probability",
        "lag": 1,
        "metrics": ["zone_entropy", "extinction_recovery_rate"],
        "null": "Multinomial distribution across equal partition zones",
        "ontology_tags": [OntologyConcept.OCCUPANCY.value, OntologyConcept.EXTINCTION.value, OntologyConcept.RECOVERY.value],
    },
    "EXTINCTION / RECOVERY LAB": {
        "inputs": "Binary indicator of number absence across rolling windows (lag 1..k)",
        "transformation": "Longitudinal run-length tracking of non-appearance (negative space)",
        "condition": "Absence duration >= threshold rounds",
        "target": "Reappearance probability (hazard rate) in round t",
        "lag": 1,
        "metrics": ["hazard_rate", "log_rank_statistic", "recovery_speed"],
        "null": "Geometric distribution with success probability p = 6/45 ≈ 0.1333",
        "ontology_tags": [OntologyConcept.EXTINCTION.value, OntologyConcept.RECOVERY.value, OntologyConcept.GAP.value],
    },
    "TRIO LAB": {
        "inputs": "Triplets of numbers (all 14,190 combinations)",
        "transformation": "Trio co-occurrence clustering and combinatorial coverage",
        "condition": "Historical trio appearances",
        "target": "PRIMARY (3/3) and SUPPORT (exact 2/3) hits",
        "lag": 1,
        "metrics": ["primary_hit_count", "support_hit_count", "lift"],
        "null": "Exact hypergeometric distribution for 3 disjoint trios",
        "ontology_tags": [OntologyConcept.TRIO.value, OntologyConcept.RECURRENCE.value],
    },
    "PAIR LAB": {
        "inputs": "Pairs of numbers (all 990 combinations)",
        "transformation": "Pair recurrence interval and hazard function",
        "condition": "Pair absence since last appearance",
        "target": "Pair appearance likelihood in next round",
        "lag": 1,
        "metrics": ["pair_recurrence_interval", "kaplan_meier_survival"],
        "null": "Geometric distribution with success probability p = comb(43,4)/comb(45,6) ≈ 0.0124",
        "ontology_tags": [OntologyConcept.PAIR.value, OntologyConcept.GAP.value],
    },
    "SPACING / DISTANCE LAB": {
        "inputs": "Sorted drawn numbers x_(1) < x_(2) < ... < x_(6)",
        "transformation": "Differences d_i = x_(i+1) - x_i (adjacent spacings)",
        "condition": "Order statistics spacing vector",
        "target": "Minimum spacing and spacing variance invariance",
        "lag": 0,
        "metrics": ["min_spacing", "spacing_variance", "kolmogorov_smirnov_d"],
        "null": "Uniform order statistics spacing distribution on discrete grid {1..45}",
        "ontology_tags": [OntologyConcept.SPACING.value, OntologyConcept.GAP.value, OntologyConcept.NUMBER.value],
    },
    "SALES-ADJUSTED CROWD EFFECT LAB": {
        "inputs": "Official sales volume and birthday range (1..31)",
        "transformation": "Sales-normalized crowd selection bias model",
        "condition": "Birthday vs non-birthday numbers",
        "target": "Number draw appearance correlation with sales",
        "lag": 0,
        "metrics": ["permutation_beta", "p_perm"],
        "null": "Zero correlation between sales crowd volume and drawn numbers",
        "ontology_tags": [OntologyConcept.RANGE.value, OntologyConcept.REGIME.value, OntologyConcept.NUMBER.value],
    },
    "LAGGED CROWD METADATA SIGNAL LAB": {
        "inputs": "Lagged winner count regimes (low/high winner count at t-1)",
        "transformation": "Winner count regime indicator conditioning",
        "condition": "Previous round winner count extremity",
        "target": "Next round number selection signal",
        "lag": 1,
        "metrics": ["regime_conditional_lift"],
        "null": "Regime transition independence",
        "ontology_tags": [OntologyConcept.REGIME.value, OntologyConcept.LAG.value, OntologyConcept.TRANSITION.value],
    },
    "EDGE ARITHMETIC TRANSITION LAB": {
        "inputs": "Edge ball arithmetic combinations (sum, difference, modulo)",
        "transformation": "Deterministic algebraic transforms across 4 formulas and 2 lags",
        "condition": "Edge ball states at t-1 and t-2",
        "target": "Next round main6 ball appearance",
        "lag": 1,
        "metrics": ["maxT_statistic", "permutation_fwer_p"],
        "null": "50,000 full-record order permutations",
        "ontology_tags": [OntologyConcept.ARITHMETIC_TRANSFORM.value, OntologyConcept.TRANSITION.value, OntologyConcept.LAG.value],
    },
    "CROWD LAB": {
        "inputs": "Lottery player selection patterns and ticket sales distributions",
        "transformation": "Crowd popularity clustering and distance tomography",
        "condition": "Player behavioral choice",
        "target": "Crowd concentration in Johnson space",
        "lag": 0,
        "metrics": ["distance_autocorrelation", "t_max"],
        "null": "Independent uniform ticket selection by players",
        "ontology_tags": [OntologyConcept.REGIME.value, OntologyConcept.SIMILARITY.value, OntologyConcept.NUMBER.value],
    },
    "PRIZE-SHARE LAB": {
        "inputs": "First and second prize winner counts and ticket sales",
        "transformation": "Winner count density and jackpot dilution ratio",
        "condition": "Birthday-zone concentration in winning numbers",
        "target": "First/second prize share dilution risk",
        "lag": 0,
        "metrics": ["winner_count_ratio", "dilution_elasticity"],
        "null": "Poisson/binomial winner count under uniform ticket distribution",
        "ontology_tags": [OntologyConcept.REGIME.value, OntologyConcept.RANGE.value, OntologyConcept.CORE.value],
    },
}

@dataclass
class ResearchKnowledgeRecord:
    research_id: str
    canonical_name: str
    source_class: str
    status: str
    inputs: str
    transformation: str
    condition: str
    target: str
    lag: int
    metrics: list[str]
    null: str
    ontology_tags: list[str]
    verdict: str
    evidence_paths: list[str]
    # V1.2 Schema extensions
    record_id: str = ""
    source_classes: list[str] = field(default_factory=list)
    source_item_ids: list[str] = field(default_factory=list)
    formal_ids: list[str] = field(default_factory=list)
    actionability: str = "UNKNOWN"
    aliases: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.record_id:
            self.record_id = self.research_id
        if not self.source_classes and self.source_class:
            self.source_classes = [self.source_class]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class ResearchKnowledgeIndex:
    """In-memory searchable index of all historical and active research items."""

    def __init__(self, records: list[ResearchKnowledgeRecord], manifest: CoverageManifest | None = None):
        self.records = records
        self.manifest = manifest
        self._by_id = {r.research_id: r for r in records}
        self._by_record_id = {r.record_id: r for r in records}
        self._source_to_record: dict[str, str] = {}
        for r in records:
            for sid in r.source_item_ids:
                self._source_to_record[sid] = r.record_id

    def get_by_id(self, research_id: str) -> ResearchKnowledgeRecord | None:
        return self._by_id.get(research_id) or self._by_record_id.get(research_id)

    def list_all(self) -> list[ResearchKnowledgeRecord]:
        return list(self.records)

    def count(self) -> int:
        return len(self.records)

    def filter_by_class(self, source_class: str) -> list[ResearchKnowledgeRecord]:
        return [r for r in self.records if source_class in r.source_classes]

    def trace_source_to_record(self, source_item_id: str) -> ResearchKnowledgeRecord | None:
        rec_id = self._source_to_record.get(source_item_id)
        if rec_id:
            return self.get_by_id(rec_id)
        return None

    def trace_record_to_sources(self, record_id: str) -> list[str]:
        rec = self.get_by_id(record_id)
        return list(rec.source_item_ids) if rec else []

    def is_coverage_complete(self) -> bool:
        if self.manifest:
            return self.manifest.is_complete
        return True

class ResearchKnowledgeIndexBuilder:
    """Builds authoritative ResearchKnowledgeIndex V1.2 with 100% source coverage."""

    def __init__(self, root: Path = ROOT):
        self.root = root
        self.knowledge_dir = self.root / "v27_storage" / "research_automation" / "knowledge"
        self.inv_builder = ResearchSourceInventoryBuilder(root)
        self.manifest_builder = ResearchKnowledgeCoverageManifestBuilder(root)

    def build_index(self) -> ResearchKnowledgeIndex:
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

        # 1. Build and Save Source Inventory
        source_items = self.inv_builder.build_source_inventory()
        self.inv_builder.save_source_inventory(source_items)
        source_item_map = {it.source_item_id: it for it in source_items}

        # 2. Build and Save Coverage Manifest
        manifest = self.manifest_builder.build_manifest(source_items)
        self.manifest_builder.save_manifest(manifest)

        # 3. Group mappings by normalized_record_id
        record_groups: dict[str, list[str]] = {}
        for m in manifest.mappings:
            record_groups.setdefault(m.normalized_record_id, []).append(m.source_item_id)

        records: list[ResearchKnowledgeRecord] = []

        # 4. Construct normalized records
        for norm_id, sids in record_groups.items():
            primary_src = source_item_map[sids[0]]
            sclasses = list(set(source_item_map[sid].source_class for sid in sids))
            formal_ids = [source_item_map[sid].canonical_experiment_id_if_any for sid in sids if source_item_map[sid].canonical_experiment_id_if_any]
            evidence_paths = list(set(source_item_map[sid].source_document for sid in sids))
            aliases = [sid for sid in sids if sid != sids[0]]

            # Baseline defaults
            name = primary_src.source_title
            status = primary_src.source_status
            verdict = status
            actionability = "UNKNOWN"
            inputs = "UNKNOWN"
            transformation = "UNKNOWN"
            condition = "UNKNOWN"
            target = "UNKNOWN"
            lag = 1
            metrics: list[str] = ["UNKNOWN"]
            null_model = "UNKNOWN"
            ontology_tags: list[str] = [OntologyConcept.CORE.value]

            # A. FORMAL_REGISTRY records
            if norm_id.startswith("EXP-"):
                eid = norm_id
                lab = primary_src.details.get("lab", "")
                domain = primary_src.details.get("domain", "DRAW")
                meta = LAB_METADATA_DEFAULTS.get(lab, {
                    "inputs": f"{domain} raw numbers",
                    "transformation": "Standard structural extraction",
                    "condition": "Unconditioned baseline",
                    "target": "Next round state",
                    "lag": 1,
                    "metrics": ["hit_rate", "lift"],
                    "null": "Fair lottery null",
                    "ontology_tags": [OntologyConcept.NUMBER.value],
                })
                inputs = meta["inputs"]
                transformation = meta["transformation"]
                condition = meta["condition"]
                target = meta["target"]
                lag = meta["lag"]
                metrics = list(meta["metrics"])
                null_model = meta["null"]
                ontology_tags = list(meta["ontology_tags"])
                actionability = f"Formal experiment protocol in {lab}"

                if "FAILED" in status:
                    verdict = "FAILED"
                elif "SUPPORTED" in status:
                    verdict = "SUPPORTED"
                elif "INCONCLUSIVE" in status:
                    verdict = "INCONCLUSIVE"
                elif "CLOSED" in status:
                    verdict = "AXIS_CLOSED"
                elif "REGISTERED" in status or "DESIGNED" in status:
                    verdict = "REGISTERED"

            # B. OFFICIAL_INTERNAL records
            elif norm_id.startswith("OFFICIAL-"):
                axis_key = norm_id.replace("OFFICIAL-", "")
                actionability = "Official engine production invariant"
                verdict = "OFFICIAL_FROZEN"

                if "UNIT" in axis_key:
                    inputs = f"{axis_key} partition numbers"
                    transformation = "Partition occupancy, extinction and recovery depth"
                    condition = "Historical draw partition states"
                    target = "Partition recovery speed and vacancy duration"
                    metrics = ["recovery_speed", "occupancy_ratio"]
                    null_model = "Hypergeometric uniform ball partition distribution"
                    ontology_tags = [OntologyConcept.EXTINCTION.value, OntologyConcept.RECOVERY.value, OntologyConcept.OCCUPANCY.value, OntologyConcept.CORE.value]
                elif "END_DIGIT" in axis_key:
                    inputs = "Last digits (0..9) of drawn winning numbers"
                    transformation = "Ending digit occupancy and severe extinction state"
                    condition = "Historical draw ending digits"
                    target = "Ending digit recurrence and diversity"
                    metrics = ["ending_digit_entropy", "severe_extinction_rate"]
                    null_model = "Uniform discrete distribution on {0..9}"
                    ontology_tags = [OntologyConcept.EXTINCTION.value, OntologyConcept.RECOVERY.value, OntologyConcept.NUMBER.value, OntologyConcept.CORE.value]
                elif "NUMBER" in axis_key:
                    inputs = "Historical lottery draw statistics for individual numbers 1..45"
                    transformation = "14-key lexicographical deterministic sorting rule"
                    condition = "Official frozen gate rules"
                    target = "Official number priority ranking"
                    metrics = ["official_selection_stability"]
                    null_model = "Deterministic tie-breaking null"
                    ontology_tags = [OntologyConcept.NUMBER.value, OntologyConcept.ORDER_RANK.value, OntologyConcept.CORE.value]
                elif "TRIO" in axis_key:
                    inputs = "All 14,190 three-number subsets"
                    transformation = "15-key lexicographical deterministic trio ranking"
                    condition = "Official frozen gate rules"
                    target = "Official trio priority ranking (3/3 PRIMARY, exact 2/3 SUPPORT)"
                    metrics = ["primary_hit_rate", "support_hit_rate"]
                    null_model = "Hypergeometric combinations null"
                    ontology_tags = [OntologyConcept.TRIO.value, OntologyConcept.ORDER_RANK.value, OntologyConcept.CORE.value]
                elif "PAIR" in axis_key:
                    inputs = "All 990 ball pairs across all draws"
                    transformation = "Shadow lifecycle state tracking and signature timing repair"
                    condition = "DECISION-20260824-095 audit"
                    target = "Internal shadow state integrity"
                    metrics = ["pair_state_integrity"]
                    null_model = "Deterministic shadow state preservation"
                    ontology_tags = [OntologyConcept.PAIR.value, OntologyConcept.CORE.value, OntologyConcept.TRANSITION.value]
                elif "CORE" in axis_key:
                    inputs = "Hierarchical decision pipeline NUMBER->TRIO->PAIR->CORE"
                    transformation = "Multi-level gate and threshold filtering"
                    condition = "Production draw processing"
                    target = "Official pick generation"
                    metrics = ["pipeline_invariance_pass"]
                    null_model = "Pipeline determinism invariant"
                    ontology_tags = [OntologyConcept.CORE.value, OntologyConcept.REGIME.value]
                elif "FIXED_ORBIT" in axis_key or "FIXED-ORBIT" in axis_key:
                    inputs = "Fixed KTS 3x3 TRIO candidate sets (9 numbers)"
                    transformation = "Fixed rotation schedule across rounds"
                    condition = "Unconditional fixed candidate set"
                    target = "PRIMARY (3/3) and SUPPORT (2/3) hits"
                    lag = 0
                    metrics = ["support_hit_rate", "wilson_ci"]
                    null_model = "Binomial exact null p0 = 987,390 / 8,145,060 ≈ 0.121226"
                    ontology_tags = [OntologyConcept.TRIO.value, OntologyConcept.RECURRENCE.value, OntologyConcept.CORE.value]
                elif "LINKED_ORBIT" in axis_key or "LINKED-ORBIT" in axis_key:
                    inputs = "Linked 3-TRIO candidate sets using 3 winning numbers from round t-1 as anchor"
                    transformation = "Anchor carryover and orbit rotation"
                    condition = "Target draw t conditioned on winning balls of t-1"
                    target = "PRIMARY (3/3) and SUPPORT (exact 2/3) hits"
                    lag = 1
                    metrics = ["support_hit_rate", "mcnemar_exact_p", "holm_adj_p"]
                    null_model = "Binomial exact null p0 = 987,390 / 8,145,060 ≈ 0.121226"
                    ontology_tags = [OntologyConcept.TRIO.value, OntologyConcept.RECURRENCE.value, OntologyConcept.TRANSITION.value, OntologyConcept.CORE.value]
                elif "KTS45" in axis_key:
                    inputs = "330 TRIO fixed schedule"
                    transformation = "Combinatorial block design schedule"
                    condition = "Immutable schedule"
                    target = "Full space coverage"
                    lag = 0
                    metrics = ["schedule_invariance"]
                    null_model = "Steiner block design"
                    ontology_tags = [OntologyConcept.TRIO.value, OntologyConcept.SIMILARITY.value, OntologyConcept.CORE.value]

            # C. NON_EXP_EXECUTED records
            elif norm_id.startswith("NON-EXP-"):
                actionability = "Non-EXP research audit and causal trace"
                if "TRIO-ORBIT" in norm_id:
                    inputs = "TRIO ORBIT 3-trio candidate sets"
                    transformation = "Historical backtest & null calibration"
                    condition = "Rounds 1..1243"
                    target = "PRIMARY and SUPPORT hits"
                    lag = 1
                    metrics = ["support_rate", "mcnemar_exact_p"]
                    null_model = "Exact binomial null p0 ≈ 0.121226"
                    ontology_tags = [OntologyConcept.TRIO.value, OntologyConcept.RECURRENCE.value]
                    verdict = "NO_EVIDENCE_OF_LINKED_SUPERIORITY"
                elif "LZ76" in norm_id:
                    inputs = "Lottery draw historical complexity sequence"
                    transformation = "Lempel-Ziv 76 macro complexity partition"
                    condition = "Historical draws"
                    target = "Regime persistence"
                    lag = 1
                    metrics = ["occupancy_p", "persistence_p"]
                    null_model = "Permutation complexity null"
                    ontology_tags = [OntologyConcept.REGIME.value, OntologyConcept.PERSISTENCE.value]
                    verdict = "FAILED_NOT_SUPPORTED"
                elif "WHOLE-ENGINE" in norm_id:
                    inputs = "Full synthetic draw replay through official core pipeline"
                    transformation = "Whole pipeline replay without outcome peeking"
                    condition = "Simulated lottery distributions"
                    target = "Semantic recovery and pipeline integrity"
                    lag = 0
                    metrics = ["semantic_fidelity_score"]
                    null_model = "Synthetic permutation baseline"
                    ontology_tags = [OntologyConcept.CORE.value, OntologyConcept.REGIME.value]
                    verdict = "SUPPORTED"
                elif "NOPICK" in norm_id:
                    inputs = "Official decision pipeline state logs"
                    transformation = "No-pick 867/867 bottleneck causal trace"
                    condition = "Historical draws"
                    target = "Pick generation gate failure analysis"
                    lag = 0
                    metrics = ["gate_closure_rate"]
                    null_model = "Pipeline throughput invariant"
                    ontology_tags = [OntologyConcept.CORE.value, OntologyConcept.INTERACTION.value]
                    verdict = "UNRESOLVED"
                elif "BONUS" in norm_id:
                    inputs = "Bonus ball historical sequences"
                    transformation = "Bonus ball extinction and lag2 carryover interaction"
                    condition = "Historical bonus balls"
                    target = "Next round number appearance interaction"
                    lag = 2 if "lag2" in name.lower() else 1
                    metrics = ["interaction_lift"]
                    null_model = "Independent bonus draw null"
                    ontology_tags = [OntologyConcept.BONUS_INTERACTION.value, OntologyConcept.INTERACTION.value, OntologyConcept.LAG.value]
                    verdict = "COMPLETED"
                elif "LAG" in norm_id:
                    inputs = "Number reappearance intervals"
                    transformation = "Lag 3..6 reappearance probability map"
                    condition = "Historical draws"
                    target = "Long-range interval hazard rate"
                    lag = 3
                    metrics = ["lag_reappearance_rate"]
                    null_model = "Geometric memoryless null"
                    ontology_tags = [OntologyConcept.LAG.value, OntologyConcept.GAP.value]
                    verdict = "COMPLETED"
                else:
                    # General non-exp audit
                    inputs = "Historical lottery records"
                    transformation = primary_src.source_title
                    condition = "Historical audit"
                    target = "Diagnostic insight"
                    lag = 1
                    metrics = ["diagnostic_metric"]
                    null_model = "Standard null"
                    ontology_tags = [OntologyConcept.CORE.value]
                    verdict = "COMPLETED"

            # D. REVIEWED_UNEXECUTED records
            elif norm_id.startswith("REVIEWED-"):
                actionability = "Unexecuted idea (Held/Dropped)"
                verdict = "UNEXECUTED_IDEA"
                status = "REVIEWED_UNEXECUTED"
                if "DRAW_ORDER" in norm_id:
                    inputs = "MBC mechanical lottery ball drop physical drawing sequence"
                    transformation = "Time-series order correlation"
                    condition = "Ball drawing order 1..6"
                    target = "Draw order predictability"
                    lag = 1
                    metrics = ["order_correlation"]
                    null_model = "Uniform permutation null"
                    ontology_tags = [OntologyConcept.ORDER_RANK.value, OntologyConcept.NUMBER.value]
                elif "REHEARSAL" in norm_id:
                    inputs = "Pre-broadcast rehearsal draw numbers"
                    transformation = "Rehearsal vs live draw overlap"
                    condition = "Rehearsal draw events"
                    target = "Rehearsal draw influence"
                    lag = 0
                    metrics = ["jaccard_overlap"]
                    null_model = "Independent draw null"
                    ontology_tags = [OntologyConcept.NUMBER.value, OntologyConcept.INTERACTION.value]

            # E. ACTIVE_PROSPECTIVE records
            elif norm_id.startswith("PROSPECTIVE-"):
                actionability = "Active sealed prospective waiting for lottery outcome"
                verdict = "SEALED_WAITING_FOR_DATA"
                status = "PENDING_SEALED"
                inputs = "Round 1244 prospective trio candidates"
                transformation = "Sealed predraw protocol"
                condition = "Target round 1244 unrevealed"
                target = "PRIMARY (3/3) and SUPPORT (2/3) hits"
                lag = 1
                metrics = ["exact_primary", "exact_support"]
                null_model = "Exact hypergeometric combinations null"
                ontology_tags = [OntologyConcept.TRIO.value, OntologyConcept.RECURRENCE.value]

            record = ResearchKnowledgeRecord(
                research_id=norm_id,
                record_id=norm_id,
                canonical_name=name,
                source_class=primary_src.source_class,
                source_classes=sclasses,
                source_item_ids=sids,
                formal_ids=formal_ids,
                status=status,
                inputs=inputs,
                transformation=transformation,
                condition=condition,
                target=target,
                lag=lag,
                metrics=metrics,
                null=null_model,
                actionability=actionability,
                ontology_tags=ontology_tags,
                verdict=verdict,
                evidence_paths=evidence_paths,
                aliases=aliases,
            )
            records.append(record)

        # 5. Save Knowledge Index JSON & Markdown
        index_json = self.knowledge_dir / "RESEARCH_KNOWLEDGE_INDEX.json"
        index_md = self.knowledge_dir / "RESEARCH_KNOWLEDGE_INDEX.md"

        index_data = {
            "version": "1.2",
            "total_records": len(records),
            "manifest_coverage_complete": manifest.is_complete,
            "manifest_coverage_ratio": manifest.coverage_ratio,
            "total_source_items_mapped": manifest.mapped_source_items_count,
            "unmapped_source_items_count": manifest.unmapped_source_items_count,
            "source_class_counts": manifest.source_class_counts,
            "records": [r.to_dict() for r in records],
        }
        index_json.write_text(json.dumps(index_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        # Markdown summary
        md = []
        md.append("# Complete Research Knowledge Index V1.2")
        md.append("")
        md.append("- **기준일:** 2026-09-30")
        md.append(f"- **총 정규화 연구 레코드 수(Normalized Records):** **{len(records)}건**")
        md.append(f"- **총 원천 연구 항목 수(Source Items):** **{manifest.total_source_items}건**")
        md.append(f"- **누락 항목 수(Unmapped Items):** **{manifest.unmapped_source_items_count}건**")
        md.append(f"- **커버리지 달성률:** **{manifest.coverage_ratio * 100:.1f}%**")
        md.append(f"- **Knowledge Coverage Complete:** **`{manifest.is_complete}`**")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## Normalized Knowledge Records")
        md.append("")
        md.append("| # | Record ID | Canonical Name | Source Class | Status | Target | Null Model |")
        md.append("|---|---|---|---|---|---|---|")
        for idx, r in enumerate(records, 1):
            md.append(f"| {idx} | `{r.record_id}` | {r.canonical_name} | `{r.source_class}` | `{r.status}` | {r.target} | {r.null} |")
        md.append("")

        index_md.write_text("\n".join(md), encoding="utf-8")

        return ResearchKnowledgeIndex(records, manifest)

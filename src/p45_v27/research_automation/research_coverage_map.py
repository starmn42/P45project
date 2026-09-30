"""Research Coverage Map generator for P45 RESEARCH DISCOVERY AGENT V1.

Inspects authoritative registry snapshots, master index, active experiments,
and maps them against the 24 Research Ontology axes.
Outputs RESEARCH_COVERAGE_MAP.json.
"""
from __future__ import annotations

import csv
import json
import logging
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .constants import ROOT
from .research_ontology import ALL_ONTOLOGY_CONCEPTS, OntologyConcept

logger = logging.getLogger("p45.research_automation.coverage")

class CoverageStatus(str, Enum):
    TESTED = "TESTED"
    FAILED = "FAILED"
    SUPPORTED = "SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    BLOCKED = "BLOCKED"
    ACTIVE = "ACTIVE"
    PARTIALLY_TESTED = "PARTIALLY_TESTED"
    UNTESTED = "UNTESTED"

@dataclass
class AxisCoverageRecord:
    concept: str
    status: str
    associated_experiments: list[str] = field(default_factory=list)
    failed_mechanisms: list[str] = field(default_factory=list)
    active_mechanisms: list[str] = field(default_factory=list)
    untested_structural_spaces: list[str] = field(default_factory=list)
    notes: str = ""

# Authoritative known structural mapping of P45 Experiments to Ontology Concepts
EXPERIMENT_ONTOLOGY_MAPPING: dict[str, dict[str, Any]] = {
    "EXP-001": {
        "title": "숫자 동시출현 관계망",
        "concepts": [OntologyConcept.NUMBER, OntologyConcept.CROSS_ROUND_RELATION, OntologyConcept.INTERACTION],
        "verdict": "FAILED",
        "mechanism": "Unconditional simultaneous number co-occurrence clustering",
    },
    "EXP-002": {
        "title": "NO-PICK COVERAGE & QUALIFIED FALLBACK",
        "concepts": [OntologyConcept.CORE, OntologyConcept.NUMBER, OntologyConcept.ORDER_RANK],
        "verdict": "FAILED",
        "mechanism": "Number-rank fallback for official pick coverage",
    },
    "EXP-003": {
        "title": "NUMBER 1-STEP TRANSITION / ROUND TRACE",
        "concepts": [OntologyConcept.NUMBER, OntologyConcept.TRANSITION, OntologyConcept.LAG],
        "verdict": "FAILED",
        "mechanism": "1-step markovian transition on raw numbers",
    },
    "EXP-004": {
        "title": "가변 전멸구간",
        "concepts": [OntologyConcept.EXTINCTION, OntologyConcept.RANGE, OntologyConcept.OCCUPANCY],
        "verdict": "FAILED",
        "mechanism": "Variable extinction zone detection without pre-registered boundary",
    },
    "EXP-005": {
        "title": "격회 재출현",
        "concepts": [OntologyConcept.RECURRENCE, OntologyConcept.LAG, OntologyConcept.CROSS_ROUND_RELATION],
        "verdict": "FAILED",
        "mechanism": "Lag-2 number carryover recurrence",
    },
    "EXP-006": {
        "title": "같은 끝자리 회차 전이",
        "concepts": [OntologyConcept.ARITHMETIC_TRANSFORM, OntologyConcept.TRANSITION, OntologyConcept.CROSS_ROUND_RELATION],
        "verdict": "FAILED",
        "mechanism": "Modulo-10 last digit round periodicity",
    },
    "EXP-009": {
        "title": "홀수 개수 lag-1 공분산",
        "concepts": [OntologyConcept.ARITHMETIC_TRANSFORM, OntologyConcept.LAG, OntologyConcept.PERSISTENCE],
        "verdict": "FAILED",
        "mechanism": "Parity balance serial autocorrelation",
    },
    "EXP-010": {
        "title": "추첨 합계 lag-1 공분산",
        "concepts": [OntologyConcept.ARITHMETIC_TRANSFORM, OntologyConcept.RANGE, OntologyConcept.LAG],
        "verdict": "FAILED",
        "mechanism": "Sum-of-six lag-1 serial autocorrelation",
    },
    "EXP-011": {
        "title": "미러 보수 전이 (Mirror complement)",
        "concepts": [OntologyConcept.ARITHMETIC_TRANSFORM, OntologyConcept.OPPOSITE_STATE, OntologyConcept.TRANSITION],
        "verdict": "FAILED",
        "mechanism": "46-x arithmetic mirror transition",
    },
    "EXP-012": {
        "title": "개별 숫자 return-age rank",
        "concepts": [OntologyConcept.ORDER_RANK, OntologyConcept.GAP, OntologyConcept.RECOVERY],
        "verdict": "FAILED",
        "mechanism": "Return-age rank priority for selection",
    },
    "EXP-013": {
        "title": "누적 빈도 rank",
        "concepts": [OntologyConcept.ORDER_RANK, OntologyConcept.PERSISTENCE, OntologyConcept.REGIME],
        "verdict": "FAILED",
        "mechanism": "Cumulative frequency rank bias",
    },
    "EXP-014": {
        "title": "직전 BONUS→다음 MAIN",
        "concepts": [OntologyConcept.BONUS_INTERACTION, OntologyConcept.TRANSITION, OntologyConcept.RECURRENCE],
        "verdict": "FAILED",
        "mechanism": "Bonus ball lag-1 recurrence to main6",
    },
    "EXP-015": {
        "title": "BONUS 상대 순위 교환가능성",
        "concepts": [OntologyConcept.BONUS_INTERACTION, OntologyConcept.ORDER_RANK, OntologyConcept.SIMILARITY],
        "verdict": "FAILED",
        "mechanism": "Bonus relative rank exchangeability",
    },
    "EXP-016": {
        "title": "번호 라벨 이질성·지속성",
        "concepts": [OntologyConcept.NUMBER, OntologyConcept.PERSISTENCE, OntologyConcept.REGIME],
        "verdict": "FAILED",
        "mechanism": "Ball physical label persistent heterogeneity",
    },
    "EXP-017": {
        "title": "TRIO ORBIT CONSENSUS NUMBER EFFECT V1",
        "concepts": [OntologyConcept.TRIO, OntologyConcept.INTERACTION, OntologyConcept.NUMBER],
        "verdict": "FAILED",
        "mechanism": "Consensus overlap number enhancement",
    },
    "EXP-018": {
        "title": "RESIDUAL NEIGHBOR CLOSURE LAB",
        "concepts": [OntologyConcept.SPACING, OntologyConcept.GAP, OntologyConcept.NUMBER],
        "verdict": "FAILED",
        "mechanism": "Adjacency / residual neighbor distance effect",
    },
    "EXP-019": {
        "title": "SALES-ADJUSTED BIRTHDAY-RANGE CROWD EFFECT V1",
        "concepts": [OntologyConcept.RANGE, OntologyConcept.REGIME, OntologyConcept.NUMBER],
        "verdict": "FAILED",
        "mechanism": "Sales volume / crowd birthday number bias",
    },
    "EXP-020": {
        "title": "LAGGED WINNER-COUNT REGIME NEXT-DRAW NUMBER SIGNAL V1",
        "concepts": [OntologyConcept.REGIME, OntologyConcept.LAG, OntologyConcept.TRANSITION],
        "verdict": "FAILED",
        "mechanism": "Lagged winner count regime indicator",
    },
    "TRIO-ORBIT-PROSPECTIVE": {
        "title": "TRIO ORBIT FIXED & LINKED PROSPECTIVE",
        "concepts": [OntologyConcept.TRIO, OntologyConcept.RECURRENCE, OntologyConcept.TRANSITION],
        "verdict": "ACTIVE",
        "mechanism": "Prospective 3-Trio coverage tracking (Fixed vs Linked)",
    },
}

class ResearchCoverageMapBuilder:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.coverage_dir = self.root / "v27_storage" / "research_automation" / "coverage"

    def build_coverage_map(self) -> dict[str, Any]:
        """Reads registry and master artifacts, categorizes all 24 axes, and saves JSON."""
        self.coverage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize map for all 24 concepts
        axis_records: dict[str, AxisCoverageRecord] = {}
        for concept in ALL_ONTOLOGY_CONCEPTS:
            axis_records[concept.value] = AxisCoverageRecord(
                concept=concept.value,
                status=CoverageStatus.UNTESTED.value,
            )

        # Map known experiments
        for exp_id, meta in EXPERIMENT_ONTOLOGY_MAPPING.items():
            verdict = meta["verdict"]
            mech = meta["mechanism"]
            for concept in meta["concepts"]:
                rec = axis_records[concept.value]
                if exp_id not in rec.associated_experiments:
                    rec.associated_experiments.append(exp_id)
                if verdict in ("FAILED", "FAILED_EARLY", "FAILED_NOT_SUPPORTED", "AXIS_CLOSED"):
                    if mech not in rec.failed_mechanisms:
                        rec.failed_mechanisms.append(mech)
                elif verdict == "ACTIVE":
                    if mech not in rec.active_mechanisms:
                        rec.active_mechanisms.append(mech)

        # Categorize status of each axis
        for concept_str, rec in axis_records.items():
            if rec.active_mechanisms:
                rec.status = CoverageStatus.ACTIVE.value
            elif rec.failed_mechanisms:
                # If tested and failed, check if partially tested or failed
                if len(rec.associated_experiments) >= 3:
                    rec.status = CoverageStatus.FAILED.value
                else:
                    rec.status = CoverageStatus.PARTIALLY_TESTED.value
            elif rec.associated_experiments:
                rec.status = CoverageStatus.TESTED.value
            else:
                rec.status = CoverageStatus.UNTESTED.value

        # Identify structural gaps for each axis
        self._annotate_structural_gaps(axis_records)

        coverage_data = {
            "version": "1.0",
            "total_concepts": len(ALL_ONTOLOGY_CONCEPTS),
            "status_summary": {
                status.value: sum(1 for r in axis_records.values() if r.status == status.value)
                for status in CoverageStatus
            },
            "axes": {k: asdict(v) for k, v in axis_records.items()},
        }

        output_file = self.coverage_dir / "RESEARCH_COVERAGE_MAP.json"
        output_file.write_text(json.dumps(coverage_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        logger.info(f"Built Research Coverage Map with {len(axis_records)} axes -> {output_file}")
        return coverage_data

    def _annotate_structural_gaps(self, records: dict[str, AxisCoverageRecord]) -> None:
        """Annotates explicitly defined untested structural spaces for each axis."""
        # Pair lifecycle dynamics
        records[OntologyConcept.PAIR.value].untested_structural_spaces.append(
            "Conditional transition of pair lifecycle states without parameter mutation"
        )
        # Extinction & Recovery
        records[OntologyConcept.EXTINCTION.value].untested_structural_spaces.append(
            "Negative space: behavior of remaining partition zones when a major partition undergoes zero-occupancy extinction"
        )
        records[OntologyConcept.RECOVERY.value].untested_structural_spaces.append(
            "Recovery velocity invariance: testing if recovery time follows memoryless geometric null"
        )
        # Decay & Persistence
        records[OntologyConcept.DECAY.value].untested_structural_spaces.append(
            "Multi-round structural decay: hazard of non-appearance over 3..7 rounds"
        )
        records[OntologyConcept.PERSISTENCE.value].untested_structural_spaces.append(
            "Negative space persistence: persistent non-occupancy duration in fixed 5-zone partition"
        )
        # Interaction & Conditional transition
        records[OntologyConcept.CONDITIONAL_TRANSITION.value].untested_structural_spaces.append(
            "Cross-structure interaction: pair state transition conditional on partition extinction"
        )
        records[OntologyConcept.OPPOSITE_STATE.value].untested_structural_spaces.append(
            "Repulsion / negative-space dispersion as opposite hypothesis to failed co-occurrence clustering"
        )

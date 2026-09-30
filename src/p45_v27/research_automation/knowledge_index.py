"""Research Knowledge Index for P45 RESEARCH DISCOVERY AGENT V1.1.

Dynamically parses and indexes all known research items in P45:
- 69 Formal Registry Experiments (DRAW 54, CROWD 9, PRIZE_SHARE 6)
- Non-EXP executed research axes (TRIO ORBIT prospective, etc.)
- Official internal core research axes (NUMBER, TRIO, PAIR, CORE, UNIT partitions)

Normalizes all records with structural fields:
inputs, transformation, condition, target, lag, metrics, null, ontology_tags, verdict, evidence_paths.
Saves to v27_storage/research_automation/knowledge/RESEARCH_KNOWLEDGE_INDEX.json.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .constants import ROOT
from .research_ontology import OntologyConcept

logger = logging.getLogger("p45.research_automation.knowledge_index")

@dataclass
class ResearchKnowledgeRecord:
    research_id: str
    canonical_name: str
    source_class: str  # "FORMAL_REGISTRY", "NON_EXP_EXECUTED", "OFFICIAL_INTERNAL"
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
    evidence_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResearchKnowledgeRecord:
        return cls(**data)

# Semantic attribute enrichment for formal registry items based on lab and registry details
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
    "TRANSITION LAB": {
        "inputs": "Winning numbers from round t-1",
        "transformation": "1-step Markov transition matrix or modulo arithmetic",
        "condition": "Consecutive round transitions (t-1 -> t)",
        "target": "Next draw winning numbers",
        "lag": 1,
        "metrics": ["transition_probability", "empirical_lift"],
        "null": "Uniform independent transitions across 45 states",
        "ontology_tags": [OntologyConcept.NUMBER.value, OntologyConcept.TRANSITION.value, OntologyConcept.LAG.value],
    },
    "STRUCTURE LAB": {
        "inputs": "Partition zones and deciles (e.g. 5 zones of 9 numbers, variable zones)",
        "transformation": "Zero-occupancy extinction tracking and return velocity",
        "condition": "Extinction event (0 balls in zone) or deficiency",
        "target": "Next-round zone rebound or recovery duration",
        "lag": 1,
        "metrics": ["recovery_rounds", "zone_occupancy_excess_z"],
        "null": "Binomial/hypergeometric memoryless zone occupancy",
        "ontology_tags": [OntologyConcept.EXTINCTION.value, OntologyConcept.RECOVERY.value, OntologyConcept.OCCUPANCY.value, OntologyConcept.RANGE.value],
    },
    "SIMILAR ROUND LAB": {
        "inputs": "Full draw outcome vectors across historical rounds",
        "transformation": "Multivariate set distance / twin round vector matching",
        "condition": "Historical round with high similarity score to current draw",
        "target": "Next-round carryover following similar round",
        "lag": 1,
        "metrics": ["set_intersection_size", "twin_similarity_score"],
        "null": "Permutation null of draw order",
        "ontology_tags": [OntologyConcept.SIMILARITY.value, OntologyConcept.CROSS_ROUND_RELATION.value, OntologyConcept.TRANSITION.value],
    },
    "SPACING LAB": {
        "inputs": "Sorted winning numbers x1 < x2 < ... < x6",
        "transformation": "Adjacent ball differences (x_{i+1} - x_i) and spacing dispersion",
        "condition": "Within-round spacing distribution or arithmetic progression",
        "target": "Spacing vector and dispersion variance",
        "lag": 0,
        "metrics": ["spacing_variance", "adjacent_gap_vector", "minimum_spacing"],
        "null": "Uniform order statistics spacing distribution on {1..45}",
        "ontology_tags": [OntologyConcept.SPACING.value, OntologyConcept.GAP.value, OntologyConcept.NUMBER.value],
    },
    "SERIAL COMPOSITION LAB": {
        "inputs": "Summary statistics of winning draws (odd count, sum of six)",
        "transformation": "Time-series lag-1 covariance and autocorrelation",
        "condition": "Serial consecutive draws",
        "target": "Next draw macro property (parity, sum)",
        "lag": 1,
        "metrics": ["autocorrelation_rho", "lag1_covariance"],
        "null": "Zero serial autocorrelation under independent Bernoulli/hypergeometric draws",
        "ontology_tags": [OntologyConcept.ARITHMETIC_TRANSFORM.value, OntologyConcept.LAG.value, OntologyConcept.PERSISTENCE.value],
    },
    "RETURN LAB": {
        "inputs": "Number appearance history",
        "transformation": "Return-age rank (rounds since last appearance)",
        "condition": "Ranking by dormancy duration",
        "target": "Next draw selection priority",
        "lag": 1,
        "metrics": ["rank_correlation", "hit_rate_by_rank"],
        "null": "Geometric distribution of return ages",
        "ontology_tags": [OntologyConcept.ORDER_RANK.value, OntologyConcept.GAP.value, OntologyConcept.RECOVERY.value],
    },
    "FREQUENCY LAB": {
        "inputs": "Cumulative historical draw frequencies",
        "transformation": "Frequency rank sorting",
        "condition": "Historical hot/cold accumulation",
        "target": "Next draw selection priority",
        "lag": 1,
        "metrics": ["frequency_rank_hit_rate"],
        "null": "Multinomial equal frequency null",
        "ontology_tags": [OntologyConcept.ORDER_RANK.value, OntologyConcept.PERSISTENCE.value, OntologyConcept.REGIME.value],
    },
    "BONUS TRANSITION LAB": {
        "inputs": "Bonus ball (7th ball) from round t-1",
        "transformation": "Migration indicator from bonus to main6",
        "condition": "Prior round bonus ball",
        "target": "Next draw main6 appearance",
        "lag": 1,
        "metrics": ["bonus_to_main_recurrence_rate"],
        "null": "Fair lottery recurrence probability 6/45 ≈ 13.33%",
        "ontology_tags": [OntologyConcept.BONUS_INTERACTION.value, OntologyConcept.TRANSITION.value, OntologyConcept.RECURRENCE.value],
    },
    "BONUS ROLE LAB": {
        "inputs": "Bonus ball vs main 6 balls",
        "transformation": "Relative size rank exchangeability",
        "condition": "Bonus relative position in sorted draw",
        "target": "Rank distribution uniformity",
        "lag": 0,
        "metrics": ["rank_uniformity_chi2"],
        "null": "Discrete uniform distribution on {1..7}",
        "ontology_tags": [OntologyConcept.BONUS_INTERACTION.value, OntologyConcept.ORDER_RANK.value, OntologyConcept.SIMILARITY.value],
    },
    "MARGINAL LABEL LAB": {
        "inputs": "Physical ball labels 1..45",
        "transformation": "Long-term label heterogeneity test",
        "condition": "Complete official draw history",
        "target": "Ball physical drawing bias",
        "lag": 0,
        "metrics": ["goodness_of_fit_chi2"],
        "null": "Uniform multinomial probability p = 1/45 for all balls",
        "ontology_tags": [OntologyConcept.NUMBER.value, OntologyConcept.PERSISTENCE.value, OntologyConcept.REGIME.value],
    },
    "PAIR OFFICIAL CHANGE CONTROL": {
        "inputs": "990 ball pair combinations in official engine",
        "transformation": "Pair shadow lifecycle status tracking (active vs dormant)",
        "condition": "Official engine shadow execution audit",
        "target": "Shadow lifecycle accuracy without official parameter change",
        "lag": 1,
        "metrics": ["shadow_pair_audit_match"],
        "null": "Official invariant rules preserved",
        "ontology_tags": [OntologyConcept.PAIR.value, OntologyConcept.CORE.value, OntologyConcept.TRANSITION.value],
    },
    "TRIO ORBIT CONSENSUS NUMBER LAB": {
        "inputs": "TRIO orbit sets A, B, C",
        "transformation": "Consensus number overlap across orbits",
        "condition": "Numbers appearing in multiple orbit trios",
        "target": "Consensus number next-draw hit rate",
        "lag": 1,
        "metrics": ["consensus_hit_rate_lift"],
        "null": "Exact combinatorial null of orbit overlapping",
        "ontology_tags": [OntologyConcept.TRIO.value, OntologyConcept.INTERACTION.value, OntologyConcept.NUMBER.value],
    },
    "RESIDUAL NEIGHBOR CLOSURE LAB": {
        "inputs": "Winning numbers and numerical neighbors (x +- 1)",
        "transformation": "Residual neighbor adjacency distance and boundary closure",
        "condition": "Winning numbers in round t-1",
        "target": "Adjacency attraction into round t",
        "lag": 1,
        "metrics": ["neighbor_hit_rate", "bootstrap_percentile_u95"],
        "null": "Combinatorial null of neighbor ball selection",
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

class ResearchKnowledgeIndex:
    """In-memory searchable index of all historical and active research items."""

    def __init__(self, records: list[ResearchKnowledgeRecord]):
        self.records = records
        self._by_id = {r.research_id: r for r in records}

    def get_by_id(self, research_id: str) -> ResearchKnowledgeRecord | None:
        return self._by_id.get(research_id)

    def list_all(self) -> list[ResearchKnowledgeRecord]:
        return list(self.records)

    def count(self) -> int:
        return len(self.records)

    def filter_by_class(self, source_class: str) -> list[ResearchKnowledgeRecord]:
        return [r for r in self.records if r.source_class == source_class]

    def filter_by_status(self, status: str) -> list[ResearchKnowledgeRecord]:
        return [r for r in self.records if r.status == status]

class ResearchKnowledgeIndexBuilder:
    """Constructs the canonical RESEARCH_KNOWLEDGE_INDEX.json from authoritative local files."""

    def __init__(self, root: Path = ROOT):
        self.root = root
        self.knowledge_dir = self.root / "v27_storage" / "research_automation" / "knowledge"

    def build_index(self) -> ResearchKnowledgeIndex:
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        records: list[ResearchKnowledgeRecord] = []

        # 1. Parse 69 Formal Registry Rows from 06_INITIAL_EXPERIMENT_REGISTRY.md
        registry_path = self.root / "00_P45_STATE" / "experiment_lab" / "06_INITIAL_EXPERIMENT_REGISTRY.md"
        if registry_path.exists():
            content = registry_path.read_text(encoding="utf-8")
            rows = re.findall(
                r'\|(EXP-[A-Z]+-\d+-\d+-V\d+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|',
                content,
            )
            for r in rows:
                eid = r[0].strip()
                lab = r[1].strip()
                domain = r[2].strip()
                name = r[3].strip()
                source_status = r[4].strip()
                status = r[5].strip()
                official_effect = r[6].strip()
                promo = r[7].strip()

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

                # Determine verdict from status
                verdict = status
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

                record = ResearchKnowledgeRecord(
                    research_id=eid,
                    canonical_name=name,
                    source_class="FORMAL_REGISTRY",
                    status=status,
                    inputs=meta["inputs"],
                    transformation=meta["transformation"],
                    condition=meta["condition"],
                    target=meta["target"],
                    lag=meta["lag"],
                    metrics=list(meta["metrics"]),
                    null=meta["null"],
                    ontology_tags=list(meta["ontology_tags"]),
                    verdict=verdict,
                    evidence_paths=[str(registry_path)],
                )
                records.append(record)

        # 2. Add Non-EXP Executed Research Axes
        records.append(
            ResearchKnowledgeRecord(
                research_id="NON-EXP-TRIO-ORBIT-FIXED",
                canonical_name="TRIO ORBIT Pure Fixed Prospective Tracking (1239..1243)",
                source_class="NON_EXP_EXECUTED",
                status="ACTIVE",
                inputs="Fixed 3-TRIO candidate sets (9 numbers)",
                transformation="Direct set matching against drawn main6 balls",
                condition="Fixed invariant trios without anchor replacement",
                target="PRIMARY (3/3) and SUPPORT (exact 2/3) hits",
                lag=1,
                metrics=["support_hit_rate", "exact_binomial_p", "wilson_ci"],
                null="Binomial exact null p0 = 987,390 / 8,145,060 ≈ 0.121226",
                ontology_tags=[OntologyConcept.TRIO.value, OntologyConcept.RECURRENCE.value],
                verdict="SMALL_SAMPLE_INCONCLUSIVE",
                evidence_paths=["v27_storage/audits/trio_orbit_prospective_retrospective_001/"],
            )
        )
        records.append(
            ResearchKnowledgeRecord(
                research_id="NON-EXP-TRIO-ORBIT-LINKED",
                canonical_name="TRIO ORBIT Linked Previous Draw Tracking (1239..1243)",
                source_class="NON_EXP_EXECUTED",
                status="ACTIVE",
                inputs="Linked 3-TRIO candidate sets using 3 winning numbers from round t-1 as anchor",
                transformation="Anchor carryover and orbit rotation",
                condition="Target draw t conditioned on winning balls of t-1",
                target="PRIMARY (3/3) and SUPPORT (exact 2/3) hits",
                lag=1,
                metrics=["support_hit_rate", "mcnemar_exact_p", "holm_adj_p"],
                null="Binomial exact null p0 = 987,390 / 8,145,060 ≈ 0.121226",
                ontology_tags=[OntologyConcept.TRIO.value, OntologyConcept.RECURRENCE.value, OntologyConcept.TRANSITION.value],
                verdict="NO_EVIDENCE_OF_LINKED_SUPERIORITY",
                evidence_paths=["v27_storage/audits/trio_orbit_prospective_retrospective_001/"],
            )
        )
        records.append(
            ResearchKnowledgeRecord(
                research_id="NON-EXP-WHOLE-ENGINE-SYNTHETIC-REPLAY",
                canonical_name="Whole Engine Synthetic Replay Semantics Recovery Audit 001",
                source_class="NON_EXP_EXECUTED",
                status="COMPLETED",
                inputs="Full synthetic draw replay through official core pipeline",
                transformation="Whole pipeline replay without outcome peeking",
                condition="Simulated lottery distributions",
                target="Semantic recovery and pipeline integrity",
                lag=0,
                metrics=["semantic_fidelity_score", "invariant_check_pass"],
                null="Synthetic permutation baseline",
                ontology_tags=[OntologyConcept.CORE.value, OntologyConcept.REGIME.value],
                verdict="SUPPORTED",
                evidence_paths=["v27_storage/audits/whole_engine_synthetic_replay_semantics_recovery_001/"],
            )
        )

        # 3. Add Official Internal Research Axes
        records.append(
            ResearchKnowledgeRecord(
                research_id="OFFICIAL-NUMBER-14KEY",
                canonical_name="P45 Official NUMBER 14-Key Deterministic Sorting Rule",
                source_class="OFFICIAL_INTERNAL",
                status="OFFICIAL_FROZEN",
                inputs="Historical lottery draw statistics for individual numbers 1..45",
                transformation="14-key lexicographical sort without arbitrary weights",
                condition="Official frozen gate rules",
                target="Official number priority ranking",
                lag=1,
                metrics=["official_selection_stability"],
                null="Deterministic tie-breaking baseline",
                ontology_tags=[OntologyConcept.NUMBER.value, OntologyConcept.ORDER_RANK.value, OntologyConcept.CORE.value],
                verdict="OFFICIAL_FROZEN",
                evidence_paths=["src/p45_v27/"],
            )
        )
        records.append(
            ResearchKnowledgeRecord(
                research_id="OFFICIAL-TRIO-15KEY",
                canonical_name="P45 Official TRIO 15-Key Deterministic Sorting Rule",
                source_class="OFFICIAL_INTERNAL",
                status="OFFICIAL_FROZEN",
                inputs="All 14,190 three-number subsets",
                transformation="15-key lexicographical sort without arbitrary weights",
                condition="Official frozen gate rules",
                target="Official trio priority ranking",
                lag=1,
                metrics=["official_trio_stability"],
                null="Deterministic tie-breaking baseline",
                ontology_tags=[OntologyConcept.TRIO.value, OntologyConcept.ORDER_RANK.value, OntologyConcept.CORE.value],
                verdict="OFFICIAL_FROZEN",
                evidence_paths=["src/p45_v27/"],
            )
        )
        records.append(
            ResearchKnowledgeRecord(
                research_id="OFFICIAL-PAIR-LIFECYCLE",
                canonical_name="P45 Official PAIR Shadow Lifecycle System",
                source_class="OFFICIAL_INTERNAL",
                status="OFFICIAL_FROZEN",
                inputs="990 ball pairs across all draws",
                transformation="Shadow lifecycle state tracking (Active vs Dormant)",
                condition="Official engine change control audit DECISION-20260824-095",
                target="Internal shadow validation and state integrity",
                lag=1,
                metrics=["pair_state_integrity"],
                null="Official shadow state preservation",
                ontology_tags=[OntologyConcept.PAIR.value, OntologyConcept.CORE.value, OntologyConcept.TRANSITION.value],
                verdict="OFFICIAL_FROZEN",
                evidence_paths=["src/p45_v27/"],
            )
        )
        records.append(
            ResearchKnowledgeRecord(
                research_id="OFFICIAL-CORE-INVARIANTS",
                canonical_name="P45 Official Core Engine Invariant Rules (NO-PICK 867/867)",
                source_class="OFFICIAL_INTERNAL",
                status="OFFICIAL_FROZEN",
                inputs="Historical backtest coverage windows 43..1235",
                transformation="Strict non-mutation of frozen gates and signatures",
                condition="Zero-coverage invariant preservation",
                target="Official engine safety and reproducibility",
                lag=0,
                metrics=["invariant_violation_count"],
                null="Engine frozen state",
                ontology_tags=[OntologyConcept.CORE.value],
                verdict="OFFICIAL_FROZEN",
                evidence_paths=["src/p45_v27/"],
            )
        )
        records.append(
            ResearchKnowledgeRecord(
                research_id="OFFICIAL-UNIT-PARTITIONS",
                canonical_name="P45 Official UNIT Partitions (UNIT_3, UNIT_5, UNIT_9, UNIT_10)",
                source_class="OFFICIAL_INTERNAL",
                status="OFFICIAL_FROZEN",
                inputs="Lottery balls 1..45 partitioned into equal or structured subsets",
                transformation="Fixed partition grouping for internal representation",
                condition="Fixed partition boundaries without variable threshold hunting",
                target="Internal representation buckets",
                lag=0,
                metrics=["partition_balance"],
                null="Hypergeometric partition null",
                ontology_tags=[OntologyConcept.RANGE.value, OntologyConcept.OCCUPANCY.value, OntologyConcept.CORE.value],
                verdict="OFFICIAL_FROZEN",
                evidence_paths=["src/p45_v27/"],
            )
        )

        output_file = self.knowledge_dir / "RESEARCH_KNOWLEDGE_INDEX.json"
        data = {
            "version": "1.1",
            "total_records": len(records),
            "counts_by_source_class": {
                "FORMAL_REGISTRY": sum(1 for r in records if r.source_class == "FORMAL_REGISTRY"),
                "NON_EXP_EXECUTED": sum(1 for r in records if r.source_class == "NON_EXP_EXECUTED"),
                "OFFICIAL_INTERNAL": sum(1 for r in records if r.source_class == "OFFICIAL_INTERNAL"),
            },
            "records": [r.to_dict() for r in records],
        }
        output_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        logger.info(f"Built Research Knowledge Index with {len(records)} records -> {output_file}")
        return ResearchKnowledgeIndex(records)

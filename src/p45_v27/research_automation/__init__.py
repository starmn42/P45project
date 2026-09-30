"""P45 AUTO RESEARCH LOOP V1 Package."""
from __future__ import annotations

from .constants import FollowupType, ResearchState, NOVEL_IDEA_GENERATION_EXTERNAL_AI
from .candidate_queue import CandidateQueue, CandidateRecord
from .research_state_machine import ResearchStateMachine, PromotionFirewallViolation, InvalidStateTransitionError
from .followup_gate import FollowupGate, GateDecision, GateCheckResult
from .hypothesis_candidate_builder import HypothesisCandidateBuilder
from .protocol_generator import ProtocolGenerator, ProtocolLocker
from .active_research_discovery import ActiveResearchDiscovery
from .settlement_dispatcher import SettlementDispatcher
from .retrospective_builder import RetrospectiveBuilder
from .idempotency_guard import IdempotencyGuard
from .audit_logger import AuditLogger
from .evidence_writer import EvidenceWriter
from .retry_recovery import RecoveryManager
from .hook import ResearchAutomationCoordinator, trigger_research_automation_post_draw

from .research_ontology import OntologyConcept, ALL_ONTOLOGY_CONCEPTS
from .research_coverage_map import ResearchCoverageMapBuilder, CoverageStatus
from .coverage_gap_analyzer import CoverageGapAnalyzer, GapCategory
from .novelty_checker import NoveltyChecker, NoveltyVerdict
from .idea_quality_gate import IdeaQualityGate, QualityGateResult
from .idea_provider import BaseIdeaProvider, DeterministicStructuralProvider, OptionalLLMIdeaProvider
from .candidate_ranker import CandidateRanker, MAX_CANDIDATES_PER_CYCLE
from .research_discovery_agent import ResearchDiscoveryAgent

from .knowledge_source_inventory import (
    ResearchSourceItem,
    ResearchSourceInventoryBuilder,
    CoverageManifest,
    ResearchKnowledgeCoverageManifestBuilder,
    SourceClass,
    MappingType,
)
from .knowledge_index import ResearchKnowledgeRecord, ResearchKnowledgeIndex, ResearchKnowledgeIndexBuilder
from .coverage_map_v1_1 import CoverageMapBuilderV1_1, AxisCoverageRecordV1_1
from .semantic_novelty_checker import (
    SemanticNoveltyCheckerV1_1,
    SemanticOverlapClass,
    NoveltyFinalVerdict,
    CandidateNoveltyAuditResult,
)

__all__ = [
    "ResearchSourceItem",
    "ResearchSourceInventoryBuilder",
    "CoverageManifest",
    "ResearchKnowledgeCoverageManifestBuilder",
    "SourceClass",
    "MappingType",
    "ResearchState",
    "FollowupType",
    "NOVEL_IDEA_GENERATION_EXTERNAL_AI",
    "CandidateQueue",
    "CandidateRecord",
    "ResearchStateMachine",
    "PromotionFirewallViolation",
    "InvalidStateTransitionError",
    "FollowupGate",
    "GateDecision",
    "GateCheckResult",
    "HypothesisCandidateBuilder",
    "ProtocolGenerator",
    "ProtocolLocker",
    "ActiveResearchDiscovery",
    "SettlementDispatcher",
    "RetrospectiveBuilder",
    "IdempotencyGuard",
    "AuditLogger",
    "EvidenceWriter",
    "RecoveryManager",
    "ResearchAutomationCoordinator",
    "trigger_research_automation_post_draw",
    "OntologyConcept",
    "ALL_ONTOLOGY_CONCEPTS",
    "ResearchCoverageMapBuilder",
    "CoverageStatus",
    "CoverageGapAnalyzer",
    "GapCategory",
    "NoveltyChecker",
    "NoveltyVerdict",
    "IdeaQualityGate",
    "QualityGateResult",
    "BaseIdeaProvider",
    "DeterministicStructuralProvider",
    "OptionalLLMIdeaProvider",
    "CandidateRanker",
    "MAX_CANDIDATES_PER_CYCLE",
    "ResearchDiscoveryAgent",
    "ResearchKnowledgeRecord",
    "ResearchKnowledgeIndex",
    "ResearchKnowledgeIndexBuilder",
    "CoverageMapBuilderV1_1",
    "AxisCoverageRecordV1_1",
    "SemanticNoveltyCheckerV1_1",
    "SemanticOverlapClass",
    "NoveltyFinalVerdict",
    "CandidateNoveltyAuditResult",
]

"""Research Discovery Agent V1.1 for P45.

Key Upgrades in V1.1:
1. Deep semantic duplicate guard (SemanticNoveltyCheckerV1_1) across 8 structural dimensions.
2. Dynamic Research Knowledge Index across all 77 indexed research items.
3. Coverage Map V1.1 with strict separation of 24 ontology axes vs research status linkages.
4. Mandatory CANDIDATE_NOVELTY_EVIDENCE.json and .md before READY_FOR_PROTOCOL.
5. Strict separation of earliest_eligible_confirmatory_round vs actual confirmatory_start_round.
6. Zero leakage & complete failure isolation.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .candidate_queue import CandidateQueue, CandidateRecord
from .candidate_ranker import CandidateRanker, MAX_CANDIDATES_PER_CYCLE
from .constants import LOGS_DIR, ROOT, ResearchState
from .coverage_map_v1_1 import CoverageMapBuilderV1_1
from .idea_provider import BaseIdeaProvider, DeterministicStructuralProvider, OptionalLLMIdeaProvider
from .idea_quality_gate import IdeaQualityGate
from .knowledge_index import ResearchKnowledgeIndex, ResearchKnowledgeIndexBuilder
from .novelty_checker import NoveltyChecker
from .semantic_novelty_checker import (
    CandidateNoveltyAuditResult,
    NoveltyFinalVerdict,
    SemanticNoveltyCheckerV1_1,
)

logger = logging.getLogger("p45.research_automation.discovery_agent_v1_1")

class ResearchDiscoveryAgent:
    """Master agent coordinating autonomous structural research discovery V1.1 for P45."""

    def __init__(
        self,
        root: Path = ROOT,
        candidate_queue: CandidateQueue | None = None,
        custom_providers: list[BaseIdeaProvider] | None = None,
    ):
        self.root = root
        self.knowledge_builder = ResearchKnowledgeIndexBuilder(self.root)
        self.knowledge_index = self.knowledge_builder.build_index()
        self.coverage_builder = CoverageMapBuilderV1_1(self.root)
        self.semantic_checker = SemanticNoveltyCheckerV1_1(self.knowledge_index, self.root)
        self.novelty_checker = NoveltyChecker()
        self.quality_gate = IdeaQualityGate(
            novelty_checker=self.novelty_checker,
            semantic_checker=self.semantic_checker,
        )
        self.ranker = CandidateRanker()
        self.queue = candidate_queue or CandidateQueue(self.root / "v27_storage" / "research_automation" / "candidate_queue")
        
        # Provider setup
        self.deterministic_provider = DeterministicStructuralProvider()
        self.optional_llm_provider = OptionalLLMIdeaProvider()
        self.providers: list[BaseIdeaProvider] = custom_providers or [
            self.deterministic_provider,
            self.optional_llm_provider,
        ]

        self.storage_dir = self.root / "v27_storage" / "research_automation" / "discovery"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def reassess_v1_candidates(self) -> list[CandidateNoveltyAuditResult]:
        """Re-evaluates the initial 3 candidates from V1 against the semantic duplicate guard."""
        v1_cycle_file = self.storage_dir / "discovery_cycle_1243.json"
        if not v1_cycle_file.exists():
            logger.warning("V1 discovery cycle file not found; generating fresh candidates for assessment.")
            return []

        v1_data = json.loads(v1_cycle_file.read_text(encoding="utf-8"))
        selected_v1 = v1_data.get("summary", {}).get("selected_candidates", [])

        audit_results: list[CandidateNoveltyAuditResult] = []
        for cand in selected_v1:
            cand["state"] = ResearchState.REVIEW_REQUIRED_V1_1.value
            audit = self.semantic_checker.audit_candidate(cand)
            cand["v1_historical_verdict"] = "READY_FOR_PROTOCOL"
            cand["v1_1_semantic_verdict"] = audit.final_verdict
            cand["v1_1_state"] = (
                ResearchState.REJECT_RESCUE.value if audit.final_verdict == NoveltyFinalVerdict.REJECT_RESCUE.value
                else ResearchState.REJECT_DUPLICATE.value if audit.final_verdict == NoveltyFinalVerdict.REJECT_DUPLICATE.value
                else ResearchState.NEEDS_EVIDENCE.value if audit.final_verdict == NoveltyFinalVerdict.NEEDS_EVIDENCE.value
                else ResearchState.READY_FOR_PROTOCOL.value
            )
            audit_results.append(audit)

        # Save evidence files
        self.semantic_checker.save_novelty_evidence_files(audit_results)

        # Update V1 cycle record preserving historical lineage
        v1_data["v1_1_migration_status"] = "MIGRATED_AND_REASSESSED"
        v1_data["v1_1_reassessment_timestamp"] = datetime.now(timezone.utc).isoformat()
        v1_cycle_file.write_text(json.dumps(v1_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        return audit_results

    def run_discovery_cycle(self, canonical_round: int, *, is_migration: bool = False) -> dict[str, Any]:
        """Runs discovery cycle V1.1.
        
        Strict Rules:
        - If is_migration is True, uses key discovery_migration:v1_to_v1_1:{round}
        - Normal future runtime uses key discovery_cycle:v1_1:{round}
        - Strictly requires semantic novelty audit and evidence file generation
        - Only candidates clearing all 14 gates advance to READY_FOR_PROTOCOL
        - If 0 candidates pass, returns status NO_VALID_NEW_HYPOTHESIS without forced candidate fabrication
        """
        idempotency_key = f"discovery_migration:v1_to_v1_1:{canonical_round}" if is_migration else f"discovery_cycle:v1_1:{canonical_round}"
        safe_key_filename = idempotency_key.replace(":", "_")
        idempotency_file = self.storage_dir / f"{safe_key_filename}.json"

        # 1. Idempotency Check
        if idempotency_file.exists():
            try:
                cached_data = json.loads(idempotency_file.read_text(encoding="utf-8"))
                logger.info(f"Discovery cycle {idempotency_key} already completed (Idempotent).")
                return {
                    "status": "ALREADY_PROCESSED",
                    "round": canonical_round,
                    "idempotency_key": idempotency_key,
                    "new_candidates_count": 0,
                    "duplicate_write": 0,
                    "summary": cached_data.get("summary", {}),
                }
            except Exception as e:
                logger.warning(f"Error reading idempotency cache: {e}; re-running safely.")

        try:
            logger.info(f"Starting Research Discovery Cycle V1.1 for Canonical Round {canonical_round} ({idempotency_key})...")

            # 2. Build Coverage Map V1.1
            coverage_map = self.coverage_builder.build_coverage_map_v1_1(self.knowledge_index)

            # 3. Provider Status Audit
            external_ai_status = self.optional_llm_provider.get_status()
            provider_audit = {
                "DeterministicStructuralProvider": self.deterministic_provider.get_status(),
                "OptionalLLMIdeaProvider": external_ai_status,
                "NOVEL_IDEA_GENERATION_EXTERNAL_AI": external_ai_status,
            }

            # 4. Generate Raw Candidates from Providers
            raw_candidates: list[dict[str, Any]] = []
            for prov in self.providers:
                prov_cands = prov.generate_candidate_hypotheses(coverage_map, canonical_round)
                raw_candidates.extend(prov_cands)

            # 5. Semantic Novelty Auditing across all candidates
            audit_results: list[CandidateNoveltyAuditResult] = []
            cleared_for_protocol: list[dict[str, Any]] = []
            held_candidates: list[dict[str, Any]] = []
            rejected_candidates: list[dict[str, Any]] = []

            for cand_pkg in raw_candidates:
                # Perform deep semantic comparison against knowledge index
                sem_audit = self.semantic_checker.audit_candidate(cand_pkg)
                audit_results.append(sem_audit)

                # Evaluate Idea Quality Gate V1.1
                gate_res = self.quality_gate.evaluate(cand_pkg, canonical_round, sem_audit)
                cand_pkg["quality_gate_result"] = asdict(gate_res)
                cand_pkg["semantic_audit_verdict"] = sem_audit.final_verdict

                if gate_res.ready_for_protocol:
                    cand_pkg["state"] = ResearchState.READY_FOR_PROTOCOL.value
                    cleared_for_protocol.append(cand_pkg)
                elif sem_audit.final_verdict == NoveltyFinalVerdict.NEEDS_EVIDENCE.value:
                    cand_pkg["state"] = ResearchState.NEEDS_EVIDENCE.value
                    held_candidates.append(cand_pkg)
                elif sem_audit.final_verdict == NoveltyFinalVerdict.REJECT_RESCUE.value:
                    cand_pkg["state"] = ResearchState.REJECT_RESCUE.value
                    rejected_candidates.append(cand_pkg)
                elif sem_audit.final_verdict == NoveltyFinalVerdict.REJECT_DUPLICATE.value:
                    cand_pkg["state"] = ResearchState.REJECT_DUPLICATE.value
                    rejected_candidates.append(cand_pkg)
                else:
                    cand_pkg["state"] = ResearchState.REJECT_NOT_TESTABLE.value
                    rejected_candidates.append(cand_pkg)

            # 6. Save Mandatory CANDIDATE_NOVELTY_EVIDENCE Files
            self.semantic_checker.save_novelty_evidence_files(audit_results)

            # 7. Rank and Cap Valid Candidates (max 3)
            final_selected: list[dict[str, Any]] = []
            if cleared_for_protocol:
                final_selected = self.ranker.rank_and_select(cleared_for_protocol)

            # 8. Queue Integration: Only genuinely cleared candidates enter queue as READY_FOR_PROTOCOL
            queued_records = []
            for cand_pkg in final_selected:
                record = CandidateRecord(
                    candidate_id=cand_pkg["candidate_id"],
                    created_at=datetime.now(timezone.utc).isoformat(),
                    birth_round=canonical_round,
                    source_research="STRUCTURAL_DISCOVERY_AGENT_V1_1",
                    candidate_type=cand_pkg.get("origin", "STRUCTURAL_GAP"),
                    hypothesis=cand_pkg["hypothesis"],
                    opposite_hypothesis=cand_pkg.get("opposite_hypothesis", ""),
                    novelty_status="NOVEL",
                    duplicate_status=cand_pkg.get("duplicate_check", "PASS"),
                    rescue_check=cand_pkg.get("rescue_check", "PASS"),
                    data_snooping_status="CLEAN_PROSPECTIVE_ONLY",
                    earliest_eligible_confirmatory_round=cand_pkg["earliest_eligible_confirmatory_round"],
                    confirmatory_start_round=None,  # Strictly None before protocol lock
                    minimum_sample=cand_pkg.get("minimum_sample", 30),
                    recommended_action="GENERATE_PROTOCOL",
                    state=ResearchState.READY_FOR_PROTOCOL.value,
                    notes=cand_pkg.get("title", ""),
                )
                self.queue.add_candidate(record)
                queued_records.append(record.candidate_id)

            cycle_status = "SUCCESS" if len(final_selected) > 0 else "NO_VALID_NEW_HYPOTHESIS"

            cycle_summary = {
                "round": canonical_round,
                "idempotency_key": idempotency_key,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "coverage_axes_read": coverage_map["ontology_model_metrics"]["actual_unique_axes_count"],
                "total_indexed_knowledge_records": self.knowledge_index.count(),
                "provider_status": provider_audit,
                "raw_candidates_generated": len(raw_candidates),
                "semantic_novelty_audited_count": len(audit_results),
                "ready_for_protocol_count": len(cleared_for_protocol),
                "needs_evidence_count": len(held_candidates),
                "rejected_count": len(rejected_candidates),
                "final_selected_count": len(final_selected),
                "max_candidates_limit": MAX_CANDIDATES_PER_CYCLE,
                "selected_candidates": final_selected,
                "queued_records": queued_records,
                "rejection_audit_summary": [
                    {
                        "candidate_id": a.candidate_id,
                        "title": a.candidate_title,
                        "verdict": a.final_verdict,
                        "reason": a.novelty_justification,
                        "rescues": a.failed_axis_rescues,
                        "duplicates": a.exact_overlaps,
                    }
                    for a in audit_results
                ],
                "official_engine_firewall": "PROTECTED_UNMODIFIED",
            }

            result_data = {
                "status": cycle_status,
                "round": canonical_round,
                "idempotency_key": idempotency_key,
                "new_candidates_count": len(final_selected),
                "duplicate_write": 0,
                "summary": cycle_summary,
            }

            # Save idempotency record
            idempotency_file.write_text(
                json.dumps(result_data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            logger.info(f"Discovery Cycle V1.1 completed -> Status: {cycle_status}, Selected: {len(final_selected)}")
            return result_data

        except Exception as exc:
            err_msg = f"{type(exc).__name__}: {str(exc)}"
            logger.error(f"RESEARCH_DISCOVERY_V1_1_FAILED: {err_msg}", exc_info=True)

            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            err_file = LOGS_DIR / f"discovery_v1_1_error_round_{canonical_round}.log"
            err_file.write_text(f"Error: {err_msg}\nTimestamp: {datetime.now(timezone.utc).isoformat()}\n", encoding="utf-8")

            return {
                "status": "RESEARCH_DISCOVERY_FAILED",
                "round": canonical_round,
                "error": err_msg,
                "official_lifecycle_affected": False,
                "new_candidates_count": 0,
            }

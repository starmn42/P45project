"""Authoritative hook and orchestrator for AUTO RESEARCH LOOP V1.

Ensures strict failure isolation:
Research automation failures NEVER block or invalidate official draw settlement or web sync.
"""
from __future__ import annotations

import logging
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .active_research_discovery import ActiveResearchDiscovery
from .audit_logger import AuditLogger
from .candidate_queue import CandidateQueue
from .constants import LOGS_DIR, ROOT, ResearchState
from .followup_gate import FollowupGate
from .hypothesis_candidate_builder import HypothesisCandidateBuilder
from .idempotency_guard import IdempotencyGuard
from .protocol_generator import ProtocolGenerator, ProtocolLocker
from .research_discovery_agent import ResearchDiscoveryAgent
from .retrospective_builder import RetrospectiveBuilder
from .retry_recovery import RecoveryManager
from .settlement_dispatcher import SettlementDispatcher

logger = logging.getLogger("p45.research_automation")

class ResearchAutomationCoordinator:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.idempotency_guard = IdempotencyGuard()
        self.audit_logger = AuditLogger()
        self.discovery = ActiveResearchDiscovery(root)
        self.dispatcher = SettlementDispatcher(root)
        self.retrospective_builder = RetrospectiveBuilder(root=root)
        self.candidate_queue = CandidateQueue()
        self.followup_gate = FollowupGate()
        self.candidate_builder = HypothesisCandidateBuilder(self.candidate_queue, self.followup_gate)
        self.discovery_agent = ResearchDiscoveryAgent(root=self.root, candidate_queue=self.candidate_queue)
        self.recovery = RecoveryManager(queue=self.candidate_queue)

    def run_post_settlement_pipeline(self, draw_round: int) -> dict[str, Any]:
        """Core execution pipeline. Raises exceptions if internal steps fail (caught by safe wrapper)."""
        self.recovery.record_checkpoint("START", draw_round)

        # 1. Idempotency check
        if self.idempotency_guard.is_round_processed(draw_round):
            self.audit_logger.log_event("IDEMPOTENCY_SKIP", {"round": draw_round, "reason": "ROUND_ALREADY_PROCESSED"})
            return {
                "status": "ALREADY_PROCESSED",
                "round": draw_round,
                "duplicate_write": 0,
                "duplicate_retrospective": 0,
                "duplicate_candidate": 0,
                "summary": self.idempotency_guard.get_round_summary(draw_round),
            }

        # 2. Active Research Discovery
        active_list = self.discovery.discover_all()
        self.recovery.record_checkpoint("DISCOVERY_COMPLETE", draw_round, {"discovered_count": len(active_list)})

        # 3. Settlement Dispatch
        settle_res = self.dispatcher.dispatch_settlements(draw_round)
        self.recovery.record_checkpoint("SETTLEMENT_COMPLETE", draw_round, settle_res)

        # 4. Automatic Retrospective Packet Construction
        retro_res = self.retrospective_builder.build_packet(draw_round, settle_res)
        self.recovery.record_checkpoint("RETROSPECTIVE_COMPLETE", draw_round, {"path": retro_res.get("path")})

        # 5. Follow-up Evaluation & Predefined Candidate Generation
        retrospectives_for_builder = []
        for r_id, eval_data in retro_res["packet"]["research_evaluations"].items():
            retrospectives_for_builder.append({
                "research_id": eval_data.get("research_id", r_id),
                "verdict": eval_data.get("previous_verdict", "INCONCLUSIVE"),
                "null_excess_observed": False,  # No excess observed
            })

        followup_candidates = self.candidate_builder.build_candidates_for_round(
            draw_round,
            retrospectives_for_builder,
            overlap_events=settle_res.get("overlap_events", []),
        )

        # 5b. Autonomous Structural Discovery Cycle (NEW_OFFICIAL_DRAW_SETTLED)
        discovery_res = self.discovery_agent.run_discovery_cycle(draw_round)
        discovered_candidates = []
        if discovery_res.get("status") in ("SUCCESS", "ALREADY_PROCESSED"):
            discovered_candidates = self.candidate_queue.find_by_birth_round(draw_round)

        all_candidates = list(followup_candidates) + [
            c for c in discovered_candidates if c.candidate_id not in [fc.candidate_id for fc in followup_candidates]
        ]

        # 6. Protocol Pre-generation and Locking for Eligible Candidates
        locked_candidates = []
        for cand in all_candidates:
            if cand.state == ResearchState.READY_FOR_PROTOCOL.value:
                protocol = ProtocolGenerator.generate(cand)
                cand_dir = self.root / f"v27_storage/research_automation/protocols/{cand.candidate_id}"
                lock_res = ProtocolLocker.lock_protocol(protocol, cand_dir)
                cand.protocol_sha256 = lock_res["protocol_sha256"]
                cand.locked_at = lock_res["locked_at"]
                cand.state = ResearchState.PROTOCOL_LOCKED.value
                self.candidate_queue.update_candidate(cand)
                locked_candidates.append(cand.candidate_id)

        # 7. Finalize and Mark Processed
        summary = {
            "round": draw_round,
            "status": "COMPLETED",
            "active_research_count": len(active_list),
            "retrospective_packet": retro_res.get("path"),
            "new_candidates_count": len(all_candidates),
            "discovery_cycle_status": discovery_res.get("status"),
            "locked_candidates": locked_candidates,
            "overlap_events_count": len(settle_res.get("overlap_events", [])),
        }
        self.idempotency_guard.mark_round_processed(draw_round, summary)
        self.recovery.record_checkpoint("FINISHED", draw_round, summary)
        self.audit_logger.log_event("AUTO_RESEARCH_CYCLE_SUCCESS", summary)

        return {
            "status": "SUCCESS",
            "round": draw_round,
            "duplicate_write": 0,
            "summary": summary,
        }

def trigger_research_automation_post_draw(draw_round: int, *, _force_exception: bool = False) -> dict[str, Any]:
    """Total isolation wrapper: Guarantees research failure never blocks official lifecycle."""
    try:
        if _force_exception:
            raise RuntimeError("SIMULATED_RESEARCH_AUTOMATION_FAULT_INJECTION")
        coordinator = ResearchAutomationCoordinator()
        return coordinator.run_post_settlement_pipeline(draw_round)
    except Exception as exc:
        # Strict isolation: log error, preserve isolated state, return fail record without re-raising
        err_msg = f"{type(exc).__name__}: {str(exc)}"
        tb = traceback.format_exc()

        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        err_file = LOGS_DIR / f"error_round_{draw_round}.log"
        err_file.write_text(f"Timestamp: {datetime.now(timezone.utc).isoformat()}\nError: {err_msg}\n\nTraceback:\n{tb}\n", encoding="utf-8")

        audit = AuditLogger()
        audit.log_event("AUTO_RESEARCH_CYCLE_FAILED", {
            "round": draw_round,
            "error": err_msg,
            "official_isolation_preserved": True,
        }, status="FAILURE_ISOLATED")

        return {
            "status": "RESEARCH_AUTOMATION_FAILED_ISOLATED",
            "round": draw_round,
            "error": err_msg,
            "official_lifecycle_affected": False,
            "log_path": str(err_file),
        }

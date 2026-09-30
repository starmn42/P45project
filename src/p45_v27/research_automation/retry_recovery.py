"""Crash recovery and resume manager for AUTO RESEARCH LOOP V1."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .candidate_queue import CandidateQueue
from .constants import STATE_DIR

class RecoveryManager:
    def __init__(self, state_dir: Path = STATE_DIR, queue: CandidateQueue | None = None):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.recovery_log = self.state_dir / "recovery.json"
        self.queue = queue or CandidateQueue()

    def check_incomplete_states(self) -> list[str]:
        """Scans candidate queue and protocols for incomplete or inconsistent states."""
        inconsistencies = []
        for cand in self.queue.list_all():
            # If state is PROTOCOL_LOCKED but protocol_sha256 is missing
            if cand.state == "PROTOCOL_LOCKED" and not cand.protocol_sha256:
                inconsistencies.append(f"Candidate {cand.candidate_id} marked PROTOCOL_LOCKED but missing protocol_sha256")
        return inconsistencies

    def record_checkpoint(self, stage: str, round_num: int, metadata: dict[str, Any] | None = None) -> None:
        payload = {
            "stage": stage,
            "round": round_num,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        self.recovery_log.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def get_last_checkpoint(self) -> dict[str, Any] | None:
        if not self.recovery_log.exists():
            return None
        try:
            return json.loads(self.recovery_log.read_text(encoding="utf-8"))
        except Exception:
            return None

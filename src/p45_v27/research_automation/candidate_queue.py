"""Candidate queue storage and query manager for AUTO RESEARCH LOOP V1."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from .constants import CANDIDATE_QUEUE_DIR, FollowupType, ResearchState

@dataclass
class CandidateRecord:
    candidate_id: str
    created_at: str
    birth_round: int
    source_research: str
    candidate_type: str
    hypothesis: str
    opposite_hypothesis: str
    novelty_status: str
    duplicate_status: str
    rescue_check: str
    data_snooping_status: str
    confirmatory_start_round: int | None = None
    earliest_eligible_confirmatory_round: int | None = None
    minimum_sample: int = 30
    recommended_action: str = "EVALUATE"
    state: str = ResearchState.IDEA_CANDIDATE.value
    protocol_sha256: str | None = None
    locked_at: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CandidateRecord:
        return cls(**data)

class CandidateQueue:
    def __init__(self, queue_dir: Path = CANDIDATE_QUEUE_DIR):
        self.queue_dir = queue_dir
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def _file_path(self, candidate_id: str) -> Path:
        safe_id = candidate_id.replace("/", "_").replace("\\", "_")
        return self.queue_dir / f"{safe_id}.json"

    def add_candidate(self, candidate: CandidateRecord) -> Path:
        path = self._file_path(candidate.candidate_id)
        if path.exists():
            raise FileExistsError(f"Candidate {candidate.candidate_id} already exists in queue.")
        path.write_text(json.dumps(candidate.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def get_candidate(self, candidate_id: str) -> CandidateRecord | None:
        path = self._file_path(candidate_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return CandidateRecord.from_dict(data)

    def update_candidate(self, candidate: CandidateRecord) -> None:
        path = self._file_path(candidate.candidate_id)
        path.write_text(json.dumps(candidate.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def update_state(self, candidate_id: str, new_state: ResearchState, note: str = "") -> CandidateRecord:
        cand = self.get_candidate(candidate_id)
        if cand is None:
            raise KeyError(f"Candidate {candidate_id} not found.")
        cand.state = new_state.value
        if note:
            cand.notes = (cand.notes + " | " + note).strip(" | ")
        self.update_candidate(cand)
        return cand

    def list_all(self) -> list[CandidateRecord]:
        results = []
        for file in sorted(self.queue_dir.glob("*.json")):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                results.append(CandidateRecord.from_dict(data))
            except Exception:
                continue
        return results

    def find_by_birth_round(self, round_num: int) -> list[CandidateRecord]:
        return [c for c in self.list_all() if c.birth_round == round_num]

    def count_by_birth_round(self, round_num: int) -> int:
        return len(self.find_by_birth_round(round_num))

"""Duplicate hypothesis checker for AUTO RESEARCH LOOP V1."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .candidate_queue import CandidateQueue
from .constants import ROOT

class DuplicateChecker:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.registry_file = self.root / "00_P45_STATE/experiment_lab/06_INITIAL_EXPERIMENT_REGISTRY.md"
        self.master_file = self.root / "90_RESEARCH/P45_RESEARCH_MASTER_INDEX_005.md"
        self.candidate_queue = CandidateQueue()

    def check_duplicate(self, candidate_name: str, hypothesis_text: str) -> dict[str, Any]:
        """Checks whether a candidate or hypothesis already exists in Registry, Master, or Candidate Queue."""
        # 1. Check Candidate Queue
        for queued in self.candidate_queue.list_all():
            if queued.hypothesis.strip().lower() == hypothesis_text.strip().lower():
                return {
                    "is_duplicate": True,
                    "matched_source": "CANDIDATE_QUEUE",
                    "matched_id": queued.candidate_id,
                    "reason": f"Exact hypothesis text match in candidate {queued.candidate_id}",
                }

        # 2. Check Experiment Registry
        if self.registry_file.exists():
            content = self.registry_file.read_text(encoding="utf-8")
            # check name or hypothesis keywords
            norm_name = re.sub(r"\s+", " ", candidate_name.strip().lower())
            for line in content.splitlines():
                if norm_name in line.lower() and norm_name:
                    return {
                        "is_duplicate": True,
                        "matched_source": "INITIAL_EXPERIMENT_REGISTRY",
                        "matched_id": line.strip()[:40],
                        "reason": f"Candidate name matched existing Registry entry: {candidate_name}",
                    }

        # 3. Check Research Master
        if self.master_file.exists():
            content = self.master_file.read_text(encoding="utf-8")
            norm_name = re.sub(r"\s+", " ", candidate_name.strip().lower())
            if norm_name in content.lower() and norm_name:
                return {
                    "is_duplicate": True,
                    "matched_source": "RESEARCH_MASTER",
                    "matched_id": norm_name,
                    "reason": f"Candidate name matched Research Master index: {candidate_name}",
                }

        return {
            "is_duplicate": False,
            "matched_source": None,
            "matched_id": None,
            "reason": "NO_DUPLICATE_FOUND",
        }

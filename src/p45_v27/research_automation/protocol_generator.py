"""Protocol generator and locker for AUTO RESEARCH LOOP V1."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .candidate_queue import CandidateRecord

class ProtocolGenerator:
    @staticmethod
    def generate(candidate: CandidateRecord) -> dict[str, Any]:
        """Generates a complete, locked protocol specification for a candidate."""
        r = candidate.birth_round
        return {
            "protocol_version": "P45-AUTO-PROTOCOL-V1",
            "candidate_id": candidate.candidate_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source_research": candidate.source_research,
            "candidate_type": candidate.candidate_type,
            "hypothesis": candidate.hypothesis,
            "opposite_hypothesis": candidate.opposite_hypothesis,
            "rationale": "Automated empirical follow-up under strict pre-registration.",
            "data_ranges": {
                "historical_prior_range": [1, r],
                "discovery_range": [1, r],
                "discovery_data_status": "EXPLORATORY_ONLY_CANNOT_BE_USED_FOR_CONFIRMATORY_VERDICT",
                "confirmatory_start_round": r + 1,
                "confirmatory_range_type": "PROSPECTIVE_OR_UNTOUCHED_HOLDOUT",
            },
            "metrics": {
                "primary": "Hit rate in official target MAIN6 vs fair random null",
                "secondary": ["Wilson 95% CI", "Exact two-sided binomial p", "Sequential Wald stopping bound"],
            },
            "null_model": "Fair 6/45 uniform hypergeometric / permutation null",
            "minimum_sample": candidate.minimum_sample,
            "success_criteria": "Confirmatory hit rate > null with two-sided p <= 0.05 and minimum sample satisfied",
            "failure_criteria": "Confirmatory hit rate <= null or failure to achieve significance at stopping bound",
            "multiple_testing_family": f"FAMILY-{candidate.candidate_id}",
            "prospective_walkforward_plan": "Append-only shadow tracking on new canonical draws as published",
            "stopping_rule": "Minimum 50 rounds, formal interim look every 25 rounds, terminate if Wald lower rejection boundary crossed",
            "future_data_blocking": {
                "status": "ENFORCED",
                "pending_outcomes_masked": True,
                "read_future_forbidden": True,
            },
            "official_isolation": {
                "official_engine_modification": "PROHIBITED",
                "official_db_modification": "PROHIBITED",
                "official_web_recommendation_modification": "PROHIBITED",
                "promotion_requires_explicit_user_approval": True,
            },
        }

class ProtocolLocker:
    @staticmethod
    def lock_protocol(protocol: dict[str, Any], output_dir: Path) -> dict[str, Any]:
        """Calculates SHA-256 and creates an authoritative PROTOCOL_LOCK record."""
        output_dir.mkdir(parents=True, exist_ok=True)
        canonical_json = json.dumps(protocol, ensure_ascii=False, sort_keys=True, indent=2)
        digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

        lock_record = {
            "candidate_id": protocol["candidate_id"],
            "protocol_sha256": digest,
            "locked_at": datetime.now(timezone.utc).isoformat(),
            "state": "PROTOCOL_LOCKED",
            "outcomes_computed_before_lock": False,
        }

        protocol_file = output_dir / "protocol.json"
        protocol_file.write_text(canonical_json + "\n", encoding="utf-8")

        lock_file = output_dir / "PROTOCOL_LOCK.json"
        lock_file.write_text(json.dumps(lock_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        return {
            "protocol_file": str(protocol_file),
            "lock_file": str(lock_file),
            "protocol_sha256": digest,
            "locked_at": lock_record["locked_at"],
        }

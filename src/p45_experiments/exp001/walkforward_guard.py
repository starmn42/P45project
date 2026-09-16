from __future__ import annotations

from dataclasses import dataclass

from .calculator import prediction_hash


@dataclass
class PreResultGuard:
    evaluation_round: int
    source_end_round: int
    prediction_network_hash: str | None = None
    outcome_accesses: int = 0

    def __post_init__(self) -> None:
        if self.source_end_round != self.evaluation_round - 1:
            raise ValueError("SOURCE_END_ROUND_NOT_R_MINUS_ONE")

    def lock_prediction(self, payload: object) -> str:
        if self.outcome_accesses:
            raise RuntimeError("OUTCOME_ALREADY_ACCESSED")
        self.prediction_network_hash = prediction_hash(payload)
        return self.prediction_network_hash

    def authorize_outcome_access(self) -> None:
        if not self.prediction_network_hash:
            raise RuntimeError("PREDICTION_HASH_REQUIRED_BEFORE_OUTCOME")
        self.outcome_accesses += 1


"""Data contracts for the independent P45 v2.7 unit calculators."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Draw:
    round: int
    main: tuple[int, int, int, int, int, int]
    bonus: int

    def __post_init__(self) -> None:
        if self.round < 1 or len(set(self.main)) != 6:
            raise ValueError("invalid draw")
        if self.bonus in self.main or any(n < 1 or n > 45 for n in (*self.main, self.bonus)):
            raise ValueError("draw numbers must be seven distinct values from 1 through 45")


@dataclass(frozen=True)
class UnitGroup:
    order: int
    label: str
    members: tuple[int, ...]

    @property
    def size(self) -> int:
        return len(self.members)


@dataclass(frozen=True)
class UnitDefinition:
    unit_type: str
    groups: tuple[UnitGroup, ...]
    correction_method: str = "GROUP_SIZE_RATE_EXPECTATION_NORMALIZED_DEVIATION"


@dataclass(frozen=True)
class UnitAnalysis:
    unit_type: str
    analysis_round: int
    definition: dict[str, Any]
    round_metrics: tuple[dict[str, Any], ...]
    period_metrics: dict[str, Any]
    exact_vector_sample: dict[str, Any]
    group_local_state_samples: dict[str, Any]
    performance: dict[str, Any]
    number_metrics: dict[int, dict[str, Any]]
    sample_state: str
    opposite_hypothesis_inputs: dict[str, Any]
    structure_collapse_inputs: dict[str, Any]
    unit_state: str
    calculation_status: str
    data_hash: str
    execution_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

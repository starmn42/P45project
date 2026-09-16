"""Immutable inputs and candidate records for PAIR stage 2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


ALLOWED_TRIO_STATES = {"TRIO_PASS", "TRIO_WEAKEN", "TRIO_TEST"}


@dataclass(frozen=True)
class TrioInput:
    trio_id: str
    numbers: tuple[int, int, int]
    trio_state: str
    trio_rule_signature: str
    valid_for_pair: bool = True

    def __post_init__(self) -> None:
        if len(self.numbers) != 3 or tuple(sorted(self.numbers)) != self.numbers:
            raise ValueError("TRIO_NUMBERS_NOT_STRICTLY_SORTED")
        if len(set(self.numbers)) != 3 or any(number < 1 or number > 45 for number in self.numbers):
            raise ValueError("TRIO_NUMBERS_INVALID")
        if self.trio_state not in ALLOWED_TRIO_STATES:
            raise ValueError("TRIO_STATE_NOT_PAIR_ELIGIBLE")
        if len(self.trio_rule_signature) != 64:
            raise ValueError("TRIO_SIGNATURE_INVALID")

    @property
    def trio_key(self) -> str:
        return "-".join(str(number) for number in self.numbers)


@dataclass(frozen=True)
class PairSignatureContext:
    pair_pool_type: str
    pair_unit_coverage_state_vector: tuple[str, ...]
    role_diversity_vector: tuple[int, ...]
    evidence_overlap_vector: tuple[int, ...]
    member_maximum_risk: str
    member_structure_summary: str

    def __post_init__(self) -> None:
        if len(self.pair_unit_coverage_state_vector) != 5:
            raise ValueError("PAIR_UNIT_VECTOR_NOT_FIVE")
        if len(self.role_diversity_vector) != 5 or len(self.evidence_overlap_vector) != 5:
            raise ValueError("PAIR_ROLE_EVIDENCE_VECTOR_NOT_FIVE")
        if any(value < 0 for value in (*self.role_diversity_vector, *self.evidence_overlap_vector)):
            raise ValueError("PAIR_VECTOR_NEGATIVE")


@dataclass(frozen=True)
class PairCandidate:
    pair_candidate_id: str
    canonical_pair_key: str
    lower_member: TrioInput
    upper_member: TrioInput
    pair_rule_signature: str
    signature_payload: Mapping[str, Any]

    @property
    def numbers(self) -> tuple[int, ...]:
        return tuple(sorted((*self.lower_member.numbers, *self.upper_member.numbers)))

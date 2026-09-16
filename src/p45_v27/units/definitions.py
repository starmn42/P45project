"""Exact, non-overlapping definitions of the five mandatory v2.7 units."""

from __future__ import annotations

from .models import UnitDefinition, UnitGroup


def _ranges(unit_type: str, width: int) -> UnitDefinition:
    groups = []
    for order, start in enumerate(range(1, 46, width), 1):
        end = min(start + width - 1, 45)
        groups.append(UnitGroup(order, f"{start}-{end}", tuple(range(start, end + 1))))
    return UnitDefinition(unit_type, tuple(groups))


UNIT_3 = _ranges("UNIT_3", 3)
UNIT_5 = _ranges("UNIT_5", 5)
UNIT_9 = _ranges("UNIT_9", 9)
UNIT_10 = _ranges("UNIT_10", 10)

END_DIGIT = UnitDefinition(
    "END_DIGIT",
    tuple(
        UnitGroup(order=digit + 1, label=f"END_{digit}",
                  members=tuple(n for n in range(1, 46) if n % 10 == digit))
        for digit in range(10)
    ),
)

DEFINITIONS = {d.unit_type: d for d in (UNIT_3, UNIT_5, UNIT_9, UNIT_10, END_DIGIT)}


def validate_definition(definition: UnitDefinition) -> None:
    flattened = [n for group in definition.groups for n in group.members]
    if sorted(flattened) != list(range(1, 46)):
        raise ValueError(f"{definition.unit_type} must contain every number 1..45 exactly once")
    if any(group.order != index for index, group in enumerate(definition.groups, 1)):
        raise ValueError("group order must be continuous")


for _definition in DEFINITIONS.values():
    validate_definition(_definition)

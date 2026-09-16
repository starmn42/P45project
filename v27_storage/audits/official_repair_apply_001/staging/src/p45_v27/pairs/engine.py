"""Disjoint PAIR candidate, canonical key, and identity-free rule signature."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections.abc import Callable, Iterable, Mapping
from typing import Any

from .models import PairCandidate, PairSignatureContext, TrioInput
from .audit_v12 import SIGNATURE_VERSION, canonical_json, rule_signature


def canonical_pair_key(first: TrioInput, second: TrioInput) -> str:
    if set(first.numbers) & set(second.numbers):
        raise ValueError("PAIR_MEMBERS_OVERLAP")
    lower, upper = sorted((first.trio_key, second.trio_key))
    return f"{lower}__{upper}"


def signature_payload(first: TrioInput, second: TrioInput, context: PairSignatureContext) -> dict[str, Any]:
    """Return v1.2 repeatable policy identity only; all member/round context is excluded."""
    return rule_signature(context.pair_pool_type)[2]


def pair_rule_signature(first: TrioInput, second: TrioInput, context: PairSignatureContext) -> tuple[str, dict[str, Any]]:
    digest, _, payload = rule_signature(context.pair_pool_type)
    return digest, payload


base_pair_rule_signature = pair_rule_signature


def generate_pair_candidates(
    trios: Iterable[TrioInput],
    context_factory: Callable[[TrioInput, TrioInput], PairSignatureContext],
) -> tuple[PairCandidate, ...]:
    eligible = sorted((trio for trio in trios if trio.valid_for_pair), key=lambda item: item.trio_key)
    candidates: dict[str, PairCandidate] = {}
    for first, second in itertools.combinations(eligible, 2):
        if set(first.numbers) & set(second.numbers):
            continue
        key = canonical_pair_key(first, second)
        if key in candidates:
            continue
        lower, upper = sorted((first, second), key=lambda item: item.trio_key)
        signature, payload = pair_rule_signature(lower, upper, context_factory(lower, upper))
        candidate_id = "PAIR-" + hashlib.sha256(key.encode("utf-8")).hexdigest()
        candidates[key] = PairCandidate(candidate_id, key, lower, upper, signature, payload)
    return tuple(candidates[key] for key in sorted(candidates))

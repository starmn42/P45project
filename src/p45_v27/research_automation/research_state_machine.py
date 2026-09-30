"""State machine and promotion firewall for AUTO RESEARCH LOOP V1."""
from __future__ import annotations

from typing import Set

from .constants import ResearchState

# Allowed state transitions
VALID_TRANSITIONS: dict[ResearchState, Set[ResearchState]] = {
    ResearchState.IDEA_CANDIDATE: {
        ResearchState.REJECT_DUPLICATE,
        ResearchState.REJECT_RESCUE,
        ResearchState.REJECT_NOT_TESTABLE,
        ResearchState.WAIT_PROSPECTIVE,
        ResearchState.READY_FOR_PROTOCOL,
        ResearchState.REVIEW_REQUIRED_V1_1,
        ResearchState.NEEDS_EVIDENCE,
    },
    ResearchState.REVIEW_REQUIRED_V1_1: {
        ResearchState.REJECT_DUPLICATE,
        ResearchState.REJECT_RESCUE,
        ResearchState.NEEDS_EVIDENCE,
        ResearchState.READY_FOR_PROTOCOL,
        ResearchState.RETIREMENT_CANDIDATE,
    },
    ResearchState.NEEDS_EVIDENCE: {
        ResearchState.READY_FOR_PROTOCOL,
        ResearchState.REJECT_DUPLICATE,
        ResearchState.REJECT_RESCUE,
        ResearchState.RETIREMENT_CANDIDATE,
    },
    ResearchState.READY_FOR_PROTOCOL: {
        ResearchState.PROTOCOL_LOCKED,
        ResearchState.REJECT_NOT_TESTABLE,
        ResearchState.REVIEW_REQUIRED_V1_1,
        ResearchState.REJECT_DUPLICATE,
        ResearchState.REJECT_RESCUE,
        ResearchState.NEEDS_EVIDENCE,
    },
    ResearchState.PROTOCOL_LOCKED: {
        ResearchState.TESTING,
        ResearchState.WAIT_PROSPECTIVE,
    },
    ResearchState.WAIT_PROSPECTIVE: {
        ResearchState.TESTING,
        ResearchState.RETIREMENT_CANDIDATE,
    },
    ResearchState.TESTING: {
        ResearchState.SUPPORTED,
        ResearchState.INCONCLUSIVE,
        ResearchState.FAILED,
    },
    ResearchState.SUPPORTED: {
        ResearchState.PROMOTION_CANDIDATE,
    },
    ResearchState.INCONCLUSIVE: {
        ResearchState.WAIT_PROSPECTIVE,
        ResearchState.RETIREMENT_CANDIDATE,
    },
    ResearchState.FAILED: {
        ResearchState.RETIREMENT_CANDIDATE,
    },
    ResearchState.PROMOTION_CANDIDATE: {
        ResearchState.USER_APPROVAL_REQUIRED,
    },
    # Terminal states or user-held states
    ResearchState.USER_APPROVAL_REQUIRED: set(),
    ResearchState.REJECT_DUPLICATE: set(),
    ResearchState.REJECT_RESCUE: set(),
    ResearchState.REJECT_NOT_TESTABLE: set(),
    ResearchState.RETIREMENT_CANDIDATE: set(),
}

class PromotionFirewallViolation(PermissionError):
    """Raised when an attempt is made to bypass user approval or auto-promote into official engine."""
    pass

class InvalidStateTransitionError(ValueError):
    """Raised when an illegal state transition is attempted."""
    pass

class ResearchStateMachine:
    @staticmethod
    def validate_transition(current: str | ResearchState, target: str | ResearchState) -> None:
        try:
            curr_state = ResearchState(current) if isinstance(current, str) else current
        except ValueError:
            raise InvalidStateTransitionError(f"UNRECOGNIZED_STATE: {current}")

        # Promotion Firewall check: if at PROMOTION_CANDIDATE, the ONLY permissible transition is USER_APPROVAL_REQUIRED
        if curr_state == ResearchState.PROMOTION_CANDIDATE:
            if target not in (ResearchState.USER_APPROVAL_REQUIRED, ResearchState.USER_APPROVAL_REQUIRED.value):
                raise PromotionFirewallViolation(
                    "PROMOTION_FIREWALL_ACTIVE: A promotion candidate must stop at USER_APPROVAL_REQUIRED. "
                    "Automatic promotion into the Official Engine is strictly prohibited."
                )

        try:
            tgt_state = ResearchState(target) if isinstance(target, str) else target
        except ValueError:
            raise InvalidStateTransitionError(f"UNRECOGNIZED_TARGET_STATE: {target}")

        allowed = VALID_TRANSITIONS.get(curr_state, set())
        if tgt_state not in allowed:
            raise InvalidStateTransitionError(
                f"ILLEGAL_STATE_TRANSITION: Cannot transition from {curr_state.value} to {tgt_state.value}. "
                f"Allowed targets: {[s.value for s in allowed]}"
            )

    @staticmethod
    def is_terminal(state: str | ResearchState) -> bool:
        s = ResearchState(state) if isinstance(state, str) else state
        return len(VALID_TRANSITIONS.get(s, set())) == 0

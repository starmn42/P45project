# NULL SEMANTICS AUDIT

## Input classification

- Canonical draw CSV and MAIN6/BONUS-derived UNIT/NUMBER features: `A — draw outcome-derived`.
- TRIO walk-forward exposure DB: `A — draw outcome-derived`; it contains prior actual-history outcomes and rule exposures.
- PAIR walk-forward DB: `A — draw outcome-derived`; it contains prior actual-history outcomes, lifecycle evidence, and round decisions.
- KTS/locked policy files: `B/C — pre-draw or round-index deterministic`.
- Target outcome at decision time: forbidden; baseline confirms source boundary `R-1`.

## Blocking finding

The authoritative baseline entrypoint does not derive the complete engine state from the supplied draw CSV alone. It combines:

1. `analysis-input.csv`,
2. the persisted official TRIO walk-forward database, and
3. the persisted official PAIR walk-forward database.

Replacing only the draw CSV would retain actual winning-number-derived TRIO/PAIR evidence and invalidate the fair null. Rebuilding both databases would require choosing a lifecycle/materialization path for which no single locked whole-engine null entrypoint or locked cache key exists. The repository contains both historical anomaly evidence and later shadow/compatibility repair code; selecting one as the synthetic production semantics would be a new semantic decision, not a read/cache/batch optimization.

Therefore the same FROZEN Official meaning cannot currently be applied to synthetic histories without either retaining actual-history information or introducing an unapproved engine-semantic implementation choice.

- Actual-history derived feature retained: `BLOCKED`
- Future leakage permitted: `0`
- Safe fair-null execution: `NO`
- Decision: `STOP_NULL_SEMANTICS_NOT_VALID`


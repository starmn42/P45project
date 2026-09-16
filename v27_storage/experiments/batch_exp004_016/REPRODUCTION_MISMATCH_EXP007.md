# P45 EXP-004~016 batch settlement — reproduction mismatch

- phase: `PHASE_C_INDEPENDENT_REPRODUCTION`
- first mismatching experiment: `EXP-007`
- status: `REPRODUCTION_MISMATCH`
- registry/state/decision reflection: `NO`
- official engine change: `NO`

## Locked rule

`P45_EXP007_사전등록_프로토콜_LOCKED_001.md`, Walkforward section:

- minimum training: 200 informative target rounds
- expose target R only when the training analytical two-sided p-value is `<= 0.05`
- training uses only prior informative outcomes

## Independent result

- informative target rounds: `1213`
- post-minimum evaluable rounds: `1013`
- rounds satisfying the locked analytical signal gate: `0`
- therefore signal-exposed rounds under the locked rule: `0`

## Comparison document

`P45_EXP007_독립분석_결과_001.md` reports:

- `SIGNAL_EXPOSED_ROUNDS: 1013`

That value equals every post-minimum evaluable round and is not the result of
applying the locked `p <= 0.05` signal gate.  The mismatch is integer/exact and
cannot be treated as a numerical-library tolerance.

## Settlement consequence

- EXP-007 is not marked `REPRODUCED`.
- EXP-004~016 batch settlement is not reflected in Registry/Decision/STATE.
- EXP-008~016 calculations present in the raw batch log are
  `NOT_ADJUDICATED` and must not be used as settlement evidence.
- The timestamped pre-write backup is retained.
- No threshold, protocol, or result was changed to force agreement.

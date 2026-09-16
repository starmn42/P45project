# EXP-CROWD-TOPO-001-V1 FINAL RESULT

- Final judgment: `FAILED`
- Domain: `CROWD / PRIZE_SHARE`, separate from DRAW
- Protocol: `EXP-CROWD-TOPO-001-PROTOCOL-1.0`
- Protocol SHA-256: `421720adfa6cee93b622cdf51e7aac3200f3e44ae934e36c2790289aa1988006`
- Data: exactly rounds 1–1237
- Snapshot SHA-256: `1a03abc4babec2cd64eda8c426429747352e412bc1f63e5513f7794aa980ef32`
- Round 1238+ used: `NO`

## Locked structure

- Johnson graph: `J(45,6)`
- vertices: `8,145,060`
- distance-1 degree: `234`
- K2 shell: `6`
- K3 shell: `228`
- full-shell identity: `PASS`

## Sequential result

- TRAIN 1–800 THETA: `0.04552699104566624`
- TRAIN direction gate: `PASS`
- HOLDOUT 801–1237 THETA: `-0.006490796148433605`
- HOLDOUT T: `-0.23637472744996546`
- primary 19-round block-wild one-sided p: `0.6344536554634453`
- primary bootstrap repetitions: `100,000`
- secondary fair-uniform MC one-sided p: `0.6814531854681454`
- secondary MC repetitions: `100,000`

The confirmatory holdout direction was negative and the locked primary p-value was above 0.05. The distance-1 hypothesis therefore failed under the pre-registered rule. The positive TRAIN result cannot override the confirmatory failure.

## Secondary diagnostics

- V_HAT: `0.038860200996909955`
- RHO1_HAT: `-0.16702940236849864`
- positive 19-round holdout blocks: `11 / 23`
- median block THETA: `-0.005232795236369419`
- first 11 blocks mean: `-0.06480323753447471`
- last 12 blocks mean: `0.046962275122104075`

These diagnostics are descriptive only and do not alter the failure judgment.

## Reproducibility and interpretation

- deterministic locked rerun: `PASS`
- independent implementation: `NOT_YET`
- novelty: `NOVELTY_NOT_CONFIRMED`
- promotion candidate: `NO`
- official/DRAW connection: `NO`
- recommendation generated: `NO`

This result does not establish the absence of every form of crowd clustering. It rejects only the locked V1 global-average Johnson-distance-1 hypothesis under its specified observable, split, and inference rule. Distance 2/3 or any altered construction requires a new independently pre-registered experiment and may not be used to rescue V1.

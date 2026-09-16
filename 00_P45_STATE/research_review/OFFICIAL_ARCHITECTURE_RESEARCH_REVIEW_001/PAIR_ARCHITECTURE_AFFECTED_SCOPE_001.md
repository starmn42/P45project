# PAIR ARCHITECTURE AFFECTED SCOPE 001

| Scope | Count / status | Interpretation |
|---|---:|---|
| valid evaluation rounds | 867 | end-to-end intended gate-performance interpretation affected |
| rounds with raw PAIR candidates | 258 | directly affected by missing evidence/lifecycle |
| raw PAIR candidates | 148,215 | PG07/PG08 incomplete; TEST_READY unreachable |
| CORE entry rounds directly blocked after PAIR existed | 258 | cannot attribute all to intended canonical gates |
| official output rounds | 0/867 | observed implementation fact, not valid intended-gate performance evidence |

Other consumers:

- v1.2 PAIR walk-forward runner: affected.
- final aggregation: partially compensates for current round by post-materializing historical metrics and calling `decide_state`; it does not repair historical per-r states.
- draw update/current live diagnostic: affected because it calls `ProductionPairPipeline` and consumes its `pair_state` directly.
- web adapter: downstream display only; it reflects stored live state and does not create the anomaly.
- NUMBER and TRIO calculators: no evidence that their own raw computation is changed by this PAIR anomaly.

`LIVE_CURRENT_PATH_AFFECTED = YES`.


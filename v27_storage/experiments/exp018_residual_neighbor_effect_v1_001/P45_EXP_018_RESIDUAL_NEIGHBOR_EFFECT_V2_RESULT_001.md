# P45 EXP-018 V2 — LOCKED HISTORICAL RESULT 001

## Final verdict

`AXIS_CLOSED_NO_PRACTICALLY_USEFUL_RESIDUAL_NEIGHBOR_EFFECT`

Both locked historical splits meet `NO_PRACTICALLY_USEFUL_EFFECT` because their one-sided percentile cluster-bootstrap `U95_DELTA` values are below the predeclared `+1.00 percentage point` practical threshold. This does not assert an exactly zero effect.

## Lock and structural gates

- V2 protocol SHA-256: `a75bbe585f01be80ced3dd1252aad2f3b5de2e1b0d93e5db3d3ade73408c3127` — `PASS`
- V2 lock SHA-256: `da2c637e994fbd0c39b49a97471f342a1dbc332e91fa2817b8b9fbf37b7a8909` — `PASS`
- Structural reproduction: `PASS`
- V1 preserved: `YES`; V1 outcome peek remained `0`

## Development — targets 2..867

- Targets: `866`
- Matched target rounds: `865`
- Matched strata: `4824`
- Neighbor exposures/hits: `6395 / 794`
- Control exposures/hits: `10995 / 1503`
- Neighbor pooled hit rate: `0.12415949960906958`
- Control pooled hit rate: `0.13669849931787176`
- DELTA_MATCH: `-0.014799096572073877` (`-1.4799096572073878 percentage points`)
- Exact one-sided upper-tail p_primary: `0.9958470161615511`
- Bootstrap: target-round cluster percentile; `B=100000`; seed `20260827`; Python `random.Random`
- U95_DELTA: `-0.005820557149569155` (`-0.5820557149569155 percentage points`)
- Split verdict: `NO_PRACTICALLY_USEFUL_EFFECT`

## Holdout / Historical Walkforward — targets 868..1238

- Targets: `371`
- Matched target rounds: `371`
- Matched strata: `2030`
- Neighbor exposures/hits: `2788 / 361`
- Control exposures/hits: `4828 / 651`
- Neighbor pooled hit rate: `0.12948350071736012`
- Control pooled hit rate: `0.13483844241922122`
- DELTA_MATCH: `-0.011945017326033019` (`-1.1945017326033018 percentage points`)
- Exact one-sided upper-tail p_primary: `0.9216621575441747`
- Bootstrap: target-round cluster percentile; `B=100000`; seed `20260827`; Python `random.Random`
- U95_DELTA: `0.002524020616370079` (`0.2524020616370079 percentage points`)
- Split verdict: `NO_PRACTICALLY_USEFUL_EFFECT`

## Closure interpretation

The exact closed scope is `T-1 MAIN6 -> numerical label ±1 adjacency -> T MAIN6 predictive axis`. Without new independent external evidence, no V3 rescue, historical retuning, Age subgroup, +1/-1 split, favorable-period/number mining, or combination of this ±1 axis with Return-age, extinction, frequency, or an existing failed axis is permitted.

This result does not close ±2 or larger distances, same-round consecutive pairs, sorted-position adjacency, TRIO-internal relations, physical-ball adjacency, or other independent spatial/transition structures.

## Reproducibility and protection

- Two complete identical runner executions before annotation produced calculation SHA-256 `022cfe1a6dd9baf2bdfbad0a6d2e9eb3038925b016f5d81ddc576d5fad4adaf2`.
- Primary exact, DELTA_MATCH, U95, both split verdicts, and final verdict reproduction: `PASS`.
- Signalization allowed now: `NO`.
- Prospective required: `NO`.
- V1 files changed: `NO`.
- V2 protocol/lock changed: `NO`.
- Official/DB/Fixed/Linked/KTS/sealed 1239/prospective outcome changes: `0`.
- Existing experiment verdict changes: `0`.
- FUTURE_LEAKAGE: `0`.

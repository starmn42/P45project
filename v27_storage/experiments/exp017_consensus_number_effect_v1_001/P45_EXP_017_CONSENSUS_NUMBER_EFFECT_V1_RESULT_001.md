# P45 EXP-017 — TRIO ORBIT CONSENSUS NUMBER EFFECT V1 RESULT 001

## Final verdict

`FAILED_NOT_SUPPORTED`

The locked Development stage did not satisfy both confirmatory conditions. Formal Historical Walkforward was therefore not executed.

## Lock verification

- Protocol SHA-256 expected/actual: `da86d5192cf25a7d45b3c8eb8d68a55d06f720613cd2335dc41f06fdf0cd83a3` / `da86d5192cf25a7d45b3c8eb8d68a55d06f720613cd2335dc41f06fdf0cd83a3` — `PASS`
- Lock SHA-256 expected/actual: `839ae4c0e96a19823d8b900447cb8082fd696dc67bbac4e75d28c504e381272c` / `839ae4c0e96a19823d8b900447cb8082fd696dc67bbac4e75d28c504e381272c` — `PASS`
- Structural reproduction: `PASS`

## Development — targets 2..867

- Targets: `866`
- Consensus-active rounds: `769`
- Total exposures: `1592`
- Total hits: `224`
- Consensus inclusion rate: `0.1407035175879397` (`14.07035175879397%`)
- Null rate: `0.1333333333333333` (`13.33333333333333%`)
- Absolute lift: `+0.7370184254606366 percentage points`
- Exact one-sided upper-tail p_primary: `0.19907501596738386`
- Rate condition: `PASS`
- p-value condition at locked alpha 0.05: `FAIL`
- Development verdict: `FAILED_NOT_SUPPORTED`

The exact primary p-value is from dynamic-programming convolution of the locked per-target `Hypergeometric(45, k_t, 6)` distributions. No binomial or Monte Carlo approximation replaced the primary null.

## Conditional Historical Walkforward

- Executed: `NO`
- Reason: `DEVELOPMENT_FAILED_PROTOCOL_GATE`
- Targets 868..1238 were not formally outcome-evaluated by this execution.

## Secondary robustness

- Executed on Development interval: `YES`
- Target shuffles: `100000`
- Seed: `20260827`
- One-sided add-one p_secondary: `0.1993580064199358`
- Status: `ROBUSTNESS_CONTEXT_ONLY`

This secondary result does not alter or rescue the failed primary verdict.

## Lifecycle and prospective status

- Lifecycle: `READY_FOR_TEST -> TESTING -> BACKTESTED -> FAILED`
- Historical conclusion: `FAILED_NOT_SUPPORTED`
- WALKFORWARD_TESTED: `NO`
- SUPPORTED: `NO`
- PROMOTION_CANDIDATE: `NO`
- Formal prospective confirmation required under the locked historical gate: `NO`
- Sealed target 1239 remains unchanged and its outcome was neither read nor written.

## Protection

- Protocol changed: `NO`
- Lock changed: `NO`
- Official changes: `0`
- DB changes: `0`
- Fixed changes: `0`
- Linked changes: `0`
- KTS changes: `0`
- Sealed 1239 changes: `0`
- Prospective outcome changes: `0`
- Existing TRIO ORBIT verdict changed: `NO`
- Divergence attribution verdict changed: `NO`
- FUTURE_LEAKAGE: `0`

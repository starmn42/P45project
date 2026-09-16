# P45 SURVIVOR POOL ACTIONABILITY ROLLING-ORIGIN RESULT 001

## Final

- FINAL_VERDICT: `SURVIVOR_POOL_ACTIONABILITY_VALIDATION_COMPLETE`
- PRIMARY_VERDICT: `NO_DISCOVERY_K`
- MAX_ACTIONABLE_POOL: `NOT_CONFIRMED`
- Current target 1239 ACTIONABLE: `NOT_CONFIRMED`
- PROTOCOL_LOCKED: `YES`
- PROTOCOL_SHA256: `64dead6a65b141bf99725bcfc98106f713bc44843c2135244ea37e4eefa08a44`
- RESULT_JSON_SHA256: `ee9d834047867a0877192f7bd1d09a39f55742de13f336394bae7f073f94cf09`

No discovery K from `1..45` met the locked rule requiring minimum sample and a round-cluster-bootstrap 95% CI lower bound above zero. Therefore no K was selected, no confirmation predictive test was performed, and no maximum actionable pool can be introduced. Survivor pools remain research information without an arbitrary cap or top-K truncation.

## Protocol and boundaries

- Valid targets: `3..1238` (`1236`)
- DISCOVERY_RANGE: `3..867` (`865` targets)
- CONFIRMATION_RANGE: `868..1238` (`371` targets)
- Discovery size fixed as `floor(0.70 × 1236)=865` before outcome calculation.
- Target t feature source maximum: `t-1`; raw survivors froze before MAIN6 scoring.
- Target 1239 outcome access/scoring: `0/0`
- Future leakage: `0`
- Input: contiguous `1..1238`, SHA-256 `1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8`
- Protocol hash unchanged after execution: `PASS`

## Discovery and confirmation

- K candidates evaluated: all integers `1..45`
- Per-K minimum: actionable rounds `>=100`, observations `>=300`
- Per-K bootstrap: `10,000` round-cluster replicates, seed `20260825+K`
- K_DISCOVERY: `NO_DISCOVERY_K`
- DISCOVERY_ACTIONABLE_ROUNDS / OBSERVATIONS / HIT_RATE / DELTA / 95% CI: `N/A — no K satisfied the locked selection rule`
- Confirmation K: `NONE`
- CONFIRMATION_MIN_SAMPLE_PASS: `N/A`
- CONFIRMATION_ACTIONABLE_ROUNDS / OBSERVATIONS / HIT_RATE / DELTA / 95% CI: `NOT_RUN`
- Confirmation predictive outcome test performed: `NO`
- After `NO_DISCOVERY_K` was frozen, confirmation outcomes were used only to complete the required per-target and descriptive exact-N/bin evidence. They did not select, retune, or test a K.
- Multiple-testing / anti-overfit policy: `PASS`

The discovery profile is preserved at `P45_SURVIVOR_POOL_ACTIONABILITY_DISCOVERY_K_PROFILE_001.csv`; it shows no row with `lower_ci_gt_zero=True`.

## Historical raw survivor-count distribution

| Count bucket | Rounds |
|---|---:|
| 0 | 51 |
| 1 | 34 |
| 2 | 25 |
| 3 | 10 |
| 4 | 18 |
| 5 | 7 |
| >=6 | 1091 |

This reproduces the prior official survivor-count distribution across all 1,236 valid targets.

## Fixed coarse-bin descriptive profile

| Bin | Rounds | Avg pool | Candidate hit rate | Avg MAIN hits | Random expected | Lift |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 51 | 0 | N/A | 0 | 0 | N/A |
| 1–2 | 59 | 1.4237 | 0.11905 | 0.16949 | 0.18983 | 0.89286 |
| 3–5 | 35 | 3.9143 | 0.15328 | 0.60000 | 0.52190 | 1.14964 |
| 6–9 | 6 | 6.8333 | 0.12195 | 0.83333 | 0.91111 | 0.91463 |
| 10–14 | 16 | 12.5625 | 0.10448 | 1.31250 | 1.67500 | 0.78358 |
| 15–19 | 129 | 17.7597 | 0.12789 | 2.27132 | 2.36796 | 0.95919 |
| 20–29 | 743 | 24.4859 | 0.13588 | 3.32705 | 3.26478 | 1.01907 |
| 30–39 | 170 | 32.2824 | 0.13156 | 4.24706 | 4.30431 | 0.98670 |
| 40–45 | 27 | 43.1852 | 0.13208 | 5.70370 | 5.75802 | 0.99057 |

The apparent `3–5` descriptive lift cannot establish K: the bin has only 35 rounds, the K rule was evaluated only on discovery, and no discovery K passed its locked clustered CI rule. Bins and exact-N results cannot rescue the primary failure.

## Evidence artifacts

- Per-target evidence: `P45_SURVIVOR_POOL_ACTIONABILITY_PER_TARGET_EVIDENCE_001.csv`; SHA-256 `371b16e7280352c335122da35cf0ab995f1a0ace845ff3886ae40dc2ee10797b`
- Exact-N profile: `P45_SURVIVOR_POOL_ACTIONABILITY_EXACT_N_PROFILE_001.csv`; SHA-256 `48ea2c71b54cf84ac6644c3091e426f31e530ae4eb55945b7ea456e651f57825`
- Coarse-bin profile: `P45_SURVIVOR_POOL_ACTIONABILITY_COARSE_BIN_PROFILE_001.csv`; SHA-256 `d9b5706b0a7245865415aafe56b7697c5d68681e740807a987ec2849f5bc38d7`
- Discovery K profile: `P45_SURVIVOR_POOL_ACTIONABILITY_DISCOVERY_K_PROFILE_001.csv`; SHA-256 `2c63fcc57ba6ef0f1571ca7ec77649b0aa32cbf87624d0ed34259a79c83c1621`
- Exact-N round total: `1236`, validation `PASS`

## Current target 1239 context

- RAW_SURVIVOR_COUNT: `5`
- RAW_SURVIVOR_POOL: `13, 18, 20, 24, 27`
- MAX_ACTIONABLE_POOL: `NOT_CONFIRMED`
- Current 1239 actionable: `NOT_CONFIRMED`
- Target 1239 outcome was neither accessed nor scored.

## Policy disposition

### PARTIAL_SURVIVOR_REPORTING

- Status remains `REPORTING_POLICY_DIRECTION_CONFIRMED`
- REPORTING_MINIMUM remains `NONE`; preserve/report actual raw survivor count `0..N` as research information.

### SURVIVOR_POOL_ACTIONABILITY_POLICY

- Preserve every raw survivor `0..45` in audit evidence.
- User-facing actionable display may use only a data-confirmed `MAX_ACTIONABLE_POOL`.
- MAX cannot be assigned arbitrarily.
- Because MAX is not confirmed, no 5/6/10 or other cap is introduced.
- If a MAX is ever confirmed, `N>MAX` must be `BROAD_POOL / NO_ACTIONABLE_PICK`; `N<=MAX` displays the actual pool; top-K truncation remains forbidden.
- Official 3×2 remains separate.

## Protected state

- Opposite-period validation: `INCONCLUSIVE`; official filter change: `NO`
- State / Decision / Registry: `1.0.88 / DECISION-20260824-095 / 63`
- OFFICIAL ENGINE / NO-PICK / DRAW_DISCOVERY_PAUSE / EXP-017: `FROZEN / UNRESOLVED / ACTIVE / NOT_CREATED`
- Official source / DB changes: `0/0`
- State / Decision / Registry changes: `0/0/0`
- Gate / threshold / signature changes: `0/0/0`
- Forced pick / hidden score / top-K truncation: `0/0/0`
- PROJECT_SOURCES_ACTION_REQUIRED: `YES`

## NEXT_ACTION

`NO_ACTIONABILITY_CAP_MAINTAIN_RESEARCH_ONLY_REPORTING_001`

Keep MAX_ACTIONABLE_POOL unconfirmed and preserve survivor pools as research-only reporting; do not introduce an arbitrary cap or actionable recommendation layer.

`SURVIVOR_POOL_ACTIONABILITY_VALIDATION_COMPLETE`

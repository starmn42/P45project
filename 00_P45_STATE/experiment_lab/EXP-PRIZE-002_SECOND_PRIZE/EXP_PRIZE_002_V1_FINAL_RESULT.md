# EXP-PRIZE-002 V1 Final Result

- STATUS: `SUPPORTED_CROSS_OUTCOME`
- Logical ID: `EXP-PRIZE-002-V1`
- Registry ID: `EXP-PRIZE-20260821-004-V1`
- Protocol SHA-256: `e27100d726264310d2402cb691f8ca8a53d0d2e5f9ece861cd033156573f5302`
- Data range: `1~1237`
- Data SHA-256: `95955ee79afd6b7004f0283776eba9007834d30fd8f0b4b18cce379bf3ec9e4b`
- Round 1238+ used: `NO`
- Rows / missing / duplicate / canonical mismatch: `1237 / 0 / 0 / 0`
- X2 enumeration-to-formula mismatch: `0`

## Locked analysis

- TRAIN beta2: `0.039379783189906856` — PASS
- HOLDOUT beta2: `0.04020656383082838`
- Effect per +1 X2: `1.0410257902595796`
- Primary within-time-block permutation p: `0.028089719102808972` (`2,808` exceedances; 100,000; seed 2026082103) — PASS
- Secondary global permutation p: `0.02867971320286797` (`2,867` exceedances; 100,000; seed 2026082104; diagnostic only)
- WF block delta LL: `10.566984493988855`, `-1.793163354441674`, `0.2987422313137813`, `12.924911390340185`
- WF delta LL total: `21.997474761201147` — PASS
- Deterministic complete rerun: PASS; result SHA-256 unchanged at `785bb10a8d6183f58ac29f7214e5a0ed8a8946784354b1f2f95bfbf7779cc88b`.

## Interpretation boundary

`Cross-outcome corroboration supported.` In the fixed historical sample, the pre-locked average birthday-zone count of the six exact second-prize ticket combinations was positively associated with the second-prize winning-game count after conditioning on sold lines, and passed the locked holdout block-permutation and walkforward gates.

This is not independent empirical replication, causal proof, evidence that buyers actually used birthdays, or a DRAW probability signal. It is not an official-engine rule and is not a promotion candidate. A separately approved prospective confirmation or genuinely independent external dataset is still required.

## Protection

- Future leakage: `0`
- Official engine changed: `NO`
- DRAW_DISCOVERY_PAUSE: `ACTIVE`
- EXP-017 DRAW: `NOT_CREATED`
- NO-PICK: `UNRESOLVED`
- EXP-PRIZE-001 V1/V2/reproduction evidence: unchanged


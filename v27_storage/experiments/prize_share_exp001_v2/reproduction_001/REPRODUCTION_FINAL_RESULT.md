# EXP-PRIZE-001-V2 INDEPENDENT REPRODUCTION RESULT

- STATUS: `INDEPENDENT_REPRODUCTION_PASS`
- Input range: `1~1237`
- Input SHA-256: `86b14968aca3ad10b854f9d5c53eba00a786627f73e353938e1e801dc888fa21`
- Round 1238+ used: `NO`
- Independent implementation: `INDEPENDENT_IRLS_2X2_NEWTON`
- Independent calculator SHA-256: `c3157891c06196b40b4c2bdb2daf31dc058323b3201af3aafc83d45d38b4f29d`
- Independent raw result SHA-256: `5ceb4ffa7798f046fa292ff1964bc2998f5f262de0fc94be377fe2abc3a8ee87`

## Data assertions

- Rows: `1237`
- Missing/duplicates: `0/0`
- Derived birthday-count mismatch: `0`
- Derived historical-price mismatch: `0`
- Derived sold-line mismatch: `0`
- Future leakage: `0`

## Deterministic reproduction

|Quantity|Original reference|Independent|Absolute delta|Limit|Result|
|---|---:|---:|---:|---:|---|
|TRAIN beta|0.0143280465|0.014328046466611778|0.000000000033388222|1e-8|PASS|
|HOLDOUT beta|0.0402626277|0.04026262768425499|0.00000000001574501|1e-8|PASS|
|WF delta LL|3.4704933|3.470493272595604|0.000000027404396|1e-6|PASS|

Independent WF blocks: `0.7178853096798434`, `0.6662083655322135`, `1.640822168657735`, `0.4455774287258123`.

## Fresh permutation

- Fresh seed: `2026082102`
- Fresh permutations: `100,000`
- Exceed count: `2,042`
- Fresh p: `0.02042979570204298`
- Original reference p: `0.0199998`
- Absolute p delta: `0.0004299957020429798`
- Consistency gate `<=0.005`: `PASS`
- Fresh p `<=0.05`: `PASS`
- HOLDOUT beta positive: `PASS`

## Interpretation

`EXP-PRIZE-001 V2 independently reproduced.` Birthday-zone count is associated with a higher first-prize winning-ticket rate conditional on sold lines in this historical dataset.

This is not a causal claim, does not prove actual birthday-number use, does not increase DRAW probability, and is not connected to official recommendations. `PROMOTION_CANDIDATE=NO`; prospective confirmation still requires a separate approved protocol.

## Protection

- Original V1/V2 files changed: `0`
- Official/DRAW engine changed: `0`
- DRAW_DISCOVERY_PAUSE: `ACTIVE`
- EXP-017 DRAW: `NOT_CREATED`
- NO-PICK: `UNRESOLVED`

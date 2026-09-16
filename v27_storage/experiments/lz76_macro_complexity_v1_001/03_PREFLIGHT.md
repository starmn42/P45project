# P45 LZ76 MACRO COMPLEXITY V1 — PREFLIGHT

- status: `PASS`
- duplicate P45 research: `NONE FOUND`
- formal EXP number assigned: `NO`
- Registry write: `0`
- protocol SHA-256: `ca19e210753725ad16f7b692d4be1e9f4a5042ccc1171508141c4a509c1b0b81`

## Synthetic LZ76 crosscheck

|case|length|slow reference c(n)|calculator c(n)|result|
|---|---:|---:|---:|---|
|repeating|256|9|9|PASS|
|alternating|256|9|9|PASS|
|fixed-seed random|256|37|37|PASS|

The slow reference and suffix-automaton calculator use independent implementations of the locked parser and agree in every preregistered synthetic case.

## Input

- exact path: `E:\P45 프로젝트\v27_storage\experiments\exp020_lagged_winner_count_regime_signal_v1_001\P45_EXP_020_OFFICIAL_FULL_HISTORY_001.csv`
- size: `28878 bytes`
- SHA-256: `04394615583466fe52b8c87939ec5c60a8903f119d04b8103ad72e7f356eb4ea`
- rows: `1238`
- rounds: contiguous `1..1238`
- MAIN6 per round: exactly 6 unique values in 1..45 — PASS
- encoded shape: `1238 × 45`
- ones per encoded round: exactly 6 — PASS
- fields read: `draw, main1..main6`
- `winner_count_1st`: ignored
- BONUS used: `NO`
- rounds 1239+: `0`

## Window and environment

- rolling windows: `1139`
- bits per window: `4500`
- adjacent state pairs: `1138`
- Python: `3.12.13`
- NumPy: `2.3.5`
- RNG: `numpy.random.Generator(PCG64)`
- threshold seed: `2026082901`
- final null seed: `2026082902`

All locked preflight gates passed. Threshold/null/actual calculation is authorized under the unchanged protocol.


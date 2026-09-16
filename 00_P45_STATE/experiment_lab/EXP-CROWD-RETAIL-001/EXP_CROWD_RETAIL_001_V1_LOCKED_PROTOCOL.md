# EXP-CROWD-RETAIL-001-V1 LOCKED PROTOCOL

- Logical ID: `EXP-CROWD-RETAIL-001-V1`
- Title: `MANUAL SAME-RETAILER JACKPOT COLLISION`
- Evidence: `POST_LINEAGE_EXPLORATORY`
- Locked after source-schema PASS and before outcome test.
- Input SHA-256: `854ca7256219eadf574ac32ad256b84e9a5bfa42ceece09f0a09dd1eed79cd50`
- Historical range: 262..1237 only; 1238+ forbidden.
- Primary population: offline AUTO/MANUAL first-prize winner rows. SEMIAUTO and official online store ID `51100000` excluded.
- Retailer key: official stable store ID; if absent, exact normalized official store name+address. Fuzzy matching forbidden.
- Primary S_CELL: number of round-retailer cells with at least two MANUAL winner rows.
- Null: round-conditional exchangeability of exactly m manual labels across n eligible winner slots with retailer cell multiplicities fixed.
- E_CELL: sum of exact Hypergeometric P(M_cell>=2).
- Exposure gate: at least 20 duplicate-capable cells and E_CELL>=5.
- Randomization: 500,000, seed `2026082307`, one-sided `(1+count(S*>=S_obs))/500001`.
- Positive gate: exposure PASS, CELL_EXCESS>0, p<=0.01, deterministic rerun PASS.
- Otherwise: `EXPLORATORY_NOT_SUPPORTED`; low exposure ends as `INCONCLUSIVE_LOW_COLLISION_EXPOSURE` without significance test.
- Secondary descriptive only: manual pairs, maximum multiplicity, extra tickets, online-inclusive S_CELL, fixed early/late periods, largest 1/5 cell removal. No additional p-values.
- No same-person claim, no official promotion, no DRAW-engine effect, no threshold change, no prospective protocol change.

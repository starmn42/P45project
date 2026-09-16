# PAIR SHADOW REPAIR 001 LOCKED SPEC

- status: `LOCKED_BEFORE_SHADOW_EXECUTION`
- lock timestamp: `2026-08-24T13:55:49.9081221+09:00`
- baseline state: `1.0.86`
- baseline decision: `DECISION-20260824-093`
- review judgment: `ARCHITECTURE_REPAIR_SPECIFIABLE`
- valid-round definition: the unchanged 867-round population from NO-PICK ROOT CAUSE AUDIT 001
- future boundary: for target r, candidate inputs and historical outcomes end at r-1; outcome r and r+1+ are forbidden

## Locked sources

| File | SHA-256 |
|---|---|
| PAIR_REPAIR_SPECIFICATION_001.md | `214b9cf431a691b8697b7fc2bac284aed17f1e1b6e18ef7ebc24a47a756b2764` |
| PAIR_HISTORICAL_MATERIALIZATION_CONTRACT_V1.md | `1a7b961c13a0c1fd4a5ab0eb9032fb3c3dfc1082833356ed9f9d8d9efe03e542` |
| PAIR_EVIDENCE_PROVENANCE_MAP.md | `72985eb300b3ed66a8aad073d27932eae7d2a41cd619212fb3cf89a9f90f0a23` |
| PAIR_LIFECYCLE_STATE_MACHINE.md | `11fd8d346e38b059d0b4ddf520960e9aa0794a77c95e13256ed27b34253017b4` |
| P45_v2.7.4_PAIR_Gate_Amendment_UTF8_BOM_CRLF.md | `a31a065838f88c65d40605c1a170c13eb5fca7cf3d706de5eda088b43227ae6f` |
| P45_v2.7.4_PAIR_Walkforward_Bootstrap_PATCH_UTF8_BOM_CRLF.md | `df85587a618e520064553456ec82feb87d5d72b1b3b29139d98fc2120d8dcd86` |
| P45_v2.7.4_PAIR_Gate_Timing_PATCH_UTF8_BOM_CRLF.md | `0ecca7f3122cf9017df1d862f86662e851e70202052f994f440e3ffc113bafa7` |
| P45_v2.7.4_PAIR_PG13_Sequence_PATCH_UTF8_BOM_CRLF.md | `4412b86bf7ad322c6e3e4cc3a33023a3b09fa4083195e22f9f1c023b513cbc19` |
| P45_v2.7.4_PAIR_Signature_v1.2_PATCH_UTF8_BOM_CRLF.md | `0c91315ef0cc7d1638a61f321faf3e62079f9545a1386bd3271710b27e113316` |

## Frozen semantics

- Integrated and main exact 3/3 are separate PRIMARY endpoints.
- Integrated and main exact 2/3 are separate SUPPORT endpoints and are never added to PRIMARY.
- Evidence uses canonical Wilson 95%, exact upper/lower one-sided binomial tests, alpha .05, and official endpoint baselines.
- Selection exposure, not identity exposure, is the statistical sample.
- `<50` is RESEARCH_HOLD; `50..199` is at most TEST_READY; `>=200` enables READY statistical gates.
- RECENT100/RECENT50 use selection exposure order; RECENT20 is TEST_ONLY.
- PG01–PG14, TEST_READY §11.4/11.4.1, state precedence, risk, structure, bonus, signature v1.2, and CORE eligibility are unchanged.
- Missing evidence remains explicit; no fallback, invented threshold, implicit PASS, or result-driven exclusion is allowed.

This lock authorizes shadow-only replay. It does not authorize official implementation or recommendation.


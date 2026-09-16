# EXP-CROWD-TOPO-003-V1 SOURCE SCHEMA PREFLIGHT

- Status: `PASS`
- Checked before protocol lock and before tomography outcome analysis.
- Source: immutable local copies of the official lottery API under `downloads/official-1-1237/raw`.
- Semantics: `rnk1WnNope`..`rnk5WnNope` are the first through fifth prize winning-game counts K1..K5; `wholEpsdSumNtslAmt` is total draw sales in KRW.
- Required range: rounds 1..1237 exactly; round 1238+ is excluded.
- Ticket price boundary: rounds 1..87 = KRW 2,000; rounds 88..1237 = KRW 1,000.

## Fixed-round audit

|round|K1|K2|K3|K4|K5|sales|
|---:|---:|---:|---:|---:|---:|---:|
|1|0|1|28|2,537|40,155|3,681,782,000|
|87|11|33|1,250|54,768|890,859|83,793,642,000|
|88|4|31|1,183|64,639|1,098,115|51,910,612,000|
|801|8|51|1,999|97,006|1,618,941|74,034,792,000|
|1201|19|84|3,321|166,050|2,711,377|115,389,593,000|
|1237|23|75|3,745|172,132|2,663,409|118,363,161,000|

The preflight found no missing required field and no source-semantics conflict. The older EXP-001 snapshot has only K1..K3 and therefore is not reused as the calculation input. A new experiment-isolated immutable snapshot is required.

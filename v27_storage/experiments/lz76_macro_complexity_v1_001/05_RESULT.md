# P45 LZ76 MACRO COMPLEXITY V1 — RESULT

## Final verdict

`FAILED_NOT_SUPPORTED`

The preregistered occupancy metric passed its one-sided threshold, but the persistence metric did not. Because the locked verdict requires both metrics to pass, the joint criterion failed. No rescue, alternate window, alternate threshold, alternate direction, subgroup, or seed was tested.

## Locked results

|field|value|criterion|result|
|---|---:|---:|---|
|Threshold q phrase count|211|20,000th / 100,000|LOCKED|
|Threshold q Normalized_LZ76|0.5690299243040062|state A iff score ≤ q|LOCKED|
|Actual state A count|511 / 1,139|diagnostic count|—|
|Actual occupancy|0.4486391571553995|one-sided p ≤ 0.025|PASS|
|Null occupancy mean|0.3092855136084285|10,000 histories|—|
|p1 occupancy|0.014598540145985401|≤ 0.025|PASS|
|Actual lag-1 autocorrelation|0.591537998171019|one-sided p ≤ 0.025|FAIL|
|Null lag-1 autocorrelation mean|0.5832729833447268|10,000 histories|—|
|p2 autocorrelation|0.43745625437456254|≤ 0.025|FAIL|
|Joint AND criterion|false|p1 and p2 both pass|FAIL|

## Scope and interpretation

- data: rounds `1..1238`, MAIN6 only
- rolling windows: `1,139`, exactly 100 rounds / 4,500 bits each
- threshold seed: `2026082901`; final null seed: `2026082902`
- future data used: `0`
- BONUS used: `NO`
- Null NOT_ESTIMABLE: `0 / 10,000`
- reproducibility: `PASS`, canonical numeric result exact match
- official effect: `NONE`
- Registry/Master append applied: `NO`

The result does not support the joint claim that low-complexity states are both more frequent and more persistent than the locked fair 6/45 null. It makes no claim about manipulation, predictability, individual numbers, TRIO, or Official P45 improvement.


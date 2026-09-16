# EXP-CROWD-RETAIL-001-V1 SOURCE SCHEMA PREFLIGHT

- Status: `PASS`
- Checked before protocol lock and before outcome testing.
- Official endpoint: `https://www.dhlottery.co.kr/wnprchsplcsrch/selectLtWnShp.do`
- Parameters: first-prize rank, one specified draw, all locations.
- Official winner-count crosscheck: local immutable official draw API `rnk1WnNope`.
- Range: 262..1237 exactly; 976 rounds; 9,193 first-prize winner rows.
- Unresolved mode/store count mismatches: 0.
- Snapshot SHA-256: `854ca7256219eadf574ac32ad256b84e9a5bfa42ceece09f0a09dd1eed79cd50`
- Source audit SHA-256: `5601e547836243b04b24537c24947ae46aa8dbd174d10fe4730172f568481555`

## Fixed-round semantic audit

|round|rows|mode counts|duplicate retailer cells|online rows|
|---:|---:|---|---:|---:|
|262|2|AUTO 2|0|0|
|879|6|MANUAL 2, AUTO 4|0|0|
|1161|16|MANUAL 6, AUTO 10|1 (max 2)|0|
|1166|14|MANUAL 8, AUTO 6|1 (max 5)|0|
|1176|13|MANUAL 7, AUTO 6|2 (max 4)|0|
|1237|23|MANUAL 9, AUTO 14|2 (max 2)|1|

The API preserves one row per first-prize winning game: repeated official `ltShpId` values remain repeated rows. `atmtPsvYnTxt` supplies `자동`, `수동`, or `반자동`. Online sales are deterministically identified by official store ID `51100000` (with the official internet-site name as an additional audit signal). Stable official `ltShpId` is the primary retailer key; normalized exact official name+address is used only if that ID is absent. No fuzzy matching is permitted.

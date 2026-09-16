# Source availability preflight

- Checked: `2026-08-24T10:53:59+09:00`
- Official page: `https://www.dhlottery.co.kr/wnprchsplcsrch/home`
- Official row endpoint: `https://www.dhlottery.co.kr/wnprchsplcsrch/selectLtWnShp.do`
- Latest published row-level round: `1238` (`23` first-prize rows).
- Round 1239 row total: `0`; result unpublished at lock.
- Stable retailer ID: `ltShpId`; deterministic exact fallback: normalized `shpNm + shpAddr`.
- Mode mapping: `atmtPsvYnTxt` gives `자동/수동/반자동`.
- Duplicate retailer rows are returned as separate rows and retain `rnum`.
- Official row total is provided in `data.total` and can be checked against list length and the official first-prize count.
- Online channel is identifiable by official store ID `51100000` or official internet store name.
- Source semantics remain compatible with the immutable 262~1237 snapshot.

Result: `PASS`. Only source/schema availability was examined; prospective signal statistics were not calculated.

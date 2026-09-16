# EXP-PRIZE-001-V2 SOURCE SEMANTICS NOTE

## Official result semantics

- Official page: `https://www.dhlottery.co.kr/lt645/result`
- Official/internal endpoint: `https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do`
- Retrieval timestamp: `2026-08-21T17:13:55+09:00`
- Official raw bundle: `downloads/official-1-1237/raw`
- Official raw bundle SHA-256: `4b851c6a1e786ec2a7d413f1ac347e9d15e1b7a6fdae032d0309791b9a918b34`
- The official page binds `data.wholEpsdSumNtslAmt` to the element labelled `총판매금액`.
- The official page binds `data.rnk1WnNope` to `1등 / 당첨게임 수`.
- V2 denominator amount: `wholEpsdSumNtslAmt` only.
- `rlvtEpsdSumNtslAmt` is audit-only and excluded from inference.

Modern audit round 1201 confirms the fields are not interchangeable:

- `wholEpsdSumNtslAmt = 115,389,593,000 KRW`
- `rlvtEpsdSumNtslAmt = 57,694,796,500 KRW`
- Official UI total-sales binding: `wholEpsdSumNtslAmt`

## Historical price boundary

- Rounds 1~87: `2,000 KRW/game`.
- Round 88 onward: `1,000 KRW/game`.
- The price reduction began with sales for draw 88 on 2004-08-01; draw 88 was held on 2004-08-07.

Cross-check evidence:

1. National Assembly Budget Office, `2005년도 기금 결산 분석`: describes the August 2004 change in online lottery game price. `https://www.nabo.go.kr/board/file/down.do?fid=1202`
2. Contemporary report quoting the government lottery issuance coordination decision: price reduced from 2,000 to 1,000 KRW from 2004-08-01. `https://www.seoul.co.kr/news/2004/01/31/20040131001005`
3. Contemporary draw-boundary report: sales for draw 88 (drawn 2004-08-07) began on 2004-08-01 at 1,000 KRW instead of 2,000 KRW. `https://www.seoul.co.kr/news/economy/2004/07/22/20040722019001`

These sources agree on both the date and the draw-88 boundary. No third-party dataset is used as the primary K/sales source.

## Fixed semantic audit

|Round|Whole sales KRW|Audit-only relevant amount KRW|Price KRW|Sold lines|First-prize games|Result|
|---:|---:|---:|---:|---:|---:|---|
|1|3,681,782,000|3,681,782,000|2,000|1,840,891|0|PASS|
|10|260,856,392,000|260,856,392,000|2,000|130,428,196|13|PASS|
|87|83,793,642,000|83,793,642,000|2,000|41,896,821|11|PASS|
|88|51,910,612,000|51,910,612,000|1,000|51,910,612|4|PASS|
|1201|115,389,593,000|57,694,796,500|1,000|115,389,593|19|PASS|
|1237|118,363,161,000|59,181,583,190|1,000|118,363,161|23|PASS|

- Integer sold-line conversion: `6/6 PASS` in fixed audit and `1237/1237 PASS` overall.
- Canonical main-number comparison: `1237/1237 PASS`.
- Missing rounds: `0`.
- Duplicate rounds: `0`.
- Round 1238+ in historical snapshot: `0`.
- Semantic audit result: `SEMANTIC_AUDIT_PASS`.

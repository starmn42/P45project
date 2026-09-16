# EXP-CROWD-TOPO-001-V1 Source-Schema Preflight

- Status: `PASS`
- Performed before any LOCAL_EXCESS, correlation, beta, p-value, or outcome-relation calculation.
- Official endpoint: `https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do`
- Official result page binding: `https://www.dhlottery.co.kr/lt645/result`

## Field semantics

- round: `ltEpsd`
- main six: `tm1WnNo` through `tm6WnNo`
- first-prize winning games K1: `rnk1WnNope`
- second-prize winning games K2: `rnk2WnNope`
- third-prize winning games K3: `rnk3WnNope`
- total sales: `wholEpsdSumNtslAmt`
- rounds 1–87 price/game: 2,000 KRW
- rounds 88–1237 price/game: 1,000 KRW
- sold lines N: total sales divided by the applicable price/game

The official result page source binds rank 1, rank 2, rank 3 winner-game counts and total sales to these API fields. The total-sales and price-regime semantics agree with the locked EXP-PRIZE-001 V2 and EXP-PRIZE-002 V1 evidence.

## Fixed semantic-audit rounds

| Round | Main | K1 | K2 | K3 | Total sales KRW | Price/game |
|---:|---|---:|---:|---:|---:|---:|
| 1 | 10-23-29-33-37-40 | 0 | 1 | 28 | 3,681,782,000 | 2,000 |
| 87 | 4-12-16-23-34-43 | 11 | 33 | 1,250 | 83,793,642,000 | 2,000 |
| 88 | 1-17-20-24-30-41 | 4 | 31 | 1,183 | 51,910,612,000 | 1,000 |
| 801 | 17-25-28-37-43-44 | 8 | 51 | 1,999 | 74,034,792,000 | 1,000 |
| 1201 | 7-9-24-27-35-36 | 19 | 84 | 3,321 | 115,389,593,000 | 1,000 |
| 1237 | 10-20-23-34-37-40 | 23 | 75 | 3,745 | 118,363,161,000 | 1,000 |

## Prize-shell identity

- second-prize combinations: main 5 plus bonus; 6 distance-1 vertices
- third-prize combinations: main 5 plus one of the other 38 non-main/non-bonus numbers, with 6 choices for the omitted main; `6 × 38 = 228` vertices
- complete Johnson distance-1 shell: `6 + 228 = 234`
- `K2 + K3` therefore counts winning tickets in the full distance-1 shell.

No historical relationship or experimental outcome was calculated during this preflight.

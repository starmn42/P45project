# EXP-PRIZE-002 V1 Source-Schema Preflight

- Status: `SOURCE_SCHEMA_PREFLIGHT_PASS`
- Audit scope: schema and UI binding only; no relationship, beta, correlation, p-value, subgroup, or trend was calculated before protocol lock.
- Official page: `https://www.dhlottery.co.kr/lt645/result`
- Official endpoint: `https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do`
- Round: `ltEpsd`
- Main numbers: `tm1WnNo` through `tm6WnNo`
- Bonus: `bnsWnNo`
- Second-prize winning games: `rnk2WnNope`
- Total sales: `wholEpsdSumNtslAmt`
- Price: rounds 1~87 = 2,000 KRW; rounds 88~1237 = 1,000 KRW.

The archived official result page binds `data.rnk2WnNope` to the second-rank cell whose header is `당첨게임 수`, binds `data.wholEpsdSumNtslAmt` to the displayed `총판매금액`, and displays `bnsWnNo` as the bonus ball. The official page also defines second prize as five main numbers plus the bonus number.

## Fixed semantic audit rounds

| Round | Bonus (`bnsWnNo`) | Second-prize games (`rnk2WnNope`) | Total sales (`wholEpsdSumNtslAmt`) | Price/game |
|---:|---:|---:|---:|---:|
| 1 | 16 | 1 | 3,681,782,000 | 2,000 |
| 87 | 26 | 33 | 83,793,642,000 | 2,000 |
| 88 | 27 | 31 | 51,910,612,000 | 1,000 |
| 801 | 2 | 51 | 74,034,792,000 | 1,000 |
| 1201 | 37 | 84 | 115,389,593,000 | 1,000 |
| 1237 | 36 | 75 | 118,363,161,000 | 1,000 |

The archived payload, archived official frontend binding, current official UI semantics, existing official updater endpoint, and EXP-PRIZE-001 V2 sales semantics agree. Source ambiguity: 0.


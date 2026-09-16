# Signal-Blind Source Mapping

| Ledger field | Official field |
|---|---|
| round | `ltEpsd` |
| main_numbers | `tm1WnNo`~`tm6WnNo` |
| bonus | `bnsWnNo` |
| first_prize_games | `rnk1WnNope` |
| second_prize_games | `rnk2WnNope` |
| total_sales_amount_krw | `wholEpsdSumNtslAmt` |

Additional raw provenance fields are source endpoint, source schema version, retrieval timestamp, full source-payload SHA-256, selected source-record SHA-256, collector version, and append-batch SHA-256.

Stored derived research fields: `0`. The collector does not import UNIT, NUMBER, TRIO, PAIR, CORE, prize calculators, or statistical libraries.


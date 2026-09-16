# P45 Prospective Raw Source Audit

- Audit status: `COMPLETE`
- Existing updater audited: `YES`
- Existing weekly task found: `NO` (`P45 Weekly Draw Update` was not registered at audit time; its installer definition remains present and unchanged)
- Existing updater modified: `NO`
- Existing scheduler modified: `NO`
- Existing live DB schema modified: `NO`
- Decision: `SUFFICIENT_EXISTING_SOURCE = NO`
- Implementation: `BRANCH B — dedicated official-source raw sidecar`

## Existing updater trace

- Entry point: `P45 회차 업데이트.cmd`
- Module: `src/p45_v27/draw_update.py`
- Live DB: `v27_storage/live/p45_new_draw_update_v1.sqlite3`
- Live CSV: `v27_storage/live/p45_live_draws.csv`
- Endpoint: `https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do`

The live `draw_result` table persistently stores round, date, main-number JSON, bonus, source URL, source-payload hash, and fetched timestamp. It does not persist the required first-prize game count, second-prize game count, or whole-round total sales amount, and it does not retain the full raw payload. Therefore it cannot serve as the complete prospective raw source without modifying frozen official code or the live schema, both of which are forbidden.

The sidecar is consequently isolated from the official/live writer and writes only to the locked prospective experiment namespace.


# OPERATIONS-008 — Weekly Updater Stale Run Audit

- Audit result: `NON_BLOCKING_STALE_AUDIT_RECORD`
- Recovery executed: `NO`
- Original row modified or deleted: `NO`

## Task result

- Decimal: `-1073741510`
- Unsigned value: `3221225786`
- Hex: `0xC000013A`
- Common Windows symbolic interpretation: `STATUS_CONTROL_C_EXIT` / interrupted console-control termination.
- P45 root cause: `NOT_CONFIRMED`

No matching event was available from the local Task Scheduler Operational history for the relevant time window. The updater DB does not record PID, process identity, stdout, stderr, or termination events. Therefore the numeric mapping does not establish who or what interrupted this P45 process.

## Preserved stale row

- run_id: `1283b25b-edee-48c3-96d4-32a29634c16e`
- started_at: `2026-08-23T15:01:45+09:00`
- status: `RUNNING`
- completed_at: `NULL`
- PID/process identity in row: `NONE`
- current matching updater process: `NONE`
- active updater lock or mutex artifact: `NONE FOUND`
- same-run stdout/stderr/log: `NONE FOUND`
- later completed run: `NONE`

## Recovery and readiness

The current updater has no canonical interrupted-run recovery operation. It creates a new run row and does not query older RUNNING rows as a gate. Directly updating the historical row would invent a recovery rule, so it was not done.

A read-only copy of the live DB was exercised with the official fetch replaced by a deterministic `NO_NEW_DRAW` result:

- stale RUNNING row remained preserved: `YES`
- new cloned run reached terminal status: `DRAW_ALREADY_CURRENT`
- stale row blocked the run: `NO`
- clone integrity: `ok`
- clone FK violations: `0`
- source live DB SHA changed: `NO`

This establishes code-path readiness and non-blocking behavior without fetching, fabricating, or storing a future draw.

## Scheduler coexistence

- `P45 Weekly Draw Update`: enabled/ready; Saturday 22:30 and Sunday 09:00.
- `P45 Prize Prospective Raw Capture`: enabled/ready; Sunday 09:30.
- shared write target: `NO`.
- prospective deferral test while updater is active: `PASS`.
- scheduler definitions changed: `NO`.

## Protection

- live DB integrity: `ok`
- live DB FK violations: `0`
- official engine changed: `NO`
- DRAW engine changed: `NO`
- prospective protocol changed: `NO`
- prospective signal calculations: `0`

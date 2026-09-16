# Prospective Raw Capture Operating Note

- Collector: `src/p45_experiments/prospective_raw_capture.py`
- Launcher: `P45 prospective raw capture.cmd`
- Task: `P45 Prize Prospective Raw Capture`
- Schedule: every Sunday 09:30 local time
- Missed-start policy: start when available
- Multiple-instance policy: ignore new instance
- Ledger: `v27_storage/experiments/prize_share_prospective_001_v1/PRIZE_SHARE_PROSPECTIVE_001_LEDGER.jsonl`
- Corrections: `v27_storage/experiments/prize_share_prospective_001_v1/PRIZE_SHARE_PROSPECTIVE_001_CORRECTIONS.jsonl`
- Runs: `v27_storage/experiments/prize_share_prospective_001_v1/collector_runs.jsonl`

The collector verifies the most recently captured official record, then appends only consecutive published rounds beginning at 1238. Equal data produces no write. A changed existing record creates an append-only integrity-conflict record and blocks analysis. Missing source data stops catch-up without skipping a round.

If another Python process or P45 live lock is present, collection returns `DEFERRED_DUE_TO_P45_UPDATE`. Source failure returns no write. The collector never writes the official/live DB.

Before round 1289 is fully published, only raw integrity and availability may be inspected. No partial direction or research-signal report is allowed.


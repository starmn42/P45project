# Prospective raw capture operating note

- Task: `P45 Crowd Retail Prospective Raw Capture`
- Schedule: Sunday 10:00 local time
- Command: `P45 crowd retail prospective raw capture.cmd`
- Collector: `src/p45_experiments/crowd_retail_prospective_raw_capture.py`
- START: 1239; rounds below START always produce no ledger write.
- Same official record hash produces `NO_WRITE`.
- Changed official data appends a new version plus correction record; prior data is never deleted.
- Active collector/update lock, unavailable source, network error or invalid schema causes safe no-write/defer.
- Output is operational metadata only. Signal statistics are absent until an approved stage analysis.
- The PRIZE prospective collector, ledger, task and protocol are separate and unchanged.

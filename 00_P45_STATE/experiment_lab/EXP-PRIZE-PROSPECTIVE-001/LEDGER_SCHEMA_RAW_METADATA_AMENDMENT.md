# Prospective Ledger Raw-Metadata Amendment

- Previous schema: `PRIZE-SHARE-PROSPECTIVE-LEDGER-1.0`
- New schema: `PRIZE-SHARE-PROSPECTIVE-LEDGER-1.1`
- Scope: raw metadata only.
- Reason: the signal-blind collector must persist a deterministic selected-record hash and collector version in every append-only row.
- Added fields: `source_record_sha256`, `collector_version`.
- Predictor, derived signal, model, threshold, and outcome-analysis fields added: `0`.
- Locked prospective protocol changed: `NO`.
- Backup: `v27_storage/experiments/prize_share_prospective_001_v1/PRIZE_SHARE_PROSPECTIVE_001_LEDGER_SCHEMA_PRE_SIDECAR_BACKUP.json`.


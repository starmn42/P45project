# P45 TRIO ORBIT PROSPECTIVE LOG SCHEMA 001

## Purpose

This schema adds prospective attribution records only. It does not alter the locked TRIO ORBIT V1 fixed or linked selection rules, KTS schedule, reset rules, or success definition.

## One row per target round

| field | definition |
|---|---|
| target_round | Evaluated draw number R |
| source_round | R-1 |
| fixed_A, fixed_B, fixed_C | Three fixed V1 TRIOs, stored before R outcome |
| linked_A, linked_B, linked_C | Three linked V1 TRIOs, stored before R outcome |
| linked_anchor_A/B/C | Assigned R-1 anchor for each linked TRIO |
| common_count | Size of fixed/linked TRIO intersection, 0..3 |
| common_trios | Exact common TRIO identities |
| fixed_only_trios | Fixed minus linked; REMOVED_BY_LINK |
| linked_only_trios | Linked minus fixed; ADDED_BY_LINK |
| fixed_hits_A/B/C | Outcome hits 0/1/2/3 for each fixed TRIO |
| linked_hits_A/B/C | Outcome hits 0/1/2/3 for each linked TRIO |
| fixed_success | At least one fixed exact3 |
| linked_success | At least one linked exact3 |
| fixed_only_exact3_contribution | Number of fixed-only exact3 TRIOs |
| linked_only_exact3_contribution | Number of linked-only exact3 TRIOs |
| fixed_only_exact2_contribution | Number of fixed-only exact2 TRIOs |
| linked_only_exact2_contribution | Number of linked-only exact2 TRIOs |
| linked_only_anchor_reappeared | Per linked-only TRIO, whether assigned anchor is in target MAIN6 |
| reset_before_selection | Whether linked orbit reset before selecting this round |
| selection_record_sha256 | Hash of the pre-outcome selection record |
| outcome_attached_at | Timestamp when outcome fields were appended |
| future_leakage_flag | Must be 0 |

## Integrity rules

- Store selection fields and `selection_record_sha256` before target outcome is attached.
- Exactly three distinct fixed and three distinct linked TRIOs are required.
- `fixed_only_count = linked_only_count = 3-common_count` must hold.
- Outcome attachment may populate hit and contribution fields only; it may not rewrite selections, anchors, or reset status.
- No field in this schema is a recommendation, gate, threshold, or rule-tuning input without a separately locked future protocol.

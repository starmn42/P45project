"""Standalone schema 274 for PAIR normalized storage and synthetic fixtures."""

SCHEMA_VERSION = 274

PAIR_SCHEMA_274 = r"""
PRAGMA foreign_keys = ON;

CREATE TABLE pair_run (
    pair_run_id TEXT PRIMARY KEY,
    run_class TEXT NOT NULL CHECK(run_class IN ('SYNTHETIC_TEST','DIAGNOSTIC','BACKTEST','LIVE_TEST','LIVE_OFFICIAL')),
    pair_rule_hash TEXT NOT NULL CHECK(length(pair_rule_hash)=64),
    source_snapshot_hash TEXT NOT NULL CHECK(length(source_snapshot_hash)=64),
    run_status TEXT NOT NULL CHECK(run_status IN ('CANDIDATE_ONLY','COMPLETE','FAILED_ROLLED_BACK')),
    created_at TEXT NOT NULL
);

CREATE TABLE pair_source_trio (
    trio_id TEXT PRIMARY KEY,
    pair_run_id TEXT NOT NULL REFERENCES pair_run(pair_run_id) ON DELETE RESTRICT,
    trio_key TEXT NOT NULL,
    n1 INTEGER NOT NULL CHECK(n1 BETWEEN 1 AND 45),
    n2 INTEGER NOT NULL CHECK(n2 BETWEEN 1 AND 45),
    n3 INTEGER NOT NULL CHECK(n3 BETWEEN 1 AND 45),
    trio_state TEXT NOT NULL CHECK(trio_state IN ('TRIO_PASS','TRIO_WEAKEN','TRIO_TEST')),
    trio_rule_signature TEXT NOT NULL CHECK(length(trio_rule_signature)=64),
    valid_for_pair INTEGER NOT NULL CHECK(valid_for_pair IN (0,1)),
    CHECK(n1<n2 AND n2<n3),
    UNIQUE(pair_run_id,trio_key)
);

CREATE TABLE pair_rule_signature (
    signature_id TEXT PRIMARY KEY,
    pair_run_id TEXT NOT NULL REFERENCES pair_run(pair_run_id) ON DELETE RESTRICT,
    signature_version TEXT NOT NULL,
    signature_payload_json TEXT NOT NULL,
    signature_sha256 TEXT NOT NULL CHECK(length(signature_sha256)=64),
    created_at TEXT NOT NULL,
    UNIQUE(pair_run_id,signature_sha256)
);

CREATE TABLE pair_candidate (
    pair_candidate_id TEXT PRIMARY KEY,
    pair_run_id TEXT NOT NULL REFERENCES pair_run(pair_run_id) ON DELETE RESTRICT,
    canonical_pair_key TEXT NOT NULL,
    signature_id TEXT NOT NULL REFERENCES pair_rule_signature(signature_id) ON DELETE RESTRICT,
    calculation_status TEXT NOT NULL CHECK(calculation_status IN ('CANDIDATE_ONLY','COMPLETE','SYSTEM_ERROR')),
    pair_state TEXT CHECK(pair_state IS NULL OR pair_state IN ('PAIR_READY','PAIR_TEST_READY','PAIR_RESEARCH_HOLD','PAIR_SYSTEM_HOLD')),
    selected INTEGER NOT NULL DEFAULT 0 CHECK(selected IN (0,1)),
    row_hash TEXT NOT NULL CHECK(length(row_hash)=64),
    created_at TEXT NOT NULL,
    UNIQUE(pair_run_id,canonical_pair_key)
);

CREATE TABLE pair_member (
    pair_candidate_id TEXT NOT NULL REFERENCES pair_candidate(pair_candidate_id) ON DELETE RESTRICT,
    member_slot TEXT NOT NULL CHECK(member_slot IN ('CANONICAL_LOWER','CANONICAL_UPPER')),
    trio_id TEXT NOT NULL REFERENCES pair_source_trio(trio_id) ON DELETE RESTRICT,
    trio_key TEXT NOT NULL,
    PRIMARY KEY(pair_candidate_id,member_slot),
    UNIQUE(pair_candidate_id,trio_id)
);

CREATE TABLE pair_unit_coverage (
    pair_candidate_id TEXT NOT NULL REFERENCES pair_candidate(pair_candidate_id) ON DELETE RESTRICT,
    unit_type TEXT NOT NULL CHECK(unit_type IN ('UNIT_3','UNIT_5','UNIT_9','UNIT_10','END_DIGIT')),
    raw_cells_json TEXT NOT NULL,
    complete_cell_count INTEGER NOT NULL CHECK(complete_cell_count BETWEEN 0 AND 6),
    support_cell_count INTEGER NOT NULL CHECK(support_cell_count BETWEEN 0 AND 6),
    conflict_cell_count INTEGER NOT NULL CHECK(conflict_cell_count BETWEEN 0 AND 6),
    role_diversity_count INTEGER NOT NULL CHECK(role_diversity_count>=0),
    shared_evidence_count INTEGER NOT NULL CHECK(shared_evidence_count>=0),
    coverage_hash TEXT NOT NULL CHECK(length(coverage_hash)=64),
    PRIMARY KEY(pair_candidate_id,unit_type)
);

CREATE TABLE pair_role_evidence (
    pair_role_evidence_id TEXT PRIMARY KEY,
    pair_candidate_id TEXT NOT NULL REFERENCES pair_candidate(pair_candidate_id) ON DELETE RESTRICT,
    unit_type TEXT NOT NULL,
    role_ids_json TEXT NOT NULL,
    evidence_ids_json TEXT NOT NULL,
    overlap_flag INTEGER NOT NULL CHECK(overlap_flag IN (0,1)),
    evidence_hash TEXT NOT NULL CHECK(length(evidence_hash)=64),
    UNIQUE(pair_candidate_id,unit_type,evidence_hash)
);

CREATE TABLE pair_gate_result (
    pair_candidate_id TEXT NOT NULL REFERENCES pair_candidate(pair_candidate_id) ON DELETE RESTRICT,
    gate_id TEXT NOT NULL,
    gate_order INTEGER NOT NULL CHECK(gate_order>=1),
    gate_status TEXT NOT NULL CHECK(gate_status IN ('PASS','FAIL','INCOMPLETE')),
    gate_input_json TEXT NOT NULL,
    reason_code TEXT,
    PRIMARY KEY(pair_candidate_id,gate_id),
    UNIQUE(pair_candidate_id,gate_order)
);

CREATE TABLE pair_period_metric (
    pair_period_metric_id TEXT PRIMARY KEY,
    signature_id TEXT NOT NULL REFERENCES pair_rule_signature(signature_id) ON DELETE RESTRICT,
    endpoint TEXT NOT NULL CHECK(endpoint IN ('INTEGRATED_PRIMARY','MAIN_PRIMARY','INTEGRATED_SUPPORT','MAIN_SUPPORT','SIMULTANEOUS_FAILURE')),
    period TEXT NOT NULL CHECK(period IN ('OVERALL','RECENT_100','RECENT_50','RECENT_20')),
    exposure_count INTEGER NOT NULL CHECK(exposure_count>=0),
    event_count INTEGER NOT NULL CHECK(event_count>=0),
    event_rate REAL,
    metric_hash TEXT NOT NULL CHECK(length(metric_hash)=64),
    UNIQUE(signature_id,endpoint,period)
);

CREATE TABLE pair_stat_test (
    pair_stat_test_id TEXT PRIMARY KEY,
    signature_id TEXT NOT NULL REFERENCES pair_rule_signature(signature_id) ON DELETE RESTRICT,
    endpoint TEXT NOT NULL,
    period TEXT NOT NULL,
    sample_count INTEGER NOT NULL CHECK(sample_count>=0),
    success_count INTEGER NOT NULL CHECK(success_count>=0),
    baseline REAL NOT NULL,
    wilson_low REAL NOT NULL,
    wilson_high REAL NOT NULL,
    p_upper REAL NOT NULL,
    p_lower REAL NOT NULL,
    evidence_state TEXT NOT NULL,
    UNIQUE(signature_id,endpoint,period)
);

CREATE TABLE pair_risk_metric (
    pair_candidate_id TEXT PRIMARY KEY REFERENCES pair_candidate(pair_candidate_id) ON DELETE RESTRICT,
    member_risk TEXT NOT NULL,
    pair_rule_risk TEXT NOT NULL,
    final_risk TEXT NOT NULL,
    reason_codes_json TEXT NOT NULL,
    risk_hash TEXT NOT NULL CHECK(length(risk_hash)=64)
);

CREATE TABLE pair_structure_metric (
    pair_structure_metric_id TEXT PRIMARY KEY,
    signature_id TEXT NOT NULL REFERENCES pair_rule_signature(signature_id) ON DELETE RESTRICT,
    endpoint_round INTEGER NOT NULL,
    comparison_endpoint_count INTEGER NOT NULL CHECK(comparison_endpoint_count>=0),
    adverse_metrics_json TEXT NOT NULL,
    percentile_json TEXT NOT NULL,
    structure_state TEXT NOT NULL,
    structure_hash TEXT NOT NULL CHECK(length(structure_hash)=64),
    UNIQUE(signature_id,endpoint_round)
);

CREATE TABLE pair_pareto_relation (
    pair_run_id TEXT NOT NULL REFERENCES pair_run(pair_run_id) ON DELETE RESTRICT,
    pair_a_id TEXT NOT NULL REFERENCES pair_candidate(pair_candidate_id) ON DELETE RESTRICT,
    pair_b_id TEXT NOT NULL REFERENCES pair_candidate(pair_candidate_id) ON DELETE RESTRICT,
    relation TEXT NOT NULL CHECK(relation IN ('A_DOMINATES','B_DOMINATES','NONDOMINATED','NOT_COMPARABLE')),
    vector_a_hash TEXT NOT NULL CHECK(length(vector_a_hash)=64),
    vector_b_hash TEXT NOT NULL CHECK(length(vector_b_hash)=64),
    PRIMARY KEY(pair_run_id,pair_a_id,pair_b_id),
    CHECK(pair_a_id<pair_b_id)
);

CREATE TABLE pair_walkforward_run (
    walkforward_run_id TEXT PRIMARY KEY,
    cache_key TEXT NOT NULL UNIQUE CHECK(length(cache_key)=64),
    start_round INTEGER NOT NULL,
    end_round INTEGER NOT NULL,
    run_status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE pair_walkforward_round (
    walkforward_run_id TEXT NOT NULL REFERENCES pair_walkforward_run(walkforward_run_id) ON DELETE RESTRICT,
    evaluation_round INTEGER NOT NULL,
    round_status TEXT NOT NULL,
    data_prefix_hash TEXT NOT NULL CHECK(length(data_prefix_hash)=64),
    prediction_hash_before_result TEXT CHECK(prediction_hash_before_result IS NULL OR length(prediction_hash_before_result)=64),
    candidate_count INTEGER NOT NULL DEFAULT 0,
    error_code TEXT,
    PRIMARY KEY(walkforward_run_id,evaluation_round)
);

CREATE TABLE pair_walkforward_exposure (
    exposure_id TEXT PRIMARY KEY,
    walkforward_run_id TEXT NOT NULL,
    evaluation_round INTEGER NOT NULL,
    signature_id TEXT NOT NULL REFERENCES pair_rule_signature(signature_id) ON DELETE RESTRICT,
    pair_candidate_id TEXT NOT NULL REFERENCES pair_candidate(pair_candidate_id) ON DELETE RESTRICT,
    exposure_type TEXT NOT NULL CHECK(exposure_type IN ('SELECTION_RULE','PAIR_IDENTITY')),
    representative INTEGER NOT NULL CHECK(representative IN (0,1)),
    FOREIGN KEY(walkforward_run_id,evaluation_round) REFERENCES pair_walkforward_round(walkforward_run_id,evaluation_round) ON DELETE RESTRICT
);

CREATE UNIQUE INDEX ux_pair_selection_exposure
ON pair_walkforward_exposure(walkforward_run_id,evaluation_round,signature_id)
WHERE exposure_type='SELECTION_RULE';
CREATE UNIQUE INDEX ux_pair_identity_exposure
ON pair_walkforward_exposure(walkforward_run_id,evaluation_round,pair_candidate_id)
WHERE exposure_type='PAIR_IDENTITY';

CREATE TABLE pair_walkforward_outcome (
    exposure_id TEXT PRIMARY KEY REFERENCES pair_walkforward_exposure(exposure_id) ON DELETE RESTRICT,
    a_integrated_hits INTEGER NOT NULL CHECK(a_integrated_hits BETWEEN 0 AND 3),
    b_integrated_hits INTEGER NOT NULL CHECK(b_integrated_hits BETWEEN 0 AND 3),
    a_main_hits INTEGER NOT NULL CHECK(a_main_hits BETWEEN 0 AND 3),
    b_main_hits INTEGER NOT NULL CHECK(b_main_hits BETWEEN 0 AND 3),
    a_bonus_assisted_triple INTEGER NOT NULL CHECK(a_bonus_assisted_triple IN (0,1)),
    b_bonus_assisted_triple INTEGER NOT NULL CHECK(b_bonus_assisted_triple IN (0,1)),
    integrated_category TEXT NOT NULL,
    main_category TEXT NOT NULL,
    outcome_hash TEXT NOT NULL CHECK(length(outcome_hash)=64)
);

CREATE TABLE pair_rank (
    pair_candidate_id TEXT PRIMARY KEY REFERENCES pair_candidate(pair_candidate_id) ON DELETE RESTRICT,
    pareto_state TEXT NOT NULL,
    tie_key_json TEXT NOT NULL,
    final_rank INTEGER NOT NULL CHECK(final_rank>=1),
    stable_key TEXT NOT NULL,
    rank_hash TEXT NOT NULL CHECK(length(rank_hash)=64),
    UNIQUE(stable_key)
);

CREATE INDEX idx_pair_candidate_run ON pair_candidate(pair_run_id,canonical_pair_key);
CREATE INDEX idx_pair_member_trio ON pair_member(trio_id);
CREATE INDEX idx_pair_signature_hash ON pair_rule_signature(signature_sha256);
"""

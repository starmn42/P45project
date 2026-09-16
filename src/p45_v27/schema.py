"""SQLite schemas for the isolated P45 v2.7 CORE and AUDIT stores."""

SCHEMA_VERSION = 273

CORE_TABLES = {
    "approval_record",
    "core_locked_result",
    "core_run",
    "engine_version_record",
    "number_ledger",
    "pair_ledger",
    "sealed_forward_ledger",
    "trio_ledger",
    "trio_unit_coverage",
    "trio_role_evidence",
    "trio_period_metric",
    "trio_stat_test",
    "trio_gate_result",
    "trio_pareto_relation",
    "trio_walkforward_run",
    "trio_walkforward_exposure",
    "trio_walkforward_outcome",
    "trio_risk_metric",
    "trio_structure_metric",
    "unit_definition",
    "unit_group",
    "unit_number_metric",
    "unit_relation",
    "unit_round_metric",
    "unit_structure_ledger",
}

AUDIT_TABLES = {"audit_run", "audit_chunk", "audit_cache"}

CORE_SCHEMA = r"""
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS engine_version_record (
    engine_version_id TEXT PRIMARY KEY,
    version_label TEXT NOT NULL UNIQUE,
    directive_sha256 TEXT NOT NULL CHECK(length(directive_sha256) = 64),
    implementation_order_sha256 TEXT NOT NULL CHECK(length(implementation_order_sha256) = 64),
    rule_hash TEXT NOT NULL CHECK(length(rule_hash) = 64),
    code_hash TEXT NOT NULL CHECK(length(code_hash) = 64),
    search_family_hash TEXT CHECK(search_family_hash IS NULL OR length(search_family_hash) = 64),
    effective_round INTEGER NOT NULL CHECK(effective_round >= 1),
    version_status TEXT NOT NULL CHECK(version_status IN ('DRAFT','APPROVED','ACTIVE','RETIRED')),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS approval_record (
    approval_id TEXT PRIMARY KEY,
    engine_version_id TEXT NOT NULL REFERENCES engine_version_record(engine_version_id),
    approval_type TEXT NOT NULL,
    approval_scope TEXT NOT NULL CHECK(approval_scope IN ('CORE_VERSION','AUDIT_CERTIFICATION','RULE_PROMOTION','EXPERIMENT_EXCEPTION')),
    approval_status TEXT NOT NULL CHECK(approval_status IN ('PENDING','APPROVED','REJECTED','SUPERSEDED')),
    effective_round INTEGER CHECK(effective_round IS NULL OR effective_round >= 1),
    approved_by TEXT,
    approval_reason TEXT,
    approved_at TEXT,
    data_hash TEXT CHECK(data_hash IS NULL OR length(data_hash) = 64),
    rule_hash TEXT NOT NULL CHECK(length(rule_hash) = 64),
    code_hash TEXT NOT NULL CHECK(length(code_hash) = 64),
    audit_result_hash TEXT CHECK(audit_result_hash IS NULL OR length(audit_result_hash) = 64),
    record_hash TEXT NOT NULL CHECK(length(record_hash) = 64),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS unit_definition (
    unit_definition_id TEXT PRIMARY KEY,
    engine_version_id TEXT NOT NULL REFERENCES engine_version_record(engine_version_id),
    unit_type TEXT NOT NULL CHECK(unit_type IN ('UNIT_3','UNIT_5','UNIT_9','UNIT_10','END_DIGIT')),
    group_count INTEGER NOT NULL CHECK(group_count > 0),
    correction_method TEXT NOT NULL,
    display_order INTEGER NOT NULL CHECK(display_order BETWEEN 1 AND 5),
    definition_status TEXT NOT NULL CHECK(definition_status IN ('ACTIVE','RETIRED')),
    definition_json TEXT NOT NULL,
    definition_hash TEXT NOT NULL CHECK(length(definition_hash) = 64),
    created_at TEXT NOT NULL,
    UNIQUE(engine_version_id, unit_type),
    UNIQUE(engine_version_id, display_order)
);

CREATE TABLE IF NOT EXISTS unit_group (
    unit_group_id TEXT PRIMARY KEY,
    unit_definition_id TEXT NOT NULL REFERENCES unit_definition(unit_definition_id),
    group_order INTEGER NOT NULL CHECK(group_order >= 1),
    group_label TEXT NOT NULL,
    group_size INTEGER NOT NULL CHECK(group_size > 0),
    start_number INTEGER CHECK(start_number IS NULL OR start_number BETWEEN 1 AND 45),
    end_number INTEGER CHECK(end_number IS NULL OR end_number BETWEEN 1 AND 45),
    member_numbers_json TEXT NOT NULL,
    group_status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(group_status IN ('ACTIVE','RETIRED')),
    group_hash TEXT NOT NULL CHECK(length(group_hash) = 64),
    created_at TEXT NOT NULL,
    UNIQUE(unit_definition_id, group_order),
    UNIQUE(unit_definition_id, group_label)
);

CREATE TABLE IF NOT EXISTS core_run (
    core_run_id TEXT PRIMARY KEY,
    engine_version_id TEXT NOT NULL REFERENCES engine_version_record(engine_version_id),
    analysis_round INTEGER NOT NULL CHECK(analysis_round >= 1),
    record_class TEXT NOT NULL CHECK(record_class IN ('BACKTEST','LIVE_TEST','LIVE_OFFICIAL','EXPERIMENT_EXCEPTION')),
    data_start_round INTEGER NOT NULL CHECK(data_start_round >= 1),
    data_end_round INTEGER NOT NULL CHECK(data_end_round = analysis_round - 1),
    source_namespace TEXT NOT NULL DEFAULT 'v27',
    raw_data_hash TEXT NOT NULL CHECK(length(raw_data_hash) = 64),
    normalized_data_hash TEXT NOT NULL CHECK(length(normalized_data_hash) = 64),
    rule_hash TEXT NOT NULL CHECK(length(rule_hash) = 64),
    code_hash TEXT NOT NULL CHECK(length(code_hash) = 64),
    search_family_hash TEXT CHECK(search_family_hash IS NULL OR length(search_family_hash) = 64),
    execution_hash TEXT CHECK(execution_hash IS NULL OR length(execution_hash) = 64),
    core_status TEXT NOT NULL CHECK(core_status IN ('RUNNING','CORE_SET_READY','CORE_TEST_SET_READY','CORE_RESEARCH_HOLD','CORE_SYSTEM_HOLD')),
    calculation_status TEXT NOT NULL CHECK(calculation_status IN ('PARTIAL','COMPLETE','SYSTEM_ERROR','DATA_ERROR','INSUFFICIENT_SAMPLE','NOT_APPLICABLE')),
    core_error_code TEXT,
    lock_status TEXT NOT NULL DEFAULT 'UNLOCKED' CHECK(lock_status IN ('UNLOCKED','LOCKED')),
    started_at TEXT NOT NULL,
    completed_at TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(engine_version_id, analysis_round, record_class, normalized_data_hash, rule_hash, code_hash)
);

CREATE TABLE IF NOT EXISTS unit_round_metric (
    unit_round_metric_id TEXT PRIMARY KEY,
    core_run_id TEXT NOT NULL REFERENCES core_run(core_run_id),
    unit_group_id TEXT NOT NULL REFERENCES unit_group(unit_group_id),
    source_round INTEGER NOT NULL CHECK(source_round >= 1),
    integrated_occupancy INTEGER NOT NULL CHECK(integrated_occupancy BETWEEN 0 AND 7),
    main_occupancy INTEGER NOT NULL CHECK(main_occupancy BETWEEN 0 AND 6),
    group_size INTEGER NOT NULL CHECK(group_size > 0),
    integrated_occupancy_rate REAL NOT NULL,
    main_occupancy_rate REAL NOT NULL,
    expected_integrated_count REAL NOT NULL,
    expected_main_count REAL NOT NULL,
    raw_integrated_deviation REAL NOT NULL,
    raw_main_deviation REAL NOT NULL,
    standardized_integrated_deviation REAL NOT NULL,
    standardized_main_deviation REAL NOT NULL,
    is_annihilated INTEGER NOT NULL CHECK(is_annihilated IN (0,1)),
    consecutive_annihilation_length INTEGER NOT NULL CHECK(consecutive_annihilation_length >= 0),
    next_return_count INTEGER CHECK(next_return_count IS NULL OR next_return_count >= 0),
    return_depth TEXT CHECK(return_depth IS NULL OR return_depth IN ('0','1','2','3_PLUS')),
    occupancy_vector_json TEXT NOT NULL,
    period_metrics_json TEXT NOT NULL,
    opposite_hypothesis_json TEXT NOT NULL,
    structure_collapse_json TEXT NOT NULL,
    unit_state TEXT NOT NULL CHECK(unit_state IN ('UNIT_PASS','UNIT_WEAKEN','UNIT_TEST','UNIT_HOLD','UNIT_FAIL','UNIT_SYSTEM_ERROR','UNIT_NOT_APPLICABLE')),
    calculation_status TEXT NOT NULL CHECK(calculation_status IN ('COMPLETE','PARTIAL','SYSTEM_ERROR','DATA_ERROR','INSUFFICIENT_SAMPLE','NOT_APPLICABLE')),
    data_hash TEXT NOT NULL CHECK(length(data_hash) = 64),
    vector_hash TEXT NOT NULL CHECK(length(vector_hash) = 64),
    row_hash TEXT NOT NULL CHECK(length(row_hash) = 64),
    execution_hash TEXT NOT NULL CHECK(length(execution_hash) = 64),
    created_at TEXT NOT NULL,
    UNIQUE(core_run_id, unit_group_id, source_round)
);

CREATE TABLE IF NOT EXISTS unit_number_metric (
    unit_number_metric_id TEXT PRIMARY KEY,
    core_run_id TEXT NOT NULL REFERENCES core_run(core_run_id),
    unit_definition_id TEXT NOT NULL REFERENCES unit_definition(unit_definition_id),
    number INTEGER NOT NULL CHECK(number BETWEEN 1 AND 45),
    sample_count INTEGER NOT NULL CHECK(sample_count >= 0),
    overall_metrics_json TEXT NOT NULL,
    recent_100_metrics_json TEXT NOT NULL,
    recent_50_metrics_json TEXT NOT NULL,
    recent_20_metrics_json TEXT NOT NULL,
    exact_vector_metrics_json TEXT NOT NULL,
    local_state_metrics_json TEXT NOT NULL,
    opposite_hypothesis_json TEXT NOT NULL,
    structure_collapse_json TEXT NOT NULL,
    sample_state TEXT NOT NULL CHECK(sample_state IN ('SUFFICIENT','BORDERLINE','INSUFFICIENT')),
    risk_state TEXT NOT NULL CHECK(risk_state IN ('LOW','MEDIUM','HIGH','NOT_APPLICABLE','INSUFFICIENT_SAMPLE','SYSTEM_ERROR')),
    unit_state TEXT NOT NULL CHECK(unit_state IN ('UNIT_PASS','UNIT_WEAKEN','UNIT_TEST','UNIT_HOLD','UNIT_FAIL','UNIT_SYSTEM_ERROR','UNIT_NOT_APPLICABLE')),
    primary_context TEXT NOT NULL,
    secondary_context TEXT NOT NULL,
    context_relation TEXT NOT NULL,
    bonus_dependence TEXT NOT NULL CHECK(bonus_dependence IN ('BONUS_DEPENDENCE_NONE','BONUS_DEPENDENCE_MEDIUM','BONUS_DEPENDENCE_HIGH')),
    opposite_risk TEXT NOT NULL CHECK(opposite_risk IN ('LOW','MEDIUM','HIGH')),
    structure_state TEXT NOT NULL CHECK(structure_state IN ('NORMAL','CAUTION','WARNING','SEVERE','INSUFFICIENT_SAMPLE')),
    first_limiting_gate TEXT,
    reason_codes_json TEXT NOT NULL,
    decision_json TEXT NOT NULL,
    decision_hash TEXT NOT NULL CHECK(length(decision_hash) = 64),
    data_hash TEXT NOT NULL CHECK(length(data_hash) = 64),
    metric_hash TEXT NOT NULL CHECK(length(metric_hash) = 64),
    execution_hash TEXT NOT NULL CHECK(length(execution_hash) = 64),
    created_at TEXT NOT NULL,
    UNIQUE(core_run_id, unit_definition_id, number)
);

CREATE TABLE IF NOT EXISTS unit_relation (
    unit_relation_id TEXT PRIMARY KEY,
    core_run_id TEXT NOT NULL REFERENCES core_run(core_run_id),
    entity_type TEXT NOT NULL CHECK(entity_type IN ('NUMBER','TRIO','PAIR')),
    entity_key TEXT NOT NULL,
    unit_state_vector_json TEXT NOT NULL,
    support_units_json TEXT NOT NULL,
    weaken_units_json TEXT NOT NULL,
    test_units_json TEXT NOT NULL,
    hold_units_json TEXT NOT NULL,
    fail_units_json TEXT NOT NULL,
    related_support_json TEXT NOT NULL,
    independent_context_json TEXT NOT NULL,
    conflict_raw_json TEXT NOT NULL,
    relation_state TEXT NOT NULL CHECK(relation_state IN ('UNIT_CONSENSUS_SUPPORT','UNIT_PARTIAL_SUPPORT','UNIT_CONFLICT','UNIT_NO_SUPPORT','UNIT_RELATION_INCOMPLETE')),
    pareto_state TEXT NOT NULL CHECK(pareto_state IN ('NON_DOMINATED','DOMINATED','NOT_COMPARABLE','NOT_APPLICABLE')),
    relation_hash TEXT NOT NULL CHECK(length(relation_hash) = 64),
    execution_hash TEXT NOT NULL CHECK(length(execution_hash) = 64),
    created_at TEXT NOT NULL,
    UNIQUE(core_run_id, entity_type, entity_key)
);

CREATE TABLE IF NOT EXISTS unit_structure_ledger (
    unit_structure_ledger_id TEXT PRIMARY KEY,
    core_run_id TEXT NOT NULL REFERENCES core_run(core_run_id),
    unit_definition_id TEXT NOT NULL REFERENCES unit_definition(unit_definition_id),
    analysis_round INTEGER NOT NULL CHECK(analysis_round >= 1),
    reference_start_round INTEGER NOT NULL CHECK(reference_start_round >= 1),
    reference_end_round INTEGER NOT NULL CHECK(reference_end_round < analysis_round),
    sample_count INTEGER NOT NULL CHECK(sample_count >= 0),
    metric_names_json TEXT NOT NULL,
    current_metrics_json TEXT NOT NULL,
    historical_distribution_json TEXT NOT NULL,
    metric_percentiles_json TEXT NOT NULL,
    overall_percentile REAL,
    structure_state TEXT NOT NULL CHECK(structure_state IN ('NORMAL','CAUTION','WARNING','SEVERE','INSUFFICIENT_SAMPLE')),
    decision_reason TEXT NOT NULL,
    data_hash TEXT NOT NULL CHECK(length(data_hash) = 64),
    calculation_hash TEXT NOT NULL CHECK(length(calculation_hash) = 64),
    created_at TEXT NOT NULL,
    UNIQUE(core_run_id, unit_definition_id)
);

CREATE TABLE IF NOT EXISTS number_ledger (
    core_run_id TEXT NOT NULL REFERENCES core_run(core_run_id),
    number INTEGER NOT NULL CHECK(number BETWEEN 1 AND 45),
    candidate_role TEXT NOT NULL,
    number_state TEXT NOT NULL CHECK(number_state IN ('NUMBER_PASS','NUMBER_WEAKEN','NUMBER_TEST','NUMBER_HOLD','NUMBER_FAIL','NUMBER_RETIRED')),
    elimination_stage TEXT NOT NULL CHECK(elimination_stage IN ('NUMBER_SELECTED_POOL','NUMBER_RUNNER_UP','NUMBER_MIDDLE_ELIMINATED','NUMBER_EARLY_ELIMINATED')),
    unit_state_vector_json TEXT NOT NULL,
    unit_relation_state TEXT NOT NULL,
    first_failed_gate TEXT,
    primary_reason_code TEXT NOT NULL,
    secondary_reason_codes_json TEXT NOT NULL,
    gate_input_values_json TEXT NOT NULL,
    gate_output_values_json TEXT NOT NULL,
    expected_gate_sequence_json TEXT NOT NULL,
    executed_gate_sequence_json TEXT NOT NULL,
    status_after_each_gate_json TEXT NOT NULL,
    tie_break_key_json TEXT NOT NULL,
    rank_before_tie_break INTEGER CHECK(rank_before_tie_break IS NULL OR rank_before_tie_break >= 1),
    rank_after_tie_break INTEGER CHECK(rank_after_tie_break IS NULL OR rank_after_tie_break >= 1),
    candidate_pool_type TEXT NOT NULL CHECK(candidate_pool_type IN ('CORE_PASS_POOL','EXPANDED_TEST_POOL','RESEARCH_HOLD','NOT_SELECTED')),
    return_roles_json TEXT NOT NULL,
    primary_return_role TEXT,
    nonreturn_role TEXT,
    role_signature_json TEXT NOT NULL,
    role_overlap_json TEXT NOT NULL,
    number_performance_context_json TEXT NOT NULL,
    secondary_contexts_json TEXT NOT NULL,
    number_bonus_dependence TEXT NOT NULL CHECK(number_bonus_dependence IN ('BONUS_DEPENDENCE_NONE','BONUS_DEPENDENCE_MEDIUM','BONUS_DEPENDENCE_HIGH')),
    number_opposite_risk TEXT NOT NULL CHECK(number_opposite_risk IN ('LOW','MEDIUM','HIGH')),
    number_structure_state TEXT NOT NULL CHECK(number_structure_state IN ('NORMAL','CAUTION','WARNING','SEVERE')),
    structure_insufficient_sample INTEGER NOT NULL CHECK(structure_insufficient_sample IN (0,1)),
    number_context_conflict TEXT NOT NULL CHECK(number_context_conflict IN ('NONE','MEDIUM','HIGH')),
    valid_test_status INTEGER NOT NULL CHECK(valid_test_status IN (0,1)),
    retired_reason TEXT,
    first_limited_gate TEXT,
    decision_hash TEXT NOT NULL CHECK(length(decision_hash) = 64),
    final_rank INTEGER CHECK(final_rank IS NULL OR final_rank >= 1),
    selected_pool INTEGER NOT NULL CHECK(selected_pool IN (0,1)),
    data_hash TEXT NOT NULL CHECK(length(data_hash) = 64),
    row_hash TEXT NOT NULL CHECK(length(row_hash) = 64),
    execution_hash TEXT NOT NULL CHECK(length(execution_hash) = 64),
    created_at TEXT NOT NULL,
    PRIMARY KEY(core_run_id, number)
);

CREATE TABLE IF NOT EXISTS trio_ledger (
    trio_id TEXT PRIMARY KEY,
    core_run_id TEXT NOT NULL REFERENCES core_run(core_run_id),
    n1 INTEGER NOT NULL CHECK(n1 BETWEEN 1 AND 45),
    n2 INTEGER NOT NULL CHECK(n2 BETWEEN 1 AND 45),
    n3 INTEGER NOT NULL CHECK(n3 BETWEEN 1 AND 45),
    trio_key TEXT NOT NULL,
    trio_state TEXT NOT NULL CHECK(trio_state IN ('TRIO_PASS','TRIO_WEAKEN','TRIO_TEST','TRIO_HOLD','TRIO_FAIL','TRIO_RETIRED')),
    calculation_status TEXT NOT NULL CHECK(calculation_status IN ('COMPLETE','INCOMPLETE','SYSTEM_ERROR')),
    system_error_code TEXT,
    candidate_pool_type TEXT NOT NULL,
    candidate_pool_hash TEXT NOT NULL CHECK(length(candidate_pool_hash)=64),
    number_ledger_snapshot_hash TEXT NOT NULL CHECK(length(number_ledger_snapshot_hash)=64),
    trio_rule_version TEXT NOT NULL,
    trio_rule_hash TEXT NOT NULL CHECK(length(trio_rule_hash)=64),
    trio_rule_signature TEXT NOT NULL CHECK(length(trio_rule_signature)=64),
    selection_rule_exposure_count INTEGER NOT NULL CHECK(selection_rule_exposure_count>=0),
    trio_identity_exposure_count INTEGER NOT NULL CHECK(trio_identity_exposure_count>=0),
    walkforward_run_id TEXT,
    bonus_dependency_state TEXT NOT NULL CHECK(bonus_dependency_state IN ('BONUS_DEPENDENCE_NONE','BONUS_DEPENDENCE_MEDIUM','BONUS_DEPENDENCE_HIGH')),
    member_opposite_risk TEXT NOT NULL CHECK(member_opposite_risk IN ('LOW','MEDIUM','HIGH')),
    trio_rule_opposite_risk TEXT NOT NULL CHECK(trio_rule_opposite_risk IN ('LOW','MEDIUM','HIGH')),
    member_structure_summary TEXT NOT NULL,
    trio_rule_structure_state TEXT NOT NULL,
    final_structure_state TEXT NOT NULL,
    recent_support_collapse_state TEXT NOT NULL,
    pareto_state TEXT NOT NULL CHECK(pareto_state IN ('UNIT_PARETO_NONDOMINATED','UNIT_PARETO_DOMINATED','NOT_COMPARABLE')),
    pareto_vector_hash TEXT NOT NULL CHECK(length(pareto_vector_hash)=64),
    valid_for_pair INTEGER NOT NULL CHECK(valid_for_pair IN (0,1)),
    pair_eligibility_reason TEXT NOT NULL,
    expected_gate_sequence_json TEXT NOT NULL,
    executed_gate_sequence_json TEXT NOT NULL,
    gate_order_hash TEXT NOT NULL CHECK(length(gate_order_hash)=64),
    prediction_hash_before_result TEXT CHECK(prediction_hash_before_result IS NULL OR length(prediction_hash_before_result)=64),
    decision_hash TEXT NOT NULL CHECK(length(decision_hash)=64),
    elimination_stage TEXT NOT NULL CHECK(elimination_stage IN ('TRIO_SELECTED_SET1','TRIO_SELECTED_SET2','TRIO_RUNNER_UP','TRIO_MIDDLE_ELIMINATED','TRIO_EARLY_ELIMINATED')),
    exposure_count INTEGER NOT NULL CHECK(exposure_count >= 0),
    integrated_3of3_count INTEGER NOT NULL CHECK(integrated_3of3_count >= 0),
    integrated_3of3_rate REAL,
    main_3of3_count INTEGER NOT NULL CHECK(main_3of3_count >= 0),
    main_3of3_rate REAL,
    integrated_2of3_count INTEGER NOT NULL CHECK(integrated_2of3_count >= 0),
    integrated_2of3_rate REAL,
    main_2of3_count INTEGER NOT NULL CHECK(main_2of3_count >= 0),
    main_2of3_rate REAL,
    integrated_1of3_count INTEGER NOT NULL CHECK(integrated_1of3_count >= 0),
    integrated_1of3_rate REAL,
    unit_coverage_matrix_json TEXT NOT NULL,
    gate_result_json TEXT NOT NULL,
    first_failed_gate TEXT,
    primary_reason_code TEXT NOT NULL,
    secondary_reason_codes_json TEXT NOT NULL,
    final_rank INTEGER CHECK(final_rank IS NULL OR final_rank >= 1),
    selected_set INTEGER CHECK(selected_set IS NULL OR selected_set IN (1,2)),
    data_hash TEXT NOT NULL CHECK(length(data_hash) = 64),
    row_hash TEXT NOT NULL CHECK(length(row_hash) = 64),
    execution_hash TEXT NOT NULL CHECK(length(execution_hash) = 64),
    created_at TEXT NOT NULL,
    CHECK(n1 < n2 AND n2 < n3),
    UNIQUE(core_run_id, n1, n2, n3),
    UNIQUE(core_run_id, trio_key)
);

CREATE TABLE IF NOT EXISTS trio_unit_coverage (
    trio_id TEXT NOT NULL REFERENCES trio_ledger(trio_id) ON DELETE RESTRICT,
    number INTEGER NOT NULL CHECK(number BETWEEN 1 AND 45), unit_type TEXT NOT NULL,
    cell_json TEXT NOT NULL, source_metric_hash TEXT NOT NULL CHECK(length(source_metric_hash)=64),
    PRIMARY KEY(trio_id,number,unit_type)
);
CREATE TABLE IF NOT EXISTS trio_role_evidence (
    trio_id TEXT NOT NULL REFERENCES trio_ledger(trio_id) ON DELETE RESTRICT,
    unit_type TEXT NOT NULL, diversity_state TEXT NOT NULL, overlap_state TEXT NOT NULL,
    evidence_json TEXT NOT NULL, evidence_hash TEXT NOT NULL CHECK(length(evidence_hash)=64),
    PRIMARY KEY(trio_id,unit_type)
);
CREATE TABLE IF NOT EXISTS trio_period_metric (
    trio_id TEXT NOT NULL REFERENCES trio_ledger(trio_id) ON DELETE RESTRICT,
    scope TEXT NOT NULL CHECK(scope IN ('INTEGRATED','MAIN')),
    hit_type TEXT NOT NULL CHECK(hit_type IN ('EXACT_3_OF_3','EXACT_2_OF_3','EXACT_1_OF_3','EXACT_0_OF_3')),
    period TEXT NOT NULL CHECK(period IN ('OVERALL','FIRST_HALF','SECOND_HALF','RECENT_100','RECENT_50','RECENT_20')),
    sample_count INTEGER NOT NULL, hit_count INTEGER NOT NULL, rate REAL, metric_json TEXT NOT NULL,
    PRIMARY KEY(trio_id,scope,hit_type,period)
);
CREATE TABLE IF NOT EXISTS trio_stat_test (
    trio_id TEXT NOT NULL REFERENCES trio_ledger(trio_id) ON DELETE RESTRICT,
    scope TEXT NOT NULL, hit_type TEXT NOT NULL, sample_count INTEGER NOT NULL, success_count INTEGER NOT NULL,
    rate REAL NOT NULL, p0 REAL NOT NULL, wilson_low REAL NOT NULL, wilson_high REAL NOT NULL,
    p_upper REAL NOT NULL, p_lower REAL NOT NULL, evidence_label TEXT NOT NULL,
    PRIMARY KEY(trio_id,scope,hit_type)
);
CREATE TABLE IF NOT EXISTS trio_gate_result (
    trio_id TEXT NOT NULL REFERENCES trio_ledger(trio_id) ON DELETE RESTRICT,
    gate_order INTEGER NOT NULL, gate_code TEXT NOT NULL, gate_status TEXT NOT NULL,
    input_json TEXT NOT NULL, reason_code TEXT, PRIMARY KEY(trio_id,gate_order), UNIQUE(trio_id,gate_code)
);
CREATE TABLE IF NOT EXISTS trio_pareto_relation (
    core_run_id TEXT NOT NULL REFERENCES core_run(core_run_id), dominator_trio_id TEXT NOT NULL REFERENCES trio_ledger(trio_id),
    dominated_trio_id TEXT NOT NULL REFERENCES trio_ledger(trio_id), relation_hash TEXT NOT NULL CHECK(length(relation_hash)=64),
    PRIMARY KEY(core_run_id,dominator_trio_id,dominated_trio_id)
);
CREATE TABLE IF NOT EXISTS trio_walkforward_run (
    walkforward_run_id TEXT PRIMARY KEY, engine_version_id TEXT NOT NULL REFERENCES engine_version_record(engine_version_id),
    analysis_round INTEGER NOT NULL, first_eligible_round INTEGER, last_evaluated_round INTEGER,
    rule_hash TEXT NOT NULL CHECK(length(rule_hash)=64), future_block_status TEXT NOT NULL, run_hash TEXT NOT NULL CHECK(length(run_hash)=64), created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS trio_walkforward_exposure (
    exposure_id TEXT PRIMARY KEY, walkforward_run_id TEXT NOT NULL REFERENCES trio_walkforward_run(walkforward_run_id),
    outer_round INTEGER NOT NULL, trio_rule_signature TEXT NOT NULL, representative_trio_key TEXT NOT NULL,
    candidate_pool_hash TEXT NOT NULL CHECK(length(candidate_pool_hash)=64), prediction_hash_before_result TEXT NOT NULL CHECK(length(prediction_hash_before_result)=64),
    UNIQUE(walkforward_run_id,outer_round,trio_rule_signature)
);
CREATE TABLE IF NOT EXISTS trio_walkforward_outcome (
    exposure_id TEXT PRIMARY KEY REFERENCES trio_walkforward_exposure(exposure_id), integrated_hits INTEGER NOT NULL CHECK(integrated_hits BETWEEN 0 AND 3),
    main_hits INTEGER NOT NULL CHECK(main_hits BETWEEN 0 AND 3), bonus_hit INTEGER NOT NULL CHECK(bonus_hit IN (0,1)), outcome_hash TEXT NOT NULL CHECK(length(outcome_hash)=64)
);
CREATE TABLE IF NOT EXISTS trio_risk_metric (
    trio_id TEXT PRIMARY KEY REFERENCES trio_ledger(trio_id), risk_json TEXT NOT NULL, risk_hash TEXT NOT NULL CHECK(length(risk_hash)=64)
);
CREATE TABLE IF NOT EXISTS trio_structure_metric (
    trio_id TEXT NOT NULL REFERENCES trio_ledger(trio_id), metric_code TEXT NOT NULL, current_value REAL,
    sample_count INTEGER NOT NULL, percentile REAL, structure_state TEXT NOT NULL, metric_json TEXT NOT NULL,
    metric_hash TEXT NOT NULL CHECK(length(metric_hash)=64), PRIMARY KEY(trio_id,metric_code)
);

CREATE TABLE IF NOT EXISTS pair_ledger (
    pair_id TEXT PRIMARY KEY,
    core_run_id TEXT NOT NULL REFERENCES core_run(core_run_id),
    trio_a_id TEXT NOT NULL REFERENCES trio_ledger(trio_id),
    trio_b_id TEXT NOT NULL REFERENCES trio_ledger(trio_id),
    pair_state TEXT NOT NULL CHECK(pair_state IN ('PAIR_READY','PAIR_TEST_READY','PAIR_RESEARCH_HOLD','PAIR_SYSTEM_HOLD')),
    elimination_stage TEXT NOT NULL CHECK(elimination_stage IN ('PAIR_SELECTED','PAIR_RUNNER_UP','PAIR_ELIMINATED')),
    non_overlap_verified INTEGER NOT NULL CHECK(non_overlap_verified IN (0,1)),
    exposure_count INTEGER NOT NULL CHECK(exposure_count >= 0),
    at_least_one_integrated_3of3_count INTEGER NOT NULL CHECK(at_least_one_integrated_3of3_count >= 0),
    at_least_one_integrated_3of3_rate REAL,
    at_least_one_main_3of3_count INTEGER NOT NULL CHECK(at_least_one_main_3of3_count >= 0),
    at_least_one_main_3of3_rate REAL,
    both_integrated_2of3_count INTEGER NOT NULL CHECK(both_integrated_2of3_count >= 0),
    both_integrated_2of3_rate REAL,
    simultaneous_failure_count INTEGER NOT NULL CHECK(simultaneous_failure_count >= 0),
    simultaneous_failure_rate REAL,
    pair_unit_coverage_matrix_json TEXT NOT NULL,
    gate_result_json TEXT NOT NULL,
    first_failed_gate TEXT,
    primary_reason_code TEXT NOT NULL,
    secondary_reason_codes_json TEXT NOT NULL,
    final_rank INTEGER CHECK(final_rank IS NULL OR final_rank >= 1),
    selected INTEGER NOT NULL CHECK(selected IN (0,1)),
    data_hash TEXT NOT NULL CHECK(length(data_hash) = 64),
    row_hash TEXT NOT NULL CHECK(length(row_hash) = 64),
    execution_hash TEXT NOT NULL CHECK(length(execution_hash) = 64),
    created_at TEXT NOT NULL,
    CHECK(trio_a_id < trio_b_id),
    UNIQUE(core_run_id, trio_a_id, trio_b_id)
);

CREATE TABLE IF NOT EXISTS core_locked_result (
    core_locked_result_id TEXT PRIMARY KEY,
    core_run_id TEXT NOT NULL UNIQUE REFERENCES core_run(core_run_id),
    engine_version_id TEXT NOT NULL REFERENCES engine_version_record(engine_version_id),
    analysis_round INTEGER NOT NULL CHECK(analysis_round >= 1),
    record_class TEXT NOT NULL CHECK(record_class IN ('BACKTEST','LIVE_TEST','LIVE_OFFICIAL','EXPERIMENT_EXCEPTION')),
    core_status TEXT NOT NULL CHECK(core_status IN ('CORE_SET_READY','CORE_TEST_SET_READY','CORE_RESEARCH_HOLD','CORE_SYSTEM_HOLD')),
    selected_pair_id TEXT REFERENCES pair_ledger(pair_id),
    set1_n1 INTEGER CHECK(set1_n1 BETWEEN 1 AND 45),
    set1_n2 INTEGER CHECK(set1_n2 BETWEEN 1 AND 45),
    set1_n3 INTEGER CHECK(set1_n3 BETWEEN 1 AND 45),
    set2_n1 INTEGER CHECK(set2_n1 BETWEEN 1 AND 45),
    set2_n2 INTEGER CHECK(set2_n2 BETWEEN 1 AND 45),
    set2_n3 INTEGER CHECK(set2_n3 BETWEEN 1 AND 45),
    audit_status_at_lock TEXT NOT NULL DEFAULT 'AUDIT_NOT_RUN' CHECK(audit_status_at_lock IN ('AUDIT_NOT_RUN','AUDIT_PENDING','AUDIT_RUNNING','AUDIT_PASS','AUDIT_BORDERLINE','AUDIT_FAIL','AUDIT_INCOMPLETE','AUDIT_INVALIDATED')),
    certification_at_lock TEXT NOT NULL DEFAULT 'EXPLORATORY' CHECK(certification_at_lock IN ('EXPLORATORY','TESTED','VALIDATED','CERTIFIED')),
    lock_status TEXT NOT NULL DEFAULT 'LOCKED' CHECK(lock_status = 'LOCKED'),
    core_result_hash TEXT NOT NULL CHECK(length(core_result_hash) = 64),
    report_hash TEXT NOT NULL CHECK(length(report_hash) = 64),
    manifest_hash TEXT NOT NULL CHECK(length(manifest_hash) = 64),
    previous_lock_hash TEXT CHECK(previous_lock_hash IS NULL OR length(previous_lock_hash) = 64),
    locked_at TEXT NOT NULL,
    CHECK(
      core_status IN ('CORE_RESEARCH_HOLD','CORE_SYSTEM_HOLD') OR
      (set1_n1 < set1_n2 AND set1_n2 < set1_n3 AND set2_n1 < set2_n2 AND set2_n2 < set2_n3 AND
       set1_n1 NOT IN (set2_n1,set2_n2,set2_n3) AND set1_n2 NOT IN (set2_n1,set2_n2,set2_n3) AND
       set1_n3 NOT IN (set2_n1,set2_n2,set2_n3))
    ),
    UNIQUE(engine_version_id, analysis_round, record_class, core_result_hash)
);

CREATE TABLE IF NOT EXISTS sealed_forward_ledger (
    sealed_forward_id TEXT PRIMARY KEY,
    engine_version_id TEXT NOT NULL REFERENCES engine_version_record(engine_version_id),
    core_run_id TEXT NOT NULL REFERENCES core_run(core_run_id),
    core_locked_result_id TEXT NOT NULL REFERENCES core_locked_result(core_locked_result_id),
    analysis_round INTEGER NOT NULL CHECK(analysis_round >= 1),
    entry_phase TEXT NOT NULL CHECK(entry_phase IN ('PRE_RESULT','POST_RESULT')),
    sealed_stage TEXT NOT NULL CHECK(sealed_stage IN ('SEALED_ACCUMULATING','SEALED_REVIEW','SEALED_MATURE')),
    payload_json TEXT NOT NULL,
    previous_entry_hash TEXT CHECK(previous_entry_hash IS NULL OR length(previous_entry_hash) = 64),
    entry_hash TEXT NOT NULL CHECK(length(entry_hash) = 64),
    created_at TEXT NOT NULL,
    UNIQUE(engine_version_id, analysis_round, entry_phase)
);

CREATE INDEX IF NOT EXISTS idx_approval_version_round ON approval_record(engine_version_id, effective_round, approval_status);
CREATE INDEX IF NOT EXISTS idx_core_version_round_class ON core_run(engine_version_id, analysis_round, record_class);
CREATE INDEX IF NOT EXISTS idx_core_status ON core_run(core_status, lock_status);
CREATE INDEX IF NOT EXISTS idx_unit_round_run_group ON unit_round_metric(core_run_id, unit_group_id, source_round);
CREATE INDEX IF NOT EXISTS idx_unit_number_run_number ON unit_number_metric(core_run_id, number);
CREATE INDEX IF NOT EXISTS idx_unit_number_state ON unit_number_metric(core_run_id, unit_state);
CREATE INDEX IF NOT EXISTS idx_relation_entity ON unit_relation(core_run_id, entity_type, entity_key);
CREATE INDEX IF NOT EXISTS idx_relation_state ON unit_relation(core_run_id, relation_state, pareto_state);
CREATE INDEX IF NOT EXISTS idx_structure_run_state ON unit_structure_ledger(core_run_id, structure_state);
CREATE INDEX IF NOT EXISTS idx_number_state_rank ON number_ledger(core_run_id, number_state, final_rank);
CREATE INDEX IF NOT EXISTS idx_trio_state_rank ON trio_ledger(core_run_id, trio_state, final_rank);
CREATE INDEX IF NOT EXISTS idx_pair_state_rank ON pair_ledger(core_run_id, pair_state, final_rank);
CREATE INDEX IF NOT EXISTS idx_pair_selected ON pair_ledger(core_run_id, selected) WHERE selected = 1;
CREATE INDEX IF NOT EXISTS idx_locked_version_round ON core_locked_result(engine_version_id, analysis_round, record_class);
CREATE INDEX IF NOT EXISTS idx_sealed_version_round ON sealed_forward_ledger(engine_version_id, analysis_round, entry_phase);

CREATE TRIGGER IF NOT EXISTS immutable_locked_result_update
BEFORE UPDATE ON core_locked_result BEGIN SELECT RAISE(ABORT, 'core_locked_result is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_locked_result_delete
BEFORE DELETE ON core_locked_result BEGIN SELECT RAISE(ABORT, 'core_locked_result is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_sealed_update
BEFORE UPDATE ON sealed_forward_ledger BEGIN SELECT RAISE(ABORT, 'sealed_forward_ledger is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_sealed_delete
BEFORE DELETE ON sealed_forward_ledger BEGIN SELECT RAISE(ABORT, 'sealed_forward_ledger is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_approved_version_update
BEFORE UPDATE ON engine_version_record WHEN OLD.version_status IN ('APPROVED','ACTIVE','RETIRED')
BEGIN SELECT RAISE(ABORT, 'approved engine version is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_approved_version_delete
BEFORE DELETE ON engine_version_record WHEN OLD.version_status IN ('APPROVED','ACTIVE','RETIRED')
BEGIN SELECT RAISE(ABORT, 'approved engine version is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_decided_approval_update
BEFORE UPDATE ON approval_record WHEN OLD.approval_status <> 'PENDING'
BEGIN SELECT RAISE(ABORT, 'decided approval is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_decided_approval_delete
BEFORE DELETE ON approval_record WHEN OLD.approval_status <> 'PENDING'
BEGIN SELECT RAISE(ABORT, 'decided approval is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_locked_core_run_update
BEFORE UPDATE ON core_run WHEN OLD.lock_status = 'LOCKED'
BEGIN SELECT RAISE(ABORT, 'locked core_run is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_locked_core_run_delete
BEFORE DELETE ON core_run WHEN OLD.lock_status = 'LOCKED'
BEGIN SELECT RAISE(ABORT, 'locked core_run is immutable'); END;
CREATE TRIGGER IF NOT EXISTS require_locked_core_before_result
BEFORE INSERT ON core_locked_result
WHEN (SELECT lock_status FROM core_run WHERE core_run_id = NEW.core_run_id) <> 'LOCKED'
BEGIN SELECT RAISE(ABORT, 'core_run must be locked before core_locked_result insert'); END;
CREATE TRIGGER IF NOT EXISTS pair_trios_same_run
BEFORE INSERT ON pair_ledger
WHEN (SELECT core_run_id FROM trio_ledger WHERE trio_id = NEW.trio_a_id) <> NEW.core_run_id
  OR (SELECT core_run_id FROM trio_ledger WHERE trio_id = NEW.trio_b_id) <> NEW.core_run_id
BEGIN SELECT RAISE(ABORT, 'pair trios must belong to the same core_run'); END;
"""

for _table in (
    "unit_round_metric", "unit_number_metric", "unit_relation", "number_ledger",
    "trio_ledger", "pair_ledger",
):
    CORE_SCHEMA += f"""
CREATE TRIGGER IF NOT EXISTS immutable_{_table}_update
BEFORE UPDATE ON {_table}
WHEN EXISTS (SELECT 1 FROM core_run WHERE core_run_id = OLD.core_run_id AND lock_status = 'LOCKED')
BEGIN SELECT RAISE(ABORT, 'locked CORE child row is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_{_table}_delete
BEFORE DELETE ON {_table}
WHEN EXISTS (SELECT 1 FROM core_run WHERE core_run_id = OLD.core_run_id AND lock_status = 'LOCKED')
BEGIN SELECT RAISE(ABORT, 'locked CORE child row is immutable'); END;
"""

AUDIT_SCHEMA = r"""
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS audit_run (
    audit_run_id TEXT PRIMARY KEY,
    engine_version_id TEXT NOT NULL,
    core_run_id TEXT NOT NULL,
    core_result_hash TEXT NOT NULL CHECK(length(core_result_hash) = 64),
    normalized_data_hash TEXT NOT NULL CHECK(length(normalized_data_hash) = 64),
    rule_hash TEXT NOT NULL CHECK(length(rule_hash) = 64),
    code_hash TEXT NOT NULL CHECK(length(code_hash) = 64),
    search_family_hash TEXT NOT NULL CHECK(length(search_family_hash) = 64),
    generator_id TEXT NOT NULL,
    seed_root TEXT NOT NULL CHECK(length(seed_root) = 64),
    audit_kind TEXT NOT NULL CHECK(audit_kind IN ('DEVELOPMENT_1K','TEST_10K','CERTIFICATION_50K','STABILITY','PLACEBO','NESTED_WALK_FORWARD')),
    target_iterations INTEGER NOT NULL CHECK(target_iterations >= 0),
    completed_iterations INTEGER NOT NULL DEFAULT 0 CHECK(completed_iterations >= 0 AND completed_iterations <= target_iterations),
    audit_status TEXT NOT NULL CHECK(audit_status IN ('AUDIT_NOT_RUN','AUDIT_PENDING','AUDIT_RUNNING','AUDIT_PASS','AUDIT_BORDERLINE','AUDIT_FAIL','AUDIT_INCOMPLETE','AUDIT_INVALIDATED')),
    certification_level TEXT NOT NULL CHECK(certification_level IN ('EXPLORATORY','TESTED','VALIDATED','CERTIFIED')),
    iid_adjusted_p REAL,
    permutation_adjusted_p REAL,
    conservative_adjusted_p REAL,
    result_hash TEXT CHECK(result_hash IS NULL OR length(result_hash) = 64),
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_chunk (
    audit_chunk_id TEXT PRIMARY KEY,
    audit_run_id TEXT NOT NULL REFERENCES audit_run(audit_run_id),
    null_type TEXT NOT NULL CHECK(null_type IN ('IID_SYNTHETIC_NULL','ROUND_ORDER_PERMUTATION_NULL','STABILITY','PLACEBO','NESTED_WALK_FORWARD')),
    iteration_start INTEGER NOT NULL CHECK(iteration_start >= 0),
    iteration_end INTEGER NOT NULL CHECK(iteration_end > iteration_start),
    worker_id TEXT,
    chunk_status TEXT NOT NULL CHECK(chunk_status IN ('PENDING','RUNNING','COMPLETE','FAILED')),
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK(attempt_count >= 0),
    result_path TEXT,
    result_hash TEXT CHECK(result_hash IS NULL OR length(result_hash) = 64),
    distribution_hash TEXT CHECK(distribution_hash IS NULL OR length(distribution_hash) = 64),
    summary_json TEXT,
    error_text TEXT,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(audit_run_id, null_type, iteration_start, iteration_end)
);

CREATE TABLE IF NOT EXISTS audit_cache (
    audit_cache_id TEXT PRIMARY KEY,
    audit_run_id TEXT NOT NULL REFERENCES audit_run(audit_run_id),
    parent_cache_id TEXT REFERENCES audit_cache(audit_cache_id),
    cache_key TEXT NOT NULL CHECK(length(cache_key) = 64),
    null_type TEXT NOT NULL CHECK(null_type IN ('IID_SYNTHETIC_NULL','ROUND_ORDER_PERMUTATION_NULL')),
    completed_iterations INTEGER NOT NULL CHECK(completed_iterations >= 0),
    completed_ranges_json TEXT NOT NULL,
    distribution_path TEXT NOT NULL,
    distribution_hash TEXT NOT NULL CHECK(length(distribution_hash) = 64),
    cache_status TEXT NOT NULL CHECK(cache_status IN ('COMPLETE','INVALIDATED')),
    snapshot_hash TEXT NOT NULL CHECK(length(snapshot_hash) = 64),
    created_at TEXT NOT NULL,
    UNIQUE(cache_key, null_type, completed_iterations)
);

CREATE INDEX IF NOT EXISTS idx_audit_core ON audit_run(core_run_id, core_result_hash);
CREATE INDEX IF NOT EXISTS idx_audit_status ON audit_run(audit_status, certification_level);
CREATE INDEX IF NOT EXISTS idx_chunk_status_range ON audit_chunk(audit_run_id, chunk_status, null_type, iteration_start);
CREATE INDEX IF NOT EXISTS idx_cache_lookup ON audit_cache(cache_key, null_type, completed_iterations);

CREATE TRIGGER IF NOT EXISTS immutable_terminal_audit_update
BEFORE UPDATE ON audit_run WHEN OLD.audit_status IN ('AUDIT_PASS','AUDIT_BORDERLINE','AUDIT_FAIL','AUDIT_INVALIDATED')
BEGIN SELECT RAISE(ABORT, 'terminal audit_run is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_terminal_audit_delete
BEFORE DELETE ON audit_run WHEN OLD.audit_status IN ('AUDIT_PASS','AUDIT_BORDERLINE','AUDIT_FAIL','AUDIT_INVALIDATED')
BEGIN SELECT RAISE(ABORT, 'terminal audit_run is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_complete_chunk_update
BEFORE UPDATE ON audit_chunk WHEN OLD.chunk_status = 'COMPLETE'
BEGIN SELECT RAISE(ABORT, 'completed audit_chunk is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_complete_chunk_delete
BEFORE DELETE ON audit_chunk WHEN OLD.chunk_status = 'COMPLETE'
BEGIN SELECT RAISE(ABORT, 'completed audit_chunk is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_cache_update
BEFORE UPDATE ON audit_cache BEGIN SELECT RAISE(ABORT, 'audit_cache snapshot is immutable'); END;
CREATE TRIGGER IF NOT EXISTS immutable_cache_delete
BEFORE DELETE ON audit_cache BEGIN SELECT RAISE(ABORT, 'audit_cache snapshot is immutable'); END;
"""

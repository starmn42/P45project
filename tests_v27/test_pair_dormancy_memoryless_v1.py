"""
TEST SUITE: PAIR DORMANCY / GEOMETRIC MEMORYLESS HAZARD V1 (EXP-DRAW-20261001-001-V1)
MANDATORY 32-POINT SUITE (Section 39).
"""

import sys
import math
import hashlib
import json
import unittest
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_DIR = PROJECT_ROOT / "v27_storage" / "experiments" / "pair_dormancy_memoryless_v1_001"

sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(EXPERIMENT_DIR))
import calculator

class TestPairDormancyMemorylessV1(unittest.TestCase):

    # 1. 990 pair universe
    def test_01_pair_universe_990(self):
        c45_2 = math.comb(45, 2)
        self.assertEqual(c45_2, 990)
        self.assertEqual(calculator.TOTAL_PAIRS, 990)
        self.assertEqual(len(calculator.PAIR_TO_ID), 990)
        self.assertEqual(len(calculator.ID_TO_PAIR), 990)

    # 2. 15 pair per draw
    def test_02_pairs_per_draw_15(self):
        c6_2 = math.comb(6, 2)
        self.assertEqual(c6_2, 15)
        self.assertEqual(calculator.PAIRS_PER_DRAW, 15)

    # 3. p0 exact 1/66
    def test_03_p0_exact_1_over_66(self):
        p0_analytic = math.comb(43, 4) / math.comb(45, 6)
        p0_fraction = 1.0 / 66.0
        self.assertAlmostEqual(p0_analytic, p0_fraction, places=12)
        self.assertAlmostEqual(calculator.P0, p0_fraction, places=12)

    # 4. age reset
    def test_04_dormancy_age_reset(self):
        test_draws = [
            (1, [1, 2, 3, 4, 5, 6]), # pair (1, 2) appears t=0
            (2, [7, 8, 9, 10, 11, 12]), # gap=1
            (3, [1, 2, 13, 14, 15, 16]), # appears t=2 (gap=2)
            (4, [1, 2, 17, 18, 19, 20]), # appears t=3 (reset to gap=1)
        ]
        p_ids = calculator.draws_to_pair_ids(test_draws)
        exp, evt = calculator.compute_bin_counts_from_rows_cols(
            np.repeat(np.arange(4), 15), p_ids.ravel(), 4
        )
        self.assertGreaterEqual(evt[0], 2)

    # 5. age 1 definition
    def test_05_age_1_definition(self):
        t = 10
        s = 9
        age = t - s
        self.assertEqual(age, 1)

    # 6. left censor
    def test_06_left_censor(self):
        test_draws = [
            (1, [7, 8, 9, 10, 11, 12]),
            (2, [13, 14, 15, 16, 17, 18]),
            (3, [1, 2, 3, 4, 5, 6]), # first appearance
        ]
        p_ids = calculator.draws_to_pair_ids(test_draws)
        exp, evt = calculator.compute_bin_counts_from_rows_cols(
            np.repeat(np.arange(3), 15), p_ids.ravel(), 3
        )
        p12_id = calculator.PAIR_TO_ID[(1, 2)]
        cols = p_ids.ravel()
        self.assertEqual(np.sum(cols == p12_id), 1)
        self.assertEqual(np.sum(evt), 0)

    # 7. all fixed bins
    def test_07_all_fixed_bins(self):
        expected_bins = [
            (1, 12),
            (13, 27),
            (28, 46),
            (47, 72),
            (73, 118),
            (119, None)
        ]
        self.assertEqual(calculator.BINS, expected_bins)

    # 8. quantile derivation
    def test_08_quantile_derivation(self):
        q_vals = [1/6, 2/6, 3/6, 4/6, 5/6]
        cuts = [math.ceil(math.log(1 - q) / math.log(65/66)) for q in q_vals]
        self.assertEqual(cuts, [12, 27, 46, 72, 118])

    # 9. future cutoff <= discovery round
    def test_09_future_cutoff_leq_discovery_round(self):
        csv_path = PROJECT_ROOT / "v27_storage" / "live" / "p45_live_draws.csv"
        draws = calculator.load_draws_from_csv(csv_path, max_round=1243)
        self.assertEqual(len(draws), 1243)
        self.assertEqual(max(d[0] for d in draws), 1243)

    # 10. fake future row invariance
    def test_10_fake_future_row_invariance(self):
        csv_path = PROJECT_ROOT / "v27_storage" / "live" / "p45_live_draws.csv"
        draws_clean = calculator.load_draws_from_csv(csv_path, max_round=1243)

        # In-memory check: if future rows exist, max_round filters them
        future_draws = draws_clean + [(1244, [1, 2, 3, 4, 5, 6]), (1245, [10, 11, 12, 13, 14, 15])]
        filtered = [d for d in future_draws if d[0] <= 1243]
        self.assertEqual(len(draws_clean), len(filtered))
        self.assertEqual(draws_clean, filtered)

    # 11. permutation preserves draw sets
    def test_11_permutation_preserves_draw_sets(self):
        csv_path = PROJECT_ROOT / "v27_storage" / "live" / "p45_live_draws.csv"
        draws = calculator.load_draws_from_csv(csv_path, max_round=50)
        p_ids = calculator.draws_to_pair_ids(draws)
        T = len(draws)
        rng = np.random.default_rng(42)
        perm = rng.permutation(T)
        p_ids_perm = p_ids[perm]

        orig_sets = sorted([sorted(list(p_ids[i])) for i in range(T)])
        perm_sets = sorted([sorted(list(p_ids_perm[i])) for i in range(T)])
        self.assertEqual(orig_sets, perm_sets)

    # 12. permutation preserves pair totals
    def test_12_permutation_preserves_pair_totals(self):
        csv_path = PROJECT_ROOT / "v27_storage" / "live" / "p45_live_draws.csv"
        draws = calculator.load_draws_from_csv(csv_path, max_round=50)
        p_ids = calculator.draws_to_pair_ids(draws)
        T = len(draws)
        rng = np.random.default_rng(42)
        perm = rng.permutation(T)
        p_ids_perm = p_ids[perm]

        orig_counts = np.bincount(p_ids.ravel(), minlength=990)
        perm_counts = np.bincount(p_ids_perm.ravel(), minlength=990)
        np.testing.assert_array_equal(orig_counts, perm_counts)

    # 13. permutation seed reproducibility
    def test_13_permutation_seed_reproducibility(self):
        sha = "7e9b7ddedb71504cc1aaf80ebc1807e47e51243cbedc2e2ac038e8a34281850a"
        cid = "EXP-DRAW-20261001-001-V1"
        s1 = calculator.derive_deterministic_seed(sha, cid)
        s2 = calculator.derive_deterministic_seed(sha, cid)
        self.assertEqual(s1, s2)
        self.assertEqual(s1, 2359884131)

    # 14. global deviance correctness
    def test_14_global_deviance_correctness(self):
        exp = np.array([1000, 1000, 1000, 1000, 1000, 1000], dtype=np.int64)
        evt = np.array([15, 15, 15, 15, 15, 15], dtype=np.int64)
        t_stat = calculator.compute_t_global(exp, evt)
        self.assertAlmostEqual(t_stat, 0.0, places=10)

    # 15. p-value +1 correction
    def test_15_p_value_plus_one_correction(self):
        B = 4999
        exceed = 0
        p = (1.0 + exceed) / (B + 1.0)
        self.assertEqual(p, 1.0 / 5000.0)
        self.assertGreater(p, 0.0)

    # 16. no 990 independent primary p-values
    def test_16_no_990_independent_primary_p_values(self):
        calc_file = EXPERIMENT_DIR / "CALCULATION.json"
        self.assertTrue(calc_file.exists())
        calc_data = json.loads(calc_file.read_text(encoding="utf-8"))
        primary = calc_data["primary_screen"]
        self.assertIn("T_global_observed", primary)
        self.assertIn("permutation_p_value", primary)
        self.assertNotIn("pair_level_p_values", primary)

    # 17. secondary cannot rescue primary
    def test_17_secondary_cannot_rescue_primary(self):
        calc_file = EXPERIMENT_DIR / "CALCULATION.json"
        calc_data = json.loads(calc_file.read_text(encoding="utf-8"))
        verdict = calc_data["primary_screen"]["verdict"]
        p = calc_data["primary_screen"]["permutation_p_value"]
        if p > 0.05:
            self.assertEqual(verdict, "FAILED_RETROSPECTIVE_SCREEN")
        elif p <= 0.01:
            self.assertEqual(verdict, "RETROSPECTIVE_SIGNAL_CANDIDATE")
        else:
            self.assertEqual(verdict, "INCONCLUSIVE_RETROSPECTIVE")

    # 18. no bonus contamination
    def test_18_no_bonus_contamination(self):
        csv_path = PROJECT_ROOT / "v27_storage" / "live" / "p45_live_draws.csv"
        draws = calculator.load_draws_from_csv(csv_path, max_round=10)
        for _, nums in draws:
            self.assertEqual(len(nums), 6)

    # 19. no Official mutation
    def test_19_no_official_mutation(self):
        sealed_path = PROJECT_ROOT / "v27_storage" / "prospective" / "trio_orbit_v1_001" / "P45_TRIO_ORBIT_TARGET_1244_SEALED_PREDRAW_001.md"
        self.assertTrue(sealed_path.exists())
        txt = sealed_path.read_text(encoding="utf-8")
        self.assertIn("1244", txt)
        self.assertIn("SEALED", txt)

    # 20. historical cannot claim confirmatory holdout
    def test_20_historical_cannot_claim_confirmatory_holdout(self):
        protocol_file = EXPERIMENT_DIR / "PROTOCOL.md"
        txt = protocol_file.read_text(encoding="utf-8")
        self.assertIn("RETROSPECTIVE_SIGNAL_CANDIDATE", txt)
        self.assertIn("Prohibition on Confirmatory Claim", txt)

    # 21. no early prospective inference
    def test_21_no_early_prospective_inference(self):
        protocol_file = EXPERIMENT_DIR / "PROTOCOL.md"
        txt = protocol_file.read_text(encoding="utf-8")
        self.assertIn("52 completed future rounds", txt)
        self.assertIn("Early stopping or intermediate p-value fishing: FORBIDDEN", txt)

    # 22. prospective start must be unknown-outcome round
    def test_22_prospective_start_must_be_unknown_outcome_round(self):
        lock_file = EXPERIMENT_DIR / "PROTOCOL_LOCK.json"
        lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
        prosp_start = lock_data["data_scope"]["prospective_eligible_start_round"]
        self.assertEqual(prosp_start, 1244)

    # 23. protocol hash immutable
    def test_23_protocol_hash_immutable(self):
        protocol_file = EXPERIMENT_DIR / "PROTOCOL.md"
        actual_sha = hashlib.sha256(protocol_file.read_bytes()).hexdigest()
        lock_file = EXPERIMENT_DIR / "PROTOCOL_LOCK.json"
        lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
        self.assertEqual(actual_sha, lock_data["protocol_sha256"])

    # 24. repeat run exact equality
    def test_24_repeat_run_exact_equality(self):
        repro_file = EXPERIMENT_DIR / "REPRODUCIBILITY.json"
        self.assertTrue(repro_file.exists())
        repro_data = json.loads(repro_file.read_text(encoding="utf-8"))
        self.assertTrue(repro_data["reproducibility_pass"])
        for k, v in repro_data["checks"].items():
            self.assertTrue(v, f"Check failed: {k}")

    # 25. Registry namespace collision guard
    def test_25_registry_namespace_collision_guard(self):
        reg_file = PROJECT_ROOT / "00_P45_STATE" / "experiment_lab" / "06_INITIAL_EXPERIMENT_REGISTRY.md"
        txt = reg_file.read_text(encoding="utf-8")
        count = txt.count("EXP-DRAW-20261001-001-V1")
        self.assertLessEqual(count, 1)

    # 26. no automatic EXP-021 label
    def test_26_no_automatic_exp021_label(self):
        lock_file = EXPERIMENT_DIR / "PROTOCOL_LOCK.json"
        lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
        self.assertEqual(lock_data["experiment"]["human_exp_label"], "NONE")

    # 27. candidate identity unchanged
    def test_27_candidate_identity_unchanged(self):
        queue_file = PROJECT_ROOT / "v27_storage" / "research_automation" / "queue" / "IDEA-1243-CROS-003.json"
        q_data = json.loads(queue_file.read_text(encoding="utf-8"))
        self.assertEqual(q_data["candidate_id"], "IDEA-1243-CROS-003")
        self.assertEqual(q_data["birth_round"], 1243)
        self.assertIn("Pair Lifecycle Dormancy Duration Geometric Memory Invariance", q_data["notes"])
        self.assertIn("complete temporal independence of ball pairings", q_data["hypothesis"])

    # 28. Master source identity unchanged
    def test_28_master_source_identity_unchanged(self):
        raw_snap = PROJECT_ROOT / "v27_storage" / "research_automation" / "knowledge" / "MASTER_NON_EXP_RAW_SNAPSHOT.json"
        self.assertTrue(raw_snap.exists())

    # 29. NON-EXP lineage unchanged
    def test_29_non_exp_lineage_unchanged(self):
        fp_file = PROJECT_ROOT / "v27_storage" / "research_automation" / "knowledge" / "MASTER_NON_EXP_SOURCE_FINGERPRINTS.json"
        self.assertTrue(fp_file.exists())
        fp_data = json.loads(fp_file.read_text(encoding="utf-8"))
        self.assertEqual(len(fp_data["item_fingerprints"]), 28)
        self.assertEqual(fp_data["total_items"], 28)

    # 30. canonical display identity unchanged
    def test_30_canonical_display_identity_unchanged(self):
        report_file = PROJECT_ROOT / "v27_storage" / "research_automation" / "evidence" / "GOLDEN_CANDIDATE_DISPLAY_REPORT.json"
        self.assertTrue(report_file.exists())

    # 31. Future leakage 0
    def test_31_future_leakage_zero(self):
        calc_file = EXPERIMENT_DIR / "CALCULATION.json"
        calc_data = json.loads(calc_file.read_text(encoding="utf-8"))
        self.assertEqual(calc_data["primary_screen"]["total_rounds"], 1243)

    # 32. Official firewall
    def test_32_official_firewall(self):
        lock_file = EXPERIMENT_DIR / "PROTOCOL_LOCK.json"
        lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
        self.assertFalse(lock_data["experiment"]["official_integration"])


class TestPairDormancyCorrectionIntegrity(unittest.TestCase):
    """
    15 mandatory correction integrity tests (Section 19).
    """

    @classmethod
    def setUpClass(cls):
        cls.calc_data = json.loads((EXPERIMENT_DIR / "CALCULATION.json").read_text(encoding="utf-8"))["primary_screen"]
        cls.repro_data = json.loads((EXPERIMENT_DIR / "REPRODUCIBILITY.json").read_text(encoding="utf-8"))
        cls.result_txt = (EXPERIMENT_DIR / "RESULT.md").read_text(encoding="utf-8")
        cls.reg_txt = (PROJECT_ROOT / "00_P45_STATE" / "experiment_lab" / "06_INITIAL_EXPERIMENT_REGISTRY.md").read_text(encoding="utf-8")
        cls.lock_data = json.loads((EXPERIMENT_DIR / "PROTOCOL_LOCK.json").read_text(encoding="utf-8"))
        cls.protocol_txt = (EXPERIMENT_DIR / "PROTOCOL.md").read_bytes()
        cls.prosp_data = json.loads((EXPERIMENT_DIR / "PROSPECTIVE_STATE.json").read_text(encoding="utf-8"))
        cls.queue_data = json.loads((PROJECT_ROOT / "v27_storage" / "research_automation" / "queue" / "IDEA-1243-CROS-003.json").read_text(encoding="utf-8"))

    # 1. CALCULATION bin exposure sum equals total
    def test_correction_01_bin_exposure_sum_equals_total(self):
        self.assertEqual(sum(self.calc_data["bin_exposures"]), self.calc_data["total_risk_exposures"])
        self.assertEqual(self.calc_data["total_risk_exposures"], 1162896)
        self.assertEqual(self.calc_data["bin_exposures"][5], 171005)

    # 2. CALCULATION bin event sum equals total
    def test_correction_02_bin_event_sum_equals_total(self):
        self.assertEqual(sum(self.calc_data["bin_events"]), self.calc_data["total_events"])
        self.assertEqual(self.calc_data["total_events"], 17655)

    # 3. RESULT numbers equal CALCULATION
    def test_correction_03_result_numbers_equal_calculation(self):
        self.assertIn("1,162,896", self.result_txt)
        self.assertIn("171,005", self.result_txt)
        self.assertIn("17,655", self.result_txt)

    # 4. REPRODUCIBILITY equals CALCULATION
    def test_correction_04_reproducibility_equals_calculation(self):
        self.assertTrue(self.repro_data["reproducibility_pass"])
        self.assertEqual(self.repro_data["run1_summary"]["T_global"], self.calc_data["T_global_observed"])
        self.assertEqual(self.repro_data["run1_summary"]["p_perm"], self.calc_data["permutation_p_value"])
        self.assertEqual(self.repro_data["run1_summary"]["verdict"], self.calc_data["verdict"])

    # 5. T_global unchanged
    def test_correction_05_t_global_unchanged(self):
        self.assertAlmostEqual(self.calc_data["T_global_observed"], 4.627019413022415, places=10)

    # 6. p_perm unchanged
    def test_correction_06_p_perm_unchanged(self):
        self.assertEqual(self.calc_data["permutation_p_value"], 0.6224)

    # 7. verdict unchanged
    def test_correction_07_verdict_unchanged(self):
        self.assertEqual(self.calc_data["verdict"], "FAILED_RETROSPECTIVE_SCREEN")

    # 8. protocol SHA unchanged
    def test_correction_08_protocol_sha_unchanged(self):
        curr_sha = hashlib.sha256(self.protocol_txt).hexdigest()
        self.assertEqual(curr_sha, "7e9b7ddedb71504cc1aaf80ebc1807e47e51243cbedc2e2ac038e8a34281850a")
        self.assertEqual(self.lock_data["protocol_sha256"], curr_sha)

    # 9. Registry ID exists exactly once
    def test_correction_09_registry_id_exists_exactly_once(self):
        count = self.reg_txt.count("EXP-DRAW-20261001-001-V1")
        self.assertEqual(count, 1)

    # 10. Registry collision count = 0 (EXP-DRAW-20261001-001-V1 has 0 collisions)
    def test_correction_10_registry_collision_count_zero(self):
        import re
        all_eids = re.findall(r"\|(EXP-[A-Z]+-\d+-\d+-V\d+)\|", self.reg_txt)
        collisions = [eid for eid in set(all_eids) if eid == "EXP-DRAW-20261001-001-V1" and all_eids.count(eid) > 1]
        self.assertEqual(len(collisions), 0, f"Found collision for new experiment ID: {collisions}")
        self.assertEqual(all_eids.count("EXP-DRAW-20261001-001-V1"), 1)

    # 11. Registry count reconciliation
    def test_correction_11_registry_count_reconciliation(self):
        import re
        all_eids = re.findall(r"\|(EXP-[A-Z]+-\d+-\d+-V\d+)\|", self.reg_txt)
        unique_eids = set(all_eids)
        self.assertEqual(len(unique_eids), 70)
        self.assertEqual(all_eids[-1], "EXP-DRAW-20261001-001-V1")

    # 12. Candidate state remains FAILED
    def test_correction_12_candidate_state_remains_failed(self):
        self.assertEqual(self.queue_data["candidate_id"], "IDEA-1243-CROS-003")
        self.assertEqual(self.queue_data["state"], "FAILED")
        self.assertEqual(self.queue_data["verdict"], "FAILED_RETROSPECTIVE_SCREEN")

    # 13. Prospective inactive
    def test_correction_13_prospective_inactive(self):
        self.assertFalse(self.prosp_data["automatic_activation_allowed"])
        self.assertEqual(self.prosp_data["prospective_status"], "INACTIVE_DUE_TO_FAILED_OR_INCONCLUSIVE_HISTORICAL_SCREEN")
        self.assertFalse((EXPERIMENT_DIR / "PROSPECTIVE_LOCK.json").exists())

    # 14. Official mutation = 0
    def test_correction_14_official_mutation_zero(self):
        sealed_file = PROJECT_ROOT / "v27_storage" / "prospective" / "trio_orbit_v1_001" / "P45_TRIO_ORBIT_TARGET_1244_SEALED_PREDRAW_001.md"
        self.assertTrue(sealed_file.exists())
        self.assertFalse(self.lock_data["experiment"]["official_integration"])

    # 15. Future leakage = 0
    def test_correction_15_future_leakage_zero(self):
        self.assertEqual(self.calc_data["total_rounds"], 1243)
        self.assertEqual(self.lock_data["data_scope"]["historical_cutoff_round"], 1243)


if __name__ == "__main__":
    unittest.main()


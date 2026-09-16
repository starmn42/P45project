from __future__ import annotations

import tempfile
import unittest
from math import sqrt
from pathlib import Path

from p45_v27.core_store import CoreStore
from p45_v27.database import StoragePaths
from p45_v27.initialize import initialize_storage
from p45_v27.units import DEFINITIONS, Draw, calculate_unit
from p45_v27.units.persistence import load_unit_analysis_counts, persist_unit_analysis


H64 = "a" * 64


def draws(count=40):
    result = []
    for rnd in range(1, count + 1):
        start = (rnd * 7) % 45
        values = [((start + offset * 11) % 45) + 1 for offset in range(7)]
        result.append(Draw(rnd, tuple(sorted(values[:6])), values[6]))
    return result


class Stage4UnitsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history = draws()
        cls.results = {name: calculate_unit(definition, cls.history, 41) for name, definition in DEFINITIONS.items()}

    def test_01_exact_group_shapes(self):
        expected = {"UNIT_3": [3]*15, "UNIT_5": [5]*9, "UNIT_9": [9]*5,
                    "UNIT_10": [10,10,10,10,5], "END_DIGIT": [4,5,5,5,5,5,4,4,4,4]}
        for name, sizes in expected.items():
            self.assertEqual([g.size for g in DEFINITIONS[name].groups], sizes)
        self.assertEqual(DEFINITIONS["END_DIGIT"].groups[0].members, (10,20,30,40))

    def test_02_complete_partition(self):
        for definition in DEFINITIONS.values():
            numbers = [n for group in definition.groups for n in group.members]
            self.assertEqual(sorted(numbers), list(range(1,46)))
            self.assertEqual(len(numbers), len(set(numbers)))

    def test_03_occupancy_sums(self):
        for result in self.results.values():
            for rnd in range(1, 41):
                rows = [r for r in result.round_metrics if r["source_round"] == rnd]
                self.assertEqual(sum(r["integrated"] for r in rows), 7)
                self.assertEqual(sum(r["main"] for r in rows), 6)

    def test_04_size_correction(self):
        for result in self.results.values():
            for row in result.round_metrics:
                self.assertAlmostEqual(row["integrated_occupancy_rate"], row["integrated"] / row["group_size"])
                self.assertAlmostEqual(row["expected_integrated_count"], 7 * row["group_size"] / 45)
                p = row["group_size"] / 45
                sd = sqrt(7 * p * (1-p) * ((45-7)/44))
                self.assertAlmostEqual(row["raw_integrated_deviation"], row["integrated"] - 7 * p)
                self.assertAlmostEqual(row["standardized_integrated_deviation"],
                                       (row["integrated"] - 7 * p) / sd)
                self.assertAlmostEqual(row["expected_main_count"], 6 * row["group_size"] / 45)

    def test_05_annihilation_streak_return_and_vector(self):
        for result in self.results.values():
            group_count = len(result.definition["groups"])
            for row in result.round_metrics:
                self.assertEqual(row["is_annihilated"], row["integrated"] == 0)
                self.assertEqual(len(row["occupancy_vector"]), group_count)
                if row["return_depth"] == "3_PLUS":
                    self.assertTrue(row["structural_exception_3_plus"])

    def test_06_periods_and_independent_outputs(self):
        for name, result in self.results.items():
            self.assertEqual(result.unit_type, name)
            self.assertEqual(set(next(iter(result.period_metrics.values()))),
                             {"overall","first_half","second_half","recent100","recent50","recent20"})
            self.assertEqual(len(result.number_metrics), 45)
            self.assertEqual(result.unit_state, "UNIT_TEST")

    def test_07_future_data_is_blocked(self):
        baseline = calculate_unit(DEFINITIONS["UNIT_10"], self.history, 41)
        contaminated = self.history + [Draw(41, (1,2,3,4,5,6), 7), Draw(999, (40,41,42,43,44,45), 1)]
        blocked = calculate_unit(DEFINITIONS["UNIT_10"], contaminated, 41)
        self.assertEqual(baseline.execution_hash, blocked.execution_hash)
        self.assertEqual(baseline.round_metrics, blocked.round_metrics)

    def test_08_deterministic_ten_runs(self):
        hashes = {calculate_unit(DEFINITIONS["END_DIGIT"], self.history, 41).execution_hash for _ in range(10)}
        self.assertEqual(len(hashes), 1)

    def test_09_database_roundtrip_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = initialize_storage(Path(temp))
            store = CoreStore(paths)
            engine = store.register_engine_version(version_label="2.7-stage4-test", directive_sha256=H64,
                implementation_order_sha256=H64, rule_hash=H64, code_hash=H64, effective_round=1)
            run = store.create_core_run(engine_version_id=engine, analysis_round=41, record_class="BACKTEST",
                raw_data_hash=H64, normalized_data_hash=H64, rule_hash=H64, code_hash=H64)
            for result in self.results.values():
                persist_unit_analysis(store, run, result)
                counts = load_unit_analysis_counts(store, run, result.unit_type)
                self.assertEqual(counts, {"groups": len(result.definition["groups"]),
                                         "round_metrics": 40 * len(result.definition["groups"]), "number_metrics": 45})

    def test_10_required_payloads_exist(self):
        for result in self.results.values():
            self.assertTrue(result.exact_vector_sample)
            self.assertTrue(result.group_local_state_samples)
            self.assertTrue(result.performance)
            self.assertTrue(result.opposite_hypothesis_inputs)
            self.assertTrue(result.structure_collapse_inputs)
            self.assertEqual(result.calculation_status, "COMPLETE")


if __name__ == "__main__":
    unittest.main()

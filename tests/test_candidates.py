from __future__ import annotations

import unittest

from p45.candidates import Exposure, _gate_result, _stats


class CandidateTests(unittest.TestCase):
    def test_stats_separate_main_and_bonus(self) -> None:
        stats = _stats([
            Exposure(2, True, True, False),
            Exposure(3, True, False, True),
            Exposure(4, False, False, False),
        ])
        self.assertEqual(stats["integrated_hits"], 2)
        self.assertEqual(stats["main_hits"], 1)
        self.assertEqual(stats["bonus_hits"], 1)

    def test_unresolved_gates_prevent_pass(self) -> None:
        good = {
            "sample_count": 40,
            "integrated_rate": 0.25,
            "main_rate": 0.20,
        }
        periods = {
            "overall": good,
            "recent_100": {**good, "sample_count": 20},
            "recent_50": {**good, "sample_count": 10},
        }
        gate, status = _gate_result(periods)
        self.assertEqual(gate["provisional_numeric_status"], "NUMERIC_PASS_PENDING_UNRESOLVED_GATES")
        self.assertEqual(status, "HOLD")

    def test_random_or_lower_overall_is_fail(self) -> None:
        weak = {"sample_count": 40, "integrated_rate": 7 / 45, "main_rate": 6 / 45}
        periods = {"overall": weak, "recent_100": weak, "recent_50": weak}
        _, status = _gate_result(periods)
        self.assertEqual(status, "FAIL")


if __name__ == "__main__":
    unittest.main()

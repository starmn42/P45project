from __future__ import annotations

import unittest

from p45.experiment_v24 import fixed_collapse_stage, opposite_risk


def risk_record(overall: float, recent100: float, recent50: float, lower: float = 0.16) -> dict:
    def period(rate: float, sample: int) -> dict:
        return {"integrated_rate": rate, "sample_count": sample, "integrated_wilson_95": [lower, 0.3]}
    return {"primary_performance": {
        "overall": period(overall, 100),
        "recent_100": period(recent100, 20),
        "recent_50": period(recent50, 10),
    }}


class ExperimentV24Tests(unittest.TestCase):
    def test_low_risk_requires_all_periods_and_wilson(self) -> None:
        self.assertEqual(opposite_risk(risk_record(0.20, 0.20, 0.20)), "LOW")

    def test_high_risk_when_both_recent_periods_are_below_random(self) -> None:
        self.assertEqual(opposite_risk(risk_record(0.20, 0.10, 0.10)), "HIGH")

    def test_fixed_collapse_uses_approved_thresholds(self) -> None:
        self.assertEqual(fixed_collapse_stage(0.30, 0.14, 0.20)["stage"], "SEVERE")
        self.assertEqual(fixed_collapse_stage(0.20, 0.18, 0.18)["stage"], "NORMAL")


if __name__ == "__main__":
    unittest.main()

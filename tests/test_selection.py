from __future__ import annotations

import copy
import unittest

from p45.selection import select_final_six


def record(number: int, status: str, role: str = "RETURN") -> dict[str, object]:
    return {
        "number": number,
        "status": status,
        "role": role,
        "rule_state": "TEST" if role == "NON_RETURN_TEST" else "OFFICIAL_GATE_REVIEW",
        "group_9": f"{((number - 1) // 9) * 9 + 1}~{min(((number - 1) // 9 + 1) * 9, 45)}",
        "primary_performance": {
            name: {
                "sample_count": 40 if name == "overall" else 20,
                "integrated_hits": 10,
                "integrated_rate": 0.25,
                "integrated_wilson_95": [0.16, 0.38],
                "main_hits": 8,
                "main_rate": 0.20,
            }
            for name in ("overall", "recent_100", "recent_50")
        },
        "exact_occupancy_vector_performance": {"sample_count": 20},
        "independent_evidence_groups": {
            "structure": True, "performance": True, "risk": True, "composition": True,
        },
        "gate": {"criteria": {
            "overall_integrated_at_least_random_plus_1_5pp": True,
            "recent_100_integrated_at_least_random": True,
            "recent_50_not_below_random_by_more_than_2pp": True,
            "structure_collapse_not_severe": True,
        }},
    }


class SelectionTests(unittest.TestCase):
    def test_selects_six_official_pass_candidates(self) -> None:
        result = select_final_six([record(number, "PASS") for number in range(1, 8)])
        self.assertEqual(result["selection_mode"], "OFFICIAL")
        self.assertEqual(result["selected_count"], 6)
        self.assertTrue(result["all_six_unique"])

    def test_builds_mixed_only_from_valid_test(self) -> None:
        records = [record(1, "PASS"), record(2, "PASS")]
        records += [record(number, "TEST", "NON_RETURN_TEST") for number in range(10, 15)]
        result = select_final_six(records)
        self.assertEqual(result["selection_mode"], "MIXED_TEST")
        self.assertEqual(result["selected_count"], 6)

    def test_hold_and_fail_are_never_forced_in(self) -> None:
        records = [record(1, "PASS")]
        records += [record(number, "HOLD") for number in range(2, 10)]
        records += [record(number, "FAIL") for number in range(10, 20)]
        result = select_final_six(records)
        self.assertEqual(result["selection_mode"], "NONE")
        self.assertEqual(result["selected_numbers"], [])
        self.assertFalse(result["forced_fill_performed"])

    def test_same_input_is_deterministic(self) -> None:
        records = [record(number, "PASS") for number in range(1, 8)]
        first = select_final_six(copy.deepcopy(records))
        second = select_final_six(copy.deepcopy(records))
        self.assertEqual(first, second)

    def test_high_opposite_risk_has_specific_reason(self) -> None:
        item = record(1, "FAIL")
        item["gate"]["criteria"]["opposite_hypothesis_risk"] = "HIGH"
        result = select_final_six([item])
        self.assertEqual(result["stages"]["initial_eliminated"][0]["reason_code"], "OPPOSITE_HIGH")


if __name__ == "__main__":
    unittest.main()

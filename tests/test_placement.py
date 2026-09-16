from __future__ import annotations

import unittest

from p45.placement import place_two_sets


def candidate(number: int, role: str = "NON_RETURN_TEST", group: str | None = None) -> dict[str, object]:
    return {
        "number": number,
        "role": role,
        "group_9": group or f"{((number - 1) // 9) * 9 + 1}~{min(((number - 1) // 9 + 1) * 9, 45)}",
        "independent_evidence_groups": {
            "structure": True,
            "performance": number % 2 == 0,
            "risk": True,
            "composition": True,
        },
    }


class PlacementTests(unittest.TestCase):
    def test_hold_when_six_are_not_available(self) -> None:
        records = {number: candidate(number) for number in range(1, 6)}
        result = place_two_sets([1, 2, 3, 4, 5], records)
        self.assertEqual(result["placement_status"], "HOLD")
        self.assertEqual(result["set_1"], [])
        self.assertEqual(result["set_2"], [])

    def test_one_return_candidate_goes_to_set_one(self) -> None:
        records = {number: candidate(number) for number in range(1, 7)}
        records[4] = candidate(4, "RETURN")
        result = place_two_sets([4, 1, 2, 3, 5, 6], records)
        self.assertEqual(result["placement_status"], "COMPLETE")
        self.assertIn(4, result["set_1"])
        self.assertEqual(len(result["set_1"]), 3)
        self.assertEqual(len(result["set_2"]), 3)

    def test_two_return_candidates_are_split(self) -> None:
        records = {number: candidate(number) for number in range(1, 7)}
        records[4] = candidate(4, "RETURN")
        records[5] = candidate(5, "RETURN")
        result = place_two_sets([4, 5, 1, 2, 3, 6], records)
        self.assertIn(4, result["set_1"])
        self.assertIn(5, result["set_2"])

    def test_candidates_are_never_replaced(self) -> None:
        records = {number: candidate(number) for number in range(1, 7)}
        result = place_two_sets([1, 2, 3, 4, 5, 6], records)
        self.assertEqual(set(result["set_1"] + result["set_2"]), set(range(1, 7)))
        self.assertFalse(result["candidate_replacement_performed"])


if __name__ == "__main__":
    unittest.main()

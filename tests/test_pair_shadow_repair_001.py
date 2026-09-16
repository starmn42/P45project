from __future__ import annotations

import unittest

from p45_audits.pair_shadow_repair_001 import (
    BASELINES, _candidate_decision, materialize_history, synthetic_test_ready_fixture,
)


class PairShadowRepair001Tests(unittest.TestCase):
    def test_warmup_is_explicit(self) -> None:
        result = materialize_history([], [])
        self.assertEqual("INSUFFICIENT", result["stats"]["INTEGRATED_PRIMARY"]["evidence_label"])
        self.assertEqual("INSUFFICIENT", result["stats"]["MAIN_PRIMARY"]["evidence_label"])
        self.assertEqual("INSUFFICIENT_SAMPLE", result["recent_state"])

    def test_recent_is_computed_after_fifty_exposures(self) -> None:
        history = [{"a_integrated_hits": 0, "b_integrated_hits": 0, "a_main_hits": 0, "b_main_hits": 0,
                    "representative_conflict": False} for _ in range(50)]
        result = materialize_history(history, [])
        self.assertIn(result["recent_state"], {"STABLE", "WARNING", "SEVERE"})
        self.assertNotEqual("INSUFFICIENT_SAMPLE", result["recent_state"])

    def test_synthetic_test_ready_uses_canonical_decision(self) -> None:
        self.assertEqual("PAIR_TEST_READY", synthetic_test_ready_fixture())

    def test_candidate_materializes_non_null_gate_evidence(self) -> None:
        metrics = materialize_history([], [])
        gate_input = {"member_states": ["TRIO_TEST", "TRIO_TEST"], "member_numbers": [[1,2,3],[4,5,6]],
                      "unit_statuses": ["COMPLETE"]*5, "coverage_complete_cells": 30,
                      "final_risk": "LOW", "final_structure": "NORMAL", "determinism_ok": True}
        rank = [0,0,0,0,0,0,0,[0],[-1,0],0,0,[[],[]],0,[1,2,3],[4,5,6],"1-2-3__4-5-6"]
        result = _candidate_decision(gate_input, rank, metrics, 2)
        self.assertIsNotNone(result["data"]["integrated_primary_evidence"])
        self.assertIsNotNone(result["data"]["main_primary_evidence"])
        self.assertEqual("PAIR_RESEARCH_HOLD", result["state"])

    def test_baselines_are_frozen_positive_probabilities(self) -> None:
        self.assertEqual({"INTEGRATED_PRIMARY", "INTEGRATED_SUPPORT", "MAIN_PRIMARY", "MAIN_SUPPORT"}, set(BASELINES))
        self.assertTrue(all(0 < value < 1 for value in BASELINES.values()))


if __name__ == "__main__":
    unittest.main()

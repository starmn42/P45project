from __future__ import annotations

import unittest

from p45_v27.pairs import (
    GATE_IDS, GateResult, ParetoVector, assign_sets, bonus_dependence,
    decide_state, evaluate_gates, final_structure, pair_risk,
    pair_unit_coverage, pareto_dominates, ranking_key, recent_support_state, structure_state,
)


def base() -> dict:
    return {
        "member_states": ("TRIO_PASS", "TRIO_PASS"), "member_numbers": ((1, 2, 3), (4, 5, 6)),
        "unit_statuses": ("COMPLETE",) * 5, "coverage_complete_cells": 30,
        "walkforward_prelock_ok": True, "selection_exposure": 200,
        "integrated_primary_rate": .01, "integrated_primary_baseline": .004,
        "integrated_primary_evidence": "SUPERIOR_TENTATIVE",
        "main_primary_rate": .003, "main_primary_baseline": .002,
        "main_primary_evidence": "SUPERIOR_TENTATIVE", "recent_state": "STABLE",
        "final_risk": "LOW", "final_structure": "NORMAL", "determinism_ok": True,
        "executed_gate_ids": GATE_IDS, "ledger_complete": True,
        "valid_trio_count": 2, "disjoint": True, "bonus_dependence": "NONE",
        "primary_evidence": "SUPERIOR_TENTATIVE", "support_evidence": "NEUTRAL",
        "conflict_columns": 0, "members_valid": True, "pool_type": "CORE_PASS_POOL",
        "walkforward_ok": True, "signature_ok": True, "prediction_hash_ok": True,
        "atomic_storage_ok": True,
    }


class PairStage3Tests(unittest.TestCase):
    def test_pair_unit_coverage_exact_30_cells(self) -> None:
        cells = tuple(tuple(tuple({"calculation_status": "COMPLETE", "support": True,
                                   "conflict": unit == 0, "role": f"R{number}",
                                   "evidence_ids": ("SHARED", f"E{member}{number}{unit}")}
                                  for unit in range(5)) for number in range(3)) for member in range(2))
        result = pair_unit_coverage(cells)
        self.assertEqual(5, len(result))
        self.assertEqual(30, sum(x["complete_cell_count"] for x in result))
        self.assertEqual(6, result[0]["conflict_cell_count"])
        self.assertEqual(3, result[0]["distinct_role_count"])
        self.assertEqual(1, result[0]["shared_evidence_id_count"])

    def test_each_gate_pass_fail_incomplete(self) -> None:
        pass_data = base()
        self.assertTrue(all(x.status == "PASS" for x in evaluate_gates(pass_data)))
        missing_keys = ("member_states", "member_numbers", "unit_statuses", "coverage_complete_cells",
                        "walkforward_prelock_ok", "selection_exposure", "integrated_primary_rate",
                        "main_primary_rate", "recent_state", "final_risk", "final_structure",
                        "determinism_ok", "executed_gate_ids", "ledger_complete")
        fail_values = (
            ("TRIO_TEST", "TRIO_PASS"), ((1, 2, 3), (3, 4, 5)), ("COMPLETE",) * 4 + ("ERROR",), 29,
            False, 199, 0.0, 0.0, "SEVERE", "HIGH", "SEVERE", False, tuple(reversed(GATE_IDS)), False,
        )
        for index, (key, value) in enumerate(zip(missing_keys, fail_values)):
            data = base(); data[key] = value
            self.assertEqual("FAIL", evaluate_gates(data)[index].status, GATE_IDS[index])
            data = base(); data[key] = None
            self.assertEqual("INCOMPLETE", evaluate_gates(data)[index].status, GATE_IDS[index])

    def test_ready_all_fourteen_pass(self) -> None:
        data = base()
        self.assertEqual("PAIR_READY", decide_state(evaluate_gates(data), data))

    def _state(self, **changes: object) -> str:
        data = base(); data.update(changes)
        return decide_state(evaluate_gates(data), data)

    def test_test_ready_eight_fixed_cases(self) -> None:
        cases = [
            ({"integrated_primary_rate": 0.001}, "PAIR_TEST_READY"),
            ({"main_primary_rate": 0.001}, "PAIR_TEST_READY"),
            ({"integrated_primary_rate": 0.001, "main_primary_rate": 0.001}, "PAIR_TEST_READY"),
            ({"integrated_primary_rate": 0.001, "integrated_primary_evidence": "INFERIOR_CONFIRMED", "primary_evidence": "INFERIOR_CONFIRMED"}, "PAIR_RESEARCH_HOLD"),
            ({"integrated_primary_rate": 0.001, "recent_state": "SEVERE"}, "PAIR_RESEARCH_HOLD"),
            ({}, "PAIR_READY"),
            ({"signature_ok": False}, "PAIR_SYSTEM_HOLD"),
            ({"selection_exposure": 49}, "PAIR_RESEARCH_HOLD"),
        ]
        self.assertEqual([expected for _, expected in cases], [self._state(**changes) for changes, _ in cases])

    def test_state_precedence_and_totality(self) -> None:
        self.assertEqual("PAIR_SYSTEM_HOLD", self._state(signature_ok=False, selection_exposure=0))
        self.assertEqual("PAIR_RESEARCH_HOLD", self._state(selection_exposure=49, integrated_primary_rate=.001))
        allowed = {"PAIR_SYSTEM_HOLD", "PAIR_RESEARCH_HOLD", "PAIR_READY", "PAIR_TEST_READY"}
        for exposure in (0, 49, 50, 199, 200):
            self.assertIn(self._state(selection_exposure=exposure), allowed)

    def test_risk_boundaries_and_conservative_max(self) -> None:
        self.assertEqual(("MEDIUM", "MEDIUM", "MEDIUM"), pair_risk("LOW", "MEDIUM", primary="NEUTRAL", support="NEUTRAL", integrated_primary="NEUTRAL", main_primary="NEUTRAL", bonus="NONE", recent="STABLE", conflict_columns=0))
        self.assertEqual("HIGH", pair_risk("LOW", "LOW", primary="NEUTRAL", support="NEUTRAL", integrated_primary="NEUTRAL", main_primary="NEUTRAL", bonus="NONE", recent="STABLE", conflict_columns=2)[2])

    def test_recent_100_50_and_20_not_an_input(self) -> None:
        self.assertEqual("SEVERE", recent_support_state(.1, .11, (.08, .09), (.07, .08)))
        self.assertEqual("WARNING", recent_support_state(.1, .11, (.08, .09), (.12, .13)))
        self.assertEqual("STABLE", recent_support_state(.1, .11, None, None))

    def test_bonus_dependence(self) -> None:
        self.assertEqual("HIGH", bonus_dependence("SUPERIOR_CONFIRMED", "INFERIOR_CONFIRMED", True, .001, .002))
        self.assertEqual("MEDIUM", bonus_dependence("SUPERIOR_TENTATIVE", "INFERIOR_TENTATIVE", True, .001, .002))
        self.assertEqual("NONE", bonus_dependence("NEUTRAL", "NEUTRAL", False, .003, .002))

    def test_structure_six_metrics_and_boundaries(self) -> None:
        overall = {"primary": .2, "support": .3, "failure": .1, "conflict": .1}
        r100 = {"primary": .1, "support": .2}
        r50 = {"primary": .05, "support": .1, "failure": .3, "conflict": .2}
        metrics, _, state = structure_state(overall, r100, r50, [tuple([1.0] * 6)] * 49)
        self.assertEqual(6, len(metrics)); self.assertEqual("INSUFFICIENT_SAMPLE", state)
        _, _, state = structure_state(overall, r100, r50, [tuple([0.0] * 6)] * 50)
        self.assertEqual("SEVERE", state)
        self.assertEqual("WARNING", final_structure("NORMAL", "WARNING", "CAUTION"))

    def test_pareto_domination_and_tradeoff(self) -> None:
        a = ParetoVector(0, 0, (2, 2, 2, 2, 2), (0, 0, 0, 0, 0), "LOW", "LOW", "NORMAL")
        b = ParetoVector(1, 0, (1, 1, 1, 1, 1), (1, 1, 1, 1, 1), "MEDIUM", "LOW", "CAUTION")
        self.assertTrue(pareto_dominates(a, b)); self.assertFalse(pareto_dominates(b, a))
        c = ParetoVector(0, 1, (3, 1, 1, 1, 1), (0, 0, 0, 0, 0), "LOW", "LOW", "NORMAL")
        self.assertFalse(pareto_dominates(a, c)); self.assertFalse(pareto_dominates(c, a))

    def test_ranking_fifteen_keys_stable_key_and_sets(self) -> None:
        row = {"both_pass": True, "pareto": "NONDOMINATED", "integrated_primary_rate": .01,
               "integrated_baseline": .004, "main_primary_rate": .003, "support_rate": .1,
               "recent": "STABLE", "weaker_member_vector": (.1, .2, .1, .2), "final_risk": "LOW",
               "conflict_columns": 0, "structure": "NORMAL", "role_diversity": (2,)*5,
               "evidence_overlap": (0,)*5, "simultaneous_failure_rate": .1,
               "set1": (1,2,3), "set2": (4,5,6), "canonical_pair_key": "1-2-3__4-5-6"}
        key = ranking_key(row)
        self.assertEqual(16, len(key))
        changed = dict(row, canonical_pair_key="1-2-3__7-8-9")
        self.assertLess(key, ranking_key(changed))
        self.assertEqual(((1,2,3),(4,5,6)), assign_sets((4,5,6),(1,2,3),(1,),(1,)))
        self.assertEqual(assign_sets((1,2,3),(4,5,6),(2,),(1,)), assign_sets((4,5,6),(1,2,3),(1,),(2,)))

    def test_determinism_ten_times(self) -> None:
        data = base()
        results = [(evaluate_gates(data), decide_state(evaluate_gates(data), data)) for _ in range(10)]
        self.assertEqual(1, len(set(results)))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from p45_v27.core_store import CoreStore
from p45_v27.initialize import initialize_storage
from p45_v27.unit_relation_store import load_relation, persist_relation
from p45_v27.unit_relations import UNIT_ORDER, UnitEvidence, build_relation, pareto_classify, pareto_compare
from p45_v27.units import DEFINITIONS, Draw, calculate_unit

H64 = "b" * 64


def evidence(states):
    return {unit: UnitEvidence(state, {"observed": index, "expected": index / 2},
                               ("shared-size" if unit in ("UNIT_3", "UNIT_9") else f"key-{unit}",),
                               {"recent_context": unit})
            for index, (unit, state) in enumerate(zip(UNIT_ORDER, states), 1)}


def test_draws():
    return [Draw(r, tuple(sorted((((r * 5 + i * 7) % 45) + 1 for i in range(6)))),
                 ((r * 5 + 42) % 45) + 1) for r in range(1, 31)]


class Stage5RelationsTest(unittest.TestCase):
    def test_01_vector_order_and_incomplete(self):
        complete = build_relation("NUMBER", "1", evidence(["UNIT_PASS"] * 5))
        self.assertEqual(complete["unit_state_vector"], ["UNIT_PASS"] * 5)
        partial_input = evidence(["UNIT_PASS"] * 5)
        del partial_input["UNIT_9"]
        missing = build_relation("NUMBER", "1", partial_input)
        self.assertEqual(missing["relation_state"], "UNIT_RELATION_INCOMPLETE")
        self.assertEqual(missing["unit_state_vector"][2], None)

    def test_02_relation_rules(self):
        cases = [
            (["UNIT_PASS","UNIT_WEAKEN","UNIT_PASS","UNIT_WEAKEN","UNIT_PASS"], "UNIT_CONSENSUS_SUPPORT"),
            (["UNIT_PASS","UNIT_TEST","UNIT_HOLD","UNIT_TEST","UNIT_HOLD"], "UNIT_PARTIAL_SUPPORT"),
            (["UNIT_PASS","UNIT_TEST","UNIT_FAIL","UNIT_HOLD","UNIT_TEST"], "UNIT_CONFLICT"),
            (["UNIT_TEST","UNIT_HOLD","UNIT_FAIL","UNIT_TEST","UNIT_HOLD"], "UNIT_NO_SUPPORT"),
        ]
        for states, expected in cases:
            self.assertEqual(build_relation("NUMBER", "7", evidence(states))["relation_state"], expected)
        strong = evidence(["UNIT_PASS","UNIT_TEST","UNIT_TEST","UNIT_TEST","UNIT_TEST"])
        strong["UNIT_10"] = UnitEvidence("UNIT_TEST", {"z": -4.2}, strong_opposition=True)
        self.assertEqual(build_relation("NUMBER", "7", strong)["relation_state"], "UNIT_CONFLICT")

    def test_03_raw_related_independent_and_duplicates_preserved(self):
        relation = build_relation("NUMBER", "8", evidence(["UNIT_PASS"] * 5))
        blocks = relation["evidence"]
        self.assertEqual(set(blocks), {"RAW_UNIT_SUPPORT","RELATED_UNIT_SUPPORT",
                                       "INDEPENDENT_CONTEXT_SUPPORT","UNIT_CONFLICT"})
        self.assertEqual(relation["duplicate_evidence"], {"shared-size": ["UNIT_3", "UNIT_9"]})
        self.assertEqual(blocks["RAW_UNIT_SUPPORT"]["UNIT_3"]["values"]["observed"], 1)
        self.assertEqual(blocks["INDEPENDENT_CONTEXT_SUPPORT"]["UNIT_3"]["recent_context"], "UNIT_3")

    def test_04_no_scores_or_weights(self):
        relation = build_relation("NUMBER", "9", evidence(["UNIT_PASS"] * 5))
        forbidden = ("score", "weight", "average", "pass_count", "total_score")
        serialized = json.dumps(relation).lower()
        self.assertFalse(any(term in serialized for term in forbidden))

    def test_05_pareto_domination(self):
        better = build_relation("NUMBER", "1", evidence(["UNIT_PASS"] * 5))
        worse = build_relation("NUMBER", "2", evidence(["UNIT_WEAKEN","UNIT_PASS","UNIT_PASS","UNIT_PASS","UNIT_PASS"]))
        self.assertEqual(pareto_compare(better, worse), "UNIT_PARETO_DOMINATE")
        self.assertEqual(pareto_compare(worse, better), "UNIT_PARETO_DOMINATED")
        classified = pareto_classify({"1": better, "2": worse})
        self.assertEqual(classified, {"1": "UNIT_PARETO_NONDOMINATED", "2": "UNIT_PARETO_DOMINATED"})

    def test_06_tradeoffs_remain_nondominated(self):
        left = build_relation("NUMBER", "1", evidence(["UNIT_PASS","UNIT_FAIL","UNIT_TEST","UNIT_TEST","UNIT_TEST"]))
        right = build_relation("NUMBER", "2", evidence(["UNIT_FAIL","UNIT_PASS","UNIT_TEST","UNIT_TEST","UNIT_TEST"]))
        self.assertEqual(pareto_compare(left, right), "UNIT_PARETO_NONDOMINATED")
        self.assertEqual(pareto_classify({"1": left, "2": right}),
                         {"1": "UNIT_PARETO_NONDOMINATED", "2": "UNIT_PARETO_NONDOMINATED"})

    def test_07_deterministic_ten_runs(self):
        hashes = {build_relation("NUMBER", "11", evidence(["UNIT_PASS","UNIT_WEAKEN","UNIT_TEST","UNIT_HOLD","UNIT_FAIL"]))["relation_hash"]
                  for _ in range(10)}
        self.assertEqual(len(hashes), 1)

    def test_08_database_roundtrip(self):
        relation = build_relation("NUMBER", "12", evidence(["UNIT_PASS","UNIT_TEST","UNIT_HOLD","UNIT_TEST","UNIT_HOLD"]))
        with tempfile.TemporaryDirectory() as temp:
            paths = initialize_storage(Path(temp))
            store = CoreStore(paths)
            engine = store.register_engine_version(version_label="2.7-stage5-test", directive_sha256=H64,
                implementation_order_sha256=H64, rule_hash=H64, code_hash=H64, effective_round=1)
            run = store.create_core_run(engine_version_id=engine, analysis_round=31, record_class="BACKTEST",
                raw_data_hash=H64, normalized_data_hash=H64, rule_hash=H64, code_hash=H64)
            persist_relation(store, run, relation, "UNIT_PARETO_NONDOMINATED", relation["relation_hash"])
            loaded = load_relation(store, run, "NUMBER", "12")
            self.assertIsNotNone(loaded)
            self.assertEqual(json.loads(loaded["unit_state_vector_json"]), relation["unit_state_vector"])
            self.assertEqual(loaded["relation_state"], relation["relation_state"])
            self.assertEqual(loaded["relation_hash"], relation["relation_hash"])
            raw = json.loads(loaded["conflict_raw_json"])["raw_values"]
            self.assertEqual(raw["UNIT_3"]["values"]["observed"], 1)

    def test_09_future_boundary_filters_only_future(self):
        history = test_draws()
        baseline = calculate_unit(DEFINITIONS["UNIT_10"], history, 31)
        with_future = calculate_unit(DEFINITIONS["UNIT_10"], history + [Draw(31, (1,2,3,4,5,6), 7)], 31)
        self.assertEqual(baseline.execution_hash, with_future.execution_hash)
        changed_boundary = history[:-1] + [Draw(30, (1,2,3,4,5,6), 7)]
        self.assertNotEqual(baseline.execution_hash,
                            calculate_unit(DEFINITIONS["UNIT_10"], changed_boundary, 31).execution_hash)
        with self.assertRaises(ValueError):
            calculate_unit(DEFINITIONS["UNIT_10"], history[:-1], 31)

    def test_10_test_is_never_promoted(self):
        relation = build_relation("NUMBER", "13", evidence(["UNIT_TEST"] * 5))
        self.assertEqual(relation["unit_state_vector"], ["UNIT_TEST"] * 5)
        self.assertEqual(relation["relation_state"], "UNIT_NO_SUPPORT")


if __name__ == "__main__":
    unittest.main()

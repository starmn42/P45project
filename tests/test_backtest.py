from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from p45.backtest import generate_return_events, run_backtest, summarize_events, wilson_interval
from p45.data import Draw


def make_structure_bundle(root: Path) -> Path:
    bundle = root / "structure-4"
    bundle.mkdir()
    input_path = bundle / "analysis-input.csv"
    input_path.write_text(
        "round,date,n1,n2,n3,n4,n5,n6,bonus\n"
        "1,2002-12-07,1,2,10,11,19,37,45\n"
        "2,2002-12-14,3,4,12,20,28,38,44\n"
        "3,2002-12-21,5,6,13,21,29,39,43\n",
        encoding="utf-8",
    )
    report = {
        "previous_draw_structure": {"occupancy_9": [2, 1, 1, 1, 2]}
    }
    report_path = bundle / "structure-report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    metadata = {
        "analysis_type": "BASIC_STRUCTURE",
        "analysis_status": "COMPLETE",
        "target_round": 4,
        "effective_data_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "structure_report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
    }
    (bundle / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    return bundle


class BacktestTests(unittest.TestCase):
    def test_event_uses_previous_draw_condition(self) -> None:
        draws = [
            Draw(1, date(2002, 12, 7), (1, 2, 10, 11, 19, 37), 45),
            Draw(2, date(2002, 12, 14), (3, 4, 12, 20, 28, 38), 44),
        ]
        events = generate_return_events(draws)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].group, "28~36")
        self.assertEqual(events[0].generation_cutoff_round, 1)
        self.assertEqual(events[0].target_round, 2)
        self.assertEqual(events[0].integrated_depth, 1)

    def test_summary_separates_continued_annihilation(self) -> None:
        draws = [
            Draw(1, None, (1, 2, 10, 11, 19, 37), 45),
            Draw(2, None, (3, 4, 12, 20, 21, 38), 44),
        ]
        summary = summarize_events(generate_return_events(draws))
        self.assertEqual(summary["integrated"]["depth_counts"]["0"], 1)
        self.assertEqual(summary["opposite_hypothesis"]["continued_annihilation"], 1)

    def test_wilson_is_bounded(self) -> None:
        interval = wilson_interval(7, 10)
        self.assertIsNotNone(interval)
        self.assertTrue(0 <= interval[0] < interval[1] <= 1)

    def test_backtest_records_hold_without_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = run_backtest(make_structure_bundle(root), root / "backtests")
            report = json.loads((result / "backtest-report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["leakage_audit"]["status"], "PASS")
            self.assertEqual(report["official_gate"]["status"], "HOLD")
            self.assertFalse(report["structure_collapse"]["arbitrary_threshold_created"])
            self.assertEqual(
                report["current_exact_occupancy_vector"]["evidence_status"],
                "REFERENCE_OR_HOLD",
            )


if __name__ == "__main__":
    unittest.main()

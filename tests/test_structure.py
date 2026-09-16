from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from p45.data import Draw
from p45.structure import (
    StructureAnalysisError,
    analyze_structure,
    build_draw_structure,
    split_periods,
)


def make_dataset(root: Path) -> Path:
    dataset = root / "validated-1-3"
    dataset.mkdir()
    csv_path = dataset / "normalized.csv"
    csv_path.write_text(
        "round,date,n1,n2,n3,n4,n5,n6,bonus\n"
        "1,2002-12-07,1,2,10,11,19,37,45\n"
        "2,2002-12-14,3,4,12,20,28,38,44\n"
        "3,2002-12-21,5,6,13,21,29,39,43\n",
        encoding="utf-8",
    )
    metadata = {
        "confirmation_status": "CONFIRMED",
        "analysis_allowed": True,
        "normalized_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
    }
    (dataset / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    return dataset


class StructureTests(unittest.TestCase):
    def test_builds_seven_number_structure(self) -> None:
        draw = Draw(1, None, (1, 2, 10, 11, 19, 37), 45)
        result = build_draw_structure(draw)
        self.assertEqual(result.occupancy_9, (2, 2, 1, 0, 2))
        self.assertEqual(result.annihilated_9, ("28~36",))
        self.assertIn(3, result.absent_endings)
        self.assertNotIn(0, result.absent_endings)

    def test_odd_split_puts_extra_draw_in_second_half(self) -> None:
        draws = [Draw(i, None, (1, 2, 3, 4, 5, 6), 7) for i in range(1, 6)]
        periods = split_periods(draws)
        self.assertEqual(len(periods["first_half"]), 2)
        self.assertEqual(len(periods["second_half"]), 3)

    def test_historical_target_blocks_future_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = analyze_structure(make_dataset(root), root / "analysis", target_round=3)
            report = json.loads((result / "structure-report.json").read_text(encoding="utf-8"))
            metadata = json.loads((result / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(report["data_range"]["end"], 2)
            self.assertEqual(metadata["future_data_blocked_after_round"], 2)
            self.assertNotIn("3,2002-12-21", (result / "analysis-input.csv").read_text(encoding="utf-8"))

    def test_rejects_changed_confirmed_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dataset = make_dataset(root)
            with (dataset / "normalized.csv").open("a", encoding="utf-8") as stream:
                stream.write("\n")
            with self.assertRaises(StructureAnalysisError):
                analyze_structure(dataset, root / "analysis")


if __name__ == "__main__":
    unittest.main()

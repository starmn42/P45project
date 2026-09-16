from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from p45.data import DataValidationError, load_and_validate_csv, prepare_dataset


HEADER = "round,date,n1,n2,n3,n4,n5,n6,bonus\n"


class DataTests(unittest.TestCase):
    def write_csv(self, root: Path, body: str) -> Path:
        path = root / "draws.csv"
        path.write_text(HEADER + body, encoding="utf-8")
        return path

    def test_normalizes_numbers_and_writes_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.write_csv(
                root,
                "1,2002-12-07,40,10,23,29,33,37,16\n"
                "2,2002-12-14,9,13,21,25,32,42,2\n",
            )
            result = prepare_dataset(source, root / "out", "테스트")
            normalized = (result / "normalized.csv").read_text(encoding="utf-8")
            self.assertIn("1,2002-12-07,10,23,29,33,37,40,16", normalized)
            metadata = json.loads((result / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["valid_draw_count"], 2)
            self.assertEqual(len(metadata["raw_sha256"]), 64)
            self.assertEqual(metadata["confirmation_status"], "CONFIRMED")

    def test_rejects_missing_round(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.write_csv(root, "2,2002-12-14,9,13,21,25,32,42,2\n")
            with self.assertRaises(DataValidationError) as caught:
                load_and_validate_csv(source)
            self.assertIn("누락 회차", str(caught.exception))

    def test_rejects_number_and_bonus_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.write_csv(root, "1,2002-12-07,10,10,23,29,33,37,10\n")
            with self.assertRaises(DataValidationError) as caught:
                load_and_validate_csv(source)
            message = str(caught.exception)
            self.assertIn("본번호 내부에 중복", message)
            self.assertIn("보너스번호", message)

    def test_failure_does_not_create_confirmed_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.write_csv(root, "1,bad-date,1,2,3,4,5,46,7\n")
            output = root / "out"
            with self.assertRaises(DataValidationError):
                prepare_dataset(source, output, "테스트")
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()

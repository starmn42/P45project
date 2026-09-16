from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from p45.data import load_and_validate_csv
from p45.validate import (
    CollectionValidationError,
    DataConflictError,
    compare_user_data,
    validate_collected_dataset,
)


CSV = (
    "round,date,n1,n2,n3,n4,n5,n6,bonus\n"
    "1,2002-12-07,10,23,29,33,37,40,16\n"
    "2,2002-12-14,9,13,21,25,32,42,2\n"
)


def make_collection(root: Path) -> Path:
    collection = root / "official-1-2"
    raw = collection / "raw"
    raw.mkdir(parents=True)
    (raw / "api-0001.json").write_text("{}", encoding="utf-8")
    (raw / "result-page.html").write_text("official", encoding="utf-8")
    csv_path = collection / "official.csv"
    csv_path.write_text(CSV, encoding="utf-8")
    bundle = hashlib.sha256()
    for path in sorted(raw.iterdir(), key=lambda item: item.name):
        bundle.update(path.name.encode())
        bundle.update(path.read_bytes())
    metadata = {
        "source": "동행복권 공식 사이트",
        "source_page": "https://www.dhlottery.co.kr/lt645/result",
        "source_api": "https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do",
        "collection_status": "COLLECTED_UNVERIFIED",
        "start_round": 1,
        "end_round": 2,
        "draw_count": 2,
        "raw_bundle_sha256": bundle.hexdigest(),
        "csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
    }
    (collection / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
    return collection


class ValidateTests(unittest.TestCase):
    def test_confirms_intact_collection(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = validate_collected_dataset(make_collection(root), root / "validated")
            metadata = json.loads((result / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["confirmation_status"], "CONFIRMED")
            self.assertTrue(metadata["analysis_allowed"])

    def test_detects_collection_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            collection = make_collection(root)
            (collection / "official.csv").write_text(CSV.replace(",16\n", ",17\n"), encoding="utf-8")
            with self.assertRaises(CollectionValidationError) as caught:
                validate_collected_dataset(collection, root / "validated")
            self.assertIn("변경", str(caught.exception))

    def test_reports_exact_user_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            official_path = root / "official.csv"
            user_path = root / "user.csv"
            official_path.write_text(CSV, encoding="utf-8")
            user_path.write_text(CSV.replace(",2\n", ",3\n"), encoding="utf-8")
            conflicts = compare_user_data(
                load_and_validate_csv(official_path), load_and_validate_csv(user_path)
            )
            self.assertEqual(conflicts[0].round, 2)
            self.assertEqual(conflicts[0].field, "bonus")

    def test_conflict_does_not_create_confirmed_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            collection = make_collection(root)
            user_path = root / "user.csv"
            user_path.write_text(CSV.replace(",2\n", ",3\n"), encoding="utf-8")
            output = root / "validated"
            with self.assertRaises(DataConflictError):
                validate_collected_dataset(collection, output, user_csv=user_path)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()

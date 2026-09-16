from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from p45.ledger import LedgerError, review_result, verify_locked_record


class LedgerReviewTests(unittest.TestCase):
    def make_locked_record(self, root: Path) -> Path:
        record = root / "records" / "round-10"
        record.mkdir(parents=True)
        locked = {
            "target_round": 10,
            "selection": {
                "selected_numbers": [1, 2, 3, 10, 11, 12],
                "stages": {
                    "final_selected": [1, 2, 3, 10, 11, 12],
                    "alternate_eliminated": [],
                    "middle_eliminated": [{"number": 4, "reason_code": "SAMPLE_INSUFFICIENT"}],
                    "initial_eliminated": [{"number": 5, "reason_code": "OVERALL_FAIL"}],
                },
            },
            "sets": {"set_1": [1, 3, 11], "set_2": [2, 10, 12]},
            "record_class": "LIVE_OFFICIAL",
        }
        locked_path = record / "locked-report.json"
        locked_path.write_text(json.dumps(locked), encoding="utf-8")
        files = [{
            "path": "locked-report.json",
            "size": locked_path.stat().st_size,
            "sha256": hashlib.sha256(locked_path.read_bytes()).hexdigest(),
        }]
        manifest_path = record / "manifest.json"
        manifest_path.write_text(json.dumps({"files": files}), encoding="utf-8")
        metadata = {
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "locked_report_sha256": hashlib.sha256(locked_path.read_bytes()).hexdigest(),
        }
        (record / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
        return record

    def test_review_is_add_only_and_scores_separately(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self.make_locked_record(root)
            before = hashlib.sha256((record / "locked-report.json").read_bytes()).hexdigest()
            result = review_result(root, 10, [1, 4, 5, 20, 21, 22], 2)
            review = json.loads((result / "review.json").read_text(encoding="utf-8"))
            after = hashlib.sha256((record / "locked-report.json").read_bytes()).hexdigest()
            self.assertEqual(review["main_hit_count"], 1)
            self.assertTrue(review["bonus_hit"])
            self.assertEqual(review["integrated_hit_count"], 2)
            self.assertEqual(before, after)

    def test_tampered_record_blocks_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self.make_locked_record(root)
            with (record / "locked-report.json").open("a", encoding="utf-8") as stream:
                stream.write(" ")
            with self.assertRaises(LedgerError):
                review_result(root, 10, [1, 2, 3, 4, 5, 6], 7)

    def test_manifest_verification_passes_for_intact_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self.make_locked_record(root)
            verify_locked_record(record)


if __name__ == "__main__":
    unittest.main()

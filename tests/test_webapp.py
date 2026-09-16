from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from p45.webapp import dashboard_status


class WebAppTests(unittest.TestCase):
    def test_empty_workspace_reports_pending_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            status = dashboard_status(Path(temp))
            self.assertEqual(len(status["phases"]), 10)
            self.assertEqual(status["phases"][0]["status"], "COMPLETE")
            self.assertEqual(status["phases"][1]["status"], "PENDING")

    def test_dashboard_reads_locked_result_without_changing_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = root / "ledger" / "records" / "round-10"
            record.mkdir(parents=True)
            locked = {
                "target_round": 10,
                "record_class": "LIVE_TEST",
                "first_execution": True,
            }
            (record / "locked-report.json").write_text(json.dumps(locked), encoding="utf-8")
            (record / "metadata.json").write_text(json.dumps({"lock_status": "LOCKED", "manifest_sha256": "abc"}), encoding="utf-8")
            before = (record / "locked-report.json").read_bytes()
            status = dashboard_status(root)
            after = (record / "locked-report.json").read_bytes()
            self.assertEqual(status["target_round"], 10)
            self.assertEqual(status["lock"]["status"], "LOCKED")
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()

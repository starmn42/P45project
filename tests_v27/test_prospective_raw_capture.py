from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from p45_experiments import prospective_raw_capture as m


class ProspectiveRawCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        doc = json.loads(m.FIXTURE.read_text(encoding="utf-8"))
        cls.fixture_1237 = m.FIXTURE.read_bytes()
        item = next(x for x in doc["data"]["list"] if int(x["ltEpsd"]) == 1237)
        cls.base_item = dict(item)

    def payload(self, round_number: int, *, second_count: int | None = None) -> bytes:
        item = dict(self.base_item)
        item["ltEpsd"] = round_number
        if second_count is not None:
            item["rnk2WnNope"] = second_count
        return json.dumps({"data": {"list": [item]}}, separators=(",", ":")).encode()

    def test_01_fixture_mapping(self):
        row = m.source_row(self.fixture_1237, 1237, "TEST")
        self.assertEqual(row["main_numbers"], [10, 20, 23, 34, 37, 40])
        self.assertEqual((row["bonus"], row["first_prize_games"], row["second_prize_games"]), (36, 23, 75))
        self.assertEqual(row["total_sales_amount_krw"], 118363161000)

    def test_02_static_guard(self):
        self.assertEqual(m.static_guard()["signal_calculation_code_paths"], 0)

    def test_03_dry_run_does_not_write_ledger(self):
        before = m.LEDGER.read_bytes() if m.LEDGER.exists() else b""
        self.assertEqual(m.dry_run_1237()["status"], "PASS")
        after = m.LEDGER.read_bytes() if m.LEDGER.exists() else b""
        self.assertEqual(before, after)

    def isolated(self, temp: Path):
        return mock.patch.multiple(
            m, STORE=temp, LEDGER=temp / "ledger.jsonl", CORRECTIONS=temp / "corrections.jsonl",
            RUN_LOG=temp / "runs.jsonl", LOCK=temp / ".lock",
        )

    def test_04_append_and_idempotency(self):
        with tempfile.TemporaryDirectory() as td, self.isolated(Path(td)), mock.patch.object(m, "live_update_running", return_value=False):
            def fetcher(round_number: int, timeout: float = 20.0):
                if round_number == 1238:
                    return self.payload(1238)
                raise LookupError("SOURCE_UNAVAILABLE")
            with mock.patch.object(m, "fetch", side_effect=fetcher):
                first = m.capture()
                second = m.capture()
            self.assertEqual((first["written"], second["written"]), (1, 0))
            self.assertEqual(len(m.read_jsonl(m.LEDGER)), 1)

    def test_05_changed_existing_record_blocks(self):
        with tempfile.TemporaryDirectory() as td, self.isolated(Path(td)), mock.patch.object(m, "live_update_running", return_value=False):
            with mock.patch.object(m, "fetch", side_effect=lambda r, timeout=20.0: self.payload(r) if r == 1238 else (_ for _ in ()).throw(LookupError())):
                self.assertEqual(m.capture()["written"], 1)
            changed = self.payload(1238, second_count=76)
            with mock.patch.object(m, "fetch", return_value=changed):
                result = m.capture()
            self.assertEqual(result["status"], "DATA_INTEGRITY_CONFLICT")
            self.assertEqual(len(m.read_jsonl(m.LEDGER)), 1)
            self.assertEqual(len(m.read_jsonl(m.CORRECTIONS)), 1)

    def test_06_defer_has_no_ledger_write(self):
        with tempfile.TemporaryDirectory() as td, self.isolated(Path(td)), mock.patch.object(m, "live_update_running", return_value=True):
            result = m.capture()
            self.assertEqual(result["status"], "DEFERRED_DUE_TO_P45_UPDATE")
            self.assertFalse(m.LEDGER.exists())

    def test_07_raw_row_has_no_derived_signal_fields(self):
        row = m.source_row(self.fixture_1237, 1237, "TEST")
        forbidden = {"m", "b", "B1", "X2", "Z2", "SHARE_INDEX", "SHARE2_INDEX", "beta", "p", "effect", "direction", "score", "rank"}
        self.assertFalse(forbidden.intersection(row))


if __name__ == "__main__":
    unittest.main()

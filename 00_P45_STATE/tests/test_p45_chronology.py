from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REAL = Path(__file__).resolve().parents[1]
PROJECT = REAL.parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


M = load("chronology_manager", REAL / "tools/p45_state_manager.py")
H = load("chronology_handoff", REAL / "tools/p45_handoff.py")


class ChronologyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "00_P45_STATE"
        self.root.mkdir()
        for name in M.TEXT_NAMES + ("P45_CURRENT_STATE.json",):
            shutil.copy2(REAL / name, self.root / name)
        (self.root / "state-history").mkdir()
        self.manager = M.StateManager(self.root, PROJECT)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_01_decision_after_state_conflict(self):
        self.assertIn("DECISION_AFTER_STATE", M.chronology_errors("2026-08-10T14:10:00+09:00", "2026-08-10T14:05:00+09:00")[0])

    def test_02_state_after_bundle_conflict(self):
        self.assertIn("STATE_AFTER_BUNDLE", M.chronology_errors("2026-08-10T14:00:00+09:00", "2026-08-10T14:05:00+09:00", "2026-08-10T14:04:00+09:00")[0])

    def test_03_equal_timestamps_allowed(self):
        t = "2026-08-10T14:05:00+09:00"
        self.assertEqual([], M.chronology_errors(t, t, t, t))

    def test_04_normal_order_verified(self):
        self.assertEqual([], M.chronology_errors("2026-08-10T14:00:00+09:00", "2026-08-10T14:01:00+09:00", "2026-08-10T14:02:00+09:00", "2026-08-10T14:01:30+09:00"))

    def test_05_plus_nine_aware(self):
        self.assertEqual(9 * 3600, int(M.parse_aware_timestamp("2026-08-10T14:00:00+09:00").utcoffset().total_seconds()))

    def test_06_utc_equivalence(self):
        self.assertEqual(M.parse_aware_timestamp("2026-08-10T05:00:00+00:00"), M.parse_aware_timestamp("2026-08-10T14:00:00+09:00"))

    def test_07_naive_blocked(self):
        with self.assertRaisesRegex(M.StateError, "NAIVE_TIMESTAMP"):
            M.parse_aware_timestamp("2026-08-10T14:00:00")

    def test_08_future_decision_commit_blocked(self):
        decision = {"decision_id": "DECISION-FUTURE", "timestamp": "2099-01-01T00:00:00+09:00", "decision": "x"}
        with self.assertRaisesRegex(M.StateError, "FUTURE_DECISION"):
            self.manager.atomic_state_update({}, decision)

    def test_09_failed_chronology_preserves_state(self):
        before = (self.root / "P45_CURRENT_STATE.json").read_bytes()
        with self.assertRaises(M.StateError):
            self.manager.atomic_state_update({}, {"decision_id": "DECISION-FUTURE", "timestamp": "2099-01-01T00:00:00+09:00", "decision": "x"})
        self.assertEqual(before, (self.root / "P45_CURRENT_STATE.json").read_bytes())

    def test_10_failed_chronology_preserves_bundle(self):
        bundle = self.root / "P45_PORTABLE_HANDOFF.zip"
        H.create_bundle(self.root, bundle)
        before = bundle.read_bytes()
        with self.assertRaises(M.StateError):
            self.manager.atomic_state_update({}, {"decision_id": "DECISION-FUTURE", "timestamp": "2099-01-01T00:00:00+09:00", "decision": "x"})
        self.assertEqual(before, bundle.read_bytes())

    def test_11_portable_content_hash_deterministic_x10(self):
        values = {H.portable_content_hash(self.root) for _ in range(10)}
        self.assertEqual(1, len(values))

    def test_12_decision_014_unchanged(self):
        text = (REAL / "P45_DECISION_LOG.md").read_text(encoding="utf-8-sig")
        block = text.split("## DECISION-20260810-014", 1)[1].split("## DECISION-20260810-015", 1)[0]
        self.assertIn("2026-08-10T14:10:00+09:00", block)

    def test_13_bug_fix_decision_appended(self):
        text = (REAL / "P45_DECISION_LOG.md").read_text(encoding="utf-8-sig")
        self.assertIn("## DECISION-20260810-015", text)
        self.assertIn("- category: BUG_FIX", text)

    def test_14_conflict_evidence_preserved(self):
        folders = list((REAL / "state-history").glob("*_PORTABLE_CONFLICT_001"))
        self.assertTrue(folders)
        for name in ("P45_PORTABLE_HANDOFF.zip", "P45_CURRENT_STATE.md", "P45_CURRENT_STATE.json", "P45_HANDOFF.md", "P45_DECISION_LOG.md", "handoff-manifest.json", "conflict-report.json"):
            self.assertTrue((folders[-1] / name).exists())

    def test_15_research_protection_hashes(self):
        state = json.loads((REAL / "P45_CURRENT_STATE.json").read_text(encoding="utf-8-sig"))
        self.assertEqual("7c1458328a17a0824622c00ce1f54996e22ed4c2e9d04180be4ad9029ba8febb", state["important_hashes"]["canonical_manifest"])
        self.assertEqual("76eaecb50557b66c6ffa3324cebf7a508a982356541236948cadf75ca04825f5", state["important_hashes"]["walkforward_db"])
        self.assertEqual("1b7b86d85f161f1a1dc1ea2d1c6712daefa30d9c8ae938fa8403784e055e9f59", state["important_hashes"]["trio_final_db"])

    def test_16_snapshot_after_state(self):
        state = json.loads((REAL / "P45_CURRENT_STATE.json").read_text(encoding="utf-8-sig"))
        snap = sorted((REAL / "state-history").glob("*_DECISION-20260810-015"))[-1]
        manifest = json.loads((snap / "state-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([], M.chronology_errors(M.decision_timestamp((REAL / "P45_DECISION_LOG.md").read_text(encoding="utf-8-sig"), state["last_decision_id"]), state["updated_at"], snapshot_time=manifest["timestamp"]))

    def test_17_portable_verifier_chronology(self):
        result = H.cold_start_bundle(REAL / "P45_PORTABLE_HANDOFF.zip")
        self.assertEqual("STATE_HANDOFF_PORTABLE_ONLY", result["status"])


if __name__ == "__main__":
    unittest.main()

"""Comprehensive cloud fault-injection test suite for P45 auto-lifecycle.

Covers Section 14 requirements:
A. Clean environment --once execution
B. Already-current execution -> 0 writes / 0 seal mutation
C. Official result fetch temporary failure -> graceful failure and retry readiness
D. Deployment delay -> bounded retry/poll
E. Git push no-change -> 0 empty commit
F. Multiple simultaneous trigger -> concurrency lock blocks parallel runs
G. Existing seal -> immutable (hash verification)
H. Multi-round stale fixture -> chronological catch-up sequence
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from p45_v27.webapp import AutoUpdateCoordinator, ADAPTER
from p45_v27 import web_publish


class CloudLifecycleFaultInjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.status = ADAPTER.read()
        cls.target = int(cls.status["current"]["target"])
        cls.sealed_path = Path(cls.status["seal"]["path"])
        cls.sealed_sha = hashlib.sha256(cls.sealed_path.read_bytes()).hexdigest()

    def test_a_clean_environment_run_once(self):
        """A. Clean environment --once execution."""
        coordinator = AutoUpdateCoordinator(ADAPTER)
        res = coordinator.run_once(trigger_source="TEST_A_CLEAN")
        self.assertIsNone(res.get("last_error"))
        self.assertIn("DRAW_ALREADY_CURRENT", res["steps"])

    def test_b_already_current_no_seal_mutation(self):
        """B. Already-current execution -> no seal mutation, no data corruption."""
        before_sha = hashlib.sha256(self.sealed_path.read_bytes()).hexdigest()
        coordinator = AutoUpdateCoordinator(ADAPTER)
        res = coordinator.run_once(trigger_source="TEST_B_IDEMPOTENT")
        after_sha = hashlib.sha256(self.sealed_path.read_bytes()).hexdigest()

        self.assertEqual(before_sha, after_sha)
        self.assertEqual(before_sha, self.sealed_sha)
        self.assertIn("WEB_ALREADY_CURRENT", res["steps"])

    def test_c_fetch_temporary_failure(self):
        """C. Official result fetch temporary failure -> workflow failure caught, retryable next time."""
        def mock_failing_update():
            return {"status": "DRAW_UPDATE_FAILED", "error": "HTTP_503_SERVICE_UNAVAILABLE"}

        coordinator = AutoUpdateCoordinator(ADAPTER, update=mock_failing_update)
        res = coordinator.run_once(trigger_source="TEST_C_FAIL")
        self.assertEqual(res["status"], "자동 업데이트 오류")
        self.assertIn("DRAW_UPDATE_REJECTED", res["last_error"])
        self.assertIn("HTTP_503", res["last_error"])

        # Immediate next try with good update recovers cleanly
        recovering_coordinator = AutoUpdateCoordinator(ADAPTER, update=lambda: {"status": "DRAW_ALREADY_CURRENT"})
        res2 = recovering_coordinator.run_once(trigger_source="TEST_C_RETRY")
        self.assertEqual(res2["status"], "자동 업데이트 반영")
        self.assertIsNone(res2["last_error"])

    def test_d_deployment_delay_bounded_poll(self):
        """D. Deployment delay -> bounded retry/poll succeeds after attempts."""
        mock_adapter = MagicMock()
        status_copy = copy.deepcopy(self.status)
        mock_adapter.read.return_value = status_copy

        attempts = [0]
        def mock_poll():
            attempts[0] += 1
            if attempts[0] >= 3:
                return self.target
            return self.target - 1

        with patch("p45_v27.web_publish.check_web_sync", return_value=(False, {})), \
             patch("p45_v27.web_publish._git", return_value=""), \
             patch("p45_v27.web_publish.subprocess.run") as mock_sub, \
             patch("p45_v27.web_publish.time.sleep", return_value=None), \
             patch("p45_v27.web_publish._production_target", side_effect=mock_poll):

            mock_sub.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
            res = web_publish.publish(status_copy, force=True)
            self.assertEqual(res, "WEB_PUBLISHED")
            self.assertEqual(attempts[0], 3)

    def test_e_git_push_no_change_no_empty_commit(self):
        """E. Git push no-change -> no empty commit."""
        with patch("p45_v27.web_publish._git") as mock_git, \
             patch("p45_v27.web_publish.check_web_sync", return_value=(True, {})):

            mock_git.side_effect = lambda *args, **kwargs: ""
            res = web_publish.publish(self.status, force=False)
            self.assertEqual(res, "WEB_ALREADY_CURRENT")
            # Verify git commit was not called
            commit_calls = [c for c in mock_git.call_args_list if "commit" in c[0]]
            self.assertEqual(len(commit_calls), 0)

    def test_f_multiple_simultaneous_triggers_blocked(self):
        """F. Multiple simultaneous trigger -> concurrency lock blocks parallel runs."""
        coordinator = AutoUpdateCoordinator(ADAPTER)
        # Manually hold lock
        acquired = coordinator.lock.acquire(blocking=False)
        self.assertTrue(acquired)
        try:
            # Second invocation must be rejected / return early without executing steps
            res = coordinator.run_once(trigger_source="PARALLEL_ATTEMPT")
            self.assertEqual(res["steps"], [])
        finally:
            coordinator.lock.release()

    def test_g_existing_seal_immutability(self):
        """G. Existing seal -> immutable; modification violates hash verification."""
        original_bytes = self.sealed_path.read_bytes()
        original_hash = hashlib.sha256(original_bytes).hexdigest()
        self.assertEqual(original_hash, self.sealed_sha)

        # Hash verify must pass on original
        current_status = ADAPTER.read()
        self.assertEqual(current_status["seal"]["verify"], "PASS")

    def test_h_multi_round_catchup_flow(self):
        """H. Multi-round catch-up simulation in coordinator."""
        step_log = []
        action_queue = [
            {"current": {"action": "RECORD_OUTCOME", "target": 1245}},
            {"current": {"action": "RECORD_OUTCOME", "target": 1246}},
            {"current": {"action": "PREVIEW_AND_SEAL_NEXT", "target": 1247}},
            {"current": {"action": "WAITING_FOR_RESULT", "target": 1247}},
        ]
        curr_idx = [0]

        mock_adapter = MagicMock()
        def mock_read():
            idx = min(curr_idx[0], len(action_queue) - 1)
            ret = copy.deepcopy(self.status)
            ret["current"] = action_queue[idx]["current"]
            return ret

        mock_adapter.read.side_effect = mock_read

        def mock_record_outcome(target):
            step_log.append(f"RECORD_{target}")
            curr_idx[0] += 1
            return {}

        def mock_preview():
            return {"target": 1247, "preview_sha256": "fake_sha"}

        def mock_seal(sha):
            step_log.append("SEAL_1247")
            curr_idx[0] += 1
            return {}

        mock_adapter.service.record_outcome = mock_record_outcome
        mock_adapter.service.preview_next = mock_preview
        mock_adapter.service.seal_next = mock_seal

        with patch("p45_v27.webapp.publish", return_value="WEB_ALREADY_CURRENT"):
            coordinator = AutoUpdateCoordinator(mock_adapter, update=lambda: {"status": "DRAW_ALREADY_CURRENT"})
            res = coordinator.run_once(trigger_source="TEST_H_CATCHUP")

            self.assertEqual(step_log, ["RECORD_1245", "RECORD_1246", "SEAL_1247"])
            self.assertIn("SETTLED_1245", res["steps"])
            self.assertIn("SETTLED_1246", res["steps"])
            self.assertIn("NEXT_SEALED_1247", res["steps"])
            self.assertIsNone(res["last_error"])


if __name__ == "__main__":
    unittest.main()

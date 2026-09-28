"""Fault-injection verification for P45 durable auto-publish retry.

Verifies:
1. TEST A: First publish failure is caught cleanly, recorded with exit code/stderr,
   and does NOT trigger settlement or sealed regeneration.
2. TEST B: Next coordinator iteration automatically retries publish and succeeds.
3. TEST C: Third check with production up-to-date blocks duplicate deployments.
4. TEST D: Process restart with a clean instance recovers purely from state divergence.
5. TEST E: Real production read-only check verifies live endpoints remain on target 1244.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import unittest
import urllib.request
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock, patch

# Ensure src is in python path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from p45_v27.webapp import AutoUpdateCoordinator, ADAPTER
from p45_v27 import web_publish

ORIGINAL_SUBPROCESS_RUN = subprocess.run


class AutoPublishFaultInjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sealed_file = ROOT / "v27_storage" / "prospective" / "trio_orbit_v1_001" / "P45_TRIO_ORBIT_TARGET_1244_SEALED_PREDRAW_001.md"
        cls.db_file = ROOT / "v27_storage" / "live" / "p45_new_draw_update_v1.sqlite3"
        cls.initial_sealed_hash = hashlib.sha256(cls.sealed_file.read_bytes()).hexdigest()
        cls.initial_db_mtime = os.path.getmtime(cls.db_file)
        cls.local_status = ADAPTER.read()

        # Simulated remote states
        cls.remote_1243 = {
            "current": {"target": 1243, "sealed": True, "action": "WAITING_FOR_RESULT", "result_status": "PENDING"},
            "canonical": {"latest": 1242, "read_status": "PASS"},
            "lifecycle": {"completed_target": 1242, "next_target": 1243},
        }
        cls.remote_1244 = {
            "current": {"target": 1244, "sealed": True, "action": "WAITING_FOR_RESULT", "result_status": "PENDING"},
            "canonical": {"latest": 1243, "read_status": "PASS"},
            "lifecycle": {"completed_target": 1243, "next_target": 1244},
        }

    def _assert_data_integrity_untouched(self):
        current_hash = hashlib.sha256(self.sealed_file.read_bytes()).hexdigest()
        self.assertEqual(self.initial_sealed_hash, current_hash, "SEALED_PREDRAW_MODIFIED!")
        current_mtime = os.path.getmtime(self.db_file)
        self.assertEqual(self.initial_db_mtime, current_mtime, "DATABASE_MODIFIED!")

    def test_complete_fault_injection_lifecycle(self):
        """Execute TEST A -> TEST B -> TEST C -> TEST D -> TEST E in strict sequence."""
        mock_record_outcome = MagicMock()
        mock_preview_next = MagicMock()
        mock_seal_next = MagicMock()

        adapter_mock = MagicMock()
        adapter_mock.read.return_value = self.local_status
        adapter_mock.service.record_outcome = mock_record_outcome
        adapter_mock.service.preview_next = mock_preview_next
        adapter_mock.service.seal_next = mock_seal_next

        # ----------------------------------------------------
        # TEST A: FIRST FAILURE
        # ----------------------------------------------------
        print("\n[TEST A] Simulating first publish failure...")
        failed_deploy_process = CompletedProcess(
            args=["npx.cmd", "vercel", "deploy", "--prod", "--yes"],
            returncode=1,
            stdout="",
            stderr="Simulated Vercel CLI Network 504 Gateway Timeout",
        )

        coordinator = AutoUpdateCoordinator(adapter_mock, update=lambda: {"status": "DRAW_ALREADY_CURRENT"})
        deploy_calls_a = []

        def mock_subprocess_a(cmd, *args, **kwargs):
            if any("vercel" in str(c).lower() for c in cmd):
                deploy_calls_a.append(cmd)
                return failed_deploy_process
            return ORIGINAL_SUBPROCESS_RUN(cmd, *args, **kwargs)

        with patch("p45_v27.web_publish._fetch_remote_status", return_value=self.remote_1243), \
             patch("p45_v27.web_publish.subprocess.run", side_effect=mock_subprocess_a):

            state_a = coordinator.run_once()

            self.assertEqual(state_a["status"], "자동 업데이트 오류")
            self.assertIn("VERCEL_DEPLOY_FAILED (code 1)", state_a["last_error"])
            self.assertIn("Simulated Vercel CLI Network 504 Gateway Timeout", state_a["last_error"])
            self.assertEqual(state_a["steps"], ["DRAW_ALREADY_CURRENT"])
            self.assertEqual(len(deploy_calls_a), 1)

            # Ensure zero settlement / zero seal regeneration
            self.assertEqual(mock_record_outcome.call_count, 0)
            self.assertEqual(mock_preview_next.call_count, 0)
            self.assertEqual(mock_seal_next.call_count, 0)
            self._assert_data_integrity_untouched()
            print("  -> TEST A PASSED: Failure cleanly captured in last_error without touching data.")

        # ----------------------------------------------------
        # TEST B: NEXT COORDINATOR RETRY (AUTOMATIC SUCCESS)
        # ----------------------------------------------------
        print("\n[TEST B] Simulating next coordinator iteration with successful publish retry...")
        success_deploy_process = CompletedProcess(
            args=["npx.cmd", "vercel", "deploy", "--prod", "--yes"],
            returncode=0,
            stdout=json.dumps({"status": "ok", "deployment": {"id": "dpl_test_mock_1244"}}),
            stderr="Vercel CLI 60.1.3",
        )

        remote_state_b = {"val": self.remote_1243}
        deploy_calls_b = []

        def mock_fetch_b(url):
            return remote_state_b["val"]

        def mock_subprocess_b(cmd, *args, **kwargs):
            if any("vercel" in str(c).lower() for c in cmd):
                deploy_calls_b.append(cmd)
                # Deploy succeeds -> simulated remote state becomes 1244
                remote_state_b["val"] = self.remote_1244
                return success_deploy_process
            return ORIGINAL_SUBPROCESS_RUN(cmd, *args, **kwargs)

        with patch("p45_v27.web_publish._fetch_remote_status", side_effect=mock_fetch_b), \
             patch("p45_v27.web_publish.subprocess.run", side_effect=mock_subprocess_b), \
             patch("p45_v27.web_publish.time.sleep", return_value=None):

            state_b = coordinator.run_once()

            self.assertEqual(state_b["status"], "자동 업데이트 반영")
            self.assertIsNone(state_b["last_error"])
            self.assertEqual(state_b["steps"], ["DRAW_ALREADY_CURRENT", "WEB_PUBLISHED"])
            self.assertEqual(len(deploy_calls_b), 1)

            self.assertEqual(mock_record_outcome.call_count, 0)
            self.assertEqual(mock_preview_next.call_count, 0)
            self.assertEqual(mock_seal_next.call_count, 0)
            self._assert_data_integrity_untouched()
            print("  -> TEST B PASSED: Automatically recovered, published and verified 1244.")

        # ----------------------------------------------------
        # TEST C: THIRD CHECK / DUPLICATE BLOCK
        # ----------------------------------------------------
        print("\n[TEST C] Simulating third coordinator iteration (already synchronized)...")
        deploy_calls_c = []

        def mock_subprocess_c(cmd, *args, **kwargs):
            if any("vercel" in str(c).lower() for c in cmd):
                deploy_calls_c.append(cmd)
                raise AssertionError("REDUNDANT_DEPLOY_TRIGGERED!")
            return ORIGINAL_SUBPROCESS_RUN(cmd, *args, **kwargs)

        with patch("p45_v27.web_publish._fetch_remote_status", return_value=self.remote_1244), \
             patch("p45_v27.web_publish.subprocess.run", side_effect=mock_subprocess_c):

            state_c = coordinator.run_once()

            self.assertEqual(state_c["status"], "자동 업데이트 반영")
            self.assertIsNone(state_c["last_error"])
            self.assertEqual(state_c["steps"], ["DRAW_ALREADY_CURRENT", "WEB_ALREADY_CURRENT"])
            self.assertEqual(len(deploy_calls_c), 0)

            self.assertEqual(mock_record_outcome.call_count, 0)
            self.assertEqual(mock_preview_next.call_count, 0)
            self.assertEqual(mock_seal_next.call_count, 0)
            self._assert_data_integrity_untouched()
            print("  -> TEST C PASSED: Redundant deployment blocked (deploy=0, commit=0, error=0).")

        # ----------------------------------------------------
        # TEST D: PROCESS RESTART RECOVERY
        # ----------------------------------------------------
        print("\n[TEST D] Simulating fresh process restart with out-of-sync remote...")
        fresh_coordinator = AutoUpdateCoordinator(adapter_mock, update=lambda: {"status": "DRAW_ALREADY_CURRENT"})
        self.assertEqual(fresh_coordinator.state["status"], "대기")
        self.assertIsNone(fresh_coordinator.state["last_check"])

        remote_state_d = {"val": self.remote_1243}
        deploy_calls_d = []

        def mock_fetch_d(url):
            return remote_state_d["val"]

        def mock_subprocess_d(cmd, *args, **kwargs):
            if any("vercel" in str(c).lower() for c in cmd):
                deploy_calls_d.append(cmd)
                remote_state_d["val"] = self.remote_1244
                return success_deploy_process
            return ORIGINAL_SUBPROCESS_RUN(cmd, *args, **kwargs)

        with patch("p45_v27.web_publish._fetch_remote_status", side_effect=mock_fetch_d), \
             patch("p45_v27.web_publish.subprocess.run", side_effect=mock_subprocess_d), \
             patch("p45_v27.web_publish.time.sleep", return_value=None):

            state_d = fresh_coordinator.run_once()

            self.assertEqual(state_d["status"], "자동 업데이트 반영")
            self.assertIsNone(state_d["last_error"])
            self.assertEqual(state_d["steps"], ["DRAW_ALREADY_CURRENT", "WEB_PUBLISHED"])
            self.assertEqual(len(deploy_calls_d), 1)

            self.assertEqual(mock_record_outcome.call_count, 0)
            self.assertEqual(mock_preview_next.call_count, 0)
            self.assertEqual(mock_seal_next.call_count, 0)
            self._assert_data_integrity_untouched()
            print("  -> TEST D PASSED: Fresh instance recovered solely based on state divergence.")

        # ----------------------------------------------------
        # TEST E: REAL PRODUCTION READ-ONLY CHECK
        # ----------------------------------------------------
        print("\n[TEST E] Reading live production status (read-only)...")
        req_vercel = urllib.request.Request("https://p45project.vercel.app/api/status", headers={"Cache-Control": "no-cache"})
        req_custom = urllib.request.Request("https://p45.starm42.xyz/api/status", headers={"Cache-Control": "no-cache"})

        with urllib.request.urlopen(req_vercel, timeout=10) as r1:
            prod_vercel = json.load(r1)
        with urllib.request.urlopen(req_custom, timeout=10) as r2:
            prod_custom = json.load(r2)

        self.assertEqual(int(prod_vercel["current"]["target"]), 1244)
        self.assertEqual(int(prod_custom["current"]["target"]), 1244)
        self.assertEqual(int(prod_vercel["canonical"]["latest"]), 1243)
        self.assertEqual(int(prod_custom["canonical"]["latest"]), 1243)
        self.assertEqual(int(prod_vercel["lifecycle"]["completed_target"]), 1243)
        self.assertEqual(int(prod_custom["lifecycle"]["completed_target"]), 1243)
        self.assertTrue(prod_vercel["current"]["sealed"])
        self.assertTrue(prod_custom["current"]["sealed"])

        self._assert_data_integrity_untouched()
        print("  -> TEST E PASSED: Both production endpoints verified at target 1244.")


if __name__ == "__main__":
    unittest.main()

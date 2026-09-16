import hashlib
import unittest
from pathlib import Path

from p45_v27.prospective_web import ProspectiveOrbitService
from p45_v27.lan_ip import detect_lan_ipv4


ROOT = Path(__file__).resolve().parents[1]


class WebExecutionPathFix001Tests(unittest.TestCase):
    def test_append_only_target_versions_collapse_in_read_projection(self):
        protected = [
            ROOT / "v27_storage/prospective/trio_orbit_v1_001/P45_TRIO_ORBIT_PROSPECTIVE_LOG_001.csv",
            ROOT / "v27_storage/prospective/trio_orbit_v1_001/P45_TRIO_ORBIT_PROSPECTIVE_STATE_002.json",
            ROOT / "v27_storage/prospective/trio_orbit_v1_001/P45_TRIO_ORBIT_TARGET_1239_SEALED_PREDRAW_001.md",
        ]
        before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in protected]
        status = ProspectiveOrbitService(ROOT).read()
        after = [hashlib.sha256(path.read_bytes()).hexdigest() for path in protected]
        self.assertEqual(before, after)
        targets = [int(row["target_round"]) for row in status["prospective"]["rows"]]
        self.assertEqual(len(targets), len(set(targets)))
        self.assertEqual(targets.count(1239), 1)
        self.assertEqual(status["prospective"]["completed_rounds"], 2)
        self.assertEqual(status["prospective"]["fixed_exact2"], 2)
        self.assertIn(status["current"]["result_status"], {"OUTCOME_RECORDED", "PENDING"})

    def test_phone_launcher_uses_command_form_not_usebackq(self):
        launcher = (ROOT / "P45 휴대폰 미리보기.cmd").read_text(encoding="utf-8-sig")
        self.assertNotIn('for /f "usebackq delims="', launcher.lower())
        self.assertIn('-m p45_v27.lan_ip', launcher)
        self.assertIn('p45_v27.webapp --host 0.0.0.0 --port 8045', launcher)

    def test_lan_detector_returns_non_loopback_ipv4(self):
        value = detect_lan_ipv4()
        self.assertRegex(value, r"^\d{1,3}(?:\.\d{1,3}){3}$")
        self.assertFalse(value.startswith("127."))


if __name__ == "__main__":
    unittest.main()

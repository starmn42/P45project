from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from p45_v27.prospective_web import ProspectiveOrbitService


ROOT = Path(__file__).resolve().parents[1]


class WebFinal1240Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ProspectiveOrbitService(ROOT)
        self.status = self.service.read()

    def test_completed_1239_is_not_presented_as_current_future_round(self):
        current = self.status["current"]
        lifecycle = self.status["lifecycle"]
        self.assertEqual(1240, lifecycle["completed_target"])
        self.assertEqual(1241, current["target"])
        self.assertEqual(1241, lifecycle["display_target"])
        self.assertEqual("PENDING", current["result_status"])

    def test_next_target_tracks_canonical(self):
        self.assertEqual(self.status["canonical"]["latest"] + 1, self.status["lifecycle"]["next_target"])

    def test_preview_route_and_frontend_action_are_connected(self):
        server = (ROOT / "src/p45_v27/webapp.py").read_text(encoding="utf-8")
        app = (ROOT / "web/app.js").read_text(encoding="utf-8")
        self.assertIn('/api/prospective/preview', server)
        self.assertIn('/api/prospective/preview', app)
        self.assertIn('previewNext', app)

    def test_seal_route_and_frontend_action_are_connected(self):
        server = (ROOT / "src/p45_v27/webapp.py").read_text(encoding="utf-8")
        app = (ROOT / "web/app.js").read_text(encoding="utf-8")
        self.assertIn('/api/prospective/seal', server)
        self.assertIn('/api/prospective/seal', app)
        self.assertIn('sealNext', app)

    def test_stale_exp017_not_created_is_absent(self):
        app = (ROOT / "web/app.js").read_text(encoding="utf-8")
        service = (ROOT / "src/p45_v27/prospective_web.py").read_text(encoding="utf-8")
        self.assertNotIn('NOT_CREATED', app)
        self.assertNotIn('"exp017":"NOT_CREATED"', service)
        self.assertEqual("EXP-020", self.status["operation"]["latest_exp"])
        self.assertEqual("FAILED_NO_SELECTION_SIGNAL", self.status["operation"]["latest_exp_status"])

    def test_projection_has_one_row_per_target(self):
        targets = [int(row["target_round"]) for row in self.status["prospective"]["rows"]]
        self.assertEqual(len(targets), len(set(targets)))
        if self.status["current"]["target"] == 1241:
            self.assertEqual(2, self.status["prospective"]["completed_rounds"])
            self.assertEqual(1, self.status["prospective"]["pending_count"])

    def test_luck_principle_is_present(self):
        html = (ROOT / "web/index.html").read_text(encoding="utf-8")
        self.assertIn('<div class="drawer-title"><span>P45</span><h1>운칠기삼</h1><small>TRIO ORBIT</small></div>', html)
        self.assertEqual(1, html.count("<h1>운칠기삼</h1>"))
        self.assertNotIn("luck-principle", html)

    def test_read_does_not_change_protected_1239(self):
        files = [
            ROOT / "v27_storage/prospective/trio_orbit_v1_001/P45_TRIO_ORBIT_TARGET_1239_SEALED_PREDRAW_001.md",
            ROOT / "v27_storage/prospective/trio_orbit_v1_001/P45_TRIO_ORBIT_TARGET_1239_SETTLEMENT_001.json",
        ]
        before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in files]
        self.service.read()
        after = [hashlib.sha256(path.read_bytes()).hexdigest() for path in files]
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()

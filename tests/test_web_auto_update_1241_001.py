from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from p45_v27.prospective_web import ProspectiveOrbitService
from p45_v27.webapp import AutoUpdateCoordinator


ROOT = Path(__file__).resolve().parents[1]


class FakeService:
    def __init__(self):
        self.phase = 0
        self.recorded = []
        self.sealed = []

    def record_outcome(self, target):
        self.recorded.append(target); self.phase = 1

    def preview_next(self):
        return {"target": 1241, "preview_sha256": "locked"}

    def seal_next(self, sha):
        self.sealed.append(sha); self.phase = 2


class FakeAdapter:
    def __init__(self): self.service = FakeService()
    def read(self):
        actions = ["RECORD_OUTCOME", "PREVIEW_AND_SEAL_NEXT", "WAITING_FOR_RESULT"]
        return {"current": {"target": 1240, "action": actions[self.service.phase]}}


class WebAutoUpdate1241Tests(unittest.TestCase):
    def test_update_settlement_and_seal_chain(self):
        adapter = FakeAdapter()
        coordinator = AutoUpdateCoordinator(adapter, update=lambda: {"status": "DRAW_READY"})
        result = coordinator.run_once()
        self.assertEqual([1240], adapter.service.recorded)
        self.assertEqual(["locked"], adapter.service.sealed)
        self.assertEqual(["DRAW_READY", "SETTLED", "NEXT_SEALED"], result["steps"])

    def test_real_projection_is_1241_with_1240_result(self):
        status = ProspectiveOrbitService(ROOT).read()
        self.assertEqual(1240, status["canonical"]["latest"])
        self.assertEqual(1241, status["current"]["target"])
        self.assertEqual("PENDING", status["current"]["result_status"])
        result = status["latest_result"]
        self.assertEqual([11, 13, 19, 20, 31, 44], result["main"])
        self.assertEqual(27, result["bonus"])
        self.assertEqual(([2, 0, 1], [0, 0, 1]),
                         ([x["hits"] for x in result["fixed"]], [x["hits"] for x in result["linked"]]))
        self.assertEqual((0, 1, 0, 0), (result["fixed_primary"], result["fixed_support"], result["linked_primary"], result["linked_support"]))

    def test_duplicate_cycle_is_no_write(self):
        service = ProspectiveOrbitService(ROOT)
        watched = [service.log_path, service._latest_state_path(), service._latest_sealed(),
                   service.prospective_root / "P45_TRIO_ORBIT_TARGET_1240_SETTLEMENT_001.json"]
        before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in watched]
        status = service.read()
        self.assertEqual("WAITING_FOR_RESULT", status["current"]["action"])
        after = [hashlib.sha256(path.read_bytes()).hexdigest() for path in watched]
        self.assertEqual(before, after)

    def test_home_contains_requested_korean_ui(self):
        html = (ROOT / "web/index.html").read_text(encoding="utf-8")
        app = (ROOT / "web/app.js").read_text(encoding="utf-8")
        for text in ("지난회차 결과 보기", "다음회차 출격 보기", "픽 기준 회차", "추천픽 결과 요약", "세트별 적중 결과", "주적중(3/3)", "보조적중(2/3)"):
            self.assertIn(text, html)
        self.assertIn("hit-number", app)


if __name__ == "__main__":
    unittest.main()

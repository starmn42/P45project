"""Read-only web projection of the frozen P45 operation state."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any
from .draw_update import read_live_status

EXPECTED_STATUS = "P45_RESEARCH_ENGINE_FROZEN_WEB_READY"

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""): digest.update(block)
    return digest.hexdigest()

class FrozenWebAdapter:
    """Expose one safe JSON view without interpreting research databases."""
    def __init__(self, project_root: Path) -> None:
        self.root = Path(project_root)
        self.state_path = self.root / "00_P45_STATE" / "P45_CURRENT_STATE.json"
        self.report_path = self.root / "v27_storage" / "reports" / "p45_v274_pair_v12_final_aggregation.json"

    def read(self) -> dict[str, Any]:
        state = json.loads(self.state_path.read_text(encoding="utf-8-sig")); pair = state["pair_state"]
        if pair.get("research_engine_frozen") is not True: raise RuntimeError("P45_WEB_STATE_NOT_FROZEN")
        if int(pair.get("final_valid_for_core_count", -1)) != 0: raise RuntimeError("P45_WEB_CORE_STATE_CONFLICT")
        if pair.get("official_final_six") != "NONE": raise RuntimeError("P45_WEB_FINAL_NUMBERS_CONFLICT")
        report = json.loads(self.report_path.read_text(encoding="utf-8"))
        metrics = report.get("historical_metrics", {})
        metric_keys = {
            "integrated_primary": "INTEGRATED_PRIMARY|TOTAL",
            "integrated_support": "INTEGRATED_SUPPORT|TOTAL",
            "main_primary": "MAIN_PRIMARY|TOTAL",
            "main_support": "MAIN_SUPPORT|TOTAL",
        }
        performance = {}
        for name, key in metric_keys.items():
            item = metrics[key]
            performance[name] = {
                "success_count": int(item["success_count"]),
                "sample_count": int(item["sample_count"]),
                "rate": float(item["rate"]),
                "evidence": str(item["evidence_label"]),
            }
        diagnostics = [{"rank": item["rank"], "pair_key": item["pair"], "set_1": list(item["set1"]),
          "set_2": list(item["set2"]), "label": "DIAGNOSTIC ONLY", "official_recommendation": False}
          for item in report.get("ranking", [])[:3]]
        live = read_live_status()
        if live:
            diagnostics = live["diagnostic_top3"]
            pair_counts = live["pair_state_counts"]
            official = list(live["official_selection"])
            latest_evaluation = int(live["current_analysis_draw"])
            latest_completed = int(live["latest_completed_draw"])
        else:
            pair_counts = {"ready":int(pair["final_ready_count"]),"test_ready":int(pair["final_test_ready_count"]),
              "research_hold":int(pair["final_research_hold_count"]),"system_hold":int(pair["final_system_hold_count"])}
            official=[];latest_evaluation=int(pair["final_aggregation_round"]);latest_completed=latest_evaluation-1
        return {"app":"P45","project_version":state["project_version"],"engine_status":EXPECTED_STATUS,
          "current_state":"RESEARCH_HOLD","latest_evaluation_round":latest_evaluation,
          "official_core_available":bool(official),"official_final_numbers":official,"official_message":"공식 선택 생성 완료" if official else "CORE 조건을 충족한 후보가 없습니다.",
          "pair_state_counts":pair_counts,
          "valid_for_core":int(live["valid_for_core"] if live else pair["final_valid_for_core_count"]),"selection_exposure":int(report["historical_selection_exposure"]),
          "state_updated_at":state["updated_at"],"historical_performance":performance,"diagnostic_top_pairs":diagnostics,
          "latest_completed_draw":latest_completed,"current_analysis_draw":latest_evaluation,
          "draw_update_status":live["draw_update_status"] if live else "NOT_RUN","last_update_time":live["last_update_time"] if live else None,
          "official_selection":official,"diagnostic_top3":diagnostics,
          "provenance":{"source":"P45_CURRENT_STATE + FINAL_AGGREGATION_REPORT","state_version":state["state_version"],
            "state_hash":state["state_hash"],"decision_id":state["last_decision_id"],
            "signature_version":pair["official_signature_version"],"context_version":pair["official_context_fingerprint_version"],
            "walkforward_run_id":pair["v12_walkforward_run_id"],"walkforward_db_sha256":pair["v12_walkforward_db_sha256"],
            "aggregation_hash":pair["final_aggregation_hash"],"aggregation_report_sha256":_sha256(self.report_path),"read_only":True}}

from pathlib import Path
from math import isclose

from p45_v27.web_adapter import FrozenWebAdapter

ROOT = Path(__file__).resolve().parents[1]


def test_frozen_adapter_keeps_official_and_diagnostic_separate():
    value = FrozenWebAdapter(ROOT).read()
    assert value["engine_status"] == "P45_RESEARCH_ENGINE_FROZEN_WEB_READY"
    assert value["official_core_available"] is False
    assert value["official_final_numbers"] == []
    assert value["valid_for_core"] == 0
    assert value["pair_state_counts"] == {"ready": 0, "test_ready": 0, "research_hold": 10, "system_hold": 0}
    assert len(value["diagnostic_top_pairs"]) == 3
    assert all(item["label"] == "DIAGNOSTIC ONLY" and item["official_recommendation"] is False for item in value["diagnostic_top_pairs"])
    assert value["selection_exposure"] == 258
    performance = value["historical_performance"]
    assert [(performance[key]["success_count"], performance[key]["sample_count"], performance[key]["evidence"]) for key in performance] == [
        (1, 258, "INFERIOR_TENTATIVE"),
        (44, 258, "SUPERIOR_CONFIRMED"),
        (1, 258, "SUPERIOR_TENTATIVE"),
        (29, 258, "SUPERIOR_TENTATIVE"),
    ]
    assert isclose(performance["integrated_primary"]["rate"], 1 / 258)
    assert isclose(performance["integrated_support"]["rate"], 44 / 258)
    assert isclose(performance["main_primary"]["rate"], 1 / 258)
    assert isclose(performance["main_support"]["rate"], 29 / 258)


def test_adapter_is_deterministic_and_read_only():
    adapter = FrozenWebAdapter(ROOT)
    before = (ROOT / "00_P45_STATE" / "P45_CURRENT_STATE.json").read_bytes()
    values = [adapter.read() for _ in range(10)]
    after = (ROOT / "00_P45_STATE" / "P45_CURRENT_STATE.json").read_bytes()
    assert all(value == values[0] for value in values)
    assert before == after
    assert values[0]["provenance"]["read_only"] is True

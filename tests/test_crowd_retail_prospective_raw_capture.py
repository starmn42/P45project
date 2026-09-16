import json
from pathlib import Path

from p45_experiments.crowd_retail_prospective_raw_capture import parse, persist_record, static_signal_blind_guard


def payload(mode="수동", name="상점", address="서울 1", store_id="1"):
    return json.dumps({"data":{"total":1,"list":[{"rnum":1,"shpNm":name,"shpAddr":address,
        "atmtPsvYn":"M","atmtPsvYnTxt":mode,"ltShpId":store_id}]}}, ensure_ascii=False).encode()


def test_schema_and_signal_guard():
    assert static_signal_blind_guard()["signal_calculation_code_paths"] == 0
    assert parse(payload(), 1239, "T")["official_first_prize_row_total"] == 1


def test_equal_hash_no_write(tmp_path: Path):
    ledger, corrections, raw = tmp_path/"ledger.jsonl", tmp_path/"corrections.jsonl", tmp_path/"raw"
    data=payload(); record=parse(data,1239,"T")
    assert persist_record(record,data,ledger,corrections,raw)["status"] == "CAPTURED"
    assert persist_record(record,data,ledger,corrections,raw)["status"] == "NO_WRITE"
    assert len(ledger.read_text(encoding="utf-8").splitlines()) == 1


def test_correction_is_append_only(tmp_path: Path):
    ledger, corrections, raw = tmp_path/"ledger.jsonl", tmp_path/"corrections.jsonl", tmp_path/"raw"
    first=payload(); second=payload(name="정정상점")
    persist_record(parse(first,1239,"T1"),first,ledger,corrections,raw)
    result=persist_record(parse(second,1239,"T2"),second,ledger,corrections,raw)
    assert result["status"] == "CORRECTION_APPENDED"
    assert len(ledger.read_text(encoding="utf-8").splitlines()) == 2
    assert len(corrections.read_text(encoding="utf-8").splitlines()) == 1

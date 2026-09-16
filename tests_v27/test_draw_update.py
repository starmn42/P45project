import json, sqlite3
from pathlib import Path
import pytest

from p45_v27.draw_update import Draw, parse_official, validate_draw, _evaluation, _connect

def payload(round_=1236, main=(12,18,21,29,34,38), bonus=10):
    row={"ltEpsd":round_,"ltRflYmd":"20260808","bnsWnNo":bonus}
    row.update({f"tm{i}WnNo":n for i,n in enumerate(main,1)})
    return json.dumps({"data":{"list":[row]}}).encode()

def test_official_parse_and_all_number_rules():
    draw=parse_official(payload(),1236);validate_draw(draw,1235)
    assert draw.main==(12,18,21,29,34,38) and draw.bonus==10
    for main,bonus in [((1,1,2,3,4,5),6),((0,2,3,4,5,6),7),((1,2,3,4,5,6),6)]:
        with pytest.raises(ValueError):validate_draw(Draw(1236,"2026-08-08",main,bonus,"x","h"),1235)

def test_round_must_be_exactly_next():
    with pytest.raises(ValueError,match="CONTIGUOUS"):validate_draw(parse_official(payload(1237),1237),1235)

def test_primary_and_exact2_are_separate():
    draw=parse_official(payload(),1236)
    primary=_evaluation("PAIR","p",(12,18,21),(1,2,3),draw)
    support=_evaluation("PAIR","s",(12,18,40),(1,2,3),draw)
    assert (primary["ip"],primary["is"])==(1,0)
    assert (support["ip"],support["is"])==(0,1)

def test_schema_integrity_fk_and_unique(tmp_path:Path):
    db=_connect(tmp_path/"live.sqlite3")
    assert db.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
    assert db.execute("PRAGMA foreign_key_check").fetchall()==[]
    db.execute("INSERT INTO draw_result VALUES(?,?,?,?,?,?,?)",(1236,"2026-08-08","[12,18,21,29,34,38]",10,"u","h","t"));db.commit()
    with pytest.raises(sqlite3.IntegrityError):db.execute("INSERT INTO draw_result VALUES(?,?,?,?,?,?,?)",(1236,"2026-08-08","[]",10,"u","h","t"))
    db.close()

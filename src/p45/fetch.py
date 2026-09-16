from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .data import REQUIRED_COLUMNS


OFFICIAL_ORIGIN = "https://www.dhlottery.co.kr"
RESULT_PAGE_URL = f"{OFFICIAL_ORIGIN}/lt645/result"
RESULT_API_URL = f"{OFFICIAL_ORIGIN}/lt645/selectPstLt645InfoNew.do"
USER_AGENT = "P45-Research-Engine/0.2 (+official-result-collector)"


class FetchError(RuntimeError):
    """공식 자료를 안전하게 확정할 수 없을 때 발생합니다."""


@dataclass(frozen=True)
class OfficialDraw:
    round: int
    draw_date: date
    main: tuple[int, int, int, int, int, int]
    bonus: int


Transport = Callable[[str], bytes]


def _default_transport(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
            "Referer": RESULT_PAGE_URL,
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            return response.read()
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise FetchError(f"공식 사이트 연결 실패: {exc}") from exc


def _decode(payload: bytes) -> str:
    for encoding in ("utf-8", "euc-kr"):
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise FetchError("공식 응답의 문자 인코딩을 확인할 수 없습니다.")


def discover_latest_round(payload: bytes) -> int:
    text = _decode(payload)
    if "/lt645/result" not in text and "추첨결과" not in text:
        raise FetchError("공식 결과 페이지 형식이 예상과 다릅니다.")
    candidates = [int(value) for value in re.findall(r'(?:data-value|value)=["\'](\d+)["\']', text)]
    if not candidates:
        candidates = [int(value) for value in re.findall(r"제\s*(\d+)회\s*추첨\s*결과", text)]
    if not candidates:
        raise FetchError("공식 결과 페이지에서 최신 회차를 찾지 못했습니다.")
    return max(candidates)


def _unwrap_list(document: object) -> list[dict[str, object]]:
    if not isinstance(document, dict):
        raise FetchError("공식 API 응답이 JSON 객체가 아닙니다.")
    data = document.get("data")
    if isinstance(data, dict) and isinstance(data.get("list"), list):
        return data["list"]
    # 일부 공통 응답 래퍼는 result 아래에 data를 둔다.
    result = document.get("result")
    if isinstance(result, dict):
        nested = result.get("data")
        if isinstance(nested, dict) and isinstance(nested.get("list"), list):
            return nested["list"]
    raise FetchError("공식 API 응답에서 당첨 결과 목록을 찾지 못했습니다.")


def parse_api_page(payload: bytes) -> list[OfficialDraw]:
    try:
        document = json.loads(_decode(payload))
    except json.JSONDecodeError as exc:
        raise FetchError("공식 API가 올바른 JSON을 반환하지 않았습니다.") from exc

    required = {
        "ltEpsd", "ltRflYmd", "tm1WnNo", "tm2WnNo", "tm3WnNo",
        "tm4WnNo", "tm5WnNo", "tm6WnNo", "bnsWnNo",
    }
    draws: list[OfficialDraw] = []
    for index, item in enumerate(_unwrap_list(document), start=1):
        if not isinstance(item, dict) or not required.issubset(item):
            missing = sorted(required - set(item) if isinstance(item, dict) else required)
            raise FetchError(f"공식 API {index}번째 항목의 필드가 부족합니다: {missing}")
        try:
            round_no = int(item["ltEpsd"])
            raw_date = str(item["ltRflYmd"]).strip().replace(".", "-")
            if re.fullmatch(r"\d{8}", raw_date):
                raw_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
            draw_date = date.fromisoformat(raw_date)
            main = tuple(int(item[f"tm{i}WnNo"]) for i in range(1, 7))
            bonus = int(item["bnsWnNo"])
        except (TypeError, ValueError) as exc:
            raise FetchError(f"공식 API {index}번째 항목의 값 형식이 잘못되었습니다.") from exc
        if round_no < 1 or len(set(main)) != 6 or any(not 1 <= n <= 45 for n in (*main, bonus)):
            raise FetchError(f"공식 API {round_no}회 번호 값이 유효하지 않습니다.")
        if bonus in main:
            raise FetchError(f"공식 API {round_no}회 보너스번호가 본번호와 중복됩니다.")
        draws.append(OfficialDraw(round_no, draw_date, tuple(sorted(main)), bonus))
    if not draws:
        raise FetchError("공식 API가 빈 결과를 반환했습니다.")
    return draws


def _api_url(direction: str, round_no: int) -> str:
    if direction == "center":
        query = {"srchDir": "center", "srchLtEpsd": str(round_no)}
    else:
        query = {"srchDir": "older", "srchCursorLtEpsd": str(round_no)}
    return f"{RESULT_API_URL}?{urlencode(query)}"


def fetch_official_draws(
    output_root: Path,
    *,
    transport: Transport = _default_transport,
    pause_seconds: float = 0.1,
) -> Path:
    landing_payload = transport(RESULT_PAGE_URL)
    latest_round = discover_latest_round(landing_payload)
    dataset_id = f"official-1-{latest_round}"
    final_dir = output_root / dataset_id
    staging = output_root / f".{dataset_id}.staging"
    if final_dir.exists():
        raise FileExistsError(f"이미 수집된 공식 데이터가 있습니다: {final_dir}")
    if staging.exists():
        raise FileExistsError(f"미완료 수집 묶음이 있습니다: {staging}")

    staging.mkdir(parents=True)
    raw_dir = staging / "raw"
    raw_dir.mkdir()
    try:
        (raw_dir / "result-page.html").write_bytes(landing_payload)
        collected: dict[int, OfficialDraw] = {}
        cursor = latest_round
        direction = "center"
        page_number = 1
        while cursor >= 1:
            payload = transport(_api_url(direction, cursor))
            (raw_dir / f"api-{page_number:04d}.json").write_bytes(payload)
            page = parse_api_page(payload)
            previous_count = len(collected)
            for draw in page:
                existing = collected.get(draw.round)
                if existing is not None and existing != draw:
                    raise FetchError(f"공식 응답 안에서 {draw.round}회 데이터가 충돌합니다.")
                collected[draw.round] = draw
            if len(collected) == previous_count:
                raise FetchError("공식 API가 같은 회차만 반복하여 수집을 중단했습니다.")
            oldest = min(draw.round for draw in page)
            if oldest <= 1:
                break
            cursor = oldest
            direction = "older"
            page_number += 1
            if pause_seconds:
                time.sleep(pause_seconds)

        expected = set(range(1, latest_round + 1))
        missing = sorted(expected - set(collected))
        extra = sorted(set(collected) - expected)
        if missing or extra:
            raise FetchError(f"공식 수집 회차 불연속: 누락={missing[:20]}, 범위초과={extra[:20]}")

        csv_path = staging / "official.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(REQUIRED_COLUMNS)
            for round_no in sorted(collected):
                draw = collected[round_no]
                writer.writerow([draw.round, draw.draw_date.isoformat(), *draw.main, draw.bonus])

        raw_hash = hashlib.sha256()
        for path in sorted(raw_dir.iterdir(), key=lambda p: p.name):
            raw_hash.update(path.name.encode("utf-8"))
            raw_hash.update(path.read_bytes())
        metadata = {
            "source": "동행복권 공식 사이트",
            "source_page": RESULT_PAGE_URL,
            "source_api": RESULT_API_URL,
            "collection_status": "COLLECTED_UNVERIFIED",
            "start_round": 1,
            "end_round": latest_round,
            "draw_count": len(collected),
            "raw_bundle_sha256": raw_hash.hexdigest(),
            "csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
            "collected_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "next_gate": "PHASE_3_DATA_VALIDATION",
        }
        (staging / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        staging.rename(final_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return final_dir

from __future__ import annotations

import csv
import hashlib
import json
import ssl
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
PROTOCOL = EXP_DIR / "P45_EXP_019_SALES_ADJUSTED_BIRTHDAY_CROWD_EFFECT_V1_PROTOCOL_001.md"
LOCK = EXP_DIR / "P45_EXP_019_PROTOCOL_LOCK_001.md"
CANONICAL = ROOT / "v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv"
RAW = EXP_DIR / "P45_EXP_019_OFFICIAL_RAW_BATCHES_001.jsonl"
DATASET = EXP_DIR / "P45_EXP_019_OFFICIAL_CROWD_METADATA_001.csv"
MANIFEST = EXP_DIR / "P45_EXP_019_OFFICIAL_SOURCE_MANIFEST_001.json"

EXPECTED_PROTOCOL_SHA = "220d59aa8c50e11c74f6146061784b8f5e0413c5a7013758a47891404e2f4d5c"
EXPECTED_LOCK_SHA = "fb28b4daed366e4a9448a33c68155bb742a63fecda41a2f6ce37eec30ef32b6a"
EXPECTED_CANONICAL_SHA = "1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8"
ENDPOINT = "https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do"
START = 88
END = 1238
PRICE_PER_GAME = 1000
COMBINATION_UNIVERSE = 8_145_060


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_canonical() -> dict[int, tuple[int, ...]]:
    if sha256(CANONICAL) != EXPECTED_CANONICAL_SHA:
        raise RuntimeError("CANONICAL_SHA_MISMATCH")
    rows: dict[int, tuple[int, ...]] = {}
    with CANONICAL.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            draw = int(row["round"])
            if START <= draw <= END:
                rows[draw] = tuple(sorted(int(row[f"n{i}"]) for i in range(1, 7)))
    if set(rows) != set(range(START, END + 1)):
        raise RuntimeError("CANONICAL_RANGE_MISMATCH")
    return rows


def load_resumable_raw() -> dict[int, dict]:
    records: dict[int, dict] = {}
    if not RAW.exists():
        return records
    with RAW.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            batch = json.loads(line)
            for item in batch["records"]:
                draw = int(item["ltEpsd"])
                if START <= draw <= END:
                    records[draw] = item
    return records


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "P45-EXP019-Official-Data-Preflight/1.0", "Accept": "application/json"})
    context = ssl.create_default_context()
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(request, timeout=30, context=context) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP_{response.status}")
                return json.loads(response.read().decode("utf-8"))
        except Exception as error:
            last_error = error
            if attempt < 3:
                time.sleep(attempt)
    raise RuntimeError(f"DATA_ACQUISITION_BLOCKED: {last_error}")


def acquire() -> tuple[dict[int, dict], list[str]]:
    records = load_resumable_raw()
    urls: list[str] = []
    # The official endpoint serves the latest ten records through the
    # "center" query; subsequent pages use the oldest returned draw as the
    # exclusive "older" cursor.
    if END not in records:
        params = urllib.parse.urlencode({"srchDir": "center", "srchLtEpsd": END})
        url = f"{ENDPOINT}?{params}"
        urls.append(url)
        payload = fetch_json(url)
        official_list = payload.get("data", {}).get("list", [])
        if not official_list:
            raise RuntimeError(f"DATA_ACQUISITION_BLOCKED_EMPTY_CENTER_{END}")
        with RAW.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps({"source_url": url, "records": official_list}, ensure_ascii=False, separators=(",", ":")) + "\n")
        for item in official_list:
            draw = int(item["ltEpsd"])
            if START <= draw <= END:
                records[draw] = item
        time.sleep(0.25)

    cursor = min(records)
    batch_number = 0
    while any(draw not in records for draw in range(START, END + 1)):
        params = urllib.parse.urlencode({"srchDir": "older", "srchCursorLtEpsd": cursor})
        url = f"{ENDPOINT}?{params}"
        urls.append(url)
        expected_batch = set(range(max(1, cursor - 10), cursor))
        if not expected_batch.intersection(range(START, END + 1)).issubset(records):
            payload = fetch_json(url)
            official_list = payload.get("data", {}).get("list", [])
            if not official_list:
                raise RuntimeError(f"DATA_ACQUISITION_BLOCKED_EMPTY_BATCH_CURSOR_{cursor}")
            batch_record = {"source_url": url, "records": official_list}
            with RAW.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(batch_record, ensure_ascii=False, separators=(",", ":")) + "\n")
            for item in official_list:
                draw = int(item["ltEpsd"])
                if START <= draw <= END:
                    records[draw] = item
            time.sleep(0.25)
        cursor -= 10
        batch_number += 1
        if batch_number % 10 == 0:
            print(f"progress batches={batch_number} formal_records={len(records)}", flush=True)
        if cursor < START - 10:
            break
    return records, urls


def official_source_url(draw: int) -> str:
    cursor = ((END + 1 - draw - 1) // 10) * 10
    cursor_value = END + 1 - cursor
    return f"{ENDPOINT}?" + urllib.parse.urlencode({"srchDir": "older", "srchCursorLtEpsd": cursor_value})


def build_dataset(records: dict[int, dict], canonical: dict[int, tuple[int, ...]]) -> dict:
    expected = set(range(START, END + 1))
    missing = sorted(expected - set(records))
    if missing:
        raise RuntimeError(f"DATA_COMPLETENESS_BLOCK:{missing}")
    rows: list[dict] = []
    main_mismatches: list[int] = []
    invalid_sales: list[int] = []
    for draw in range(START, END + 1):
        item = records[draw]
        main6 = tuple(sorted(int(item[f"tm{i}WnNo"]) for i in range(1, 7)))
        if main6 != canonical[draw]:
            main_mismatches.append(draw)
        sales = int(item["wholEpsdSumNtslAmt"])
        if sales % PRICE_PER_GAME:
            invalid_sales.append(draw)
        games_sold = sales // PRICE_PER_GAME
        first_total = int(item.get("rnk1SumWnAmt") or int(item["rnk1WnNope"]) * int(item["rnk1WnAmt"]))
        date_raw = str(item["ltRflYmd"])
        rows.append({
            "draw": draw,
            "draw_date": f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:8]}",
            "main1": main6[0], "main2": main6[1], "main3": main6[2],
            "main4": main6[3], "main5": main6[4], "main6": main6[5],
            "bonus": int(item["bnsWnNo"]),
            "winner_count_1st": int(item["rnk1WnNope"]),
            "first_prize_total_krw": first_total,
            "first_prize_per_game_krw": int(item["rnk1WnAmt"]),
            "total_sales_krw": sales,
            "price_per_game": PRICE_PER_GAME,
            "games_sold": games_sold,
            "lambda_uniform": format(games_sold / COMBINATION_UNIVERSE, ".15g"),
            "birthday_range_count": sum(value <= 31 for value in main6),
            "source_url": official_source_url(draw),
            "source_type": "OFFICIAL_DHLOTTERY_AJAX_JSON",
        })
    if main_mismatches:
        raise RuntimeError(f"DATA_INTEGRITY_BLOCK_MAIN6_MISMATCH:{main_mismatches}")
    if invalid_sales:
        raise RuntimeError(f"DATA_INTEGRITY_BLOCK_PRICE_OR_SALES:{invalid_sales}")

    fieldnames = list(rows[0])
    with DATASET.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    sales_values = [row["total_sales_krw"] for row in rows]
    games_values = [row["games_sold"] for row in rows]
    lambda_values = [float(row["lambda_uniform"]) for row in rows]
    b_values = [row["birthday_range_count"] for row in rows]
    return {
        "rows": rows,
        "main_mismatches": main_mismatches,
        "invalid_sales": invalid_sales,
        "sales_min": min(sales_values), "sales_max": max(sales_values),
        "games_min": min(games_values), "games_max": max(games_values),
        "lambda_min": min(lambda_values), "lambda_max": max(lambda_values),
        "b_min": min(b_values), "b_max": max(b_values),
        "b_distribution": {str(k): v for k, v in sorted(Counter(b_values).items())},
    }


def main() -> int:
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA or sha256(LOCK) != EXPECTED_LOCK_SHA:
        raise RuntimeError("EXP_019_PROTOCOL_BLOCKED_LOCK_MISMATCH")
    canonical = load_canonical()
    records, urls = acquire()
    summary = build_dataset(records, canonical)
    retrieval_timestamp = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    manifest = {
        "experiment_id": "EXP-019 / EXP-DRAW-20260827-019-V1",
        "source_domain": "www.dhlottery.co.kr",
        "official_third_party_flag": "OFFICIAL",
        "source_method": "GET /lt645/selectPstLt645InfoNew.do: one center batch followed by sequential 10-round older batches",
        "retrieval_timestamp": retrieval_timestamp,
        "round_range": [START, END],
        "expected_rounds": END - START + 1,
        "obtained_rounds": len(summary["rows"]),
        "development_rounds": sum(88 <= row["draw"] <= 867 for row in summary["rows"]),
        "holdout_rounds": sum(868 <= row["draw"] <= 1238 for row in summary["rows"]),
        "missing_rounds": [],
        "duplicate_rounds": [],
        "main6_mismatch_rounds": summary["main_mismatches"],
        "invalid_sales_rounds": summary["invalid_sales"],
        "price_per_game": PRICE_PER_GAME,
        "dataset_path": str(DATASET.relative_to(ROOT)).replace("\\", "/"),
        "dataset_sha256": sha256(DATASET),
        "raw_batches_path": str(RAW.relative_to(ROOT)).replace("\\", "/"),
        "raw_batches_sha256": sha256(RAW),
        "source_endpoint": ENDPOINT,
        "source_urls_requested_count": len(set(urls)),
        "structural_preflight": {
            "sales_min": summary["sales_min"], "sales_max": summary["sales_max"],
            "games_sold_min": summary["games_min"], "games_sold_max": summary["games_max"],
            "lambda_min": summary["lambda_min"], "lambda_max": summary["lambda_max"],
            "birthday_range_count_min": summary["b_min"], "birthday_range_count_max": summary["b_max"],
            "birthday_range_count_distribution": summary["b_distribution"],
        },
        "relationship_peek": {
            "b_vs_winner_relationship": False,
            "sales_adjusted_effect": False,
            "beta": False,
            "u_statistic": False,
            "permutation": False,
            "p_value": False,
            "split_verdict": False,
        },
        "future_leakage": 0,
        "status": "DATA_PREFLIGHT_PASS",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

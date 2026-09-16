from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from p45.fetch import FetchError, discover_latest_round, fetch_official_draws, parse_api_page


def api_payload(items: list[dict[str, object]]) -> bytes:
    return json.dumps({"data": {"list": items}}, ensure_ascii=False).encode()


def item(round_no: int, values: tuple[int, int, int, int, int, int, int]) -> dict[str, object]:
    return {
        "ltEpsd": str(round_no),
        "ltRflYmd": f"2002-12-{6 + round_no:02d}",
        **{f"tm{i}WnNo": values[i - 1] for i in range(1, 7)},
        "bnsWnNo": values[6],
    }


class FetchTests(unittest.TestCase):
    def test_discovers_latest_round_from_current_page_shape(self) -> None:
        html = '<a href="/lt645/result">추첨결과</a><li data-value="1235">1235회</li>'
        self.assertEqual(discover_latest_round(html.encode()), 1235)

    def test_parses_official_fields(self) -> None:
        payload = api_payload([item(1, (40, 10, 23, 29, 33, 37, 16))])
        draw = parse_api_page(payload)[0]
        self.assertEqual(draw.main, (10, 23, 29, 33, 37, 40))
        self.assertEqual(draw.bonus, 16)

    def test_collects_pages_and_marks_unverified(self) -> None:
        landing = '<a href="/lt645/result">추첨결과</a><i data-value="3"></i>'.encode()
        first = api_payload([
            item(2, (9, 13, 21, 25, 32, 42, 2)),
            item(3, (11, 16, 19, 21, 27, 31, 30)),
        ])
        older = api_payload([item(1, (10, 23, 29, 33, 37, 40, 16))])

        def transport(url: str) -> bytes:
            if url.endswith("/lt645/result"):
                return landing
            return older if "srchDir=older" in url else first

        with tempfile.TemporaryDirectory() as temp:
            result = fetch_official_draws(Path(temp), transport=transport, pause_seconds=0)
            csv_text = (result / "official.csv").read_text(encoding="utf-8")
            self.assertIn("1,2002-12-07,10,23,29,33,37,40,16", csv_text)
            metadata = json.loads((result / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["collection_status"], "COLLECTED_UNVERIFIED")
            self.assertEqual(metadata["draw_count"], 3)

    def test_schema_change_leaves_no_bundle(self) -> None:
        landing = '<a href="/lt645/result">추첨결과</a><i data-value="1"></i>'.encode()

        def transport(url: str) -> bytes:
            if url.endswith("/lt645/result"):
                return landing
            return api_payload([{"ltEpsd": "1"}])

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(FetchError):
                fetch_official_draws(root, transport=transport, pause_seconds=0)
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()

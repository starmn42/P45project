from __future__ import annotations

import argparse
import json
import mimetypes
import secrets
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .backtest import run_backtest
from .candidates import evaluate_candidates
from .fetch import fetch_official_draws
from .ledger import lock_analysis, review_result, verify_locked_record
from .placement import create_set_placement
from .selection import create_selection
from .structure import analyze_structure
from .validate import validate_collected_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = PROJECT_ROOT / "web"
PIPELINE_LOCK = threading.Lock()
API_TOKEN = secrets.token_urlsafe(24)


def _latest_numbered(directory: Path, prefix: str) -> Path | None:
    if not directory.is_dir():
        return None
    matches: list[tuple[int, Path]] = []
    for path in directory.iterdir():
        if path.is_dir() and path.name.startswith(prefix):
            try:
                matches.append((int(path.name.removeprefix(prefix)), path))
            except ValueError:
                continue
    return max(matches, default=(0, None), key=lambda item: item[0])[1]


def _json_or_empty(path: Path | None) -> dict[str, object]:
    if path is None or not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}


def dashboard_status(root: Path = PROJECT_ROOT) -> dict[str, object]:
    collection = _latest_numbered(root / "downloads", "official-1-")
    validated = _latest_numbered(root / "validated", "validated-1-")
    structure = _latest_numbered(root / "analysis", "structure-")
    backtest = _latest_numbered(root / "backtests", "backtest-")
    candidates = _latest_numbered(root / "candidate-results", "candidates-")
    selection = _latest_numbered(root / "selections", "selection-")
    sets = _latest_numbered(root / "sets", "sets-")
    locked = _latest_numbered(root / "ledger" / "records", "round-")

    collection_meta = _json_or_empty(collection / "metadata.json" if collection else None)
    validated_meta = _json_or_empty(validated / "metadata.json" if validated else None)
    structure_report = _json_or_empty(structure / "structure-report.json" if structure else None)
    backtest_report = _json_or_empty(backtest / "backtest-report.json" if backtest else None)
    candidate_report = _json_or_empty(candidates / "candidate-report.json" if candidates else None)
    selection_report = _json_or_empty(selection / "selection-report.json" if selection else None)
    set_report = _json_or_empty(sets / "set-report.json" if sets else None)
    locked_report = _json_or_empty(locked / "locked-report.json" if locked else None)
    locked_meta = _json_or_empty(locked / "metadata.json" if locked else None)
    experiment_root = root / "experimental" / "v2.4-1236"
    experiment_candidate = _json_or_empty(experiment_root / "candidates-1236" / "candidate-report.json")
    experiment_selection = _json_or_empty(experiment_root / "selections" / "selection-1236" / "selection-report.json")
    experiment_sets = _json_or_empty(experiment_root / "sets" / "sets-1236" / "set-report.json")
    experiment_lock = _json_or_empty(
        root / "ledger-experimental" / "v2.4-1236" / "records" / "round-1236" / "metadata.json"
    )

    phases = [
        {"number": 1, "name": "기본 화면", "status": "COMPLETE"},
        {"number": 2, "name": "당첨번호 가져오기", "status": "COMPLETE" if collection else "PENDING"},
        {"number": 3, "name": "데이터 검사", "status": "COMPLETE" if validated_meta.get("confirmation_status") == "CONFIRMED" else "PENDING"},
        {"number": 4, "name": "기본 구조 분석", "status": "COMPLETE" if structure_report else "PENDING"},
        {"number": 5, "name": "과거 회차 시험", "status": "COMPLETE" if backtest_report else "PENDING"},
        {"number": 6, "name": "후보 판정", "status": "COMPLETE" if candidate_report else "PENDING"},
        {"number": 7, "name": "최종 6개 선택", "status": "COMPLETE" if selection_report else "PENDING"},
        {"number": 8, "name": "두 세트 배치", "status": "COMPLETE" if set_report else "PENDING"},
        {"number": 9, "name": "결과 저장과 복기", "status": "COMPLETE" if locked_report else "PENDING"},
        {"number": 10, "name": "휴대폰 배포", "status": "COMPLETE"},
    ]
    previous = structure_report.get("previous_draw_structure", {})
    overall = backtest_report.get("periods", {}).get("overall", {}) if backtest_report else {}
    return {
        "app": "P45 Research Engine",
        "online": True,
        "phases": phases,
        "latest_data_round": collection_meta.get("end_round"),
        "validated_round": validated_meta.get("end_round"),
        "target_round": locked_report.get("target_round") or selection_report.get("target_round"),
        "structure": {
            "previous_round": previous.get("round"),
            "seven": previous.get("seven", []),
            "occupancy_9": previous.get("occupancy_9", []),
            "annihilated_9": previous.get("annihilated_9", []),
        },
        "backtest": {
            "sample_count": overall.get("sample_count"),
            "integrated_return_rate": overall.get("integrated", {}).get("return_rate") if overall else None,
            "leakage_status": backtest_report.get("leakage_audit", {}).get("status") if backtest_report else None,
        },
        "result": {
            "official_status": selection_report.get("official_status", "NOT_RUN"),
            "mixed_test_status": selection_report.get("mixed_test_status", "NOT_RUN"),
            "selected_numbers": selection_report.get("selected_numbers", []),
            "placement_status": set_report.get("placement_status", "NOT_RUN"),
            "set_1": set_report.get("set_1", []),
            "set_2": set_report.get("set_2", []),
        },
        "lock": {
            "status": locked_meta.get("lock_status", "NOT_LOCKED"),
            "manifest_sha256": locked_meta.get("manifest_sha256"),
            "record_class": locked_report.get("record_class"),
            "first_execution": locked_report.get("first_execution"),
        },
        "experiment": {
            "available": bool(experiment_sets),
            "version": experiment_candidate.get("experiment_version"),
            "label": experiment_candidate.get("label"),
            "selection_mode": experiment_selection.get("selection_mode"),
            "selected_numbers": experiment_selection.get("selected_numbers", []),
            "set_1": experiment_sets.get("set_1", []),
            "set_2": experiment_sets.get("set_2", []),
            "forced_fill_performed": experiment_sets.get("candidate_replacement_performed"),
            "lock_status": experiment_lock.get("lock_status"),
            "manifest_sha256": experiment_lock.get("manifest_sha256"),
        },
    }


def run_latest_pipeline(root: Path = PROJECT_ROOT) -> dict[str, object]:
    collection = None
    try:
        collection = fetch_official_draws(root / "downloads")
    except FileExistsError:
        collection = _latest_numbered(root / "downloads", "official-1-")
    if collection is None:
        raise RuntimeError("공식 수집 묶음을 찾을 수 없습니다.")
    end_round = int(_json_or_empty(collection / "metadata.json")["end_round"])
    target = end_round + 1
    validated = root / "validated" / f"validated-1-{end_round}"
    if not validated.exists():
        validated = validate_collected_dataset(collection, root / "validated")
    structure = root / "analysis" / f"structure-{target}"
    if not structure.exists():
        structure = analyze_structure(validated, root / "analysis")
    backtest = root / "backtests" / f"backtest-{target}"
    if not backtest.exists():
        backtest = run_backtest(structure, root / "backtests")
    candidates = root / "candidate-results" / f"candidates-{target}"
    if not candidates.exists():
        candidates = evaluate_candidates(structure, backtest, root / "candidate-results")
    selection = root / "selections" / f"selection-{target}"
    if not selection.exists():
        selection = create_selection(candidates, root / "selections")
    sets = root / "sets" / f"sets-{target}"
    if not sets.exists():
        sets = create_set_placement(selection, candidates, root / "sets")
    record = root / "ledger" / "records" / f"round-{target}"
    if not record.exists():
        record = lock_analysis(
            dataset_dir=validated,
            structure_dir=structure,
            backtest_dir=backtest,
            candidate_dir=candidates,
            selection_dir=selection,
            sets_dir=sets,
            ledger_root=root / "ledger",
        )
    return {"message": f"{target}회 분석 파이프라인 완료", "status": dashboard_status(root)}


class P45Handler(BaseHTTPRequestHandler):
    server_version = "P45/0.10"

    def _json(self, value: object, status: int = 200) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 16_384:
            raise ValueError("요청이 너무 큽니다.")
        value = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("JSON 객체가 필요합니다.")
        return value

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/status":
            self._json(dashboard_status())
            return
        if path == "/api/session":
            self._json({"token": API_TOKEN})
            return
        if path == "/api/verify":
            latest = _latest_numbered(PROJECT_ROOT / "ledger" / "records", "round-")
            if latest is None:
                self._json({"verified": False, "error": "잠금 기록 없음"}, 404)
                return
            try:
                metadata = verify_locked_record(latest)
                self._json({"verified": True, "round": metadata["target_round"], "manifest_sha256": metadata["manifest_sha256"]})
            except Exception as exc:
                self._json({"verified": False, "error": str(exc)}, 409)
            return
        relative = "index.html" if path in ("", "/") else path.lstrip("/")
        file_path = (WEB_ROOT / relative).resolve()
        try:
            file_path.relative_to(WEB_ROOT.resolve())
        except ValueError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = file_path.read_bytes()
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type + ("; charset=utf-8" if content_type.startswith("text/") else ""))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache" if file_path.name == "index.html" else "public, max-age=3600")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if self.headers.get("X-P45-Token") != API_TOKEN:
            self._json({"ok": False, "error": "유효한 앱 세션이 아닙니다."}, 403)
            return
        if path == "/api/pipeline":
            if not PIPELINE_LOCK.acquire(blocking=False):
                self._json({"ok": False, "error": "다른 분석이 진행 중입니다."}, 409)
                return
            try:
                self._json({"ok": True, **run_latest_pipeline()})
            except Exception as exc:
                self._json({"ok": False, "error": str(exc)}, 500)
            finally:
                PIPELINE_LOCK.release()
            return
        if path == "/api/review":
            try:
                body = self._body_json()
                result = review_result(
                    PROJECT_ROOT / "ledger",
                    int(body["round"]),
                    [int(value) for value in body["main"]],
                    int(body["bonus"]),
                )
                self._json({"ok": True, "path": str(result), "review": _json_or_empty(result / "review.json")})
            except Exception as exc:
                self._json({"ok": False, "error": str(exc)}, 400)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8045) -> None:
    server = ThreadingHTTPServer((host, port), P45Handler)
    print(f"P45 모바일 화면: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="P45 모바일 웹앱")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8045, type=int)
    args = parser.parse_args(argv)
    serve(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

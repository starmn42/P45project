"""Publish the already-validated public web projection after a local lifecycle."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "web_runtime" / "status.json"
RELATIVE = "web_runtime/status.json"


def _git(*args: str) -> str:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never")
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True,
        encoding="utf-8", check=False, timeout=60, env=env,
    )
    if result.returncode:
        raise RuntimeError(f"WEB_PUBLISH_GIT_FAILED:{' '.join(args[:2])}:{result.stderr.strip()}")
    return result.stdout.strip()


def snapshot_body(status: dict) -> str:
    """Make a deterministic projection of the existing public status response."""
    current, lifecycle, integrity = status["current"], status["lifecycle"], status["integrity"]
    if not (
        integrity["all_pass"] and integrity["future_leakage"] == 0
        and status["seal"]["verify"] == "PASS"
        and current["sealed"] and current["result_status"] == "PENDING"
        and current["target"] == status["canonical"]["latest"] + 1
        and lifecycle["completed_target"] == status["canonical"]["latest"]
    ):
        raise RuntimeError("WEB_PUBLISH_INTEGRITY_GATE_FAILED")
    payload = dict(status)
    payload["auto_update"] = {"status": "로컬 정산·봉인 반영 완료"}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def publish(status: dict) -> str:
    """Only the public snapshot is staged; canonical and sealed files stay local."""
    if _git("branch", "--show-current") != "main":
        raise RuntimeError("WEB_PUBLISH_PRODUCTION_BRANCH_MISMATCH")
    if _git("diff", "--cached", "--name-only"):
        raise RuntimeError("WEB_PUBLISH_INDEX_NOT_EMPTY")
    head = _git("rev-parse", "HEAD")
    if _git("ls-remote", "--heads", "origin", "main").split()[0] != head:
        raise RuntimeError("WEB_PUBLISH_REMOTE_HEAD_MISMATCH")
    body = snapshot_body(status)
    if SNAPSHOT.exists() and SNAPSHOT.read_text(encoding="utf-8") == body:
        return "WEB_ALREADY_CURRENT"
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(body, encoding="utf-8", newline="\n")
    _git("add", "--", RELATIVE)
    if _git("diff", "--cached", "--name-only") != RELATIVE:
        raise RuntimeError("WEB_PUBLISH_STAGE_SCOPE_MISMATCH")
    _git("commit", "-m", f"publish: web status for round {current['target']}")
    _git("push", "origin", "HEAD:main")
    return "WEB_PUBLISHED"

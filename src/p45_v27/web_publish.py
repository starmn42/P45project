"""Publish the already-validated public web projection after a local lifecycle."""
from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "web_runtime" / "status.json"
RELATIVE = "web_runtime/status.json"
PRODUCTION_STATUS = "https://p45project.vercel.app/api/status"
CUSTOM_DOMAIN_STATUS = "https://p45.starm42.xyz/api/status"


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


def _fetch_remote_status(url: str) -> dict | None:
    try:
        req = urllib.request.Request(
            url,
            headers={"Cache-Control": "no-cache", "User-Agent": "P45-Sync-Check/1.0"},
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                return json.load(response)
    except Exception:
        pass
    return None


def check_web_sync(local_status: dict) -> tuple[bool, dict]:
    """Compare LOCAL vs PRODUCTION status fields.

    Comparison fields:
    - target
    - canonical.latest
    - lifecycle.completed_target
    """
    local_target = int(local_status["current"]["target"])
    local_canonical = int(local_status["canonical"]["latest"])
    local_completed = int(local_status["lifecycle"]["completed_target"])

    remote = _fetch_remote_status(PRODUCTION_STATUS)
    if not remote:
        remote = _fetch_remote_status(CUSTOM_DOMAIN_STATUS)
    if not remote:
        return False, {"error": "PRODUCTION_STATUS_UNREACHABLE"}

    try:
        remote_target = int(remote["current"]["target"])
        remote_canonical = int(remote["canonical"]["latest"])
        remote_completed = int(remote["lifecycle"]["completed_target"])
    except (KeyError, TypeError, ValueError):
        return False, remote

    is_sync = (
        local_target == remote_target
        and local_canonical == remote_canonical
        and local_completed == remote_completed
    )
    return is_sync, remote


def _production_target() -> int:
    remote = _fetch_remote_status(PRODUCTION_STATUS)
    if not remote:
        remote = _fetch_remote_status(CUSTOM_DOMAIN_STATUS)
    if not remote or "current" not in remote or "target" not in remote["current"]:
        raise RuntimeError("WEB_PUBLISH_PRODUCTION_API_NOT_READY")
    return int(remote["current"]["target"])


def publish(status: dict, force: bool = False) -> str:
    """Publish validated web projection with durable retry and Vercel CLI deploy."""
    is_sync, remote_info = check_web_sync(status)
    if is_sync and not force:
        return "WEB_ALREADY_CURRENT"

    if _git("branch", "--show-current") != "main":
        raise RuntimeError("WEB_PUBLISH_PRODUCTION_BRANCH_MISMATCH")
    if _git("diff", "--cached", "--name-only"):
        raise RuntimeError("WEB_PUBLISH_INDEX_NOT_EMPTY")

    target = int(status["current"]["target"])
    body = snapshot_body(status)

    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(body, encoding="utf-8", newline="\n")

    diff_status = _git("status", "--porcelain=v2", "--", RELATIVE)
    head = _git("rev-parse", "HEAD")
    remote_heads = _git("ls-remote", "--heads", "origin", "main").split()
    remote_head = remote_heads[0] if remote_heads else ""

    if diff_status or head != remote_head:
        _git("add", "--", RELATIVE)
        cached = _git("diff", "--cached", "--name-only")
        if cached != RELATIVE:
            _git("reset", "HEAD")
            raise RuntimeError("WEB_PUBLISH_STAGE_SCOPE_MISMATCH")
        if cached:
            _git("commit", "-m", f"publish: web status for round {target}")
        _git("push", "origin", "HEAD:main")

    # Vercel CLI production deployment
    env = dict(os.environ, NO_UPDATE_CHECK="1", VERCEL_TELEMETRY_DISABLED="1")
    cmd = ["npx.cmd" if os.name == "nt" else "npx", "vercel", "deploy", "--prod", "--yes"]
    start_time = time.time()
    res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=120, env=env)
    duration = time.time() - start_time

    print(f"[VERCEL DEPLOY] cmd={' '.join(cmd)} exit_code={res.returncode} duration={duration:.1f}s")
    if res.stdout.strip():
        print(f"[VERCEL STDOUT]\n{res.stdout.strip()}")
    if res.stderr.strip():
        print(f"[VERCEL STDERR]\n{res.stderr.strip()}")

    if res.returncode != 0:
        err_msg = res.stderr.strip() or res.stdout.strip()
        raise RuntimeError(f"VERCEL_DEPLOY_FAILED (code {res.returncode}): {err_msg}")

    # Verify production endpoint reflects target
    for attempt in range(1, 16):
        time.sleep(10)
        try:
            if _production_target() == target:
                print(f"[VERCEL VERIFIED] Production reflects round {target} (attempt {attempt})")
                return "WEB_PUBLISHED"
        except Exception:
            pass

    raise RuntimeError("WEB_PUBLISH_DEPLOY_NOT_VISIBLE")


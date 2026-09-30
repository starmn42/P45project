"""Idempotency guard for AUTO RESEARCH LOOP V1.

Guarantees:
- Repeat execution on the same round produces duplicate_write = 0, duplicate_retrospective = 0, duplicate_candidate = 0.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .constants import STATE_DIR

class IdempotencyGuard:
    def __init__(self, state_dir: Path = STATE_DIR):
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "processed_rounds.json"
        if not self.state_file.exists():
            self._save({"processed_rounds": {}, "last_updated": datetime.now(timezone.utc).isoformat()})

    def _load(self) -> dict[str, Any]:
        try:
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        except Exception:
            return {"processed_rounds": {}, "last_updated": datetime.now(timezone.utc).isoformat()}

    def _save(self, data: dict[str, Any]) -> None:
        self.state_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def is_round_processed(self, round_num: int) -> bool:
        data = self._load()
        return str(round_num) in data.get("processed_rounds", {})

    def get_round_summary(self, round_num: int) -> dict[str, Any] | None:
        data = self._load()
        return data.get("processed_rounds", {}).get(str(round_num))

    def mark_round_processed(self, round_num: int, summary: dict[str, Any]) -> None:
        data = self._load()
        rounds = data.setdefault("processed_rounds", {})
        rounds[str(round_num)] = {
            "processed_at": datetime.now(timezone.utc).isoformat(),
            **summary,
        }
        data["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._save(data)

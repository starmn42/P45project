"""Evidence writer for research automation artifacts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import ROOT, STORAGE_BASE

class EvidenceWriter:
    def __init__(self, base_dir: Path = STORAGE_BASE):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, relative_path: str, data: dict[str, Any]) -> Path:
        target = self.base_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return target

    def write_text(self, relative_path: str, text: str) -> Path:
        target = self.base_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

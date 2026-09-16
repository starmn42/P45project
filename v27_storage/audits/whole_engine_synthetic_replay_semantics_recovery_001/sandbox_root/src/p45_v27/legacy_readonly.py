"""Strictly read-only access to legacy P45 artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .integrity import sha256_file


class LegacyReadOnlyError(RuntimeError):
    pass


DEFAULT_LEGACY_ROOTS = (
    "analysis", "validated", "ledger", "experimental", "ledger-experimental",
    "downloads", "backtests", "candidate-results", "selections", "sets",
)


@dataclass(frozen=True)
class LegacyReadOnlyAdapter:
    project_root: Path
    allowed_roots: tuple[str, ...] = DEFAULT_LEGACY_ROOTS

    def _resolve(self, relative_path: str | Path) -> Path:
        target = (self.project_root / relative_path).resolve()
        allowed = [(self.project_root / name).resolve() for name in self.allowed_roots]
        if not any(target == root or root in target.parents for root in allowed):
            raise LegacyReadOnlyError(f"허용된 과거 읽기 경로가 아닙니다: {relative_path}")
        return target

    def read_bytes(self, relative_path: str | Path) -> bytes:
        target = self._resolve(relative_path)
        if not target.is_file():
            raise LegacyReadOnlyError(f"과거 파일이 없습니다: {relative_path}")
        return target.read_bytes()

    def read_text(self, relative_path: str | Path) -> str:
        return self.read_bytes(relative_path).decode("utf-8")

    def read_json(self, relative_path: str | Path) -> Any:
        try:
            return json.loads(self.read_text(relative_path))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise LegacyReadOnlyError(f"과거 JSON을 읽을 수 없습니다: {relative_path}: {exc}") from exc

    def verify_locked_record(self, relative_record_dir: str | Path) -> dict[str, Any]:
        record_dir = self._resolve(relative_record_dir)
        manifest_path = record_dir / "manifest.json"
        metadata_path = record_dir / "metadata.json"
        if not manifest_path.is_file() or not metadata_path.is_file():
            raise LegacyReadOnlyError("과거 잠금 Manifest 또는 metadata가 없습니다.")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("manifest_sha256") != sha256_file(manifest_path):
            raise LegacyReadOnlyError("과거 잠금 Manifest 해시가 일치하지 않습니다.")
        for entry in manifest.get("files", []):
            path = record_dir / entry["path"]
            if not path.is_file() or path.stat().st_size != entry["size"] or sha256_file(path) != entry["sha256"]:
                raise LegacyReadOnlyError(f"과거 잠금 파일이 누락 또는 변경됐습니다: {entry['path']}")
        return metadata


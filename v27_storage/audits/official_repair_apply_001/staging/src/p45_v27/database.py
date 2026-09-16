"""Database initialization and connection policy for P45 v2.7."""

from __future__ import annotations

import sqlite3
import json
from dataclasses import dataclass
from pathlib import Path

from .schema import AUDIT_SCHEMA, CORE_SCHEMA, SCHEMA_VERSION


class StorageError(RuntimeError):
    pass


@dataclass(frozen=True)
class StoragePaths:
    root: Path

    @property
    def db_dir(self) -> Path:
        return self.root / "db"

    @property
    def core_db(self) -> Path:
        return self.db_dir / self._active_names()[0]

    @property
    def audit_db(self) -> Path:
        return self.db_dir / self._active_names()[1]

    @property
    def active_pointer(self) -> Path:
        return self.root / "active_schema.json"

    def _active_names(self) -> tuple[str, str]:
        if not self.active_pointer.is_file():
            return "p45_v27_core.sqlite3", "p45_v27_audit.sqlite3"
        try:
            payload = json.loads(self.active_pointer.read_text(encoding="utf-8"))
            return payload["core_db"], payload["audit_db"]
        except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise StorageError(f"invalid active schema pointer: {self.active_pointer}") from exc

    @property
    def managed_dirs(self) -> tuple[Path, ...]:
        return (
            self.db_dir,
            self.root / "core",
            self.root / "audit" / "chunks",
            self.root / "audit" / "checkpoints",
            self.root / "audit" / "logs",
            self.root / "sealed",
            self.root / "exports" / "core",
            self.root / "exports" / "audit",
            self.root / "exports" / "sealed",
            self.root / "backups" / "core",
            self.root / "backups" / "audit",
        )


def _connect(path: Path, *, readonly: bool = False) -> sqlite3.Connection:
    if readonly:
        if not path.is_file():
            raise StorageError(f"읽기 전용 DB가 없습니다: {path}")
        connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    else:
        connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    if not readonly:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = FULL")
    return connection


def connect_core(paths: StoragePaths, *, readonly: bool = False) -> sqlite3.Connection:
    return _connect(paths.core_db, readonly=readonly)


def connect_audit(paths: StoragePaths, *, readonly: bool = False) -> sqlite3.Connection:
    return _connect(paths.audit_db, readonly=readonly)


def _initialize_database(path: Path, schema: str) -> None:
    connection = _connect(path)
    try:
        with connection:
            connection.executescript(schema)
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        result = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise StorageError(f"DB 무결성 검사 실패: {path}: {result}")
    finally:
        connection.close()


def initialize_storage(root: Path, *, fail_if_exists: bool = True) -> StoragePaths:
    paths = StoragePaths(root.resolve())
    if fail_if_exists and (paths.core_db.exists() or paths.audit_db.exists()):
        raise FileExistsError("v2.7 DB가 이미 존재합니다. 기존 DB를 덮어쓰지 않습니다.")
    for directory in paths.managed_dirs:
        directory.mkdir(parents=True, exist_ok=True)
    _initialize_database(paths.core_db, CORE_SCHEMA)
    try:
        _initialize_database(paths.audit_db, AUDIT_SCHEMA)
    except Exception:
        # CORE DB는 진단을 위해 남긴다. 자동 삭제로 증거를 잃지 않는다.
        raise
    return paths


def schema_tables(connection: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }


def integrity_check(connection: sqlite3.Connection) -> list[str]:
    return [row[0] for row in connection.execute("PRAGMA integrity_check")]

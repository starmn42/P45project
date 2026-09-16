"""Integrity, SQLite backup, and auditable export foundations."""

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .integrity import canonical_json, sha256_file


class MaintenanceError(RuntimeError):
    pass


def integrity_report(database_path: Path) -> dict[str, object]:
    if not database_path.is_file():
        raise MaintenanceError(f"DB 파일이 없습니다: {database_path}")
    source = sqlite3.connect(f"file:{database_path.as_posix()}?mode=ro", uri=True)
    try:
        source.execute("PRAGMA foreign_keys = ON")
        integrity = [row[0] for row in source.execute("PRAGMA integrity_check")]
        foreign_keys = [tuple(row) for row in source.execute("PRAGMA foreign_key_check")]
        user_version = source.execute("PRAGMA user_version").fetchone()[0]
    finally:
        source.close()
    return {
        "database": str(database_path.resolve()),
        "sha256": sha256_file(database_path),
        "user_version": user_version,
        "integrity_check": integrity,
        "foreign_key_violations": foreign_keys,
        "pass": integrity == ["ok"] and not foreign_keys,
    }


def backup_database(source_path: Path, destination_path: Path) -> dict[str, object]:
    if not source_path.is_file():
        raise MaintenanceError(f"백업할 DB가 없습니다: {source_path}")
    if destination_path.exists():
        raise FileExistsError(f"기존 백업을 덮어쓰지 않습니다: {destination_path}")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(f"file:{source_path.as_posix()}?mode=ro", uri=True)
    destination = sqlite3.connect(destination_path)
    try:
        source.backup(destination)
    finally:
        destination.close()
        source.close()
    report = integrity_report(destination_path)
    if not report["pass"]:
        raise MaintenanceError(f"백업 무결성 검사 실패: {destination_path}")
    return report


def _safe_table_name(connection: sqlite3.Connection, table: str) -> str:
    exists = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    if not exists:
        raise MaintenanceError(f"내보낼 테이블이 없습니다: {table}")
    return '"' + table.replace('"', '""') + '"'


def export_tables(
    database_path: Path,
    destination_dir: Path,
    tables: Iterable[str],
    *,
    export_format: str = "jsonl",
) -> Path:
    if export_format not in ("jsonl", "csv"):
        raise ValueError("내보내기 형식은 jsonl 또는 csv만 허용합니다.")
    if destination_dir.exists():
        raise FileExistsError(f"기존 내보내기를 덮어쓰지 않습니다: {destination_dir}")
    destination_dir.mkdir(parents=True)
    db = sqlite3.connect(f"file:{database_path.as_posix()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    files: list[dict[str, object]] = []
    try:
        for table in tables:
            quoted = _safe_table_name(db, table)
            rows = db.execute(f"SELECT * FROM {quoted} ORDER BY rowid").fetchall()
            path = destination_dir / f"{table}.{export_format}"
            if export_format == "jsonl":
                with path.open("w", encoding="utf-8", newline="\n") as stream:
                    for row in rows:
                        stream.write(canonical_json(dict(row)) + "\n")
            else:
                columns = [item[0] for item in db.execute(f"SELECT * FROM {quoted} LIMIT 0").description]
                with path.open("w", encoding="utf-8-sig", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\r\n")
                    writer.writeheader()
                    writer.writerows(dict(row) for row in rows)
            files.append({"name": path.name, "row_count": len(rows), "sha256": sha256_file(path)})
    finally:
        db.close()
    manifest = {
        "database": str(database_path.resolve()),
        "database_sha256": sha256_file(database_path),
        "format": export_format,
        "files": files,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    manifest_path = destination_dir / "export-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


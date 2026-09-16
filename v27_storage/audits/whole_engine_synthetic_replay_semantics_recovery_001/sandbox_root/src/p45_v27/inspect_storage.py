"""Read-only stage-3 storage inspection command."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .database import StoragePaths, connect_audit, connect_core, schema_tables
from .maintenance import integrity_report


def inspect(root: Path) -> dict[str, object]:
    paths = StoragePaths(root.resolve())
    core = connect_core(paths, readonly=True)
    audit = connect_audit(paths, readonly=True)
    try:
        core_tables = sorted(schema_tables(core))
        audit_tables = sorted(schema_tables(audit))
        return {
            "core_integrity": integrity_report(paths.core_db),
            "audit_integrity": integrity_report(paths.audit_db),
            "core_user_version": core.execute("PRAGMA user_version").fetchone()[0],
            "audit_user_version": audit.execute("PRAGMA user_version").fetchone()[0],
            "core_rows": {
                table: core.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                for table in core_tables
            },
            "audit_rows": {
                table: audit.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                for table in audit_tables
            },
            "core_trigger_count": core.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'"
            ).fetchone()[0],
            "audit_trigger_count": audit.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'"
            ).fetchone()[0],
        }
    finally:
        audit.close()
        core.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="P45 v2.7 저장구조 읽기 전용 점검")
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(inspect(args.root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


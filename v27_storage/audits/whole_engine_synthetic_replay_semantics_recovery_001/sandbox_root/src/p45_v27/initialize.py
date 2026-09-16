"""Initialize the approved isolated v2.7 stage-3 storage layout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .database import connect_audit, connect_core, initialize_storage, schema_tables


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="P45 v2.7 저장구조 초기화")
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args(argv)
    paths = initialize_storage(args.root)
    core = connect_core(paths, readonly=True)
    audit = connect_audit(paths, readonly=True)
    try:
        result = {
            "storage_root": str(paths.root),
            "core_db": str(paths.core_db),
            "audit_db": str(paths.audit_db),
            "core_tables": sorted(schema_tables(core)),
            "audit_tables": sorted(schema_tables(audit)),
        }
    finally:
        audit.close()
        core.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


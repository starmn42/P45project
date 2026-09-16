"""Safely prepare and activate empty schema-271 operating databases."""

from __future__ import annotations

import hashlib, json, os, shutil, sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .database import StoragePaths, _initialize_database
from .schema import AUDIT_SCHEMA, AUDIT_TABLES, CORE_SCHEMA, CORE_TABLES


def _sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()


def _inspect(path: Path) -> dict[str, Any]:
    db=sqlite3.connect(path)
    try:
        tables=[r[0] for r in db.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")]
        return {"user_version":db.execute("pragma user_version").fetchone()[0],
                "integrity":db.execute("pragma integrity_check").fetchone()[0],
                "foreign_key_violations":len(db.execute("pragma foreign_key_check").fetchall()),
                "tables":sorted(tables),"total_rows":sum(db.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0] for t in tables),
                "trigger_count":db.execute("select count(*) from sqlite_master where type='trigger'").fetchone()[0]}
    finally:db.close()


def prepare(root: Path) -> dict[str, Any]:
    root=root.resolve();db_dir=root/"db";db_dir.mkdir(parents=True,exist_ok=True)
    old_core=db_dir/"p45_v27_core.sqlite3";old_audit=db_dir/"p45_v27_audit.sqlite3"
    if not old_core.is_file() or not old_audit.is_file():raise FileNotFoundError("schema-27 operating DB missing")
    before={"core":_inspect(old_core),"audit":_inspect(old_audit)}
    if before["core"]["total_rows"] or before["audit"]["total_rows"]:raise RuntimeError("operating DB is not empty")
    for path in (old_core,old_audit):
        db=sqlite3.connect(path);db.execute("pragma wal_checkpoint(TRUNCATE)");db.close()
    stamp=datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    backup=root/"backups"/"schema27"/stamp;backup.mkdir(parents=True,exist_ok=False)
    backup_core=backup/old_core.name;backup_audit=backup/old_audit.name
    shutil.copy2(old_core,backup_core);shutil.copy2(old_audit,backup_audit)
    hashes={"source_core":_sha(old_core),"backup_core":_sha(backup_core),
            "source_audit":_sha(old_audit),"backup_audit":_sha(backup_audit)}
    if hashes["source_core"]!=hashes["backup_core"] or hashes["source_audit"]!=hashes["backup_audit"]:
        raise RuntimeError("schema-27 backup hash mismatch")
    next_core=db_dir/"p45_v271_core.sqlite3.next";next_audit=db_dir/"p45_v271_audit.sqlite3.next"
    final_core=db_dir/"p45_v271_core.sqlite3";final_audit=db_dir/"p45_v271_audit.sqlite3"
    if any(p.exists() for p in (next_core,next_audit,final_core,final_audit)):raise FileExistsError("schema-271 target already exists")
    _initialize_database(next_core,CORE_SCHEMA);_initialize_database(next_audit,AUDIT_SCHEMA)
    core_check,audit_check=_inspect(next_core),_inspect(next_audit)
    if set(core_check["tables"])!=CORE_TABLES or set(audit_check["tables"])!=AUDIT_TABLES \
            or core_check["integrity"]!="ok" or audit_check["integrity"]!="ok" \
            or core_check["foreign_key_violations"] or audit_check["foreign_key_violations"] \
            or core_check["total_rows"] or audit_check["total_rows"]:
        raise RuntimeError("schema-271 validation failed")
    os.replace(next_core,final_core);os.replace(next_audit,final_audit)
    pointer={"schema_version":271,"core_db":final_core.name,"audit_db":final_audit.name,
             "previous_core_db":old_core.name,"previous_audit_db":old_audit.name,"activated_at":stamp}
    pointer_tmp=root/"active_schema.json.tmp";pointer_path=root/"active_schema.json"
    pointer_tmp.write_text(json.dumps(pointer,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    os.replace(pointer_tmp,pointer_path)
    report={"backup_dir":str(backup),"hashes":hashes,"before":before,
            "schema271":{"core":core_check,"audit":audit_check},"pointer":pointer,
            "new_hashes":{"core":_sha(final_core),"audit":_sha(final_audit)}}
    (backup/"migration-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report


def rollback_pointer(root: Path) -> None:
    root=root.resolve();path=root/"active_schema.json";payload=json.loads(path.read_text(encoding="utf-8"))
    restored={"schema_version":27,"core_db":payload["previous_core_db"],"audit_db":payload["previous_audit_db"],
              "rolled_back_from":payload["schema_version"]}
    temp=root/"active_schema.json.tmp";temp.write_text(json.dumps(restored,indent=2)+"\n",encoding="utf-8");os.replace(temp,path)

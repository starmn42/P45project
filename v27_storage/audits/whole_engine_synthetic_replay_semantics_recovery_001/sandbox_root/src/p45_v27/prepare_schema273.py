"""Back up empty schema-272 DBs, create/validate schema-273, then switch atomically."""
from __future__ import annotations
import hashlib,json,os,shutil,sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
from .database import StoragePaths,_initialize_database
from .schema import AUDIT_SCHEMA,AUDIT_TABLES,CORE_SCHEMA,CORE_TABLES,SCHEMA_VERSION

def _sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def _inspect(path:Path)->dict[str,Any]:
 db=sqlite3.connect(str(path))
 try:
  ts=[r[0] for r in db.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")]
  return {'user_version':db.execute('pragma user_version').fetchone()[0],'integrity':db.execute('pragma integrity_check').fetchone()[0],
    'foreign_key_violations':len(db.execute('pragma foreign_key_check').fetchall()),'tables':sorted(ts),
    'total_rows':sum(db.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0] for t in ts),'trigger_count':db.execute("select count(*) from sqlite_master where type='trigger'").fetchone()[0]}
 finally:db.close()

def prepare(root:Path)->dict[str,Any]:
 root=root.resolve();active=StoragePaths(root);old_core=active.core_db;old_audit=active.audit_db;before={'core':_inspect(old_core),'audit':_inspect(old_audit)}
 if before['core']['total_rows'] or before['audit']['total_rows']:raise RuntimeError('active DB is not empty')
 stamp=datetime.now().astimezone().strftime('%Y%m%dT%H%M%S%z');backup=root/'backups'/'schema272'/stamp;backup.mkdir(parents=True)
 for p in (old_core,old_audit):
  db=sqlite3.connect(str(p));db.execute('pragma wal_checkpoint(TRUNCATE)');db.close()
 bc=backup/old_core.name;ba=backup/old_audit.name;shutil.copy2(old_core,bc);shutil.copy2(old_audit,ba)
 hashes={'source_core':_sha(old_core),'backup_core':_sha(bc),'source_audit':_sha(old_audit),'backup_audit':_sha(ba)}
 if hashes['source_core']!=hashes['backup_core'] or hashes['source_audit']!=hashes['backup_audit']:raise RuntimeError('backup hash mismatch')
 nc=root/'db'/'p45_v273_core.sqlite3.next';na=root/'db'/'p45_v273_audit.sqlite3.next';fc=root/'db'/'p45_v273_core.sqlite3';fa=root/'db'/'p45_v273_audit.sqlite3'
 if any(p.exists() for p in (nc,na,fc,fa)):raise FileExistsError('schema-273 target exists')
 _initialize_database(nc,CORE_SCHEMA);_initialize_database(na,AUDIT_SCHEMA);ci,ai=_inspect(nc),_inspect(na)
 if SCHEMA_VERSION!=273 or set(ci['tables'])!=CORE_TABLES or set(ai['tables'])!=AUDIT_TABLES or ci['integrity']!='ok' or ai['integrity']!='ok' or ci['total_rows'] or ai['total_rows']:raise RuntimeError('schema-273 validation failed')
 os.replace(nc,fc);os.replace(na,fa);previous=json.loads((root/'active_schema.json').read_text(encoding='utf-8'))
 pointer={'schema_version':273,'core_db':fc.name,'audit_db':fa.name,'previous_core_db':old_core.name,'previous_audit_db':old_audit.name,'previous_schema_version':previous.get('schema_version'),'activated_at':stamp}
 temp=root/'active_schema.json.tmp';temp.write_text(json.dumps(pointer,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(temp,root/'active_schema.json')
 report={'backup_dir':str(backup),'hashes':hashes,'before':before,'schema273':{'core':ci,'audit':ai},'pointer':pointer,'new_hashes':{'core':_sha(fc),'audit':_sha(fa)}}
 (backup/'migration-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return report

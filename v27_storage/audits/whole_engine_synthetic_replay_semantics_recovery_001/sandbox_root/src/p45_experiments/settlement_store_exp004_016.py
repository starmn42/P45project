"""Create the isolated EXP-004..016 settlement audit database."""
from __future__ import annotations
import hashlib,json,os,sqlite3,uuid
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'v27_storage/experiments/batch_exp004_016'
DB=BASE/'exp004_016_settlement.sqlite3'
RAW=BASE/'reproduction_errata_004.json'
ADJ=BASE/'adjudication_errata_004.json'
ERR=ROOT/'v27_storage/experiments/exp007/P45_EXP007_독립분석_결과_ERRATA_001.md'
STATUS={**{f'EXP-{n:03d}':'FAILED' for n in range(4,9)},**{f'EXP-{n:03d}':'FAILED_EARLY' for n in range(9,17)}}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->None:
 data=json.loads(RAW.read_text(encoding='utf8'));adj=json.loads(ADJ.read_text(encoding='utf8'))
 if adj['status']!='PASS' or adj['round_1238_used']:raise SystemExit('ADJUDICATION_NOT_PASS')
 tmp=DB.with_suffix('.sqlite3.next');tmp.unlink(missing_ok=True)
 db=sqlite3.connect(tmp)
 db.executescript('''PRAGMA foreign_keys=ON;
 CREATE TABLE settlement_run(run_id TEXT PRIMARY KEY,created_at TEXT NOT NULL,data_range TEXT NOT NULL,data_sha256 TEXT NOT NULL,round_1238_used INTEGER NOT NULL CHECK(round_1238_used=0),adjudicated INTEGER NOT NULL,matched INTEGER NOT NULL,unresolved_mismatch INTEGER NOT NULL,official_engine_changed INTEGER NOT NULL CHECK(official_engine_changed=0));
 CREATE TABLE experiment_result(experiment_id TEXT PRIMARY KEY,run_id TEXT NOT NULL REFERENCES settlement_run(run_id),protocol_sha256 TEXT NOT NULL,result_document_sha256 TEXT NOT NULL,reproduction_status TEXT NOT NULL,final_judgment TEXT NOT NULL,future_leakage INTEGER NOT NULL CHECK(future_leakage=0),recommendation_connection INTEGER NOT NULL CHECK(recommendation_connection=0),calculation_json TEXT NOT NULL);
 CREATE TABLE evidence(experiment_id TEXT NOT NULL REFERENCES experiment_result(experiment_id),evidence_type TEXT NOT NULL,path TEXT NOT NULL,sha256 TEXT NOT NULL,PRIMARY KEY(experiment_id,evidence_type));
 CREATE TABLE errata(experiment_id TEXT PRIMARY KEY REFERENCES experiment_result(experiment_id),error_field TEXT NOT NULL,original_value TEXT NOT NULL,corrected_value TEXT NOT NULL,root_cause TEXT NOT NULL,final_judgment_changed INTEGER NOT NULL CHECK(final_judgment_changed=0),errata_path TEXT NOT NULL,errata_sha256 TEXT NOT NULL);
 ''')
 run=str(uuid.uuid4());now=datetime.now().astimezone().isoformat()
 db.execute('INSERT INTO settlement_run VALUES(?,?,?,?,?,?,?,?,?)',(run,now,'1~1237',data['data_sha256_bom_excluded'],0,13,13,0,0))
 for exp,row in data['results'].items():
  calc=json.dumps(row['calculation'],ensure_ascii=False,sort_keys=True,separators=(',',':'))
  db.execute('INSERT INTO experiment_result VALUES(?,?,?,?,?,?,?,?,?)',(exp,run,row['protocol_sha256'],row['result_document_sha256'],'REPRODUCED_WITH_ERRATA' if exp=='EXP-007' else 'REPRODUCED',STATUS[exp],0,0,calc))
  n=exp[-3:];folder=ROOT/f'v27_storage/experiments/exp{n}'
  for typ,name in [('LOCKED_PROTOCOL',f'P45_EXP{n}_사전등록_프로토콜_LOCKED_001.md'),('ORIGINAL_RESULT',f'P45_EXP{n}_독립분석_결과_001.md')]:
   path=folder/name;db.execute('INSERT INTO evidence VALUES(?,?,?,?)',(exp,typ,str(path.relative_to(ROOT)).replace('\\','/'),sha(path)))
 db.execute('INSERT INTO errata VALUES(?,?,?,?,?,?,?,?)',('EXP-007','WALKFORWARD.SIGNAL_EXPOSED_ROUNDS','1013','0','post-minimum evaluable count was incorrectly reported as p<=0.05 signal exposure',0,str(ERR.relative_to(ROOT)).replace('\\','/'),sha(ERR)))
 db.commit(); assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not db.execute('PRAGMA foreign_key_check').fetchall();db.close()
 os.replace(tmp,DB)
 print(json.dumps({'run_id':run,'db':str(DB),'sha256':sha(DB),'rows':13},ensure_ascii=False))
if __name__=='__main__':main()

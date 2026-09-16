from __future__ import annotations
import json,sqlite3,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from p45_v27.protection_manifest import build_manifest,compare_manifests
from p45_v27.trio_walkforward import connect,get_or_create_run,hashes,run

ROOT=Path('.').resolve();DATA=(ROOT/'analysis/structure-1236/analysis-input.csv').resolve()

class Stage71WalkforwardTest(unittest.TestCase):
 def test_01_resume_exact_next_and_no_complete_replay(self):
  with tempfile.TemporaryDirectory() as t:
   db=Path(t)/'wf.sqlite3';a=run(project_root=ROOT,db_path=db,data_path=DATA,start_round=43,end_round=44,max_rounds=1,max_seconds=60)
   self.assertEqual(a['next_resume_round'],44);self.assertEqual(a['processed_this_call'],1);self.assertFalse(a['official_aggregate_allowed'])
   b=run(project_root=ROOT,db_path=db,data_path=DATA,start_round=43,end_round=44,resume=True,max_rounds=1,max_seconds=60)
   self.assertEqual(a['run_id'],b['run_id']);self.assertEqual(b['next_resume_round'],None);self.assertTrue(b['official_aggregate_allowed'])
   c=run(project_root=ROOT,db_path=db,data_path=DATA,start_round=43,end_round=44,resume=True,max_seconds=60)
   self.assertEqual(c['processed_this_call'],0)

 def test_02_unique_round_and_exposure_constraints(self):
  with tempfile.TemporaryDirectory() as t:
   path=Path(t)/'wf.sqlite3';r=run(project_root=ROOT,db_path=path,data_path=DATA,start_round=43,end_round=43,max_seconds=60);db=sqlite3.connect(path)
   row=db.execute('select * from wf_exposure limit 1').fetchone();cols=[x[1] for x in db.execute('pragma table_info(wf_exposure)')];item=dict(zip(cols,row))
   with self.assertRaises(sqlite3.IntegrityError):db.execute('insert into wf_exposure values (?,?,?,?,?,?,?,?,?,?,?)',('other',item['run_id'],item['evaluation_round'],item['trio_rule_signature'],item['representative_trio_key'],item['prediction_hash_before_result'],item['integrated_hits'],item['main_hits'],item['bonus_hit'],item['unit_conflict'],item['outcome_hash']))
   db.close()

 def test_03_failure_rolls_back_exposures_and_marks_retryable(self):
  with tempfile.TemporaryDirectory() as t:
   path=Path(t)/'wf.sqlite3'
   with patch('p45_v27.trio_walkforward._round_representatives',side_effect=RuntimeError('controlled')):r=run(project_root=ROOT,db_path=path,data_path=DATA,start_round=43,end_round=43,max_seconds=60)
   db=sqlite3.connect(path);self.assertEqual(db.execute('select count(*) from wf_exposure').fetchone()[0],0);self.assertEqual(db.execute('select run_status from wf_round').fetchone()[0],'FAILED_RETRYABLE');db.close()

 def test_04_hash_change_new_run_same_hash_reuse(self):
  with tempfile.TemporaryDirectory() as t:
   db=connect(Path(t)/'wf.sqlite3');h=hashes(ROOT,DATA);a,reuse=get_or_create_run(db,h,43,44);self.assertFalse(reuse);b,reuse=get_or_create_run(db,h,43,44);self.assertEqual(a,b);self.assertTrue(reuse)
   changed=dict(h);changed['code_hash']='0'*64;c,reuse=get_or_create_run(db,changed,43,44);self.assertNotEqual(a,c);self.assertFalse(reuse);db.close()

 def test_05_future_boundary_and_prediction_before_outcome(self):
  with tempfile.TemporaryDirectory() as t:
   path=Path(t)/'wf.sqlite3';run(project_root=ROOT,db_path=path,data_path=DATA,start_round=43,end_round=43,max_seconds=60);db=sqlite3.connect(path)
   cp=db.execute('select data_prefix_hash,prediction_hash_before_result,run_status from wf_round').fetchone();self.assertEqual(cp[2],'COMPLETE');self.assertEqual(len(cp[0]),64);self.assertEqual(len(cp[1]),64)
   self.assertTrue(all(len(x[0])==64 for x in db.execute('select prediction_hash_before_result from wf_exposure')));db.close()

 def test_06_partial_never_allows_official_aggregate(self):
  with tempfile.TemporaryDirectory() as t:
   r=run(project_root=ROOT,db_path=Path(t)/'wf.sqlite3',data_path=DATA,start_round=43,end_round=45,max_rounds=1,max_seconds=60)
   self.assertEqual(r['run_status'],'WALKFORWARD_INCOMPLETE');self.assertFalse(r['official_aggregate_allowed'])

 def test_07_deterministic_checkpoint(self):
  decisions=[]
  for _ in range(10):
   with tempfile.TemporaryDirectory() as t:
    path=Path(t)/'wf.sqlite3';run(project_root=ROOT,db_path=path,data_path=DATA,start_round=43,end_round=43,max_seconds=60);db=sqlite3.connect(path);decisions.append(db.execute('select decision_hash from wf_round').fetchone()[0]);db.close()
  self.assertEqual(len(set(decisions)),1)

 def test_08_canonical_manifest_ignores_generated_cache(self):
  a=build_manifest(ROOT);b=build_manifest(ROOT);self.assertTrue(compare_manifests(a,b)['equal']);self.assertTrue(a['roots']['src/p45']['excluded_generated_files'])

 def test_09_operational_databases_stay_empty_and_pair_zero(self):
  pointer=json.loads((ROOT/'v27_storage/active_schema.json').read_text())
  for key in ('core_db','audit_db'):
   db=sqlite3.connect(ROOT/'v27_storage/db'/pointer[key]);tables=[x[0] for x in db.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")];self.assertEqual(sum(db.execute(f'SELECT count(*) FROM "{x}"').fetchone()[0] for x in tables),0)
   if key=='core_db':self.assertEqual(db.execute('select count(*) from pair_ledger').fetchone()[0],0);self.assertEqual(db.execute('select count(*) from number_ledger').fetchone()[0],0)
   db.close()

if __name__=='__main__':unittest.main()

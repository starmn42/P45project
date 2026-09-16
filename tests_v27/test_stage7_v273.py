from __future__ import annotations
import copy,sqlite3,tempfile,unittest
from pathlib import Path
from p45_v27.core_store import CoreStore
from p45_v27.initialize import initialize_storage
from p45_v27.number_store import persist_number_ledger
from p45_v27.schema import SCHEMA_VERSION,CORE_TABLES
from p45_v27.stage6_diagnostics import diagnose_stage6
from p45_v27.trio_engine import (build_current_trios,generate_trios,performance,random_probability,run_walkforward,
    statistic,structure_collapse,wilson95)
from p45_v27.trio_store import load_trios,number_snapshot_hash,persist_trios
from p45_v27.units import DEFINITIONS

DATA=Path('analysis/structure-1236/analysis-input.csv');H='e'*64

class Stage7V273Test(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s6=diagnose_stage6(DATA,1236);cls.result=build_current_trios(cls.s6,DEFINITIONS)

 def test_01_counts_6_to_12_and_order(self):
  expected={6:20,7:35,8:56,9:84,10:120,11:165,12:220}
  for n,c in expected.items():
   rows=generate_trios(list(range(1,n+1)));self.assertEqual(len(rows),c);self.assertEqual(len(set(rows)),c);self.assertTrue(all(a<b<c for a,b,c in rows))

 def test_02_current_220_coverage_and_signature(self):
  self.assertEqual(self.result['trio_count'],220)
  for row in self.result['rows'].values():
   self.assertEqual(len(row['coverage']['cells']),15);self.assertEqual(len(row['coverage']['trio_unit_state_vector']),5)
   self.assertNotIn(str(row['trio']),row['trio_rule_signature']);self.assertEqual(len(row['trio_rule_signature']),64)

 def test_03_unit_role_overlap_domains(self):
  us={'UNIT_TRIO_COMPLETE_SUPPORT','UNIT_TRIO_PARTIAL_SUPPORT','UNIT_TRIO_TEST_MIXED','UNIT_TRIO_CONFLICT','UNIT_TRIO_INCOMPLETE'}
  ds={'ROLE_COMPLETE_DIVERSITY','ROLE_PARTIAL_DIVERSITY','ROLE_DUPLICATED'};os={'EVIDENCE_IDENTICAL','EVIDENCE_HIGH_OVERLAP','EVIDENCE_PARTIAL_OVERLAP','EVIDENCE_NONE'}
  for r in self.result['rows'].values():self.assertTrue(set(r['coverage']['trio_unit_state_vector'])<=us);self.assertTrue(set(r['coverage']['role_diversity_vector'])<=ds);self.assertTrue(set(r['coverage']['evidence_overlap_vector'])<=os)

 def test_04_pareto_does_not_auto_fail(self):
  self.assertTrue(self.result['pareto_relations']);self.assertTrue(all(not (r['pareto_state']=='UNIT_PARETO_DOMINATED' and r['trio_state']=='TRIO_FAIL') for r in self.result['rows'].values()))

 def test_05_random_exact_events(self):
  for scope,m in (('INTEGRATED',7),('MAIN',6)):
   self.assertAlmostEqual(sum(random_probability(scope,k) for k in range(4)),1);self.assertAlmostEqual(random_probability(scope,3),__import__('math').comb(m,3)/__import__('math').comb(45,3))

 def test_06_wilson_binomial_zero(self):
  lo,hi=wilson95(0,200);self.assertEqual(lo,0);self.assertGreater(hi,0)
  s=statistic(0,200,random_probability('INTEGRATED',3));self.assertEqual(s['rate'],0);self.assertEqual(s['p_upper'],1);self.assertGreaterEqual(s['p_lower'],0)

 def test_07_exact_3210_separate(self):
  out=[{'integrated_hits':i%4,'main_hits':(i+1)%4,'unit_conflict':0} for i in range(200)];p=performance(out)
  for scope in ('INTEGRATED','MAIN'):self.assertEqual(sum(p['statistics'][(scope,f'EXACT_{k}_OF_3')]['success_count'] for k in range(4)),200)

 def test_08_recent20_test_only(self):
  out=[{'integrated_hits':2,'main_hits':2,'unit_conflict':0} for _ in range(180)]+[{'integrated_hits':0,'main_hits':0,'unit_conflict':0} for _ in range(20)]
  a=build_current_trios(self.s6,DEFINITIONS);b=performance(out)
  self.assertEqual(b['period_metrics'][('INTEGRATED','EXACT_0_OF_3','RECENT_20')]['hit_count'],20);self.assertEqual(len(a['rows']),220)

 def test_09_structure_49_50_endpoint_boundary(self):
  item={'integrated_hits':0,'main_hits':0,'unit_conflict':0}
  self.assertEqual(structure_collapse([item]*99)['state'],'INSUFFICIENT_SAMPLE');self.assertNotEqual(structure_collapse([item]*100)['state'],'INSUFFICIENT_SAMPLE')

 def test_10_current_pass_zero_and_all_stored(self):
  counts={}
  for r in self.result['rows'].values():counts[r['trio_state']]=counts.get(r['trio_state'],0)+1
  self.assertEqual(counts.get('TRIO_PASS',0),0);self.assertEqual(sum(counts.values()),220)

 def test_11_expanded_pool_forbids_pass(self):
  self.assertEqual(self.s6['candidate_pool_type'],'EXPANDED_TEST_POOL');self.assertFalse(any(r['trio_state']=='TRIO_PASS' for r in self.result['rows'].values()))

 def test_12_determinism_10(self):
  hashes={build_current_trios(self.s6,DEFINITIONS)['execution_hash'] for _ in range(10)};self.assertEqual(len(hashes),1)

 def test_13_walkforward_recomputes_and_blocks_future(self):
  actual={10:{'main':(1,2,3,4,5,6),'bonus':7},11:{'main':(2,3,4,5,6,7),'bonus':8}}
  calls=[]
  def pipe(r):
   calls.append(r);x=copy.deepcopy(self.s6);x['analysis_round']=r;x['source_rounds']=(1,r-1);return x
  w=run_walkforward([10,11],pipe,actual,DEFINITIONS);self.assertEqual(calls,[10,11]);self.assertTrue(w['future_blocked']);self.assertEqual(w['first_eligible_round'],10)
  self.assertTrue(all(len({e['outer_round'] for e in es})==len(es) for es in w['exposures'].values()))

 def test_14_future_leak_rejected(self):
  def bad(r):
   x=copy.deepcopy(self.s6);x['analysis_round']=r;x['source_rounds']=(1,r);return x
  with self.assertRaises(RuntimeError):run_walkforward([10],bad,{10:{'main':(1,2,3,4,5,6),'bonus':7}},DEFINITIONS)

 def test_15_schema_store_roundtrip_and_number_guard(self):
  with tempfile.TemporaryDirectory() as t:
   paths=initialize_storage(Path(t));self.assertEqual(SCHEMA_VERSION,273);store=CoreStore(paths)
   e=store.register_engine_version(version_label='273-test',directive_sha256=H,implementation_order_sha256=H,rule_hash=H,code_hash=H,effective_round=1)
   run=store.create_core_run(engine_version_id=e,analysis_round=1236,record_class='BACKTEST',raw_data_hash=H,normalized_data_hash=H,rule_hash=H,code_hash=H)
   persist_number_ledger(store,run,self.s6,H,self.s6['execution_hash']);before=number_snapshot_hash(store,run)
   persist_trios(store,run,self.result,data_hash=H,execution_hash=self.result['execution_hash'],number_hash=before)
   self.assertEqual(len(load_trios(store,run)),220);self.assertEqual(before,number_snapshot_hash(store,run))
   with self.assertRaises(sqlite3.IntegrityError):
    with store.transaction() as db:db.execute('UPDATE number_ledger SET number_state=number_state WHERE core_run_id=?',(run,))
   with store.transaction() as db:self.assertEqual(db.execute('SELECT count(*) FROM pair_ledger').fetchone()[0],0);self.assertEqual(set(r[0] for r in db.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")),CORE_TABLES)

if __name__=='__main__':unittest.main()

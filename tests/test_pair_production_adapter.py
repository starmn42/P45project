from __future__ import annotations
import hashlib, sqlite3, tempfile, unittest
from pathlib import Path
from p45_v27.integrity import sha256_json
from p45_v27.pairs.engine import SIGNATURE_VERSION
from p45_v27.pairs.production import ProductionPairPipeline
from p45_v27.pairs.walkforward import PairWalkforwardRunner

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'analysis/structure-1236/analysis-input.csv'
TRIO=ROOT/'v27_storage/backtests/p45_v273_trio_walkforward.sqlite3'
def h(x):return hashlib.sha256(x.encode()).hexdigest()

class ProductionAdapterTests(unittest.TestCase):
 def test_boundaries_and_smoke(self):
  p=ProductionPairPipeline(DATA,TRIO)
  a=p.build_prediction_context(43,42,{})
  b=p.build_prediction_context(1235,1234,{})
  c=p.build_prediction_context(1236,1235,{})
  self.assertEqual((42,1234,1235),(a.source_end_round,b.source_end_round,c.source_end_round))
  self.assertEqual([],p.outcome_accesses)
  self.assertEqual(10,len(c.candidates))
  self.assertEqual({SIGNATURE_VERSION},{x.context['signature_version'] for x in c.candidates})
 def test_boundary_cannot_be_bypassed(self):
  p=ProductionPairPipeline(DATA,TRIO)
  with self.assertRaisesRegex(RuntimeError,'FUTURE_LEAKAGE'):p.build_prediction_context(1236,1236,{})
 def test_determinism_ten(self):
  p=ProductionPairPipeline(DATA,TRIO);values=[]
  for _ in range(10):
   x=p.build_prediction_context(1236,1235,{})
   values.append(sha256_json({'prefix':x.data_prefix_hash,'pairs':[(c.canonical_pair_key,c.base_pair_rule_signature,c.rank_key,c.context) for c in x.candidates]}))
  self.assertEqual(1,len(set(values)));self.assertEqual([],p.outcome_accesses)
 def test_runner_persists_official_v12_audit_before_outcome(self):
  class TestOutcome(ProductionPairPipeline):
   def load_round_outcome(self,r):
    self.outcome_accesses.append(r);return {'main':(1,2,3,4,5,6),'bonus':7}
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/'pair.sqlite3';p=TestOutcome(DATA,TRIO);events=[]
   p.prediction_persisted=lambda r,x:events.append(('prediction',r,x))
   runner=PairWalkforwardRunner(path,run_id='PRODUCTION-SMOKE',start_round=1236,end_round=1236,rule_hash=h('r'),code_hash=h('c'),schema_hash=h('s'),pipeline=p)
   out=runner.run(max_rounds=1);self.assertTrue(out['complete'])
   self.assertEqual([1236],p.outcome_accesses);self.assertEqual('prediction',events[0][0])
   db=sqlite3.connect(path);self.assertEqual(1,db.execute('select count(*) from wf_round').fetchone()[0]);self.assertGreater(db.execute('select count(*) from wf_prediction_audit').fetchone()[0],0);self.assertEqual(0,len(db.execute('pragma foreign_key_check').fetchall()));db.close()

if __name__=='__main__':unittest.main()

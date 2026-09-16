from __future__ import annotations
import hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from p45_v27.pairs.walkforward import PairPrediction,PairWalkforwardRunner,RoundPrediction
from p45_v27.pairs.audit_v12 import CONTEXT_FIELD_IDS,CONTEXT_VERSION,SIGNATURE_VERSION,context_fingerprint,rule_signature,semantic_policy_hashes

def h(x:str)->str:return hashlib.sha256(x.encode()).hexdigest()

class Source:
 def __init__(self,rounds=range(10,14),change_sig=False,fail_round=None):
  self.rounds=list(rounds);self.events=[];self.change_sig=change_sig;self.fail_round=fail_round;self._hash=h('source')
 def source_hash(self):return self._hash
 def prediction_persisted(self,r,p):self.events.append(('prediction',r,p))
 def compute_pre_result(self,r,end,history):
  self.events.append(('compute',r,end,{k:len(v) for k,v in history.items()}))
  if r==self.fail_round:raise RuntimeError('synthetic')
  policies=semantic_policy_hashes()
  if self.change_sig and r>=12:policies['eligibility_policy_hash']=h('changed-policy')
  sig,rule_json,_=rule_signature('EXPANDED_TEST_POOL',policy_hashes=policies)
  gates={f'PG{i:02d}':'PASS' for i in range(1,15)}
  fields={key:{'value':key} for key in CONTEXT_FIELD_IDS};fingerprint,context_json,_=context_fingerprint(fields)
  lifecycle={'marker':'PG13_PENDING_FINAL'}
  records=[{'gate_id':f'PG{i:02d}','pg13_lifecycle':lifecycle if i==13 else None} for i in range(1,15)]
  ctx={'history_n':len(history.get(sig,[])),'gate_input':{'synthetic':True},'gate_results':gates,'pair_state':'PAIR_READY',
       'signature_version':SIGNATURE_VERSION,'canonical_rule_payload_json':rule_json,
       'context_fingerprint_version':CONTEXT_VERSION,'pair_context_fingerprint':fingerprint,
       'canonical_context_payload_json':context_json,'prelock':{'hash':h('prelock')},
       'final_prediction':{'hash':h('prediction')},'finalization':{'hash':h('finalization')},'gate_records':records}
  a=PairPrediction('1-2-3__4-5-6',sig,(1,2,3),(4,5,6),(0,),ctx)
  b=PairPrediction('1-2-3__7-8-9',sig,(1,2,3),(7,8,9),(1,),ctx)
  return RoundPrediction(end,h(f'prefix-{end}'),(a,b))
 def read_result(self,r):
  self.events.append(('result',r));return {'main':(1,4,10,20,30,40),'bonus':2}

class RunnerTests(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.path=Path(self.t.name)/'wf.sqlite3'
 def tearDown(self):self.t.cleanup()
 def runner(self,s,code='c',start=10,end=13):return PairWalkforwardRunner(self.path,run_id='FIXED-RUN',start_round=start,end_round=end,rule_hash=h('rule'),code_hash=h(code),schema_hash=h('schema'),pipeline=s)
 def test_prefix_prediction_result_and_r_plus_one_history(self):
  s=Source(range(10,12));self.runner(s,start=10,end=11).run()
  self.assertEqual([10,11],[e[2]+1 for e in s.events if e[0]=='compute'])
  for r in (10,11):self.assertLess(s.events.index(next(e for e in s.events if e[0]=='prediction' and e[1]==r)),s.events.index(('result',r)))
  computes=[e for e in s.events if e[0]=='compute'];self.assertEqual({},computes[0][3]);self.assertEqual(1,list(computes[1][3].values())[0])
 def test_selection_identity_separation_and_one_rep(self):
  self.runner(Source(),start=10,end=10).run();c=sqlite3.connect(self.path)
  self.assertEqual(2,c.execute('select count(*) from wf_identity_exposure').fetchone()[0]);self.assertEqual(1,c.execute('select count(*) from wf_selection_exposure').fetchone()[0]);c.close()
 def test_new_and_changed_signature_bootstrap(self):
  s=Source(change_sig=True);self.runner(s).run();comp=[e for e in s.events if e[0]=='compute']
  new_sig=next(key for key in comp[3][3] if key not in comp[2][3]);self.assertEqual({},comp[0][3]);self.assertEqual(1,comp[3][3][new_sig])
 def test_atomic_rollback_and_resume(self):
  s=Source(fail_round=11);r=self.runner(s)
  with self.assertRaises(RuntimeError):r.run()
  c=sqlite3.connect(self.path);self.assertEqual([10],[x[0] for x in c.execute('select evaluation_round from wf_round')]);c.close()
  s.fail_round=None;out=r.run();self.assertTrue(out['complete'])
 def test_resume_equals_continuous(self):
  s=Source();r=self.runner(s);r.run(max_rounds=2);r.run()
  c=sqlite3.connect(self.path);a=c.execute('select evaluation_round,decision_hash from wf_round order by 1').fetchall();c.close()
  other=Path(self.t.name)/'other.sqlite3';s2=Source();PairWalkforwardRunner(other,run_id='FIXED-RUN',start_round=10,end_round=13,rule_hash=h('rule'),code_hash=h('c'),schema_hash=h('schema'),pipeline=s2).run()
  c=sqlite3.connect(other);b=c.execute('select evaluation_round,decision_hash from wf_round order by 1').fetchall();c.close();self.assertEqual(a,b)
 def test_duplicate_constraints(self):
  self.runner(Source(),start=10,end=10).run();c=sqlite3.connect(self.path);c.execute('pragma foreign_keys=on')
  with self.assertRaises(sqlite3.IntegrityError):c.execute("insert into wf_round values ('FIXED-RUN',10,'COMPLETE',9,?,null,null,0,0,0,null)",(h('x'),))
  row=c.execute('select * from wf_selection_exposure').fetchone()
  with self.assertRaises(sqlite3.IntegrityError):c.execute('insert into wf_selection_exposure values (?,?,?,?,?,?)',('x',row[1],row[2],row[3],row[4],row[5]))
  c.close()
 def test_hash_mismatch_resume_blocked(self):
  self.runner(Source(),start=10,end=10).run()
  with self.assertRaisesRegex(RuntimeError,'CACHE_HASH_MISMATCH'):self.runner(Source(),code='changed',start=10,end=10).run()
 def test_future_leak_and_source_change_fail_fast(self):
  class Leak(Source):
   def compute_pre_result(self,r,end,history):return RoundPrediction(r,h('bad'),())
  with self.assertRaisesRegex(RuntimeError,'FUTURE_LEAKAGE'):self.runner(Leak(),start=10,end=10).run()
  s=Source();p=Path(self.t.name)/'source-change.sqlite3';r=PairWalkforwardRunner(p,run_id='FIXED-RUN',start_round=10,end_round=11,rule_hash=h('rule'),code_hash=h('c'),schema_hash=h('schema'),pipeline=s);r.run(max_rounds=1);s._hash=h('changed')
  with self.assertRaisesRegex(RuntimeError,'SOURCE_CHANGED'):r.run()
 def test_determinism(self):
  values=[]
  for i in range(10):
   p=Path(self.t.name)/f'{i}.sqlite3';PairWalkforwardRunner(p,run_id='FIXED-RUN',start_round=10,end_round=10,rule_hash=h('rule'),code_hash=h('c'),schema_hash=h('schema'),pipeline=Source()).run();c=sqlite3.connect(p);values.append(c.execute('select decision_hash from wf_round').fetchone()[0]);c.close()
  self.assertEqual(1,len(set(values)))
 def test_missing_gate_state_context_fails_before_outcome(self):
  class Missing(Source):
   def compute_pre_result(self,r,end,history):
    return RoundPrediction(end,h('prefix'),(PairPrediction('1-2-3__4-5-6',h('sig'),(1,2,3),(4,5,6),(0,),{}),))
  s=Missing()
  with self.assertRaisesRegex(RuntimeError,'GATE_STATE_CONTEXT_MISSING'):self.runner(s,start=10,end=10).run()
  self.assertFalse(any(e[0]=='result' for e in s.events))

if __name__=='__main__':unittest.main()

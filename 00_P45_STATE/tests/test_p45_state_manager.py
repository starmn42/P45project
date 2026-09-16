from __future__ import annotations
import copy, importlib.util, json, os, shutil, tempfile, unittest
from pathlib import Path

HERE=Path(__file__).resolve(); REAL_ROOT=HERE.parents[1]; PROJECT=REAL_ROOT.parent
SPEC=importlib.util.spec_from_file_location("p45_state_manager",REAL_ROOT/"tools/p45_state_manager.py")
M=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(M)

class StateManagerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=Path(tempfile.mkdtemp());self.root=self.tmp/"00_P45_STATE";self.root.mkdir()
  for name in M.TEXT_NAMES+("P45_CURRENT_STATE.json",):shutil.copy2(REAL_ROOT/name,self.root/name)
  (self.root/"state-history").mkdir();(self.root/"tools").mkdir()
  self.m=M.StateManager(self.root,PROJECT)
  self.decision={"decision_id":"DECISION-20990101-001","timestamp":"2099-01-01T00:00:00+09:00","project_version":"P45 v2.7.3","stage":"STATE_TEST","category":"TEST","decision":"테스트 결정","reason":"테스트","evidence":"synthetic","affected_files":"state only","affected_schema":"none","previous_rule":"A","new_rule":"B","allowed_next_action":"test","forbidden_actions":"none","approval_source":"test"}
 def tearDown(self):shutil.rmtree(self.tmp,ignore_errors=True)
 def install(self,state):
  state["state_hash"]=M.calculate_state_hash(state)
  (self.root/"P45_CURRENT_STATE.json").write_bytes(self.m.write_current_state_json(state))
  (self.root/"P45_CURRENT_STATE.md").write_bytes(M._encode_text(self.m.rebuild_current_state(state)))
  (self.root/"P45_HANDOFF.md").write_bytes(M._encode_text(self.m.rebuild_handoff(state)))
 def hashes(self):return {n:M.calculate_file_sha256(self.root/n) for n in M.TEXT_NAMES+("P45_CURRENT_STATE.json",)}

 def test_01_load_current_state(self):self.assertEqual(self.m.load_current_state()["current_stage"],"STAGE_7_2_COMPLETE")
 def test_02_md_json_core_match(self):self.assertTrue(self.m.validate_current_state()["valid"])
 def test_03_required_fields(self):
  s=self.m.load_current_state();del s["current_stage"];self.assertIn("REQUIRED_FIELD_MISSING:current_stage",self.m.validate_current_state(s,False)["errors"])
 def test_04_state_hash_ten_times(self):
  s=self.m.load_current_state();self.assertEqual(len({M.calculate_state_hash(s) for _ in range(10)}),1)
 def test_05_decision_hash_deterministic(self):self.assertEqual(M.calculate_decision_hash(self.decision),M.calculate_decision_hash({**self.decision,"timestamp":"other"}))
 def test_06_duplicate_decision_skipped(self):
  status,b=self.m.append_decision(self.decision);(self.root/"P45_DECISION_LOG.md").write_bytes(b);status2,b2=self.m.append_decision(self.decision);self.assertEqual((status2,b2),("DECISION_DUPLICATE_SKIPPED",b))
 def test_07_new_decision_one_append(self):
  old=(self.root/"P45_DECISION_LOG.md").read_bytes();status,new=self.m.append_decision(self.decision);self.assertEqual(status,"DECISION_APPENDED");self.assertEqual(new.count(self.decision["decision_id"].encode()),1);self.assertGreater(len(new),len(old))
 def test_08_decision_prefix_preserved(self):
  old=(self.root/"P45_DECISION_LOG.md").read_bytes();_,new=self.m.append_decision(self.decision);self.assertTrue(new.startswith(old))
 def test_09_current_state_update(self):
  r=self.m.atomic_state_update({"next_action":"TEST_ACTION"},dry_run=False);self.assertEqual(r["status"],"COMMITTED");self.assertEqual(self.m.load_current_state()["next_action"],"TEST_ACTION")
 def test_10_handoff_regenerated(self):
  self.m.atomic_state_update({"next_action":"HANDOFF_TEST"});self.assertIn("HANDOFF_TEST",M._decode_text(self.root/"P45_HANDOFF.md"))
 def test_11_snapshot_created(self):self.assertTrue((self.m.create_snapshot("TEST")/"state-manifest.json").exists())
 def test_12_existing_snapshot_immutable(self):
  p=self.m.create_snapshot("SAME");h=M.calculate_file_sha256(p/"state-manifest.json");self.m.create_snapshot("SAME");self.assertEqual(h,M.calculate_file_sha256(p/"state-manifest.json"))
 def test_13_dry_run_no_change(self):
  before=self.hashes();r=self.m.atomic_state_update({"next_action":"DRY"},dry_run=True);self.assertTrue(r["dry_run"]);self.assertEqual(before,self.hashes())
 def test_14_staged_validation_failure_keeps_original(self):
  before=self.hashes();orig=self.m.write_current_state_json;self.m.write_current_state_json=lambda s:b"bad"
  with self.assertRaises(M.StateError):self.m.atomic_state_update({"next_action":"BAD"})
  self.m.write_current_state_json=orig;self.assertEqual(before,self.hashes())
 def test_15_replace_failure_rolls_back(self):
  before=self.hashes()
  with self.assertRaises(OSError):self.m.atomic_state_update({"next_action":"ROLLBACK"},fail_after_replace=2)
  self.assertEqual(before,self.hashes())
 def test_16_interrupted_transaction_recovery(self):
  tx=self.root/".transactions"/"x";(tx/"backup").mkdir(parents=True);name="P45_HANDOFF.md";shutil.copy2(self.root/name,tx/"backup"/name);old=(self.root/name).read_bytes();(self.root/name).write_bytes(b"broken");(tx/"transaction.json").write_text(json.dumps({"status":"REPLACING","files":[name]}));self.m.recover_interrupted_transaction();self.assertEqual(old,(self.root/name).read_bytes())
 def test_17_lock_blocks_concurrent_writer(self):
  with self.m.lock("a"):
   with self.assertRaises(M.StateLocked):
    with self.m.lock("b"):pass
 def test_18_stale_lock_safe_recovery(self):
  self.m.lock_path.write_text(json.dumps({"pid":99999999,"transaction_id":"none"}));self.assertTrue(self.m.inspect_lock()["stale"])
  with self.m.lock("new"):self.assertTrue(self.m.lock_path.exists())
 def test_19_invalid_json_blocked(self):
  (self.root/"P45_CURRENT_STATE.json").write_bytes(M._encode_text("{"))
  with self.assertRaises(M.StateError):self.m.load_current_state()
 def test_20_md_json_mismatch_detected(self):
  p=self.root/"P45_CURRENT_STATE.md";p.write_bytes(M._encode_text(M._decode_text(p).replace("STAGE_7_2_COMPLETE","OTHER")));self.assertTrue(any("MD_JSON_MISMATCH" in x for x in self.m.validate_current_state()["errors"]))
 def test_21_replacement_character_blocked(self):
  p=self.root/"P45_HANDOFF.md";p.write_bytes(M._encode_text(M._decode_text(p)+"\ufffd"));self.assertTrue(any("U_FFFD" in x for x in self.m.validate_current_state()["errors"]))
 def test_22_crlf_bom_violation_blocked(self):
  p=self.root/"P45_HANDOFF.md";p.write_bytes(b"x\ny");e=self.m.validate_current_state()["errors"];self.assertTrue(any("BOM" in x or "BARE_LF" in x for x in e))
 def test_23_official_document_hash_conflict(self):
  s=self.m.load_current_state();s["official_documents"][0]["sha256"]="0"*64;self.install(s);self.assertIn("OFFICIAL_DOCUMENT_HASH",str(self.m.verify_handoff()["conflicts"]))
 def test_24_canonical_manifest_conflict(self):
  s=self.m.load_current_state();s["important_hashes"]["canonical_manifest"]="0"*64;self.install(s);self.assertIn("CANONICAL_MANIFEST_HASH",self.m.verify_handoff()["conflicts"])
 def test_25_walkforward_hash_conflict(self):
  s=self.m.load_current_state();s["important_hashes"]["walkforward_db"]="0"*64;self.install(s);self.assertIn("DB_HASH:walkforward_db",self.m.verify_handoff()["conflicts"])
 def test_26_trio_final_hash_conflict(self):
  s=self.m.load_current_state();s["important_hashes"]["trio_final_db"]="0"*64;self.install(s);self.assertIn("DB_HASH:trio_final_db",self.m.verify_handoff()["conflicts"])
 def test_27_normal_project_verified(self):self.assertEqual(self.m.verify_handoff()["status"],"STATE_HANDOFF_VERIFIED")
 def test_28_bootstrap_snapshot(self):
  p=self.m.create_snapshot("BOOTSTRAP");self.assertTrue(all((p/n).exists() for n in ("P45_CURRENT_STATE.md","P45_CURRENT_STATE.json","P45_HANDOFF.md","state-manifest.json")))
 def test_29_bootstrap_snapshot_no_state_change(self):
  before=self.hashes();self.m.create_snapshot("BOOTSTRAP");self.assertEqual(before,self.hashes())
 def test_30_protected_hashes_verified(self):self.assertFalse(any(x.startswith("PROTECTED_HASH") for x in self.m.verify_handoff()["conflicts"]))

if __name__=="__main__":unittest.main(verbosity=2)

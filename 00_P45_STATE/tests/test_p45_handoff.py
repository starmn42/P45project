from __future__ import annotations
import importlib.util,json,shutil,sqlite3,tempfile,unittest,zipfile
from pathlib import Path
REAL=Path(__file__).resolve().parents[1];PROJECT=REAL.parent
def load(name,path):s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=load("manager",REAL/"tools/p45_state_manager.py");H=load("handoff",REAL/"tools/p45_handoff.py")
class HandoffTests(unittest.TestCase):
 def setUp(self):
  self.tmp=Path(tempfile.mkdtemp());self.root=self.tmp/"00_P45_STATE";self.root.mkdir()
  for n in M.TEXT_NAMES+("P45_CURRENT_STATE.json",):shutil.copy2(REAL/n,self.root/n)
  (self.root/"state-history").mkdir();self.m=M.StateManager(self.root,PROJECT);self.bundle=self.root/"P45_PORTABLE_HANDOFF.zip"
  self.idea={"event_type":"IDEA_PENDING","source":"USER","title":"portable test","summary":"portable update","reason":"test","related_stage":"TEST","related_rule":"NONE","official_effect":"NONE"}
  self.decision={"event_type":"DECISION_CONFIRMED","source":"USER","approval_explicit":True,"decision_id":"DECISION-20990101-HANDOFF","decision":"handoff test decision","reason":"test","affected_state":{"next_action":"HANDOFF_TEST"}}
 def tearDown(self):shutil.rmtree(self.tmp,ignore_errors=True)
 def make(self):return H.create_bundle(self.root,self.bundle)
 def test_01_new_chat_exists(self):self.assertTrue((self.root/"P45_NEW_CHAT_START.md").exists())
 def test_02_bundle_created(self):self.assertTrue(Path(self.make()["path"]).exists())
 def test_03_required_files(self):
  self.make();
  with zipfile.ZipFile(self.bundle) as z:self.assertTrue(set(H.REQUIRED+("handoff-manifest.json",))<=set(z.namelist()))
 def test_04_manifest_file_hashes(self):
  self.make();
  with zipfile.ZipFile(self.bundle) as z:
   m=json.loads(z.read("handoff-manifest.json"));self.assertTrue(all(H.sha_bytes(z.read(e["relative_path"]))==e["sha256"] for e in m["files"]))
 def test_05_official_docs_hashes(self):
  b=self.make();self.assertTrue(all(Path(d["original_path"]).read_bytes()==zipfile.ZipFile(self.bundle).read(d["bundle_path"]) for d in b["manifest"]["official_documents"]))
 def test_06_db_excluded(self):
  self.make();
  with zipfile.ZipFile(self.bundle) as z:self.assertFalse(any(n.endswith((".sqlite3",".db")) for n in z.namelist()))
 def test_07_db_manifest(self):
  m=self.make()["manifest"];self.assertTrue(all("path" in m["external_sources"][k] and "sha256" in m["external_sources"][k] for k in ("walkforward_db","trio_final_db")))
 def test_08_content_hash_x10(self):self.assertEqual(len({H.portable_content_hash(self.root) for _ in range(10)}),1)
 def test_09_rebuild_same_meaning_hash(self):self.assertEqual(self.make()["portable_content_hash"],self.make()["portable_content_hash"])
 def test_10_conversation_no_bundle_change(self):
  self.make();h=H.sha_file(self.bundle);self.m.process_event({"event_type":"CONVERSATION_ONLY","source":"USER"});self.assertEqual(h,H.sha_file(self.bundle))
 def test_11_idea_updates_bundle(self):
  self.make();h=H.sha_file(self.bundle);self.m.process_event(self.idea);self.assertNotEqual(h,H.sha_file(self.bundle))
 def test_12_decision_updates_bundle(self):
  self.make();h=H.sha_file(self.bundle);self.m.process_event(self.decision);self.assertNotEqual(h,H.sha_file(self.bundle))
 def test_13_bundle_failure_keeps_commit(self):
  old=self.m.refresh_portable_bundle;self.m.refresh_portable_bundle=lambda:(_ for _ in()).throw(OSError("fail"));r=self.m.process_event(self.decision);self.assertEqual(r["status"],"STATE_COMMITTED_BUNDLE_FAILED");self.assertEqual(self.m.load_current_state()["next_action"],"HANDOFF_TEST");self.m.refresh_portable_bundle=old
 def test_14_bundle_failure_report(self):
  old=self.m.refresh_portable_bundle;self.m.refresh_portable_bundle=lambda:(_ for _ in()).throw(OSError("fail"));self.assertIn("bundle_error",self.m.process_event(self.decision));self.m.refresh_portable_bundle=old
 def test_15_bundle_retry(self):self.assertEqual(self.m.refresh_portable_bundle()["status"],"BUNDLE_READY")
 def test_16_boot_order(self):self.assertEqual(H.cold_start_local(self.root,PROJECT)["read_order"],list(H.BOOT_ORDER))
 def test_17_stage_from_files(self):
  s=json.loads((self.root/"P45_CURRENT_STATE.json").read_bytes().decode("utf-8-sig"));self.assertEqual(H.cold_start_local(self.root,PROJECT)["recovered"]["stage"],s["current_stage"])
 def test_18_walkforward_recovered(self):self.assertEqual(H.cold_start_local(self.root,PROJECT)["recovered"]["walkforward"],self.m.load_current_state()["walkforward"])
 def test_19_trio_counts_recovered(self):self.assertEqual(H.cold_start_local(self.root,PROJECT)["recovered"]["trio_state"],self.m.load_current_state()["trio_state"])
 def test_20_valid_pair_recovered(self):self.assertEqual(H.cold_start_local(self.root,PROJECT)["recovered"]["trio_state"]["valid_for_pair_true"],self.m.load_current_state()["trio_state"]["valid_for_pair_true"])
 def test_21_pair_recovered(self):self.assertEqual(H.cold_start_local(self.root,PROJECT)["recovered"]["pair_state"],self.m.load_current_state()["pair_state"])
 def test_22_next_recovered(self):self.assertEqual(H.cold_start_local(self.root,PROJECT)["recovered"]["next_action"],self.m.load_current_state()["next_action"])
 def test_23_forbidden_recovered(self):self.assertEqual(H.cold_start_local(self.root,PROJECT)["recovered"]["forbidden_actions"],self.m.load_current_state()["forbidden_actions"])
 def test_24_decision_recovered(self):self.assertEqual(H.cold_start_local(self.root,PROJECT)["recovered"]["latest_decision"],self.m.load_current_state()["last_decision_id"])
 def test_25_unresolved_ideas_recovered(self):
  self.m.process_event(self.idea);self.assertTrue(self.m.unresolved_ideas())
 def test_26_full_verification(self):self.assertEqual(H.cold_start_local(self.root,PROJECT,True)["status"],"STATE_HANDOFF_VERIFIED")
 def test_27_portable_only(self):
  self.make();self.assertEqual(H.cold_start_bundle(self.bundle)["status"],"STATE_HANDOFF_PORTABLE_ONLY")
 def test_28_hash_conflict(self):
  self.make();tmp=self.bundle.with_suffix('.bad');
  with zipfile.ZipFile(self.bundle) as a,zipfile.ZipFile(tmp,'w') as b:
   for n in a.namelist():b.writestr(n,b'bad' if n=='P45_HANDOFF.md' else a.read(n))
  self.assertEqual(H.cold_start_bundle(tmp)["status"],"STATE_HANDOFF_CONFLICT")
 def test_29_meaning_conflict(self):
  p=self.root/"P45_HANDOFF.md";p.write_bytes(M._encode_text(M._decode_text(p).replace(self.m.load_current_state()["current_stage"],"OTHER")));self.assertEqual(H.cold_start_local(self.root,PROJECT)["status"],"STATE_HANDOFF_CONFLICT")
 def test_30_q1_q6(self):self.assertTrue(all(H.cold_start_local(self.root,PROJECT)["questions"].values()))
 def test_31_state_check_recovered(self):self.assertTrue(H.cold_start_local(self.root,PROJECT)["state_check_recovered"])
 def test_32_protected(self):self.assertFalse(any(x.startswith("PROTECTED_HASH") for x in self.m.verify_handoff()["conflicts"]))
 def test_33_walk_db(self):self.assertEqual(H.sha_file(Path(self.m.load_current_state()["walkforward"]["source_db"])),self.m.load_current_state()["walkforward"]["sha256"])
 def test_34_trio_db(self):self.assertEqual(H.sha_file(Path(self.m.load_current_state()["trio_state"]["result_db"])),self.m.load_current_state()["trio_state"]["sha256"])
 def test_35_number_zero(self):
  with sqlite3.connect(PROJECT/"v27_storage/db/p45_v273_core.sqlite3") as d:self.assertEqual(d.execute("select count(*) from number_ledger").fetchone()[0],0)
 def test_36_pair_zero(self):
  with sqlite3.connect(PROJECT/"v27_storage/db/p45_v273_core.sqlite3") as d:self.assertEqual(d.execute("select count(*) from pair_ledger").fetchone()[0],0)
 def test_37_core_audit_zero(self):
  for p in (PROJECT/"v27_storage/db/p45_v273_core.sqlite3",PROJECT/"v27_storage/db/p45_v273_audit.sqlite3"):
   with sqlite3.connect(p) as d:
    ts=[r[0] for r in d.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")];self.assertEqual(sum(d.execute(f"select count(*) from {t}").fetchone()[0] for t in ts),0)
if __name__=="__main__":unittest.main(verbosity=2)

from __future__ import annotations
import importlib.util,json,shutil,sqlite3,tempfile,unittest
from pathlib import Path

HERE=Path(__file__).resolve();REAL=HERE.parents[1];PROJECT=REAL.parent
S=importlib.util.spec_from_file_location("p45_state_manager",REAL/"tools/p45_state_manager.py");M=importlib.util.module_from_spec(S);S.loader.exec_module(M)

class CaptureTests(unittest.TestCase):
 def setUp(self):
  self.tmp=Path(tempfile.mkdtemp());self.root=self.tmp/"00_P45_STATE";self.root.mkdir()
  for n in M.TEXT_NAMES+("P45_CURRENT_STATE.json",):shutil.copy2(REAL/n,self.root/n)
  (self.root/"state-history").mkdir();self.m=M.StateManager(self.root,PROJECT)
  self.question={"event_type":"CONVERSATION_ONLY","source":"USER","summary":"왜 43회부터야?"}
  self.idea={"event_type":"IDEA_PENDING","source":"USER","title":"끝수와 3단위 교차 연구","summary":"끝수와 3단위를 함께 보는 별도 연구를 시험한다","reason":"독립 문맥 가능성","related_stage":"FUTURE_RESEARCH","related_rule":"NONE","official_effect":"NONE"}
  self.amb={**self.idea,"event_type":"AMBIGUOUS_IMPORTANT","title":"방향 변경 가능성","summary":"이 방식으로 가는 게 나을 수도 있다"}
  self.decision={"event_type":"DECISION_CONFIRMED","source":"USER","approval_explicit":True,"decision_id":"DECISION-20990101-CAPTURE","decision":"앞으로 작업 종료 전 STATE CHECK를 한다","reason":"인수인계 보존","related_stage":"STATE_SYSTEM_STAGE_3","affected_state":{"next_action":"STATE_CHECK_ACTIVE"},"allowed_next_action":"STATE_CHECK","forbidden_actions":["SKIP_STATE_CHECK"]}
 def tearDown(self):shutil.rmtree(self.tmp,ignore_errors=True)
 def hashes(self):return {n:M.calculate_file_sha256(self.root/n) for n in M.TEXT_NAMES+("P45_CURRENT_STATE.json",)}
 def test_01_question_class(self):self.assertEqual(self.m.process_event(self.question)["status"],"STATE_NO_CHANGE")
 def test_02_question_changes_nothing(self):
  h=self.hashes();self.m.process_event(self.question);self.assertEqual(h,self.hashes())
 def test_03_new_proposal_valid_idea(self):self.assertTrue(self.m.validate_event(self.idea)["valid"])
 def test_04_idea_appends_inbox(self):
  r=self.m.process_event(self.idea);self.assertEqual(r["status"],"IDEA_CAPTURED");self.assertIn("끝수와 3단위",M._decode_text(self.root/"P45_IDEA_INBOX.md"))
 def test_05_idea_does_not_change_research_state(self):
  s=self.m.load_current_state();self.m.process_event(self.idea);s2=self.m.load_current_state();self.assertEqual(M._logical_state(s),M._logical_state(s2))
 def test_06_duplicate_idea_skipped(self):
  self.m.process_event(self.idea);r=self.m.process_event(self.idea);self.assertEqual(r["status"],"IDEA_DUPLICATE_SKIPPED")
 def test_07_modified_idea_separate(self):
  self.m.process_event(self.idea);x={**self.idea,"summary":self.idea["summary"]+" 수정"};self.assertEqual(self.m.process_event(x)["status"],"IDEA_CAPTURED")
 def test_08_ambiguous_not_decision(self):
  r=self.m.process_event(self.amb);self.assertEqual(r["classification"],"AMBIGUOUS_IMPORTANT");self.assertNotIn("DECISION-",r)
 def test_09_clear_future_instruction_decision(self):self.assertTrue(self.m.validate_event(self.decision)["valid"])
 def test_10_clear_prohibition_decision(self):
  e={**self.decision,"decision":"앞으로 이 방식은 쓰지 마","decision_id":"DECISION-20990101-NO"};self.assertEqual(self.m.process_event(e)["status"],"STATE_UPDATE_OK")
 def test_11_persistent_instruction_logged(self):
  self.m.process_event(self.decision);self.assertIn(self.decision["decision"],M._decode_text(self.root/"P45_DECISION_LOG.md"))
 def test_12_decision_updates_state(self):
  self.m.process_event(self.decision);self.assertEqual(self.m.load_current_state()["next_action"],"STATE_CHECK_ACTIVE")
 def test_13_decision_updates_handoff(self):
  self.m.process_event(self.decision);self.assertIn("STATE_CHECK_ACTIVE",M._decode_text(self.root/"P45_HANDOFF.md"))
 def test_14_decision_creates_snapshot(self):
  self.m.process_event(self.decision);self.assertEqual(len(list((self.root/"state-history").iterdir())),1)
 def test_15_verify_after_decision(self):
  self.m.process_event(self.decision);self.assertEqual(self.m.verify_handoff()["status"],"STATE_HANDOFF_VERIFIED")
 def test_16_idea_failure_preserves_original(self):
  before=(self.root/"P45_IDEA_INBOX.md").read_bytes();idea=self.m._idea_from_event(self.idea)
  with self.assertRaises(OSError):self.m.append_idea(idea,simulate_failure=True)
  self.assertEqual(before,(self.root/"P45_IDEA_INBOX.md").read_bytes())
 def test_17_decision_failure_rollback(self):
  h=self.hashes()
  with self.assertRaises(OSError):self.m.atomic_state_update({"next_action":"X"},fail_after_replace=1)
  self.assertEqual(h,self.hashes())
 def test_18_duplicate_decision_skipped(self):
  self.m.process_event(self.decision);v=self.m.load_current_state()["state_version"];r=self.m.process_event(self.decision);self.assertEqual(r["status"],"DECISION_DUPLICATE_SKIPPED");self.assertEqual(v,self.m.load_current_state()["state_version"])
 def test_19_unknown_event_blocked(self):
  with self.assertRaises(M.StateError):self.m.process_event({"event_type":"UNKNOWN"})
 def test_20_idea_auto_promotion_blocked(self):
  with self.assertRaises(M.StateError):self.m.process_event({**self.idea,"promote_to_official":True})
 def test_21_ambiguous_auto_promotion_blocked(self):
  with self.assertRaises(M.StateError):self.m.process_event({**self.amb,"affected_state":{"project_version":"x"}})
 def test_22_no_change_version_same(self):
  v=self.m.load_current_state()["state_version"];self.m.process_event(self.question);self.assertEqual(v,self.m.load_current_state()["state_version"])
 def test_23_idea_research_state_same(self):
  s=self.m.load_current_state();self.m.process_event(self.idea);a=self.m.load_current_state();self.assertEqual((s["current_stage"],s["project_version"]),(a["current_stage"],a["project_version"]))
 def test_24_official_update_bumps_version(self):
  v=self.m.load_current_state()["state_version"];self.m.process_event(self.decision);self.assertNotEqual(v,self.m.load_current_state()["state_version"])
 def test_25_stage2_core_validation_still_passes(self):self.assertTrue(self.m.validate_current_state()["valid"])
 def test_26_protected_hashes_unchanged(self):self.assertFalse(any(x.startswith("PROTECTED_HASH") for x in self.m.verify_handoff()["conflicts"]))
 def test_27_walkforward_hash_unchanged(self):self.assertNotIn("DB_HASH:walkforward_db",self.m.verify_handoff()["conflicts"])
 def test_28_trio_final_hash_unchanged(self):self.assertNotIn("DB_HASH:trio_final_db",self.m.verify_handoff()["conflicts"])
 def test_29_number_unchanged(self):
  with sqlite3.connect(PROJECT/"v27_storage/db/p45_v273_core.sqlite3") as d:self.assertEqual(d.execute("select count(*) from number_ledger").fetchone()[0],0)
 def test_30_pair_zero(self):
  with sqlite3.connect(PROJECT/"v27_storage/db/p45_v273_core.sqlite3") as d:self.assertEqual(d.execute("select count(*) from pair_ledger").fetchone()[0],0)
 def test_31_core_audit_zero(self):
  for p in (PROJECT/"v27_storage/db/p45_v273_core.sqlite3",PROJECT/"v27_storage/db/p45_v273_audit.sqlite3"):
   with sqlite3.connect(p) as d:
    tabs=[r[0] for r in d.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")];self.assertEqual(sum(d.execute(f"select count(*) from {t}").fetchone()[0] for t in tabs),0)
 def test_32_event_hash_deterministic(self):self.assertEqual(len({M.calculate_event_hash(self.idea) for _ in range(10)}),1)
 def test_33_start_here_policy_order(self):
  text=M._decode_text(self.root/"P45_START_HERE.md");self.assertLess(text.index("P45_CAPTURE_POLICY.md"),text.index("P45_HANDOFF.md"))
 def test_34_unresolved_idea_loaded(self):
  self.m.process_event(self.idea);self.assertEqual(len(self.m.unresolved_ideas()),1)
 def test_35_state_check_protocol(self):self.assertEqual(self.m.state_check_protocol()["protocol"],"P45_STATE_CHECK")

if __name__=="__main__":unittest.main(verbosity=2)

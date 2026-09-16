from __future__ import annotations
import hashlib, json, shutil, tempfile, unittest
from pathlib import Path

from p45_v27.prospective_web import ProspectiveOrbitService, calculate_outcome

ROOT=Path(__file__).resolve().parents[1]

class WebV1Tests(unittest.TestCase):
    def service(self)->ProspectiveOrbitService:return ProspectiveOrbitService(ROOT)

    def test_current_real_state_exact_and_read_only(self):
        protected=[ROOT/'v27_storage/prospective/trio_orbit_v1_001/P45_TRIO_ORBIT_TARGET_1239_SEALED_PREDRAW_001.md',ROOT/'v27_storage/prospective/trio_orbit_v1_001/P45_TRIO_ORBIT_PROSPECTIVE_LOG_001.csv',ROOT/'v27_storage/prospective/trio_orbit_v1_001/P45_TRIO_ORBIT_PROSPECTIVE_STATE_001.json']
        before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in protected];d=self.service().read();after=[hashlib.sha256(p.read_bytes()).hexdigest() for p in protected]
        self.assertEqual(before,after);self.assertEqual(1240,d['canonical']['latest']);self.assertEqual(1241,d['current']['target']);self.assertEqual('WAITING_FOR_RESULT',d['current']['action'])
        self.assertEqual(['20 22 36','23 25 39','26 28 42'],d['orbits']['fixed']['trios']);self.assertEqual(['6 11 16','13 33 38','20 30 40'],d['orbits']['linked']['trios']);self.assertEqual([11,13,20],d['orbits']['linked']['anchors'])
        self.assertEqual(0,d['divergence']['common_count']);self.assertEqual('NO',d['divergence']['reset']);self.assertEqual('PASS',d['seal']['verify']);self.assertTrue(d['integrity']['kts_pass']);self.assertTrue(d['integrity']['all_pass'])

    def test_real_no_result_blocks_outcome_and_preview(self):
        service=self.service()
        with self.assertRaisesRegex(RuntimeError,'TARGET_RESULT_NOT_AVAILABLE'):service.record_outcome(1241)
        with self.assertRaisesRegex(RuntimeError,'PREVIOUS_OUTCOME_NOT_RECORDED'):service.preview_next()

    def test_protected_path_write_blocked(self):
        with self.assertRaisesRegex(RuntimeError,'PROTECTED_PATH_WRITE_BLOCKED'):self.service()._safe_write(ROOT/'blocked.txt','x')

    def test_outcome_math_fixture(self):
        d={'fixed_A':'1 2 3','fixed_B':'4 5 6','fixed_C':'7 8 9','linked_A':'1 2 3','linked_B':'4 7 10','linked_C':'11 12 13'}
        x=calculate_outcome(d,(1,2,3,4,5,10));self.assertEqual([3,2,0],x['fixed_hits']);self.assertEqual([3,2,0],x['linked_hits']);self.assertTrue(x['fixed_success']);self.assertTrue(x['linked_success'])

    def make_fixture(self,temp:Path)->ProspectiveOrbitService:
        for rel in ['v27_storage/live','v27_storage/audits/current_1239_predraw_rerun_001','v27_storage/experiments/trio_orbit_v1_001','v27_storage/prospective/trio_orbit_v1_001','00_P45_STATE','v27_storage/reports','v27_storage/backtests','90_RESEARCH']:(temp/rel).mkdir(parents=True,exist_ok=True)
        files=['v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv','00_P45_STATE/P45_CURRENT_STATE.json','v27_storage/reports/p45_v274_pair_v12_final_aggregation.json','v27_storage/backtests/p45_v274_pair_v12_final_aggregation.sqlite3']
        orbit=['P45_TRIO_ORBIT_V1_PROTOCOL_LOCKED_001.md','P45_TRIO_ORBIT_V1_KTS45_SCHEDULE_001.csv','P45_TRIO_ORBIT_V1_ROUND_TRACE_001.csv','P45_TRIO_ORBIT_V1_BACKTEST_RESULT_001.md','p45_trio_orbit_v1_backtest_001.py']
        prospective=['P45_TRIO_ORBIT_TARGET_1239_SEALED_PREDRAW_001.md','P45_TRIO_ORBIT_PROSPECTIVE_LOG_001.csv','P45_TRIO_ORBIT_PROSPECTIVE_STATE_001.json','P45_PROSPECTIVE_ORBIT_START_AND_STATE_SYNC_SHA256SUMS_001.txt']
        for rel in files:shutil.copy2(ROOT/rel,temp/rel)
        shutil.copy2(ROOT/'90_RESEARCH/P45_RESEARCH_MASTER_INDEX_003.md',temp/'90_RESEARCH/P45_RESEARCH_MASTER_INDEX_003.md')
        for name in orbit:shutil.copy2(ROOT/'v27_storage/experiments/trio_orbit_v1_001'/name,temp/'v27_storage/experiments/trio_orbit_v1_001'/name)
        for name in prospective:shutil.copy2(ROOT/'v27_storage/prospective/trio_orbit_v1_001'/name,temp/'v27_storage/prospective/trio_orbit_v1_001'/name)
        # The initial manifest also references these two root documents.
        shutil.copy2(ROOT/'1-P45_GPT_RECOVERY_HANDOFF_032.md',temp/'1-P45_GPT_RECOVERY_HANDOFF_032.md');shutil.copy2(ROOT/'2-P45_PROJECT_CORE_GUIDE_TRIO_FIRST_ORBIT_006.md',temp/'2-P45_PROJECT_CORE_GUIDE_TRIO_FIRST_ORBIT_006.md')
        canonical=temp/'v27_storage/live/p45_live_draws.csv';shutil.copy2(ROOT/'v27_storage/audits/current_1239_predraw_rerun_001/STAGING_CONTIGUOUS_DRAW_1_1238.csv',canonical)
        with canonical.open('a',encoding='utf-8',newline='') as f:f.write('1239,2026-08-29,1,2,3,4,5,6,7\n')
        service=ProspectiveOrbitService(temp);service.canonical=canonical
        row=service._log_rows()[0]
        for key in [x for x in row if "hits_" in x or "success" in x or "contribution" in x or x in ("linked_only_anchor_reappeared","outcome_recorded_at")]:row[key]="PENDING" if key!="outcome_recorded_at" else ""
        row["result_status"]="PENDING";service._write_log([row]);service._write_manifest();return service

    def test_fixture_outcome_preview_seal_and_immutability(self):
        with tempfile.TemporaryDirectory() as td:
            service=self.make_fixture(Path(td));old_sealed=service._latest_sealed();old_hash=hashlib.sha256(old_sealed.read_bytes()).hexdigest()
            outcome=service.record_outcome(1239);self.assertEqual(1239,outcome['target']);self.assertEqual(old_hash,hashlib.sha256(old_sealed.read_bytes()).hexdigest())
            a=service.preview_next();b=service.preview_next();self.assertEqual(a,b);self.assertEqual(1240,a['target'])
            sealed=service.seal_next(a['preview_sha256']);self.assertEqual(1240,sealed['target']);self.assertTrue(Path(sealed['sealed_path']).is_file());self.assertEqual(old_hash,hashlib.sha256(old_sealed.read_bytes()).hexdigest())
            with self.assertRaisesRegex(RuntimeError,'SEALED_OVERWRITE_BLOCKED'):service._safe_write(Path(sealed['sealed_path']),'x',overwrite=False)
            self.assertTrue(service.read()['integrity']['all_pass'])

    def test_preview_state_change_blocks_retro_seal(self):
        with tempfile.TemporaryDirectory() as td:
            service=self.make_fixture(Path(td));service.record_outcome(1239);preview=service.preview_next();canonical=service.canonical
            with canonical.open('a',encoding='utf-8',newline='') as f:f.write('1240,2026-09-05,8,9,10,11,12,13,14\n')
            with self.assertRaisesRegex(RuntimeError,'CANONICAL_STATE_MISMATCH|PREVIEW_STATE_CHANGED'):service.seal_next(preview['preview_sha256'])

    def test_duplicate_target_blocks_preview(self):
        with tempfile.TemporaryDirectory() as td:
            service=self.make_fixture(Path(td));service.record_outcome(1239);rows=service._log_rows();duplicate=dict(rows[-1]);duplicate['target_round']='1240';duplicate['source_round']='1239';duplicate['result_status']='PENDING';service._write_log(rows+[duplicate]);service._write_manifest()
            with self.assertRaisesRegex(RuntimeError,'DUPLICATE_TARGET'):service.preview_next()

    def test_ui_has_four_pages_and_no_manual_number_controls(self):
        html=(ROOT/'web/index.html').read_text(encoding='utf-8');self.assertEqual(4,html.count('class="v1-page'))
        for forbidden in ('<input','<textarea','reroll','manual TRIO selector'):self.assertNotIn(forbidden,html)

if __name__=='__main__':unittest.main()

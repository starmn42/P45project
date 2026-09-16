from __future__ import annotations

import copy,tempfile,unittest
from pathlib import Path

from p45_v27.core_store import CoreStore
from p45_v27.initialize import initialize_storage
from p45_v27.number_engine import (_overlap,calculate_roles,combine_number_risk,decide_number,
    finalize_numbers,select_number_context)
from p45_v27.number_store import load_number_ledger,persist_number_ledger
from p45_v27.schema import SCHEMA_VERSION
from p45_v27.stage55_diagnostics import load_draw_csv
from p45_v27.stage6_diagnostics import diagnose_stage6
from p45_v27.units import DEFINITIONS,Draw

H64="e"*64
DATA=Path("analysis/structure-1236/analysis-input.csv")


class Stage6V272Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=diagnose_stage6(DATA,1236);cls.draws=load_draw_csv(DATA)

    def test_01_context_selection_deterministic_and_not_weighted(self):
        metrics={u:self.result["unit_metrics"][u][3] for u in DEFINITIONS}
        choices=[select_number_context(metrics)[0]["unit_type"] for _ in range(10)]
        self.assertEqual(len(set(choices)),1)
        self.assertNotIn("score",str(select_number_context(metrics)).lower())

    def test_02_conservative_risk_max(self):
        metrics={u:copy.deepcopy(self.result["unit_metrics"][u][3]) for u in DEFINITIONS}
        metrics["UNIT_3"]["bonus_dependence"]="BONUS_DEPENDENCE_HIGH"
        metrics["UNIT_5"]["opposite_risk"]="HIGH";metrics["UNIT_9"]["structure_state"]="SEVERE"
        risk=combine_number_risk(metrics)
        self.assertEqual((risk["number_bonus_dependence"],risk["number_opposite_risk"],risk["number_structure_state"]),
                         ("BONUS_DEPENDENCE_HIGH","HIGH","SEVERE"))

    def test_03_real_state_boundaries_and_pass_18_gates(self):
        self.assertEqual(self.result["state_counts"],{"NUMBER_HOLD":20,"NUMBER_WEAKEN":21,"NUMBER_PASS":1,"NUMBER_TEST":3})
        passed=self.result["rows"][3]
        self.assertTrue(all(passed["gate_results"].values()));self.assertEqual(len(passed["gate_results"]),18)
        self.assertTrue(any(r["number_state"]=="NUMBER_HOLD" for r in self.result["rows"].values()))
        self.assertTrue(any(r["number_state"]=="NUMBER_WEAKEN" for r in self.result["rows"].values()))
        self.assertTrue(any(r["number_state"]=="NUMBER_TEST" for r in self.result["rows"].values()))
        metrics={u:copy.deepcopy(self.result["unit_metrics"][u][3]) for u in DEFINITIONS}
        for metric in metrics.values():metric["unit_state"]="UNIT_FAIL"
        base=self.result["rows"][3];roles={k:base[k] for k in ("return_roles","primary_return_role","role_signature")};roles["has_return_role"]=True
        relation=copy.deepcopy(self.result["relations"][3]);relation["relation_state"]="UNIT_NO_SUPPORT"
        failed=decide_number(3,metrics,relation,self.result["pareto"]["3"],roles)
        self.assertEqual(failed["number_state"],"NUMBER_FAIL")

    def test_04_valid_test_and_pareto_not_auto_fail(self):
        self.assertEqual(self.result["valid_test_count"],3)
        self.assertTrue(all(r["number_state"]!="NUMBER_FAIL" for r in self.result["rows"].values() if r["pareto_state"]=="UNIT_PARETO_DOMINATED"))

    def test_05_retired_excluded(self):
        base=self.result["rows"][3];metrics={u:self.result["unit_metrics"][u][3] for u in DEFINITIONS}
        roles={k:base[k] for k in ("return_roles","primary_return_role","role_signature")};roles["has_return_role"]=True
        retired=decide_number(3,metrics,self.result["relations"][3],self.result["pareto"]["3"],roles,retired_reason="SUPERSEDED")
        self.assertEqual(retired["number_state"],"NUMBER_RETIRED");self.assertFalse(retired["valid_test_status"])

    def test_06_return_future_boundary_and_multiple_roles(self):
        metrics={u:self.result["unit_metrics"][u][3] for u in DEFINITIONS}
        primary=select_number_context(metrics)[0]["unit_type"]
        a=calculate_roles(DEFINITIONS,self.draws,1236,3,primary,metrics)
        b=calculate_roles(DEFINITIONS,self.draws+[Draw(1236,(1,2,3,4,5,6),7)],1236,3,primary,metrics)
        self.assertEqual(a,b);self.assertEqual(len(a["return_roles"]),5)
        self.assertEqual(len(a["role_signature"]),5)

    def test_07_nonreturn_and_return_counts(self):
        self.assertEqual(self.result["return_candidate_count"],21)
        self.assertEqual(self.result["nonreturn_candidate_count"],4)

    def test_08_overlap_four_states(self):
        p={"unit_type":"UNIT_3","role_type":"RETURN_FROM_ANNIHILATION","group_id":"1-3"}
        q={"unit_type":"UNIT_5","role_type":"CONTINUATION_CONTEXT","group_id":"1-5"}
        a={("UNIT_3","R","G","E")};b=set(a);c={("UNIT_3","X","Y","Z")};d={("UNIT_5","C","H","K")}
        self.assertEqual(_overlap(a,b,p,p),"IDENTICAL")
        self.assertEqual(_overlap(a,c,p,p),"HIGH")
        self.assertEqual(_overlap(a,a|d,p,q),"PARTIAL")
        self.assertEqual(_overlap(a,d,p,q),"NONE")

    def _scenario(self,passes,weaken,tests=0):
        rows=copy.deepcopy(self.result["rows"])
        for n,row in rows.items():row["number_state"]="NUMBER_HOLD";row["valid_test_status"]=False;row["pareto_state"]="UNIT_PARETO_NONDOMINATED"
        nums=list(range(1,46))
        for n in nums[:passes]:rows[n]["number_state"]="NUMBER_PASS"
        for n in nums[passes:passes+weaken]:rows[n]["number_state"]="NUMBER_WEAKEN"
        for n in nums[passes+weaken:passes+weaken+tests]:rows[n]["number_state"]="NUMBER_TEST";rows[n]["valid_test_status"]=True
        return finalize_numbers(rows)

    def test_09_pass_pool_6_to_12(self):
        r=self._scenario(8,0);self.assertEqual(r["candidate_pool_type"],"CORE_PASS_POOL");self.assertEqual(len(r["candidate_numbers"]),8)

    def test_10_pass_pool_13_top12(self):
        r=self._scenario(13,0);self.assertEqual(len(r["candidate_numbers"]),12);self.assertTrue(all(n<=13 for n in r["candidate_numbers"]))

    def test_11_expanded_pool_and_top12(self):
        r=self._scenario(2,13,3);self.assertEqual(r["candidate_pool_type"],"EXPANDED_TEST_POOL");self.assertEqual(len(r["candidate_numbers"]),12)

    def test_12_expanded_under6_hold(self):
        r=self._scenario(2,2,1);self.assertEqual(r["candidate_pool_type"],"RESEARCH_HOLD");self.assertEqual(r["candidate_numbers"],[])

    def test_13_tie_order_14_and_determinism(self):
        self.assertTrue(all(len(row["tie_break_key"])==14 for row in self.result["rows"].values()))
        hashes={diagnose_stage6(DATA,1236)["execution_hash"] for _ in range(10)}
        self.assertEqual(len(hashes),1)

    def test_14_45_row_database_roundtrip(self):
        with tempfile.TemporaryDirectory() as t:
            paths=initialize_storage(Path(t));self.assertEqual(SCHEMA_VERSION,273);store=CoreStore(paths)
            e=store.register_engine_version(version_label="2.7.2-test",directive_sha256=H64,implementation_order_sha256=H64,
                rule_hash=H64,code_hash=H64,effective_round=1)
            run=store.create_core_run(engine_version_id=e,analysis_round=1236,record_class="BACKTEST",raw_data_hash=H64,
                normalized_data_hash=H64,rule_hash=H64,code_hash=H64)
            persist_number_ledger(store,run,self.result,H64,self.result["execution_hash"])
            loaded=load_number_ledger(store,run);self.assertEqual(len(loaded),45)
            self.assertEqual([r["decision_hash"] for r in loaded],[self.result["rows"][n]["decision_hash"] for n in range(1,46)])


if __name__=="__main__":unittest.main()

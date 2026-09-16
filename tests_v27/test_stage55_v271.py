from __future__ import annotations

import tempfile
import unittest
from math import sqrt
from pathlib import Path

from p45_v27.core_store import CoreStore
from p45_v27.database import connect_core, initialize_storage
from p45_v27.initialize import initialize_storage as initialize
from p45_v27.schema import SCHEMA_VERSION
from p45_v27.unit_relations import build_number_relations
from p45_v27.unit_state_store import load_unit_decisions, update_unit_decisions
from p45_v27.unit_states import (_context_sample_state, _period_level, decide_unit_state,
    evidence_label, evaluate_number_unit, wilson95)
from p45_v27.units import DEFINITIONS, Draw, calculate_unit
from p45_v27.units.persistence import persist_unit_analysis

H64 = "c" * 64


def summary(label, rate=.2, count=100):
    return {"sample_count": count, "hit_count": round(rate*count), "rate": rate,
            "wilson_low_95": max(0,rate-.05), "wilson_high_95": min(1,rate+.05), "evidence_label": label}


def context(label="POSITIVE_CONFIRMED", state="SUFFICIENT", main_label="POSITIVE_TENTATIVE"):
    overall = {"integrated": summary(label), "main": summary(main_label,.16), "bonus": summary("NEUTRAL",1/45)}
    r100 = {"integrated": summary("POSITIVE_TENTATIVE",.18,20), "main": summary("NEUTRAL",.14,20),
            "bonus": summary("NEUTRAL",.02,20), "sample_level":"OFFICIAL"}
    r50 = {"integrated": summary("NEUTRAL",7/45,10), "main": summary("NEUTRAL",6/45,10),
           "bonus": summary("NEUTRAL",1/45,10), "sample_level":"OFFICIAL"}
    return {"sample_state":state,"overall":overall,"recent100":r100,"recent50":r50,
            "recent20":{**r50,"sample_level":"TEST_ONLY"}}


def draws(count=80):
    out=[]
    for r in range(1,count+1):
        start=(r*7)%45; vals=[((start+i*11)%45)+1 for i in range(7)]
        out.append(Draw(r,tuple(sorted(vals[:6])),vals[6]))
    return out


class Stage55V271Test(unittest.TestCase):
    def test_01_schema_271(self):
        self.assertEqual(SCHEMA_VERSION,273)
        with tempfile.TemporaryDirectory() as t:
            paths=initialize(Path(t)); db=connect_core(paths)
            try:
                self.assertEqual(db.execute("pragma user_version").fetchone()[0],273)
                columns={r[1] for r in db.execute("pragma table_info(unit_round_metric)")}
                self.assertIn("raw_integrated_deviation",columns);self.assertIn("standardized_integrated_deviation",columns)
                self.assertNotIn("normalized_integrated_deviation",columns)
            finally: db.close()

    def test_02_raw_and_standardized_deviation(self):
        result=calculate_unit(DEFINITIONS["UNIT_10"],draws(),81)
        row=next(r for r in result.round_metrics if r["group_size"]==5)
        expected=7*5/45; raw=row["integrated"]-expected
        variance=7*(5/45)*(1-5/45)*((45-7)/44)
        self.assertAlmostEqual(row["raw_integrated_deviation"],raw)
        self.assertAlmostEqual(row["standardized_integrated_deviation"],raw/sqrt(variance))
        self.assertNotEqual(row["raw_integrated_deviation"],row["standardized_integrated_deviation"])
        end=calculate_unit(DEFINITIONS["END_DIGIT"],draws(),81)
        self.assertEqual({r["group_size"] for r in end.round_metrics},{4,5})

    def test_03_actual_round_windows(self):
        result=calculate_unit(DEFINITIONS["UNIT_3"],draws(130),131)
        periods=next(iter(result.period_metrics.values()))
        self.assertEqual(periods["recent100"]["sample_count"],100)
        self.assertEqual(periods["recent50"]["sample_count"],50)
        self.assertEqual(periods["recent20"]["sample_count"],20)

    def test_04_wilson_known_and_labels(self):
        low,high=wilson95(5,10)
        self.assertAlmostEqual(low,0.236593,places=5);self.assertAlmostEqual(high,0.763407,places=5)
        cases=[(30,100,"POSITIVE_CONFIRMED"),(18,100,"POSITIVE_TENTATIVE"),(7,45,"NEUTRAL"),
               (10,100,"NEGATIVE_TENTATIVE"),(2,100,"NEGATIVE_CONFIRMED")]
        for h,n,label in cases:self.assertEqual(evidence_label(h,n,7/45,True)["evidence_label"],label)
        self.assertEqual(evidence_label(30,100,7/45,False)["evidence_label"],"INSUFFICIENT")

    def test_05_context_and_period_boundaries(self):
        self.assertEqual(_context_sample_state("EXACT_VECTOR_CONTEXT",20),"SUFFICIENT")
        self.assertEqual(_context_sample_state("EXACT_VECTOR_CONTEXT",19),"BORDERLINE")
        self.assertEqual(_context_sample_state("LOCAL_GROUP_CONTEXT",30),"SUFFICIENT")
        self.assertEqual(_context_sample_state("LOCAL_GROUP_CONTEXT",29),"BORDERLINE")
        self.assertEqual((_period_level("recent100",15),_period_level("recent100",14)),("OFFICIAL","BORDERLINE"))
        self.assertEqual((_period_level("recent50",8),_period_level("recent50",7)),("OFFICIAL","BORDERLINE"))
        self.assertEqual(_period_level("recent20",100),"TEST_ONLY")

    def test_06_five_control_states(self):
        positive=context(); tentative=context("POSITIVE_TENTATIVE")
        neutral=context("NEUTRAL"); negative=context("NEGATIVE_CONFIRMED")
        states={
            decide_unit_state(primary_name="EXACT_VECTOR_CONTEXT",primary=positive,secondary=None,relation="CONTEXT_ALIGNED",
                bonus_dependence="BONUS_DEPENDENCE_NONE",opposite_risk="LOW",structure_state="NORMAL")[0],
            decide_unit_state(primary_name="EXACT_VECTOR_CONTEXT",primary=tentative,secondary=None,relation="CONTEXT_ALIGNED",
                bonus_dependence="BONUS_DEPENDENCE_NONE",opposite_risk="LOW",structure_state="NORMAL")[0],
            decide_unit_state(primary_name="EXACT_VECTOR_CONTEXT",primary=neutral,secondary=None,relation="CONTEXT_INCONCLUSIVE",
                bonus_dependence="BONUS_DEPENDENCE_NONE",opposite_risk="LOW",structure_state="NORMAL")[0],
            decide_unit_state(primary_name="NO_EVALUABLE_CONTEXT",primary=None,secondary=None,relation="CONTEXT_INCONCLUSIVE",
                bonus_dependence="BONUS_DEPENDENCE_NONE",opposite_risk="LOW",structure_state="NORMAL")[0],
            decide_unit_state(primary_name="EXACT_VECTOR_CONTEXT",primary=negative,secondary=None,relation="CONTEXT_ALIGNED",
                bonus_dependence="BONUS_DEPENDENCE_NONE",opposite_risk="HIGH",structure_state="SEVERE")[0]}
        self.assertEqual(states,{"UNIT_PASS","UNIT_WEAKEN","UNIT_TEST","UNIT_HOLD","UNIT_FAIL"})

    def test_07_risk_caps(self):
        p=context()
        for bonus,risk,structure,expected in [
            ("BONUS_DEPENDENCE_HIGH","HIGH","NORMAL","UNIT_HOLD"),
            ("BONUS_DEPENDENCE_MEDIUM","MEDIUM","NORMAL","UNIT_WEAKEN"),
            ("BONUS_DEPENDENCE_NONE","LOW","WARNING","UNIT_WEAKEN")]:
            self.assertEqual(decide_unit_state(primary_name="EXACT_VECTOR_CONTEXT",primary=p,secondary=None,
                relation="CONTEXT_ALIGNED",bonus_dependence=bonus,opposite_risk=risk,structure_state=structure)[0],expected)

    def test_08_future_boundary_and_determinism(self):
        history=draws(80); a=evaluate_number_unit(DEFINITIONS["UNIT_9"],history,81,7)
        b=evaluate_number_unit(DEFINITIONS["UNIT_9"],history+[Draw(81,(1,2,3,4,5,6),7)],81,7)
        self.assertEqual(a["decision_hash"],b["decision_hash"])
        changed=history[:-1]+[Draw(80,(1,2,3,4,5,6),7)]
        self.assertNotEqual(a["decision_hash"],evaluate_number_unit(DEFINITIONS["UNIT_9"],changed,81,7)["decision_hash"])
        self.assertEqual(len({evaluate_number_unit(DEFINITIONS["UNIT_9"],history,81,7)["decision_hash"] for _ in range(10)}),1)

    def test_09_number_state_vector_connection(self):
        metrics={u:{n:{"unit_state":"UNIT_PASS" if n==1 else "UNIT_TEST","decision_hash":H64,
            "reason_codes":[],"opposite_risk":"LOW","structure_state":"NORMAL","primary_context":"EXACT_VECTOR_CONTEXT"}
            for n in range(1,46)} for u in DEFINITIONS}
        relations=build_number_relations(metrics)
        self.assertEqual(relations[1]["unit_state_vector"],["UNIT_PASS"]*5)
        self.assertEqual(relations[2]["unit_state_vector"],["UNIT_TEST"]*5)
        self.assertNotIn("score",str(relations).lower());self.assertNotIn("weight",str(relations).lower())

    def test_10_schema271_database_roundtrip(self):
        history=draws(80); analysis=calculate_unit(DEFINITIONS["UNIT_9"],history,81)
        decisions={n:evaluate_number_unit(DEFINITIONS["UNIT_9"],history,81,n) for n in range(1,46)}
        with tempfile.TemporaryDirectory() as t:
            paths=initialize(Path(t));store=CoreStore(paths)
            engine=store.register_engine_version(version_label="2.7.1-test",directive_sha256=H64,
                implementation_order_sha256=H64,rule_hash=H64,code_hash=H64,effective_round=1)
            run=store.create_core_run(engine_version_id=engine,analysis_round=81,record_class="BACKTEST",
                raw_data_hash=H64,normalized_data_hash=H64,rule_hash=H64,code_hash=H64)
            persist_unit_analysis(store,run,analysis);update_unit_decisions(store,run,"UNIT_9",decisions)
            loaded=load_unit_decisions(store,run)["UNIT_9"]
            self.assertEqual({n:loaded[n]["decision_hash"] for n in loaded},{n:decisions[n]["decision_hash"] for n in decisions})


if __name__=="__main__":unittest.main()

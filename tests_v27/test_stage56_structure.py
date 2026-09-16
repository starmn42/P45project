from __future__ import annotations

import sqlite3,tempfile,unittest
from pathlib import Path

from p45_v27.core_store import CoreStore
from p45_v27.initialize import initialize_storage
from p45_v27.prepare_schema271 import prepare,rollback_pointer
from p45_v27.structure_collapse import StructureCalculationError,_state,calculate_structure_ledger
from p45_v27.structure_store import load_structure_ledger,persist_structure_ledger
from p45_v27.units import DEFINITIONS,Draw,calculate_unit
from p45_v27.units.persistence import persist_unit_analysis

H64="d"*64
def draws(count):
    out=[]
    for r in range(1,count+1):
        start=(r*13)%45;v=[((start+i*7)%45)+1 for i in range(7)]
        out.append(Draw(r,tuple(sorted(v[:6])),v[6]))
    return out


class Stage56StructureTest(unittest.TestCase):
    def test_01_five_control_states(self):
        self.assertEqual([_state(x) for x in (89.99,90,95,99)],
                         ["NORMAL","CAUTION","WARNING","SEVERE"])
        self.assertEqual(calculate_structure_ledger(DEFINITIONS["UNIT_3"],draws(50),51)["structure_state"],
                         "INSUFFICIENT_SAMPLE")

    def test_02_sample_49_and_50_boundary(self):
        self.assertEqual(calculate_structure_ledger(DEFINITIONS["UNIT_5"],draws(50),51)["sample_count"],49)
        result=calculate_structure_ledger(DEFINITIONS["UNIT_5"],draws(51),52)
        self.assertEqual(result["sample_count"],50);self.assertIsNotNone(result["overall_percentile"])

    def test_03_missing_input_is_error(self):
        with self.assertRaises(StructureCalculationError):
            calculate_structure_ledger(DEFINITIONS["UNIT_9"],draws(49),51)

    def test_04_future_boundary_and_determinism(self):
        history=draws(80);base=calculate_structure_ledger(DEFINITIONS["UNIT_10"],history,81)
        future=calculate_structure_ledger(DEFINITIONS["UNIT_10"],history+[Draw(81,(1,2,3,4,5,6),7)],81)
        self.assertEqual(base["calculation_hash"],future["calculation_hash"])
        changed=history[:-1]+[Draw(80,(1,2,3,4,5,6),7)]
        self.assertNotEqual(base["calculation_hash"],calculate_structure_ledger(DEFINITIONS["UNIT_10"],changed,81)["calculation_hash"])
        self.assertEqual(len({calculate_structure_ledger(DEFINITIONS["UNIT_10"],history,81)["calculation_hash"] for _ in range(10)}),1)

    def test_05_all_units_and_raw_distributions(self):
        for definition in DEFINITIONS.values():
            result=calculate_structure_ledger(definition,draws(80),81)
            self.assertEqual(result["sample_count"],79)
            self.assertEqual(set(result["metric_names"]),set(result["historical_distribution"]))
            self.assertTrue(all(len(values)==79 for values in result["historical_distribution"].values()))

    def test_06_structure_database_roundtrip(self):
        history=draws(80);analysis=calculate_unit(DEFINITIONS["END_DIGIT"],history,81)
        ledger=calculate_structure_ledger(DEFINITIONS["END_DIGIT"],history,81)
        with tempfile.TemporaryDirectory() as t:
            paths=initialize_storage(Path(t));store=CoreStore(paths)
            e=store.register_engine_version(version_label="2.7.1-s56",directive_sha256=H64,
                implementation_order_sha256=H64,rule_hash=H64,code_hash=H64,effective_round=1)
            run=store.create_core_run(engine_version_id=e,analysis_round=81,record_class="BACKTEST",
                raw_data_hash=H64,normalized_data_hash=H64,rule_hash=H64,code_hash=H64)
            persist_unit_analysis(store,run,analysis);persist_structure_ledger(store,run,ledger)
            loaded=load_structure_ledger(store,run,"END_DIGIT")
            self.assertEqual(loaded["calculation_hash"],ledger["calculation_hash"])
            self.assertEqual(loaded["metric_percentiles_json"],ledger["metric_percentiles"])

    def test_07_pointer_activation_and_rollback(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/"db").mkdir()
            for name in ("p45_v27_core.sqlite3","p45_v27_audit.sqlite3"):
                c=sqlite3.connect(root/"db"/name);c.execute("pragma user_version=27");c.close()
            report=prepare(root)
            self.assertEqual(report["schema271"]["core"]["user_version"],273)
            self.assertEqual(report["schema271"]["core"]["total_rows"],0)
            rollback_pointer(root)
            self.assertIn('"schema_version": 27',(root/"active_schema.json").read_text())


if __name__=="__main__":unittest.main()

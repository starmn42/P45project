from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import unittest
from collections import OrderedDict
from pathlib import Path

from p45_v27.pairs.audit_v12 import (
    CONTEXT_FIELD_IDS, CONTEXT_VERSION, GATE_STATE_POLICY_HASH, RANKING_POLICY_HASH,
    SIGNATURE_VERSION, canonical_json, context_fingerprint, rule_signature,
    semantic_policy_hashes, verify_official_patch,
)
from p45_v27.pairs.production import ProductionPairPipeline
from p45_v27.pairs.walkforward import PairWalkforwardRunner, SCHEMA_VERSION

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "analysis/structure-1236/analysis-input.csv"
TRIO = ROOT / "v27_storage/backtests/p45_v273_trio_walkforward.sqlite3"

class PairV12OfficialTests(unittest.TestCase):
    def test_official_versions_patch_and_policy_hashes(self):
        verify_official_patch(ROOT)
        self.assertEqual("PAIR-RULE-SIGNATURE-1.2", SIGNATURE_VERSION)
        self.assertEqual("PAIR-CONTEXT-FINGERPRINT-1.0", CONTEXT_VERSION)
        self.assertEqual(2743, SCHEMA_VERSION)
        hashes=semantic_policy_hashes();self.assertEqual(9,len(hashes))
        self.assertEqual(RANKING_POLICY_HASH,hashes["ranking_policy_hash"])
        self.assertEqual(GATE_STATE_POLICY_HASH,hashes["gate_state_policy_hash"])

    def test_signature_determinism_dynamic_independence_and_policy_changes(self):
        base,raw,payload=rule_signature("EXPANDED_TEST_POOL")
        self.assertEqual(1,len({rule_signature("EXPANDED_TEST_POOL")[0] for _ in range(10)}))
        self.assertNotIn("round",raw);self.assertNotIn("number",raw);self.assertNotIn("outcome",raw)
        six=("eligibility_policy_hash","candidate_generation_policy_hash","ranking_policy_hash",
             "representative_selection_policy_hash","gate_state_policy_hash","bootstrap_policy_hash")
        for key in six:
            changed=semantic_policy_hashes();changed[key]=hashlib.sha256(key.encode()).hexdigest()
            self.assertNotEqual(base,rule_signature("EXPANDED_TEST_POOL",policy_hashes=changed)[0])
        self.assertEqual(base,hashlib.sha256(canonical_json(json.loads(raw)).encode()).hexdigest())

    def test_context_exact_21_rehash_and_rejections(self):
        fields=OrderedDict((key,{"fixed":key}) for key in CONTEXT_FIELD_IDS)
        digest,raw,payload=context_fingerprint(fields)
        self.assertEqual(21,len(payload["fields"]));self.assertEqual(digest,hashlib.sha256(canonical_json(json.loads(raw)).encode()).hexdigest())
        changed=OrderedDict(fields);changed["role_diversity"]={"fixed":"changed"}
        self.assertNotEqual(digest,context_fingerprint(changed)[0])
        missing=OrderedDict(fields);missing.popitem()
        with self.assertRaisesRegex(ValueError,"FIXED_FIELDS"):context_fingerprint(missing)
        extra=OrderedDict(fields);extra["extra"]={"x":1}
        with self.assertRaisesRegex(ValueError,"FIXED_FIELDS"):context_fingerprint(extra)
        empty=OrderedDict(fields);empty["role_diversity"]={}
        with self.assertRaisesRegex(ValueError,"EMPTY_OBJECT"):context_fingerprint(empty)
        future=OrderedDict(fields);future["role_diversity"]={"outcome":1}
        with self.assertRaisesRegex(ValueError,"FUTURE_OR_OUTCOME"):context_fingerprint(future)

    def test_production_context_timing_sequence_and_rehash(self):
        pipeline=ProductionPairPipeline(DATA,TRIO);prediction=pipeline.build_prediction_context(1236,1235,{})
        self.assertEqual([],pipeline.outcome_accesses);self.assertEqual(10,len(prediction.candidates))
        candidate=prediction.candidates[0];ctx=candidate.context
        self.assertEqual(SIGNATURE_VERSION,ctx["signature_version"]);self.assertEqual(CONTEXT_VERSION,ctx["context_fingerprint_version"])
        self.assertEqual(candidate.base_pair_rule_signature,hashlib.sha256(canonical_json(json.loads(ctx["canonical_rule_payload_json"])).encode()).hexdigest())
        self.assertEqual(ctx["pair_context_fingerprint"],hashlib.sha256(canonical_json(json.loads(ctx["canonical_context_payload_json"])).encode()).hexdigest())
        gates=ctx["gate_records"];self.assertEqual([f"PG{i:02d}" for i in range(1,15)],[x["gate_id"] for x in gates])
        self.assertEqual("PG13_PENDING_FINAL",gates[12]["pg13_lifecycle"]["pending_final_marker"])
        self.assertEqual(0,ctx["finalization"]["outcome_access_count_before_finalization"])

    def test_temporary_runner_storage_integrity_and_audit(self):
        class OutcomePipeline(ProductionPairPipeline):
            def load_round_outcome(self, round_):
                self.outcome_accesses.append(round_);return {"main":(1,2,3,4,5,6),"bonus":7}
        with tempfile.TemporaryDirectory() as td:
            db_path=Path(td)/"v12.sqlite3";p=OutcomePipeline(DATA,TRIO)
            runner=PairWalkforwardRunner(db_path,run_id="V12-SMOKE",start_round=1236,end_round=1236,
                rule_hash="a"*64,code_hash="b"*64,schema_hash="c"*64,pipeline=p)
            self.assertTrue(runner.run(max_rounds=1)["complete"]);self.assertEqual([1236],p.outcome_accesses)
            db=sqlite3.connect(db_path)
            self.assertEqual("ok",db.execute("pragma integrity_check").fetchone()[0]);self.assertEqual([],db.execute("pragma foreign_key_check").fetchall())
            row=db.execute("select canonical_rule_payload_json,base_pair_rule_signature,canonical_context_payload_json,pair_context_fingerprint from wf_pair_candidate limit 1").fetchone()
            self.assertEqual(row[1],hashlib.sha256(canonical_json(json.loads(row[0])).encode()).hexdigest())
            self.assertEqual(row[3],hashlib.sha256(canonical_json(json.loads(row[2])).encode()).hexdigest())
            self.assertGreater(db.execute("select count(*) from wf_prediction_audit").fetchone()[0],0);db.close()

if __name__ == "__main__": unittest.main()

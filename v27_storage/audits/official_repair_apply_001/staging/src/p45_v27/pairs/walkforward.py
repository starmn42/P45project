"""Resumable, fail-fast PAIR walk-forward transaction runner (no automatic full run)."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

from .engine import SIGNATURE_VERSION, canonical_json
from .audit_v12 import CONTEXT_VERSION

SCHEMA_VERSION = 2743
ROUND_STATES = ("RUNNING", "COMPLETE", "SKIPPED_TRIO_UNDER_2", "SKIPPED_NO_DISJOINT_PAIR", "SKIPPED_RESEARCH_HOLD")

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS wf_run(run_id TEXT PRIMARY KEY, cache_key TEXT NOT NULL UNIQUE, run_status TEXT NOT NULL,
 rule_hash TEXT NOT NULL, code_hash TEXT NOT NULL, schema_hash TEXT NOT NULL, signature_version TEXT NOT NULL,
 source_hash TEXT NOT NULL, start_round INTEGER NOT NULL, end_round INTEGER NOT NULL, last_error TEXT);
CREATE TABLE IF NOT EXISTS wf_round(run_id TEXT NOT NULL REFERENCES wf_run(run_id), evaluation_round INTEGER NOT NULL,
 round_status TEXT NOT NULL, source_end_round INTEGER NOT NULL, data_prefix_hash TEXT NOT NULL,
 prediction_context_json TEXT, prediction_hash_before_result TEXT, candidate_count INTEGER NOT NULL DEFAULT 0,
 identity_count INTEGER NOT NULL DEFAULT 0, selection_count INTEGER NOT NULL DEFAULT 0, decision_hash TEXT,
 PRIMARY KEY(run_id,evaluation_round));
CREATE TABLE IF NOT EXISTS wf_pair_candidate(run_id TEXT NOT NULL,evaluation_round INTEGER NOT NULL,canonical_pair_key TEXT NOT NULL,
 base_pair_rule_signature TEXT NOT NULL,rule_signature_version TEXT NOT NULL,canonical_rule_payload_json TEXT NOT NULL,
 pair_context_fingerprint TEXT NOT NULL,context_fingerprint_version TEXT NOT NULL,canonical_context_payload_json TEXT NOT NULL,
 rank_key_json TEXT NOT NULL,context_json TEXT NOT NULL,
 gate_input_json TEXT NOT NULL,gate_results_json TEXT NOT NULL,
 pair_state TEXT NOT NULL CHECK(pair_state IN('PAIR_READY','PAIR_TEST_READY','PAIR_RESEARCH_HOLD','PAIR_SYSTEM_HOLD')),
 PRIMARY KEY(run_id,evaluation_round,canonical_pair_key),
 FOREIGN KEY(run_id,evaluation_round) REFERENCES wf_round(run_id,evaluation_round));
CREATE TABLE IF NOT EXISTS wf_prediction_audit(run_id TEXT NOT NULL,evaluation_round INTEGER NOT NULL,canonical_pair_key TEXT NOT NULL,
 prelock_json TEXT NOT NULL,prelock_hash TEXT NOT NULL,final_prediction_json TEXT NOT NULL,final_prediction_hash TEXT NOT NULL,
 pg13_lifecycle_json TEXT NOT NULL,finalization_json TEXT NOT NULL,finalization_hash TEXT NOT NULL,final_pre_result_state TEXT NOT NULL,
 PRIMARY KEY(run_id,evaluation_round,canonical_pair_key),
 FOREIGN KEY(run_id,evaluation_round,canonical_pair_key) REFERENCES wf_pair_candidate(run_id,evaluation_round,canonical_pair_key));
CREATE TABLE IF NOT EXISTS wf_identity_exposure(run_id TEXT NOT NULL,evaluation_round INTEGER NOT NULL,canonical_pair_key TEXT NOT NULL,
 PRIMARY KEY(run_id,evaluation_round,canonical_pair_key),
 FOREIGN KEY(run_id,evaluation_round,canonical_pair_key) REFERENCES wf_pair_candidate(run_id,evaluation_round,canonical_pair_key));
CREATE TABLE IF NOT EXISTS wf_selection_exposure(selection_id TEXT PRIMARY KEY,run_id TEXT NOT NULL,evaluation_round INTEGER NOT NULL,
 base_pair_rule_signature TEXT NOT NULL,representative_pair_key TEXT NOT NULL,prediction_hash_before_result TEXT NOT NULL,
 UNIQUE(run_id,evaluation_round,base_pair_rule_signature),
 FOREIGN KEY(run_id,evaluation_round,representative_pair_key) REFERENCES wf_pair_candidate(run_id,evaluation_round,canonical_pair_key));
CREATE TABLE IF NOT EXISTS wf_outcome(selection_id TEXT PRIMARY KEY REFERENCES wf_selection_exposure(selection_id),
 a_integrated_hits INTEGER NOT NULL CHECK(a_integrated_hits BETWEEN 0 AND 3),b_integrated_hits INTEGER NOT NULL CHECK(b_integrated_hits BETWEEN 0 AND 3),
 a_main_hits INTEGER NOT NULL CHECK(a_main_hits BETWEEN 0 AND 3),b_main_hits INTEGER NOT NULL CHECK(b_main_hits BETWEEN 0 AND 3),
 a_bonus_assisted_triple INTEGER NOT NULL CHECK(a_bonus_assisted_triple IN(0,1)),b_bonus_assisted_triple INTEGER NOT NULL CHECK(b_bonus_assisted_triple IN(0,1)),
 integrated_category TEXT NOT NULL,main_category TEXT NOT NULL,outcome_hash TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_wf_resume ON wf_round(run_id,round_status,evaluation_round);
CREATE INDEX IF NOT EXISTS idx_wf_history ON wf_selection_exposure(run_id,base_pair_rule_signature,evaluation_round);
"""


def _sha(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PairPrediction:
    canonical_pair_key: str
    base_pair_rule_signature: str
    member_a: tuple[int, int, int]
    member_b: tuple[int, int, int]
    rank_key: tuple[Any, ...]
    context: Mapping[str, Any]


@dataclass(frozen=True)
class RoundPrediction:
    source_end_round: int
    data_prefix_hash: str
    candidates: tuple[PairPrediction, ...]
    skip_status: str | None = None


class WalkforwardPipeline(Protocol):
    def source_hash(self) -> str: ...
    def compute_pre_result(self, evaluation_round: int, source_end_round: int,
                           history: Mapping[str, Sequence[Mapping[str, Any]]]) -> RoundPrediction: ...
    def read_result(self, evaluation_round: int) -> Mapping[str, Any]: ...


def _category(x: int, y: int) -> str:
    if x == y == 3: return "DOUBLE_TRIPLE_SUCCESS"
    if (x == 3) ^ (y == 3): return "SINGLE_TRIPLE_SUCCESS"
    if x != 3 and y != 3 and x == y == 2: return "NO_TRIPLE_WITH_DOUBLE_EXACT2"
    if x != 3 and y != 3 and ((x == 2) ^ (y == 2)): return "NO_TRIPLE_WITH_SINGLE_EXACT2"
    return "NO_TRIPLE_NO_EXACT2"


class PairWalkforwardRunner:
    def __init__(self, db_path: Path, *, run_id: str, start_round: int, end_round: int,
                 rule_hash: str, code_hash: str, schema_hash: str, pipeline: WalkforwardPipeline) -> None:
        self.db_path=Path(db_path); self.run_id=run_id; self.start_round=start_round; self.end_round=end_round
        self.rule_hash=rule_hash; self.code_hash=code_hash; self.schema_hash=schema_hash; self.pipeline=pipeline
        self.source_hash=pipeline.source_hash()
        self.cache_key=_sha({"run_id":run_id,"range":[start_round,end_round],"rule":rule_hash,"code":code_hash,
                             "schema":schema_hash,"signature":SIGNATURE_VERSION,"source":self.source_hash})

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True,exist_ok=True); db=sqlite3.connect(self.db_path);db.row_factory=sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON");db.execute("PRAGMA journal_mode=WAL");db.execute("PRAGMA synchronous=FULL");db.executescript(SCHEMA);db.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
        return db

    def _prepare_run(self, db: sqlite3.Connection) -> None:
        row=db.execute("SELECT * FROM wf_run WHERE run_id=?",(self.run_id,)).fetchone()
        expected=(self.cache_key,self.rule_hash,self.code_hash,self.schema_hash,SIGNATURE_VERSION,self.source_hash,self.start_round,self.end_round)
        if row:
            actual=tuple(row[k] for k in ("cache_key","rule_hash","code_hash","schema_hash","signature_version","source_hash","start_round","end_round"))
            if actual != expected: raise RuntimeError("PAIR_WALKFORWARD_CACHE_HASH_MISMATCH")
        else:
            db.execute("INSERT INTO wf_run VALUES (?,?,?,?,?,?,?,?,?,?,NULL)",(self.run_id,self.cache_key,"WALKFORWARD_INCOMPLETE",self.rule_hash,self.code_hash,self.schema_hash,SIGNATURE_VERSION,self.source_hash,self.start_round,self.end_round));db.commit()

    def _history(self, db: sqlite3.Connection, round_: int) -> dict[str,list[dict[str,Any]]]:
        rows=db.execute("SELECT s.*,o.* FROM wf_selection_exposure s JOIN wf_outcome o USING(selection_id) JOIN wf_round r USING(run_id,evaluation_round) WHERE s.run_id=? AND s.evaluation_round<? AND r.round_status='COMPLETE' ORDER BY s.evaluation_round,s.selection_id",(self.run_id,round_)).fetchall()
        out:dict[str,list[dict[str,Any]]]={}
        for row in rows: out.setdefault(row["base_pair_rule_signature"],[]).append(dict(row))
        return out

    def run(self, *, max_rounds: int | None=None) -> dict[str,Any]:
        db=self._connect()
        try:
            self._prepare_run(db)
            complete={r[0] for r in db.execute("SELECT evaluation_round FROM wf_round WHERE run_id=? AND round_status!='RUNNING'",(self.run_id,))}
            processed=0
            for r in range(self.start_round,self.end_round+1):
                if r in complete: continue
                if max_rounds is not None and processed>=max_rounds: break
                if self.pipeline.source_hash()!=self.source_hash: raise RuntimeError("PAIR_SOURCE_CHANGED")
                try:
                    db.execute("BEGIN IMMEDIATE")
                    db.execute("INSERT INTO wf_round VALUES (?,?, 'RUNNING',?,?,?,?,0,0,0,NULL)",(self.run_id,r,r-1,"",None,None))
                    history=self._history(db,r)
                    prediction=self.pipeline.compute_pre_result(r,r-1,history)
                    if prediction.source_end_round!=r-1: raise RuntimeError("PAIR_FUTURE_LEAKAGE")
                    if prediction.skip_status:
                        if prediction.skip_status not in ROUND_STATES[2:]: raise RuntimeError("PAIR_SKIP_STATUS_INVALID")
                        decision=_sha({"round":r,"status":prediction.skip_status,"prefix":prediction.data_prefix_hash})
                        db.execute("UPDATE wf_round SET round_status=?,data_prefix_hash=?,decision_hash=? WHERE run_id=? AND evaluation_round=?",(prediction.skip_status,prediction.data_prefix_hash,decision,self.run_id,r));db.commit();processed+=1;continue
                    candidates=sorted(prediction.candidates,key=lambda x:x.canonical_pair_key)
                    for c in candidates:
                        if len(c.base_pair_rule_signature)!=64: raise RuntimeError("PAIR_SIGNATURE_INVALID")
                        gate_input=c.context.get("gate_input");gate_results=c.context.get("gate_results");pair_state=c.context.get("pair_state")
                        if not isinstance(gate_input,Mapping) or not isinstance(gate_results,Mapping) or tuple(gate_results)!=tuple(f"PG{i:02d}" for i in range(1,15)) or any(v not in ("PASS","FAIL","INCOMPLETE") for v in gate_results.values()) or pair_state not in ("PAIR_READY","PAIR_TEST_READY","PAIR_RESEARCH_HOLD","PAIR_SYSTEM_HOLD"):
                            raise RuntimeError("PAIR_GATE_STATE_CONTEXT_MISSING")
                        rule_json=c.context.get("canonical_rule_payload_json");context_json=c.context.get("canonical_context_payload_json")
                        fingerprint=c.context.get("pair_context_fingerprint");prelock=c.context.get("prelock");final_prediction=c.context.get("final_prediction");finalization=c.context.get("finalization")
                        records=c.context.get("gate_records")
                        if c.context.get("signature_version")!=SIGNATURE_VERSION or c.context.get("context_fingerprint_version")!=CONTEXT_VERSION:
                            raise RuntimeError("PAIR_RULE_CONTEXT_VERSION_MISMATCH")
                        if not all(isinstance(x,str) for x in (rule_json,context_json,fingerprint)) or _sha(json.loads(rule_json))!=c.base_pair_rule_signature or _sha(json.loads(context_json))!=fingerprint:
                            raise RuntimeError("PAIR_AUDIT_JSON_REHASH_MISMATCH")
                        if not all(isinstance(x,Mapping) for x in (prelock,final_prediction,finalization)) or not isinstance(records,Sequence):
                            raise RuntimeError("PAIR_PREDICTION_AUDIT_MISSING")
                        pg13=next((x.get("pg13_lifecycle") for x in records if x.get("gate_id")=="PG13"),None)
                        if not isinstance(pg13,Mapping): raise RuntimeError("PAIR_PG13_LIFECYCLE_MISSING")
                        db.execute("INSERT INTO wf_pair_candidate VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(self.run_id,r,c.canonical_pair_key,c.base_pair_rule_signature,SIGNATURE_VERSION,rule_json,fingerprint,CONTEXT_VERSION,context_json,canonical_json(c.rank_key),canonical_json(c.context),canonical_json(gate_input),canonical_json(gate_results),pair_state))
                        db.execute("INSERT INTO wf_prediction_audit VALUES (?,?,?,?,?,?,?,?,?,?,?)",(self.run_id,r,c.canonical_pair_key,canonical_json(prelock),prelock["hash"],canonical_json(final_prediction),final_prediction["hash"],canonical_json(pg13),canonical_json(finalization),finalization["hash"],pair_state))
                        db.execute("INSERT INTO wf_identity_exposure VALUES (?,?,?)",(self.run_id,r,c.canonical_pair_key))
                    reps={}
                    for c in candidates:
                        current=reps.get(c.base_pair_rule_signature)
                        if current is None or (c.rank_key,c.canonical_pair_key)<(current.rank_key,current.canonical_pair_key): reps[c.base_pair_rule_signature]=c
                    context={"run_id":self.run_id,"round":r,"source_end_round":r-1,"data_prefix_hash":prediction.data_prefix_hash,
                             "signature_version":SIGNATURE_VERSION,"representatives":[{"signature":s,"pair":reps[s].canonical_pair_key} for s in sorted(reps)]}
                    prediction_hash=_sha(context)
                    db.execute("UPDATE wf_round SET data_prefix_hash=?,prediction_context_json=?,prediction_hash_before_result=?,candidate_count=?,identity_count=?,selection_count=? WHERE run_id=? AND evaluation_round=?",(prediction.data_prefix_hash,canonical_json(context),prediction_hash,len(candidates),len(candidates),len(reps),self.run_id,r))
                    for sig,c in sorted(reps.items()):
                        sid=_sha({"run":self.run_id,"round":r,"signature":sig})
                        db.execute("INSERT INTO wf_selection_exposure VALUES (?,?,?,?,?,?)",(sid,self.run_id,r,sig,c.canonical_pair_key,prediction_hash))
                    persisted=db.execute("SELECT prediction_hash_before_result FROM wf_round WHERE run_id=? AND evaluation_round=?",(self.run_id,r)).fetchone()[0]
                    if persisted!=prediction_hash: raise RuntimeError("PAIR_PREDICTION_NOT_PERSISTED")
                    hook=getattr(self.pipeline,"prediction_persisted",None)
                    if hook is not None: hook(r,prediction_hash)
                    result=self.pipeline.read_result(r)
                    main=set(result["main"]); integrated=main|{result["bonus"]}
                    for sig,c in sorted(reps.items()):
                        ah=len(set(c.member_a)&integrated);bh=len(set(c.member_b)&integrated);am=len(set(c.member_a)&main);bm=len(set(c.member_b)&main)
                        sid=_sha({"run":self.run_id,"round":r,"signature":sig}); vals=(ah,bh,am,bm,int(ah==3 and am<3),int(bh==3 and bm<3),_category(ah,bh),_category(am,bm))
                        db.execute("INSERT INTO wf_outcome VALUES (?,?,?,?,?,?,?,?,?,?)",(sid,*vals,_sha({"prediction":prediction_hash,"values":vals})))
                    decision=_sha({"prediction":prediction_hash,"round":r,"selection_count":len(reps)})
                    db.execute("UPDATE wf_round SET round_status='COMPLETE',decision_hash=? WHERE run_id=? AND evaluation_round=?",(decision,self.run_id,r));db.commit();processed+=1
                except Exception:
                    db.rollback();raise
            terminal=db.execute("SELECT count(*) FROM wf_round WHERE run_id=? AND round_status!='RUNNING'",(self.run_id,)).fetchone()[0]
            total=self.end_round-self.start_round+1
            if terminal==total: db.execute("UPDATE wf_run SET run_status='WALKFORWARD_COMPLETE' WHERE run_id=?",(self.run_id,));db.commit()
            return {"run_id":self.run_id,"processed":processed,"terminal":terminal,"total":total,"complete":terminal==total,
                    "next_round":next((r for r in range(self.start_round,self.end_round+1) if r not in complete and not db.execute("SELECT 1 FROM wf_round WHERE run_id=? AND evaluation_round=? AND round_status!='RUNNING'",(self.run_id,r)).fetchone()),None)}
        finally: db.close()

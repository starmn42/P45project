"""P45 state system v1.0: deterministic, transactional handoff storage."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Mapping

STATE_SYSTEM_VERSION = "1.2.1"
ALLOWED_EVENT_TYPES = {"CONVERSATION_ONLY", "IDEA_PENDING", "AMBIGUOUS_IMPORTANT", "DECISION_CONFIRMED"}
_HANDOFF_MODULE = None
TEXT_NAMES = (
    "P45_START_HERE.md", "P45_HANDOFF.md", "P45_CURRENT_STATE.md",
    "P45_DECISION_LOG.md", "P45_IDEA_INBOX.md", "P45_CAPTURE_POLICY.md", "P45_NEW_CHAT_START.md",
    "P45_FINAL_OPERATION_STATE.md",
)
MANAGED_NAMES = ("P45_CURRENT_STATE.md", "P45_CURRENT_STATE.json", "P45_HANDOFF.md", "P45_DECISION_LOG.md")
REQUIRED = (
    "state_version", "project_version", "schema_version", "current_stage",
    "current_status", "last_completed_stage", "next_stage", "next_action",
    "official_documents", "walkforward", "number_state", "trio_state",
    "pair_state", "core_state", "audit_state", "blockers",
    "forbidden_actions", "important_hashes", "last_decision_id", "state_hash",
)


class StateError(RuntimeError):
    pass


class StateLocked(StateError):
    pass


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def parse_aware_timestamp(value: str) -> dt.datetime:
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise StateError(f"STATE_CHRONOLOGY_CONFLICT:INVALID_TIMESTAMP:{value}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise StateError(f"STATE_CHRONOLOGY_CONFLICT:NAIVE_TIMESTAMP:{value}")
    return parsed


def ordered_timestamp(not_before: str | None = None) -> str:
    current = parse_aware_timestamp(now_iso())
    if not_before is not None:
        floor = parse_aware_timestamp(not_before)
        if current < floor:
            current = floor
    return current.isoformat(timespec="seconds")


def decision_timestamp(log_text: str, decision_id: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(decision_id)}\s*$.*?^- timestamp:\s*(.+?)\s*$", log_text)
    if not match:
        raise StateError(f"STATE_CHRONOLOGY_CONFLICT:DECISION_NOT_FOUND:{decision_id}")
    return match.group(1).strip()


def chronology_errors(decision_time: str, state_time: str, bundle_time: str | None = None,
                      snapshot_time: str | None = None) -> list[str]:
    try:
        decision_dt = parse_aware_timestamp(decision_time)
        state_dt = parse_aware_timestamp(state_time)
        bundle_dt = parse_aware_timestamp(bundle_time) if bundle_time else None
        snapshot_dt = parse_aware_timestamp(snapshot_time) if snapshot_time else None
    except StateError as exc:
        return [str(exc)]
    errors = []
    if decision_dt > state_dt: errors.append("STATE_CHRONOLOGY_CONFLICT:DECISION_AFTER_STATE")
    if bundle_dt is not None and state_dt > bundle_dt: errors.append("STATE_CHRONOLOGY_CONFLICT:STATE_AFTER_BUNDLE")
    if snapshot_dt is not None and state_dt > snapshot_dt: errors.append("STATE_CHRONOLOGY_CONFLICT:STATE_AFTER_SNAPSHOT")
    return errors


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def calculate_file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _logical_state(state: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(state))
    for field in ("state_hash", "updated_at", "updated_by"):
        result.pop(field, None)
    return result


def calculate_state_hash(state: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(_logical_state(state)).encode("utf-8")).hexdigest()


def calculate_decision_hash(decision: Mapping[str, Any]) -> str:
    core = {k: v for k, v in decision.items() if k not in ("timestamp", "decision_id", "decision_hash")}
    return hashlib.sha256(canonical_json(core).encode("utf-8")).hexdigest()


def calculate_idea_hash(idea: Mapping[str, Any]) -> str:
    core = {k: v for k, v in idea.items() if k not in ("timestamp", "idea_id", "idea_hash")}
    return hashlib.sha256(canonical_json(core).encode("utf-8")).hexdigest()


def calculate_event_hash(event: Mapping[str, Any]) -> str:
    core = {k: v for k, v in event.items() if k not in ("timestamp", "event_id", "event_hash")}
    return hashlib.sha256(canonical_json(core).encode("utf-8")).hexdigest()


def _encode_text(text: str) -> bytes:
    clean = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
    return b"\xef\xbb\xbf" + clean.encode("utf-8")


def _decode_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8-sig")


def _validate_text_bytes(data: bytes, name: str) -> list[str]:
    errors: list[str] = []
    if not data.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{name}: UTF8_BOM_MISSING")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return [f"{name}: UTF8_INVALID:{exc}"]
    if "\ufffd" in text:
        errors.append(f"{name}: U_FFFD_PRESENT")
    if "\n" in text.replace("\r\n", ""):
        errors.append(f"{name}: BARE_LF_PRESENT")
    if "\r" in text.replace("\r\n", ""):
        errors.append(f"{name}: BARE_CR_PRESENT")
    return errors


def _deep_merge(base: dict[str, Any], updates: Mapping[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base)
    for key, value in updates.items():
        if isinstance(value, Mapping) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def _bump_version(value: str) -> str:
    parts = value.split(".")
    if parts and parts[-1].isdigit():
        parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)
    return value + ".1"


class StateManager:
    def __init__(self, state_root: str | Path | None = None, project_root: str | Path | None = None):
        self.root = Path(state_root or Path(__file__).resolve().parents[1]).resolve()
        self.project = Path(project_root or self.root.parent).resolve()
        self.history = self.root / "state-history"
        self.transactions = self.root / ".transactions"
        self.lock_path = self.root / ".state-manager.lock"
        self.root.mkdir(parents=True, exist_ok=True)
        self.history.mkdir(exist_ok=True)
        self.transactions.mkdir(exist_ok=True)

    def path(self, name: str) -> Path:
        return self.root / name

    def refresh_portable_bundle(self, simulate_failure: bool = False) -> dict[str, Any]:
        global _HANDOFF_MODULE
        module_path = Path(__file__).with_name("p45_handoff.py")
        if _HANDOFF_MODULE is None:
            spec = importlib.util.spec_from_file_location("p45_handoff_runtime", module_path)
            _HANDOFF_MODULE = importlib.util.module_from_spec(spec); spec.loader.exec_module(_HANDOFF_MODULE)
        return _HANDOFF_MODULE.create_bundle(self.root, simulate_failure=simulate_failure)

    def load_current_state(self) -> dict[str, Any]:
        try:
            return json.loads(self.path("P45_CURRENT_STATE.json").read_bytes().decode("utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise StateError(f"CURRENT_STATE_JSON_INVALID:{exc}") from exc

    def validate_current_state(self, state: Mapping[str, Any] | None = None, check_files: bool = True) -> dict[str, Any]:
        state = dict(state or self.load_current_state())
        errors = [f"REQUIRED_FIELD_MISSING:{key}" for key in REQUIRED if key not in state]
        if not errors and state["state_hash"] != calculate_state_hash(state):
            errors.append("STATE_HASH_MISMATCH")
        if check_files:
            for name in TEXT_NAMES + ("P45_CURRENT_STATE.json",):
                path = self.path(name)
                if not path.exists():
                    errors.append(f"FILE_MISSING:{name}")
                else:
                    errors.extend(_validate_text_bytes(path.read_bytes(), name))
            if not errors:
                md = _decode_text(self.path("P45_CURRENT_STATE.md"))
                for value in (state["current_stage"], state["current_status"], str(state["trio_state"]["total"]), str(state["trio_state"]["valid_for_pair_true"])):
                    if value not in md:
                        errors.append(f"MD_JSON_MISMATCH:{value}")
        return {"valid": not errors, "errors": errors, "state_hash": calculate_state_hash(state)}

    def render_current_state_md(self, state: Mapping[str, Any]) -> str:
        wf, num, trio, pair = state["walkforward"], state["number_state"], state["trio_state"], state["pair_state"]
        docs = "\n".join(f"- {d['name']}: `{d['path']}` — `{d['sha256']}`" for d in state["official_documents"])
        valid = ", ".join(trio["valid_trios"])
        forbidden = "\n".join(f"- {x}" for x in state["forbidden_actions"])
        return f"""# P45 CURRENT STATE

## STATE META
- state_system_version: {state.get('state_system_version', STATE_SYSTEM_VERSION)}
- state_version: {state['state_version']}
- updated_at: {state.get('updated_at', '')}
- updated_by: {state.get('updated_by', '')}
- project_version: {state['project_version']}
- schema_version: {state['schema_version']}
- canonical_manifest_sha256: `{state['important_hashes']['canonical_manifest']}`
- state_hash: `{state['state_hash']}`

## OFFICIAL DOCUMENTS
{docs}

## CURRENT PHASE
- current_stage: {state['current_stage']}
- current_status: {state['current_status']}
- last_completed_stage: {state['last_completed_stage']}
- next_stage: {state['next_stage']}
- next_action: {state['next_action']}
- pair_implementation_approved: {str(state.get('pair_implementation_approved', False)).lower()}

## WALKFORWARD
- run_id: `{wf['run_id']}`
- evaluation_range: {wf['evaluation_range']}
- total_rounds: {wf['total_rounds']}
- COMPLETE: {wf['complete']}
- SKIPPED_RESEARCH_HOLD: {wf['skipped_research_hold']}
- FAILED: {wf['failed']}
- selection_exposure: {wf['selection_exposure']}
- status: {wf['status']}
- source_db: `{wf['source_db']}`
- source_db_sha256: `{wf['sha256']}`

## CURRENT NUMBER STATE
- analysis_round: {num['analysis_round']}
- candidates: {', '.join(map(str, num['candidates']))}
- candidate_pool_type: {num['candidate_pool_type']}
- NUMBER_PASS: {num['number_pass']}
- operational_number_ledger_rows: {num['operational_ledger_rows']}

## CURRENT TRIO STATE
- total: {trio['total']}
- TRIO_PASS: {trio['pass']}
- TRIO_WEAKEN: {trio['weaken']}
- TRIO_TEST: {trio['test']}
- TRIO_HOLD: {trio['hold']}
- TRIO_FAIL: {trio['fail']}
- valid_for_pair_true: {trio['valid_for_pair_true']}
- valid_trios: {valid}
- result_db: `{trio['result_db']}`
- result_db_sha256: `{trio['sha256']}`

이 목록은 최종 추천번호가 아니라 PAIR 연구에 전달 가능한 TRIO 목록이다.

## PAIR STATE
- PAIR rows: {pair['rows']}
- PAIR 생성: {pair['status']}
- PAIR 승인: {'APPROVED' if pair['approved'] else 'NOT_APPROVED'}

## CORE / AUDIT
- operational_core_official_rows: {state['core_state']['official_rows']}
- operational_audit_official_rows: {state['audit_state']['official_rows']}
- official_final_lock: {state['core_state']['final_lock']}

## CURRENT BLOCKER
{chr(10).join('- ' + x for x in state['blockers'])}

## NEXT APPROVED ACTION
{state['next_action']}

## FORBIDDEN UNTIL NEXT APPROVAL
{forbidden}

## IMPORTANT HASHES
{chr(10).join(f'- {k}: `{v}`' for k, v in state['important_hashes'].items())}

## LAST DECISION
- last_decision_id: {state['last_decision_id']}
"""

    def rebuild_current_state(self, state: Mapping[str, Any]) -> str:
        return self.render_current_state_md(state)

    def write_current_state_json(self, state: Mapping[str, Any]) -> bytes:
        return _encode_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")

    def rebuild_handoff(self, state: Mapping[str, Any]) -> str:
        trio, pair, wf = state["trio_state"], state["pair_state"], state["walkforward"]
        forbidden = ", ".join(state["forbidden_actions"][:5])
        crowd_topology = state.get("research_state", {}).get("crowd_topology", {})
        crowd_topology_line = (
            f"- CROWD_TOPOLOGY: {crowd_topology['status']}\n"
            if crowd_topology.get("status") else ""
        )
        return f"""# P45 HANDOFF

- 프로젝트 버전: {state['project_version']}
- 현재 단계: {state['current_stage']}
- 마지막 완료: {state['last_completed_stage']}
- 현재 상태: {state['current_status']}
- WALKFORWARD: {wf['status']}
- TRIO: PASS {trio['pass']} / WEAKEN {trio['weaken']} / TEST {trio['test']} / HOLD {trio['hold']} / FAIL {trio['fail']}
- valid_for_pair: {trio['valid_for_pair_true']}
- PAIR: {pair['status']} / {'APPROVED' if pair['approved'] else 'NOT_APPROVED'}
{crowd_topology_line}- 다음 허용 작업: {state['next_action']}
- 현재 금지 핵심: {forbidden}
- CURRENT_STATE: `P45_CURRENT_STATE.md`
- DECISION_LOG: `P45_DECISION_LOG.md`
- IDEA_INBOX: `P45_IDEA_INBOX.md`
- 마지막 decision_id: {state['last_decision_id']}
- state_hash: `{state['state_hash']}`

새 세션은 `P45_START_HERE.md`부터 읽고 검증 전에는 구현을 시작하지 않는다.
"""

    def detect_duplicate_decision(self, decision: Mapping[str, Any], log_text: str | None = None) -> bool:
        digest = calculate_decision_hash(decision)
        return digest in (log_text if log_text is not None else _decode_text(self.path("P45_DECISION_LOG.md")))

    def _decision_block(self, decision: Mapping[str, Any]) -> str:
        d = dict(decision)
        d["decision_hash"] = calculate_decision_hash(d)
        ordered = ("timestamp", "project_version", "stage", "category", "decision", "reason", "evidence", "affected_files", "affected_schema", "previous_rule", "new_rule", "allowed_next_action", "forbidden_actions", "approval_source", "decision_hash")
        return "\n## " + d["decision_id"] + "\n" + "\n".join(f"- {k}: {d.get(k, '')}" for k in ordered) + "\n"

    def validate_event(self, event: Mapping[str, Any]) -> dict[str, Any]:
        errors: list[str] = []; kind = event.get("event_type")
        if kind not in ALLOWED_EVENT_TYPES:
            errors.append(f"UNKNOWN_EVENT_TYPE:{kind}")
        if kind in ("IDEA_PENDING", "AMBIGUOUS_IMPORTANT"):
            for key in ("source", "title", "summary", "reason", "related_stage", "related_rule"):
                if not event.get(key): errors.append(f"EVENT_FIELD_REQUIRED:{key}")
            if event.get("official_effect", "NONE") != "NONE": errors.append("IDEA_OFFICIAL_EFFECT_FORBIDDEN")
            if event.get("promote_to_official") or event.get("affected_state") or event.get("official_document_change"):
                errors.append("IDEA_AUTO_PROMOTION_FORBIDDEN")
        if kind == "DECISION_CONFIRMED":
            for key in ("source", "decision", "reason"):
                if not event.get(key): errors.append(f"EVENT_FIELD_REQUIRED:{key}")
            if event.get("approval_explicit") is not True: errors.append("EXPLICIT_APPROVAL_REQUIRED")
            if event.get("research_rule_change") and (event.get("affected_state") or not event.get("formal_amendment_required", True)):
                errors.append("RESEARCH_RULE_FIREWALL")
        return {"valid": not errors, "errors": errors, "event_hash": calculate_event_hash(event)}

    def _idea_from_event(self, event: Mapping[str, Any]) -> dict[str, Any]:
        date = dt.datetime.now().strftime("%Y%m%d")
        return {"idea_id": event.get("idea_id", f"IDEA-{date}-{uuid.uuid4().hex[:8].upper()}"),
         "timestamp": event.get("timestamp", now_iso()), "source": event["source"], "title": event["title"],
         "idea": event["summary"], "reason": event["reason"], "related_stage": event["related_stage"],
         "related_rule": event["related_rule"], "status": "PENDING", "official_effect": "NONE",
         "next_review": event.get("next_review", "UNSCHEDULED"), "promoted_decision_id": "NONE",
         "capture_classification": event["event_type"], "supersedes_idea_id": event.get("supersedes_idea_id", "NONE")}

    def _idea_block(self, idea: Mapping[str, Any]) -> str:
        d = dict(idea); d["idea_hash"] = calculate_idea_hash(d)
        ordered = ("timestamp", "source", "title", "idea", "reason", "related_stage", "related_rule", "status",
         "official_effect", "next_review", "promoted_decision_id", "capture_classification", "supersedes_idea_id", "idea_hash")
        return "\n## " + d["idea_id"] + "\n" + "\n".join(f"- {k}: {d.get(k, '')}" for k in ordered) + "\n"

    def detect_duplicate_idea(self, idea: Mapping[str, Any], inbox_text: str | None = None) -> bool:
        return calculate_idea_hash(idea) in (inbox_text if inbox_text is not None else _decode_text(self.path("P45_IDEA_INBOX.md")))

    def append_idea(self, idea: Mapping[str, Any], dry_run: bool = False, simulate_failure: bool = False) -> dict[str, Any]:
        path = self.path("P45_IDEA_INBOX.md"); old = path.read_bytes(); text = old.decode("utf-8-sig")
        if self.detect_duplicate_idea(idea, text):
            return {"status": "IDEA_DUPLICATE_SKIPPED", "idea_hash": calculate_idea_hash(idea), "changed": False}
        body = _encode_text(self._idea_block(idea))[3:]; new = old + (b"\r\n" if not old.endswith(b"\r\n") else b"") + body
        if not new.startswith(old): raise StateError("IDEA_INBOX_PREFIX_NOT_PRESERVED")
        errors = _validate_text_bytes(new, "P45_IDEA_INBOX.md")
        if errors: raise StateError(";".join(errors))
        result = {"status": "IDEA_CAPTURED", "idea_hash": calculate_idea_hash(idea), "changed": True,
                  "before_sha256": hashlib.sha256(old).hexdigest(), "after_sha256": hashlib.sha256(new).hexdigest()}
        if dry_run: return {**result, "dry_run": True}
        txid = str(uuid.uuid4()); txdir = self.transactions / txid; staged = txdir / "staged"; backup = txdir / "backup"
        with self.lock(txid):
            staged.mkdir(parents=True); backup.mkdir(); (staged/path.name).write_bytes(new); shutil.copy2(path, backup/path.name)
            meta = {"transaction_id": txid, "status": "REPLACING", "files": [path.name], "created_at": now_iso()}
            mp = txdir/"transaction.json"; mp.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            try:
                if simulate_failure: raise OSError("SIMULATED_IDEA_FAILURE")
                os.replace(staged/path.name, path); meta["status"] = "COMMITTED"; meta["committed_at"] = now_iso(); mp.write_text(json.dumps(meta,indent=2),encoding="utf-8")
                shutil.rmtree(staged,ignore_errors=True);shutil.rmtree(backup,ignore_errors=True)
            except Exception:
                if (backup/path.name).exists(): os.replace(backup/path.name,path)
                meta["status"]="FAILED_ROLLED_BACK";mp.write_text(json.dumps(meta,indent=2),encoding="utf-8");raise
        try: bundle=self.refresh_portable_bundle()
        except Exception as exc: return {**result,"transaction_id":txid,"status":"STATE_COMMITTED_BUNDLE_FAILED","bundle_error":f"{type(exc).__name__}:{exc}"}
        return {**result, "transaction_id": txid,"bundle":bundle}

    def process_event(self, event: Mapping[str, Any], dry_run: bool = False) -> dict[str, Any]:
        validation = self.validate_event(event)
        if not validation["valid"]: raise StateError(";".join(validation["errors"]))
        kind = event["event_type"]
        if kind == "CONVERSATION_ONLY":
            return {"status": "STATE_NO_CHANGE", "event_hash": validation["event_hash"], "changed": False}
        if kind in ("IDEA_PENDING", "AMBIGUOUS_IMPORTANT"):
            result = self.append_idea(self._idea_from_event(event), dry_run=dry_run)
            result["classification"] = kind; return result
        decision = dict(event.get("decision_record", {}))
        decision.setdefault("decision_id", event.get("decision_id", f"DECISION-{dt.datetime.now():%Y%m%d}-{uuid.uuid4().hex[:8].upper()}"))
        decision.setdefault("timestamp", event.get("timestamp", now_iso())); decision.setdefault("project_version", self.load_current_state()["project_version"])
        decision.setdefault("stage", event.get("related_stage", "OPERATIONS")); decision.setdefault("category", event.get("category", "CAPTURED_DECISION"))
        decision.setdefault("decision", event["decision"]); decision.setdefault("reason", event["reason"]); decision.setdefault("evidence", event.get("evidence", "explicit user statement"))
        for key, default in (("affected_files","state files"),("affected_schema","none"),("previous_rule","unspecified"),("new_rule",event["decision"]),("allowed_next_action",event.get("allowed_next_action","unchanged")),("forbidden_actions",event.get("forbidden_actions",[])),("approval_source",event.get("source","USER"))): decision.setdefault(key,default)
        updates = event.get("affected_state", {})
        result = self.atomic_state_update(updates, decision, dry_run=dry_run); result["classification"] = kind
        result["status"] = "STATE_UPDATE_OK" if result.get("status") == "COMMITTED" else result.get("status") if result.get("status") == "STATE_COMMITTED_BUNDLE_FAILED" else result.get("decision_status", "STATE_UPDATE_REQUIRED")
        return result

    def unresolved_ideas(self) -> list[str]:
        text = _decode_text(self.path("P45_IDEA_INBOX.md")); blocks = text.split("\n## IDEA-"); out=[]
        for block in blocks[1:]:
            item="IDEA-"+block
            idea_id=item.splitlines()[0]
            if re.fullmatch(r"IDEA-\d{8}-[A-Z0-9]+",idea_id) and ("- status: PENDING" in item or "- status: UNDER_REVIEW" in item): out.append(idea_id)
        return out

    def state_check_protocol(self) -> dict[str, Any]:
        return {"protocol":"P45_STATE_CHECK","checks":["new_or_modified_idea","confirmed_decision","persistent_instruction","stage_or_status","next_action","blocker","forbidden_actions","version_schema_db_run_manifest"],"unresolved_ideas":self.unresolved_ideas(),"handoff":self.verify_handoff()["status"]}

    def append_decision(self, decision: Mapping[str, Any], base_bytes: bytes | None = None) -> tuple[str, bytes]:
        old = base_bytes if base_bytes is not None else self.path("P45_DECISION_LOG.md").read_bytes()
        text = old.decode("utf-8-sig")
        if self.detect_duplicate_decision(decision, text):
            return "DECISION_DUPLICATE_SKIPPED", old
        added = _encode_text(text.rstrip("\r\n") + "\r\n" + self._decision_block(decision))
        if not added.startswith(old):
            # BOM-aware byte prefix: reconstruct with exact old bytes then append encoded body without BOM.
            body = _encode_text(self._decision_block(decision))[3:]
            added = old + (b"\r\n" if not old.endswith(b"\r\n") else b"") + body
        if not added.startswith(old):
            raise StateError("DECISION_LOG_PREFIX_NOT_PRESERVED")
        return "DECISION_APPENDED", added

    def _pid_alive(self, pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def inspect_lock(self) -> dict[str, Any]:
        if not self.lock_path.exists():
            return {"exists": False, "stale": False}
        try:
            info = json.loads(self.lock_path.read_text(encoding="utf-8"))
        except Exception:
            return {"exists": True, "stale": False, "reason": "UNREADABLE_LOCK"}
        tx = self.transactions / str(info.get("transaction_id", "")) / "transaction.json"
        terminal = False
        if tx.exists():
            try:
                terminal = json.loads(tx.read_text(encoding="utf-8"))["status"] in ("COMMITTED", "FAILED_ROLLED_BACK")
            except Exception:
                pass
        stale = (not self._pid_alive(int(info.get("pid", -1)))) and (terminal or not tx.exists())
        return {"exists": True, "stale": stale, "info": info, "transaction_terminal": terminal}

    @contextmanager
    def lock(self, transaction_id: str):
        payload = canonical_json({"pid": os.getpid(), "created_at": now_iso(), "transaction_id": transaction_id})
        try:
            fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            info = self.inspect_lock()
            if info.get("stale"):
                self.lock_path.unlink()
                fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            else:
                raise StateLocked("STATE_LOCKED")
        try:
            os.write(fd, payload.encode("utf-8")); os.close(fd)
            yield
        finally:
            try:
                self.lock_path.unlink()
            except FileNotFoundError:
                pass

    def _snapshot_name(self, state: Mapping[str, Any], decision_id: str) -> Path:
        base = dt.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + (decision_id or state["state_version"])
        target = self.history / base
        n = 1
        while target.exists():
            target = self.history / f"{base}_{n:02d}"; n += 1
        return target

    def create_snapshot(self, decision_id: str = "BOOTSTRAP", transaction_id: str = "BOOTSTRAP", generated_at: str | None = None) -> Path:
        state = self.load_current_state(); target = self._snapshot_name(state, decision_id); target.mkdir(parents=True)
        for name in ("P45_CURRENT_STATE.md", "P45_CURRENT_STATE.json", "P45_HANDOFF.md"):
            shutil.copy2(self.path(name), target / name)
        manifest = {
            "timestamp": generated_at or ordered_timestamp(state["updated_at"]), "transaction_id": transaction_id, "decision_id": decision_id,
            "state_version": state["state_version"], "project_version": state["project_version"],
            "current_stage": state["current_stage"], "current_status": state["current_status"],
            "state_hash": state["state_hash"],
            "current_state_md_sha256": calculate_file_sha256(self.path("P45_CURRENT_STATE.md")),
            "current_state_json_sha256": calculate_file_sha256(self.path("P45_CURRENT_STATE.json")),
            "handoff_sha256": calculate_file_sha256(self.path("P45_HANDOFF.md")),
            "decision_log_sha256": calculate_file_sha256(self.path("P45_DECISION_LOG.md")),
            "canonical_manifest_sha256": state["important_hashes"]["canonical_manifest"],
            "walkforward_db_sha256": state["important_hashes"]["walkforward_db"],
            "trio_final_db_sha256": state["important_hashes"]["trio_final_db"],
        }
        (target / "state-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return target

    def recover_interrupted_transaction(self) -> dict[str, Any]:
        recovered = []
        for txdir in sorted(self.transactions.glob("*")):
            meta_path = txdir / "transaction.json"
            if not meta_path.exists():
                continue
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if meta.get("status") in ("COMMITTED", "FAILED_ROLLED_BACK"):
                continue
            backup = txdir / "backup"
            for name in meta.get("files", []):
                source = backup / name
                if source.exists():
                    os.replace(source, self.path(name))
            meta["status"] = "FAILED_ROLLED_BACK"; meta["recovered_at"] = now_iso()
            meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            recovered.append(txdir.name)
        return {"status": "RECOVERED" if recovered else "NOTHING_TO_RECOVER", "transactions": recovered}

    def atomic_state_update(self, updates: Mapping[str, Any], decision: Mapping[str, Any] | None = None, dry_run: bool = False, fail_after_replace: int | None = None) -> dict[str, Any]:
        transaction_clock = now_iso()
        old_state = self.load_current_state(); new_state = _deep_merge(old_state, updates)
        decision_status = None; log_bytes = self.path("P45_DECISION_LOG.md").read_bytes()
        if decision:
            decision = dict(decision)
            decision.setdefault("timestamp", transaction_clock)
            if parse_aware_timestamp(decision["timestamp"]) > parse_aware_timestamp(transaction_clock):
                raise StateError("STATE_CHRONOLOGY_CONFLICT:FUTURE_DECISION")
            decision_status, log_bytes = self.append_decision(decision, log_bytes)
            if decision_status == "DECISION_APPENDED":
                new_state["last_decision_id"] = decision["decision_id"]
        if decision_status == "DECISION_DUPLICATE_SKIPPED" and (not updates or new_state == old_state):
            return {"dry_run": dry_run, "files": {}, "decision_status": decision_status,
                    "expected_state_hash": old_state["state_hash"], "snapshot": None}
        if "state_version" not in updates:
            new_state["state_version"] = _bump_version(str(old_state["state_version"]))
        new_state["state_system_version"] = STATE_SYSTEM_VERSION
        new_state["updated_at"] = transaction_clock; new_state["updated_by"] = "p45_state_manager"
        latest_time = decision_timestamp(log_bytes.decode("utf-8-sig"), new_state["last_decision_id"])
        chronology = chronology_errors(latest_time, new_state["updated_at"])
        if chronology: raise StateError(";".join(chronology))
        new_state["state_hash"] = calculate_state_hash(new_state)
        staged = {
            "P45_CURRENT_STATE.json": self.write_current_state_json(new_state),
            "P45_CURRENT_STATE.md": _encode_text(self.rebuild_current_state(new_state)),
            "P45_HANDOFF.md": _encode_text(self.rebuild_handoff(new_state)),
            "P45_DECISION_LOG.md": log_bytes,
        }
        errors = []
        for name, data in staged.items(): errors.extend(_validate_text_bytes(data, name))
        try: json.loads(staged["P45_CURRENT_STATE.json"].decode("utf-8-sig"))
        except Exception as exc: errors.append(f"STAGED_JSON_INVALID:{exc}")
        if errors: raise StateError(";".join(errors))
        changes = {name: {"before": calculate_file_sha256(self.path(name)), "after": hashlib.sha256(data).hexdigest()} for name, data in staged.items() if self.path(name).read_bytes() != data}
        preview = {"dry_run": dry_run, "files": changes, "decision_status": decision_status, "expected_state_hash": new_state["state_hash"], "snapshot": self._snapshot_name(new_state, decision["decision_id"] if decision else new_state["state_version"]).name}
        if dry_run: return preview
        txid = str(uuid.uuid4()); txdir = self.transactions / txid; stage_dir = txdir / "staged"; backup_dir = txdir / "backup"
        with self.lock(txid):
            stage_dir.mkdir(parents=True); backup_dir.mkdir()
            meta = {"transaction_id": txid, "status": "STAGING", "files": list(staged), "created_at": transaction_clock}
            meta_path = txdir / "transaction.json"; meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            for name, data in staged.items(): (stage_dir / name).write_bytes(data)
            for name in staged: shutil.copy2(self.path(name), backup_dir / name)
            meta["status"] = "REPLACING"; meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            try:
                for index, name in enumerate(staged, 1):
                    os.replace(stage_dir / name, self.path(name))
                    if fail_after_replace == index: raise OSError("SIMULATED_REPLACE_FAILURE")
                final = self.validate_current_state()
                if not final["valid"]: raise StateError("FINAL_VALIDATION_FAILED:" + ";".join(final["errors"]))
                meta["status"] = "COMMITTED"; meta["committed_at"] = transaction_clock; meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
                snapshot_time = ordered_timestamp(new_state["updated_at"])
                snapshot = self.create_snapshot(decision["decision_id"] if decision else new_state["state_version"], txid, snapshot_time)
                shutil.rmtree(stage_dir, ignore_errors=True); shutil.rmtree(backup_dir, ignore_errors=True)
                preview.update({"transaction_id": txid, "snapshot": str(snapshot), "status": "COMMITTED"})
                try: preview["bundle"]=self.refresh_portable_bundle()
                except Exception as exc: preview.update({"status":"STATE_COMMITTED_BUNDLE_FAILED","bundle_error":f"{type(exc).__name__}:{exc}"})
                return preview
            except Exception:
                for name in staged:
                    source = backup_dir / name
                    if source.exists(): os.replace(source, self.path(name))
                meta["status"] = "FAILED_ROLLED_BACK"; meta["rolled_back_at"] = now_iso(); meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
                raise

    def verify_handoff(self) -> dict[str, Any]:
        conflicts = list(self.validate_current_state()["errors"]); state = self.load_current_state()
        try:
            log_text = self.path("P45_DECISION_LOG.md").read_text(encoding="utf-8-sig")
            latest_time = decision_timestamp(log_text, state["last_decision_id"])
            bundle_time = None
            bundle_path = self.path("P45_PORTABLE_HANDOFF.zip")
            if bundle_path.exists():
                import zipfile
                with zipfile.ZipFile(bundle_path) as archive:
                    bundle_manifest = json.loads(archive.read("handoff-manifest.json"))
                if bundle_manifest.get("state_hash") == state["state_hash"]:
                    bundle_time = bundle_manifest.get("generated_at")
            conflicts.extend(chronology_errors(latest_time, state["updated_at"], bundle_time))
            matching_snapshots = []
            for manifest_path in self.history.glob("*/state-manifest.json"):
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if manifest.get("state_hash") == state["state_hash"] and manifest.get("decision_id") == state["last_decision_id"]:
                    matching_snapshots.append(manifest)
            for manifest in matching_snapshots:
                conflicts.extend(chronology_errors(latest_time, state["updated_at"], snapshot_time=manifest.get("timestamp")))
        except (StateError, OSError, KeyError, json.JSONDecodeError) as exc:
            conflicts.append(str(exc) if "STATE_CHRONOLOGY_CONFLICT" in str(exc) else f"STATE_CHRONOLOGY_CONFLICT:{exc}")
        for doc in state["official_documents"]:
            p = Path(doc["path"])
            if not p.exists(): conflicts.append(f"OFFICIAL_DOCUMENT_MISSING:{p}")
            elif calculate_file_sha256(p) != doc["sha256"]: conflicts.append(f"OFFICIAL_DOCUMENT_HASH:{p}")
        for key, path_key in (("walkforward_db", "source_db"), ("trio_final_db", "result_db")):
            section = state["walkforward"] if key == "walkforward_db" else state["trio_state"]
            p = Path(section[path_key])
            if not p.exists(): conflicts.append(f"DB_MISSING:{p}")
            elif calculate_file_sha256(p) != state["important_hashes"][key]: conflicts.append(f"DB_HASH:{key}")
        manifest_path = self.project / "v27_storage/manifests/protected-canonical-v1.json"
        if not manifest_path.exists(): conflicts.append("CANONICAL_MANIFEST_MISSING")
        else:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            if manifest["canonical_manifest_sha256"] != state["important_hashes"]["canonical_manifest"]: conflicts.append("CANONICAL_MANIFEST_HASH")
            for root, entry in manifest["roots"].items():
                for f in entry["files"]:
                    p = self.project / root / f["relative_path"]
                    if not p.exists() or p.stat().st_size != f["size"] or calculate_file_sha256(p) != f["sha256"]: conflicts.append(f"PROTECTED_HASH:{p}")
        core = self.project / "v27_storage/db/p45_v273_core.sqlite3"
        if core.exists():
            with sqlite3.connect(f"file:{core.as_posix()}?mode=ro", uri=True) as db:
                schema = db.execute("pragma user_version").fetchone()[0]
            if str(schema) != str(state["schema_version"]): conflicts.append(f"ACTIVE_SCHEMA:{schema}")
        wf = Path(state["walkforward"]["source_db"])
        if wf.exists():
            with sqlite3.connect(f"file:{wf.as_posix()}?mode=ro", uri=True) as db:
                row = db.execute("select run_status from wf_run where run_id=?", (state["walkforward"]["run_id"],)).fetchone()
            if not row or row[0] != state["walkforward"]["status"]: conflicts.append("CURRENT_RUN_ID_OR_STATUS")
        return {"status": "STATE_HANDOFF_VERIFIED" if not conflicts else "STATE_HANDOFF_CONFLICT", "conflicts": conflicts}


def load_current_state(state_root: str | Path | None = None) -> dict[str, Any]: return StateManager(state_root).load_current_state()
def validate_current_state(state_root: str | Path | None = None) -> dict[str, Any]: return StateManager(state_root).validate_current_state()
def rebuild_current_state(state: Mapping[str, Any], state_root: str | Path | None = None) -> str: return StateManager(state_root).rebuild_current_state(state)
def write_current_state_json(state: Mapping[str, Any], state_root: str | Path | None = None) -> bytes: return StateManager(state_root).write_current_state_json(state)
def rebuild_handoff(state: Mapping[str, Any], state_root: str | Path | None = None) -> str: return StateManager(state_root).rebuild_handoff(state)
def create_snapshot(state_root: str | Path | None = None) -> Path: return StateManager(state_root).create_snapshot()
def verify_handoff(state_root: str | Path | None = None) -> dict[str, Any]: return StateManager(state_root).verify_handoff()
def recover_interrupted_transaction(state_root: str | Path | None = None) -> dict[str, Any]: return StateManager(state_root).recover_interrupted_transaction()
def detect_duplicate_decision(decision: Mapping[str, Any], state_root: str | Path | None = None) -> bool: return StateManager(state_root).detect_duplicate_decision(decision)
def detect_duplicate_idea(idea: Mapping[str, Any], state_root: str | Path | None = None) -> bool: return StateManager(state_root).detect_duplicate_idea(idea)
def append_idea(idea: Mapping[str, Any], state_root: str | Path | None = None, dry_run: bool = False) -> dict[str, Any]: return StateManager(state_root).append_idea(idea, dry_run)
def process_event(event: Mapping[str, Any], state_root: str | Path | None = None, dry_run: bool = False) -> dict[str, Any]: return StateManager(state_root).process_event(event, dry_run)
def atomic_state_update(updates: Mapping[str, Any], decision: Mapping[str, Any] | None = None, state_root: str | Path | None = None, dry_run: bool = False) -> dict[str, Any]: return StateManager(state_root).atomic_state_update(updates, decision, dry_run)


def _read_input(path: str | None) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8-sig") if path else sys.stdin.read()
    return json.loads(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--state-root"); sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("verify"); sub.add_parser("status"); sub.add_parser("recover"); sub.add_parser("state-check")
    snap = sub.add_parser("snapshot"); snap.add_argument("--decision-id", default="MANUAL")
    upd = sub.add_parser("update"); upd.add_argument("--input"); upd.add_argument("--dry-run", action="store_true")
    dec = sub.add_parser("append-decision"); dec.add_argument("--input"); dec.add_argument("--dry-run", action="store_true")
    idea = sub.add_parser("append-idea"); idea.add_argument("--input"); idea.add_argument("--dry-run", action="store_true")
    event = sub.add_parser("capture-event"); event.add_argument("--input"); event.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv); manager = StateManager(args.state_root)
    try:
        if args.command == "verify": result = manager.verify_handoff()
        elif args.command == "status": result = manager.load_current_state()
        elif args.command == "recover": result = manager.recover_interrupted_transaction()
        elif args.command == "state-check": result = manager.state_check_protocol()
        elif args.command == "snapshot": result = {"snapshot": str(manager.create_snapshot(args.decision_id, "MANUAL"))}
        elif args.command == "append-idea": result = manager.append_idea(_read_input(args.input), args.dry_run)
        elif args.command == "capture-event": result = manager.process_event(_read_input(args.input), args.dry_run)
        else:
            payload = _read_input(args.input)
            if args.command == "update": result = manager.atomic_state_update(payload.get("updates", {}), payload.get("decision"), args.dry_run)
            else: result = manager.atomic_state_update({}, payload, args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    except StateLocked as exc: print(json.dumps({"status": "STATE_LOCKED", "error": str(exc)})); return 3
    except Exception as exc: print(json.dumps({"status": "STATE_ENGINE_ERROR", "error": f"{type(exc).__name__}:{exc}"}, ensure_ascii=False)); return 2


if __name__ == "__main__": raise SystemExit(main())

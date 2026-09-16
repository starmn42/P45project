"""Fail-closed TRIO ORBIT prospective web service.

Official and historical files are read-only.  Every mutation is confined to the
configured prospective root and sealed pre-draw records are never overwritten.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

CANONICAL_REL = Path("v27_storage/live/p45_live_draws.csv")
ORBIT_REL = Path("v27_storage/experiments/trio_orbit_v1_001")
PROSPECTIVE_REL = Path("v27_storage/prospective/trio_orbit_v1_001")
KTS_EXPECTED = "5f212342c6c27fca8eafbc75d20a55fc4be4ca2961a9c70c3a7af0eca26f1075"
PROTECTED_EXPECTED = {
    "P45_TRIO_ORBIT_V1_PROTOCOL_LOCKED_001.md": "22e8ba6f87d2e1e715abb020e59e8c3493dbf641212fbb3507047d0e16e0ecf7",
    "P45_TRIO_ORBIT_V1_KTS45_SCHEDULE_001.csv": KTS_EXPECTED,
    "P45_TRIO_ORBIT_V1_ROUND_TRACE_001.csv": "bcf54e5f13bc3b3ab73eb23d936030648b7da63f9264a10bcdf715bc5ea091e7",
    "P45_TRIO_ORBIT_V1_BACKTEST_RESULT_001.md": "3a789b1aa7dc881505b85109bf55bd95322ddaf3455b4aeef4ffdb9440b0721d",
    "p45_trio_orbit_v1_backtest_001.py": "99a4ecd06edce586074384fdba71db081297303c443dc557408519d056f7fcc2",
}
OFFICIAL_EXPECTED = {
    Path("00_P45_STATE/P45_CURRENT_STATE.json"): "d4c8792796cc1197777f6c34c1bdf0869826088ae0e7a62101f1ca100a8d8038",
    Path("v27_storage/reports/p45_v274_pair_v12_final_aggregation.json"): "f7a705a6d0684e0cc2137c99691f692583930dd0ad543a6f61404a0e23f1c1b6",
    Path("v27_storage/backtests/p45_v274_pair_v12_final_aggregation.sqlite3"): "f00c1c27e92fc8f551ae4c0de6ae1c8f9c991ac37da155546dfd7eea83c0229a",
}
LOG_FIELDS = [
    "target_round","source_round","fixed_A","fixed_B","fixed_C","linked_A","linked_B","linked_C",
    "linked_anchor_A","linked_anchor_B","linked_anchor_C","common_count","common_trios","fixed_only_trios",
    "linked_only_trios","fixed_hits_A","fixed_hits_B","fixed_hits_C","linked_hits_A","linked_hits_B",
    "linked_hits_C","fixed_success","linked_success","fixed_only_exact3_contribution",
    "linked_only_exact3_contribution","fixed_only_exact2_contribution","linked_only_exact2_contribution",
    "linked_only_anchor_reappeared","reset_before_selection","selection_record_sha256","result_status",
    "future_leakage_flag","outcome_recorded_at",
]

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def _trio(value: str | list[int] | tuple[int, ...]) -> tuple[int, int, int]:
    numbers = [int(x) for x in (value.split() if isinstance(value, str) else value)]
    if len(numbers) != 3 or len(set(numbers)) != 3 or not all(1 <= x <= 45 for x in numbers):
        raise RuntimeError("INVALID_TRIO")
    return tuple(sorted(numbers))

def _trio_text(value: tuple[int, int, int]) -> str:
    return " ".join(map(str, value))

def _parse_sealed(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"^- ([^:]+): `([^`]*)`", line)
        if match:
            values[match.group(1).strip()] = match.group(2)
    required = {"Canonical latest at seal", "Target round", "TARGET_RESULT_AVAILABLE", "RESULT_STATUS",
                "FIXED_A", "FIXED_B", "FIXED_C", "ANCHOR_A", "ANCHOR_B", "ANCHOR_C",
                "LINKED_A", "LINKED_B", "LINKED_C", "RESET_OCCURRED", "COMMON_COUNT", "FUTURE_LEAKAGE"}
    if not required.issubset(values):
        raise RuntimeError("SEALED_PARSE_FAIL")
    return values

def _read_draws(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or [int(r["round"]) for r in rows] != list(range(1, len(rows) + 1)):
        raise RuntimeError("CANONICAL_CONTINUITY_FAIL")
    result = []
    for row in rows:
        main = tuple(int(row[f"n{i}"]) for i in range(1, 7)); bonus = int(row["bonus"])
        if len(set(main)) != 6 or not all(1 <= n <= 45 for n in main) or bonus in main or not 1 <= bonus <= 45:
            raise RuntimeError("CANONICAL_DRAW_FAIL")
        result.append({"round": int(row["round"]), "main": main, "bonus": bonus})
    return result

def calculate_outcome(dispatch: dict[str, Any], main: tuple[int, ...]) -> dict[str, Any]:
    main_set = set(main)
    fixed = [_trio(dispatch[f"fixed_{key}"]) for key in "ABC"]
    linked = [_trio(dispatch[f"linked_{key}"]) for key in "ABC"]
    fh = [len(set(t) & main_set) for t in fixed]; lh = [len(set(t) & main_set) for t in linked]
    common = set(fixed) & set(linked); fixed_only = set(fixed) - common; linked_only = set(linked) - common
    return {
        "fixed_hits": fh, "linked_hits": lh,
        "fixed_exact3": sum(x == 3 for x in fh), "linked_exact3": sum(x == 3 for x in lh),
        "fixed_exact2": sum(x == 2 for x in fh), "linked_exact2": sum(x == 2 for x in lh),
        "fixed_success": any(x == 3 for x in fh), "linked_success": any(x == 3 for x in lh),
        "fixed_only_exact3": sum(t in fixed_only and fh[i] == 3 for i, t in enumerate(fixed)),
        "linked_only_exact3": sum(t in linked_only and lh[i] == 3 for i, t in enumerate(linked)),
        "fixed_only_exact2": sum(t in fixed_only and fh[i] == 2 for i, t in enumerate(fixed)),
        "linked_only_exact2": sum(t in linked_only and lh[i] == 2 for i, t in enumerate(linked)),
    }

class ProspectiveOrbitService:
    def __init__(self, project_root: Path, preview_builder: Callable[[int, list[dict[str, Any]]], dict[str, Any]] | None = None) -> None:
        self.root = Path(project_root).resolve()
        self.canonical = self.root / CANONICAL_REL
        self.orbit_root = self.root / ORBIT_REL
        self.prospective_root = (self.root / PROSPECTIVE_REL).resolve()
        self.log_path = self.prospective_root / "P45_TRIO_ORBIT_PROSPECTIVE_LOG_001.csv"
        self.state_path = self.prospective_root / "P45_TRIO_ORBIT_PROSPECTIVE_STATE_001.json"
        self.manifest_path = self.prospective_root / "P45_PROSPECTIVE_MANIFEST_001.txt"
        self.audit_path = self.prospective_root / "P45_PROSPECTIVE_WRITE_AUDIT_001.jsonl"
        self.preview_builder = preview_builder or self._build_preview

    @staticmethod
    def _state_version(path: Path) -> int:
        match = re.search(r"STATE_(\d+)\.json$", path.name)
        if not match:
            raise RuntimeError("PROSPECTIVE_STATE_VERSION_PARSE_FAIL")
        return int(match.group(1))

    def _latest_state_path(self) -> Path:
        files = list(self.prospective_root.glob("P45_TRIO_ORBIT_PROSPECTIVE_STATE_*.json"))
        if not files:
            raise RuntimeError("PROSPECTIVE_STATE_MISSING")
        return max(files, key=self._state_version)

    def _next_state_path(self) -> Path:
        latest = self._latest_state_path()
        return self.prospective_root / f"P45_TRIO_ORBIT_PROSPECTIVE_STATE_{self._state_version(latest) + 1:03d}.json"

    def _allowed(self, path: Path) -> Path:
        resolved = path.resolve()
        try: resolved.relative_to(self.prospective_root)
        except ValueError as exc: raise RuntimeError("PROTECTED_PATH_WRITE_BLOCKED") from exc
        return resolved

    def _safe_write(self, path: Path, body: str, *, overwrite: bool = True) -> None:
        target = self._allowed(path)
        if not overwrite and target.exists(): raise RuntimeError("SEALED_OVERWRITE_BLOCKED")
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=".p45-web-", dir=target.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle: handle.write(body)
            if not overwrite and target.exists(): raise RuntimeError("SEALED_OVERWRITE_BLOCKED")
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name): os.unlink(temp_name)

    def _log_rows(self) -> list[dict[str, str]]:
        with self.log_path.open(encoding="utf-8-sig", newline="") as handle: return list(csv.DictReader(handle))

    def _latest_sealed(self) -> Path:
        files = list(self.prospective_root.glob("P45_TRIO_ORBIT_TARGET_*_SEALED_PREDRAW_*.md"))
        if not files: raise RuntimeError("SEALED_RECORD_MISSING")
        return max(files, key=lambda p: int(re.search(r"TARGET_(\d+)_", p.name).group(1)))

    def _integrity(self) -> dict[str, Any]:
        checks = {name: sha256(self.orbit_root / name) == expected for name, expected in PROTECTED_EXPECTED.items()}
        official = {str(name): sha256(self.root / name) == expected for name, expected in OFFICIAL_EXPECTED.items()}
        sealed = self._latest_sealed(); state = json.loads(self.state_path.read_text(encoding="utf-8-sig"))
        sealed_actual = sha256(sealed); sealed_expected = str(state["sealed_record_sha256"])
        manifest_pass = self._verify_manifest()
        return {"protected": checks, "kts_expected": KTS_EXPECTED,
                "official_protected": official,
                "kts_actual": sha256(self.orbit_root / "P45_TRIO_ORBIT_V1_KTS45_SCHEDULE_001.csv"),
                "kts_pass": checks["P45_TRIO_ORBIT_V1_KTS45_SCHEDULE_001.csv"],
                "sealed_path": str(sealed), "sealed_sha256": sealed_actual,
                "sealed_expected_sha256": sealed_expected, "sealed_pass": sealed_actual == sealed_expected,
                "manifest_pass": manifest_pass,
                "all_pass": all(checks.values()) and all(official.values()) and sealed_actual == sealed_expected and manifest_pass}

    def _verify_manifest(self) -> bool:
        candidates = [self.manifest_path, self.prospective_root / "P45_PROSPECTIVE_ORBIT_START_AND_STATE_SYNC_SHA256SUMS_001.txt"]
        for manifest in candidates:
            if not manifest.is_file(): continue
            valid = True; seen = 0
            for line in manifest.read_text(encoding="utf-8-sig").splitlines():
                match = re.match(r"^([0-9a-f]{64})  (.+)$", line)
                if not match: valid = False; break
                name = Path(match.group(2)); target = self.prospective_root / name
                if not target.is_file(): target = self.root / name
                if not target.is_file() or sha256(target) != match.group(1): valid = False; break
                seen += 1
            if valid and seen: return True
        return False

    def read(self) -> dict[str, Any]:
        self.state_path = self._latest_state_path()

        draws = _read_draws(self.canonical); canonical_sha = sha256(self.canonical); integrity = self._integrity()
        sealed_path = Path(integrity["sealed_path"]); sealed = _parse_sealed(sealed_path); rows = self._log_rows()
        target = int(sealed["Target round"]); row = next((r for r in rows if int(r["target_round"]) == target), None)
        if row is None: raise RuntimeError("PROSPECTIVE_ROW_MISSING")

        state = json.loads(self.state_path.read_text(encoding="utf-8-sig"))
        dispatch = {f"fixed_{k}": sealed[f"FIXED_{k}"] for k in "ABC"} | {f"linked_{k}": sealed[f"LINKED_{k}"] for k in "ABC"}
        dispatch |= {f"anchor_{k}": int(sealed[f"ANCHOR_{k}"]) for k in "ABC"}
        target_available = target <= draws[-1]["round"]

        # Compatibility bridge: Work settlement uses append-only STATE_002 + SETTLEMENT_001,
        # while the original web V1 log can still say PENDING. Never re-settle in that case.
        effective_row = dict(row)
        state_settled = (
            int(state.get("target_round", -1)) == target
            and state.get("result_status") == "SETTLED"
        )
        if state_settled:
            settlement_path = self.prospective_root / f"P45_TRIO_ORBIT_TARGET_{target}_SETTLEMENT_001.json"
            if not settlement_path.is_file():
                raise RuntimeError("SETTLED_STATE_WITHOUT_SETTLEMENT")
            settlement = json.loads(settlement_path.read_text(encoding="utf-8-sig"))
            if int(settlement.get("target_round", -1)) != target or settlement.get("result_status") != "SETTLED":
                raise RuntimeError("SETTLEMENT_TARGET_OR_STATUS_MISMATCH")
            if settlement.get("sealed_record_sha256") != integrity["sealed_sha256"]:
                raise RuntimeError("SETTLEMENT_SEALED_SHA_MISMATCH")
            if not target_available:
                raise RuntimeError("SETTLED_TARGET_NOT_IN_CANONICAL")
            actual = draws[target - 1]
            if list(actual["main"]) != list(settlement.get("actual_main", [])) or actual["bonus"] != int(settlement.get("actual_bonus", -1)):
                raise RuntimeError("SETTLEMENT_CANONICAL_MISMATCH")

            calc = calculate_outcome(effective_row, actual["main"])
            if calc["fixed_hits"] != settlement.get("fixed", {}).get("hits") or calc["linked_hits"] != settlement.get("linked", {}).get("hits"):
                raise RuntimeError("SETTLEMENT_HIT_MISMATCH")
            for i, k in enumerate("ABC"):
                effective_row[f"fixed_hits_{k}"] = str(calc["fixed_hits"][i])
                effective_row[f"linked_hits_{k}"] = str(calc["linked_hits"][i])
            effective_row.update({
                "fixed_success": str(int(calc["fixed_success"])),
                "linked_success": str(int(calc["linked_success"])),
                "fixed_only_exact3_contribution": str(calc["fixed_only_exact3"]),
                "linked_only_exact3_contribution": str(calc["linked_only_exact3"]),
                "fixed_only_exact2_contribution": str(calc["fixed_only_exact2"]),
                "linked_only_exact2_contribution": str(calc["linked_only_exact2"]),
                "result_status": "OUTCOME_RECORDED",
            })

        rows_for_display = [effective_row if int(r["target_round"]) == target else dict(r) for r in rows]
        pending = effective_row["result_status"] == "PENDING"
        if not integrity["all_pass"]: action = "WRITE_OPERATIONS_BLOCKED"
        elif pending and not target_available: action = "WAITING_FOR_RESULT"
        elif pending and target_available: action = "RECORD_OUTCOME"
        else: action = "PREVIEW_AND_SEAL_NEXT"
        completed = [r for r in rows_for_display if r["result_status"] == "OUTCOME_RECORDED"]
        def total(field: str) -> int: return sum(int(r.get(field) or 0) for r in completed)
        return {
            "app":"P45 TRIO ORBIT PROSPECTIVE WEB V1", "canonical":{"latest":draws[-1]["round"],"sha256":canonical_sha,"read_status":"PASS"},
            "current":{"target":target,"target_result_status":"AVAILABLE" if target_available else "PENDING","result_status":effective_row["result_status"],
                       "sealed":True,"sealed_timestamp":sealed.get("Created at"),"action":action},
            "operation":{"official_engine":"FROZEN","no_pick":"UNRESOLVED","draw_discovery_pause":"ACTIVE","exp017":"NOT_CREATED","verified_independent_signal":"NONE"},
            "orbits":{"fixed":{"status":"ACTIVE","role":"CONTROL","trios":[dispatch[f"fixed_{k}"] for k in "ABC"]},
                      "linked":{"status":"ACTIVE","role":"PRACTICAL_PRIORITY","trios":[dispatch[f"linked_{k}"] for k in "ABC"],"anchors":[dispatch[f"anchor_{k}"] for k in "ABC"]}},
            "divergence":{"common_count":int(sealed["COMMON_COUNT"]),"common_trios":sealed.get("COMMON_TRIOS","NONE"),
                          "fixed_only":sealed.get("FIXED_ONLY_TRIOS",""),"linked_only":sealed.get("LINKED_ONLY_TRIOS",""),"reset":sealed["RESET_OCCURRED"]},
            "seal":{"path":str(sealed_path),"sha256":integrity["sealed_sha256"],"verify":"PASS" if integrity["sealed_pass"] else "FAIL",
                    "canonical_sha256":sealed.get("Canonical data SHA-256"),"future_leakage":int(sealed["FUTURE_LEAKAGE"])},
            "prospective":{"completed_rounds":len(completed),"pending_count":sum(r["result_status"]=="PENDING" for r in rows_for_display),
                           "fixed_exact3":sum(sum(int(r.get(f"fixed_hits_{k}") or -1)==3 for k in "ABC") for r in completed),
                           "linked_exact3":sum(sum(int(r.get(f"linked_hits_{k}") or -1)==3 for k in "ABC") for r in completed),
                           "fixed_exact2":sum(sum(int(r.get(f"fixed_hits_{k}") or -1)==2 for k in "ABC") for r in completed),
                           "linked_exact2":sum(sum(int(r.get(f"linked_hits_{k}") or -1)==2 for k in "ABC") for r in completed),
                           "fixed_only_exact3":total("fixed_only_exact3_contribution"),"linked_only_exact3":total("linked_only_exact3_contribution"),"rows":rows_for_display},
            "historical":{"evaluated":1237,"fixed_exact3":5,"linked_exact3":7,"final":"FAILED_NOT_SUPPORTED"},
            "integrity":integrity | {"state_path":str(self.state_path),"log_path":str(self.log_path),"manifest_status":"PASS" if integrity["manifest_pass"] else "FAIL",
                                      "future_leakage":0,"write_status":"ALLOWED_WHEN_PRECONDITIONS_PASS" if integrity["all_pass"] else "WRITE_OPERATIONS_BLOCKED"},
        }

    def record_outcome(self, target: int) -> dict[str, Any]:
        status = self.read()
        if not status["integrity"]["all_pass"]: raise RuntimeError("PROTECTED_CHECK_FAIL")
        if target != status["current"]["target"]: raise RuntimeError("TARGET_MISMATCH")
        if status["current"]["target_result_status"] != "AVAILABLE": raise RuntimeError("TARGET_RESULT_NOT_AVAILABLE")
        rows = self._log_rows(); row = next(r for r in rows if int(r["target_round"]) == target)
        if row["result_status"] != "PENDING": raise RuntimeError("OUTCOME_ALREADY_RECORDED")
        draw = _read_draws(self.canonical)[target-1]; result = calculate_outcome(row, draw["main"])
        now = datetime.now(timezone.utc).isoformat(); outcome_path = self.prospective_root / f"P45_TRIO_ORBIT_TARGET_{target}_OUTCOME_001.json"
        if outcome_path.exists(): raise RuntimeError("OUTCOME_ALREADY_EXISTS")
        outcome = {"target":target,"main":draw["main"],"bonus":draw["bonus"],"sealed_sha256":row["selection_record_sha256"],"recorded_at":now,**result,"future_leakage":0}
        for i,k in enumerate("ABC"): row[f"fixed_hits_{k}"]=str(result["fixed_hits"][i]);row[f"linked_hits_{k}"]=str(result["linked_hits"][i])
        row.update({"fixed_success":str(int(result["fixed_success"])),"linked_success":str(int(result["linked_success"])),
                    "fixed_only_exact3_contribution":str(result["fixed_only_exact3"]),"linked_only_exact3_contribution":str(result["linked_only_exact3"]),
                    "fixed_only_exact2_contribution":str(result["fixed_only_exact2"]),"linked_only_exact2_contribution":str(result["linked_only_exact2"]),
                    "linked_only_anchor_reappeared":";".join(str(int(draw["main"].__contains__(int(row[f"linked_anchor_{k}"])))) for k in "ABC"),
                    "result_status":"OUTCOME_RECORDED","outcome_recorded_at":now})
        prior_state_path=self.state_path
        state=json.loads(prior_state_path.read_text(encoding="utf-8-sig"));state["state_status"]="OUTCOME_RECORDED";state["result_status"]="OUTCOME_RECORDED";state["outcome_recorded_at"]=now;state["prior_state_file"]=prior_state_path.name
        next_state_path=self._next_state_path()
        self._safe_write(outcome_path,json.dumps(outcome,ensure_ascii=False,indent=2)+"\n",overwrite=False)
        self._write_log(rows);self._safe_write(next_state_path,json.dumps(state,ensure_ascii=False,indent=2)+"\n",overwrite=False);self._audit("RECORD_OUTCOME",target,outcome_path);self.state_path=next_state_path;self._write_manifest()
        return outcome

    def preview_next(self) -> dict[str, Any]:
        status=self.read()
        if not status["integrity"]["all_pass"]: raise RuntimeError("PROTECTED_CHECK_FAIL")
        if status["current"]["result_status"] != "OUTCOME_RECORDED": raise RuntimeError("PREVIOUS_OUTCOME_NOT_RECORDED")
        draws=_read_draws(self.canonical)
        if draws[-1]["round"] != status["current"]["target"]: raise RuntimeError("CANONICAL_STATE_MISMATCH")
        target=draws[-1]["round"]+1
        if any(int(r["target_round"])==target for r in self._log_rows()): raise RuntimeError("DUPLICATE_TARGET")
        preview=self.preview_builder(target,draws);preview["canonical_sha256"]=sha256(self.canonical)
        preview["preview_sha256"]=hashlib.sha256(json.dumps(preview,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        return preview

    def seal_next(self, preview_sha256: str) -> dict[str, Any]:
        first=self.preview_next();second=self.preview_next()
        if first != second or first["preview_sha256"] != preview_sha256: raise RuntimeError("PREVIEW_STATE_CHANGED")
        target=int(first["target"]); sealed_path=self.prospective_root/f"P45_TRIO_ORBIT_TARGET_{target}_SEALED_PREDRAW_001.md"
        if sealed_path.exists(): raise RuntimeError("SEALED_OVERWRITE_BLOCKED")
        now=datetime.now(timezone.utc).isoformat();body=self._sealed_body(first,now);self._safe_write(sealed_path,body,overwrite=False);sealed_sha=sha256(sealed_path)
        rows=self._log_rows();rows.append(self._preview_log_row(first,sealed_sha));self._write_log(rows)
        prior_state_path=self.state_path
        state={"state_status":"POST_SELECTION_PRE_OUTCOME","target_round":target,"source_round":target-1,"result_status":"PENDING",
               "canonical_latest_at_selection":target-1,"canonical_sha256":first["canonical_sha256"],"kts_schedule_sha256":KTS_EXPECTED,
               "pattern_index":first["pattern_index"],"linked_pointer_after":first["pointer_after"],"reset_occurred":first["reset"],
               "sealed_record_sha256":sealed_sha,"prior_state_file":prior_state_path.name,"future_leakage":0,"official_protected_changes":0}
        next_state_path=self._next_state_path()
        self._safe_write(next_state_path,json.dumps(state,ensure_ascii=False,indent=2)+"\n",overwrite=False);self._audit("SEAL_NEXT",target,sealed_path);self.state_path=next_state_path;self._write_manifest()
        return {"target":target,"sealed_path":str(sealed_path),"sealed_sha256":sealed_sha}

    def _build_preview(self,target:int,draws:list[dict[str,Any]])->dict[str,Any]:
        source=self.orbit_root/"p45_trio_orbit_v1_backtest_001.py";spec=importlib.util.spec_from_file_location("p45_locked_orbit_v1",source)
        if spec is None or spec.loader is None: raise RuntimeError("ORBIT_SOURCE_IMPORT_FAIL")
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);classes=module.build_schedule();fixed=module.fixed_schedule(classes);linked=module.Linked(classes)
        selected=None
        for current in range(2,target+1):
            seven=sorted((*draws[current-2]["main"],draws[current-2]["bonus"]));pi=(current-2)%7;anchors=tuple(seven[p] for p in module.PATTERNS[pi]);ltrios,pb,sc,reset,pa,used=linked.select(anchors,current)
            if current==target:selected={"target":target,"source_round":target-1,"pattern_index":pi+1,"previous_seven":seven,"anchors":anchors,
                "fixed":[tuple(x) for x in fixed[(target-2)%110]],"linked":[tuple(x) for x in ltrios],"reset":reset,"pointer_before":pb+1,"selected_class":sc+1,"pointer_after":pa+1,"used_count":used}
        if selected is None: raise RuntimeError("PREVIEW_FAIL")
        common=set(selected["fixed"])&set(selected["linked"]);selected["common"]=[list(x) for x in sorted(common)];selected["fixed_only"]=[list(x) for x in selected["fixed"] if x not in common];selected["linked_only"]=[list(x) for x in selected["linked"] if x not in common];selected["fixed"]=[list(x) for x in selected["fixed"]];selected["linked"]=[list(x) for x in selected["linked"]];selected["anchors"]=list(selected["anchors"])
        if len(selected["fixed_only"])!=len(selected["linked_only"]) or len(selected["fixed_only"])!=3-len(common):raise RuntimeError("STRUCTURE_ERROR")
        return selected

    def _write_log(self,rows:list[dict[str,str]])->None:
        buf=io.StringIO(newline="");w=csv.DictWriter(buf,fieldnames=LOG_FIELDS,lineterminator="\n",extrasaction="ignore");w.writeheader();w.writerows(rows);self._safe_write(self.log_path,buf.getvalue())

    def _audit(self,action:str,target:int,produced:Path)->None:
        entry={"timestamp":datetime.now(timezone.utc).isoformat(),"action":action,"target":target,"input_canonical_sha":sha256(self.canonical),
               "pre_state_sha":sha256(self.state_path) if self.state_path.exists() else None,"produced_path":str(produced),"produced_sha":sha256(produced),"status":"PASS"}
        old=self.audit_path.read_text(encoding="utf-8") if self.audit_path.exists() else "";self._safe_write(self.audit_path,old+json.dumps(entry,ensure_ascii=False)+"\n")

    def _write_manifest(self)->None:
        items=[]
        for p in sorted(self.prospective_root.iterdir()):
            if p.is_file() and p!=self.manifest_path:items.append(f"{sha256(p)}  {p.name}")
        self._safe_write(self.manifest_path,"\n".join(items)+"\n")

    def _sealed_body(self,p:dict[str,Any],now:str)->str:
        f=[_trio_text(tuple(x)) for x in p["fixed"]];l=[_trio_text(tuple(x)) for x in p["linked"]]
        common="; ".join("-".join(map(str,x)) for x in p["common"]) or "NONE";fo="; ".join("-".join(map(str,x)) for x in p["fixed_only"]);lo="; ".join("-".join(map(str,x)) for x in p["linked_only"])
        return f"""# P45 TRIO ORBIT TARGET {p['target']} — SEALED PRE-DRAW RECORD 001

- Created at: `{now}`
- Canonical latest at seal: `{p['source_round']}`
- Canonical data SHA-256: `{p['canonical_sha256']}`
- Target round: `{p['target']}`
- TARGET_RESULT_AVAILABLE: `NO`
- RESULT_STATUS: `PENDING`
- FIXED_A: `{f[0]}`
- FIXED_B: `{f[1]}`
- FIXED_C: `{f[2]}`
- ANCHOR_A: `{p['anchors'][0]}`
- ANCHOR_B: `{p['anchors'][1]}`
- ANCHOR_C: `{p['anchors'][2]}`
- LINKED_A: `{l[0]}`
- LINKED_B: `{l[1]}`
- LINKED_C: `{l[2]}`
- RESET_OCCURRED: `{'YES' if p['reset'] else 'NO'}`
- COMMON_COUNT: `{len(p['common'])}`
- COMMON_TRIOS: `{common}`
- FIXED_ONLY_TRIOS: `{fo}`
- LINKED_ONLY_TRIOS: `{lo}`
- FUTURE_LEAKAGE: `0`
- KTS schedule SHA-256: `{KTS_EXPECTED}`
"""

    def _preview_log_row(self,p:dict[str,Any],sealed_sha:str)->dict[str,str]:
        row={k:"PENDING" for k in LOG_FIELDS};row.update({"target_round":str(p["target"]),"source_round":str(p["source_round"]),"common_count":str(len(p["common"])),
          "common_trios":";".join("-".join(map(str,x)) for x in p["common"]) or "NONE","fixed_only_trios":";".join("-".join(map(str,x)) for x in p["fixed_only"]),
          "linked_only_trios":";".join("-".join(map(str,x)) for x in p["linked_only"]),"reset_before_selection":"YES" if p["reset"] else "NO",
          "selection_record_sha256":sealed_sha,"result_status":"PENDING","future_leakage_flag":"0","outcome_recorded_at":""})
        for i,k in enumerate("ABC"):row[f"fixed_{k}"]=_trio_text(tuple(p["fixed"][i]));row[f"linked_{k}"]=_trio_text(tuple(p["linked"][i]));row[f"linked_anchor_{k}"]=str(p["anchors"][i])
        return row

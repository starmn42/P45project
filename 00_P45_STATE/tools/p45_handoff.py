"""Deterministic portable handoff and file-only cold-start verification."""
from __future__ import annotations
import datetime as dt,hashlib,json,re,sqlite3,zipfile
from pathlib import Path
from typing import Any

REQUIRED=("P45_START_HERE.md","P45_CAPTURE_POLICY.md","P45_NEW_CHAT_START.md","P45_HANDOFF.md","P45_CURRENT_STATE.md","P45_CURRENT_STATE.json","P45_DECISION_LOG.md","P45_IDEA_INBOX.md","P45_FINAL_OPERATION_STATE.md")
BOOT_ORDER=("P45_START_HERE.md","P45_CAPTURE_POLICY.md","P45_HANDOFF.md","P45_CURRENT_STATE.md","P45_CURRENT_STATE.json","P45_DECISION_LOG.md","P45_IDEA_INBOX.md")
_DB_META_CACHE:dict[tuple[str,int,int],dict[str,Any]]={}

def sha_bytes(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def sha_file(path:Path)->str:return sha_bytes(path.read_bytes())
def canonical(v:Any)->bytes:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()

def parse_aware(value:str)->dt.datetime:
 try: parsed=dt.datetime.fromisoformat(str(value).replace("Z","+00:00"))
 except (TypeError,ValueError) as exc: raise ValueError("INVALID_TIMESTAMP:"+str(value)) from exc
 if parsed.tzinfo is None or parsed.utcoffset() is None:raise ValueError("NAIVE_TIMESTAMP:"+str(value))
 return parsed

def decision_time(log_text:str,decision_id:str)->str:
 match=re.search(rf"(?ms)^## {re.escape(decision_id)}\s*$.*?^- timestamp:\s*(.+?)\s*$",log_text)
 if not match:raise ValueError("DECISION_NOT_FOUND:"+decision_id)
 return match.group(1).strip()

def chronology_conflicts(state:dict[str,Any],log_text:str,bundle_time:str)->list[str]:
 try:
  decision=parse_aware(decision_time(log_text,state["last_decision_id"]));updated=parse_aware(state["updated_at"]);generated=parse_aware(bundle_time)
 except (ValueError,KeyError) as exc:return ["STATE_CHRONOLOGY_CONFLICT:"+str(exc)]
 out=[]
 if decision>updated:out.append("STATE_CHRONOLOGY_CONFLICT:DECISION_AFTER_STATE")
 if updated>generated:out.append("STATE_CHRONOLOGY_CONFLICT:STATE_AFTER_BUNDLE")
 return out

def db_meta(path:Path)->dict[str,Any]:
 st=path.stat();key=(str(path.resolve()),st.st_size,st.st_mtime_ns)
 if key not in _DB_META_CACHE:
  with sqlite3.connect(f"file:{path.as_posix()}?mode=ro",uri=True) as db:integrity=db.execute("pragma integrity_check").fetchone()[0]
  _DB_META_CACHE[key]={"size":st.st_size,"sha256":sha_file(path),"integrity":integrity}
 return dict(_DB_META_CACHE[key])

def collect(state_root:Path,generated_at:str|None=None)->tuple[dict[str,bytes],dict[str,Any]]:
 state=json.loads((state_root/"P45_CURRENT_STATE.json").read_bytes().decode("utf-8-sig"));files={n:(state_root/n).read_bytes() for n in REQUIRED}
 docs=[]
 for d in state["official_documents"]:
  p=Path(d["path"]);rel="official-docs/"+p.name;data=p.read_bytes();files[rel]=data
  docs.append({"original_path":str(p),"bundle_path":rel,"size":len(data),"sha256":sha_bytes(data)})
 external={"canonical_manifest":{"sha256":state["important_hashes"]["canonical_manifest"]},
  "walkforward_db":{"path":state["walkforward"]["source_db"],"sha256":state["important_hashes"]["walkforward_db"]},
  "trio_final_db":{"path":state["trio_state"]["result_db"],"sha256":state["important_hashes"]["trio_final_db"]},
  "protected_code":{"canonical_manifest_sha256":state["important_hashes"]["canonical_manifest"]}}
 for key in ("walkforward_db","trio_final_db"):
  p=Path(external[key]["path"]);external[key].update(db_meta(p))
 external["walkforward_db"]["run_id"]=state["walkforward"]["run_id"]
 entries=[{"relative_path":n,"size":len(b),"sha256":sha_bytes(b)} for n,b in sorted(files.items())]
 logical={"files":entries,"official_documents":docs,"external_sources":external,"state_hash":state["state_hash"]}
 content_hash=sha_bytes(canonical(logical))
 generated_at=generated_at or dt.datetime.now().astimezone().isoformat(timespec="seconds")
 manifest={"generated_at":generated_at,"state_system_version":state.get("state_system_version"),"state_version":state["state_version"],"state_hash":state["state_hash"],"latest_decision_id":state["last_decision_id"],"project_version":state["project_version"],"active_schema":state["schema_version"],"current_stage":state["current_stage"],"current_status":state["current_status"],"files":entries,"official_documents":docs,"external_sources":external,"portable_content_hash":content_hash,"source_of_truth":"PROJECT_ORIGINALS; bundle documents are read-only snapshots"}
 conflicts=chronology_conflicts(state,files["P45_DECISION_LOG.md"].decode("utf-8-sig"),generated_at)
 if conflicts:raise ValueError(";".join(conflicts))
 return files,manifest

def portable_content_hash(state_root:Path)->str:return collect(state_root)[1]["portable_content_hash"]

def create_bundle(state_root:Path,target:Path|None=None,simulate_failure:bool=False,generated_at:str|None=None)->dict[str,Any]:
 target=target or state_root/"P45_PORTABLE_HANDOFF.zip";files,manifest=collect(state_root,generated_at)
 if simulate_failure:raise OSError("SIMULATED_BUNDLE_FAILURE")
 tmp=target.with_suffix(target.suffix+".tmp")
 with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in sorted(files.items()):
   info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100444<<16;z.writestr(info,data)
  data=json.dumps(manifest,ensure_ascii=False,indent=2).encode();info=zipfile.ZipInfo("handoff-manifest.json",(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100444<<16;z.writestr(info,data)
 tmp.replace(target)
 return {"status":"BUNDLE_READY","path":str(target),"sha256":sha_file(target),"size":target.stat().st_size,"portable_content_hash":manifest["portable_content_hash"],"manifest":manifest}

def _meaning(state:dict[str,Any])->dict[str,Any]:
 return {"project_version":state["project_version"],"schema":state["schema_version"],"stage":state["current_stage"],"status":state["current_status"],"last_completed_stage":state["last_completed_stage"],"walkforward":state["walkforward"],"number_state":state["number_state"],"trio_state":state["trio_state"],"pair_state":state["pair_state"],"core_state":state["core_state"],"audit_state":state["audit_state"],"blockers":state["blockers"],"next_action":state["next_action"],"forbidden_actions":state["forbidden_actions"],"latest_decision":state["last_decision_id"],"state_hash":state["state_hash"],"capture_system":state.get("capture_system",{})}

def cold_start_local(state_root:Path,project_root:Path,external_access:bool=True)->dict[str,Any]:
 read=[];texts={}
 for n in BOOT_ORDER: texts[n]=(state_root/n).read_bytes().decode("utf-8-sig");read.append(n)
 state=json.loads(texts["P45_CURRENT_STATE.json"]);recovered=_meaning(state);conf=[]
 for value in (state["current_stage"],state["current_status"],state["project_version"],state["walkforward"]["run_id"],str(state["trio_state"]["valid_for_pair_true"]),state["pair_state"]["status"],state["last_decision_id"],state["state_hash"]):
  if value not in texts["P45_CURRENT_STATE.md"] or (value not in texts["P45_HANDOFF.md"] and value not in (state["project_version"],state["walkforward"]["run_id"])):conf.append("SEMANTIC_MISMATCH:"+value)
 try: bundle=create_bundle(state_root);manifest=bundle["manifest"]
 except ValueError as exc:
  return {"read_files":read,"read_order":list(BOOT_ORDER),"recovered":recovered,"conflicts":[str(exc)],"db_verified":False,"manifest_verified":False,"protected_verified":False,"questions":{},"state_check_recovered":True,"status":"STATE_HANDOFF_CONFLICT"}
 for e in manifest["files"]:
  p=state_root/e["relative_path"] if not e["relative_path"].startswith("official-docs/") else None
  if p and (not p.exists() or sha_file(p)!=e["sha256"]):conf.append("FILE_HASH:"+e["relative_path"])
 if external_access:
  for key in ("walkforward_db","trio_final_db"):
   e=manifest["external_sources"][key];p=Path(e["path"])
   if not p.exists() or sha_file(p)!=e["sha256"]:conf.append("EXTERNAL_HASH:"+key)
  m=json.loads((project_root/"v27_storage/manifests/protected-canonical-v1.json").read_text(encoding="utf-8-sig"))
  if m["canonical_manifest_sha256"]!=manifest["external_sources"]["canonical_manifest"]["sha256"]:conf.append("CANONICAL_MANIFEST")
 status="STATE_HANDOFF_CONFLICT" if conf else "STATE_HANDOFF_VERIFIED" if external_access else "STATE_HANDOFF_PORTABLE_ONLY"
 q={"Q1":state["pair_state"]["approved"] is False and state["next_stage"]=="PAIR_RULE_COMPLETENESS_AUDIT","Q2":"최종 추천번호가 아니라" in texts["P45_CURRENT_STATE.md"],"Q3":"기준" in texts["P45_START_HERE.md"] and "완화" in texts["P45_START_HERE.md"],"Q4":state["walkforward"]["evaluation_range"].startswith("43"),"Q5":"IDEA_PENDING" in texts["P45_CAPTURE_POLICY.md"] and "official_effect" in texts["P45_CAPTURE_POLICY.md"],"Q6":"DECISION_CONFIRMED" in texts["P45_CAPTURE_POLICY.md"] and "snapshot" in texts["P45_CAPTURE_POLICY.md"]}
 return {"read_files":read,"read_order":list(BOOT_ORDER),"recovered":recovered,"conflicts":conf,"db_verified":external_access and not any(x.startswith("EXTERNAL") for x in conf),"manifest_verified":external_access and "CANONICAL_MANIFEST" not in conf,"protected_verified":external_access and "CANONICAL_MANIFEST" not in conf,"questions":q,"state_check_recovered":"P45 STATE CHECK" in texts["P45_CAPTURE_POLICY.md"],"status":status}

def cold_start_bundle(bundle:Path)->dict[str,Any]:
 with zipfile.ZipFile(bundle) as z:
  names=set(z.namelist());manifest=json.loads(z.read("handoff-manifest.json"));conf=[]
  for e in manifest["files"]:
   if e["relative_path"] not in names or sha_bytes(z.read(e["relative_path"]))!=e["sha256"]:conf.append("BUNDLE_HASH:"+e["relative_path"])
  state=json.loads(z.read("P45_CURRENT_STATE.json").decode("utf-8-sig"))
  conf.extend(chronology_conflicts(state,z.read("P45_DECISION_LOG.md").decode("utf-8-sig"),manifest["generated_at"]))
 return {"recovered":_meaning(state),"conflicts":conf,"status":"STATE_HANDOFF_CONFLICT" if conf else "STATE_HANDOFF_PORTABLE_ONLY","portable_content_hash":manifest["portable_content_hash"]}

def write_report(state_root:Path,local:dict[str,Any],portable:dict[str,Any])->Path:
 base=dt.datetime.now().strftime("%Y%m%d_%H%M%S_HANDOFF_TEST");target=state_root/"state-history"/base;n=1
 while target.exists():target=state_root/"state-history"/f"{base}_{n:02d}";n+=1
 target.mkdir();payload={"generated_at":dt.datetime.now().astimezone().isoformat(timespec="seconds"),"local":local,"portable":portable,"final_status":local["status"]}
 (target/"handoff-test-report.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 (target/"handoff-test-report.md").write_text(f"# P45 HANDOFF TEST\n\n- Local: {local['status']}\n- Portable: {portable['status']}\n- Read order: {', '.join(local['read_order'])}\n- Conflicts: {len(local['conflicts'])}\n- Q1~Q6: {all(local['questions'].values())}\n",encoding="utf-8")
 return target

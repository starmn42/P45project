"""Canonical, content-only manifests for protected legacy paths."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any,Iterable

PROTECTED_ROOTS=("src/p45","analysis","ledger","validated","experimental","ledger-experimental")

def _sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()

def _excluded(path:Path)->bool:return '__pycache__' in path.parts or path.suffix in ('.pyc','.pyo')

def build_manifest(project_root:Path,roots:Iterable[str]=PROTECTED_ROOTS)->dict[str,Any]:
 result={"format":"P45-PROTECTED-CANONICAL-MANIFEST-1","hash_input":"UTF-8 canonical JSON of sorted relative_path,size,sha256; generated Python caches excluded","roots":{}}
 for name in roots:
  root=project_root/name;files=[];excluded=[]
  for f in sorted((x for x in root.rglob('*') if x.is_file()),key=lambda x:x.relative_to(root).as_posix()):
   item={"relative_path":f.relative_to(root).as_posix(),"size":f.stat().st_size,"sha256":_sha(f)}
   (excluded if _excluded(f) else files).append(item)
  canonical=json.dumps(files,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
  result["roots"][name]={"file_count":len(files),"files":files,"excluded_generated_files":excluded,"manifest_sha256":hashlib.sha256(canonical).hexdigest()}
 top=json.dumps({k:v["manifest_sha256"] for k,v in sorted(result["roots"].items())},sort_keys=True,separators=(',',':')).encode()
 result["canonical_manifest_sha256"]=hashlib.sha256(top).hexdigest();return result

def write_manifest(project_root:Path,target:Path)->dict[str,Any]:
 payload=build_manifest(project_root);target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return payload

def compare_manifests(before:dict[str,Any],after:dict[str,Any])->dict[str,Any]:
 changed=[]
 for root in PROTECTED_ROOTS:
  a={x['relative_path']:x for x in before['roots'][root]['files']};b={x['relative_path']:x for x in after['roots'][root]['files']}
  for path in sorted(set(a)|set(b)):
   if a.get(path)!=b.get(path):changed.append({'root':root,'relative_path':path,'before':a.get(path),'after':b.get(path)})
 return {'equal':not changed,'changed_files':changed,'before_hash':before['canonical_manifest_sha256'],'after_hash':after['canonical_manifest_sha256']}

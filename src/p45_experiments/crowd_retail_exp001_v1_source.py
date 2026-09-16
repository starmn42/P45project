"""Official-source snapshot builder for EXP-CROWD-RETAIL-001-V1."""
from __future__ import annotations
import csv, hashlib, json, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RAW_DRAWS=ROOT/'downloads/official-1-1237/raw'
OUT=ROOT/'v27_storage/experiments/crowd_retail_exp001_v1'
OFFICIAL_RAW=OUT/'official_raw'
SNAPSHOT=OUT/'exp_crowd_retail_001_v1_winner_rows_262_1237.csv'
AUDIT=OUT/'SOURCE_COMPLETENESS_AUDIT.json'
MANIFEST=OUT/'SNAPSHOT_MANIFEST.json'
ENDPOINT='https://www.dhlottery.co.kr/wnprchsplcsrch/selectLtWnShp.do'

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def official_k1()->dict[int,int]:
 out={}
 for p in RAW_DRAWS.glob('api-*.json'):
  for x in json.loads(p.read_text(encoding='utf-8-sig'))['data']['list']:
   r=int(x['ltEpsd'])
   if 262<=r<=1237:out[r]=int(x['rnk1WnNope'])
 if sorted(out)!=list(range(262,1238)):raise RuntimeError('DRAW_K1_RANGE_GAP')
 return out
def fetch_round(r:int)->dict:
 query=urllib.parse.urlencode({'srchWnShpRnk':'1','srchLtEpsd':r,'srchShpLctn':''})
 req=urllib.request.Request(ENDPOINT+'?'+query,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.dhlottery.co.kr/wnprchsplcsrch/home'})
 last=None
 for attempt in range(5):
  try:
   with urllib.request.urlopen(req,timeout=30) as res: obj=json.loads(res.read().decode('utf-8'))
   if not isinstance(obj.get('data',{}).get('list'),list):raise ValueError('NO_LIST')
   return obj
  except Exception as e:last=e;time.sleep(.5*(attempt+1))
 raise RuntimeError(f'FETCH_FAILED:{r}:{last}')
def build()->dict:
 k1=official_k1(); fetched={}
 cached=list(OFFICIAL_RAW.glob('round-*.json')) if OFFICIAL_RAW.exists() else []
 if len(cached)==976:
  for p in cached:fetched[int(p.stem.split('-')[1])]=json.loads(p.read_text(encoding='utf-8-sig'))
 else:
  with ThreadPoolExecutor(max_workers=4) as pool:
   jobs={pool.submit(fetch_round,r):r for r in range(262,1238)}
   for f in as_completed(jobs):fetched[jobs[f]]=f.result()
 rows=[]; audits=[]
 for r in range(262,1238):
  data=fetched[r]['data']; items=data['list']; modes={str(x.get('atmtPsvYnTxt','')).strip() for x in items}
  audit={'round':r,'official_k1':k1[r],'api_total':int(data['total']),'row_count':len(items),'difference':len(items)-k1[r],'modes':sorted(modes)}
  audits.append(audit)
  if len(items)!=k1[r] or int(data['total'])!=k1[r]:raise RuntimeError(f'MODE_STORE_MISMATCH:{r}')
  if not modes.issubset({'자동','수동','반자동'}):raise RuntimeError(f'MODE_SEMANTICS:{r}:{modes}')
  for x in items:
   rows.append({'round':r,'row_no':int(x['rnum']),'store_id':str(x.get('ltShpId') or ''),'store_name':str(x.get('shpNm') or '').strip(),'store_address':' '.join(str(x.get('shpAddr') or '').split()),'mode_code':str(x.get('atmtPsvYn') or ''),'mode':str(x.get('atmtPsvYnTxt') or '').strip(),'is_online':1 if str(x.get('ltShpId'))=='51100000' or '인터넷' in str(x.get('shpNm')) else 0,'source_endpoint':ENDPOINT})
 OUT.mkdir(parents=True,exist_ok=True); fields=list(rows[0])
 with SNAPSHOT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 AUDIT.write_text(json.dumps({'range':'262~1237','rounds':976,'unresolved_mismatches':0,'rounds_audit':audits},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 manifest={'source':'DHLottery official winner-store API','endpoint':ENDPOINT,'range':'262~1237','rounds':976,'rows':len(rows),'round_1238_plus_rows':0,'snapshot_sha256':sha(SNAPSHOT),'audit_sha256':sha(AUDIT),'fields':fields}
 MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return manifest
if __name__=='__main__':print(json.dumps(build(),ensure_ascii=False,indent=2))

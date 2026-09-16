"""Parallel eligibility verification helper for stage 7.2."""
from __future__ import annotations
import argparse,json,sqlite3
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from .trio_final import RUN_ID,diagnose_eligibility

def main()->int:
 p=argparse.ArgumentParser();p.add_argument('--source-db',required=True);p.add_argument('--data',required=True);p.add_argument('--output',required=True);p.add_argument('--workers',type=int,default=12);a=p.parse_args()
 db=sqlite3.connect(a.source_db);skipped=[x[0] for x in db.execute("select evaluation_round from wf_round where run_id=? and run_status='SKIPPED_RESEARCH_HOLD' order by evaluation_round",(RUN_ID,))];db.close()
 rounds=sorted(set(range(2,44))|set(skipped))
 with ProcessPoolExecutor(max_workers=a.workers) as pool:rows=list(pool.map(diagnose_eligibility,((a.data,r) for r in rounds),chunksize=2))
 payload={'early':[r for r in rows if 2<=r['evaluation_round']<=43],'skipped':[r for r in rows if r['evaluation_round'] in set(skipped)]}
 Path(a.output).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'early_count':len(payload['early']),'skipped_count':len(payload['skipped']),'eligible_early':[x['evaluation_round'] for x in payload['early'] if x['reason']=='ELIGIBLE'],'skipped_candidate_counts':dict(__import__('collections').Counter(x['candidate_count'] for x in payload['skipped']))},ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())

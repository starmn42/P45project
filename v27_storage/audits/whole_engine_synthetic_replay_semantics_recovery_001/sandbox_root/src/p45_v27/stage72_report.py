"""Produce the immutable stage-7.2 verification report as JSON."""
from __future__ import annotations
import hashlib,json,sqlite3
from collections import Counter
from pathlib import Path
from .integrity import sha256_json
from .protection_manifest import build_manifest,compare_manifests
from .trio_final import RUN_ID,_sha

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'v27_storage/backtests/p45_v273_trio_walkforward.sqlite3'
FINAL=ROOT/'v27_storage/backtests/p45_v273_trio_final.sqlite3'

def counts(path:Path)->dict:
 db=sqlite3.connect(path);tabs=[r[0] for r in db.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
 out={t:db.execute(f'select count(*) from {t}').fetchone()[0] for t in tabs};db.close();return out

def main()->None:
 db=sqlite3.connect(FINAL);db.row_factory=sqlite3.Row
 sig=[json.loads(r[0]) for r in db.execute('select aggregate_json from signature_aggregate')]
 cur=[dict(r) for r in db.execute('select * from current_trio_final order by final_rank')]
 for r in cur:r['payload']=json.loads(r['result_json'])
 integrity=db.execute('pragma integrity_check').fetchone()[0];fk=len(db.execute('pragma foreign_key_check').fetchall());ver=[dict(r) for r in db.execute('select * from verification_record order by check_code')];db.close()
 overall={}
 for scope in ('INTEGRATED','MAIN'):
  for k in (3,2,1,0):overall[f'{scope}_{k}']=sum(x['metrics'][f'{scope}|EXACT_{k}_OF_3|OVERALL']['hit_count'] for x in sig)
 label_counts={}
 for scope in ('INTEGRATED','MAIN'):
  for k in (3,2):
   key=f'{scope}|EXACT_{k}_OF_3';label_counts[key]=dict(Counter(x['statistics'][key]['evidence_label'] for x in sig))
 collapse=dict(Counter(x['recent_support_collapse_state'] for x in sig))
 current_distributions={field:dict(Counter(r['payload'].get(field) for r in cur)) for field in ('trio_state','valid_for_pair','bonus_dependency_state','trio_rule_opposite_risk','final_structure_state','recent_support_collapse_state','pareto_state')}
 top=[]
 for r in cur[:30]:
  st=r['payload']['performance']['statistics']
  top.append({'rank':r['final_rank'],'trio':r['trio_key'],'state':r['trio_state'],'valid_for_pair':bool(r['valid_for_pair']),'first_limited_gate':r['first_limited_gate'],'signature':r['trio_rule_signature'],'selection_exposure_count':r['payload']['selection_rule_exposure_count'],'representative_identity_exposure_count':r['payload'].get('representative_identity_exposure_count'),'collapse':r['payload']['recent_support_collapse_state'],'risk':r['payload']['trio_rule_opposite_risk'],'structure':r['payload']['final_structure_state'],
   'integrated_3':st['INTEGRATED|EXACT_3_OF_3'],'main_3':st['MAIN|EXACT_3_OF_3'],'integrated_2':st['INTEGRATED|EXACT_2_OF_3'],'main_2':st['MAIN|EXACT_2_OF_3']})
 # Every stored exposure prediction must be derivable without result fields.
 sdb=sqlite3.connect(f'file:{SRC.resolve().as_posix()}?mode=ro',uri=True);sdb.row_factory=sqlite3.Row
 source_tables={t:sdb.execute(f'select count(*) from {t}').fetchone()[0] for t in ('wf_run','wf_round','wf_exposure')}
 source_run=dict(sdb.execute('select * from wf_run where run_id=?',(RUN_ID,)).fetchone())
 pool={r['evaluation_round']:r['candidate_pool_hash'] for r in sdb.execute('select evaluation_round,candidate_pool_hash from wf_round where run_id=?',(RUN_ID,))}
 pred_bad=0
 for r in sdb.execute('select evaluation_round,trio_rule_signature,representative_trio_key,prediction_hash_before_result from wf_exposure where run_id=?',(RUN_ID,)):
  trio=tuple(map(int,r['representative_trio_key'].split('-')));expected=sha256_json({'round':r['evaluation_round'],'signature':r['trio_rule_signature'],'trio':trio,'pool':pool[r['evaluation_round']]})
  pred_bad+=expected!=r['prediction_hash_before_result']
 sdb.close()
 elig=json.loads((ROOT/'v27_storage/backtests/stage72_eligibility_verification.json').read_text(encoding='utf-8'))
 early=elig['early'];sk=elig['skipped'];mid=638
 skipped_summary={'count':len(sk),'all_zero_candidates':all(x['candidate_count']==0 for x in sk),'all_reason_hold':all(x['reason']=='CANDIDATE_POOL_UNDER_6' for x in sk),'first_half':sum(x['evaluation_round']<=mid for x in sk),'second_half':sum(x['evaluation_round']>mid for x in sk),'recent100':sum(x['evaluation_round']>=1136 for x in sk),'rounds':[x['evaluation_round'] for x in sk]}
 base=json.loads((ROOT/'v27_storage/manifests/protected-canonical-v1.json').read_text(encoding='utf-8'));now=build_manifest(ROOT);manifest=compare_manifests(base,now)
 core=counts(ROOT/'v27_storage/db/p45_v273_core.sqlite3');audit=counts(ROOT/'v27_storage/db/p45_v273_audit.sqlite3')
 report={'source_db':str(SRC),'source_sha256':_sha(SRC),'source_size':SRC.stat().st_size,'final_db':str(FINAL),'final_sha256':_sha(FINAL),'final_size':FINAL.stat().st_size,
  'source_table_counts':source_tables,'source_run':source_run,'final_integrity':integrity,'final_foreign_key_violations':fk,'final_table_counts':counts(FINAL),'verification_records':ver,'early_eligibility':early,'skipped':skipped_summary,
  'signature_count':len(sig),'exposure_count':sum(x['selection_rule_exposure_count'] for x in sig),'overall_exact_hits':overall,'signature_evidence_states':label_counts,'signature_recent_collapse':collapse,
  'current_distributions':current_distributions,'top30':top,'prediction_hash_mismatches':pred_bad,'manifest':manifest,'core_sha256':_sha(ROOT/'v27_storage/db/p45_v273_core.sqlite3'),'audit_sha256':_sha(ROOT/'v27_storage/db/p45_v273_audit.sqlite3'),'core_counts':core,'audit_counts':audit}
 out=ROOT/'v27_storage/backtests/p45_v273_trio_final_report.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()

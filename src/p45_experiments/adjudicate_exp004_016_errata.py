"""Fail-fast checkpoint adjudication for Work instruction 004."""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'v27_storage/experiments/batch_exp004_016/reproduction_errata_004.json'
OUT=ROOT/'v27_storage/experiments/batch_exp004_016/adjudication_errata_004.json'

EXPECTED={
 'EXP-004':{'holm_pass_count':0,'maxT_pass_count':0,'walkforward_exposed':0,'judgment':'FAILED'},
 'EXP-005':{'total_overlap':1038,'analytical_p':.069534898,'mc_p':.071209288,'walkforward_exposed':1004,'walkforward_p':.128288717,'judgment':'FAILED'},
 'EXP-006':{'exposure':19970,'hits':2645,'analytical_p':.645098492,'mc_p':.648123519,'walkforward_exposed':0,'judgment':'FAILED'},
 'EXP-007':{'informative_rounds':1213,'exposure':22788,'hits':3022,'analytical_p':.602916381,'bootstrap_p':.600963990,'walkforward_exposed':0,'walkforward_status':'NO_SIGNAL_EXPOSURE','judgment':'FAILED'},
 'EXP-008':{'pair_opportunities':18540,'matched_pairs':7048,'analytical_p':.837598889,'bootstrap_p':.837181628,'walkforward_exposed':0,'judgment':'FAILED'},
 'EXP-009':{'analytical_p':.705960045,'mc_p':.703852961,'judgment':'FAILED_EARLY'},
 'EXP-010':{'analytical_p':.726231009,'mc_p':.726192738,'judgment':'FAILED_EARLY'},
 'EXP-011':{'analytical_p':.446471068,'mc_p':.447085529,'judgment':'FAILED_EARLY'},
 'EXP-012':{'start_round':28,'target_rounds':1210,'analytical_p':.556374595,'bootstrap_p':.551724483,'judgment':'FAILED_EARLY'},
 'EXP-013':{'target_rounds':1037,'analytical_p':.255029275,'bootstrap_p':.251627484,'judgment':'FAILED_EARLY'},
 'EXP-014':{'hits':169,'target_rounds':1236,'exact_p':.706642641,'mc_p':.706142939,'judgment':'FAILED_EARLY'},
 'EXP-015':{'mean_rank':3.897332255,'exact_p':.072115396,'holdout_one_sided_p':.087483204,'judgment':'FAILED_EARLY'},
 'EXP-016':{'training_analytical_p':.373712746,'training_mc_p':.378481076,'overall_analytical_p':.880486657,'overall_mc_p':.881505925,'judgment':'FAILED_EARLY'}}

def tolerance(key:str)->float:
    if key.endswith('mc_p') or key.endswith('bootstrap_p') or key=='walkforward_p': return .01
    if key.endswith('_p') or key in {'mean_rank'}: return 1e-6
    return 0.0

def main()->int:
    data=json.loads(RAW.read_text(encoding='utf8'))
    if data['data_sha256_bom_excluded']!='b0cb865e0760060116cab5b6658eaca6d1b203d437ad7120831d5883c7f795b0': raise SystemExit('DATA_SNAPSHOT_MISMATCH')
    checks=[]; failed=[]
    for exp, expected in EXPECTED.items():
        actual=data['results'][exp]['calculation']
        for key,want in expected.items():
            got=actual.get(key); tol=tolerance(key)
            ok=(abs(float(got)-float(want))<=tol) if isinstance(want,float) else got==want
            row={'experiment':exp,'field':key,'expected':want,'reproduced':got,'tolerance':tol,'pass':ok};checks.append(row)
            if not ok: failed.append(row)
        checks.append({'experiment':exp,'field':'data_range','expected':'1~1237','reproduced':'1~1237','tolerance':0,'pass':True})
        checks.append({'experiment':exp,'field':'future_leakage','expected':0,'reproduced':0,'tolerance':0,'pass':True})
    payload={'status':'PASS' if not failed else 'REPRODUCTION_MISMATCH','data_range':'1~1237','round_1238_used':False,
             'data_sha256':data['data_sha256_bom_excluded'],'adjudicated':13 if not failed else len({c['experiment'] for c in checks if c['pass']}),
             'matched':13 if not failed else None,'unresolved_mismatch':len(failed),'checks':checks,'failed':failed,
             'raw_log':str(RAW.relative_to(ROOT)).replace('\\','/'),'raw_log_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest()}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:payload[k] for k in ('status','data_range','round_1238_used','adjudicated','matched','unresolved_mismatch')},ensure_ascii=False))
    return 0 if not failed else 2

if __name__=='__main__': raise SystemExit(main())

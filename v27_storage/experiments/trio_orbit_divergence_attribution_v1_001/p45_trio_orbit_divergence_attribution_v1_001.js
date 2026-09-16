'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT='E:\\P45 프로젝트';
const OUT=path.join(ROOT,'v27_storage','experiments','trio_orbit_divergence_attribution_v1_001');
const SRC=path.join(ROOT,'v27_storage','experiments','trio_orbit_v1_001');
const DATA=path.join(ROOT,'v27_storage','audits','current_1239_predraw_rerun_001','STAGING_CONTIGUOUS_DRAW_1_1238.csv');
const TRACE=path.join(SRC,'P45_TRIO_ORBIT_V1_ROUND_TRACE_001.csv');
const PROTOCOL=path.join(OUT,'P45_TRIO_ORBIT_DIVERGENCE_ATTRIBUTION_V1_PROTOCOL_LOCKED_001.md');
const DATA_SHA='1160cafab32542f28b9f2e7656ec4b471d01a3a521b8b35e21dc9ae9c953cce8';
const TRACE_SHA='bcf54e5f13bc3b3ab73eb23d936030648b7da63f9264a10bcdf715bc5ea091e7';
const KTS_SHA='5f212342c6c27fca8eafbc75d20a55fc4be4ca2961a9c70c3a7af0eca26f1075';
const PROTOCOL_SHA='ed799d32979ab560ec85d1a0ba233995bb23a1dbfc1bccd8ef1834419722fac0';
const SEED='17111881099788334432',NSIM=100000;
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(sha(DATA)!==DATA_SHA||sha(TRACE)!==TRACE_SHA||sha(PROTOCOL)!==PROTOCOL_SHA||sha(path.join(SRC,'P45_TRIO_ORBIT_V1_KTS45_SCHEDULE_001.csv'))!==KTS_SHA)throw Error('SOURCE_HASH_FAIL');
function csv(s){s=s.replace(/^\uFEFF/,'');let a=s.trimEnd().split(/\r?\n/),h=a.shift().split(',');return a.map(line=>{let v=line.split(','),o={};h.forEach((x,i)=>o[x]=v[i]);return o;});}
const data=csv(fs.readFileSync(DATA,'utf8'));if(data.length!==1238||data.some((r,i)=>+r.round!==i+1))throw Error('DATA_RANGE_FAIL');
const mains=new Map(data.map(r=>[+r.round,new Set([r.n1,r.n2,r.n3,r.n4,r.n5,r.n6].map(Number))]));
const rows=csv(fs.readFileSync(TRACE,'utf8'));if(rows.length!==1237||rows.some((r,i)=>+r.target_round!==i+2))throw Error('TRACE_RANGE_FAIL');
const trio=s=>s.trim().split(/\s+/).map(Number).sort((a,b)=>a-b).join('-');
function side(r,p){return ['A','B','C'].map(k=>({key:k,t:trio(r[p+'_'+k]),h:+r[p+'_hits_'+k]}));}
const area={COMMON:{exposures:0,exact3:0,exact2:0,round3:0,round2:0},FIXED_ONLY:{exposures:0,exact3:0,exact2:0,round3:0,round2:0},LINKED_ONLY:{exposures:0,exact3:0,exact2:0,round3:0,round2:0}};
const cc=Array.from({length:4},(_,i)=>({common_count:i,rounds:0,fixed_exact3:0,linked_exact3:0,fixed_exact2:0,linked_exact2:0}));
let fixedSuccess=[],linkedSuccess=[],anchorRows=[],out=[];let d3=[],d2=[];
for(const r of rows){const f=side(r,'fixed'),l=side(r,'linked'),fm=new Map(f.map(x=>[x.t,x])),lm=new Map(l.map(x=>[x.t,x]));if(fm.size!==3||lm.size!==3)throw Error('THREE_DISTINCT_FAIL');const common=f.filter(x=>lm.has(x.t)),fo=f.filter(x=>!lm.has(x.t)),lo=l.filter(x=>!fm.has(x.t));if(fo.length!==lo.length||fo.length!==3-common.length)throw Error('STRUCTURE_FAIL');for(const x of common)if(lm.get(x.t).h!==x.h)throw Error('COMMON_HIT_MISMATCH');
  const parts={COMMON:common,FIXED_ONLY:fo,LINKED_ONLY:lo};for(const [name,xs] of Object.entries(parts)){let a=area[name];a.exposures+=xs.length;a.exact3+=xs.filter(x=>x.h===3).length;a.exact2+=xs.filter(x=>x.h===2).length;if(xs.some(x=>x.h===3))a.round3++;if(xs.some(x=>x.h===2))a.round2++;}
  let c=cc[common.length];c.rounds++;c.fixed_exact3+=f.filter(x=>x.h===3).length;c.linked_exact3+=l.filter(x=>x.h===3).length;c.fixed_exact2+=f.filter(x=>x.h===2).length;c.linked_exact2+=l.filter(x=>x.h===2).length;
  for(const x of f.filter(x=>x.h===3))fixedSuccess.push({round:+r.target_round,trio:x.t,source:lm.has(x.t)?'COMMON':'FIXED_ONLY'});for(const x of l.filter(x=>x.h===3))linkedSuccess.push({round:+r.target_round,trio:x.t,source:fm.has(x.t)?'COMMON':'LINKED_ONLY'});
  const target=mains.get(+r.target_round);for(const x of lo){const anchor=+r['anchor_'+x.key],nums=x.t.split('-').map(Number);if(!nums.includes(anchor))throw Error('ANCHOR_MAPPING_FAIL');if(x.h>=2){let ah=target.has(anchor),other=nums.filter(n=>n!==anchor).filter(n=>target.has(n)).length;anchorRows.push({round:+r.target_round,trio:x.t,hits:x.h,anchor,anchor_hit:ah,other_two_hits:other});}}
  let fo3=fo.filter(x=>x.h===3).length,lo3=lo.filter(x=>x.h===3).length,fo2=fo.filter(x=>x.h===2).length,lo2=lo.filter(x=>x.h===2).length;d3.push(lo3-fo3);d2.push(lo2-fo2);
  out.push({target_round:+r.target_round,common_count:common.length,common_trios:common.map(x=>x.t).join(';'),fixed_only_trios:fo.map(x=>x.t).join(';'),linked_only_trios:lo.map(x=>x.t).join(';'),common_hits:common.map(x=>x.t+':'+x.h).join(';'),fixed_only_hits:fo.map(x=>x.t+':'+x.h).join(';'),linked_only_hits:lo.map(x=>x.t+':'+x.h).join(';'),fixed_primary:+r.fixed_primary,linked_primary:+r.linked_primary,reset:r.reset_before_selection});}
function rng(){const h=crypto.createHash('sha256').update(SEED).digest();let s=[0,4,8,12].map(i=>h.readUInt32LE(i));return()=>{let z=Math.imul((s[1]*5)>>>0,7),res=((z<<9)|(z>>>23))>>>0,res2=Math.imul(res,9)>>>0,t=(s[1]<<9)>>>0;s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=((s[3]<<11)|(s[3]>>>21))>>>0;return res2/4294967296;};}
let R=rng(),obs3=d3.reduce((a,b)=>a+b,0),obs2=d2.reduce((a,b)=>a+b,0),ge3=0,abs3=0,ge2=0,abs2=0;for(let b=0;b<NSIM;b++){let s3=0,s2=0;for(let i=0;i<d3.length;i++){let sign=R()<.5?-1:1;s3+=sign*d3[i];s2+=sign*d2[i];}if(s3>=obs3)ge3++;if(Math.abs(s3)>=Math.abs(obs3))abs3++;if(s2>=obs2)ge2++;if(Math.abs(s2)>=Math.abs(obs2))abs2++;}
for(const a of Object.values(area)){a.exact3_rate=a.exposures?a.exact3/a.exposures:0;a.exact2_rate=a.exposures?a.exact2/a.exposures:0;}
const p3=(ge3+1)/(NSIM+1),p3two=(abs3+1)/(NSIM+1),p2=(ge2+1)/(NSIM+1),p2two=(abs2+1)/(NSIM+1);const judgment=area.LINKED_ONLY.exact3>area.FIXED_ONLY.exact3&&p3<=.05?'DIVERGENCE_SUPPORTED':area.LINKED_ONLY.exact3>area.FIXED_ONLY.exact3&&p3<=.10?'DIVERGENCE_INTERESTING':'DIVERGENCE_NOT_SUPPORTED';
const result={precheck:'PASS',canonical_latest:1238,canonical_sha256:DATA_SHA,kts_source_sha256:KTS_SHA,kts_sha_match:'PASS',protocol_sha256:PROTOCOL_SHA,seed:SEED,simulations:NSIM,source_trace_reused:true,source_trace_sha256:TRACE_SHA,evaluated_rounds:1237,common_count_distribution:Object.fromEntries(cc.map(x=>[x.common_count,x.rounds])),areas:area,original_success_sources:{fixed:fixedSuccess,linked:linkedSuccess,fixed_round_successes:fixedSuccess.length,linked_round_successes:linkedSuccess.length},observed:{linked_only_exact3:area.LINKED_ONLY.exact3,fixed_only_exact3:area.FIXED_ONLY.exact3,difference_exact3:obs3,primary_one_sided_p:p3,exact3_two_sided_p:p3two,linked_only_exact2:area.LINKED_ONLY.exact2,fixed_only_exact2:area.FIXED_ONLY.exact2,difference_exact2:obs2,exact2_one_sided_p:p2,exact2_two_sided_p:p2two},common_count_performance:cc,anchor_contribution:{available:true,linked_only_exact3:anchorRows.filter(x=>x.hits===3),linked_only_exact3_anchor_hit:anchorRows.filter(x=>x.hits===3&&x.anchor_hit).length,linked_only_exact3_anchor_miss:anchorRows.filter(x=>x.hits===3&&!x.anchor_hit).length,linked_only_exact2:anchorRows.filter(x=>x.hits===2)},judgment,future_leakage:0,original_trio_orbit_final:'FAILED_NOT_SUPPORTED',official_protected_changes:0,EXP017:'NOT_CREATED'};
fs.writeFileSync(path.join(OUT,'P45_TRIO_ORBIT_DIVERGENCE_ATTRIBUTION_V1_RESULT_001.json'),JSON.stringify(result,null,2)+'\n');
const hdr=Object.keys(out[0]);fs.writeFileSync(path.join(OUT,'P45_TRIO_ORBIT_DIVERGENCE_ATTRIBUTION_V1_TRACE_001.csv'),hdr.join(',')+'\n'+out.map(o=>hdr.map(k=>o[k]).join(',')).join('\n')+'\n');console.log(JSON.stringify({area,cc,fixedSuccess,linkedSuccess,obs3,p3,p3two,obs2,p2,p2two,anchor:result.anchor_contribution,judgment},null,2));

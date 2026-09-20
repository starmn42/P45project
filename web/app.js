const $=id=>document.getElementById(id);
const esc=s=>String(s??"—").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const balls=(value,hits=[])=>`<div class="balls">${String(value).trim().split(/\s+/).map(n=>`<span class="ball ${hits.includes(Number(n))?"hit":""}">${esc(n)}</span>`).join("")}</div>`;
const ko={FROZEN:"동결",UNRESOLVED:"미해결",ACTIVE:"일시중단",NONE:"없음",PENDING:"결과 대기 중",AVAILABLE:"결과 확인됨",OUTCOME_RECORDED:"결과 반영 완료",READY_FOR_PREVIEW:"출격 준비",FAILED_NOT_SUPPORTED:"지지되지 않음",FAILED_NO_SELECTION_SIGNAL:"선택 신호 없음",PASS:"정상",FAIL:"오류",NO:"아니오",YES:"예"};
const kor=value=>ko[value]||value;
let currentData=null,activePreview=null;
function activatePage(name){setDrawer(false);document.querySelectorAll(".v1-page").forEach(x=>x.classList.toggle("active",x.id===name));document.querySelectorAll("[data-tab]").forEach(x=>x.classList.toggle("active",x.dataset.tab===name));scrollTo({top:0,left:0,behavior:"instant"})}
function tabs(){document.querySelectorAll("[data-tab]").forEach(a=>a.addEventListener("click",event=>{event.preventDefault();activatePage(a.dataset.tab);history.replaceState(null,"",a.getAttribute("href"))}));document.querySelectorAll("[data-home]").forEach(b=>b.addEventListener("click",()=>{activatePage("status");history.replaceState(null,"","#status")}))}
function trioCards(rootId,trios,anchors){$(rootId).innerHTML=trios.map((t,i)=>`<article class="lab-card trio-card"><span>세트 ${"ABC"[i]}</span>${balls(t)}${anchors?`<b class="anchor">기준번호 ${esc(anchors[i])}</b>`:""}<small>봉인 완료 · 수정 불가</small></article>`).join("")}
function homeSets(rootId,sets,winning=[]){$(rootId).innerHTML=sets.map((item,i)=>{const text=typeof item==="string"?item:item.numbers;const hit=typeof item==="string"?null:item.hits;return `<div class="home-set"><b>세트 ${"ABC"[i]}</b><strong>${String(text).trim().split(/\s+/).map(n=>`<span class="${winning.includes(Number(n))?"hit-number":""}">${esc(n)}</span>`).join(" · ")}</strong><small>${hit===null?"봉인":`${hit}/3${hit===3?" · 주적중":hit===2?" · 보조적중":""}`}</small></div>`}).join("")}
function renderResult(result){if(!result){$("resultOverview").hidden=true;return}$("resultOverview").hidden=false;const win=result.main.map(Number),rows=[...result.fixed.map(x=>["순수 고정",x]),...result.linked.map(x=>["직전연동",x])].map(([name,x])=>`<div><b>${name} ${esc(x.label)}</b><span>${String(x.numbers).trim().split(/\s+/).map(n=>`<i class="${win.includes(Number(n))?"hit-number":""}">${esc(n)}</i>`).join(" · ")}</span><strong>${x.hits}/3${x.hits===3?" · 주적중":x.hits===2?" · 보조적중":""}</strong></div>`).join("");$("resultRound").textContent=result.round;$("drawResultTitle").textContent=`${result.round}회 결과 요약`;$("winningNumbers").innerHTML=balls(result.main.join(" "),win);$("bonusNumber").textContent=result.bonus;$("drawDate").textContent=result.date;$("fixedPrimary").textContent=result.fixed_primary;$("fixedSupport").textContent=result.fixed_support;$("linkedPrimary").textContent=result.linked_primary;$("linkedSupport").textContent=result.linked_support;$("setResultRows").innerHTML=rows;$("resultDetailTitle").textContent=`${result.round}회 결과 상세`;$("resultCrumb").textContent=`${result.round}회 결과 상세`;$("detailWinningNumbers").innerHTML=balls(result.main.join(" "),win);$("detailBonusNumber").textContent=result.bonus;$("detailDrawDate").textContent=result.date;$("detailFixedPrimary").textContent=result.fixed_primary;$("detailFixedSupport").textContent=result.fixed_support;$("detailLinkedPrimary").textContent=result.linked_primary;$("detailLinkedSupport").textContent=result.linked_support;$("detailSetResultRows").innerHTML=rows}
function checkCard(label,value,detail=""){const pass=value===true||value==="PASS";return `<article class="lab-card integrity ${pass?"pass":"fail"}"><span>${esc(label)}</span><b>${pass?"정상":"오류"}</b><small>${esc(detail)}</small></article>`}
function formatDrawDateTime(targetRound,lastRound,lastDateStr){
 let date;
 if(lastDateStr&&targetRound&&lastRound){
  const diffWeeks=Number(targetRound)-Number(lastRound);
  const parts=String(lastDateStr).split("-").map(Number);
  date=new Date(parts[0],parts[1]-1,parts[2]);
  date.setDate(date.getDate()+(diffWeeks*7));
 }else{
  date=new Date(2026,8,19);
 }
 const y=date.getFullYear(),m=date.getMonth()+1,d=date.getDate();
 const day=["일","월","화","수","목","금","토"][date.getDay()];
 return `${y}년 ${m}월 ${d}일 (${day}) 오후 8시 35분`;
}
function render(data){
 currentData=data;const c=data.current,l=data.lifecycle,o=data.operation,s=data.seal,p=data.prospective,i=data.integrity;
 const ready=l.display_status==="READY_FOR_PREVIEW";$("mobileTarget").textContent=`${l.display_target}회 · ${kor(l.display_status)}`;$("targetRound").textContent=l.display_target;$("targetLabel").textContent=ready?"다음 미래검증 회차":"현재 미래검증 회차";$("completedRecord").textContent=l.completed_target?`${l.completed_target} 미래검증 정산 완료 기록`:"봉인 완료 · 결과 대기";$("canonicalLatest").textContent=data.canonical.latest;$("resultAvailability").textContent=ready?"출격 준비":kor(c.target_result_status);$("sealStatus").textContent=ready?"미봉인":s.verify==="PASS"?"봉인 정상":"봉인 오류";
 if($("drawScheduleRound"))$("drawScheduleRound").textContent=`${l.display_target}회 추첨`;
 if($("drawScheduleTime"))$("drawScheduleTime").textContent=formatDrawDateTime(l.display_target,data.latest_result?.round||data.canonical.latest,data.latest_result?.date);
 const action={WAITING_FOR_RESULT:"결과를 기다리세요",RECORD_OUTCOME:"이번 회차 결과를 반영하세요",PREVIEW_AND_SEAL_NEXT:"다음 회차를 생성하고 봉인하세요",WRITE_OPERATIONS_BLOCKED:"기록 작업 안전 차단"}[c.action]||c.action;$("primaryAction").textContent=action;$("primaryAction").classList.toggle("blocked",c.action==="WRITE_OPERATIONS_BLOCKED");
 $("officialEngine").textContent=kor(o.official_engine);$("noPick").textContent=kor(o.no_pick);$("discovery").textContent=o.draw_discovery_pause==="ACTIVE"?"일시중단":kor(o.draw_discovery_pause);$("latestExp").textContent=kor(o.latest_exp_status);$("verifiedSignal").textContent=kor(o.verified_independent_signal);
 renderResult(data.latest_result);homeSets("homeFixedCards",data.orbits.fixed.trios);homeSets("homeLinkedCards",data.orbits.linked.trios);$("nextPickTitle").textContent=`${l.display_target}회 추천 픽`;$("reviewSubtitle").textContent=`${data.latest_result?.round||data.canonical.latest}회 결과를 기준으로 추천픽 적중을 확인합니다.`
 trioCards("fixedCards",data.orbits.fixed.trios);trioCards("linkedCards",data.orbits.linked.trios,data.orbits.linked.anchors);$("commonCount").textContent=data.divergence.common_count;$("commonTrios").textContent=kor(data.divergence.common_trios);$("fixedOnly").textContent=data.divergence.fixed_only;$("linkedOnly").textContent=data.divergence.linked_only;$("reset").textContent=kor(data.divergence.reset);
 $("dispatchSealBadge").textContent=s.verify==="PASS"?"봉인 정상":"봉인 오류";$("sealTime").textContent=c.sealed_timestamp;$("sealDataSha").textContent=s.canonical_sha256;$("sealedSha").textContent=s.sha256;$("leakage").textContent=s.future_leakage;$("dispatchResult").textContent=kor(c.result_status);
 $("dispatchEyebrow").textContent="봉인된 신규회차";$("dispatchTitle").textContent=`${c.target}회 출격 상세`;$("dispatchCrumb").textContent=`${c.target}회 출격 상세`;
 $("completedRounds").textContent=p.completed_rounds;$("pFixed3").textContent=p.fixed_exact3;$("pLinked3").textContent=p.linked_exact3;$("pendingCount").textContent=p.pending_count;
 $("prospectiveRows").innerHTML=p.rows.map(r=>`<tr><td>${esc(r.target_round)}</td><td>${esc([r.fixed_A,r.fixed_B,r.fixed_C].join(" / "))}</td><td>${esc([r.linked_A,r.linked_B,r.linked_C].join(" / "))}</td><td>${esc(r.common_count)}</td><td>${esc(kor(r.reset_before_selection))}</td><td><b>${esc(kor(r.result_status))}</b></td><td>${esc(r.fixed_success)} / ${esc(r.linked_success)}</td><td>${esc(r.fixed_only_exact2_contribution)} / ${esc(r.linked_only_exact2_contribution)}</td><td>${r.selection_record_sha256===s.sha256?"정상":"완료 기록"}</td></tr>`).join("");
 document.querySelectorAll("#prospectiveRows td").forEach(cell=>{cell.dataset.label=document.querySelectorAll(".table-wrap th")[cell.cellIndex].textContent});
 const protectedPass=Object.values(i.protected).every(Boolean),officialPass=Object.values(i.official_protected).every(Boolean);$("integrityGrid").innerHTML=checkCard("데이터 읽기",data.canonical.read_status,"최신 회차 "+data.canonical.latest)+checkCard("KTS 무결성",i.kts_pass,i.kts_actual)+checkCard("봉인 무결성",s.verify,s.sha256)+checkCard("Fixed / Linked / KTS 보호",protectedPass,"V1 규칙")+checkCard("공식 영역 보호",officialPass,"상태 / 보고서 / DB")+checkCard("미래 데이터 누수",i.future_leakage===0,"0")+checkCard("기록 무결성",i.manifest_status,"미래검증");$("allChecks").textContent=i.all_pass?"전체 보호 점검 정상":"기록 작업 안전 차단";$("allChecks").classList.toggle("fail",!i.all_pass);$("statePath").textContent=i.state_path;$("logPath").textContent=i.log_path;$("sealedPath").textContent=i.sealed_path;$("writeStatus").textContent=i.write_status==="ALLOWED_WHEN_PRECONDITIONS_PASS"?"안전조건 충족 시에만 기록 가능":"기록 작업 안전 차단";
 $("autoUpdateStatus").textContent=data.auto_update?.status||"자동 업데이트 대기";$("showLastResult").textContent=`${data.latest_result?.round||data.canonical.latest}회 결과 보기`;$("showNextDispatch").textContent=`${l.display_target}회 출격 보기`;$("connection").textContent="연결 정상 · 오류 시 안전 차단";$("updated").textContent=`상태 확인 ${new Date().toLocaleTimeString("ko-KR")}`;$("previewNext").hidden=c.action!=="PREVIEW_AND_SEAL_NEXT";$("previewNext").textContent=`${l.next_target} 출격 미리보기`;if(c.action!=="PREVIEW_AND_SEAL_NEXT"){$("sealNext").hidden=true;$("previewPanel").hidden=true;activePreview=null}

}
async function load(){try{const r=await fetch("/api/status",{cache:"no-store"});const d=await r.json();if(!r.ok)throw Error(d.error||"상태를 읽지 못했습니다.");render(d)}catch(e){$("primaryAction").textContent="기록 작업 안전 차단";$("primaryAction").classList.add("blocked");$("connection").textContent="데이터 오류";$("updated").textContent=e.message}}
async function previewNext(){const r=await fetch("/api/prospective/preview",{cache:"no-store"});const d=await r.json();if(!r.ok||!d.ok)throw Error(d.error||"미리보기를 만들지 못했습니다.");activePreview=d.preview;$("previewTarget").textContent=activePreview.target;$("previewSource").textContent=activePreview.source_round;$("previewFixed").textContent=activePreview.fixed.map(x=>x.join(" ")).join(" / ");$("previewLinked").textContent=activePreview.linked.map(x=>x.join(" ")).join(" / ");$("previewAnchors").textContent=activePreview.anchors.join(" · ");$("previewProtocol").textContent="TRIO ORBIT V1 / "+String(currentData.integrity.kts_actual).slice(0,16)+"…";$("previewSha").textContent=activePreview.preview_sha256;$("previewGuard").textContent="미래누수 0 · 결정론 일치";$("previewPanel").hidden=false;$("sealNext").hidden=false}
async function sealNext(){if(!activePreview)throw Error("먼저 미리보기를 확인하세요.");const session=await fetch("/api/session",{cache:"no-store"}).then(r=>r.json());const r=await fetch("/api/prospective/seal",{method:"POST",headers:{"Content-Type":"application/json","X-P45-Token":session.token},body:JSON.stringify({preview_sha256:activePreview.preview_sha256})});const d=await r.json();if(!r.ok||!d.ok)throw Error(d.error||"봉인하지 못했습니다.");activePreview=null;await load()}
// Presentation-only mobile navigation; no API requests or lifecycle actions.
const mobileMenu=matchMedia("(max-width:980px)");
function setDrawer(open){
 const drawer=$("mainDrawer"),toggle=$("menuToggle"),backdrop=document.querySelector(".drawer-backdrop");
 const wasOpen=document.body.classList.contains("drawer-open");
 document.body.classList.toggle("drawer-open",open);
 toggle.setAttribute("aria-expanded",String(open));
 backdrop.hidden=!open;
 document.querySelector("main").inert=open;
 document.querySelector(".mobile-header").inert=open;
 if(open){drawer.setAttribute("role","dialog");drawer.setAttribute("aria-modal","true");document.querySelector(".drawer-close").focus()}
 else{drawer.removeAttribute("role");drawer.removeAttribute("aria-modal");if(wasOpen&&mobileMenu.matches)toggle.focus()}
}
$("menuToggle").addEventListener("click",()=>setDrawer(true));
document.querySelector(".drawer-close").addEventListener("click",()=>setDrawer(false));
document.querySelector(".drawer-backdrop").addEventListener("click",()=>setDrawer(false));
mobileMenu.addEventListener("change",()=>setDrawer(false));
document.addEventListener("keydown",event=>{
 if(!document.body.classList.contains("drawer-open"))return;
 if(event.key==="Escape"){setDrawer(false);return}
 if(event.key!=="Tab")return;
 const items=[...$("mainDrawer").querySelectorAll("button,a[href]")];
 const first=items[0],last=items[items.length-1];
 if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus()}
 else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus()}
});

tabs();$("showLastResult").addEventListener("click",()=>{activatePage("result-detail");history.replaceState(null,"","#result-detail")});$("showNextDispatch").addEventListener("click",()=>{activatePage("dispatch");history.replaceState(null,"","#dispatch")});$("previewNext").addEventListener("click",()=>previewNext().catch(e=>{$("primaryAction").textContent=e.message;$("primaryAction").classList.add("blocked")}));$("sealNext").addEventListener("click",()=>sealNext().catch(e=>{$("primaryAction").textContent=e.message;$("primaryAction").classList.add("blocked")}));load();
setInterval(()=>{if(!document.hidden)load()},60000);
document.addEventListener("visibilitychange",()=>{if(!document.hidden)load()});
window.addEventListener("focus",load);
if("serviceWorker" in navigator)navigator.serviceWorker.getRegistrations().then(registrations=>registrations.filter(registration=>[registration.active,registration.waiting,registration.installing].some(worker=>worker?.scriptURL.includes("/service-worker.js"))).forEach(registration=>registration.unregister())).catch(()=>{});





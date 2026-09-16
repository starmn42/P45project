const {chromium}=require('C:/Users/sung2/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=__dirname, shots=path.join(root,'screenshots');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1366,height:900},deviceScaleFactor:1});
 const errors=[],requests=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 page.on('request',r=>requests.push({method:r.method(),url:r.url()}));
 const response=await page.goto('http://127.0.0.1:8045/');assert.equal(response.status(),200);
 await page.waitForFunction(()=>document.querySelector('#nextPickTitle').textContent.includes('1241'));
 const api=await page.request.get('http://127.0.0.1:8045/api/status');assert.equal(api.status(),200);
 const state=await api.json();fs.writeFileSync(path.join(root,'status_after.json'),JSON.stringify(state,null,2));
 assert.equal(state.current.target,1241);assert.equal(state.integrity.future_leakage,0);assert.equal(state.integrity.all_pass,true);
 async function capture(name){
  await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:path.join(shots,name+'.png'),fullPage:true,animations:"disabled"});
  const measure=await page.evaluate(()=>{
   const w=document.documentElement.clientWidth;
   const visible=[...document.querySelectorAll('main *,.mobile-header *,.drawer *')].filter(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width&&r.height&&s.visibility!=='hidden'&&s.display!=='none'&&r.right>0&&r.left<w});
   const outside=visible.filter(e=>{const r=e.getBoundingClientRect();return r.left<-.5||r.right>w+.5}).map(e=>e.id||e.className||e.tagName);
   return {width:innerWidth,documentWidth:document.documentElement.scrollWidth,overflow:Math.max(0,document.documentElement.scrollWidth-w),outside,fonts:document.fonts.status};
  });checks.push({name,...measure});if(measure.outside.length)console.log(JSON.stringify({name,...measure}));assert.equal(measure.overflow,0,name+' horizontal overflow');assert.deepEqual(measure.outside,[],name+' outside viewport');
 }
 for(const w of [1366,1440,390,412,430]){await page.setViewportSize({width:w,height:w>980?900:844});await capture((w>980?'desktop_':'mobile_')+w)}
 await page.setViewportSize({width:390,height:844});await page.locator('#menuToggle').click();await capture('mobile_menu_390');
 await page.keyboard.press('Shift+Tab');assert.equal(await page.evaluate(()=>document.activeElement.dataset.tab),'system');
 await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.className),'drawer-close');
 await page.keyboard.press('Escape');assert.equal(await page.locator('#menuToggle').getAttribute('aria-expanded'),'false');
 await page.locator('#showNextDispatch').click();await capture('detail_1241_390');
 assert.equal(await page.locator('#dispatch .hit,#dispatch .hit-number').count(),0);assert.equal(await page.locator('#dispatchResult').textContent(),'결과 대기 중');
 for(const [id,trios] of [['fixedCards',state.orbits.fixed.trios],['linkedCards',state.orbits.linked.trios]])assert.deepEqual(await page.locator('#'+id+' .balls').allTextContents(),trios.map(s=>s.replace(/\s/g,'')));
 await page.locator('#dispatch [data-home]').click();await page.locator('#showLastResult').click();await capture('detail_1240_390');
 assert.equal(await page.locator('#detailWinningNumbers .hit').count(),6);assert.equal(await page.locator('#detailBonusNumber').textContent(),'27');
 for(const tab of ['prospective','system','status']){await page.locator('#menuToggle').click();await page.locator('.drawer [data-tab="'+tab+'"]').click();assert.equal(await page.locator('.v1-page.active').getAttribute('id'),tab);await capture(tab+'_390')}
 for(const w of [768,980,981,1366]){await page.setViewportSize({width:w,height:900});for(const tab of ['status','prospective','system']){if(w<=980)await page.locator('#menuToggle').click();await page.locator('.drawer [data-tab="'+tab+'"]').click();await capture(tab+'_'+w)}}
 assert.equal(await page.locator('[data-refresh]').count(),0);assert.equal(errors.length,0,JSON.stringify(errors));assert.equal(requests.filter(r=>r.method!=='GET').length,0);
 fs.writeFileSync(path.join(root,'browser_checks.json'),JSON.stringify({http:{home:response.status(),status:api.status()},errors,checks,requests,nonGetRequests:0,pendingHits:0,drawerFocusTrap:true,drawerEscape:true,approvedReference:'NOT_PROVIDED'},null,2));
 console.log(JSON.stringify({screenshots:checks.length,errors,overflow:checks.map(x=>[x.name,x.overflow])}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});



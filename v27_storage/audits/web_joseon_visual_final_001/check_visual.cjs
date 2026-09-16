const {chromium}=require('C:/Users/sung2/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const errors=[],checks={};page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 const r=await page.goto('http://127.0.0.1:8045/');checks.homeHttp=r.status();assert.equal(r.status(),200);
 await page.waitForFunction(()=>document.querySelector('#nextPickTitle').textContent.includes('1241'));
 checks.apiHttp=(await page.request.get('http://127.0.0.1:8045/api/status')).status();assert.equal(checks.apiHttp,200);
 await page.locator('#showNextDispatch').click();assert.equal(await page.locator('.v1-page.active').getAttribute('id'),'dispatch');checks.dispatch=true;
 await page.locator('#dispatch [data-home]').click();await page.locator('#showLastResult').click();assert.equal(await page.locator('.v1-page.active').getAttribute('id'),'result-detail');checks.result=true;
 for(const tab of ['prospective','system','status']){await page.locator('.drawer [data-tab="'+tab+'"]').click();assert.equal(await page.locator('.v1-page.active').getAttribute('id'),tab);checks[tab]=true}
 await page.screenshot({path:path.join(__dirname,'screenshots','desktop_1440.png'),fullPage:true,animations:'disabled'});
 checks.overflow={};
 for(const width of [390,412,430]){await page.setViewportSize({width,height:844});await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));checks.overflow[width]=await page.evaluate(()=>Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth));assert.equal(checks.overflow[width],0)}
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(__dirname,'screenshots','mobile_home_390.png'),fullPage:true,animations:'disabled'});
 await page.locator('#menuToggle').click();await page.screenshot({path:path.join(__dirname,'screenshots','mobile_menu_390.png'),fullPage:false,animations:'disabled'});
 await page.locator('.drawer [data-tab="system"]').click();assert.equal(await page.locator('.v1-page.active').getAttribute('id'),'system');checks.mobileMenu=true;
 assert.equal(errors.length,0,JSON.stringify(errors));checks.consoleErrors=errors;checks.screenshots=3;
 fs.writeFileSync(path.join(__dirname,'checks.json'),JSON.stringify(checks,null,2));console.log(JSON.stringify(checks));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

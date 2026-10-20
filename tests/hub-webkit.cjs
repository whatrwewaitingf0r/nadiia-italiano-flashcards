const {webkit}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path');
(async()=>{
 const browser=await webkit.launch({headless:true});
 const page=await browser.newPage({viewport:{width:375,height:812},isMobile:true,hasTouch:true});
 const errors=[],network=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
 const file=process.env.HUB_URL||'file://'+path.resolve(__dirname,'../index.html');
 await page.goto(file);
 const get=async key=>{await page.locator('#tab-'+key).click();await page.locator('#loading-'+key).waitFor({state:'hidden'});return await page.locator('#frame-'+key).contentFrame();};
 const carte=await get('carte');
 assert.equal(await carte.locator('#filter').inputValue(),'18-ott');
 assert.equal(await carte.locator('#filter option').first().innerText(),'18 ott');
 assert.equal(await carte.locator('#counter').innerText(),'1 / 100');
 assert.equal(await carte.locator('.back').evaluate(e=>getComputedStyle(e).visibility),'hidden');
 assert.equal(await carte.locator('.front').evaluate(e=>getComputedStyle(e).visibility),'visible');
 await page.screenshot({path:path.resolve(__dirname,'../.aitemp/hub-carte-mobile-v29.png'),animations:'disabled'});
 assert.ok((await carte.locator('#frontWord').innerText()).length>0);
 const result=await page.evaluate(()=>{
  const frame=document.getElementById('frame-carte');
  return frame.contentWindow.eval('({count:ALL.length,ru:ALL.some(c=>/[\\u0400-\\u04ff]/.test(JSON.stringify(c))),groups:groups.length})');
 });assert.equal(result.count,1673);assert.equal(result.ru,false);
 await carte.locator('#filter').selectOption('lisa-irregolari');
 assert.equal(await carte.locator('#direction').isDisabled(),true);
 await carte.locator('#flip').click();assert.equal(await carte.locator('.front').evaluate(e=>getComputedStyle(e).visibility),'hidden');assert.equal(await carte.locator('.back').evaluate(e=>getComputedStyle(e).visibility),'visible');assert.equal(await carte.locator('.back').evaluate(e=>getComputedStyle(e).transform),'none');assert.match(await carte.locator('#backWord').innerText(),/io/);
 const lisaState=await carte.locator('#frontWord').innerText();
 // Carte and Coppie remain embedded; drill links leave the hub entirely.
 await get('coppie');await get('carte');
 assert.equal(await carte.locator('#filter').inputValue(),'lisa-irregolari');
 assert.equal(await carte.locator('#frontWord').innerText(),lisaState);
 for(const [key,name] of Object.entries({articoli:'articoli-esercizi.html',aggettivi:'articoli-aggettivi.html',verbi:'verbi-tempi.html'})){
  await page.goto(file);await page.locator('#tab-'+key).click();
  await page.waitForURL(url=>url.pathname.endsWith('/'+name)&&url.search==='?v=48');
  assert.equal(await page.evaluate(()=>window===top),true);
  assert.ok((await page.locator('#phrase').innerText()).trim().length>5);
  assert.equal(await page.locator('a.back-link').getAttribute('href'),'index.html?v=48');
  assert.equal(await page.locator('html').evaluate(el=>el.scrollWidth<=innerWidth),true);
  await page.locator('a.back-link').click();await page.locator('#tab-carte').waitFor();
 }
 // Old shared hash links must also redirect to the standalone drill.
 await page.goto(file.split('#')[0]+'#aggettivi');
 await page.waitForURL(url=>url.pathname.endsWith('/articoli-aggettivi.html'));
 await page.locator('a.back-link').click();
 const currentCarte=await get('carte');
 await currentCarte.locator('a[href^="articoli-esercizi"]').click();
 await page.waitForURL(url=>url.pathname.endsWith('/articoli-esercizi.html'));
 await page.locator('a.back-link').click();
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await page.screenshot({path:path.resolve(__dirname,'../.aitemp/hub-mobile-v29.png'),animations:'disabled'});
 await page.setViewportSize({width:1040,height:850});await get('carte');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await page.screenshot({path:path.resolve(__dirname,'../.aitemp/hub-desktop-v29.png'),animations:'disabled'});
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({engine:'WebKit',...result,standaloneDrills:3,network:network.length,errors:errors.length,embeddedCardStatePreserved:true,mobileWidth:375}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

const {webkit}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path');
(async()=>{
 const browser=await webkit.launch({headless:true});
 const page=await browser.newPage({viewport:{width:375,height:812},isMobile:true,hasTouch:true});
 const errors=[],network=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
 const file=process.env.HUB_URL||'file://'+path.resolve(__dirname,'../index.html');
 await page.goto(file);
 const get=async key=>{await page.locator('#tab-'+key).click();await page.locator('#loading-'+key).waitFor({state:'hidden'});return await page.locator('#frame-'+key).contentFrame();};
 const carte=await get('carte');
 assert.equal(await carte.locator('#filter').inputValue(),'chiara-23-sett');
 assert.match(await carte.locator('#filter option').first().innerText(),/Chiara/);
 assert.equal(await carte.locator('#counter').innerText(),'1 / 44');
 assert.equal(await carte.locator('.back').evaluate(e=>getComputedStyle(e).visibility),'hidden');
 assert.equal(await carte.locator('.front').evaluate(e=>getComputedStyle(e).visibility),'visible');
 await page.screenshot({path:path.resolve(__dirname,'../.aitemp/hub-carte-mobile-v29.png'),animations:'disabled'});
 assert.ok((await carte.locator('#frontWord').innerText()).length>0);
 const result=await page.evaluate(()=>{
  const frame=document.getElementById('frame-carte');
  return frame.contentWindow.eval('({count:ALL.length,ru:ALL.some(c=>/[\\u0400-\\u04ff]/.test(JSON.stringify(c))),groups:groups.length})');
 });assert.equal(result.count,1377);assert.equal(result.ru,false);
 await carte.locator('#filter').selectOption('lisa-irregolari');
 assert.equal(await carte.locator('#direction').isDisabled(),true);
 await carte.locator('#flip').click();assert.equal(await carte.locator('.front').evaluate(e=>getComputedStyle(e).visibility),'hidden');assert.equal(await carte.locator('.back').evaluate(e=>getComputedStyle(e).visibility),'visible');assert.equal(await carte.locator('.back').evaluate(e=>getComputedStyle(e).transform),'none');assert.match(await carte.locator('#backWord').innerText(),/io/);
 const lisaState=await carte.locator('#frontWord').innerText();
 for(const key of ['articoli','aggettivi','verbi']){
  const frame=await get(key);
  assert.ok((await frame.locator('#phrase').innerText()).trim().length>5);
  for(const mode of ['a','b']){
   await frame.locator('#mode-'+mode).click();
   const checked=await page.evaluate(({key,mode})=>document.getElementById('frame-'+key).contentWindow.eval(`(()=>{let done=0;mode=${JSON.stringify(mode)};order=ITEMS.slice();pos=0;for(let i=0;i<order.length;i++){render();const item=order[pos],p=document.getElementById('phrase');const word=item.word||item.before||item.noun.sg;if(!p.textContent.includes(word))throw Error('Blank noun/sentence '+i+' '+p.textContent);if(!p.getBoundingClientRect().height)throw Error('Invisible phrase');submit(${key==='aggettivi'?'phrase(item)':key==='articoli'&&mode==='b'?'join(item.answer,item.word)':'item.answer'});if(document.getElementById('next').disabled)throw Error('Answer rejected '+i);document.getElementById('next').click();done++;}return done})()`),{key,mode});
   assert.equal(checked,key==='articoli'?80:key==='aggettivi'?1040:900);
  }
  assert.equal(await frame.locator('html').evaluate(el=>el.scrollWidth<=innerWidth),true);
 }
 await get('carte');assert.equal(await carte.locator('#filter').inputValue(),'lisa-irregolari');assert.equal(await carte.locator('#frontWord').innerText(),lisaState);assert.equal(await carte.locator('#scene').evaluate(el=>el.classList.contains('flipped')),true);
 // Embedded app links must switch the hub, not navigate away or fetch companion files.
 await carte.locator('a[href^="articoli-esercizi"]').click();assert.equal(await page.locator('#tab-articoli').getAttribute('aria-selected'),'true');
 await page.locator('#tab-articoli').focus();await page.keyboard.press('ArrowRight');assert.equal(await page.locator('#tab-aggettivi').getAttribute('aria-selected'),'true');
 await page.keyboard.press('Home');assert.equal(await page.locator('#tab-carte').getAttribute('aria-selected'),'true');
 await page.keyboard.press('End');assert.equal(await page.locator('#tab-verbi').getAttribute('aria-selected'),'true');
 const verbi=await get('verbi');await verbi.locator('#shuffle').click();
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await page.screenshot({path:path.resolve(__dirname,'../.aitemp/hub-mobile-v29.png'),animations:'disabled'});
 await page.setViewportSize({width:1040,height:850});await get('carte');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await page.screenshot({path:path.resolve(__dirname,'../.aitemp/hub-desktop-v29.png'),animations:'disabled'});
 assert.deepEqual(errors,[]);assert.equal(network.length,process.env.HUB_URL?1:0);
 console.log(JSON.stringify({engine:'WebKit',...result,drillPrompts:4040,network:network.length,errors:errors.length,statePreserved:true,mobileWidth:375}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

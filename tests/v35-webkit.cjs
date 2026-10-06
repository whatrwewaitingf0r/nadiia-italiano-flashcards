// Exercise actual mobile WebKit DOM/text, not just data or a stub renderer.
const {webkit}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path');
(async()=>{
 const browser=await webkit.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:375,height:812},isMobile:true,hasTouch:true});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const url=process.env.V35_HUB_URL||'file://'+path.resolve(__dirname,'../index.html');
  await page.goto(url+'#lettura');
  assert.deepEqual(await page.locator('[role=tab]').evaluateAll(ns=>ns.map(n=>n.dataset.app)),['carte','articoli','aggettivi','verbi']);
  assert.equal(await page.locator('#tab-lettura,#panel-lettura,#tab-parole-2,#panel-parole-2').count(),0);
  assert.equal(await page.locator('#tab-carte').getAttribute('aria-selected'),'true');
  await page.locator('#loading-carte').waitFor({state:'hidden'});
  const frame=await (await page.locator('#frame-carte').elementHandle()).contentFrame();
  assert.equal(await frame.locator('#filter').inputValue(),'chiara-23-sett');
  const options=await frame.locator('#filter option').evaluateAll(os=>os.map(o=>o.value));
  assert(options[0].startsWith('chiara-'));assert(!options.includes('liam-lettura'));
  assert.equal(await frame.evaluate(()=>ALL.length),1377);
  assert.equal(await frame.evaluate(()=>ALL.filter(c=>c.reading).length),0);
  let checked=0;
  for(const [key,count] of [['streghe-it-en',101],['streghe-en-it',101],['100parole-3',100]]){
   await frame.locator('#filter').selectOption(key);
   assert.equal(await frame.locator('#counter').innerText(),'1 / '+count);
   const fixed=key.startsWith('streghe');
   assert.equal(await frame.locator('#direction').isDisabled(),fixed);
   assert.equal(await frame.locator('#dirText').innerText(),key==='streghe-en-it'?'EN→IT':'IT→EN');
   const rendered=await frame.evaluate(()=>{
    const result=[];
    for(let i=0;i<pool.length;i++){index=i;render();result.push({it:pool[i].it,en:pool[i].other,direction:pool[i].direction,front:document.getElementById('frontWord').textContent,back:document.getElementById('backWord').textContent});}
    return result;
   });
   for(const c of rendered){assert.equal(c.front,key==='streghe-en-it'?c.en:c.it);assert.equal(c.back,key==='streghe-en-it'?c.it:c.en);checked++;}
   if(!fixed){
    const it=await frame.locator('#frontWord').innerText(),en=await frame.locator('#backWord').textContent();
    await frame.locator('#direction').tap();
    assert.equal(await frame.locator('#frontWord').innerText(),en);assert.equal(await frame.locator('#backWord').textContent(),it);
    assert.equal(await frame.locator('#dirText').innerText(),'EN→IT');
    await frame.locator('#direction').dispatchEvent('click',{bubbles:true,cancelable:true,detail:1});
    assert.equal(await frame.locator('#dirText').innerText(),'EN→IT','compatibility click must not undo touch reversal');
    await frame.locator('#flip').tap();assert.equal(await frame.locator('.back').evaluate(e=>getComputedStyle(e).visibility),'visible');
   }else{
    await frame.locator('#flip').tap();assert.equal(await frame.locator('.back').evaluate(e=>getComputedStyle(e).visibility),'visible');
   }
  }
  await frame.locator('#filter').selectOption('100parole-2');assert.equal(await frame.locator('#counter').innerText(),'1 / 100');assert.equal(await frame.locator('#direction').isEnabled(),true);
  await frame.locator('#filter').selectOption('ref-100-parole');assert.equal(await frame.locator('#counter').innerText(),'1 / 100');
  await frame.locator('#filter').selectOption('streghe-en-it');
  await page.screenshot({path:path.resolve(__dirname,'../.aitemp/streghe-v35/mobile.png'),animations:'disabled'});
  await page.setViewportSize({width:1040,height:850});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  await page.screenshot({path:path.resolve(__dirname,'../.aitemp/streghe-v35/desktop.png'),animations:'disabled'});
  for(const old of ['lettura','parole-2']){
   await page.evaluate(key=>location.hash=key,old);assert.equal(await page.locator('#tab-carte').getAttribute('aria-selected'),'true');
  }
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({engine:'WebKit',checkedNewCards:checked,parole3Directions:true,stregheSeparateFixedDecks:true,removedTabs:true,errors}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});

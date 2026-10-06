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
  assert.equal(await page.locator('.tabs').evaluate(el=>el.scrollWidth<=el.clientWidth),true,'All four tabs must fit on mobile without clipping');
  assert.equal(await page.locator('#tab-carte').getAttribute('aria-selected'),'true');
  await page.locator('#loading-carte').waitFor({state:'hidden'});
  const frame=await (await page.locator('#frame-carte').elementHandle()).contentFrame();
  assert.equal(await frame.locator('#filter').inputValue(),'chiara-23-sett');
  const options=await frame.locator('#filter option').evaluateAll(os=>os.map(o=>o.value));
  assert(options[0].startsWith('chiara-'));assert(!options.includes('liam-lettura'));
  assert.deepEqual(await frame.locator('#filter option').evaluateAll(os=>os.filter(o=>o.value.startsWith('streghe')).map(o=>({value:o.value,label:o.textContent}))),[{value:'streghe',label:'Streghe'}]);
  assert.equal(await frame.evaluate(()=>ALL.length),1276);
  assert.equal(await frame.evaluate(()=>ALL.filter(c=>c.reading).length),0);
  let checked=0;
  for(const [key,count] of [['streghe',101],['100parole-3',100]]){
   await frame.locator('#filter').selectOption(key);
   assert.equal(await frame.locator('#counter').innerText(),'1 / '+count);
   assert.equal(await frame.locator('#direction').isEnabled(),true);
   assert.equal(await frame.locator('#dirText').innerText(),'IT→EN');
   const rendered=await frame.evaluate(()=>{
    const result=[];
    for(let i=0;i<pool.length;i++){index=i;render();result.push({it:pool[i].it,en:pool[i].other,direction:pool[i].direction,front:document.getElementById('frontWord').textContent,back:document.getElementById('backWord').textContent});}
    return result;
   });
   for(const c of rendered){assert.equal(c.front,c.it);assert.equal(c.back,c.en);assert.equal(c.direction,undefined);checked++;}
    const it=await frame.locator('#frontWord').innerText(),en=await frame.locator('#backWord').textContent();
    await frame.locator('#direction').tap();
    assert.equal(await frame.locator('#frontWord').innerText(),en);assert.equal(await frame.locator('#backWord').textContent(),it);
    assert.equal(await frame.locator('#dirText').innerText(),'EN→IT');
    await frame.locator('#direction').dispatchEvent('click',{bubbles:true,cancelable:true,detail:1});
    assert.equal(await frame.locator('#dirText').innerText(),'EN→IT','compatibility click must not undo touch reversal');
    await frame.locator('#flip').tap();assert.equal(await frame.locator('.back').evaluate(e=>getComputedStyle(e).visibility),'visible');
    const reversed=await frame.evaluate(()=>{
     const result=[];
     for(let i=0;i<pool.length;i++){index=i;render();result.push({it:pool[i].it,en:pool[i].other,front:document.getElementById('frontWord').textContent,back:document.getElementById('backWord').textContent});}
     return result;
    });
    for(const c of reversed){assert.equal(c.front,c.en);assert.equal(c.back,c.it);checked++;}
    for(const id of ['next','prev','shuffle']){
     await frame.locator('#'+id).tap();
     assert.equal(await frame.locator('#dirText').innerText(),'EN→IT','Direction persists after '+id);
     assert.equal(await frame.evaluate(()=>document.getElementById('frontWord').textContent===pool[index].other&&document.getElementById('backWord').textContent===pool[index].it),true);
    }
    await frame.locator('#direction').tap();assert.equal(await frame.locator('#dirText').innerText(),'IT→EN');
    await frame.evaluate(()=>lastDirectionTouch=0);
    await frame.locator('#direction').click();assert.equal(await frame.locator('#dirText').innerText(),'EN→IT');
    await frame.locator('#direction').focus();await page.keyboard.press('Enter');assert.equal(await frame.locator('#dirText').innerText(),'IT→EN');
  }
  await frame.locator('#filter').selectOption('100parole-2');assert.equal(await frame.locator('#counter').innerText(),'1 / 100');assert.equal(await frame.locator('#direction').isEnabled(),true);
  await frame.locator('#filter').selectOption('ref-100-parole');assert.equal(await frame.locator('#counter').innerText(),'1 / 100');
  await frame.locator('#filter').selectOption('streghe');
  await page.screenshot({path:path.resolve(__dirname,'../.aitemp/streghe-v37/mobile.png'),animations:'disabled'});
  await page.setViewportSize({width:1040,height:850});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  await page.screenshot({path:path.resolve(__dirname,'../.aitemp/streghe-v37/desktop.png'),animations:'disabled'});
  for(const old of ['lettura','parole-2']){
   await page.evaluate(key=>location.hash=key,old);assert.equal(await page.locator('#tab-carte').getAttribute('aria-selected'),'true');
  }
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({engine:'WebKit',checkedCardDirections:checked,parole3Directions:true,stregheSingleReversibleDeck:true,removedTabs:true,errors}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});

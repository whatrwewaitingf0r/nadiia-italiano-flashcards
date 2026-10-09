// Render every card in the single mixed lesson through the actual Carte iframe.
const {webkit}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path');
(async()=>{
 const browser=await webkit.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:375,height:812},isMobile:true,hasTouch:true});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const url=process.env.LESSON_7_OTT_URL||'file://'+path.resolve(__dirname,'../index.html');
  await page.goto(url+'#carte');
  await page.locator('#loading-carte').waitFor({state:'hidden'});
  assert.deepEqual(await page.locator('[role=tab]').evaluateAll(ns=>ns.map(n=>n.dataset.app)),['carte','articoli','aggettivi','verbi']);
  assert.equal(await page.locator('.tabs').evaluate(el=>el.scrollWidth<=el.clientWidth),true);
  const frame=await (await page.locator('#frame-carte').elementHandle()).contentFrame();
  assert.equal(await frame.locator('#filter').inputValue(),'7-ott');
  const options=await frame.locator('#filter option').evaluateAll(os=>os.map(o=>({value:o.value,label:o.textContent})));
  assert.deepEqual(options[0],{value:'7-ott',label:'7 ott'});
  assert.deepEqual(options.filter(o=>o.value.startsWith('7-ott')),[{value:'7-ott',label:'7 ott'}]);
  await frame.locator('#filter').selectOption('7-ott');
  assert.equal(await frame.locator('#counter').innerText(),'1 / 48');
  assert.equal(await frame.locator('#dirText').innerText(),'IT→EN');
  assert.equal(await frame.locator('#direction').isEnabled(),true);
  const lessonOrder=await frame.evaluate(()=>ALL.filter(c=>c.group==='7 ott').map(c=>c.it));
  assert.equal(await frame.locator('#frontWord').innerText(),'un panino con prosciutto e formaggio');
  assert.deepEqual(await frame.evaluate(()=>pool.map(c=>c.it)),lessonOrder);
  const members=await frame.evaluate(()=>pool.map(c=>c.it).sort());
  assert.equal(new Set(members).size,48);
  assert(members.includes('questo')&&members.includes('il bar')&&members.includes('un panino con prosciutto e formaggio'));
  let checked=0;
  async function verifyAll(reversed){
   const renders=await frame.evaluate(()=>pool.map((c,i)=>{index=i;render();return {it:c.it,other:c.other,group:c.group,
    front:document.getElementById('frontWord').textContent,back:document.getElementById('backWord').textContent,
    note:document.getElementById('frontNote').textContent,
    fits:document.getElementById('frontWord').scrollHeight<=document.getElementById('frontWord').clientHeight};}));
   for(const c of renders){
    assert.equal(c.group,'7 ott');assert.equal(c.note,'7 ott');
    assert.equal(c.front,reversed?c.other:c.it);assert.equal(c.back,reversed?c.it:c.other);
    assert(!/[\u0400-\u04ff]/.test(c.front+c.back));assert(c.fits,c.front);checked++;
   }
  }
  await verifyAll(false);
  const it=await frame.locator('#frontWord').innerText(),en=await frame.locator('#backWord').textContent();
  await frame.locator('#direction').tap();
  assert.equal(await frame.locator('#dirText').innerText(),'EN→IT');
  assert.equal(await frame.locator('#frontWord').innerText(),en);assert.equal(await frame.locator('#backWord').textContent(),it);
  await frame.locator('#direction').dispatchEvent('click',{bubbles:true,cancelable:true,detail:1});
  assert.equal(await frame.locator('#dirText').innerText(),'EN→IT');
  await verifyAll(true);
  await frame.locator('#flip').tap();assert.equal(await frame.locator('.back').evaluate(e=>getComputedStyle(e).visibility),'visible');
  assert.equal(await frame.locator('#shuffle').isEnabled(),false);
  for(const id of ['next','prev']){
   await frame.locator('#'+id).tap();assert.equal(await frame.locator('#dirText').innerText(),'EN→IT');
   assert.deepEqual(await frame.evaluate(()=>pool.map(c=>c.it)),lessonOrder);
  }
  await frame.evaluate(()=>{shufflePool();render();});
  assert.deepEqual(await frame.evaluate(()=>pool.map(c=>c.it)),lessonOrder);
  await page.locator('#tab-verbi').tap();await page.locator('#tab-carte').tap();
  assert.equal(await frame.locator('#filter').inputValue(),'7-ott');
  assert.equal(await frame.locator('#dirText').innerText(),'EN→IT');
  await frame.locator('#direction').tap();assert.equal(await frame.locator('#dirText').innerText(),'IT→EN');
  for(const [key,count] of [['streghe',101],['verbi-forme',168],['ref-100-parole',100],['100parole-2',100],['100parole-3',100]]){
   await frame.locator('#filter').selectOption(key);assert.equal(await frame.locator('#counter').innerText(),'1 / '+count);
  }
  await frame.locator('#filter').selectOption('7-ott');
  assert.deepEqual(await frame.evaluate(()=>pool.map(c=>c.it)),lessonOrder);
  // Even a global shuffle must keep the entire new lesson first and in sheet order.
  for(let n=0;n<5;n++){
   await frame.evaluate(()=>{pool=ALL.slice();shufflePool();});
   assert.deepEqual(await frame.evaluate(()=>pool.slice(0,48).map(c=>c.it)),lessonOrder);
   assert.equal(await frame.evaluate(()=>pool.slice(48).some(c=>c.group==='7 ott')),false);
  }
  await frame.locator('#filter').selectOption('7-ott');
  await frame.evaluate(()=>{index=pool.findIndex(c=>c.it==='un panino con prosciutto e formaggio');render();});
  await page.screenshot({path:'/tmp/nadiia-7-ott-v40-mobile.png',animations:'disabled'});
  await page.reload();
  await page.locator('#loading-carte').waitFor({state:'hidden'});
  const reloaded=await (await page.locator('#frame-carte').elementHandle()).contentFrame();
  assert.equal(await reloaded.locator('#filter').inputValue(),'7-ott');
  assert.deepEqual(await reloaded.evaluate(()=>pool.map(c=>c.it)),lessonOrder);
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({engine:'mobile WebKit',lessonCards:48,checkedDirections:checked,oneMixedDeck:true,lessonFirst:true,stableLessonOrder:true,onlyFourTabs:true,errors}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});

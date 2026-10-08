// Actual mobile WebKit rendering/touch coverage of every new verb form, both directions.
const {webkit}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path');
(async()=>{
 const browser=await webkit.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:375,height:812},isMobile:true,hasTouch:true});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const url=process.env.VERBI_FORME_URL||'file://'+path.resolve(__dirname,'../index.html');
  await page.goto(url+'#carte');
  await page.locator('#loading-carte').waitFor({state:'hidden'});
  assert.deepEqual(await page.locator('[role=tab]').evaluateAll(ns=>ns.map(n=>n.dataset.app)),['carte','articoli','aggettivi','verbi']);
  assert.equal(await page.locator('.tabs').evaluate(el=>el.scrollWidth<=el.clientWidth),true);
  const frame=await (await page.locator('#frame-carte').elementHandle()).contentFrame();
  assert.equal(await frame.locator('#filter').inputValue(),'chiara-23-sett');
  const options=await frame.locator('#filter option').evaluateAll(os=>os.map(o=>({value:o.value,label:o.textContent})));
  assert(options[0].value.startsWith('chiara-'));
  assert.deepEqual(options.filter(o=>o.value.startsWith('verbi-forme')),[{value:'verbi-forme',label:'Verbi · forme'}]);
  await frame.locator('#filter').selectOption('verbi-forme');
  assert.equal(await frame.locator('#counter').innerText(),'1 / 168');
  assert.equal(await frame.locator('#dirText').innerText(),'IT→EN');
  assert.equal(await frame.locator('#direction').isEnabled(),true);
  let checked=0;
  async function verifyAll(reversed){
   const renders=await frame.evaluate(()=>pool.map((c,i)=>{index=i;render();return {it:c.it,other:c.other,tense:c.tense,front:document.getElementById('frontWord').textContent,back:document.getElementById('backWord').textContent};}));
   for(const c of renders){
    assert.equal(c.front,reversed?c.other:c.it);assert.equal(c.back,reversed?c.it:c.other);
    assert(c.other.startsWith(c.tense+' · '));assert(!/[\u0400-\u04ff]/.test(c.front+c.back));checked++;
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
  for(const id of ['next','prev','shuffle']){
   await frame.locator('#'+id).tap();assert.equal(await frame.locator('#dirText').innerText(),'EN→IT');
   assert.equal(await frame.evaluate(()=>document.getElementById('frontWord').textContent===pool[index].other),true);
  }
  await page.locator('#tab-verbi').tap();await page.locator('#tab-carte').tap();
  assert.equal(await frame.locator('#filter').inputValue(),'verbi-forme');
  assert.equal(await frame.locator('#dirText').innerText(),'EN→IT');
  await frame.locator('#direction').tap();assert.equal(await frame.locator('#dirText').innerText(),'IT→EN');
  for(const [key,count] of [['streghe',101],['ref-100-parole',100],['100parole-2',100],['100parole-3',100]]){
   await frame.locator('#filter').selectOption(key);assert.equal(await frame.locator('#counter').innerText(),'1 / '+count);
  }
  await frame.locator('#filter').selectOption('verbi-forme');
  await frame.evaluate(()=>{index=pool.findIndex(c=>c.it==='io vorrei');render();});
  await page.screenshot({path:'/tmp/nadiia-verbi-v38-mobile.png',animations:'disabled'});
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({engine:'mobile WebKit',verbForms:168,checkedDirections:checked,oneDeck:true,chiaraFirst:true,onlyFourTabs:true,errors}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});

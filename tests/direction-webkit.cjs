// Regression: a real mobile WebKit tap must reverse the second 100-word deck once.
const {webkit}=require('playwright');
const assert=require('node:assert/strict'),path=require('node:path');
(async()=>{
 const browser=await webkit.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:375,height:812},isMobile:true,hasTouch:true});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const url=process.env.DIRECTION_URL||'file://'+path.resolve(__dirname,'../index.html');
  await page.goto(url+'#carte');
  await page.locator('#loading-carte').waitFor({state:'hidden'});
  const app=await (await page.locator('#frame-carte').elementHandle()).contentFrame();
  await app.locator('#filter').selectOption('100parole-2');
  await app.evaluate(()=>{index=pool.findIndex(c=>c.it==='politico');if(index<0)throw Error('politico missing');render();});
  const button=app.locator('#direction');
  console.log('Before tap:',await button.evaluate(el=>({disabled:el.disabled,text:el.innerText,width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height,pointerEvents:getComputedStyle(el).pointerEvents})));
  assert.equal(await app.locator('#frontWord').innerText(),'politico');
  assert.equal(await app.locator('#backWord').textContent(),'political');
  assert.equal(await button.isEnabled(),true,'100 parole 2 direction toggle must not be disabled');
  const box=await button.boundingBox();assert(box.width>=44&&box.height>=44,'44px tap target');
  assert.equal(await button.evaluate(el=>{const r=el.getBoundingClientRect();return el.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2));}),true,'No overlay intercepts the tap');
  await app.evaluate(()=>{window.directionBubbles=[];for(const type of ['touchstart','touchend','click'])document.addEventListener(type,()=>directionBubbles.push(type));});
  await button.tap();
  assert.equal(await app.locator('#dirText').innerText(),'EN→IT');
  assert.equal(await app.locator('#frontWord').innerText(),'political');
  assert.equal(await app.locator('#backWord').textContent(),'politico');
  assert.equal(await app.locator('#scene').evaluate(el=>el.classList.contains('flipped')),false);
  // A compatibility click after touchend must not undo that tap.
  await button.dispatchEvent('click',{bubbles:true,cancelable:true,detail:1});
  assert.equal(await app.locator('#dirText').innerText(),'EN→IT');
  assert.deepEqual(await app.evaluate(()=>directionBubbles),[],'Direction events must not reach a parent handler');
  await button.tap();assert.equal(await app.locator('#dirText').innerText(),'IT→EN');
  await button.focus();await page.keyboard.press('Enter');
  assert.equal(await app.locator('#dirText').innerText(),'EN→IT');
  assert.equal(await app.locator('#scene').evaluate(el=>el.classList.contains('flipped')),false,'Enter on direction must not flip the card');
  // Mouse/desktop clicks still work, independently of touch timestamps.
  await app.evaluate(()=>lastDirectionTouch=0);
  await button.click();assert.equal(await app.locator('#dirText').innerText(),'IT→EN');
  await app.locator('#flip').tap();assert.equal(await app.locator('#scene').evaluate(el=>el.classList.contains('flipped')),true);
  for(const deck of ['lisa-irregolari','chiara-23-sett','grammar-verbi']){
   await app.locator('#filter').selectOption(deck);assert.equal(await button.isDisabled(),true,deck+' retains its structured-card direction lock');
  }
  await app.locator('#filter').selectOption('100parole-2');assert.equal(await button.isEnabled(),true);
  await button.tap();assert.equal(await app.locator('#dirText').innerText(),'EN→IT');
  await page.locator('#tab-verbi').tap();await page.locator('#tab-carte').tap();
  assert.equal(await app.locator('#dirText').innerText(),'EN→IT','Hub preserves reversed deck state');
  assert.equal(await app.evaluate(()=>ALL.length),1276);
  assert.equal(await app.evaluate(()=>ALL.filter(c=>c.group==='100 parole 2').length),100);
  assert.equal(await app.evaluate(()=>ALL.filter(c=>['Grammatica · articoli','Grammatica · concordanza'].includes(c.group)||(c.tags||[]).includes('lesson5')).length),0);
  assert.deepEqual(errors,[]);
  // Standalone file shares the same tap behavior, not only the hub iframe.
  if(!process.env.DIRECTION_URL){
   await page.goto('file://'+path.resolve(__dirname,'../italiano-flashcards.html')+'#100parole-2');
   await page.locator('#direction').tap();assert.equal(await page.locator('#dirText').innerText(),'EN→IT');
  }
  console.log('PASS: mobile WebKit hub and standalone tap, touch/click dedup, 44px hit target, parent isolation, keyboard/mouse, preserved decks and tab state; no page errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

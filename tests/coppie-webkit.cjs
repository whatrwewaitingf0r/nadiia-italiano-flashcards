const {webkit}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs');
(async()=>{
 const browser=await webkit.launch({headless:true});
 const shots='/tmp/nadiia-v44-qa';fs.mkdirSync(shots,{recursive:true});
 for(const width of [320,375,1040]){
  const page=await browser.newPage({viewport:{width,height:850},isMobile:width<800,hasTouch:true});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto(process.env.HUB_URL||'file://'+path.resolve(__dirname,'../index.html'));
  await page.locator('#loading-carte').waitFor({state:'hidden'});
  assert.equal(await page.locator('[role=tab]').count(),5);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  for(const tab of await page.locator('[role=tab]').all()){
   const box=await tab.boundingBox();assert(box.height>=44);assert(box.x>=0&&box.x+box.width<=width);
   assert.equal(await tab.evaluate(e=>e.scrollWidth<=e.clientWidth),true,'unclipped tab label');
  }
  const carte=page.frameLocator('#frame-carte');
  assert.equal(await carte.locator('#filter').inputValue(),'18-ott');
  assert.equal(await carte.locator('#filter option').first().innerText(),'18 ott');
  assert.equal(await carte.locator('#counter').innerText(),'1 / 81');
  await carte.locator('a.coppie-link').click();
  await page.locator('#loading-coppie').waitFor({state:'hidden'});
  assert.equal(await page.locator('#tab-coppie').getAttribute('aria-selected'),'true');
  assert.match(await page.locator('#frame-coppie').getAttribute('src'),/coppie\.html\?v=44$/);
  const coppie=page.frameLocator('#frame-coppie');
  assert.equal(await coppie.locator('#english button').count(),5);
  assert.equal(await coppie.locator('#clock').innerText(),'Nessuna fretta');
  assert.equal(await coppie.locator('input:checked').inputValue(),'18-ott');
  await coppie.locator('summary').click();
  await coppie.locator('input[value="14-ott"]').check();
  await coppie.locator('input[value="7-ott"]').check();
  await coppie.locator('input[value="18-ott"]').uncheck();
  assert.equal(await coppie.locator('input:checked').count(),2);
  await coppie.locator('summary').click();
  assert.equal(await coppie.locator('html').evaluate(e=>e.scrollWidth<=innerWidth),true);
  const left=coppie.locator('#english button').first(),id=await left.getAttribute('data-pair');
  const wrong=coppie.locator(`#italian button:not([data-pair="${id}"])`).first();
  await left.click();await wrong.click();
  assert.match(await left.getAttribute('class'),/wrong/);
  await page.waitForFunction(()=>!document.getElementById('frame-coppie').contentDocument.querySelector('.wrong'));
  await left.click();await coppie.locator(`#italian button[data-pair="${id}"]`).click();
  assert.equal(await left.isDisabled(),true);assert.match(await left.getAttribute('class'),/matched/);
  await page.screenshot({path:path.join(shots,'coppie-'+width+'.png')});
  await page.locator('#tab-carte').click();await page.locator('#tab-coppie').click();
  assert.equal(await coppie.locator('input:checked').count(),2,'preserve selected decks when switching tabs');
  await coppie.locator('header a').click();
  assert.equal(await page.locator('#tab-carte').getAttribute('aria-selected'),'true','back link switches hub, not nested navigation');
  await page.locator('#tab-carte').focus();await page.keyboard.press('End');
  assert.equal(await page.locator('#tab-coppie').getAttribute('aria-selected'),'true');
  for(const key of ['articoli','aggettivi','verbi']){
   await page.locator('#tab-'+key).click();await page.locator('#loading-'+key).waitFor({state:'hidden'});
   assert((await page.frameLocator('#frame-'+key).locator('#phrase').innerText()).trim().length>0);
  }
  assert.deepEqual(errors,[]);await page.close();
 }
 await browser.close();console.log('PASS: WebKit 320/375/1040px, five unclipped 44px tabs, default Carte 18 ott, embedded Coppie, multi-deck inputs, shuffle/mismatch/lock, state retained, back link, keyboard and all other tabs.');
})().catch(error=>{console.error(error);process.exitCode=1});

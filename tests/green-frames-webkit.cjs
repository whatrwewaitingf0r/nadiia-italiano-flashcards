const {webkit}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path');
const apps={articoli:'articoli-esercizi.html',aggettivi:'articoli-aggettivi.html',verbi:'verbi-tempi.html'};
(async()=>{
 const browser=await webkit.launch({headless:true});
 try {
 const page=await browser.newPage({viewport:{width:375,height:812},isMobile:true,hasTouch:true});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));let checks=0;
 async function colors(frame,key,state){
  const actual=await frame.evaluate(()=>{
   const input=document.getElementById('answer'),phrase=document.getElementById('phrase'),gap=phrase.querySelector('.blank,.wrong,.given,.solved');
   const color=e=>{const s=getComputedStyle(e);return {border:s.borderBottomColor,outline:s.outlineColor,fill:s.backgroundColor,color:s.color}};
   return {input:color(input),gap:gap&&color(gap),state:input.getAttribute('data-state'),phrase:phrase.textContent};
  });
  const green='rgb(52, 91, 85)',red='rgb(232, 121, 98)',expected=state==='bad'?red:green;
  assert.equal(actual.input.border,expected,`${key}/${state} input border`);
  if(await frame.locator('#answer').evaluate(e=>e===document.activeElement))assert.equal(actual.input.outline,expected,`${key}/${state} focus outline`);
  assert.equal(actual.input.fill,state==='bad'?'rgb(249, 224, 215)':'rgb(243, 250, 245)',`${key}/${state} fill`);
  if(actual.gap){assert.equal(actual.gap.color,expected,`${key}/${state} gap`);if(key==='verbi'){assert.equal(actual.gap.border,expected);assert.equal(actual.gap.fill,state==='bad'?'rgb(249, 224, 215)':'rgb(214, 234, 223)');}}
  assert.equal(actual.state,state);assert.ok(actual.phrase.trim().length>5);checks++;
 }
 for(const hub of [false,true])for(const [key,file] of Object.entries(apps)){
  await page.goto(process.env.GREEN_BASE_URL?`${process.env.GREEN_BASE_URL}/${hub?'index.html':file}?v=30`:'file://'+path.resolve(__dirname,'../'+(hub?(process.env.GREEN_HUB_FILE||'index.html'):file)));
  let frame=page;
  if(hub){await page.locator('#tab-'+key).click();await page.locator('#loading-'+key).waitFor({state:'hidden'});frame=await (await page.locator('#frame-'+key).elementHandle()).contentFrame();}
  if(key==='articoli')await frame.locator('#method').selectOption('type');
  for(const mode of ['a','b']){
   await frame.locator('#mode-'+mode).click();
   const prompt=await frame.locator('#phrase').innerText();
   await colors(frame,key,'idle');await frame.locator('#answer').focus();await colors(frame,key,'idle');
   await frame.locator('#answer').fill('   ');await frame.locator('#check').click();await colors(frame,key,'idle');
   assert.equal(await frame.locator('#phrase').innerText(),prompt);
   await frame.locator('#answer').fill('errore');await frame.locator('#check').click();await colors(frame,key,'bad');
   assert.equal(await frame.locator('#phrase').innerText(),prompt,'wrong submission must preserve noun/sentence');
   if(key==='articoli'){await frame.locator('#next').click();await colors(frame,key,'idle');}
   else {
    await frame.locator('#answer').fill('');await colors(frame,key,'idle');
    await frame.locator('#check').click();await colors(frame,key,'idle');
   }
   const answer=await frame.evaluate(({key,mode})=>key==='aggettivi'?phrase(order[pos]):key==='articoli'&&mode==='b'?join(order[pos].answer,order[pos].word):order[pos].answer,{key,mode});
   await frame.locator('#answer').fill(answer);await frame.locator('#check').click();await colors(frame,key,'good');
   await frame.locator('#next').click();await colors(frame,key,'idle');
   await frame.locator('#shuffle').click();await colors(frame,key,'idle');
   assert.equal(await frame.locator('html').evaluate(e=>e.scrollWidth<=innerWidth),true);
  }
  if(key==='verbi'&&hub)await page.screenshot({path:path.resolve(__dirname,'../.aitemp/green-frames-v30/hub-verbi-mobile.png')});
 }
 assert.deepEqual(errors,[]);console.log(JSON.stringify({engine:'WebKit',checks,standaloneAndHub:true,modes:['a','b'],errors}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});

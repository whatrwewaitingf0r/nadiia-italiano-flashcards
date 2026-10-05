const {webkit}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path');
(async()=>{
 const browser=await webkit.launch({headless:true});
 const page=await browser.newPage({viewport:{width:375,height:812},isMobile:true,hasTouch:true});
 const errors=[],network=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
 await page.goto('file://'+path.resolve(__dirname,'../index.html'));
 await page.locator('#tab-lettura').click();await page.locator('#loading-lettura').waitFor({state:'hidden'});
 const frame=await (await page.locator('#frame-lettura').elementHandle()).contentFrame();
 assert.equal(await frame.locator('#section option').count(),13);
 let totalParagraphs=0,totalQuestions=0;
 for(let i=0;i<13;i++){
  await frame.locator('#section').selectOption(String(i));
  const result=await frame.evaluate(i=>{
   const s=READING.sections[i],paras=[...document.querySelectorAll('#paragraphs > p')];
   if(JSON.stringify(paras.map(p=>p.textContent))!==JSON.stringify(s.paragraphs.map(p=>p.text)))throw Error('Source omission '+i);
   if(JSON.stringify([...document.querySelectorAll('.question > p')].map(p=>p.textContent))!==JSON.stringify(s.questions.map(q=>q.prompt)))throw Error('Question omission '+i);
   return {paragraphs:paras.length,questions:s.questions.length,overflow:document.documentElement.scrollWidth>innerWidth};
  },i);
  assert.equal(result.overflow,false);totalParagraphs+=result.paragraphs;totalQuestions+=result.questions;
 }
 assert.equal(totalParagraphs,1386);assert.equal(totalQuestions,119);
 await frame.locator('#section').selectOption('7');
 assert.match(await frame.locator('#title').innerText(),/Matteuccia/);
 await frame.locator('.question textarea').first().fill('Era una guaritrice di Todi.');
 await frame.locator('.question summary').first().click();
 assert.match(await frame.locator('.question details').first().innerText(),/Matteuccia di Francesco/);
 await frame.locator('#search').fill('Unguento, unguento');await frame.locator('#find').click();
 assert.match(await frame.locator('.match').innerText(),/sopra l’acqua e sopra il vento/);
 await frame.locator('#section').selectOption('12');
 assert.match(await frame.locator('#paragraphs').innerText(),/wicce/);assert.match(await frame.locator('#paragraphs').innerText(),/Yamauba/);
 await page.screenshot({path:path.resolve(__dirname,'../.aitemp/lettura-mobile.png'),animations:'disabled'});
 await page.setViewportSize({width:1040,height:900});
 await frame.locator('#section').selectOption('7');
 await page.screenshot({path:path.resolve(__dirname,'../.aitemp/lettura-desktop.png'),animations:'disabled'});
 await page.locator('#tab-carte').click();await page.locator('#loading-carte').waitFor({state:'hidden'});
 const cards=await (await page.locator('#frame-carte').elementHandle()).contentFrame();
 await cards.locator('#filter').selectOption('liam-lettura');
 assert.equal(await cards.locator('#direction').isDisabled(),true);
 const checked=await cards.evaluate(()=>{
  pool=ALL.filter(c=>matches(c,'liam-lettura'));index=0;
  let sourceCards=0;
  for(let i=0;i<pool.length;i++){
   index=i;render();const c=pool[i];
   if(document.getElementById('frontWord').textContent!==(c.kind==='reading'?c.sourceText:c.it))throw Error('Truncated reading front '+i);
   if(document.getElementById('backWord').textContent!==c.other)throw Error('Wrong back '+i);
   if(c.kind==='reading'){
    sourceCards++;const w=document.getElementById('frontWord');
    if(w.scrollHeight<=w.clientHeight)throw Error('Reading not scrollable '+i);
    w.scrollTop=w.scrollHeight;if(w.scrollTop===0)throw Error('Cannot reach reading ending '+i);
   }
  }
  index=0;render();return{count:pool.length,sourceCards,lesson5:ALL.filter(c=>(c.tags||[]).includes('lesson5')&&(c.tags||[]).includes('nord-sud')).length};
 });assert.deepEqual(checked,{count:257,sourceCards:13,lesson5:56});
 await cards.locator('#flip').click();assert.equal(await cards.locator('.back').evaluate(e=>getComputedStyle(e).visibility),'visible');
 await page.locator('#tab-liam').click();await page.locator('#loading-liam').waitFor({state:'hidden'});
 assert.equal(await page.locator('#tab-liam').innerText(),'Liam ieri');
 assert.deepEqual(errors,[]);assert.deepEqual(network,[]);
 console.log(JSON.stringify({sections:13,paragraphs:totalParagraphs,questions:totalQuestions,cards:checked.count,lesson5:checked.lesson5,errors,network}));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

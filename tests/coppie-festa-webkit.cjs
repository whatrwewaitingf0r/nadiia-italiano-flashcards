// Real WebKit layout, CSS animations, click-through and reduced-motion checks.
const {webkit}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const browser=await webkit.launch({headless:true});
 const shots='/tmp/nadiia-v57-festa';fs.mkdirSync(shots,{recursive:true});
 try{
  for(const width of [320,375,1040]){
   const page=await browser.newPage({viewport:{width,height:1000},isMobile:width<800,hasTouch:true});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto('file://'+path.resolve(__dirname,'../index.html')+'#coppie');
   const frame=page.frameLocator('#frame-coppie');
   await frame.locator('#english .tile').first().waitFor();
   const app=await (await page.$('#frame-coppie')).contentFrame();
   for(const [count,text,dots,ms] of [[5,'Cinque di fila.',6,2200],[10,'Dieci di fila.',10,2200],[20,'Venti di fila.',18,3000],[30,'30 di fila.',18,3000]]){
    await app.evaluate(n=>{newRound();streak=n-1;updateStreak()},count);
    const left=frame.locator('#english .tile').first(),id=await left.getAttribute('data-pair');
    await left.click();await frame.locator(`#italian .tile[data-pair="${id}"]`).click();
    await frame.locator('#festa.show').waitFor();
    assert.equal(await frame.locator('.festa-label').innerText(),text);
    assert.equal(await frame.locator('.festa-dot').count(),dots);
    assert.equal(await frame.locator('#festa').evaluate(e=>getComputedStyle(e).pointerEvents),'none');
    assert.equal(await frame.locator('.festa-label').evaluate(e=>getComputedStyle(e).animationDuration),ms/1000+'s');
    assert.equal(await frame.locator('#pair-board').evaluate(e=>getComputedStyle(e,'::before').animationName),'festa-glow');
    if(count===5||count===20){
     // Capture a deliberate mid-burst frame, not the opening opacity-zero frame.
     await app.evaluate(()=>document.getAnimations().forEach(a=>{a.pause();a.currentTime=650}));
     await page.screenshot({path:`${shots}/${width}-${count}.png`,fullPage:true});
     await app.evaluate(()=>document.getAnimations().forEach(a=>a.play()));
    }
    // A genuine next match can be tapped through the celebration.
    const nextLeft=frame.locator('#english .tile:not(:disabled)').first(),nextId=await nextLeft.getAttribute('data-pair');
    await nextLeft.click();await frame.locator(`#italian .tile[data-pair="${nextId}"]`).click();
    assert.equal(await app.evaluate(()=>streak),count+1);
    await frame.locator('#festa.show').waitFor({state:'hidden',timeout:ms+1500});
    assert.equal(await frame.locator('#festa span').count(),0);
    assert.equal(await frame.locator('#streak-line').innerText(),count+1+' di fila.');
   }
   assert.equal(await app.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
   await page.emulateMedia({reducedMotion:'reduce'});
   await app.evaluate(()=>{streak=20;showFesta()});
   assert.equal(await frame.locator('.festa-dot').first().isVisible(),false);
   assert.equal(await frame.locator('.festa-label').evaluate(e=>getComputedStyle(e).animationName),'none');
   assert.deepEqual(errors,[]);await page.close();
  }
  console.log('PASS: WebKit 320/375/1040px embedded festa, CSS-only animation durations/glow, real click-through, cleanup, reduced motion, no overflow or page errors.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});

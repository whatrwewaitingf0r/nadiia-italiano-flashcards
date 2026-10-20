const {chromium}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
  for(const width of [320,375,1040]){
   const page=await browser.newPage({viewport:{width,height:812},isMobile:width<800,hasTouch:width<800});
   page.setDefaultTimeout(15000);console.log('Checking width',width);const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(process.env.HUB_URL||'file://'+path.resolve(__dirname,'../index.html'));
   await page.locator('#tab-aggettivi').click();
   const frame=page.frameLocator('#frame-aggettivi');
   await frame.locator('#answer').waitFor();
   for(const mode of ['a','b']){
    for(const [form,label] of Object.entries({def:'Articolo determinativo',ind:'Articolo indeterminativo',pl:'Articolo determinativo',some:'Partitivo: alcuni / alcune',questo:'Dimostrativo: questo',questi:'Dimostrativo: questo',quello:'Dimostrativo: quello',quelli:'Dimostrativo: quello'})){
     await frame.locator('body').evaluate((_,{mode,form})=>{start(mode);order=[makeItem(NOUNS.find(n=>n.sg==='scarpa'),form,'nuovo')];pos=0;render();},{mode,form});
     assert.equal(await frame.locator('#category').textContent(),label);
     await frame.locator('#answer').scrollIntoViewIfNeeded();
     const layout=await frame.locator('body').evaluate(()=>{
      const category=document.getElementById('category'),input=document.getElementById('answer');
      const c=category.getBoundingClientRect(),a=input.getBoundingClientRect();
      return {inForm:category.parentElement.id==='answer-form',uppercase:getComputedStyle(category).textTransform,categoryTop:c.top,categoryBottom:c.bottom,inputTop:a.top,viewport:innerHeight,headerCategory:!!document.querySelector('.meta #category'),overflow:document.documentElement.scrollWidth>innerWidth};
     });
     assert.equal(layout.inForm,true);assert.equal(layout.headerCategory,false);assert.equal(layout.uppercase,'uppercase');
     assert.ok(layout.categoryBottom<=layout.inputTop&&layout.inputTop-layout.categoryBottom<65,JSON.stringify(layout));
     assert.ok(layout.categoryTop>=0&&layout.categoryBottom<=layout.viewport,JSON.stringify(layout));
     assert.equal(layout.overflow,false);
    }
   }
   assert.deepEqual(errors,[]);
   if(width===375)await page.screenshot({path:'/tmp/nadiia-v45-phone.png'});
   await page.close();
  }
  console.log('PASS: mobile/desktop Chromium, 48 mode/article cases; uppercase category beside input and visible after scrolling; no overflow/page errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});

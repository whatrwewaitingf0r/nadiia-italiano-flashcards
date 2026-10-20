// Run the real hub and all three exercise scripts in separate window contexts.
// Deliberately broken iframe recognition can start but never produces a result (iOS regression).
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..');
class Element {
 constructor(){this.children=[];this.style={};this.value='';this.hidden=false;this.disabled=false;this.attrs={};this.events={};this.classList={toggle(){}};}
 set textContent(v){this.text=String(v);this.children=[];}get textContent(){return (this.text||'')+this.children.map(c=>c.textContent).join('');}
 appendChild(e){this.children.push(e);}setAttribute(k,v){this.attrs[k]=String(v);}addEventListener(k,f){(this.events[k]??=[]).push(f);}focus(){}setSelectionRange(){}
}
function setup(api='webkitSpeechRecognition',startError=false){
 const queue=[],sessions=[],frames={},hubNodes={},hubEvents={},apps={};let iframeConstructions=0;
 const get=id=>hubNodes[id]??=new Element();
 const hub={location:{hash:''},history:{replaceState(){}},Event:class{constructor(type){this.type=type;}},document:{hidden:false,getElementById:get,addEventListener:(k,f)=>hubEvents[k]=f},addEventListener:(k,f)=>hubEvents[k]=f};hub.window=hub;hub.globalThis=hub;
 class Recognition{constructor(){sessions.push(this);}start(){if(startError)throw Error('denied');this.onstart?.();}stop(){this.stopped=true;}abort(){this.aborted=true;/* onend is asynchronous, like Safari */}}
 if(api)hub[api]=Recognition;
 const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
 for(const m of html.matchAll(/<script type="application\/json" id="([^"]+)">([\s\S]*?)<\/script>/g))get(m[1]).textContent=m[2];
 const hubCtx=vm.createContext(hub);vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],hubCtx);
 function flush(){for(let n=0;queue.length;n++){assert.ok(n<100,'message loop');queue.shift()();}}
 function load(key,file){
  const nodes={},events={},get=id=>nodes[id]??=new Element();
  const app={document:{hidden:false,getElementById:get,createElement:()=>new Element(),createTextNode:t=>({textContent:t}),addEventListener:(k,f)=>events[k]=f},Math,console,location:{origin:'https://example.test'},addEventListener:(k,f)=>events[k]=f,webkitSpeechRecognition:class{constructor(){iframeConstructions++;}start(){}abort(){}stop(){}}};
  app.window=app;app.globalThis=app;
  app.parent={postMessage:data=>queue.push(()=>hubEvents.message?.({data,source:app,origin:'https://example.test'}))};
  app.postMessage=data=>queue.push(()=>events.message?.({data,source:app.parent,origin:'https://example.test'}));
  frames[key]=get;hubNodes['frame-'+key].contentWindow=app;hubNodes['frame-'+key].contentDocument={dispatchEvent:event=>events[event.type]?.()};
  const ctx=vm.createContext(app),source=fs.readFileSync(path.join(root,file),'utf8');vm.runInContext(source.match(/<script>([\s\S]*?)<\/script>/)[1],ctx);
  if(key==='articoli'){nodes.method.value='type';nodes.method.onchange();}
  flush();const run=s=>vm.runInContext(s,ctx);
  return apps[key]={nodes,events,app,run,click(){nodes.speak.onclick();flush();}};
 }
 return {sessions,apps,hub,hubEvents,load,flush,get,activate(key){vm.runInContext(`activate('${key}')`,hubCtx);flush();},iframeCount:()=>iframeConstructions,result(text){sessions[0].onresult({results:[[{transcript:text}]]});flush();},end(){sessions[0].onend();flush();}};
}
for(const [key,file] of Object.entries({aggettivi:'articoli-aggettivi.html',articoli:'articoli-esercizi.html',verbi:'verbi-tempi.html'})){
 for(const api of ['webkitSpeechRecognition','SpeechRecognition']){
  const s=setup(api),a=s.load(key,file);s.activate(key);a.click();
  assert.equal(s.iframeCount(),0,'Embedded Parla must never construct iframe recognition');
  assert.equal(s.sessions.length,1,'Top window must own recognition');assert.equal(s.sessions[0].lang,'it-IT');
  assert.equal(a.nodes.speak.textContent,'Ferma');assert.match(a.nodes['speech-status'].textContent,/In ascolto/);
  a.click();assert.equal(s.sessions[0].stopped,true);assert.doesNotMatch(a.nodes['speech-status'].textContent,/In ascolto/);
  s.result(' la ragazza alta. ');s.end();assert.equal(a.nodes.answer.value,'la ragazza alta');assert.equal(a.run('total'),0);assert.equal(a.nodes.speak.textContent,'Parla');assert.doesNotMatch(a.nodes['speech-status'].textContent,/In ascolto/);
  a.click();assert.equal(s.sessions.length,1,'Reuse a single parent recognizer');s.end();assert.equal(a.nodes['speech-status'].textContent,'');
  a.click();s.sessions[0].onerror({error:'not-allowed'});s.flush();assert.equal(a.nodes.speak.textContent,'Parla');assert.match(a.nodes['speech-status'].textContent,/microfono/);s.end();
  a.click();a.nodes.shuffle.onclick();s.flush();assert.equal(s.sessions[0].aborted,true);s.result('stale phrase');assert.equal(a.nodes.answer.value,'');s.end();
  a.click();s.activate('carte');assert.equal(s.sessions[0].aborted,true);s.result('hidden phrase');s.end();assert.equal(a.nodes.answer.value,'');assert.doesNotMatch(a.nodes['speech-status'].textContent,/In ascolto/);
  s.activate(key);a.click();a.nodes.answer.value='typed';a.nodes.answer.oninput();s.flush();s.result('overwrite');s.end();assert.equal(a.nodes.answer.value,'typed');
  // A different window must not be able to send transcripts into this exercise.
  a.events.message({source:{},data:{type:'parla-text',text:'spoof'}});assert.equal(a.nodes.answer.value,'typed');
 }
 const missing=setup(null),m=missing.load(key,file);assert.equal(m.nodes.speak.disabled,true);assert.equal(m.nodes['speech-status'].textContent,'Detta solo in Safari.');
 const blocked=setup('webkitSpeechRecognition',true),b=blocked.load(key,file);blocked.activate(key);b.click();assert.equal(b.nodes.speak.textContent,'Parla');assert.doesNotMatch(b.nodes['speech-status'].textContent,/In ascolto/);
}
const s=setup(),a=s.load('aggettivi','articoli-aggettivi.html'),b=s.load('verbi','verbi-tempi.html');s.activate('aggettivi');a.click();s.result('la ragazza alta');assert.equal(b.nodes.answer.value,'','Route only to requesting frame');s.end();
s.hubEvents.message({source:{postMessage(){throw Error('Untrusted source accepted');}},data:{type:'parla',on:true}});assert.equal(s.sessions.length,1);
console.log('PASS: top-window bridge, 3 exercises, both APIs, final-after-stop/no-submit, end/error cleanup, cancellation, support and source isolation.');

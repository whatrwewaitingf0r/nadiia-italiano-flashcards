// Exercise the complete inline apps; only browser DOM and microphone service are doubled.
// Catches omitted transcript writes, auto-submit, missing stop, stale results and fallback regressions.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
class Element {
 constructor(){this.children=[];this.style={};this.value='';this.hidden=false;this.disabled=false;this.attrs={};this.events={};this.classList={toggle(){}};}
 set textContent(v){this.text=String(v);this.children=[];}
 get textContent(){return (this.text||'')+this.children.map(c=>c.textContent).join('');}
 appendChild(e){this.children.push(e);}
 setAttribute(k,v){this.attrs[k]=String(v);}
 addEventListener(k,f){(this.events[k]??=[]).push(f);}
 fire(k){for(const f of this.events[k]||[])f();}
 focus(){} setSelectionRange(){}
}
function load(file,api='SpeechRecognition',startError=false){
 const html=fs.readFileSync(path.join(__dirname,'..',file),'utf8'),nodes={},sessions=[],events={};
 const get=id=>nodes[id]??=(new Element());
 for(const m of html.matchAll(/<[a-z][^>]*\bid="([^"]+)"[^>]*>/g))get(m[1]);
 const document={hidden:false,getElementById:get,createElement:()=>new Element(),createTextNode:t=>({textContent:t}),addEventListener:(k,f)=>events[k]=f};
 class Recognition {
  constructor(){sessions.push(this);}
  start(){if(startError)throw new Error('permission');this.onstart?.();}
  stop(){this.stopped=true;}
  abort(){this.aborted=true;this.onend?.();}
 }
 const globals={document,Math,console,location:{hash:''}};
 if(api)globals[api]=Recognition;
 const ctx=vm.createContext(globals);
 vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],ctx);
 const run=s=>vm.runInContext(s,ctx);
 if(file==='articoli-esercizi.html'){nodes.method.value='type';nodes.method.onchange();}
 const click=()=>{assert.equal(typeof nodes.speak?.onclick,'function','Parla must start dictation');nodes.speak.onclick();};
 const result=(s,t)=>s.onresult({resultIndex:0,results:[Object.assign([{transcript:t,confidence:1}],{isFinal:true})]});
 return {html,nodes,sessions,document,events,run,click,result};
}
for(const file of ['articoli-aggettivi.html','articoli-esercizi.html','verbi-tempi.html']){
 for(const api of ['SpeechRecognition','webkitSpeechRecognition']){
  const app=load(file,api),{nodes,sessions,run,click,result}=app;
  assert.equal(sessions.length,0,'Never ask for microphone before a tap');
  nodes.answer.value='old';run("setAnswerState('bad')");click();
  const first=sessions[0];assert.equal(first.lang,'it-IT');assert.equal(first.continuous,false);
  assert.equal(nodes.speak.attrs['aria-pressed'],'true');
  result(first,'  un amico alto  ');
  assert.equal(nodes.answer.value,'un amico alto');assert.equal(nodes.answer.attrs['data-state'],'idle');
  assert.equal(run('total'),0,'Dictation must not submit');assert.equal(nodes.answer.disabled,false);
  click();assert.equal(first.stopped,true,'Second tap stops recording');first.onend();
  assert.equal(nodes.speak.textContent,'Parla');assert.equal(nodes.speak.attrs['aria-pressed'],'false');
  click();const second=sessions[1];second.onend();assert.equal(nodes.speak.textContent,'Parla','Auto-stop restores button');
  click();const stale=sessions[2];nodes.shuffle.onclick();result(stale,'stale text');
  assert.equal(stale.aborted,true);assert.equal(nodes.answer.value,'','New exercise rejects old audio');
  click();const hidden=sessions[3];app.document.hidden=true;app.events.visibilitychange();result(hidden,'hidden text');
  assert.equal(hidden.aborted,true);assert.equal(nodes.answer.value,'');app.document.hidden=false;
  click();const denied=sessions[4];denied.onerror({error:'not-allowed'});
  assert.match(nodes['speech-status'].textContent,/microfono/i);assert.equal(nodes.answer.disabled,false);
  assert.equal(nodes.speak.attrs['aria-pressed'],'false');
  click();const checking=sessions[5];nodes.answer.value='wrong';nodes['answer-form'].onsubmit({preventDefault(){}});
  result(checking,'late correction');assert.equal(checking.aborted,true);assert.equal(nodes.answer.value,'wrong');
  assert.equal(run('total'),1,'Only manual Verifica scores the answer');
 }
 const missing=load(file,null);assert.equal(missing.nodes.speak.disabled,true);
 assert.equal(missing.nodes['speech-status'].textContent,'Detta solo in Safari.');
 missing.nodes.answer.value='written';missing.nodes['answer-form'].onsubmit({preventDefault(){}});
 assert.equal(missing.run('total'),1,'Unsupported speech must preserve typing');
 const blocked=load(file,'SpeechRecognition',true);blocked.click();
 assert.equal(blocked.nodes.speak.attrs['aria-pressed'],'false');assert.equal(blocked.nodes.answer.disabled,false);
 assert.ok(blocked.nodes['speech-status'].textContent.length>0);
}
console.log('PASS: 3 apps, both API names, transcript/no-submit, manual/auto-stop, cancellation, errors and typing fallback.');

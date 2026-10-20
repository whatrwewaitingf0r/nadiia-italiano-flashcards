// Execute real inline scripts. The microphone double withholds text unless start()
// happens synchronously in the owning document's tap, as on iPhone Safari.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..');
class Element {
 constructor(){this.children=[];this.style={};this.value='';this.hidden=false;this.disabled=false;this.attrs={};this.events={};this.classList={toggle(){}};}
 set textContent(v){this.text=String(v);this.children=[];}get textContent(){return (this.text||'')+this.children.map(c=>c.textContent).join('');}
 appendChild(e){this.children.push(e);}setAttribute(k,v){this.attrs[k]=String(v);}addEventListener(k,f){(this.events[k]??=[]).push(f);}focus(){}setSelectionRange(){}
}
const exercises={articoli:'articoli-esercizi.html',aggettivi:'articoli-aggettivi.html',verbi:'verbi-tempi.html'};
for(const [key,file] of Object.entries(exercises)){
 const nodes={},events={},sessions=[];let tapping=false;
 const get=id=>nodes[id]??=new Element();
 const source=fs.readFileSync(path.join(root,file),'utf8');
 class Recognition {
  constructor(){assert.equal(tapping,true,'Construct recognition in the tap');sessions.push(this);}
  start(){this.gesture=tapping;assert.equal(tapping,true,'No message/async boundary before start');}
  stop(){}abort(){this.aborted=true;}
 }
 const app={document:{hidden:false,getElementById:get,createElement:()=>new Element(),createTextNode:t=>({textContent:t}),addEventListener:(k,f)=>events[k]=f},addEventListener:(k,f)=>events[k]=f,Math,console,location:{pathname:'/'+file},webkitSpeechRecognition:Recognition};
 app.parent=app;app.top=app;app.window=app;
 const ctx=vm.createContext(app);vm.runInContext(source.match(/<script>([\s\S]*?)<\/script>/)[1],ctx);
 if(key==='articoli'){nodes.method.value='type';nodes.method.onchange();}
 assert.equal(sessions.length,0);
 tapping=true;nodes.speak.onclick();tapping=false;
 const session=sessions[0];assert.ok(session);assert.equal(session.lang,'it-IT');assert.equal(session.continuous,false);assert.equal(session.interimResults,true,'Show words while speaking');
 const result=(text,final)=>{if(session.gesture)session.onresult({results:[Object.assign([{transcript:text}],{isFinal:final})]});};
 result('la ragazza',false);assert.equal(nodes.answer.value,'la ragazza','Interim text appears');
 result('la ragazza alta',true);assert.equal(nodes.answer.value,'la ragazza alta');assert.equal(vm.runInContext('total',ctx),0,'Do not auto-submit');
 session.onend();assert.equal(nodes.speak.textContent,'Parla');assert.doesNotMatch(nodes['speech-status'].textContent,/In ascolto/);
 tapping=true;nodes.speak.onclick();tapping=false;assert.equal(sessions.length,2,'Fresh recognizer per tap');
 assert.equal(typeof events.pagehide,'function');events.pagehide();assert.equal(sessions[1].aborted,true,'Navigation stops the microphone');
 assert.doesNotMatch(source,/postMessage|parla-support|parla-state|parla-text/,'No parent dictation bridge');
 assert.match(source,/<a [^>]*href="index\.html\?v=48"[^>]*>[^<]*Tutte le schede<\/a>/,'Visible return to hub');
}
const hub=fs.readFileSync(path.join(root,'index.html'),'utf8');
function loadHub(hash=''){
 const nodes={},events={},visited=[];const get=id=>nodes[id]??=new Element();
 for(const m of hub.matchAll(/<script type="application\/json" id="([^"]+)">([\s\S]*?)<\/script>/g))get(m[1]).textContent=m[2];
 const win={addEventListener:(k,f)=>events[k]=f,location:{href:'',assign:url=>visited.push(url)}};win.top=win;
 const ctx=vm.createContext({window:win,document:{getElementById:get},location:{hash},history:{replaceState(){}},console});
 vm.runInContext(hub.match(/<script>([\s\S]*?)<\/script>/)[1],ctx);
 return {nodes,get,visited,run:s=>vm.runInContext(s,ctx)};
}
for(const [key,file] of Object.entries(exercises)){
 const direct=loadHub('#'+key);assert.deepEqual(direct.visited,[file+'?v=48'],'Legacy hash opens exercise as top window');
 const click=loadHub();click.get('tab-'+key).events.click[0]();assert.deepEqual(click.visited,[file+'?v=48'],'Tab leaves hub');
 assert.ok(!click.nodes['frame-'+key]?.srcdoc,'Never embed typed dictation');
}
const s=loadHub();assert.ok(s.get('frame-carte').srcdoc);s.run("activate('coppie')");assert.ok(s.get('frame-coppie').srcdoc);
assert.doesNotMatch(hub.match(/<script>([\s\S]*?)<\/script>/)[1],/SpeechRecognition|postMessage|parla/,'Hub cannot start dictation from a message');
console.log('PASS: 3 top-level exercise routes, same-tap construction/start, interim/final text, no auto-submit, pagehide cancellation, return links, no bridge.');

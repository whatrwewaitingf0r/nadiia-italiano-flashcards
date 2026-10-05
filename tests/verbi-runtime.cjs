const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
class Element{constructor(){this.children=[];this.style={};this.value='';this.hidden=false;this.disabled=false;this.classList={toggle(){}};}set textContent(v){this.text=String(v);this.children=[];}get textContent(){return(this.text||'')+this.children.map(c=>c.textContent).join('');}appendChild(e){this.children.push(e)}setAttribute(){}focus(){}setSelectionRange(){} }
const nodes={},ctx=vm.createContext({document:{getElementById:id=>nodes[id]||(nodes[id]=new Element()),createElement:()=>new Element(),createTextNode:text=>({textContent:text}),addEventListener(){}},Math,console});
vm.runInContext(fs.readFileSync(path.resolve(__dirname,'../verbi-tempi.html'),'utf8').match(/<script>([\s\S]*?)<\/script>/)[1],ctx);
const run=s=>vm.runInContext(s,ctx);
assert.equal(run('ITEMS.length'),900);
for(const [inf,t,p,a] of [['andare','presente',0,'vado'],['mangiare','passato prossimo',0,'ho mangiato'],['partire','futuro semplice',2,'partirà'],['andare','passato prossimo',0,'sono andata'],['venire','passato prossimo',3,'siamo venute'],['stare','passato prossimo',5,'sono stati'],['essere','passato prossimo',4,'siete stati'],['bere','imperfetto',3,'bevevamo'],['dire','imperfetto',5,'dicevano'],['fare','imperfetto',0,'facevo'],['dare','futuro semplice',0,'darò'],['sapere','condizionale presente',2,'saprebbe'],['capire','presente',2,'capisce'],['finire','presente',3,'finiamo'],['pulire','presente',5,'puliscono'],['leggere','passato prossimo',1,'hai letto']])assert.equal(run(`answer(VERBS.find(v=>v.inf===${JSON.stringify(inf)}),${JSON.stringify(t)},${p})`),a);
assert.ok(nodes.phrase.textContent.includes('___'));assert.equal(nodes.hint.hidden,true);
run('submit("")');assert.equal(run('total'),0);run('submit("errore")');assert.equal(run('total'),1);assert.equal(nodes.hint.hidden,false);run('submit(order[pos].answer)');assert.equal(run('total'),1);assert.equal(run('correct'),0);assert.equal(nodes.next.disabled,false);nodes.shuffle.onclick();assert.equal(run('total'),0);
for(const mode of ['a','b']){
 run(`start('${mode}');order=ITEMS.slice();pos=0;render()`);
 for(let i=0;i<900;i++){
  const it=run('order[pos]');
  assert.ok(nodes.phrase.textContent.length>12);assert.equal(nodes.hint.hidden,true);
  assert.ok(nodes.lemma.textContent.includes(it.inf));assert.ok(nodes.lemma.textContent.includes(it.tense));assert.ok(nodes.lemma.textContent.includes(it.person));
  if(mode==='a')assert.ok(nodes.phrase.textContent.includes('___'));else{assert.ok(nodes.phrase.textContent.includes(run('wrongForm(order[pos])')));assert.notEqual(run('wrongForm(order[pos])'),it.answer)}
  run('submit(order[pos].answer.toUpperCase().replace(/ /g,"  "))');assert.equal(run('correct'),i+1);assert.equal(run('total'),i+1);
  assert.ok(nodes.phrase.textContent.includes(it.answer));run('submit("errore")');assert.equal(run('total'),i+1);nodes.next.onclick();
 }
 assert.equal(nodes.progress.style.width,'100%');assert.equal(nodes.next.disabled,true);assert.equal(nodes.phrase.textContent,'Sessione finita.');
}
console.log('PASS: 900 exercises in each mode, visible sentences, irregular forms/agreement, hints/error/retry, score/shuffle/finish.');
run("start('a');order=[ITEMS.find(it=>it.inf==='dovere'&&it.tense==='presente'&&it.p===0)];pos=0;render();submit('debbo')");assert.equal(nodes.next.disabled,false);
run("start('a');order=[ITEMS.find(it=>it.inf==='vedere'&&it.tense==='passato prossimo'&&it.p===0)];pos=0;render();submit('ho veduto')");assert.equal(nodes.next.disabled,false);

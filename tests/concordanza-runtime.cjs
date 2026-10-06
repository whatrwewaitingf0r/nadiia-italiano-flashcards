const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
class Element {constructor(){this.children=[];this.style={};this.value='';this.hidden=false;this.disabled=false;this.classList={toggle(){}};}set textContent(v){this.text=String(v);this.children=[];}get textContent(){return (this.text||'')+this.children.map(c=>c.textContent).join('');}appendChild(e){this.children.push(e);}setAttribute(){}focus(){}addEventListener(k,fn){(this.events??={})[k]=fn;}}
const root=path.resolve(__dirname,'..');
function load(file){const nodes={};const ctx=vm.createContext({document:{getElementById:id=>nodes[id]||(nodes[id]=new Element()),createElement:()=>new Element(),createTextNode:text=>({textContent:text}),addEventListener(){}},location:{hash:''},Math,console});vm.runInContext(fs.readFileSync(file,'utf8').match(/<script>([\s\S]*?)<\/script>/)[1],ctx);return {nodes,run:s=>vm.runInContext(s,ctx)};}
const {nodes,run}=load(root+'/articoli-aggettivi.html');
assert.ok(run('NOUNS.length')>=200);
assert.equal(run('new Set(NOUNS.map(n=>n.sg)).size'),run('NOUNS.length'));
const phrase=(sg,form,adj,pre=false)=>run(`phrase(makeItem(NOUNS.find(n=>n.sg===${JSON.stringify(sg)}),${JSON.stringify(form)},${JSON.stringify(adj)},${pre}))`);
for(const [sg,form,adj,pre,expected] of [
 ['amico','ind','alto',false,'un amico alto'],['studentessa','def','bravo',false,'la studentessa brava'],['yogurt','def','freddo',false,'lo yogurt freddo'],
 ['mano','pl','piccolo',false,'le mani piccole'],['problema','pl','difficile',false,'i problemi difficili'],['foto','pl','bello',false,'le foto belle'],['uomo','pl','alto',false,'gli uomini alti'],
 ['cane','def','bello',true,'il bel cane'],['amico','def','bello',true,'il bell’amico'],['studente','def','bello',true,'il bello studente'],
 ['cane','pl','bello',true,'i bei cani'],['amico','pl','bello',true,'i begli amici'],['studente','pl','bello',true,'i begli studenti'],['casa','pl','bello',true,'le belle case'],
 ['amico','ind','buono',true,'un buon amico'],['studente','ind','buono',true,'un buono studente'],['donna','ind','buono',true,'una buona donna'],
 ['libro','quello','nuovo',false,'quel libro nuovo'],['amico','quello','alto',false,'quell’amico alto'],['studente','quello','giovane',false,'quello studente giovane'],
 ['libro','quelli','nuovo',false,'quei libri nuovi'],['amico','quelli','alto',false,'quegli amici alti'],['donna','quelle','felice',false,'quelle donne felici'],
 ['amico','questo','alto',false,'quest’amico alto'],['amica','questo','alto',false,'quest’amica alta'],['libro','questi','nuovo',false,'questi libri nuovi'],
 ['casa','def','lungo',false,'la casa lunga'],['casa','pl','lungo',false,'le case lunghe'],['libro','pl','bianco',false,'i libri bianchi']
])assert.equal(phrase(sg,form,adj,pre),expected);
assert.equal(nodes.hint.hidden,true);assert.ok(nodes.phrase.textContent.includes('___'));assert.ok(nodes.lemma.textContent.length>0);
run('submit("")');assert.equal(run('total'),0);assert.equal(nodes.hint.hidden,true);
run('submit("sbagliato")');assert.equal(run('total'),1);assert.equal(run('correct'),0);assert.equal(nodes.hint.hidden,false);assert.ok(!nodes.feedback.textContent.includes(run('phrase(order[pos])')));
run('submit(phrase(order[pos]))');assert.equal(run('total'),1);assert.equal(run('correct'),0);assert.equal(nodes.next.disabled,false);
nodes.shuffle.onclick();assert.equal(run('total'),0);assert.equal(nodes.hint.hidden,true);
for(const mode of ['a','b']){
 run(`start(${JSON.stringify(mode)}); order=ITEMS.slice();pos=0;render();`);
 const size=run('order.length');
 for(let i=0;i<size;i++){
  const right=run('phrase(order[pos])');
  assert.equal(nodes.hint.hidden,true);
  if(mode==='a')assert.ok(nodes.phrase.textContent.includes(run('order[pos].word')));
  else assert.notEqual(run('norm(wrongPhrase(order[pos]))'),run('norm(phrase(order[pos]))'));
  run('submit(phrase(order[pos]).replace(/’/g,"\x27").toUpperCase()+".")');
  assert.equal(run('total'),i+1);assert.equal(run('correct'),i+1);assert.equal(nodes.next.disabled,false);
  run('submit("wrong")');assert.equal(run('total'),i+1);
  nodes.next.onclick();
 }
 assert.equal(nodes.phrase.textContent,'Sessione finita.');assert.equal(nodes.progress.style.width,'100%');assert.equal(nodes.next.disabled,true);
}
const pack=load(root+'/italiano-flashcards.html');assert.equal(pack.run('ALL.length'),1377);assert.equal(pack.run('ALL.filter(c=>matches(c,"grammar-concordanza")).length'),0);
assert.ok(pack.run('groups.findIndex(g=>g[0]==="chiara-23-sett")<groups.findIndex(g=>g[0]==="lisa-irregolari")'));
pack.nodes.filter.value='grammar-verbi';pack.nodes.filter.onchange();assert.equal(pack.nodes.direction.disabled,true);assert.equal(pack.nodes.dirText.textContent,'IT→EN');
console.log('PASS: noun inventory, irregular agreement, all A/B exercises, hints, retry/score, apostrophes, shuffle/finish, grammar filter/direction.');

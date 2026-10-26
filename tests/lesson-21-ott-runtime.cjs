// Execute both complete production scripts with minimal DOMs and their real picker handlers.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..');
function load(name){
 const elements=new Map();
 function element(){const classes=new Set();return {value:'',textContent:'',disabled:false,style:{setProperty(){}},children:[],dataset:{},attributes:{},classList:{toggle(){},add(...x){x.forEach(v=>classes.add(v))},remove(...x){x.forEach(v=>classes.delete(v))},contains(v){return classes.has(v)}},setAttribute(k,v){this.attributes[k]=v},appendChild(c){this.children.push(c)},replaceChildren(...c){this.children=c},addEventListener(k,fn){this['on'+k]=fn}}}
 const document={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},createElement:element,querySelectorAll(){return []},addEventListener(){}};
 const context=vm.createContext({document,location:{hash:''},Math:Object.assign(Object.create(Math),{random:()=>0}),Date,setTimeout(){},clearTimeout(){},setInterval(){},clearInterval(){}});
 const source=fs.readFileSync(path.join(root,name),'utf8');
 vm.runInContext(source.match(/<script>([\s\S]*?)<\/script>/)[1],context);
 return {run:s=>vm.runInContext(s,context),el:id=>document.getElementById(id)};
}
const cards=load('italiano-flashcards.html'),coppie=load('coppie.html');
const allCards=JSON.parse(cards.run('JSON.stringify(ALL)')),allDecks=JSON.parse(coppie.run('JSON.stringify(DECKS)'));
const seen=new Set([...allCards.filter(c=>c.group!=='21 ott · mangiare').map(c=>c.it.toLowerCase()),...allDecks.filter(d=>d.id!=='21-ott-mangiare').flatMap(d=>d.pairs.map(p=>p[0].toLowerCase()))]);
const specs=[JSON.parse(fs.readFileSync(path.join(__dirname,'lesson-21-ott-deck.json'),'utf8'))].map(d=>({...d,pairs:d.pairs.filter(([it])=>{if(seen.has(it.toLowerCase()))return false;seen.add(it.toLowerCase());return true})}));
assert.equal(cards.el('filter').value,'18-ott');
assert.deepEqual(Array.from(coppie.run('deckInputs')).filter(i=>i.checked).map(i=>i.value),['18-ott']);
for(const spec of specs){
 assert.equal(cards.el('filter').children.filter(o=>o.value===spec.id&&o.textContent===spec.label).length,1);
 cards.run(`filter.value=${JSON.stringify(spec.id)};filter.onchange()`);
 assert.equal(cards.run('JSON.stringify(pool.map(c=>[c.it,c.other]))'),JSON.stringify(spec.pairs));
 assert.equal(cards.el('shuffle').disabled,true);assert.match(cards.el('status').textContent,/ordine della lezione/);
 for(let i=0;i<spec.pairs.length;i++){
  cards.run(`index=${i};reverse=false;render()`);
  assert.equal(cards.el('frontWord').textContent,spec.pairs[i][0]);assert.equal(cards.el('backWord').textContent,spec.pairs[i][1]);
  cards.run("toggleDirection({preventDefault(){},stopPropagation(){},type:'click',detail:0})");
  assert.equal(cards.el('frontWord').textContent,spec.pairs[i][1]);assert.equal(cards.el('backWord').textContent,spec.pairs[i][0]);
 }
 cards.run('shufflePool()');assert.equal(cards.run('JSON.stringify(pool.map(c=>[c.it,c.other]))'),JSON.stringify(spec.pairs));
 const inputs=coppie.run('deckInputs');
 assert.equal(Array.from(inputs).filter(i=>i.value===spec.id).length,1);
 for(const input of inputs)input.checked=input.value===spec.id;
 inputs.find(i=>i.value===spec.id).onchange();
 assert.equal(coppie.run('JSON.stringify(PAIRS)'),JSON.stringify(spec.pairs));
 const visited=new Set();
 for(let i=0;i<spec.pairs.length;i++){
  for(const tile of coppie.el('italian').children)visited.add(tile.textContent);
  coppie.run('newRound()');
 }
 assert.equal(visited.size,spec.pairs.length,'all added words reachable');
}
const tutto=coppie.run("deckInputs.find(i=>i.value==='tutto')");tutto.checked=true;tutto.onchange();
assert.equal(coppie.run('PAIRS.length'),coppie.run('uniquePairs(DECKS).length'));
for(const spec of specs)for(const pair of spec.pairs)assert(coppie.run(`PAIRS.some(p=>p[0]===${JSON.stringify(pair[0])}&&p[1]===${JSON.stringify(pair[1])})`));
console.log('PASS: 21 October picker, exact order, both directions, unchanged defaults, full matching coverage and dynamic Tutto.');

// Run the complete production card script with a minimal DOM, not a copy of its logic.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const html=fs.readFileSync(process.env.CARD_HTML_PATH||path.resolve(__dirname,'../italiano-flashcards.html'),'utf8');
const elements=new Map();
function element(){return {value:'',textContent:'',disabled:false,style:{},children:[],events:{},classList:{toggle(){}},appendChild(child){this.children.push(child)},replaceChildren(...children){this.children=children},addEventListener(type,fn){this.events[type]=fn}}}
const document={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},createElement:element,addEventListener(){}};
const context=vm.createContext({document,location:{hash:''},Math:Object.assign(Object.create(Math),{random:()=>0}),Date});
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
vm.runInContext(script,context);
const run=s=>vm.runInContext(s,context), el=id=>document.getElementById(id);
const expected=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../tests/lesson-24-ott-decks.json'),'utf8'));
assert.equal(el('filter').value,'18-ott','default must not change');
for(const deck of expected){
 assert.equal(el('filter').children.filter(o=>o.value===deck.id&&o.textContent===deck.label).length,1,'selectable '+deck.id);
 run(`filter.value=${JSON.stringify(deck.id)};filter.onchange()`);
 assert.equal(run('pool.length'),deck.pairs.length,deck.id);
 assert.equal(run('JSON.stringify(pool.map(c=>[c.it,c.other]))'),JSON.stringify(deck.pairs));
 assert.equal(el('shuffle').disabled,true,'dated lessons keep their input order');
 assert.match(el('status').textContent,/ordine della lezione/);
 for(let i=0;i<deck.pairs.length;i++){
  run(`index=${i};reverse=false;render()`);
  assert.equal(el('frontWord').textContent,deck.pairs[i][0]);assert.equal(el('backWord').textContent,deck.pairs[i][1]);
  run("toggleDirection({preventDefault(){},stopPropagation(){},type:'click',detail:0})");
  assert.equal(el('frontWord').textContent,deck.pairs[i][1]);assert.equal(el('backWord').textContent,deck.pairs[i][0]);
 }
 run('shufflePool()');assert.equal(run('JSON.stringify(pool.map(c=>[c.it,c.other]))'),JSON.stringify(deck.pairs));
}
run("filter.value='18-ott';filter.onchange()");assert.equal(run('pool.length'),81);assert.equal(el('frontWord').textContent,'il tempo');
console.log('PASS: three selectable new Carte decks, exact pair order, isolation, both directions and unchanged default.');

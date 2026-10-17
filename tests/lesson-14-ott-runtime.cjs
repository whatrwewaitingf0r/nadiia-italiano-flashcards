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
assert.equal(el('filter').value,'14-ott');
assert.deepEqual(el('filter').children.slice(0,2).map(o=>[o.value,o.textContent]),[['14-ott','14 ott'],['7-ott','7 ott']]);
assert.equal(el('counter').textContent,'1 / 100');
assert.equal(el('frontWord').textContent,'I signori desiderano?');
assert.equal(el('backWord').textContent,'What would you like?');
assert.equal(el('direction').disabled,false);
assert.equal(el('shuffle').disabled,true);
assert.match(el('status').textContent,/ordine della lezione/);
const expected=run("JSON.stringify(ALL.filter(c=>c.group==='14 ott').map(c=>c.it))");
for(let n=0;n<4;n++){
 run('shufflePool()');
 assert.equal(run('JSON.stringify(pool.map(c=>c.it))'),expected);
}
// Every front/back remains paired in forward and reverse directions.
run(`for(let n=0;n<pool.length;n++){
 index=n;reverse=false;render();
 if($('frontWord').textContent!==pool[n].it||$('backWord').textContent!==pool[n].other)throw Error('IT front/back mismatch '+n);
 toggleDirection({preventDefault(){},stopPropagation(){},type:'click',detail:0});
 if($('frontWord').textContent!==pool[n].other||$('backWord').textContent!==pool[n].it)throw Error('EN front/back mismatch '+n);
}`);
run('index=99;move(1)');assert.equal(el('counter').textContent,'1 / 100');
run('move(-1)');assert.equal(el('counter').textContent,'100 / 100');
// Changing to every older dropdown never includes the new lesson.
run(`for(const [value] of groups){if(value==='14-ott')continue;
 filter.value=value;filter.onchange();
 if(pool.some(c=>c.group==='14 ott'))throw Error('new lesson leaked into '+value);
}`);
run("filter.value='7-ott';filter.onchange()");
assert.equal(el('counter').textContent,'1 / 48');
assert.equal(el('frontWord').textContent,'un panino con prosciutto e formaggio');
assert.equal(el('shuffle').disabled,true);
run("filter.value='14-ott';filter.onchange()");
assert.equal(el('frontWord').textContent,'I signori desiderano?');
assert.equal(el('dirText').textContent,'IT→EN');
// Even a direct global shuffle keeps both dated lessons contiguous, newest first.
run('pool=ALL.slice();shufflePool()');
assert.equal(run('JSON.stringify(pool.slice(0,100).map(c=>c.it))'),expected);
assert.equal(run("pool.slice(100,148).every(c=>c.group==='7 ott')"),true);
assert.equal(run("pool.slice(148).some(c=>['14 ott','7 ott'].includes(c.group))"),false);
console.log('PASS: default 14 ott, all 100 paired reversible cards, stable lesson order, old-deck isolation, preserved 7 ott.');

// Executes real card filtering/rendering and hub routing with a bounded DOM stub.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=process.env.V32_ROOT||path.resolve(__dirname,'..');
function load(name){
 const html=fs.readFileSync(path.join(root,name),'utf8'),nodes=new Map();
 const create=tag=>({tagName:tag,children:[],attributes:{},style:{},value:'',textContent:'',disabled:false,hidden:false,scrollTop:0,events:{},classList:{values:new Set(),toggle(k,v){if(v)this.values.add(k);else this.values.delete(k)}},appendChild(n){this.children.push(n);return n},replaceChildren(...n){this.children=n},setAttribute(k,v){this.attributes[k]=v},addEventListener(k,fn){this.events[k]=fn},focus(){this.focused=true}});
 for(const m of html.matchAll(/\bid="([^"]+)"/g))nodes.set(m[1],create('div'));
 for(const m of html.matchAll(/<script type="application\/json" id="([^"]+)">([\s\S]*?)<\/script>/g))nodes.get(m[1]).textContent=m[2];
 const location={hash:'#liam-lesson5'};
 const context=vm.createContext({document:{getElementById(id){assert(nodes.has(id),'Missing control '+id);return nodes.get(id)},createElement:create,addEventListener(){}},window:{addEventListener(){}},history:{replaceState(a,b,hash){location.hash=hash}},location,console,Math});
 const run=s=>vm.runInContext(s,context);
 run([...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n'));
 return{html,nodes,run,location};
}
const deck=load('italiano-flashcards.html');
assert.equal(deck.run('ALL.length'),1492);
assert.equal(deck.run("ALL.filter(c=>['Grammatica · articoli','Grammatica · concordanza'].includes(c.group)||(c.tags||[]).includes('lesson5')).length"),0);
assert.equal(deck.nodes.get('filter').value,'7-ott');
assert.equal(deck.nodes.get('counter').textContent,'1 / 48');
assert.equal(deck.run('groups.length'),20);
for(const [key,count] of [['grammar-verbi',25],['lisa-irregolari',20],['lisa-irregolari-tempi',20],['liam-16',20],['ref-100-parole',100],['100parole-2',100],['vocabolario',539],['liam-liguria',53],['100parole-3',100],['streghe',101],['verbi-forme',168],['7-ott',48]]){
 deck.nodes.get('filter').value=key;deck.nodes.get('filter').onchange();assert.equal(deck.run('pool.length'),count,key);
}
deck.run('pool=ALL.slice();index=0');
for(let i=0;i<1492;i++){
 deck.run(`index=${i};reverse=false;render()`);
 assert.equal(deck.nodes.get('frontWord').textContent,deck.run("pool[index].direction==='EN→IT'?pool[index].other:pool[index].it"));
 assert.equal(deck.nodes.get('backWord').textContent,deck.run("pool[index].direction==='EN→IT'?pool[index].it:pool[index].other"));
 assert.equal(deck.nodes.get('scene').classList.values.has('rule-card'),deck.run("pool[index].group==='Grammatica · verbi'"));
}
const hub=load('index.html');
assert.equal(hub.run('JSON.stringify(keys)'),JSON.stringify(['carte','articoli','aggettivi','verbi']));
assert.equal(hub.location.hash,'#carte');
assert(!hub.html.includes('liam-passato.html'));
for(const key of ['carte','articoli','aggettivi','verbi']){
 hub.nodes.get('tab-'+key).events.click();assert.equal(hub.location.hash,'#'+key);assert.equal(hub.nodes.get('panel-'+key).hidden,false);assert(hub.nodes.get('frame-'+key).srcdoc.includes('<main'));
}
hub.nodes.get('tab-carte').events.keydown({key:'End',preventDefault(){}});assert.equal(hub.location.hash,'#verbi');
hub.nodes.get('tab-verbi').events.keydown({key:'Home',preventDefault(){}});assert.equal(hub.location.hash,'#carte');
console.log('PASS: 1492 real card renders, retained filters/counts, four hub routes, removed-hash fallback, keyboard navigation (DOM stub; not browser QA).');

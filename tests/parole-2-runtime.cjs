// Execute real app scripts and iframe-load callbacks with a bounded DOM stub.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=process.env.PAROLE2_ROOT||path.resolve(__dirname,'..');
function load(html,hash=''){
 const nodes=new Map();
 const create=tag=>({tagName:tag,children:[],attributes:{},style:{},value:'',textContent:'',disabled:false,hidden:false,scrollTop:0,events:{},parent:null,
  classList:{values:new Set(),toggle(k,v){if(v)this.values.add(k);else this.values.delete(k)}},
  get options(){return this.children},
  appendChild(n){if(n.parent)n.parent.children=n.parent.children.filter(c=>c!==n);n.parent=this;this.children.push(n);return n},
  replaceChildren(...n){this.children=n},setAttribute(k,v){this.attributes[k]=v},addEventListener(k,fn){this.events[k]=fn},
  dispatchEvent(e){if(e.type==='change'&&this.onchange)this.onchange(e)},focus(){this.focused=true}});
 for(const m of html.matchAll(/\bid="([^"]+)"/g))nodes.set(m[1],create('div'));
 for(const m of html.matchAll(/<script type="application\/json" id="([^"]+)">([\s\S]*?)<\/script>/g))nodes.get(m[1]).textContent=m[2];
 const location={hash},document={head:create('head'),getElementById(id){assert(nodes.has(id),'Missing control '+id);return nodes.get(id)},createElement:create,addEventListener(){},querySelector(s){return s==='main'?create('main'):null}};
 const context=vm.createContext({document,window:{addEventListener(){}},history:{replaceState(a,b,h){location.hash=h}},location,console,Math,Event:class{constructor(type){this.type=type}}});
 const run=s=>vm.runInContext(s,context);
 run([...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n'));
 return{html,nodes,run,location,document};
}
const cardHTML=fs.readFileSync(path.join(root,'italiano-flashcards.html'),'utf8');
const deck=load(cardHTML);
assert.equal(deck.run("ALL.filter(c=>matches(c,'100parole-2')).length"),100);
assert.equal(deck.nodes.get('filter').value,'chiara-23-sett');
assert.equal(deck.nodes.get('counter').textContent,'1 / 44');
deck.nodes.get('filter').value='100parole-2';deck.nodes.get('filter').onchange();
assert.equal(deck.nodes.get('counter').textContent,'1 / 100');
assert.equal(deck.nodes.get('direction').disabled,false);
assert.equal(deck.nodes.get('dirText').textContent,'IT→EN');
const first=deck.nodes.get('frontWord').textContent,english=deck.nodes.get('backWord').textContent;
const click={type:'click',detail:0,preventDefault(){},stopPropagation(){}};
deck.nodes.get('direction').events.click(click);
assert.equal(deck.nodes.get('frontWord').textContent,english);assert.equal(deck.nodes.get('backWord').textContent,first);assert.equal(deck.nodes.get('dirText').textContent,'EN→IT');
deck.nodes.get('direction').events.click(click);assert.equal(deck.nodes.get('frontWord').textContent,first);
for(let i=0;i<100;i++){
 deck.run(`index=${i};render()`);
 assert.equal(deck.nodes.get('frontWord').textContent,deck.run('pool[index].it'));
 assert.equal(deck.nodes.get('backWord').textContent,deck.run('pool[index].other'));
 assert.equal(deck.nodes.get('frontNote').textContent,'100 parole 2');
 deck.nodes.get('flip').onclick();assert.equal(deck.nodes.get('scene').classList.values.has('flipped'),true);
}
deck.nodes.get('filter').value='ref-100-parole';deck.nodes.get('filter').onchange();assert.equal(deck.run('pool.length'),100);
deck.nodes.get('filter').value='lisa-irregolari';deck.nodes.get('filter').onchange();assert.equal(deck.run('pool.length'),20);
assert.equal(deck.run("ALL.filter(c=>['Grammatica · articoli','Grammatica · concordanza'].includes(c.group)||(c.tags||[]).includes('lesson5')).length"),0);
const standalone=load(cardHTML,'#100parole-2');assert.equal(standalone.nodes.get('counter').textContent,'1 / 100');
const hub=load(fs.readFileSync(path.join(root,'index.html'),'utf8'),'#liam-lesson5');
assert.equal(hub.location.hash,'#carte');
assert.equal(hub.run('JSON.stringify(keys)'),JSON.stringify(['carte','parole-2','articoli','aggettivi','verbi','lettura']));
const frames=new Map();
function activate(key){
 hub.nodes.get('tab-'+key).events.click();
 if(!frames.has(key)){
  const frame=hub.nodes.get('frame-'+key),app=load(frame.srcdoc);
  frame.contentDocument=app.document;frame.events.load();frames.set(key,app);
 }
 assert.equal(hub.nodes.get('panel-'+key).hidden,false);
 return frames.get(key);
}
const carte=activate('carte');assert.equal(carte.nodes.get('filter').value,'chiara-23-sett');
assert(carte.nodes.get('filter').options[0].value.startsWith('chiara-'));
carte.nodes.get('filter').value='lisa-irregolari';carte.nodes.get('filter').onchange();carte.nodes.get('flip').onclick();
const lisaFront=carte.nodes.get('frontWord').textContent;
const more=activate('parole-2');assert.equal(more.nodes.get('filter').value,'100parole-2');assert.equal(more.nodes.get('counter').textContent,'1 / 100');assert.equal(more.nodes.get('direction').disabled,false);
assert(more.document.head.children[0].textContent.includes('backface-visibility:visible'));
activate('carte');assert.equal(carte.nodes.get('frontWord').textContent,lisaFront);assert.equal(carte.nodes.get('filter').value,'lisa-irregolari');assert(carte.nodes.get('scene').classList.values.has('flipped'));
hub.nodes.get('tab-carte').events.keydown({key:'ArrowRight',preventDefault(){}});assert.equal(hub.location.hash,'#parole-2');
hub.nodes.get('tab-parole-2').events.keydown({key:'End',preventDefault(){}});assert.equal(hub.location.hash,'#lettura');
hub.nodes.get('tab-lettura').events.keydown({key:'Home',preventDefault(){}});assert.equal(hub.location.hash,'#carte');
console.log('PASS: 100 new IT→EN renders, independent hub tab, original 100/Lisa isolation, Chiara-first default, iframe load/filter and keyboard behavior. DOM stub; not browser visual QA.');

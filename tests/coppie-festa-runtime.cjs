// Exercise the complete production script, including real handlers and scheduled callbacks.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const html=fs.readFileSync(process.env.COPPIE_HTML_PATH||path.resolve(__dirname,'../coppie.html'),'utf8');
function setup(random=Math.random,storage=new Map()){
 const elements=new Map(), jobs=new Map();let now=0, sequence=0;
 function element(){const classes=new Set();return {textContent:'',disabled:false,children:[],dataset:{},attributes:{},className:'',style:{setProperty(){}},classList:{add(...names){names.forEach(n=>classes.add(n))},remove(...names){names.forEach(n=>classes.delete(n))},contains(n){return classes.has(n)}},setAttribute(k,v){this.attributes[k]=v},appendChild(c){this.children.push(c)},replaceChildren(...c){this.children=c},addEventListener(k,fn){this['on'+k]=fn}}}
 const chips=[...html.matchAll(/data-seconds="(\d+)" aria-pressed="(true|false)"/g)].map(m=>{const e=element();e.dataset.seconds=m[1];e.setAttribute('aria-pressed',m[2]);return e});
 const document={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},createElement:element,querySelectorAll(){return chips}};
 const context=vm.createContext({document,sessionStorage:{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,String(value))},Math:Object.assign(Object.create(Math),{random}),Date:{now:()=>now},setTimeout(fn,delay){jobs.set(++sequence,{fn,at:now+delay});return sequence},clearTimeout(id){jobs.delete(id)},setInterval(fn,delay){jobs.set(++sequence,{fn,at:now+delay,delay});return sequence},clearInterval(id){jobs.delete(id)}});
 vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
 function advance(ms){const target=now+ms;for(;;){const item=[...jobs].filter(([,v])=>v.at<=target).sort((a,b)=>a[1].at-b[1].at)[0];if(!item)break;const [id,j]=item;now=j.at;if(j.delay)j.at+=j.delay;else jobs.delete(id);j.fn()}now=target}
 const el=id=>document.getElementById(id), run=s=>vm.runInContext(s,context);
 function click(e){if(!e.disabled)e.onclick()}
 function solve(){for(const left of el('english').children){if(left.disabled)continue;click(left);click(el('italian').children.find(t=>t.dataset.pair===left.dataset.pair))}}
 return {el,run,click,solve,chips,advance,jobs};
}

assert.doesNotMatch(html, /<canvas|<audio|<script[^>]+src=|https?:\/\//);
assert.match(html, /id="festa"[^>]*aria-live="polite"/);
assert.match(html, /#festa\{[^}]*pointer-events:none/);
assert.match(html, /@keyframes festa-glow/);
assert.match(html, /@keyframes festa-dot/);
assert.match(html, /prefers-reduced-motion:reduce/);
const storage=new Map(),s=setup(()=>0,storage);
function matchOne(){const left=s.el('english').children.find(t=>!t.disabled);s.click(left);s.click(s.el('italian').children.find(t=>t.dataset.pair===left.dataset.pair));}
function reach(count){while(s.run('streak')<count){if(!s.el('next').disabled)s.click(s.el('next'));matchOne();}}
for(const [count,message,dots,duration] of [[5,'Cinque di fila.',6,2200],[10,'Dieci di fila.',10,2200],[20,'Venti di fila.',18,3000],[30,'30 di fila.',18,3000],[40,'40 di fila.',18,3000]]){
 reach(count);
 assert.equal(s.el('streak-line').textContent,count+' di fila.');
 assert(s.el('festa').classList.contains('show'));
 assert.equal(s.el('festa').children[0].textContent,message);
 assert.equal(s.el('festa').children.length,dots+1);
 assert.equal(s.el('festa').classList.contains('grande'),count>=10);
 assert.equal(s.el('festa').classList.contains('lunga'),count>=20);
 assert(s.el('pair-board').classList.contains('festive'));
 s.click(s.el('next'));
 assert.equal(s.run('streak'),count,'round of five does not reset');
 assert(s.el('festa').classList.contains('show'),'next round does not cancel the burst');
 s.advance(duration-1);assert(s.el('festa').classList.contains('show'));
 s.advance(1);assert(!s.el('festa').classList.contains('show'));
 assert.equal(s.el('festa').children.length,0,'remove dots and label');
 assert(!s.el('pair-board').classList.contains('festive'));
 assert.equal(s.el('streak-line').textContent,count+' di fila.');
 const restored=setup(()=>0,storage);
 assert.equal(restored.run('streak'),count);
 assert(!restored.el('festa').classList.contains('show'),'reload must not replay a milestone');
 restored.run('newRound()');assert(!restored.el('festa').classList.contains('show'));
}
// Correct pairs after a milestone remain clickable during the banner.
reach(50);s.click(s.el('next'));matchOne();assert.equal(s.run('streak'),51);
const left=s.el('english').children.find(t=>!t.disabled);s.click(left);
s.click(s.el('italian').children.find(t=>!t.disabled&&t.dataset.pair!==left.dataset.pair));
assert.equal(storage.get('coppie-streak'),'0');assert.equal(s.el('streak-line').textContent,'');
assert(!s.el('festa').classList.contains('show'));assert.equal(s.el('festa').children.length,0);
s.advance(420);reach(5);
const input=s.run("deckInputs.find(i=>i.value==='14-ott')");input.checked=true;input.onchange();
assert.equal(s.run('streak'),0,'deck changes reset streak');assert.equal(storage.get('coppie-streak'),'0');
assert(!s.el('festa').classList.contains('show'));assert.equal(s.el('festa').children.length,0);
s.advance(5000);assert(!s.el('festa').classList.contains('show'),'no delayed stale banner');
console.log('PASS: CSS festa milestones, sizes, 2.2/3s cleanup, quiet counter, reload/round continuity, clickable tiles and mismatch/deck resets.');

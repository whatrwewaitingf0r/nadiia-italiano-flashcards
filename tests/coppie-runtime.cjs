// Exercise the complete production script, including real handlers and scheduled callbacks.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const html=fs.readFileSync(process.env.COPPIE_HTML_PATH||path.resolve(__dirname,'../coppie.html'),'utf8');
function setup(random=Math.random){
 const elements=new Map(), jobs=new Map();let now=0, sequence=0;
 function element(){const classes=new Set();return {textContent:'',disabled:false,children:[],dataset:{},attributes:{},className:'',classList:{add(...names){names.forEach(n=>classes.add(n))},remove(...names){names.forEach(n=>classes.delete(n))},contains(n){return classes.has(n)}},setAttribute(k,v){this.attributes[k]=v},appendChild(c){this.children.push(c)},replaceChildren(...c){this.children=c},addEventListener(k,fn){this['on'+k]=fn}}}
 const chips=[0,10,15,45].map(n=>{const e=element();e.dataset.seconds=String(n);return e});
 const document={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},createElement:element,querySelectorAll(){return chips}};
 const context=vm.createContext({document,Math:Object.assign(Object.create(Math),{random}),Date:{now:()=>now},setTimeout(fn,delay){jobs.set(++sequence,{fn,at:now+delay});return sequence},clearTimeout(id){jobs.delete(id)},setInterval(fn,delay){jobs.set(++sequence,{fn,at:now+delay,delay});return sequence},clearInterval(id){jobs.delete(id)}});
 vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
 function advance(ms){const target=now+ms;for(;;){const item=[...jobs].filter(([,v])=>v.at<=target).sort((a,b)=>a[1].at-b[1].at)[0];if(!item)break;const [id,j]=item;now=j.at;if(j.delay)j.at+=j.delay;else jobs.delete(id);j.fn()}now=target}
 const el=id=>document.getElementById(id), run=s=>vm.runInContext(s,context);
 function click(e){if(!e.disabled)e.onclick()}
 function solve(){for(const left of el('english').children){if(left.disabled)continue;click(left);click(el('italian').children.find(t=>t.dataset.pair===left.dataset.pair))}}
 return {el,run,click,solve,chips,advance,jobs};
}
for(const random of [Math.random,()=>0,()=>.99999]){
 const s=setup(random),{el,click,run,advance,chips}=s;
 assert.equal(el('english').children.length,5);assert.equal(el('italian').children.length,5);
 assert.equal(el('next').disabled,true);assert.equal(s.jobs.size,0,'timer is off initially');
 assert.equal(chips[0].attributes['aria-pressed'],'true');
 const left=el('english').children,right=el('italian').children;
 left.forEach((tile,i)=>{assert.notEqual(tile.dataset.pair,right[i].dataset.pair);const pair=run(`PAIRS[${tile.dataset.pair}]`);assert.equal(tile.textContent,pair[1]);assert.equal(right.find(t=>t.dataset.pair===tile.dataset.pair).textContent,pair[0])});
 click(left[0]);assert(left[0].classList.contains('selected'));
 click(left[1]);assert(!left[0].classList.contains('selected'));assert(left[1].classList.contains('selected'));
 click(left[1]);assert(!left[1].classList.contains('selected'),'tap same tile deselects');
 click(left[0]);const wrong=right.find(t=>t.dataset.pair!==left[0].dataset.pair);click(wrong);
 assert(left[0].classList.contains('wrong'));assert(wrong.classList.contains('wrong'));
 click(left[2]);assert(!left[2].classList.contains('selected'),'ignore taps while mismatch clears');
 advance(450);assert(!left[0].classList.contains('wrong'));assert(!left[0].classList.contains('selected'));assert(!wrong.disabled);
 click(right.find(t=>t.dataset.pair===left[0].dataset.pair));click(left[0]);
 assert(left[0].disabled);assert(left[0].classList.contains('matched'));assert.equal(el('english').children.length,5);
 assert.equal(el('count').textContent,'1 / 5');
 s.solve();assert.equal(el('count').textContent,'5 / 5');assert.equal(el('next').disabled,false);
 const drawn=left.map(t=>t.dataset.pair);
 for(let n=0;n<32;n++){click(el('next'));const ids=el('english').children.map(t=>t.dataset.pair);assert.equal(new Set(ids).size,5);ids.forEach((id,i)=>assert.notEqual(id,el('italian').children[i].dataset.pair));drawn.push(...ids);s.solve()}
 assert.equal(new Set(drawn.slice(0,81)).size,81,'all deck cards once before repeating');
 assert.equal(new Set(drawn.slice(81,162)).size,81,'second full cycle has no repeats either');
 click(el('next'));click(chips[1]);assert.equal(chips[1].attributes['aria-pressed'],'true');assert.equal(el('clock').textContent,'10 s');
 advance(3000);assert.equal(el('clock').textContent,'7 s');
 click(chips[1]);assert.equal(chips[0].attributes['aria-pressed'],'true');assert.equal(s.jobs.size,0,'same timer chip switches off');
 click(chips[2]);assert.equal(el('clock').textContent,'15 s');advance(15000);
 assert.equal(el('next').disabled,false);assert.match(el('feedback').textContent,/calma/);assert.equal(s.jobs.size,0);
 const expiredLeft=el('english').children[0];click(expiredLeft);click(el('italian').children.find(t=>t.dataset.pair===expiredLeft.dataset.pair));assert(expiredLeft.disabled,'can continue matching after time ends');
 click(el('next'));assert.equal(el('clock').textContent,'15 s');assert.equal(el('next').disabled,true,'timer restarts for each round');
 advance(2000);click(chips[3]);assert.equal(el('clock').textContent,'45 s');s.solve();assert.equal(s.jobs.size,0,'round completion stops timer');
 click(el('next'));click(chips[0]);advance(60000);assert.equal(el('next').disabled,true);assert.equal(s.jobs.size,0);
}
console.log('PASS: both language columns, disjoint shuffled rows, selection, mismatch recovery, locked matches, preserved slots, 2 full 81-card cycles, timers off/10/15/45 and calm expiry.');

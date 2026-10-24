// Exercise the complete production script, including real handlers and scheduled callbacks.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const html=fs.readFileSync(process.env.COPPIE_HTML_PATH||path.resolve(__dirname,'../coppie.html'),'utf8');
function setup(random=Math.random){
 const elements=new Map(), jobs=new Map();let now=0, sequence=0;
 function element(){const classes=new Set();return {textContent:'',disabled:false,children:[],dataset:{},attributes:{},className:'',classList:{add(...names){names.forEach(n=>classes.add(n))},remove(...names){names.forEach(n=>classes.delete(n))},contains(n){return classes.has(n)}},setAttribute(k,v){this.attributes[k]=v},appendChild(c){this.children.push(c)},replaceChildren(...c){this.children=c},addEventListener(k,fn){this['on'+k]=fn}}}
 const chips=[...html.matchAll(/data-seconds="(\d+)" aria-pressed="(true|false)"/g)].map(m=>{const e=element();e.dataset.seconds=m[1];e.setAttribute('aria-pressed',m[2]);return e});
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
 const drawn=JSON.parse(run('JSON.stringify(round)'));
 for(let n=0;n<32;n++){click(el('next'));const ids=el('english').children.map(t=>t.dataset.pair);assert.equal(new Set(ids).size,5);ids.forEach((id,i)=>assert.notEqual(id,el('italian').children[i].dataset.pair));drawn.push(...JSON.parse(run('JSON.stringify(round)')));s.solve()}
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
// Picker handlers must reset all round state and isolate the pool to checked decks.
{
 const {run,el,click,jobs}=setup(()=>0);
 const inputs=run('deckInputs');
 assert.deepEqual(Array.from(inputs).filter(i=>i.checked).map(i=>i.value),['18-ott']);
 function select(ids){for(const input of inputs)input.checked=ids.includes(input.value);inputs[0].onchange();}
 select(['14-ott','7-ott']);
 assert.equal(run('PAIRS.length'),run("new Set(DECKS.filter(d=>['14-ott','7-ott'].includes(d.id)).flatMap(d=>d.pairs.map(p=>JSON.stringify(p.map(w=>w.toLowerCase()))))).size"));
 assert.equal(run("PAIRS.some(p=>p[0]==='il cuore'&&p[1]==='heart')"),false);
 assert.equal(run("PAIRS.some(p=>p[0]==='I signori desiderano?')"),true);
 for(let n=0;n<40;n++){
  const pairs=run('round.map(id=>PAIRS[id])');
  assert.equal(new Set(pairs.map(p=>p[0].toLowerCase())).size,5);
  assert.equal(new Set(pairs.map(p=>p[1].toLowerCase())).size,5);
  click(el('next'));run('newRound()');
 }
 select(['verbi-forme']);assert.equal(run('PAIRS.length'),168);
 select([]);assert.equal(el('english').children.length,0);assert.equal(el('count').textContent,'0 / 0');assert.equal(el('next').disabled,true);assert.equal(jobs.size,0);assert.match(el('feedback').textContent,/Scegli/);
 click(run('chips[1]'));assert.equal(jobs.size,0,'empty selection must not start timer');
 select(['18-ott']);assert.equal(el('english').children.length,5);assert.equal(jobs.size,1);
 click(el('english').children[0]);click(el('italian').children.find(t=>t.dataset.pair!==el('english').children[0].dataset.pair));
 assert.equal(run('busy'),true);select(['14-ott']);assert.equal(run('busy'),false);assert.equal(run('mismatch'),null);assert.equal(run('matched.size'),0);assert.equal(jobs.size,1);
 select(['18-ott','14-ott','7-ott','vocabolario','100parole-2','verbi-forme']);
 for(let n=0;n<400;n++){run('newRound()');const pairs=run('round.map(id=>PAIRS[id])');assert.equal(pairs.length,5);assert.equal(new Set(pairs.map(p=>p[0].toLowerCase())).size,5);assert.equal(new Set(pairs.map(p=>p[1].toLowerCase())).size,5);}
}
console.log('PASS: both language columns, disjoint shuffled rows, selection, mismatch recovery, locked matches, preserved slots, 2 full 81-card cycles, timers off/10/15/45 and calm expiry.');

// New vocabulary must be reachable through the real checkbox handlers.
{
 const expected=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../tests/lesson-24-ott-decks.json'),'utf8'));
 const {run,el,click,solve}=setup(()=>0);
 const inputs=run('deckInputs');
 for(const deck of expected){
  assert.equal(Array.from(inputs).filter(i=>i.value===deck.id).length,1,'selectable '+deck.id);
  for(const input of inputs)input.checked=input.value===deck.id;
  inputs.find(input=>input.value===deck.id).onchange();
  assert.equal(run('JSON.stringify(PAIRS)'),JSON.stringify(deck.pairs));
  const seen=new Set();
  for(let n=0;n<deck.pairs.length;n++){
   for(const tile of el('italian').children){seen.add(tile.textContent);assert(deck.pairs.some(pair=>pair[0]===tile.textContent));}
   solve();assert.equal(el('next').disabled,false);click(el('next'));
  }
  assert.equal(seen.size,deck.pairs.length,'every word is reachable in '+deck.id);
 }
 for(const input of inputs)input.checked=expected.some(d=>d.id===input.value);
 inputs[0].onchange();assert.equal(run('PAIRS.length'),expected.reduce((count,deck)=>count+deck.pairs.length,0));
 for(let n=0;n<100;n++){
  const pairs=run('round.map(id=>PAIRS[id])');assert.equal(pairs.length,5);
  assert.equal(new Set(pairs.map(p=>p[0].toLowerCase())).size,5);assert.equal(new Set(pairs.map(p=>p[1].toLowerCase())).size,5);
  solve();click(el('next'));
 }
}
console.log('PASS: new Coppie decks selectable separately and together, full word coverage and unambiguous matches.');

// Tutto derives its union from every deck, including appended October pairs.
{
 const {run,el}=setup(()=>0);
 const all=run("deckInputs.find(input=>input.value==='tutto')");
 all.checked=true;all.onchange();
 const expected=run('uniquePairs(DECKS).length');
 assert.equal(run('PAIRS.length'),expected);
 assert.equal(el('selection-count').textContent,'Tutto · '+expected+' carte');
 assert.equal(run("deckInputs.filter(input=>input.checked).length"),1);
 for(const spec of JSON.parse(fs.readFileSync(path.resolve(__dirname,'lesson-24-ott-more.json'),'utf8'))){
  for(const pair of spec.pairs)assert.equal(run('PAIRS.some(p=>p[0]==='+JSON.stringify(pair[0])+')'),true);
 }
 const first=run("deckInputs.find(input=>input.value==='18-ott')");
 first.checked=true;first.onchange();assert.equal(all.checked,false);assert.equal(run('PAIRS.length'),81);
}
console.log('PASS: Tutto dynamically unions all decks and remains mutually exclusive.');

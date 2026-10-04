const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Node{constructor(tag='div'){this.tagName=tag;this.children=[];this.attributes={};this.style={};this.value='';this.textContent='';this.disabled=false;this.hidden=false;this.className='';this.classList={toggle:()=>{}};}appendChild(n){this.children.push(n);if(n.tagName==='option'&&this.children.length===1)this.value=n.value;return n;}replaceChildren(...children){this.children=children;this.textContent='';}setAttribute(k,v){this.attributes[k]=v;}}
function load(file){const nodes={};const get=id=>nodes[id]||(nodes[id]=new Node());get('method').value='choose';const ctx=vm.createContext({document:{getElementById:get,createElement:t=>new Node(t),createTextNode:t=>({textContent:t}),addEventListener:()=>{}},console,Math});const script=fs.readFileSync(file,'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];vm.runInContext(script,ctx);return {nodes,ctx,run:s=>vm.runInContext(s,ctx)};}
const dir=require('node:path').resolve(__dirname,'..');
const {nodes,run}=load(dir+'/articoli-esercizi.html');
assert.equal(run('ITEMS.length'),80);assert.equal(nodes['noun-table'].children.length,20);
assert.equal(run('new Set(ITEMS.map(i=>i.form+":"+i.word)).size'),80);
const expected={bambino:['il','i','un','dei'],signore:['il','i','un','dei'],amico:['l’','gli','un','degli'],studente:['lo','gli','uno','degli'],gnocco:['lo','gli','uno','degli'],pneumatico:['lo','gli','uno','degli'],psicologo:['lo','gli','uno','degli'],xilofono:['lo','gli','uno','degli'],yogurt:['lo','gli','uno','degli'],zaino:['lo','gli','uno','degli'],bambina:['la','le','una','delle'],moglie:['la','le','una','delle'],amica:['l’','le','un’','delle'],paga:['la','le','una','delle'],chirurgo:['il','i','un','dei'],bottiglia:['la','le','una','delle'],portafoglio:['il','i','un','dei'],borsa:['la','le','una','delle'],chiave:['la','le','una','delle'],bicchiere:['il','i','un','dei']};
for(const [word,answers] of Object.entries(expected))assert.equal(run(`JSON.stringify(ITEMS.filter(i=>i.noun.sg===${JSON.stringify(word)}).map(i=>i.answer))`),JSON.stringify(answers));
run('submit("")');assert.equal(run('total'),0);assert.match(nodes.feedback.textContent,/Scrivi/);
run('submit("sbagliato")');assert.equal(run('total'),1);assert.equal(run('correct'),0);assert.equal(nodes.feedback.className,'feedback bad');assert.equal(nodes.next.disabled,false);assert.ok(nodes.choices.children.every(b=>b.disabled));
run('submit(order[pos].answer)');assert.equal(run('total'),1);assert.equal(run('correct'),0);
nodes.shuffle.onclick();assert.equal(run('total'),0);assert.equal(nodes.next.disabled,true);
// A: choose every correct article; assert feedback, progress, end screen, and double-submit protection.
for(let i=0;i<80;i++){const right=run('order[pos].answer');const btn=nodes.choices.children.find(b=>b.textContent===right);assert.ok(btn);btn.onclick();assert.equal(run('total'),i+1);assert.equal(run('correct'),i+1);assert.equal(nodes.feedback.className,'feedback good');btn.onclick();assert.equal(run('total'),i+1);nodes.next.onclick();}
assert.equal(nodes.phrase.textContent,'Sessione finita.');assert.equal(nodes.progress.style.width,'100%');assert.equal(nodes.next.disabled,true);
// A: typing path accepts ASCII apostrophes and ignores trailing punctuation and case.
nodes.shuffle.onclick();nodes.method.value='type';nodes.method.onchange();assert.equal(nodes['answer-form'].hidden,false);assert.equal(nodes.choices.hidden,true);
nodes.answer.value=run('order[pos].answer').replace(/’/g,"'").toUpperCase()+'.';nodes['answer-form'].onsubmit({preventDefault(){}});assert.equal(run('correct'),1);
// B: every shown phrase must be wrong; corrected phrases may use either apostrophe style.
nodes['mode-b'].onclick();assert.equal(nodes['input-method'].hidden,true);assert.equal(run('total'),0);
for(let i=0;i<80;i++){assert.notEqual(run('norm(join(wrongFor(order[pos]),order[pos].word))'),run('norm(join(order[pos].answer,order[pos].word))'));assert.equal(nodes.phrase.textContent,run('join(wrongFor(order[pos]),order[pos].word)'));nodes.answer.value=run('join(order[pos].answer,order[pos].word)').replace(/’/g,"'");nodes['answer-form'].onsubmit({preventDefault(){}});assert.equal(run('correct'),i+1);nodes.next.onclick();}
assert.equal(nodes.phrase.textContent,'Sessione finita.');assert.equal(run(`norm("  UN ’ AMICA.  ")`),"un'amica");
const pack=load(dir+'/index.html');
assert.equal(pack.run('ALL.length'),945);assert.equal(pack.run('groups[0][0]'),'aug-26-interrogativi');
assert.equal(pack.run('ALL.filter(c=>matches(c,"grammar-articoli")).length'),26);
assert.equal(pack.run('ALL.filter(c=>matches(c,"lisa-irregolari")).some(c=>c.group.includes("Chiara"))'),false);
assert.equal(pack.run('ALL.filter(c=>matches(c,"chiara-23-sett")).some(c=>c.group.includes("Lisa"))'),false);
pack.nodes.filter.value='grammar-articoli';pack.nodes.filter.onchange();assert.equal(pack.nodes.direction.disabled,true);assert.equal(pack.nodes.dirText.textContent,'IT→EN');
pack.nodes.direction.onclick();assert.equal(pack.nodes.dirText.textContent,'IT→EN');
console.log('PASS: 80 expected forms; all 160 A/B answers; choices, typing, corrections, feedback, score, shuffle, finish, apostrophes; 945-card pack ownership/direction.');

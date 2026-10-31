// Run the actual card picker, filtering and rendering for standalone and embedded pages.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const expected=[
 ['21-ott-mangiare','21 ott · mangiare',38],
 ['24-ott-corpo','24 ott · corpo',100],
 ['24-ott-terra','24 ott · terra',100],
 ['24-ott-casa','24 ott · casa',100],
 ['25-ott-foto','25 ott · foto',9],
 ['25-ott-dante','25 ott · Dante',130],
 ['27-ott-frasi','27 ott · frasi',19]
];
const decks=JSON.parse(fs.readFileSync(path.join(root,'coppie.html'),'utf8').match(/const DECKS=([^\n]+);/)[1]);
function load(source){
 const elements=new Map();
 function element(){return {value:'',textContent:'',disabled:false,style:{setProperty(){}},children:[],dataset:{},classList:{toggle(){},add(){},remove(){}},setAttribute(){},appendChild(c){this.children.push(c)},addEventListener(k,fn){this['on'+k]=fn}}}
 const document={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},createElement:element,addEventListener(){}};
 const context=vm.createContext({document,location:{hash:''},Math,Date,setTimeout(){},clearTimeout(){}});
 vm.runInContext(source.match(/<script>([\s\S]*?)<\/script>/)[1],context);
 return {run:s=>vm.runInContext(s,context),el:id=>document.getElementById(id)};
}
for(const folder of ['', 'www', 'anki-html']){
 const page=fs.readFileSync(path.join(root,folder,'italiano-flashcards.html'),'utf8');
 const hub=fs.readFileSync(path.join(root,folder,'index.html'),'utf8');
 const embedded=JSON.parse(hub.match(/id="app-carte">([\s\S]*?)<\/script>/)[1]);
 for(const [kind,source] of [['standalone',page],['embedded',embedded]]){
  const cards=load(source),options=cards.el('filter').children;
  assert.equal(cards.el('filter').value,'18-ott','keep the existing default');
  assert(cards.run('groups.every(g=>g.length===2)'),'picker entries must have one id and one label');
  assert.equal(cards.run('groups.length'),options.length,'no empty picker entries');
  const voc=options.findIndex(o=>o.value==='vocabolario');
  assert.deepEqual(options.slice(voc+1).map(o=>[o.value,o.textContent]),expected.map(([id,label])=>[id,label]),`${folder}/${kind}: dated decks follow Vocabolario`);
  cards.run("filter.value='vocabolario';filter.onchange()");
  assert.equal(cards.el('filter').value,'vocabolario');
  for(const [id,label,count] of expected){
   const pairs=decks.find(d=>d.id===id).pairs;
   assert.equal(pairs.length,count);
   assert.equal(options.filter(o=>o.value===id&&o.textContent===label).length,1);
   cards.run(`filter.value=${JSON.stringify(id)};filter.onchange()`);
   assert.equal(cards.run('pool.length'),count);
   assert.equal(cards.run('JSON.stringify(pool.map(c=>[c.it,c.other]))'),JSON.stringify(pairs));
   for(let i=0;i<count;i++){
    cards.run(`index=${i};render()`);
    assert.equal(cards.el('frontWord').textContent,pairs[i][0]);
    assert.equal(cards.el('backWord').textContent,pairs[i][1]);
   }
  }
 }
}
console.log('PASS: seven dated groups after Vocabolario; 496 exact pairs render in all standalone/embedded pickers; default unchanged.');

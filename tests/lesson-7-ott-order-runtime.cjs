// Exercise the production shuffler: the 48 new cards stay stable and on top.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const html=fs.readFileSync(process.env.CARD_HTML_PATH||path.resolve(__dirname,'../italiano-flashcards.html'),'utf8');
const start=html.indexOf('const ALL=')+'const ALL='.length;
const cards=JSON.parse(html.slice(start,html.indexOf(';\nconst $=',start)));
const shuffler=html.slice(html.indexOf('function shufflePool()'),html.indexOf("$('scene').onclick="));
const context=vm.createContext({pool:[],Math:Object.assign(Object.create(Math),{random:()=>0})});
vm.runInContext(shuffler,context);
const lesson=cards.filter(c=>c.group==='7 ott');
assert.equal(lesson.length,48);
assert.equal(lesson[0].it,'un panino con prosciutto e formaggio');
for(const mode of process.env.ORDER_CASE?[process.env.ORDER_CASE]:['lesson','global']){
 context.pool=mode==='lesson'?lesson.slice():cards.slice();
 for(let n=0;n<4;n++){
  vm.runInContext('shufflePool()',context);
  assert.equal(JSON.stringify(context.pool.slice(0,48)),JSON.stringify(lesson),mode+' new cards must stay first in sheet order');
  assert.equal(context.pool.slice(48).some(c=>c.group==='7 ott'),false);
  assert.equal(context.pool.length,mode==='lesson'?48:1492);
 }
}
console.log('PASS: stable lesson order and contiguous first block through repeated global shuffles.');

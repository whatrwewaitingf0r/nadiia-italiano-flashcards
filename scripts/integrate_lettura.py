"""Add Lettura to the CURRENT hub/cards without rebuilding from an old v29 file.

Idempotent for this reading dataset. Every other card/tab is retained. Companion
lesson builders must re-run this after writing their files, never restore v29.
"""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
CANON=Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')

def embed(h,key,app):
    payload=json.dumps(app,ensure_ascii=False).replace('<','\\u003c')
    pattern=r'(<script type="application/json" id="app-'+key+r'">)[\s\S]*?(</script>)'
    h,n=re.subn(pattern,lambda m:m[1]+payload+m[2],h,count=1)
    if not n:
        anchor="<script>\n'use strict';"
        assert anchor in h,'Unknown hub: cannot locate main script'
        h=h.replace(anchor,f'<script type="application/json" id="app-{key}">{payload}</script>\n'+anchor,1)
    return h

def integrate():
    old_html=(ROOT/'italiano-flashcards.html').read_text()
    old_hub=(ROOT/'index.html').read_text()
    reading=json.loads((ROOT/'liam-lettura.json').read_text())
    start=old_html.index('const ALL=')+len('const ALL=')
    cards,size=json.JSONDecoder().raw_decode(old_html[start:])
    # Lesson 5 was explicitly removed in v32; never resurrect its archived cards.
    retained=[c for c in cards if not c.get('reading','').startswith('lettura-')]
    result=retained+reading['cards']
    h=old_html[:start]+json.dumps(result,ensure_ascii=False,separators=(',',':'))+old_html[start+size:]
    if "['liam-lettura','Liam · Lettura']" not in h:
        h=h.replace('const groups=[','const groups=[\n',1)
        # Insert before the first Lisa group, after all existing Liam groups.
        marker=" ['lisa-irregolari','Lisa · irregolari'],"
        assert marker in h
        h=h.replace(marker," ['liam-lettura','Liam · Lettura'],\n"+marker,1)
    if "'liam-lettura':'Liam · Lettura'" not in h:
        h=h.replace('const byFilter={',"const byFilter={\n  'liam-lettura':'Liam · Lettura',",1)
    if 'const isReading=' not in h:
        h=h.replace('function render(){const c=pool[index];if(!c)return;',"function render(){const c=pool[index];if(!c)return;\n const isReading=Boolean(c.reading);\n $('scene').classList.toggle('reading-card',isReading);",1)
        h=h.replace('if(isLisa||isChiara23||isGrammar)reverse=false;','if(isLisa||isChiara23||isGrammar||isReading)reverse=false;',1)
        h=h.replace("$('direction').disabled=isLisa||isChiara23||isGrammar;","$('direction').disabled=isLisa||isChiara23||isGrammar||isReading;",1)
        h=h.replace("$('frontWord').textContent=first;$('backWord').textContent=second;","$('frontWord').textContent=c.kind==='reading'?c.sourceText:first;$('backWord').textContent=second;\n $('frontWord').scrollTop=0;$('backWord').scrollTop=0;",1)
        marker="$('frontNote').textContent=c.group;$('backNote').textContent=c.note;"
        assert marker in h
        h=h.replace(marker,marker+"\n if(isReading){$('frontLabel').textContent=c.kind==='reading'?'Testo originale · lettura':c.kind==='truefalse'?'Vero o falso?':'Liam · lettura';$('backLabel').textContent='English · study response';}",1)
    if '.scene.reading-card{' not in h:
        css='\n.scene.reading-card{min-height:650px}.reading-card .face{padding:60px 22px 110px;justify-content:flex-start}.reading-card .word,.reading-card .back .word{font-size:1rem;line-height:1.6;font-weight:550;letter-spacing:0;text-align:left;white-space:pre-wrap;overflow-y:auto;overscroll-behavior:contain;width:100%;max-height:480px;user-select:text}.reading-card .note{font-size:.7rem;line-height:1.3;max-height:75px;overflow-y:auto}\n'
        h=h.replace('</style>',css+'</style>',1)
    if 'href="liam-lettura.html"' not in h:
        h=h.replace('</main>','<p style="text-align:center"><a href="liam-lettura.html" style="color:var(--laguna);font-weight:750">Liam · Lettura integrale →</a></p>\n</main>',1)
    hub=old_hub
    if 'id="tab-lettura"' not in hub:
        hub=hub.replace('</nav></header>','<button type="button" id="tab-lettura" role="tab" aria-controls="panel-lettura" aria-selected="false" tabindex="-1" data-app="lettura">Lettura</button>\n</nav></header>',1)
        marker='</div>\n<noscript>'
        assert marker in hub
        hub=hub.replace(marker,'<section class="panel" id="panel-lettura" role="tabpanel" aria-labelledby="tab-lettura" hidden><div class="loading" id="loading-lettura" role="status">Prepariamo la lettura…</div><iframe id="frame-lettura" title="Liam · lettura completa"></iframe></section>\n'+marker,1)
        hub=hub.replace('</noscript>','<a href="liam-lettura.html">Lettura</a>\n</noscript>',1)
    m=re.search(r'const keys=(\[[^;]+\]);',hub);assert m
    keys=json.loads(m[1].replace("'",'"'))
    if 'lettura' not in keys:keys.append('lettura')
    hub=hub[:m.start(1)]+json.dumps(keys,separators=(',',':'))+hub[m.end(1):]
    if "'liam-lettura.html':'lettura'" not in hub:
        hub=hub.replace('const routes={',"const routes={'liam-lettura.html':'lettura',",1)
    # Horizontal mobile navigation remains usable as additive tabs accumulate.
    if '/* additive-reading-tabs */' not in hub:
        hub=hub.replace('</style>','/* additive-reading-tabs */\n.tabs{display:flex;overflow-x:auto;overscroll-behavior-x:contain}.tabs button{flex:1 0 90px}.tabs button:focus{scroll-margin-inline:8px}\n</style>',1)
    hub=embed(hub,'carte',h)
    hub=embed(hub,'lettura',(ROOT/'liam-lettura.html').read_text())
    # Cheap race guard: a concurrent writer must not be silently overwritten.
    assert (ROOT/'italiano-flashcards.html').read_text()==old_html,'Concurrent flashcard edit; re-coordinate before integration'
    assert (ROOT/'index.html').read_text()==old_hub,'Concurrent hub edit; re-coordinate before integration'
    outputs={'italiano-flashcards.html':h,'index.html':hub,'liam-lettura.html':(ROOT/'liam-lettura.html').read_text(),'liam-lettura.json':(ROOT/'liam-lettura.json').read_text()}
    for name,content in outputs.items():
        for base in [ROOT,ROOT/'www',ROOT/'anki-html',CANON,CANON/'www']:
            (base/name).write_text(content)
    print(json.dumps(dict(cards=len(result),readingCards=len(reading['cards']),tabs=keys),indent=2))

if __name__=='__main__':integrate()

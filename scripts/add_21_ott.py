"""Append the supplied food/prices lesson without changing existing Italian identities."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')


def replace_json(source, marker, value):
    before, after = source.split(marker, 1)
    _, end = json.JSONDecoder().raw_decode(after)
    return before + marker + json.dumps(value, ensure_ascii=False, separators=(',', ':')) + after[end:]


def embed(hub, page, coppie):
    hub = hub.replace('v57', 'v58').replace('?v=57', '?v=58')
    hub = hub.replace("(['carte','coppie'].includes(key)?57:", "(['carte','coppie'].includes(key)?58:")
    for key, source in [('carte', page), ('coppie', coppie)]:
        payload = json.dumps(source, ensure_ascii=True).replace('<', '\\u003c')
        hub = re.sub(r'(<script type="application/json" id="app-' + key + r'">)[\s\S]*?(</script>)', lambda m: m[1] + payload + m[2], hub)
    return hub


def main():
    spec = json.loads((ROOT / 'tests/lesson-21-ott-deck.json').read_text())
    page = (ROOT / 'italiano-flashcards.html').read_text()
    coppie = (ROOT / 'coppie.html').read_text()
    cards = json.JSONDecoder().raw_decode(page.split('const ALL=', 1)[1])[0]
    decks = json.JSONDecoder().raw_decode(coppie.split('const DECKS=', 1)[1])[0]
    if any(d['id'] == spec['id'] for d in decks):
        raise SystemExit('21 October deck already exists; no files changed')
    seen = {c['it'].casefold() for c in cards} | {it.casefold() for d in decks for it, _ in d['pairs']}
    pairs, skipped = [], []
    for it, en in spec['pairs']:
        if it.casefold() in seen:
            skipped.append(it)
            continue
        pairs.append([it, en])
        cards.append(dict(it=it, other=en, lang='EN', group=spec['label'], note='', tags=[spec['id']]))
        seen.add(it.casefold())
    decks.append(dict(id=spec['id'], label=spec['label'], pairs=pairs))
    page = replace_json(page, 'const ALL=', cards)
    coppie = replace_json(coppie, 'const DECKS=', decks)
    page = page.replace(" ['25-ott-dante','25 ott · Dante'],\n", " ['25-ott-dante','25 ott · Dante'],\n ['21-ott-mangiare','21 ott · mangiare'],\n")
    page = page.replace("  '25-ott-dante':'25 ott · Dante',\n", "  '25-ott-dante':'25 ott · Dante',\n  '21-ott-mangiare':'21 ott · mangiare',\n")
    page = page.replace("'25-ott-foto','25-ott-dante']", "'25-ott-foto','25-ott-dante','21-ott-mangiare']")
    page = page.replace("'25 ott · foto','25 ott · Dante']", "'25 ott · foto','25 ott · Dante','21 ott · mangiare']")
    page = page.replace('v55', 'v58').replace('?v=55', '?v=58')
    coppie = coppie.replace('v57', 'v58').replace('?v=57', '?v=58')
    hub = embed((ROOT / 'index.html').read_text(), page, coppie)
    for folder in [ROOT, ROOT / 'www', ROOT / 'anki-html', CANON, CANON / 'www']:
        for name, source in [('italiano-flashcards.html', page), ('coppie.html', coppie), ('index.html', hub)]:
            (folder / name).write_text(source)
    print('Added:', len(pairs))
    print('Skipped:', ', '.join(skipped))


if __name__ == '__main__':
    main()

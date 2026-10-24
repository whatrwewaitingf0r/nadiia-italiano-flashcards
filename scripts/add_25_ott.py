"""Append the supplied 25 October decks, deduplicating exact Italian identities."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')


def replace_json(source, marker, value):
    before, after = source.split(marker, 1)
    _, end = json.JSONDecoder().raw_decode(after)
    return before + marker + json.dumps(value, ensure_ascii=False, separators=(',', ':')) + after[end:]


def main():
    requested = json.loads((ROOT / 'tests/lesson-25-ott-decks.json').read_text())
    page = (ROOT / 'italiano-flashcards.html').read_text()
    coppie = (ROOT / 'coppie.html').read_text()
    cards = json.JSONDecoder().raw_decode(page.split('const ALL=', 1)[1])[0]
    decks = json.JSONDecoder().raw_decode(coppie.split('const DECKS=', 1)[1])[0]
    seen = {c['it'].casefold() for c in cards} | {it.casefold() for d in decks for it, _ in d['pairs']}
    skipped = []
    for spec in requested:
        if any(d['id'] == spec['id'] for d in decks):
            continue
        pairs = []
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
    for spec in requested:
        option = f" ['{spec['id']}','{spec['label']}'],\n"
        mapping = f"  '{spec['id']}':'{spec['label']}',\n"
        page = page.replace(option, '').replace(mapping, '')
    page = page.replace(" ['24-ott-casa','24 ott · casa'],\n", " ['24-ott-casa','24 ott · casa'],\n" + ''.join(f" ['{d['id']}','{d['label']}'],\n" for d in requested))
    page = page.replace("  '24-ott-casa':'24 ott · casa',\n", "  '24-ott-casa':'24 ott · casa',\n" + ''.join(f"  '{d['id']}':'{d['label']}',\n" for d in requested))
    # Match the dated 24 October decks: retain exact sheet order, including after shuffle.
    for field in ['id', 'label']:
        old = ["18-ott", "14-ott", "7-ott", "24-ott-corpo", "24-ott-terra", "24-ott-casa"] if field == 'id' else ['18 ott', '14 ott', '7 ott', '24 ott · corpo', '24 ott · terra', '24 ott · casa']
        old_literal = '[' + ','.join(repr(v) for v in old) + ']'
        new_literal = '[' + ','.join(repr(v) for v in old + [d[field] for d in requested]) + ']'
        page = page.replace(old_literal, new_literal)
    def version(source):
        return source.replace('v54', 'v55').replace('?v=54', '?v=55')
    page, coppie = version(page), version(coppie)
    hub = version((ROOT / 'index.html').read_text()).replace("(['carte','coppie'].includes(key)?54:", "(['carte','coppie'].includes(key)?55:")
    for key, source in [('carte', page), ('coppie', coppie)]:
        payload = json.dumps(source, ensure_ascii=True).replace('<', '\\u003c')
        hub = re.sub(r'(<script type="application/json" id="app-' + key + r'">)[\s\S]*?(</script>)', lambda m: m[1] + payload + m[2], hub)
    for folder in [ROOT, ROOT / 'www', ROOT / 'anki-html', CANON, CANON / 'www']:
        for name, source in [('italiano-flashcards.html', page), ('coppie.html', coppie), ('index.html', hub)]:
            (folder / name).write_text(source)
    print({d['id']: len(next(deck['pairs'] for deck in decks if deck['id'] == d['id'])) for d in requested})
    print('Skipped:', ', '.join(skipped))


if __name__ == '__main__':
    main()

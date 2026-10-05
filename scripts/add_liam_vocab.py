"""Append missing source-backed vocabulary without replacing any existing card."""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')


def aliases(text):
    text = unicodedata.normalize('NFKC', text).casefold().replace('’', "'")
    text = re.sub(r'\([^)]*\)', '', text)
    values = set()
    for part in text.split('/'):
        part = re.sub(r"^(?:il|lo|la|gli|le|i|un|uno|una)\s+|^(?:l|un)'", '', part.strip())
        part = re.sub(r'[^\w\s\']', '', part)
        values.add(' '.join(part.split()))
    return values - {''}


def append_missing(cards, candidates):
    result = list(cards)
    seen = set().union(*(aliases(c['it']) for c in cards))
    skipped = []
    for entry in candidates:
        card = entry['card']
        keys = aliases(card['it'])
        if seen & keys:
            skipped.append(card['it'])
            continue
        seen.update(keys)
        result.append(card)
    assert result[:len(cards)] == cards
    return result, skipped


def main():
    manifest = json.loads((ROOT / 'scripts/liam-vocab-additions.json').read_text())
    primary = ROOT / 'italiano-flashcards.html'
    html = primary.read_text()
    start = html.index('const ALL=') + len('const ALL=')
    cards, length = json.JSONDecoder().raw_decode(html[start:])
    baseline_hash = hashlib.sha256(json.dumps(cards[:944], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    assert baseline_hash == 'e33694defb736c5d037df00d1dfbac7d194dccc289d8ef488db778afdefeafce', 'Retained v32 baseline changed; stop instead of replacing it.'
    lesson5 = [c for c in cards if 'lesson5' in c.get('tags', [])]
    assert not lesson5, 'Lesson 5 was removed in v32.'
    merged, skipped = append_missing(cards, manifest['candidates'])
    updated = html[:start] + json.dumps(merged, ensure_ascii=False, separators=(',', ':')) + html[start+length:]
    # Refuse a stale write if another worker changes the same file during preparation.
    assert primary.read_text() == html, 'Concurrent flashcard update; rerun on the current file.'
    for base in [ROOT, ROOT / 'www', ROOT / 'anki-html', CANON, CANON / 'www']:
        (base / 'italiano-flashcards.html').write_text(updated)
    hub_path = ROOT / 'index.html'
    hub = hub_path.read_text()
    payload = json.dumps(updated, ensure_ascii=False).replace('<', '\\u003c')
    embedded, count = re.subn(r'(<script type="application/json" id="app-carte">)[\s\S]*?(</script>)',
                              lambda match: match[1] + payload + match[2], hub)
    assert count == 1
    assert hub_path.read_text() == hub, 'Concurrent hub update; rerun after merge.'
    for base in [ROOT, ROOT / 'www', ROOT / 'anki-html', CANON, CANON / 'www']:
        (base / 'index.html').write_text(embedded)
    report = {'before': len(cards), 'after': len(merged), 'added': len(merged)-len(cards),
              'addedFronts': [c['it'] for c in merged[len(cards):]], 'skipped': skipped,
              'retainedV32BaselinePreserved': True, 'lesson5': len(lesson5)}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

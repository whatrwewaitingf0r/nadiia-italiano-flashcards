"""24 October articles: exact vocabulary, preserved payloads, release copies."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = {'24-ott-corpo': '24 ott · corpo', '24-ott-terra': '24 ott · terra', '24-ott-casa': '24 ott · casa'}
EXPECTED = json.loads((ROOT / 'tests/lesson-24-ott-articles.json').read_text())

def data(name, token):
    return json.JSONDecoder().raw_decode((ROOT / name).read_text().split(token, 1)[1])[0]

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def bare(word):
    return re.sub(r"^(?:(?:il|lo|la|i|gli|le|un) |l['’])", '', word)

class Articles24Tests(unittest.TestCase):
    def test_exact_articles_and_preserved_data(self):
        decks = data('coppie.html', 'const DECKS=')
        cards = data('italiano-flashcards.html', 'const ALL=')
        for deck_id, group in TARGET.items():
            deck, = [d for d in decks if d['id'] == deck_id]
            lesson = [c for c in cards if c['group'] == group]
            self.assertEqual(len(deck['pairs']), 100)
            self.assertEqual([it for it, _ in deck['pairs']], EXPECTED[deck_id])
            self.assertEqual([[c['it'], c['other']] for c in lesson], deck['pairs'])
        # Removing only the new target articles must recover every original field/order.
        for d in decks:
            if d['id'] in TARGET:
                d['pairs'] = [[bare(it), en] for it, en in d['pairs']]
        for c in cards:
            if c['group'] in TARGET.values():
                c['it'] = bare(c['it'])
        self.assertEqual(digest(decks), 'e6520b57df131ad39f8da9f7882664179c33cb589ca35761dde7cf42a11b1694')
        self.assertEqual(digest(cards), '4543a6684ebd1b78bf29ce08402b50515a94d23d75e4b7f834d2f5c34c379f8a')

    def test_release_copies_payloads_version_and_color(self):
        hub = (ROOT / 'index.html').read_text()
        for key, name in [('carte', 'italiano-flashcards.html'), ('coppie', 'coppie.html')]:
            source = (ROOT / name).read_text()
            payload = re.search(r'<script type="application/json" id="app-' + key + r'">([\s\S]*?)</script>', hub)[1]
            self.assertEqual(json.loads(payload), source)
            self.assertIn(name + '?v=54', hub)
        for name in ['index.html', 'coppie.html', 'italiano-flashcards.html']:
            content = (ROOT / name).read_bytes()
            self.assertIn(b'content="v54"', content)
            for folder in [ROOT / 'www', ROOT / 'anki-html']:
                self.assertEqual((folder / name).read_bytes(), content)
        self.assertIn("(['carte','coppie'].includes(key)?54:", hub)
        self.assertIn('index.html?v=54#carte', (ROOT / 'coppie.html').read_text())
        self.assertIn('.tile.selected{background:#3d4f68;border-color:#d7c4a3;color:#f4efe4}', (ROOT / 'coppie.html').read_text())

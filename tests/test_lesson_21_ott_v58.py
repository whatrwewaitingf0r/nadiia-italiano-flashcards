"""21 October food/prices: exact identities, untouched old decks, synchronized release."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')
SPEC = json.loads((ROOT / 'tests/lesson-21-ott-deck.json').read_text())
SKIPPED = ['cenare', 'il pranzo', 'fare colazione', 'pranzare', 'allora', 'la bruschetta', 'il tiramisù', 'le patatine fritte', 'il cornetto', 'la birra', 'il cappuccino', 'il gelato']


def data(name, token):
    return json.JSONDecoder().raw_decode((ROOT / name).read_text().split(token, 1)[1])[0]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class Lesson21Tests(unittest.TestCase):
    def test_exact_new_deck_and_preserved_baseline(self):
        cards = data('italiano-flashcards.html', 'const ALL=')
        decks = data('coppie.html', 'const DECKS=')
        old_cards = [c for c in cards if c['group'] != SPEC['label']]
        old_decks = [d for d in decks if d['id'] != SPEC['id']]
        self.assertEqual(digest(old_cards), '225ad2806b15c2f183ebcc59f8bf9cf43a1af58d66ee1b5436a039690e33ef34')
        self.assertEqual(digest(old_decks), 'dbfc99e197fc8340db9e697415a5d2117a2f00d25d717a53891a34253f23a6f3')
        self.assertEqual(cards[:len(old_cards)], old_cards)
        self.assertEqual(decks[:len(old_decks)], old_decks)
        seen = {c['it'].casefold() for c in old_cards} | {p[0].casefold() for d in old_decks for p in d['pairs']}
        self.assertEqual([it for it, _ in SPEC['pairs'] if it.casefold() in seen], SKIPPED)
        expected = [[it, en] for it, en in SPEC['pairs'] if it.casefold() not in seen]
        self.assertEqual(len(expected), 38)
        self.assertEqual([d for d in decks if d['id'] == SPEC['id']], [dict(id=SPEC['id'], label=SPEC['label'], pairs=expected)])
        self.assertEqual([c for c in cards if c['group'] == SPEC['label']], [dict(it=it, other=en, lang='EN', group=SPEC['label'], note='', tags=[SPEC['id']]) for it, en in expected])
        for it, _ in expected:
            self.assertEqual(sum(c['it'].casefold() == it.casefold() for c in cards), 1, it)
            self.assertEqual(sum(p[0].casefold() == it.casefold() for d in decks for p in d['pairs']), 1, it)
        house = next(d for d in decks if d['id'] == '24-ott-casa')
        self.assertTrue({'la cucina', 'la pentola'}.issubset({p[0] for p in house['pairs']}))

    def test_release_copies_embeds_and_cache(self):
        hub = (ROOT / 'index.html').read_text()
        for key, name in [('carte', 'italiano-flashcards.html'), ('coppie', 'coppie.html')]:
            payload = re.search(r'<script type="application/json" id="app-' + key + r'">([\s\S]*?)</script>', hub)[1]
            self.assertEqual(json.loads(payload), (ROOT / name).read_text())
            self.assertIn(name + '?v=58', hub)
        for name in ['index.html', 'italiano-flashcards.html', 'coppie.html']:
            source = (ROOT / name).read_bytes()
            self.assertIn(b'content="v58"', source)
            for folder in [ROOT / 'www', ROOT / 'anki-html', CANON, CANON / 'www']:
                self.assertEqual((folder / name).read_bytes(), source)
        self.assertIn("(['carte','coppie'].includes(key)?58:", hub)
        self.assertIn('index.html?v=58#coppie', (ROOT / 'coppie.html').read_text())

    def test_real_picker_handlers_order_and_defaults(self):
        result = subprocess.run(['node', str(ROOT / 'tests/lesson-21-ott-runtime.cjs')], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

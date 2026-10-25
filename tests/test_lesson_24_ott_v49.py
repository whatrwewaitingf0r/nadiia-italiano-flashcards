"""24 October: the same three isolated EN decks in Carte and Coppie."""
import hashlib
import json
import re
import subprocess
import unittest
from test_hundred_24_ott import original_words
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')


def payload(html, marker):
    return json.JSONDecoder().raw_decode(html.split(marker, 1)[1])[0]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class Lesson24Tests(unittest.TestCase):
    def test_exact_new_cards_and_old_cards_untouched(self):
        cards = original_words(payload((ROOT / 'italiano-flashcards.html').read_text(), 'const ALL='))
        expected = json.loads((ROOT / 'tests/lesson-24-ott-decks.json').read_text())
        self.assertEqual(len(cards), 1973)
        self.assertEqual(digest(cards[:1673]), '47e9df611cbf3f14344244eb9edeb1865850b503a74307971b68cda1960ac2a3')
        seen = {c['it'].casefold() for c in cards[:1673]}
        for deck, count in zip(expected, [100, 100, 100]):
            lesson = [c for c in cards if c['group'] == deck['label']]
            self.assertEqual(len(lesson), count)
            self.assertEqual([[c['it'], c['other']] for c in lesson], deck['pairs'])
            for card in lesson:
                self.assertNotIn(card['it'].casefold(), seen)
                seen.add(card['it'].casefold())
                self.assertEqual(card['lang'], 'EN')
                self.assertEqual(card['tags'], [deck['id']])
                self.assertEqual(card['note'], '')

    def test_matching_decks_preserve_old_pairs_and_selection_color(self):
        html = (ROOT / 'coppie.html').read_text()
        decks = original_words(payload(html, 'const DECKS='))
        expected = json.loads((ROOT / 'tests/lesson-24-ott-decks.json').read_text())
        old = [d for d in decks if not d['id'].startswith('24-ott-')]
        self.assertEqual(digest(old), 'cef379a0b5c966cbb39497431298b1bdb42f15ed63054e34de9d783112105c63')
        seen = {it.casefold() for d in old for it, _ in d['pairs']}
        for deck in expected:
            self.assertEqual([d for d in decks if d['id'] == deck['id']], [deck])
            for it, _ in deck['pairs']:
                self.assertNotIn(it.casefold(), seen)
                seen.add(it.casefold())
        self.assertIn('.tile.selected{background:#3d4f68;border-color:#d7c4a3;color:#f4efe4}', html)

    def test_release_embeds_and_all_five_copies(self):
        apps = {'carte':'italiano-flashcards.html', 'coppie':'coppie.html'}
        hub = (ROOT / 'index.html').read_text()
        for key, name in apps.items():
            embedded = re.search(r'<script type="application/json" id="app-' + key + r'">([\s\S]*?)</script>', hub)[1]
            self.assertEqual(json.loads(embedded), (ROOT / name).read_text())
        for name in ['index.html', *apps.values()]:
            content = (ROOT / name).read_bytes()
            version = b'v55' if name == 'italiano-flashcards.html' else b'v56'
            self.assertIn(b'content="' + version + b'"', content)
            for folder in [ROOT / 'www', ROOT / 'anki-html', CANON, CANON / 'www']:
                self.assertEqual((folder / name).read_bytes(), content)

    def test_real_card_and_matching_picker_handlers(self):
        for name in ['lesson-24-ott-runtime.cjs', 'coppie-runtime.cjs']:
            result = subprocess.run(['node', str(ROOT / 'tests' / name)], capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_new_picker_order(self):
        source = (ROOT / 'italiano-flashcards.html').read_text()
        options = re.search(r'const groups=([\s\S]*?);', source)[1]
        actual = re.findall(r"\['(24-ott-[^']+)','([^']+)'\]", options)
        expected = json.loads((ROOT / 'tests/lesson-24-ott-decks.json').read_text())
        self.assertEqual(actual, [(d['id'], d['label']) for d in expected])

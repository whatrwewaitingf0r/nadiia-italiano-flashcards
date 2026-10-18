"""18 October: one ordered English-only deck, with all older cards frozen."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

class Lesson18Tests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / 'italiano-flashcards.html').read_text()
        self.cards = json.JSONDecoder().raw_decode(self.html.split('const ALL=', 1)[1])[0]

    def test_exact_pairs_order_and_english_only(self):
        expected = json.loads((ROOT / 'tests/lesson-18-ott-pairs.json').read_text())
        lesson = [c for c in self.cards if c['group'] == '18 ott']
        self.assertEqual(len(lesson), 81)
        self.assertEqual([[c['it'], c['other']] for c in lesson], expected)
        self.assertEqual([c['it'] for c in lesson[-4:]], ['il cuore', 'la speranza', 'la pace', 'il fuoco'])
        for card in lesson:
            self.assertEqual(card['lang'], 'EN')
            self.assertEqual(card['tags'], ['18-ott'])
            self.assertNotIn('direction', card)
        self.assertNotRegex(self.html + (ROOT / 'index.html').read_text(), r'[\u0400-\u04ff]|(?i:lettura)')

    def test_all_1592_old_cards_unchanged_and_new_deck_appended(self):
        self.assertEqual(len(self.cards), 1673)
        old = self.cards[:1592]
        self.assertTrue(all(c['group'] == '18 ott' for c in self.cards[1592:]))
        self.assertEqual(hashlib.sha256(json.dumps(old, ensure_ascii=False, sort_keys=True).encode()).hexdigest(), 'a84880b6b68f9583b6425b77d6415df9fc2891d2cbd6c7f5aa4da24faeaa4a9f')

    def test_new_first_default_runtime_toggle_and_isolation(self):
        result = subprocess.run(['node', str(ROOT / 'tests/lesson-18-ott-runtime.cjs')], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_v42_hub_and_synchronized_payloads(self):
        hub = (ROOT / 'index.html').read_text()
        self.assertEqual(re.findall(r'data-app="([^"]+)">', hub), ['carte', 'articoli', 'aggettivi', 'verbi'])
        embedded = re.search(r'<script type="application/json" id="app-carte">([\s\S]*?)</script>', hub)[1]
        self.assertEqual(json.loads(embedded), self.html)
        for name in ['index.html', 'italiano-flashcards.html', 'articoli-esercizi.html', 'articoli-aggettivi.html', 'verbi-tempi.html']:
            content = (ROOT / name).read_bytes()
            self.assertNotRegex(content.decode(), r'\?v=(?!42\b)\d+')
            if name in ['index.html', 'italiano-flashcards.html']:
                self.assertIn(b'content="v42"', content)
            for folder in ['www', 'anki-html']:
                self.assertEqual((ROOT / folder / name).read_bytes(), content)

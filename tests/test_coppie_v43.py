"""Matching pairs release: selected existing decks, unchanged Carte and five hub tabs."""
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class CoppieTests(unittest.TestCase):
    def test_exact_deck_and_offline_page(self):
        html = (ROOT / 'coppie.html').read_text()
        self.assertTrue('const DECKS=' in html, 'deck picker payload missing')
        decks = json.JSONDecoder().raw_decode(html.split('const DECKS=', 1)[1])[0]
        pairs = decks[0]['pairs']
        self.assertEqual([d['id'] for d in decks[:3]], ['18-ott', '14-ott', '7-ott'])
        self.assertGreaterEqual(len(decks), 18)
        self.assertEqual(len(decks[1]['pairs']), 100)
        self.assertEqual(len(decks[2]['pairs']), 48)
        verbs = next(d for d in decks if d['id'] == 'verbi-forme')
        self.assertIn(['io studio', 'presente · I study / I am studying'], verbs['pairs'])
        self.assertFalse(any(d['id'] in ['grammar-verbi', 'aug-26-riordina'] for d in decks))
        self.assertTrue(all(it.strip() and en.strip() and '\n' not in en for d in decks for it,en in d['pairs']))
        self.assertEqual(pairs, json.loads((ROOT / 'tests/lesson-18-ott-pairs.json').read_text()))
        self.assertEqual(len(pairs), 81)
        self.assertNotRegex(html, r'[\u0400-\u04ff]|(?i:duolingo|lettura)|https?://|fetch\(')
        self.assertIn('content="v44"', html)
        self.assertIn('viewport-fit=cover', html)
        self.assertIn('prefers-reduced-motion', html)
        self.assertIn('color-scheme:dark', html)
        self.assertIn('aria-live="polite"', html)

    def test_navigation_five_tabs_and_release_copies(self):
        hub = (ROOT / 'index.html').read_text()
        card = (ROOT / 'italiano-flashcards.html').read_text()
        self.assertEqual(re.findall(r'data-app="([^"]+)">', hub), ['carte', 'articoli', 'aggettivi', 'verbi', 'coppie'])
        self.assertIn('href="coppie.html?v=44" target="_top"', card)
        self.assertIn('>Coppie', card)
        embedded = re.search(r'<script type="application/json" id="app-carte">([\s\S]*?)</script>', hub)[1]
        self.assertEqual(json.loads(embedded), card)
        for file in ['index.html', 'italiano-flashcards.html', 'articoli-esercizi.html', 'articoli-aggettivi.html', 'verbi-tempi.html', 'coppie.html']:
            expected = (ROOT / file).read_bytes()
            self.assertNotRegex(expected.decode(), r'\?v=(?!44\b)\d+')
            for folder in ['www', 'anki-html']:
                self.assertEqual((ROOT / folder / file).read_bytes(), expected)

    def test_production_interactions_and_deck_exhaustion(self):
        result = subprocess.run(['node', str(ROOT / 'tests/coppie-runtime.cjs')], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

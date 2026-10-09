"""One Italian verb form per card; a separate reversible deck inside Carte."""
import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUP = 'Verbi · forme'
VERBS = ['studiare', 'essere', 'avere', 'volere', 'andare', 'fare', 'potere']
TENSES = ['presente', 'passato prossimo', 'futuro semplice', 'condizionale presente']
PERSONS = ['io', 'tu', 'lui', 'noi', 'voi', 'loro']

class VerbFormTests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / 'italiano-flashcards.html').read_text()
        self.cards = json.JSONDecoder().raw_decode(self.html.split('const ALL=', 1)[1])[0]
        self.deck = [c for c in self.cards if c['group'] == GROUP]

    def test_168_individual_forms_and_full_person_tense_coverage(self):
        self.assertEqual(len(self.deck), 168)
        expected = Counter((v, t, p) for v in VERBS for t in TENSES for p in PERSONS)
        self.assertEqual(Counter((c['verb'], c['tense'], c['it'].split()[0]) for c in self.deck), expected)
        self.assertEqual(len({(c['verb'], c['tense'], c['it']) for c in self.deck}), 168)
        for c in self.deck:
            self.assertEqual(c['lang'], 'EN')
            self.assertEqual(c['tags'], ['verbi-forme'])
            self.assertNotIn('direction', c)
            self.assertNotIn('\n', c['it'])
            self.assertTrue(c['other'].startswith(c['tense'] + ' · '))
            self.assertNotRegex(json.dumps(c, ensure_ascii=False), '[\u0400-\u04ff]')
        forms = {c['it']: c['other'] for c in self.deck}
        for front, back in {
            'io studio': 'presente · I study / I am studying',
            'tu hai studiato': 'passato prossimo · you studied / you have studied',
            'io studierò': 'futuro semplice · I will study',
            'io vorrei': 'condizionale presente · I would like',
            'tu vorresti': 'condizionale presente · you would like',
            'lui vorrebbe': 'condizionale presente · he would like',
            'io farei': 'condizionale presente · I would do / I would make',
            'io andrei': 'condizionale presente · I would go',
            'io potrei': 'condizionale presente · I could / I would be able to',
            'io sarei': 'condizionale presente · I would be',
            'io avrei': 'condizionale presente · I would have',
        }.items():
            self.assertEqual(forms[front], back)

    def test_old_1276_cards_are_unchanged(self):
        old = [c for c in self.cards if c['group'] not in {GROUP, '7 ott'}]
        self.assertEqual(len(old), 1276)
        self.assertEqual(hashlib.sha256(json.dumps(old, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
                         '1383a6ac2fb27014e599ca2f5117addbc57d3d153de11478f58407891ca64f0a')
        self.assertEqual(self.cards[:1276], old)

    def test_one_dropdown_option_no_top_tab_no_lettura(self):
        options = re.search(r'const groups=([\s\S]*?);', self.html)[1]
        self.assertEqual(re.findall(r"\['(verbi-forme[^']*)','([^']*)'\]", options), [('verbi-forme', GROUP)])
        self.assertIn("'verbi-forme':'Verbi · forme'", self.html)
        self.assertEqual(re.findall(r"\['([^']+)'", options)[0], '7-ott')
        hub = (ROOT / 'index.html').read_text()
        self.assertEqual(re.findall(r'data-app="([^"]+)">', hub), ['carte', 'articoli', 'aggettivi', 'verbi'])
        self.assertNotRegex(hub + self.html, r'(?i)lettura|verbi-forme-(?:it-en|en-it)')

    def test_v40_embedded_app_and_local_copies(self):
        hub = (ROOT / 'index.html').read_text()
        embedded = re.search(r'<script type="application/json" id="app-carte">([\s\S]*?)</script>', hub)[1]
        self.assertEqual(json.loads(embedded), self.html)
        for name in ['index.html', 'italiano-flashcards.html']:
            content = (ROOT / name).read_bytes()
            self.assertIn(b'content="v40"', content)
            self.assertNotRegex(content.decode(), r'\?v=(?!40\b)\d+')
            for folder in ['www', 'anki-html']:
                self.assertEqual((ROOT / folder / name).read_bytes(), content)

if __name__ == '__main__':
    unittest.main()

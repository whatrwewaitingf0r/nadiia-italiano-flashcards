"""7 October is one mixed reversible lesson, never topic subdecks."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOOD = "un panino con prosciutto e formaggio;una focaccia con le olive;una pizza Margherita;un gelato al cioccolato;un cornetto con la crema;un caffè macchiato;una bruschetta con il pomodoro;una spremuta di arancia;un'insalata di riso;un tagliere di salumi e formaggi;un tramezzino al salmone;una pizzetta;una Caprese;un tè al limone;prosciutto e melone;una cotoletta alla milanese;le lasagne alla bolognese;le linguine al pesto;gli spaghetti al pomodoro;i carciofi alla romana;gli gnocchi al gorgonzola;le penne al ragù;le crocchette di patate;le verdure alla griglia".split(';')
PLACES = 'il bar;la pizzeria;la caffetteria;la trattoria;la pasticceria;il ristorante'.split(';')
BARE = "il cappuccino;i formaggi;le patatine fritte;il cornetto;le fragole;i pomodori;la birra;le torte;il cameriere;il cliente".split(';')
DEMONSTRATIVES = 'questo;questa;questi;queste;quello;quella;quelli;quelle'.split(';')

class LessonTests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / 'italiano-flashcards.html').read_text()
        self.cards = json.JSONDecoder().raw_decode(self.html.split('const ALL=', 1)[1])[0]
        self.lesson = [c for c in self.cards if c['group'] == '7 ott']

    def test_one_lesson_exact_48_cards_without_duplicate_bare_nouns(self):
        self.assertEqual(len(self.lesson), 48)
        self.assertEqual({c['it'] for c in self.lesson}, set(FOOD + PLACES + BARE + DEMONSTRATIVES))
        for c in self.lesson:
            self.assertEqual(c['lang'], 'EN')
            self.assertEqual(c['tags'], ['7-ott'])
            self.assertNotIn('direction', c)
            self.assertTrue(c['other'])
            self.assertNotIn('\n', c['other'])
            self.assertNotRegex(json.dumps(c, ensure_ascii=False), '[\u0400-\u04ff]')
        back = {c['it']: c['other'] for c in self.lesson}
        for word, meaning in [('questo', 'this · m sg'), ('questa', 'this · f sg'),
                              ('questi', 'these · m pl'), ('queste', 'these · f pl'),
                              ('quello', 'that · m sg'), ('quella', 'that · f sg'),
                              ('quelli', 'those · m pl'), ('quelle', 'those · f pl')]:
            self.assertEqual(back[word], meaning)

    def test_all_1444_existing_cards_are_unchanged_in_order(self):
        self.assertEqual(len(self.cards), 1492)
        old = self.cards[:1444]
        digest = hashlib.sha256(json.dumps(old, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        self.assertEqual(digest, '6f381a4344df2375a3558b28a1f6d067d07bd234bb9c55cf49e80334947168ed')
        self.assertEqual(self.cards[1444:], self.lesson)

    def test_stable_order_and_first_block_at_runtime(self):
        result = subprocess.run(['node', str(ROOT / 'tests/lesson-7-ott-order-runtime.cjs')],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_one_dropdown_option_and_shared_shuffle(self):
        options = re.search(r'const groups=([\s\S]*?);', self.html)[1]
        self.assertEqual(re.findall(r"\['(7-ott[^']*)','([^']*)'\]", options), [('7-ott', '7 ott')])
        self.assertIn("'7-ott':'7 ott'", self.html)
        self.assertIn('pool=ALL.filter(c=>matches(c,filter.value));shufflePool()', self.html)
        hub = (ROOT / 'index.html').read_text()
        self.assertEqual(re.findall(r'data-app="([^"]+)">', hub), ['carte', 'articoli', 'aggettivi', 'verbi'])
        self.assertNotRegex(self.html + hub, '(?i)lettura')

    def test_v40_all_copies_and_embedded_cards(self):
        hub = (ROOT / 'index.html').read_text()
        payload = re.search(r'<script type="application/json" id="app-carte">([\s\S]*?)</script>', hub)[1]
        self.assertEqual(json.loads(payload), self.html)
        for filename in ['index.html', 'italiano-flashcards.html', 'articoli-esercizi.html', 'articoli-aggettivi.html', 'verbi-tempi.html']:
            content = (ROOT / filename).read_bytes()
            if filename in ['index.html', 'italiano-flashcards.html']:
                self.assertIn(b'content="v40"', content)
            self.assertNotRegex(content.decode(), r'\?v=(?!40\b)\d+')
            for folder in ['www', 'anki-html']:
                self.assertEqual((ROOT / folder / filename).read_bytes(), content)

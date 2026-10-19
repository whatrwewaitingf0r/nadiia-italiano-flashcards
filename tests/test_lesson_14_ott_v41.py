"""14 October stays one reversible, ordered restaurant lesson inside Carte."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOGUE = 'I signori desiderano?;Vorrei…;Cosa desidera?;Cosa desiderate?;Per me invece…;Cosa prende?;Cosa prendete?;Io prendo…;Anch’io prendo;Anch’io vorrei…;Il conto, per favore;Quant’è?;Posso pagare con la carta?;pagare in contanti'.split(';')
SLOTS = 'da bere;per antipasto;per primo;per secondo;per contorno;per dessert'.split(';')
DISHES = 'il pesce;il risotto;il minestrone;il pollo;i peperoni;le verdure;le fragole;le macedonie;le lasagne;la carne;le cotolette;gli spaghetti;il vino;l’acqua minerale;la coca cola;la cotoletta;le patatine fritte;la panna cotta;l’acqua;il gelato;la birra;la macedonia;l’insalata;i tortellini;l’arrosto;gli spinaci;la bruschetta;la bistecca;le patate;gli affettati;il vino bianco;la pizza;il vino rosso;la piadina;il tiramisù;il muffin;l’aranciata;il sorbetto;la torta;la sprite;il budino;la caprese;i ravioli;i filetti di pesce;il polpo;i cannelloni;la tartare;le scaloppine;il purè;i fichi;il melone;lo spumante;la pizzetta;le pastine;lo champagne;lo gnocco fritto;il torrone'.split(';')
FORMS = ['prendo prendi prende prendiamo prendete prendono'.split(),
         'preferisco preferisci preferisce preferiamo preferite preferiscono'.split(),
         'ordino ordini ordina ordiniamo ordinate ordinano'.split()]
POLITE = 'Scusi;per cortesia;per favore;per piacere;grazie'.split(';')


class Lesson14Tests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / 'italiano-flashcards.html').read_text()
        self.cards = json.JSONDecoder().raw_decode(self.html.split('const ALL=', 1)[1])[0]
        self.lesson = [c for c in self.cards if c['group'] == '14 ott']

    def test_all_100_cards_in_exact_lesson_order(self):
        expected = DIALOGUE + SLOTS + DISHES + sum(FORMS, []) + POLITE
        self.assertEqual(len(expected), 100)
        self.assertEqual([c['it'] for c in self.lesson], expected)
        for card in self.lesson:
            self.assertEqual(card['lang'], 'EN')
            self.assertEqual(card['tags'], ['14-ott'])
            self.assertNotIn('direction', card)
            self.assertTrue(card['other'].strip())
            self.assertNotRegex(json.dumps(card, ensure_ascii=False), r'[\u0400-\u04ff]|https?://|\n')
        backs = {c['it']: c['other'] for c in self.lesson}
        self.assertEqual(backs['I signori desiderano?'], 'What would you like?')
        self.assertEqual(backs['Anch’io prendo'], "I'll have the same")
        self.assertEqual(backs['Cosa desidera?'], 'What would you like? (formal sg)')
        self.assertEqual(backs['per contorno'], 'for a side')
        self.assertEqual(backs['le macedonie'], 'fruit salads · f pl')
        self.assertEqual(backs['lo gnocco fritto'], 'fried dough · m sg')
        self.assertEqual(backs['Scusi'], 'Excuse me (formal)')

    def test_18_separate_verb_forms_with_infinitive_person_and_english(self):
        backs = {c['it']: c['other'] for c in self.lesson}
        persons = ['io', 'tu', 'lui/lei', 'noi', 'voi', 'loro']
        subjects = ['I', 'you', 'he/she', 'we', 'you (pl)', 'they']
        for verb, forms, english in zip(['prendere', 'preferire', 'ordinare'], FORMS,
                                       ['have', 'prefer', 'order']):
            for i, form in enumerate(forms):
                inflected = english + ('s' if i == 2 else '')
                if english == 'have' and i == 2:
                    inflected = 'has'
                self.assertEqual(backs.get(form), f'{verb} · {persons[i]} · {subjects[i]} {inflected}')

    def test_all_1492_older_cards_are_untouched_and_not_retagged(self):
        old = [c for c in self.cards if c['group'] not in {'14 ott', '18 ott'}]
        self.assertEqual(len(self.cards), 1673)
        self.assertEqual(self.cards[:1492], old)
        self.assertEqual(hashlib.sha256(json.dumps(old, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
                         'f9ffdd50f8d1010ce34c5a30fa958864e665cb2a46837559e27b29cafc63738f')

    def test_one_option_first_and_no_new_top_tab_or_reading(self):
        groups = re.search(r'const groups=([\s\S]*?);', self.html)[1]
        options = re.findall(r"\['([^']+)','([^']+)'\]", groups)
        self.assertEqual(options[1:3], [('14-ott', '14 ott'), ('7-ott', '7 ott')])
        self.assertEqual([o for o in options if o[0].startswith('14-ott')], [('14-ott', '14 ott')])
        hub = (ROOT / 'index.html').read_text()
        self.assertEqual(re.findall(r'data-app="([^"]+)">', hub), ['carte', 'articoli', 'aggettivi', 'verbi'])
        self.assertNotRegex(self.html + hub, '(?i)lettura')

    def test_runtime_default_order_direction_and_deck_isolation(self):
        result = subprocess.run(['node', str(ROOT / 'tests/lesson-14-ott-runtime.cjs')],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_v43_copies_and_embedded_cards_match(self):
        hub = (ROOT / 'index.html').read_text()
        embedded = re.search(r'<script type="application/json" id="app-carte">([\s\S]*?)</script>', hub)[1]
        self.assertEqual(json.loads(embedded), self.html)
        for name in ['index.html', 'italiano-flashcards.html', 'articoli-esercizi.html', 'articoli-aggettivi.html', 'verbi-tempi.html']:
            content = (ROOT / name).read_bytes()
            self.assertNotRegex(content.decode(), r'\?v=(?!43\b)\d+')
            if name in ['index.html', 'italiano-flashcards.html']:
                self.assertIn(b'content="v43"', content)
            for folder in ['www', 'anki-html']:
                self.assertEqual((ROOT / folder / name).read_bytes(), content)

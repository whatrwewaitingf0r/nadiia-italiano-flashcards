from deck_contract import assert_v29_cards
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
GROUP = 'Grammatica · articoli'
def cards(html):
    return json.JSONDecoder().raw_decode(html.split('const ALL=', 1)[1])[0]
class ArticoliTests(unittest.TestCase):
    def test_rule_cards(self):
        html = (ROOT/'italiano-flashcards.html').read_text()
        all_cards = cards(html)
        target = [c for c in all_cards if c['group'] == GROUP]
        self.assertEqual(len(target), 0)
        assert_v29_cards(self, all_cards)
        self.assertEqual(len({c['it'] for c in target}), 0)
        for c in target:
            self.assertEqual(c['lang'], 'EN')
            self.assertEqual(c['tags'], ['grammar', 'articoli'])
            self.assertFalse(re.search('[А-Яа-яЁё]', json.dumps(c, ensure_ascii=False)))
        self.assertNotIn("['grammar-articoli','Grammatica · articoli']", html)
        self.assertNotIn("'grammar-articoli':'Grammatica · articoli'", html)
        self.assertLess(html.index("['chiara-23-sett'"), html.index("['lisa-irregolari'"))
        self.assertIn('isGrammar', html)
        self.assertIn('v36', html)
        self.assertIn('articoli-esercizi.html?v=36', html)
    def test_drill(self):
        html = (ROOT/'articoli-esercizi.html').read_text()
        self.assertFalse(re.search('[А-Яа-яЁё]', html))
        self.assertFalse(re.search(r'https?://|@import|fetch\s*\(|XMLHttpRequest|srcset=', html))
        nouns = json.JSONDecoder().raw_decode(html.split('const NOUNS=',1)[1])[0]
        self.assertEqual(len(nouns),20)
        by_word = {n['sg']:n for n in nouns}
        self.assertEqual(by_word['yogurt']['pl'], 'yogurt')
        self.assertEqual(by_word['paga']['pl'], 'paghe')
        self.assertEqual(by_word['chirurgo']['pl'], 'chirurghi')
        for word in ('studente','gnocco','pneumatico','psicologo','xilofono','yogurt','zaino'):
            self.assertEqual(by_word[word]['kind'], 'special')
        self.assertIn('Correggi', html)
        self.assertIn('Mescola', html)
        self.assertIn('some', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('const ITEMS=', html)
        self.assertIn('<span class="blank">___ </span><span class="noun">studente</span>', html)
        self.assertNotIn('replaceChildren', html)
        self.assertIn('<meta name="build-version" content="v30">', html)
        for path in (ROOT/'www/articoli-esercizi.html', ROOT/'anki-html/articoli-esercizi.html',
                     Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html/articoli-esercizi.html'),
                     Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html/www/articoli-esercizi.html')):
            self.assertEqual(html, path.read_text())
if __name__=='__main__': unittest.main()

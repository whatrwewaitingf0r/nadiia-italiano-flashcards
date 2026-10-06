"""v32 removes only the authorized decks, without losing local newer cards."""
import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')
BASES = [ROOT, ROOT/'www', ROOT/'anki-html', CANON, CANON/'www']
REMOVED = {'Grammatica · articoli', 'Grammatica · concordanza'}

def cards(html):
    return json.JSONDecoder().raw_decode(html.split('const ALL=', 1)[1])[0]

def assert_retained(test, deck):
    # v35 intentionally removes the 257 Lettura cards; all other v34 cards are frozen.
    expected = json.loads((ROOT/'tests/streghe-v35-baseline.json').read_text())
    retained = deck[:expected['count']]
    test.assertEqual(len(retained), expected['count'])
    test.assertEqual(hashlib.sha256(json.dumps(retained, ensure_ascii=False, sort_keys=True).encode()).hexdigest(), expected['sha256'])
    test.assertFalse(any(c.get('reading') for c in deck))

class RemovalTests(unittest.TestCase):
    def test_only_requested_cards_removed(self):
        deck = cards((ROOT/'italiano-flashcards.html').read_text())
        self.assertFalse(any(c['group'] in REMOVED or 'lesson5' in c.get('tags', []) for c in deck))
        assert_retained(self, deck)

    def test_removed_filters_and_links_are_absent(self):
        html = (ROOT/'italiano-flashcards.html').read_text()
        for term in [*REMOVED, 'grammar-articoli', 'grammar-concordanza', 'liam-passato.html', 'Lesson 5 + Liguria']:
            self.assertNotIn(term, html)
        for term in ['Grammatica · verbi', 'Lisa · irregolari', '100 parole', 'Vocabolario', '16 sett · Liam', 'Chiara']:
            self.assertIn(term, html)

    def test_hub_and_all_copies(self):
        hub = (ROOT/'index.html').read_text()
        self.assertIn('content="v37"', hub)
        self.assertIn('content="v37"', (ROOT/'italiano-flashcards.html').read_text())
        for term in ['liam-passato.html', 'tab-liam"', 'tab-liam-lesson5', 'app-liam"', 'app-liam-lesson5']:
            self.assertNotIn(term, hub)
        for key, name in [('carte', 'italiano-flashcards.html'), ('articoli', 'articoli-esercizi.html'), ('aggettivi', 'articoli-aggettivi.html'), ('verbi', 'verbi-tempi.html')]:
            self.assertIn('id="tab-'+key+'"', hub)
            embedded = re.search(r'<script type="application/json" id="app-'+key+r'">([\s\S]*?)</script>', hub)
            self.assertEqual(json.loads(embedded[1]), (ROOT/name).read_text())
        for base in BASES:
            self.assertFalse((base/'liam-passato.html').exists(), str(base))
            for name in ['index.html', 'italiano-flashcards.html']:
                self.assertEqual((base/name).read_bytes(), (ROOT/name).read_bytes())

    def test_deleted_reading_builders_cannot_resurrect_the_section(self):
        for name in ['integrate_lettura.py', 'build_lettura.py', 'lettura-template.html']:
            self.assertFalse((ROOT/'scripts'/name).exists())

    def test_vocabulary_reimport_accepts_retained_baseline(self):
        spec = importlib.util.spec_from_file_location('reimport_vocab', ROOT/'scripts/add_liam_vocab.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            module.ROOT, module.CANON = root, root/'canon'
            for base in [root/'www', root/'anki-html', module.CANON, module.CANON/'www', root/'scripts']:
                base.mkdir(parents=True, exist_ok=True)
            for name in ['index.html', 'italiano-flashcards.html', 'scripts/liam-vocab-additions.json']:
                (root/name).write_bytes((ROOT/name).read_bytes())
            with redirect_stdout(StringIO()):
                module.main()
            assert_retained(self, cards((root/'italiano-flashcards.html').read_text()))

if __name__ == '__main__':
    unittest.main()

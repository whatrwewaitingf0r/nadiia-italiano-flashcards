"""Append-only, English-only second 100-word deck and dedicated hub tab."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')
GROUP = '100 parole 2'
BASELINE_COUNT = 1232
BASELINE_SHA = 'f95492ab959ca699c724620cf217575c2febab2dc922d96fcac876143b279dbd'


def aliases(text):
    values = set()
    for part in re.split(r'\s*(?:/|→|\(|\n)\s*', text.casefold().replace('’', "'")):
        part = re.sub(r"^(?:il |lo |la |l'|i |gli |le |un |uno |una |un')", '', part.strip())
        values.add(part)
    return values - {''}


class Parole2Tests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT/'italiano-flashcards.html').read_text()
        self.deck = json.JSONDecoder().raw_decode(self.html.split('const ALL=', 1)[1])[0]
        self.new = [c for c in self.deck if c['group'] == GROUP]

    def test_exactly_100_new_words_without_touching_any_v32_card(self):
        self.assertEqual(len(self.new), 100)
        self.assertEqual(len(self.deck), 1332)
        retained = [c for c in self.deck if c['group'] != GROUP]
        self.assertEqual(len(retained), BASELINE_COUNT)
        digest = hashlib.sha256(json.dumps(retained, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        self.assertEqual(digest, BASELINE_SHA)
        self.assertEqual(len([c for c in retained if c['group'] == '100 parole']), 100)
        seen = set().union(*(aliases(c['it']) for c in retained))
        for c in self.new:
            self.assertFalse(seen & aliases(c['it']), c['it'])
            seen.update(aliases(c['it']))
            self.assertEqual(c['lang'], 'EN')
            self.assertEqual(c['tags'], ['100parole-2'])
            self.assertNotRegex(json.dumps(c, ensure_ascii=False), '[\u0400-\u04ff]')
        self.assertFalse(any(c['group'] in {'Grammatica · articoli', 'Grammatica · concordanza'} or 'lesson5' in c.get('tags', []) for c in self.deck))

    def test_frequency_provenance_and_new_filter(self):
        self.assertIn("['100parole-2','100 parole 2 · Altre 100']", self.html)
        self.assertIn("'100parole-2':'100 parole 2'", self.html)
        path = ROOT/'scripts/100-parole-2.json'
        self.assertTrue(path.exists(), 'Missing frequency-source manifest')
        manifest = json.loads(path.read_text())
        self.assertEqual(manifest['corpus'], 'PAISÀ')
        self.assertEqual(len(manifest['words']), 100)
        self.assertEqual([c['it'] for c in self.new], [w['front'] for w in manifest['words']])
        self.assertEqual([c['other'] for c in self.new], [w['english'] for w in manifest['words']])
        ranks = [w['rank'] for w in manifest['words']]
        self.assertGreater(min(ranks), 100)
        self.assertLess(max(ranks), 400)
        self.assertEqual(ranks, sorted(ranks))

    def test_dedicated_hub_tab_and_synchronized_v33_copies(self):
        hub = (ROOT/'index.html').read_text()
        self.assertIn('id="tab-parole-2"', hub)
        self.assertIn('data-app="parole-2">100 parole 2</button>', hub)
        self.assertLess(hub.index('id="tab-carte"'), hub.index('id="tab-parole-2"'))
        self.assertIn('id="panel-parole-2"', hub)
        self.assertIn('id="frame-parole-2"', hub)
        for base in [ROOT, ROOT/'www', ROOT/'anki-html', CANON, CANON/'www']:
            for name in ['index.html', 'italiano-flashcards.html']:
                content = (base/name).read_text()
                self.assertEqual(content, (ROOT/name).read_text())
                self.assertIn('content="v33"', content)
                self.assertNotIn('?v=32', content)
        payload = re.search(r'<script type="application/json" id="app-carte">([\s\S]*?)</script>', hub)
        self.assertEqual(json.loads(payload[1]), self.html)


if __name__ == '__main__':
    unittest.main()

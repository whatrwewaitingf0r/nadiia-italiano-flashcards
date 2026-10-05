import hashlib
import json
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')
APPS = {'carte': 'italiano-flashcards.html', 'articoli': 'articoli-esercizi.html', 'aggettivi': 'articoli-aggettivi.html', 'verbi': 'verbi-tempi.html'}
class HubTests(unittest.TestCase):
    def test_single_file_apps_and_copies(self):
        h = (ROOT/'index.html').read_text()
        self.assertIn('content="v29"', h)
        self.assertIn('role="tablist"', h)
        self.assertIn('srcdoc', h)
        self.assertNotRegex(h, '[\u0400-\u04ff]')
        for key, file in APPS.items():
            match = re.search(r'<script type="application/json" id="app-'+key+r'">([\s\S]*?)</script>', h)
            self.assertIsNotNone(match, key)
            self.assertEqual(json.loads(match[1]), (ROOT/file).read_text())
            self.assertIn('id="tab-'+key+'"', h)
            self.assertIn(file+'?v=29', h)
        for p in [ROOT/'www/index.html', ROOT/'anki-html/index.html', CANON/'index.html', CANON/'www/index.html']:
            self.assertEqual(h, p.read_text())
    def test_cards_preserved(self):
        h = (ROOT/'italiano-flashcards.html').read_text()
        cards = json.JSONDecoder().raw_decode(h.split('const ALL=',1)[1])[0]
        self.assertEqual(len(cards), 1010)
        self.assertEqual(hashlib.sha256(json.dumps(cards[:985],ensure_ascii=False,sort_keys=True).encode()).hexdigest(), 'c9cede215d23fbf6aa79d06c2db2072915f3c74ccb2a648dd840c20214c9d9c0')
        for p in [ROOT/'www/italiano-flashcards.html', ROOT/'anki-html/italiano-flashcards.html', CANON/'italiano-flashcards.html', CANON/'www/italiano-flashcards.html']:
            self.assertEqual(h, p.read_text())
if __name__ == '__main__': unittest.main()

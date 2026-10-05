import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')

class LiamLesson5Tests(unittest.TestCase):
    def test_cards_keep_baseline_and_owner(self):
        h = (ROOT/'italiano-flashcards.html').read_text()
        cards = json.JSONDecoder().raw_decode(h.split('const ALL=', 1)[1])[0]
        self.assertEqual(hashlib.sha256(json.dumps(cards[:1066], ensure_ascii=False, sort_keys=True).encode()).hexdigest(), '1f7594d9ed5ecdbd34714a281a978fc183c0c61d99290ba62610fe8b2fdf50ac')
        self.assertEqual(hashlib.sha256(json.dumps(cards[:985], ensure_ascii=False, sort_keys=True).encode()).hexdigest(), 'c9cede215d23fbf6aa79d06c2db2072915f3c74ccb2a648dd840c20214c9d9c0')
        added = [c for c in cards if c.get('tags') == ['liam', 'lesson5', 'nord-sud']]
        self.assertEqual(len(added), 56)
        self.assertEqual(len({c['it'] for c in added}), 56)
        for c in added:
            self.assertEqual(c['group'], 'Liam · Nord/Sud · Liguria')
            self.assertEqual(c['lang'], 'EN')
            self.assertEqual(c['tags'], ['liam', 'lesson5', 'nord-sud'])
        self.assertEqual(sum('Il passato' in c['note'] for c in added), 30)
        self.assertEqual(sum('Daily objects' in c['note'] for c in added), 26)
        self.assertNotRegex(h, '[\u0400-\u04ff]')
        groupcode = h.split('const groups=', 1)[1].split('];', 1)[0]
        self.assertLess(groupcode.index('chiara-23-sett'), groupcode.index('liam-liguria'))
        self.assertLess(groupcode.index('chiara-23-sett'), groupcode.index('aug-26'))
        self.assertIn("filter.value='chiara-23-sett'", h)
        for p in [ROOT/'www/italiano-flashcards.html', ROOT/'anki-html/italiano-flashcards.html', CANON/'italiano-flashcards.html', CANON/'www/italiano-flashcards.html']:
            self.assertEqual(h, p.read_text())

    def test_doc_exercises(self):
        h = (ROOT/'liam-passato.html').read_text()
        units = json.JSONDecoder().raw_decode(h.split('const UNITS=', 1)[1])[0]
        self.assertEqual([len(u['items']) for u in units], [8, 8, 8, 6])
        self.assertEqual(units[1]['items'][0]['prompt'], 'Io ___ mangiato la pizza.')
        self.assertEqual(units[2]['items'][0]['prompt'], 'Io ___ stata a casa.')
        self.assertEqual(units[3]['items'][0]['choices'], ['sono', 'ho', 'è'])
        self.assertEqual(units[3]['items'][3]['answers'], ['è'])
        self.assertIn('Daily objects and gender', h)
        self.assertIn('ho bevuto', h)
        self.assertIn('ho letto', h)
        self.assertIn('aria-live="polite"', h)
        self.assertNotRegex(h, '[\u0400-\u04ff]')
        self.assertNotRegex(h, r'https?://|@import|fetch\s*\(|XMLHttpRequest')
        for p in [ROOT/'www/liam-passato.html', ROOT/'anki-html/liam-passato.html', CANON/'liam-passato.html', CANON/'www/liam-passato.html']:
            self.assertEqual(h, p.read_text())

    def test_merged_hub(self):
        h = (ROOT/'index.html').read_text()
        self.assertIn('content="v30"', h)
        labels = re.findall(r'data-app="[^"]+">([^<]+)</button>', h)
        self.assertEqual(labels[:5], ['Carte', 'Articoli', 'Aggettivi', 'Verbi', 'Liam ieri'])
        self.assertIn('Lettura', labels)
        for key, file in [('carte', 'italiano-flashcards.html'), ('liam', 'liam-passato.html')]:
            m = re.search(r'<script type="application/json" id="app-'+key+r'">([\s\S]*?)</script>', h)
            self.assertEqual(json.loads(m[1]), (ROOT/file).read_text())
            self.assertIn(file+'?v=30', h)

if __name__ == '__main__':
    unittest.main()

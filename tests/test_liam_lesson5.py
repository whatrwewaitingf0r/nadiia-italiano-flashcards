"""The previously added Lesson 5 content was explicitly removed in v32."""
import json
import unittest
from pathlib import Path
from deck_contract import assert_v29_cards

ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')

class LiamLesson5Tests(unittest.TestCase):
    def test_retained_cards_and_lesson5_removal(self):
        html = (ROOT/'italiano-flashcards.html').read_text()
        cards = json.JSONDecoder().raw_decode(html.split('const ALL=', 1)[1])[0]
        assert_v29_cards(self, cards)
        self.assertFalse(any('lesson5' in c.get('tags', []) for c in cards))
        self.assertIn("filter.value='chiara-23-sett'", html)
        self.assertIn("['liam-liguria','Liam · Nord/Sud · Liguria']", html)

    def test_doc_exercises_removed_from_every_copy(self):
        for base in [ROOT, ROOT/'www', ROOT/'anki-html', CANON, CANON/'www']:
            self.assertFalse((base/'liam-passato.html').exists(), str(base))

    def test_hub_has_no_lesson5_tab(self):
        hub = (ROOT/'index.html').read_text()
        self.assertIn('content="v34"', hub)
        self.assertNotIn('liam-passato.html', hub)
        self.assertNotIn('id="tab-liam"', hub)
        self.assertNotIn('id="tab-liam-lesson5"', hub)
        self.assertIn('id="tab-lettura"', hub)

if __name__ == '__main__':
    unittest.main()

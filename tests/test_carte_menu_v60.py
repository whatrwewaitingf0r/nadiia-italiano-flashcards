"""Dated Coppie decks must remain reachable in every released Carte picker."""
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')


class CarteMenuTests(unittest.TestCase):
    def test_real_picker_and_all_pairs(self):
        result = subprocess.run(['node', str(ROOT / 'tests/carte-menu-runtime.cjs')], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_synced_carte_payloads_and_hub_query(self):
        page = (ROOT / 'italiano-flashcards.html').read_text()
        hub = (ROOT / 'index.html').read_text()
        self.assertIn('content="v60"', page)
        self.assertIn('content="v60"', hub)
        self.assertIn('italiano-flashcards.html?v=60', hub)
        self.assertIn("(['carte','coppie'].includes(key)?60:", hub)
        self.assertEqual(json.loads(re.search(r'id="app-carte">([\s\S]*?)</script>', hub)[1]), page)
        self.assertEqual(json.loads(re.search(r'id="app-coppie">([\s\S]*?)</script>', hub)[1]), (ROOT / 'coppie.html').read_text())
        for folder in [ROOT / 'www', ROOT / 'anki-html', CANON, CANON / 'www']:
            for name in ['italiano-flashcards.html', 'index.html', 'coppie.html']:
                self.assertEqual((folder / name).read_bytes(), (ROOT / name).read_bytes(), str(folder / name))

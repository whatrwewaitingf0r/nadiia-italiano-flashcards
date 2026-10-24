"""Keep picked words dusty blue and mistakes red in every shipped Coppie copy."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELECTED = '.tile.selected{background:#3d4f68;border-color:#d7c4a3;color:#f4efe4}'
WRONG = '.tile.wrong{background:#57302f;border-color:#ef9a94;color:#ffe1de}'


class CoppieSelectionColorTests(unittest.TestCase):
    def check_colors(self, html):
        self.assertEqual(re.findall(r'\.tile\.selected\{[^}]*\}', html), [SELECTED])
        self.assertEqual(re.findall(r'\.tile\.wrong\{[^}]*\}', html), [WRONG])
        self.assertNotIn('#594437', html)
        self.assertNotIn('#1e4a44', html)

    def test_standalone_copies_use_requested_colors(self):
        for folder in [ROOT, ROOT / 'www', ROOT / 'anki-html']:
            with self.subTest(folder=folder.name):
                self.check_colors((folder / 'coppie.html').read_text())

    def test_embedded_copies_use_requested_colors(self):
        for folder in [ROOT, ROOT / 'www', ROOT / 'anki-html']:
            with self.subTest(folder=folder.name):
                hub = (folder / 'index.html').read_text()
                payload = re.search(
                    r'<script type="application/json" id="app-coppie">([\s\S]*?)</script>', hub
                )
                self.assertIsNotNone(payload)
                embedded = json.loads(payload[1])
                self.check_colors(embedded)
                self.assertEqual(embedded, (folder / 'coppie.html').read_text())

"""Append-only 24 October expansion; full Italian strings are identities."""
import hashlib
import json
import re
import subprocess
import unittest
from test_hundred_24_ott import original_words
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')


def payload(source, marker):
    return json.JSONDecoder().raw_decode(source.split(marker, 1)[1])[0]


class More24Tests(unittest.TestCase):
    def test_requested_pairs_are_appended_in_both_apps(self):
        decks = original_words(payload((ROOT / 'coppie.html').read_text(), 'const DECKS='))
        cards = original_words(payload((ROOT / 'italiano-flashcards.html').read_text(), 'const ALL='))
        requested = json.loads((ROOT / 'tests/lesson-24-ott-more.json').read_text())
        originals = [18, 19, 16]
        self.assertEqual(len(decks), 23, 'extend existing decks, do not create another')
        self.assertEqual(len(cards), 1973)
        self.assertEqual(hashlib.sha256(json.dumps(cards[:1726], ensure_ascii=False, sort_keys=True).encode()).hexdigest(), '089a14eb363c497d3debe8ad1c639cc8b082c224200e4b9706c1b03a5c33f25b')
        for spec, count in zip(requested, originals):
            deck, = [d for d in decks if d['id'] == spec['id']]
            self.assertEqual(deck['pairs'][count:count + len(spec['pairs'])], spec['pairs'])
            lesson = [c for c in cards if c['group'] == spec['label']]
            self.assertEqual([[c['it'], c['other']] for c in lesson], deck['pairs'])
            for card in lesson[count:]:
                self.assertEqual((card['lang'], card['tags'], card['note']), ('EN', [spec['id']], ''))
        new = [it.casefold() for spec in requested for it, _ in spec['pairs']]
        self.assertEqual(len(set(new)), 126)
        for it in new:
            self.assertEqual(sum(c['it'].casefold() == it for c in cards), 1, it)
            self.assertEqual(sum(pair[0].casefold() == it for d in decks for pair in d['pairs']), 1, it)

    def test_copies_payloads_version_and_tutto(self):
        hub = (ROOT / 'index.html').read_text()
        for key, name in [('carte', 'italiano-flashcards.html'), ('coppie', 'coppie.html')]:
            source = (ROOT / name).read_text()
            embedded = re.search(r'<script type="application/json" id="app-' + key + r'">([\s\S]*?)</script>', hub)[1]
            self.assertEqual(json.loads(embedded), source)
            self.assertTrue('content="v54"' in source)
            self.assertIn(name + '?v=54', hub)
        for name in ['index.html', 'italiano-flashcards.html', 'coppie.html']:
            for folder in [ROOT / 'www', ROOT / 'anki-html', CANON, CANON / 'www']:
                self.assertEqual((folder / name).read_bytes(), (ROOT / name).read_bytes())
        source = (ROOT / 'coppie.html').read_text()
        self.assertIn('index.html?v=54#carte', source)
        self.assertIn('.tile.selected{background:#3d4f68;border-color:#d7c4a3;color:#f4efe4}', source)
        self.assertIn('uniquePairs(DECKS).length', source)
        self.assertNotIn('1622', source)
        # Execute actual production code with a minimal DOM; exercise the Tutto handler.
        result = subprocess.run(['node', str(ROOT / 'tests/coppie-runtime.cjs')], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

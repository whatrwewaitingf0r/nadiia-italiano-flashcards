"""25 October photo/Dante additions preserve all existing Italian identities."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')
REQUESTED = json.loads((ROOT / 'tests/lesson-25-ott-decks.json').read_text())
IDS = {d['id'] for d in REQUESTED}
GROUPS = {d['label'] for d in REQUESTED}
SKIPPED = ['la penna', 'il valore', 'la spada', 'una volta', 'tardi', 'le ciglia', 'quasi']


def data(name, token):
    return json.JSONDecoder().raw_decode((ROOT / name).read_text().split(token, 1)[1])[0]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class Lesson25Tests(unittest.TestCase):
    def test_preserved_baseline_and_globally_unique_exact_additions(self):
        cards = data('italiano-flashcards.html', 'const ALL=')
        decks = data('coppie.html', 'const DECKS=')
        old_cards = [c for c in cards if c['group'] not in GROUPS]
        old_decks = [d for d in decks if d['id'] not in IDS]
        self.assertEqual(digest(old_cards), '5732014a79607b62cf325d19a944cb4a87c367080812f8deb528104c680685c9')
        self.assertEqual(digest(old_decks), 'ec084e59555fcbded58942d854db50c80b02bbf3ba3a7db9e060a660fa9826fc')
        self.assertEqual(cards[:len(old_cards)], old_cards)
        self.assertEqual(decks[:len(old_decks)], old_decks)
        seen = {c['it'].casefold() for c in old_cards} | {it.casefold() for d in old_decks for it, _ in d['pairs']}
        skipped = []
        for spec, count in zip(REQUESTED, [9, 130]):
            expected = []
            for it, en in spec['pairs']:
                if it.casefold() in seen:
                    skipped.append(it)
                else:
                    expected.append([it, en])
                    seen.add(it.casefold())
                    self.assertEqual(sum(c['it'].casefold() == it.casefold() for c in cards), 1, it)
                    self.assertEqual(sum(p[0].casefold() == it.casefold() for d in decks for p in d['pairs']), 1, it)
            actual = [d for d in decks if d['id'] == spec['id']]
            self.assertEqual(actual, [dict(id=spec['id'], label=spec['label'], pairs=expected)])
            self.assertEqual(len(expected), count)
            lesson = [c for c in cards if c['group'] == spec['label']]
            self.assertEqual(lesson, [dict(it=it, other=en, lang='EN', group=spec['label'], note='', tags=[spec['id']]) for it, en in expected])
        self.assertEqual(skipped, SKIPPED)
        self.assertEqual(len(cards), 2112)
        self.assertEqual(len(decks), 25)

    def test_release_copies_embeds_and_current_versions(self):
        hub = (ROOT / 'index.html').read_text()
        for key, name in [('carte', 'italiano-flashcards.html'), ('coppie', 'coppie.html')]:
            embedded = re.search(r'<script type="application/json" id="app-' + key + r'">([\s\S]*?)</script>', hub)[1]
            self.assertEqual(json.loads(embedded), (ROOT / name).read_text())
            self.assertIn(name + '?v=57', hub)
        for name in ['index.html', 'italiano-flashcards.html', 'coppie.html']:
            content = (ROOT / name).read_bytes()
            version = b'v55' if name == 'italiano-flashcards.html' else b'v57'
            self.assertIn(b'content="' + version + b'"', content)
            for folder in [ROOT / 'www', ROOT / 'anki-html', CANON, CANON / 'www']:
                self.assertEqual((folder / name).read_bytes(), content)
        self.assertIn("(['carte','coppie'].includes(key)?57:", hub)
        self.assertIn('.tile.selected{background:#3d4f68;border-color:#d7c4a3;color:#f4efe4}', (ROOT / 'coppie.html').read_text())

    def test_production_picker_handlers_order_directions_and_tutto(self):
        result = subprocess.run(['node', str(ROOT / 'tests/lesson-25-ott-runtime.cjs')], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

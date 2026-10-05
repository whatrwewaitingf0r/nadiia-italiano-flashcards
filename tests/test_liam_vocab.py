"""Append-only source-backed Liam vocabulary import."""
import hashlib
import importlib.util
import json
import re
import unittest
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def aliases(text):
    text = unicodedata.normalize('NFKC', text).casefold().replace('’', "'")
    text = re.sub(r'\([^)]*\)', '', text)
    values = set()
    for part in text.split('/'):
        part = re.sub(r"^(?:il|lo|la|gli|le|i|un|uno|una)\s+|^(?:l|un)'", '', part.strip())
        part = re.sub(r'[^\w\s\']', '', part)
        values.add(' '.join(part.split()))
    return values - {''}


def cards(html):
    return json.JSONDecoder().raw_decode(html.split('const ALL=', 1)[1])[0]


class LiamVocabTests(unittest.TestCase):
    def test_importer_skips_article_and_slash_aliases_and_is_idempotent(self):
        spec = importlib.util.spec_from_file_location('add_liam_vocab', ROOT / 'scripts/add_liam_vocab.py')
        importer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(importer)
        existing = [{'it': 'chiacchierone / chiacchierona', 'tags': ['lesson5', 'custom']},
                    {'it': 'cachi'}, {'it': "l'abbazia"}]
        candidates = [{'card': {'it': 'chiacchierona'}}, {'card': {'it': 'caco / cachi'}},
                      {'card': {'it': 'l’abbazia'}}, {'card': {'it': 'ghiro'}}]
        merged, skipped = importer.append_missing(existing, candidates)
        self.assertEqual(merged[:len(existing)], existing)
        self.assertEqual(merged[len(existing):], [{'it': 'ghiro'}])
        self.assertEqual(skipped, ['chiacchierona', 'caco / cachi', 'l’abbazia'])
        repeated, _ = importer.append_missing(merged, candidates)
        self.assertEqual(repeated, merged)

    def test_missing_reading_vocabulary_is_present(self):
        deck = cards((ROOT / 'italiano-flashcards.html').read_text())
        fronts = set().union(*(aliases(c['it']) for c in deck))
        for word in ['ghiro', 'formula magica', 'guaritrice', 'strix',
                     'strigoi', 'lamia', 'yamauba', 'sorcières', 'hexen',
                     'matteuccia di todi', 'stregoneria']:
            self.assertTrue(word in fronts, f'Missing vocabulary: {word}')

    def test_retained_baseline_and_lesson5_removal(self):
        deck = cards((ROOT / 'italiano-flashcards.html').read_text())
        baseline_hash = hashlib.sha256(json.dumps(deck[:944], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        self.assertEqual(baseline_hash, 'e33694defb736c5d037df00d1dfbac7d194dccc289d8ef488db778afdefeafce')
        lesson5 = [c for c in deck if 'lesson5' in c.get('tags', [])]
        self.assertEqual(len(lesson5), 0)
        self.assertTrue(all(c['tags'] == ['liam', 'lesson5', 'nord-sud'] for c in lesson5))

    def test_import_is_unique_source_backed_and_english_only(self):
        deck = cards((ROOT / 'italiano-flashcards.html').read_text())
        new = [c for c in deck if 'vocab' in c.get('tags', [])]
        self.assertGreaterEqual(len(new), 1)
        seen = set()
        for card in deck:
            keys = aliases(card['it'])
            if 'vocab' in card.get('tags', []):
                self.assertFalse(keys & seen, card['it'])
                self.assertEqual(card['group'], 'Liam · Nord/Sud · Liguria')
                self.assertEqual(card['lang'], 'EN')
                self.assertEqual(card['tags'], ['liam', 'vocab', 'nord-sud'])
                self.assertNotRegex(json.dumps(card, ensure_ascii=False), '[\u0400-\u04ff]')
            seen.update(keys)

    def test_candidate_provenance_covers_final_document_paragraphs(self):
        manifest = json.loads((ROOT / 'scripts/liam-vocab-additions.json').read_text())
        self.assertEqual(manifest['paragraphCount'], 7298)
        self.assertEqual(manifest['sourceSha256'], 'acdc3691327eda6e7bc9495606dfd84358171d5a835b69b92b51e321ada2d24c')
        self.assertEqual(len(manifest['candidates']), 82)
        self.assertGreater(max(c['sourceParagraph'] for c in manifest['candidates']), 7280)
        for entry in manifest['candidates']:
            self.assertIn(entry['sourceTerm'].casefold(), entry['sourceExcerpt'].casefold())

    def test_copies_and_embedded_hub_match(self):
        html = (ROOT / 'italiano-flashcards.html').read_text()
        canonical = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')
        for path in [ROOT / 'www/italiano-flashcards.html', ROOT / 'anki-html/italiano-flashcards.html',
                     canonical / 'italiano-flashcards.html', canonical / 'www/italiano-flashcards.html']:
            self.assertEqual(path.read_text(), html)
        hub = (ROOT / 'index.html').read_text()
        embedded = re.search(r'<script type="application/json" id="app-carte">([\s\S]*?)</script>', hub)
        self.assertEqual(json.loads(embedded[1]), html)


if __name__ == '__main__':
    unittest.main()

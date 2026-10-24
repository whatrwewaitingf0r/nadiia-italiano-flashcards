"""24 October top-up: exactly 100 pairs, append-only and globally unique additions."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def data(name, token):
    return json.JSONDecoder().raw_decode((ROOT / name).read_text().split(token, 1)[1])[0]

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def original_words(items):
    # Scope historical 24 October snapshots to the payload before 25 October.
    items = [item for item in items if not item.get('id', '').startswith('25-ott-') and not item.get('group', '').startswith('25 ott · ')]
    for item in items:
        if item.get('id', '').startswith('24-ott-'):
            item['pairs'] = [[re.sub(r"^(?:(?:il|lo|la|i|gli|le) |l')", '', it), en] for it, en in item['pairs']]
        elif item.get('group', '').startswith('24 ott · '):
            item['it'] = re.sub(r"^(?:(?:il|lo|la|i|gli|le) |l')", '', item['it'])
    return items

class Hundred24Tests(unittest.TestCase):
    def test_each_deck_has_one_hundred_pairs_in_both_apps(self):
        decks = original_words(data('coppie.html', 'const DECKS='))
        cards = original_words(data('italiano-flashcards.html', 'const ALL='))
        for suffix in ['corpo', 'terra', 'casa']:
            deck, = [d for d in decks if d['id'] == '24-ott-' + suffix]
            self.assertEqual(len(deck['pairs']), 100)
            lesson = [c for c in cards if c['group'] == '24 ott · ' + suffix]
            self.assertEqual([[c['it'], c['other']] for c in lesson], deck['pairs'])
        self.assertEqual(len(cards), 1973)
        self.assertEqual(digest(cards[:1852]), '293444005cc7eb332297c51b2930b72e910d10f936bac50eec23c6579f626942')
        counts = {'24-ott-corpo': 43, '24-ott-terra': 71, '24-ott-casa': 65}
        previous = [dict(d, pairs=d['pairs'][:counts.get(d['id'], len(d['pairs']))]) for d in decks]
        self.assertEqual(digest(previous), '1a6a1e545435584286669a23a9c1f941b8488650cb3955a758f69fd27fd39d8c')
        additions = cards[1852:]
        new = [c['it'].casefold() for c in additions]
        self.assertEqual(len(new), len(set(new)))
        for word in new:
            self.assertEqual(sum(c['it'].casefold() == word for c in cards), 1)
            self.assertEqual(sum(it.casefold() == word for d in decks for it, _ in d['pairs']), 1)

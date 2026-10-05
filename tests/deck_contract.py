"""Frozen retained v29 baseline after the authorized v32 removals."""
import hashlib
import json

V29_CARD_COUNT = 944
V29_CARDS_SHA256 = 'e33694defb736c5d037df00d1dfbac7d194dccc289d8ef488db778afdefeafce'

def assert_v29_cards(test, cards):
    test.assertGreaterEqual(len(cards), V29_CARD_COUNT)
    digest = hashlib.sha256(json.dumps(cards[:V29_CARD_COUNT], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    test.assertEqual(digest, V29_CARDS_SHA256)

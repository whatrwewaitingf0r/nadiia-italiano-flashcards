"""Frozen deck preservation, independent of later additive lesson imports."""
import hashlib
import json

V29_CARD_COUNT = 1010
V29_CARDS_SHA256 = '071abaf2d84833c3f34183003f8e282853732c34bd67d1ba4a40e8fdf28e9941'

def assert_v29_cards(test, cards):
    test.assertGreaterEqual(len(cards), V29_CARD_COUNT)
    digest = hashlib.sha256(json.dumps(cards[:V29_CARD_COUNT], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    test.assertEqual(digest, V29_CARDS_SHA256)

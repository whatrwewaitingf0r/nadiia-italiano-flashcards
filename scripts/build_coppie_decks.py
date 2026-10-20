"""Refresh Coppie decks from the existing Carte source (no card edits)."""
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def decks_from_cards(source):
    cards = json.JSONDecoder().raw_decode(source.split('const ALL=', 1)[1])[0]
    groups = ast.literal_eval(re.search(r'const groups=(\[[\s\S]*?\]);', source)[1])
    mapping = ast.literal_eval('{' + re.search(r'const byFilter=\{([\s\S]*?)\};', source)[1] + '}')
    decks = []
    for key, label in groups:
        # Rule explanations and word-order puzzles are not IT/EN translations.
        if key in {'grammar-verbi', 'aug-26-riordina'}:
            continue
        pairs, seen = [], set()
        for card in cards:
            if card.get('group') != mapping[key] or card.get('lang') != 'EN':
                continue
            it = card.get('it', '').strip()
            # Lisa cards put conjugation tables after a clear English first line.
            en = card.get('other', '').split('\n')[0].strip()
            pair = (it, en)
            if not it or not en or it == en or re.search(r'[\u0400-\u04ff]|_{2,}|\.\.\.', it + en):
                continue
            if pair not in seen:
                seen.add(pair)
                pairs.append(list(pair))
        if pairs:
            decks.append({'id': key, 'label': label, 'pairs': pairs})
    return decks

if __name__ == '__main__':
    path = ROOT / 'coppie.html'
    decks = decks_from_cards((ROOT / 'italiano-flashcards.html').read_text())
    data = json.dumps(decks, ensure_ascii=False, separators=(',', ':'))
    html = re.sub(r'const DECKS=.*?;\n', lambda _: 'const DECKS=' + data + ';\n', path.read_text(), count=1)
    path.write_text(html)

"""Append the 7 October lesson as ONE mixed Carte deck and publish-ready v39 copies."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUP = '7 ott'
# One lesson: no topic field, subgroup tag, or separate direction deck.
ITEMS = [
    ('un panino con prosciutto e formaggio', 'a ham and cheese sandwich · m sg'),
    ('una focaccia con le olive', 'a focaccia with olives · f sg'),
    ('una pizza Margherita', 'a Margherita pizza · f sg'),
    ('un gelato al cioccolato', 'a chocolate ice cream · m sg'),
    ('un cornetto con la crema', 'a croissant with pastry cream · m sg'),
    ('un caffè macchiato', 'an espresso with a dash of milk · m sg'),
    ('una bruschetta con il pomodoro', 'a bruschetta with tomato · f sg'),
    ('una spremuta di arancia', 'a freshly squeezed orange juice · f sg'),
    ("un'insalata di riso", 'a rice salad · f sg'),
    ('un tagliere di salumi e formaggi', 'a platter of cured meats and cheeses · m sg'),
    ('un tramezzino al salmone', 'a salmon sandwich · m sg'),
    ('una pizzetta', 'a small pizza · f sg'),
    ('una Caprese', 'a tomato and mozzarella salad · f sg'),
    ('un tè al limone', 'a lemon tea · m sg'),
    ('prosciutto e melone', 'ham and melon'),
    ('una cotoletta alla milanese', 'a Milanese-style breaded cutlet · f sg'),
    ('le lasagne alla bolognese', 'Bolognese-style lasagne · f pl'),
    ('le linguine al pesto', 'linguine with pesto · f pl'),
    ('gli spaghetti al pomodoro', 'spaghetti with tomato sauce · m pl'),
    ('i carciofi alla romana', 'Roman-style artichokes · m pl'),
    ('gli gnocchi al gorgonzola', 'gnocchi with Gorgonzola cheese · m pl'),
    ('le penne al ragù', 'penne with meat sauce · f pl'),
    ('le crocchette di patate', 'potato croquettes · f pl'),
    ('le verdure alla griglia', 'grilled vegetables · f pl'),
    ('il bar', 'a cafe / bar · m sg'),
    ('la pizzeria', 'a pizza restaurant · f sg'),
    ('la caffetteria', 'a coffee shop · f sg'),
    ('la trattoria', 'a traditional informal restaurant · f sg'),
    ('la pasticceria', 'a pastry shop · f sg'),
    ('il ristorante', 'a restaurant · m sg'),
    ('questo', 'this · m sg'), ('questa', 'this · f sg'),
    ('questi', 'these · m pl'), ('queste', 'these · f pl'),
    ('quello', 'that · m sg'), ('quella', 'that · f sg'),
    ('quelli', 'those · m pl'), ('quelle', 'those · f pl'),
]
# Include grid nouns only if the existing decks do not already have that bare noun.
GRID = [
    ('il cappuccino', 'a cappuccino · m sg'),
    ('i formaggi', 'cheeses · m pl'),
    ('le patatine fritte', 'French fries / chips · f pl'),
    ('il gelato', 'ice cream · m sg'),
    ('la pizza', 'pizza · f sg'),
    ('gli spaghetti', 'spaghetti · m pl'),
    ('il cornetto', 'a croissant · m sg'),
    ("l'acqua", 'water · f sg'),
    ('le fragole', 'strawberries · f pl'),
    ('i pomodori', 'tomatoes · m pl'),
    ('la birra', 'beer · f sg'),
    ('le torte', 'cakes · f pl'),
    ('il cameriere', 'a waiter · m sg'),
    ('il cliente', 'a customer · m sg'),
]

def bare_noun(text):
    return re.sub(r"^(?:il |lo |la |i |gli |le |un |uno |una |l['’]|un['’])", '', text.casefold().strip())

def build_cards(existing):
    seen = {bare_noun(c['it']) for c in existing}
    items = ITEMS + [item for item in GRID if bare_noun(item[0]) not in seen]
    return [{'it': it, 'other': other, 'lang': 'EN', 'group': GROUP,
             'note': '', 'tags': ['7-ott']} for it, other in items]

def main():
    page = (ROOT / 'italiano-flashcards.html').read_text()
    before, after = page.split('const ALL=', 1)
    old, end = json.JSONDecoder().raw_decode(after)
    existing = [c for c in old if c['group'] != GROUP]
    lesson = build_cards(existing)
    page = before + 'const ALL=' + json.dumps(existing + lesson, ensure_ascii=False, separators=(',', ':')) + after[end:]
    if "['7-ott','" not in page:
        page = page.replace(" ['verbi-forme','Verbi · forme'],", " ['verbi-forme','Verbi · forme'],\n ['7-ott','7 ott'],")
        page = page.replace("  'verbi-forme':'Verbi · forme',", "  'verbi-forme':'Verbi · forme',\n  '7-ott':'7 ott',")
    page = re.sub(r'\?v=\d+', '?v=39', page.replace('v38', 'v39'))
    apps = {'carte': 'italiano-flashcards.html', 'articoli': 'articoli-esercizi.html',
            'aggettivi': 'articoli-aggettivi.html', 'verbi': 'verbi-tempi.html'}
    hub = re.sub(r'\?v=\d+', '?v=39', (ROOT / 'index.html').read_text().replace('v38', 'v39'))
    for key, filename in apps.items():
        app = page if key == 'carte' else re.sub(r'\?v=\d+', '?v=39', (ROOT / filename).read_text())
        for folder in [ROOT, ROOT / 'www', ROOT / 'anki-html']:
            (folder / filename).write_text(app)
        payload = json.dumps(app, ensure_ascii=True).replace('<', '\\u003c')
        hub = re.sub(r'(<script type="application/json" id="app-' + key + r'">)[\s\S]*?(</script>)',
                     lambda m: m[1] + payload + m[2], hub)
    for folder in [ROOT, ROOT / 'www', ROOT / 'anki-html']:
        (folder / 'index.html').write_text(hub)
    print(f'{len(lesson)} cards in one 7 ott deck; {len(existing) + len(lesson)} total; v39')

if __name__ == '__main__':
    main()

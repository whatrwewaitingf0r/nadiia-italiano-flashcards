"""Publish the 14 October restaurant lesson as one ordered, reversible Carte deck."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUP = '14 ott'
ITEMS = [
    ('I signori desiderano?', 'What would you like?'),
    ('Vorrei…', 'I would like…'),
    ('Cosa desidera?', 'What would you like? (formal sg)'),
    ('Cosa desiderate?', 'What would you like? (pl)'),
    ('Per me invece…', 'For me instead…'),
    ('Cosa prende?', 'What will you have? (formal)'),
    ('Cosa prendete?', 'What will you have? (pl)'),
    ('Io prendo…', "I'll have…"),
    ('Anch’io prendo', "I'll have the same"),
    ('Anch’io vorrei…', 'I would also like…'),
    ('Il conto, per favore', 'The bill, please'),
    ('Quant’è?', 'How much is it?'),
    ('Posso pagare con la carta?', 'Can I pay by card?'),
    ('pagare in contanti', 'to pay cash'),
    ('da bere', 'to drink'),
    ('per antipasto', 'for a starter'),
    ('per primo', 'for the first course'),
    ('per secondo', 'for the second course'),
    ('per contorno', 'for a side'),
    ('per dessert', 'for dessert'),
    ('il pesce', 'fish · m sg'),
    ('il risotto', 'risotto · m sg'),
    ('il minestrone', 'vegetable soup · m sg'),
    ('il pollo', 'chicken · m sg'),
    ('i peperoni', 'peppers · m pl'),
    ('le verdure', 'vegetables · f pl'),
    ('le fragole', 'strawberries · f pl'),
    ('le macedonie', 'fruit salads · f pl'),
    ('le lasagne', 'lasagne · f pl'),
    ('la carne', 'meat · f sg'),
    ('le cotolette', 'breaded cutlets · f pl'),
    ('gli spaghetti', 'spaghetti · m pl'),
    ('il vino', 'wine · m sg'),
    ('l’acqua minerale', 'mineral water · f sg'),
    ('la coca cola', 'Coca-Cola · f sg'),
    ('la cotoletta', 'a breaded cutlet · f sg'),
    ('le patatine fritte', 'French fries / chips · f pl'),
    ('la panna cotta', 'panna cotta / cream pudding · f sg'),
    ('l’acqua', 'water · f sg'),
    ('il gelato', 'ice cream · m sg'),
    ('la birra', 'beer · f sg'),
    ('la macedonia', 'fruit salad · f sg'),
    ('l’insalata', 'salad · f sg'),
    ('i tortellini', 'tortellini / stuffed pasta · m pl'),
    ('l’arrosto', 'roast meat · m sg'),
    ('gli spinaci', 'spinach · m pl'),
    ('la bruschetta', 'toasted bread with toppings · f sg'),
    ('la bistecca', 'steak · f sg'),
    ('le patate', 'potatoes · f pl'),
    ('gli affettati', 'cold cuts · m pl'),
    ('il vino bianco', 'white wine · m sg'),
    ('la pizza', 'pizza · f sg'),
    ('il vino rosso', 'red wine · m sg'),
    ('la piadina', 'Italian flatbread · f sg'),
    ('il tiramisù', 'tiramisu · m sg'),
    ('il muffin', 'a muffin · m sg'),
    ('l’aranciata', 'orange soda · f sg'),
    ('il sorbetto', 'sorbet · m sg'),
    ('la torta', 'cake · f sg'),
    ('la sprite', 'Sprite / lemon-lime soda · f sg'),
    ('il budino', 'pudding · m sg'),
    ('la caprese', 'tomato and mozzarella salad · f sg'),
    ('i ravioli', 'ravioli / stuffed pasta · m pl'),
    ('i filetti di pesce', 'fish fillets · m pl'),
    ('il polpo', 'octopus · m sg'),
    ('i cannelloni', 'cannelloni / filled pasta tubes · m pl'),
    ('la tartare', 'finely chopped raw meat or fish · f sg'),
    ('le scaloppine', 'thin meat cutlets · f pl'),
    ('il purè', 'mashed potatoes · m sg'),
    ('i fichi', 'figs · m pl'),
    ('il melone', 'melon · m sg'),
    ('lo spumante', 'sparkling wine · m sg'),
    ('la pizzetta', 'a small pizza · f sg'),
    ('le pastine', 'small pastries · f pl'),
    ('lo champagne', 'champagne · m sg'),
    ('lo gnocco fritto', 'fried dough · m sg'),
    ('il torrone', 'nougat · m sg'),
]
VERBS = [
    ('prendere', 'prendo prendi prende prendiamo prendete prendono', 'have'),
    ('preferire', 'preferisco preferisci preferisce preferiamo preferite preferiscono', 'prefer'),
    ('ordinare', 'ordino ordini ordina ordiniamo ordinate ordinano', 'order'),
]
PERSONS = ['io', 'tu', 'lui/lei', 'noi', 'voi', 'loro']
SUBJECTS = ['I', 'you', 'he/she', 'we', 'you (pl)', 'they']
POLITE = [('Scusi', 'Excuse me (formal)'), ('per cortesia', 'if you please'),
          ('per favore', 'please'), ('per piacere', 'please'), ('grazie', 'thank you')]


def build_cards():
    items = ITEMS.copy()
    for verb, forms, english in VERBS:
        for i, form in enumerate(forms.split()):
            inflected = english if i != 2 else ('has' if english == 'have' else english + 's')
            items.append((form, f'{verb} · {PERSONS[i]} · {SUBJECTS[i]} {inflected}'))
    items.extend(POLITE)
    return [{'it': it, 'other': other, 'lang': 'EN', 'group': GROUP,
             'note': '', 'tags': ['14-ott']} for it, other in items]


def main():
    page = (ROOT / 'italiano-flashcards.html').read_text()
    before, after = page.split('const ALL=', 1)
    old, end = json.JSONDecoder().raw_decode(after)
    existing = [c for c in old if c['group'] != GROUP]
    lesson = build_cards()
    page = before + 'const ALL=' + json.dumps(existing + lesson, ensure_ascii=False, separators=(',', ':')) + after[end:]
    if "['14-ott','" not in page:
        page = page.replace("const groups=[", "const groups=[\n ['14-ott','14 ott'],")
        page = page.replace("  '7-ott':'7 ott',", "  '14-ott':'14 ott',\n  '7-ott':'7 ott',")
    page = page.replace("filter.value='7-ott';", "filter.value='14-ott';")
    page = page.replace("filter.value==='7-ott'", "['14-ott','7-ott'].includes(filter.value)")
    old_shuffler = re.search(r'function shufflePool\(\)\{[\s\S]*?\n\}', page)[0]
    new_shuffler = """function shufflePool(){
 // Dated lessons stay together in sheet order, newest first; older decks stay separate.
 const lessons=['14 ott','7 ott'];
 const ordered=lessons.flatMap(group=>pool.filter(c=>c.group===group));
 const older=pool.filter(c=>!lessons.includes(c.group));
 for(let i=older.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[older[i],older[j]]=[older[j],older[i]]}
 pool=ordered.concat(older);
}"""
    page = page.replace(old_shuffler, new_shuffler).replace('v40', 'v41').replace('?v=40', '?v=41')
    apps = {'carte': 'italiano-flashcards.html', 'articoli': 'articoli-esercizi.html',
            'aggettivi': 'articoli-aggettivi.html', 'verbi': 'verbi-tempi.html'}
    hub = (ROOT / 'index.html').read_text().replace('v40', 'v41').replace('?v=40', '?v=41')
    for key, filename in apps.items():
        app = page if key == 'carte' else (ROOT / filename).read_text().replace('?v=40', '?v=41')
        for folder in [ROOT, ROOT / 'www', ROOT / 'anki-html']:
            (folder / filename).write_text(app)
        payload = json.dumps(app, ensure_ascii=True).replace('<', '\\u003c')
        hub = re.sub(r'(<script type="application/json" id="app-' + key + r'">)[\s\S]*?(</script>)',
                     lambda m: m[1] + payload + m[2], hub)
    for folder in [ROOT, ROOT / 'www', ROOT / 'anki-html']:
        (folder / 'index.html').write_text(hub)
    print(f'{len(lesson)} cards in one 14 ott deck; {len(existing) + len(lesson)} total; v41')


if __name__ == '__main__':
    main()

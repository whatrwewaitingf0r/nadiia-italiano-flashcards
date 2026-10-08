"""Build the separate 168-card form deck and refresh the v38 hub payload/copies."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUP = 'Verbi · forme'
PERSONS = ['io', 'tu', 'lui', 'noi', 'voi', 'loro']
EN = ['I', 'you', 'he', 'we', 'you (plural)', 'they']
# Six forms per row: io / tu / lui / noi / voi / loro.
FORMS = {
    'studiare': [
        'studio|studi|studia|studiamo|studiate|studiano',
        'ho studiato|hai studiato|ha studiato|abbiamo studiato|avete studiato|hanno studiato',
        'studierò|studierai|studierà|studieremo|studierete|studieranno',
        'studierei|studieresti|studierebbe|studieremmo|studiereste|studierebbero'],
    'essere': [
        'sono|sei|è|siamo|siete|sono',
        'sono stato|sei stato|è stato|siamo stati|siete stati|sono stati',
        'sarò|sarai|sarà|saremo|sarete|saranno',
        'sarei|saresti|sarebbe|saremmo|sareste|sarebbero'],
    'avere': [
        'ho|hai|ha|abbiamo|avete|hanno',
        'ho avuto|hai avuto|ha avuto|abbiamo avuto|avete avuto|hanno avuto',
        'avrò|avrai|avrà|avremo|avrete|avranno',
        'avrei|avresti|avrebbe|avremmo|avreste|avrebbero'],
    'volere': [
        'voglio|vuoi|vuole|vogliamo|volete|vogliono',
        'ho voluto|hai voluto|ha voluto|abbiamo voluto|avete voluto|hanno voluto',
        'vorrò|vorrai|vorrà|vorremo|vorrete|vorranno',
        'vorrei|vorresti|vorrebbe|vorremmo|vorreste|vorrebbero'],
    'andare': [
        'vado|vai|va|andiamo|andate|vanno',
        'sono andato|sei andato|è andato|siamo andati|siete andati|sono andati',
        'andrò|andrai|andrà|andremo|andrete|andranno',
        'andrei|andresti|andrebbe|andremmo|andreste|andrebbero'],
    'fare': [
        'faccio|fai|fa|facciamo|fate|fanno',
        'ho fatto|hai fatto|ha fatto|abbiamo fatto|avete fatto|hanno fatto',
        'farò|farai|farà|faremo|farete|faranno',
        'farei|faresti|farebbe|faremmo|fareste|farebbero'],
    'potere': [
        'posso|puoi|può|possiamo|potete|possono',
        'ho potuto|hai potuto|ha potuto|abbiamo potuto|avete potuto|hanno potuto',
        'potrò|potrai|potrà|potremo|potrete|potranno',
        'potrei|potresti|potrebbe|potremmo|potreste|potrebbero'],
}
TENSES = ['presente', 'passato prossimo', 'futuro semplice', 'condizionale presente']
BASE = {'studiare': 'study', 'essere': 'be', 'avere': 'have', 'volere': 'want', 'andare': 'go', 'fare': 'do', 'potere': 'be able to'}
PAST = {'studiare': ('studied', 'studied'), 'essere': ('was', 'been'), 'avere': ('had', 'had'), 'volere': ('wanted', 'wanted'), 'andare': ('went', 'gone'), 'fare': ('did', 'done'), 'potere': ('was able to', 'been able to')}

def meaning(verb, tense, person):
    subject = EN[person]
    third = person == 2
    if tense == 'presente':
        if verb == 'studiare':
            return f'{subject} {"studies" if third else "study"} / {subject} {["am", "are", "is", "are", "are", "are"][person]} studying'
        if verb == 'essere': return f'{subject} {["am", "are", "is", "are", "are", "are"][person]}'
        if verb == 'avere': return f'{subject} {"has" if third else "have"}'
        if verb == 'potere': return f'{subject} can / {subject} {["am", "are", "is", "are", "are", "are"][person]} able to'
        if verb == 'fare': return f'{subject} {"does" if third else "do"} / {subject} {"makes" if third else "make"}'
        return f'{subject} {("wants" if third else "want") if verb == "volere" else ("goes" if third else "go")}'
    if tense == 'passato prossimo':
        past, participle = PAST[verb]
        if verb in ['essere', 'potere']:
            past = ('was' if person in [0, 2] else 'were') + (' able to' if verb == 'potere' else '')
        return f'{subject} {past} / {subject} {"has" if third else "have"} {participle}'
    if tense == 'futuro semplice':
        return f'{subject} will {BASE[verb]}' + (f' / {subject} will make' if verb == 'fare' else '')
    if verb == 'volere': return f'{subject} would like'
    if verb == 'potere': return f'{subject} could / {subject} would be able to'
    return f'{subject} would {BASE[verb]}' + (f' / {subject} would make' if verb == 'fare' else '')

def build_cards():
    cards = []
    for verb, rows in FORMS.items():
        for tense, row in zip(TENSES, rows):
            for person, form in enumerate(row.split('|')):
                note = f'{verb} · {tense}'
                if tense == 'passato prossimo' and verb in ['essere', 'andare']:
                    note += ' · Participio maschile; al femminile: ' + ('stata / state' if verb == 'essere' else 'andata / andate')
                if tense == 'passato prossimo' and verb in ['volere', 'potere']:
                    note += ' · Qui senza infinito; con un altro verbo può cambiare l’ausiliare.'
                cards.append({'it': PERSONS[person] + ' ' + form, 'other': tense + ' · ' + meaning(verb, tense, person),
                              'lang': 'EN', 'group': GROUP, 'note': note, 'tags': ['verbi-forme'], 'verb': verb, 'tense': tense})
    return cards

def main():
    page = (ROOT / 'italiano-flashcards.html').read_text()
    before, after = page.split('const ALL=', 1)
    old, end = json.JSONDecoder().raw_decode(after)
    cards = [c for c in old if c['group'] != GROUP] + build_cards()
    page = before + 'const ALL=' + json.dumps(cards, ensure_ascii=False, separators=(',', ':')) + after[end:]
    if "['verbi-forme','" not in page:
        page = page.replace(" ['streghe','Streghe'],", " ['streghe','Streghe'],\n ['verbi-forme','Verbi · forme'],")
        page = page.replace("  'streghe':'Streghe',", "  'streghe':'Streghe',\n  'verbi-forme':'Verbi · forme',")
    page = re.sub(r'\?v=\d+', '?v=38', page.replace('v37', 'v38'))
    for folder in [ROOT, ROOT / 'www', ROOT / 'anki-html']:
        (folder / 'italiano-flashcards.html').write_text(page)
    hub = (ROOT / 'index.html').read_text().replace('v37', 'v38')
    hub = re.sub(r'\?v=\d+', '?v=38', hub)
    apps = {'carte': 'italiano-flashcards.html', 'articoli': 'articoli-esercizi.html',
            'aggettivi': 'articoli-aggettivi.html', 'verbi': 'verbi-tempi.html'}
    for key, filename in apps.items():
        app = re.sub(r'\?v=\d+', '?v=38', (ROOT / filename).read_text())
        for folder in [ROOT, ROOT / 'www', ROOT / 'anki-html']:
            (folder / filename).write_text(app)
        payload = json.dumps(app, ensure_ascii=True).replace('<', '\\u003c')
        hub = re.sub(r'(<script type="application/json" id="app-' + key + r'">)[\s\S]*?(</script>)',
                     lambda m: m[1] + payload + m[2], hub)
    for folder in [ROOT, ROOT / 'www', ROOT / 'anki-html']:
        (folder / 'index.html').write_text(hub)
    print(f'{len(build_cards())} Verbi · forme cards; {len(cards)} total; v38')

if __name__ == '__main__':
    main()

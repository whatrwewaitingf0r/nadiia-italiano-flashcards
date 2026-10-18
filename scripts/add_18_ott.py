"""Publish the approved 18 October missed words as one ordered Carte deck."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUP = '18 ott'


def main():
    pairs = json.loads((ROOT / 'tests/lesson-18-ott-pairs.json').read_text())
    page = (ROOT / 'italiano-flashcards.html').read_text()
    before, after = page.split('const ALL=', 1)
    cards, end = json.JSONDecoder().raw_decode(after)
    existing = [c for c in cards if c['group'] != GROUP]
    lesson = [{'it': it, 'other': en, 'lang': 'EN', 'group': GROUP,
               'note': '', 'tags': ['18-ott']} for it, en in pairs]
    page = before + 'const ALL=' + json.dumps(existing + lesson, ensure_ascii=False, separators=(',', ':')) + after[end:]
    if "['18-ott','18 ott']" not in page:
        page = page.replace('const groups=[', "const groups=[\n ['18-ott','18 ott'],")
        page = page.replace("  '14-ott':'14 ott',", "  '18-ott':'18 ott',\n  '14-ott':'14 ott',")
    page = page.replace("filter.value='14-ott';", "filter.value='18-ott';")
    page = page.replace("['14-ott','7-ott']", "['18-ott','14-ott','7-ott']")
    page = page.replace("const lessons=['14 ott','7 ott'];", "const lessons=['18 ott','14 ott','7 ott'];")
    page = page.replace('v41', 'v42').replace('?v=41', '?v=42')
    apps = {'carte': 'italiano-flashcards.html', 'articoli': 'articoli-esercizi.html',
            'aggettivi': 'articoli-aggettivi.html', 'verbi': 'verbi-tempi.html'}
    hub = (ROOT / 'index.html').read_text().replace('v41', 'v42').replace('?v=41', '?v=42')
    canon = Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')
    folders = [ROOT, ROOT / 'www', ROOT / 'anki-html', canon, canon / 'www']
    for key, filename in apps.items():
        # Non-card app behavior/data stays byte-identical except release navigation URLs.
        app = page if key == 'carte' else (ROOT / filename).read_text().replace('?v=41', '?v=42')
        for folder in folders:
            (folder / filename).write_text(app)
        payload = json.dumps(app, ensure_ascii=True).replace('<', '\\u003c')
        hub = re.sub(r'(<script type="application/json" id="app-' + key + r'">)[\s\S]*?(</script>)',
                     lambda m: m[1] + payload + m[2], hub)
    for folder in folders:
        (folder / 'index.html').write_text(hub)
    print(f'{len(lesson)} cards in one 18 ott deck; {len(existing) + len(lesson)} total; v42')


if __name__ == '__main__':
    main()

"""v40: one Streghe deck, reversed only with the shared direction toggle."""
import hashlib,json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CANON=Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')
BASES=[ROOT,ROOT/'www',ROOT/'anki-html',CANON,CANON/'www']
GROUPS=['Streghe']
REQUIRED={'la scopa volante':'flying broom','la guaritrice':'healer','la levatrice':'midwife','la partoriente':'woman in labour','la stregoneria':'witchcraft','il diavolo':'devil','il Quattrocento':'15th century','il Seicento':'17th century','il cornicello':'little horn','la spalla sinistra':'left shoulder','il numero diciassette':'seventeen','VIXI':'I have lived'}
class StregheTests(unittest.TestCase):
 def setUp(self):
  self.h=(ROOT/'italiano-flashcards.html').read_text()
  self.cards=json.JSONDecoder().raw_decode(self.h.split('const ALL=',1)[1])[0]
 def test_lettura_is_deleted_not_hidden(self):
  for name in ['index.html','italiano-flashcards.html']:
   h=(ROOT/name).read_text()
   self.assertNotRegex(h,r'(?i)lettura|reading-card|app-lettura|tab-lettura')
  self.assertFalse(any(c.get('reading') for c in self.cards))
  for base in BASES:
   for name in ['liam-lettura.html','liam-lettura.json']:self.assertFalse((base/name).exists(),str(base/name))
 def test_one_complete_unique_reversible_deck(self):
  deck=[c for c in self.cards if c['group']=='Streghe']
  self.assertEqual(len(deck),101)
  self.assertEqual(len({c['it'] for c in deck}),101)
  for c in deck:
   self.assertNotIn('direction',c)
   self.assertEqual(c['tags'],['streghe'])
   self.assertEqual(c['lang'],'EN')
   self.assertNotRegex(json.dumps(c,ensure_ascii=False),'[\u0400-\u04ff]')
  self.assertTrue(REQUIRED.items() <= {c['it']:c['other'] for c in deck}.items())
  manifest=json.loads((ROOT/'scripts/streghe.json').read_text())
  self.assertEqual([(c['it'],c['other']) for c in deck],[(c['it'],c['en']) for c in manifest['words']])
 def test_only_one_dropdown_item(self):
  options=re.search(r'const groups=([\s\S]*?);',self.h)[1]
  self.assertEqual(re.findall(r"\['(streghe[^']*)','([^']*)'\]",options),[('streghe','Streghe')])
  self.assertIn("'streghe':'Streghe'",self.h)
  self.assertNotRegex(self.h,r'Streghe · (?:IT→EN|EN→IT)|streghe-(?:it-en|en-it)')
 def test_all_unrelated_cards_preserved(self):
  unrelated=[c for c in self.cards if c['group'] not in GROUPS and c['group'] not in {'100 parole 3', 'Verbi · forme', '7 ott'}]
  frozen=json.loads((ROOT/'tests/streghe-v35-baseline.json').read_text())
  self.assertEqual(len(unrelated),frozen['count'])
  self.assertEqual(hashlib.sha256(json.dumps(unrelated,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),frozen['sha256'])
 def test_version_embedded_apps_and_copies(self):
  h=(ROOT/'index.html').read_text()
  self.assertIn('content="v40"',h);self.assertIn('content="v40"',self.h)
  self.assertEqual(re.findall(r'data-app="([^"]+)">',h),['carte','articoli','aggettivi','verbi'])
  m=re.search(r'<script type="application/json" id="app-carte">([\s\S]*?)</script>',h)
  self.assertEqual(json.loads(m[1]),self.h)
  for base in BASES:
   for name in ['index.html','italiano-flashcards.html']:self.assertEqual((base/name).read_bytes(),(ROOT/name).read_bytes())
if __name__=='__main__':unittest.main()

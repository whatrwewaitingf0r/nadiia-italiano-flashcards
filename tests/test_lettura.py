"""Full DOCX coverage, not a keyword/LESSON-heading smoke test."""
import hashlib, json, re, unittest
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/Users/it/.jaine/media/inbound/Copy_of_test---8746b41d-eb5a-4e13-a04e-8e0ca58130f5.docx')
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
SOURCE_UNIT_HASH='ecdf7e2e821641757b5414cac03ac591602ad06330af3eac9b3d224542c30517'
BASELINE_HASH='e33694defb736c5d037df00d1dfbac7d194dccc289d8ef488db778afdefeafce'
def original():
 with ZipFile(SOURCE) as z: xml=ET.fromstring(z.read('word/document.xml'))
 w='{'+NS['w']+'}'
 p=[''.join((n.text or '') if n.tag==w+'t' else '\n' if n.tag==w+'br' else '\t' if n.tag==w+'tab' else '' for n in x.iter()) for x in xml.findall('.//w:body//w:p',NS)]
 start=p.index('🧙 Folclore Italiano')
 return p[start:]
def data():
 p=ROOT/'liam-lettura.json'
 return json.loads(p.read_text()) if p.exists() else {'sections':[], 'cards':[]}
class LetturaTests(unittest.TestCase):
 def test_inline_line_breaks_are_not_discarded(self):
  paragraphs={p['index']:p['text'] for s in data()['sections'] for p in s['paragraphs']}
  self.assertIn('\n',paragraphs[5963])
 def test_full_source_is_preserved_in_order(self):
  source=[p['text'] for u in data()['sections'] for p in u['paragraphs']]
  self.assertEqual(len(source),1386)
  self.assertEqual(hashlib.sha256(json.dumps(source,ensure_ascii=False).encode()).hexdigest(),SOURCE_UNIT_HASH)
  if SOURCE.exists(): self.assertEqual(source, original())
 def test_cards_cover_full_source_and_every_question(self):
  d=data();source_cards=[c for c in d['cards'] if c.get('kind')=='reading']
  self.assertEqual([c['sourceText'] for c in source_cards],['\n'.join(p['text'] for p in s['paragraphs']) for s in d['sections']])
  self.assertGreaterEqual(len(source_cards),13)
  prompts=[q for s in d['sections'] for q in s['questions']]
  self.assertGreaterEqual(len(prompts),54)
  for q in prompts:
   self.assertTrue(any(c['it']==q['prompt'] and c['sourceParagraph']==q['sourceParagraph'] for c in d['cards']))
  for c in d['cards']:
   self.assertEqual(c['lang'],'EN');self.assertEqual(c['group'],'Liam · Lettura');self.assertIn('liam',c['tags']);self.assertTrue(c['other'])
  for term in ['Matteuccia','formula magica','Guaritrice o strega','Strigoi','Lamia','Yamauba','sorcières','wicce','Hexe','Hai capito?']:
   self.assertIn(term,json.dumps(d,ensure_ascii=False))
 def test_offline_page_contains_exact_payload(self):
  p=ROOT/'liam-lettura.html';h=p.read_text() if p.exists() else ''
  m=re.search(r'<script type="application/json" id="reading-data">([\s\S]*?)</script>',h)
  self.assertIsNotNone(m)
  self.assertEqual(json.loads(m[1]),data())
  self.assertNotRegex(h,r'fetch\s*\(|XMLHttpRequest|@import|<script[^>]+src=')

class LetturaIntegrationTests(unittest.TestCase):
 def test_additive_cards_and_lesson5_removed(self):
  current=json.JSONDecoder().raw_decode((ROOT/'italiano-flashcards.html').read_text().split('const ALL=',1)[1])[0]
  self.assertEqual([c for c in current if c.get('reading')],[c for c in data()['cards']])
  self.assertEqual(hashlib.sha256(json.dumps(current[:944],ensure_ascii=False,sort_keys=True).encode()).hexdigest(),BASELINE_HASH)
  five=[c for c in current if c.get('tags')==['liam','lesson5','nord-sud']]
  self.assertEqual(len(five),0)
 def test_all_old_tabs_plus_lettura(self):
  h=(ROOT/'index.html').read_text()
  tabs=re.findall(r'data-app="([^\"]+)">([^<]+)</button>',h)
  for pair in [('carte','Carte'),('articoli','Articoli'),('aggettivi','Articoli + aggettivi'),('verbi','Verbi')]:self.assertIn(pair,tabs)
  self.assertIn(('lettura','Lettura'),tabs);self.assertNotIn('Liam ieri',[label for key,label in tabs])
  for key,name in [('lettura','liam-lettura.html'),('carte','italiano-flashcards.html')]:
   m=re.search(r'<script type="application/json" id="app-'+key+r'">([\s\S]*?)</script>',h)
   self.assertIsNotNone(m);self.assertEqual(json.loads(m[1]),(ROOT/name).read_text())
 def test_passato_and_copies(self):
  self.assertFalse((ROOT/'liam-passato.html').exists())
  canon=Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')
  for name in ['liam-lettura.html','liam-lettura.json','italiano-flashcards.html','index.html']:
   for base in [ROOT/'www',ROOT/'anki-html',canon,canon/'www']:
    self.assertTrue((base/name).exists(),str(base/name))
    self.assertEqual((ROOT/name).read_bytes(),(base/name).read_bytes())

if __name__=='__main__':unittest.main()

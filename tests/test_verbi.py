import json,re,unittest,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CANON=Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')
def cards(h):return json.JSONDecoder().raw_decode(h.split('const ALL=',1)[1])[0]
class VerbiTests(unittest.TestCase):
 def test_drill(self):
  h=(ROOT/'verbi-tempi.html').read_text()
  self.assertFalse(re.search('[\u0400-\u04ff]',h))
  self.assertFalse(re.search(r'https?://|@import|fetch\s*\(|XMLHttpRequest|srcset=',h))
  self.assertIn('v30',h);self.assertIn('aria-live="polite"',h)
  verbs=json.JSONDecoder().raw_decode(h.split('const VERBS=',1)[1])[0]
  self.assertEqual({v['inf'] for v in verbs},set('essere avere fare andare venire stare dare dire potere volere dovere sapere vedere sentire parlare mangiare bere dormire uscire arrivare partire prendere mettere vivere scrivere leggere capire finire preferire pulire'.split()))
  for v in verbs:
   for t in ['presente','imperfetto','futuro','condizionale']:self.assertEqual(len(v[t]),6,v['inf'])
  self.assertIn('min-width:min(220px,100%)',h)
  for p in [ROOT/'www/verbi-tempi.html',ROOT/'anki-html/verbi-tempi.html',CANON/'verbi-tempi.html',CANON/'www/verbi-tempi.html']:self.assertEqual(h,p.read_text())
 def test_pack_and_preservation(self):
  h=(ROOT/'italiano-flashcards.html').read_text();cs=cards(h)
  self.assertEqual(hashlib.sha256(json.dumps(cs[:985],ensure_ascii=False,sort_keys=True).encode()).hexdigest(),'c9cede215d23fbf6aa79d06c2db2072915f3c74ccb2a648dd840c20214c9d9c0');self.assertEqual(len(cs),1010)
  new=cs[985:];self.assertEqual(len(new),25);self.assertEqual(len({c['it'] for c in new}),25)
  for c in new:self.assertEqual(c['tags'],['grammar','verbi']);self.assertEqual(c['lang'],'EN')
  self.assertFalse(re.search('[\u0400-\u04ff]',h))
  self.assertIn("'grammar-verbi':'Grammatica · verbi'",h)
  self.assertIn('verbi-tempi.html?v=30',h)
  self.assertIn('articoli-esercizi.html?v=30',h);self.assertIn('articoli-aggettivi.html?v=30',h)
  for p in [ROOT/'www/italiano-flashcards.html',ROOT/'anki-html/italiano-flashcards.html',CANON/'italiano-flashcards.html',CANON/'www/italiano-flashcards.html']:self.assertEqual(h,p.read_text())
if __name__=='__main__':unittest.main()

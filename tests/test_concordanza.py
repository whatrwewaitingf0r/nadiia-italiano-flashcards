import json,re,unittest,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CANON=Path('/Users/it/.jaine/workspace/memory/health/nadiia/italian/anki-html')
def cards(h):return json.JSONDecoder().raw_decode(h.split('const ALL=',1)[1])[0]
class ConcordanzaTests(unittest.TestCase):
 def test_inventory(self):
  h=(ROOT/'articoli-aggettivi.html').read_text()
  self.assertFalse(re.search('[\u0400-\u04ff]',h))
  self.assertFalse(re.search(r'https?://|@import|fetch\s*\(|XMLHttpRequest|<script[^>]+src',h))
  ns=json.JSONDecoder().raw_decode(h.split('const NOUNS=',1)[1])[0]
  self.assertGreaterEqual(len(ns),200)
  for w in 'casa amico studente donna uomo città problema foto mano giorno anno volta cosa vita lavoro scuola libro acqua pane caffè macchina telefono ragazzo ragazza bambino animale tempo mare sole notte musica film ristorante hotel spiaggia fiore albero cane gatto serpente'.split():self.assertIn(w,[n['sg'] for n in ns])
  self.assertIn('v30',h)
  for p in [ROOT/'www/articoli-aggettivi.html',ROOT/'anki-html/articoli-aggettivi.html',CANON/'articoli-aggettivi.html',CANON/'www/articoli-aggettivi.html']:self.assertEqual(h,p.read_text())
 def test_flashcards(self):
  h=(ROOT/'italiano-flashcards.html').read_text(); cs=cards(h)
  new=[c for c in cs if c['group']=='Grammatica · concordanza'];self.assertEqual(len(new),0)
  self.assertEqual(len({c['it'] for c in new}),0)
  for c in new:self.assertEqual(c['tags'],['grammar','concordanza']);self.assertEqual(c['lang'],'EN')
  self.assertFalse(re.search('[\u0400-\u04ff]',h))
  for p in [ROOT/'www/italiano-flashcards.html',ROOT/'anki-html/italiano-flashcards.html',CANON/'italiano-flashcards.html',CANON/'www/italiano-flashcards.html']:self.assertEqual(h,p.read_text())
  self.assertIn('.scene.rule-card{min-height:560px}',h);self.assertIn('.scene.rule-card{min-height:640px}',h)
  self.assertIn('articoli-aggettivi.html?v=40',h);self.assertIn('articoli-esercizi.html?v=40',h)
if __name__=='__main__':unittest.main()
